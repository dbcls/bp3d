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

	self.DEF_LAYOUT_BORDER = 'border';
	self.DEF_LAYOUT_WINDOW = 'window';
	self.DEF_LAYOUT = self.DEF_LAYOUT_WINDOW;

	self.glb_localdb_init = false;

	self.DEF_LOCALDB_HASH_KEY = AgDef.LOCALDB_PREFIX+'bp3d-pallet-parts';
	self.DEF_LOCALDB_TREE_INFO = AgDef.LOCALDB_PREFIX+'bp3d-tree-info';
	self.DEF_LOCALDB_FOLDER_INFO = AgDef.LOCALDB_PREFIX+'art-folder-info';
	self.DEF_LOCALDB_PROVIDER_PREFIX = AgDef.LOCALDB_PREFIX+'bp3d-mng-';
	self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY = AgDef.LOCALDB_PREFIX+'recalc-session';

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
	self.FORMAT_DATE_TIME = self.FORMAT_DATE+' '+self.FORMAT_TIME;
	self.FORMAT_ID_NUMBER = '0';

	self.USE_UPLOAD_MULTI_ORIGINAL_OBJECT = true;


	self.USE_CLICK_TO_GROUOP_SELECTED = false;	//フォルダクリック時にグループを自動的にチェック（選択状態にする）。その後、オブジェクトをリストに表示する
	self.USE_FMA_OBJ_LINK = true;	//FMA対応変更モード
	self.USE_CONFLICT_LIST = true;	//conflictリスト
	self.USE_CONFLICT_LIST_TYPE = 'window';	//conflictリスト

	self.USE_OBJ_UPLOAD = false;	//BackStageEditorでOBJファイルのアップロードor削除を行うか


//	self.TITLE_UPLOAD_FOLDER = 'semantic group of obj';
//	self.TITLE_UPLOAD_GROUP = 'physical group of obj (small modification)';
//	self.TITLE_UPLOAD_OBJECT = 'specified obj';
	self.TITLE_UPLOAD_FOLDER = 'Semantic category of obj lineage';
	self.TITLE_UPLOAD_GROUP = 'correction lineage';
	self.TITLE_UPLOAD_OBJECT = 'obj files';

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

	var modelCombo = Ext.getCmp('model-combobox');
	var versionCombo = Ext.getCmp('version-combobox');
	var treeCombo = Ext.getCmp('tree-combobox');

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

	if(modelCombo){
		modelCombo.suspendEvents(false);
		try{
			if(Ext.isString(Common.Model) && modelCombo.getValue() != Common.Model){
//				console.log("setHash2Common():Model=["+modelCombo.getValue()+"]->["+Common.Model+"]");
				modelCombo.setValue(Common.Model);
				Model = Common.Model;
				if(versionCombo) versionCombo.fireEvent('afterrender',versionCombo);
				if(treeCombo) treeCombo.fireEvent('afterrender',treeCombo);
//				updModel = true;
			}
		}catch(e){
			console.error(e);
		}
		modelCombo.resumeEvents();
	}
	if(versionCombo){
		versionCombo.suspendEvents(false);
		try{
			if(Ext.isString(Common.Version) && versionCombo.getValue() != Model+'-'+Common.Version){
//				console.log("setHash2Common():Version=["+versionCombo.getValue()+"]->["+Model+'-'+Common.Version+"]");
				versionCombo.setValue(Model+'-'+Common.Version);
//				Ext.defer(function(){ versionCombo.fireEvent('select',versionCombo); },250);
				updVersion = true;
			}

		}catch(e){
			console.error(e);
		}
		versionCombo.resumeEvents();
	}
	if(treeCombo){
		treeCombo.suspendEvents(false);
		try{
//			if(Ext.isString(Common.TreeName) && treeCombo.getValue() != ConceptInfo+'-'+ConceptBuild+'-'+Common.TreeName){
//				treeCombo.setValue(ConceptInfo+'-'+ConceptBuild+'-'+Common.TreeName);
//				updTree = true;
//			}
			if(Ext.isString(Common.TreeName) && treeCombo.getValue() != Common.TreeName){
				treeCombo.setValue(Common.TreeName);
				updTree = true;
			}

		}catch(e){
			console.error(e);
		}
		treeCombo.resumeEvents();
	}


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

	if(updVersion || updTree){
		Ext.defer(function(){
			if(updVersion){
				var versionCombo = Ext.getCmp('version-combobox');
				versionCombo.fireEvent('change',versionCombo,versionCombo.getValue());
				versionCombo.fireEvent('select',versionCombo,[versionCombo.findRecordByValue(versionCombo.getValue())]);
			}
			var treeCombo = Ext.getCmp('tree-combobox');
			if(treeCombo && treeCombo.rendered){
				treeCombo.fireEvent('select',treeCombo);
			}
		},250);
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
		try{
			var east_panel = Ext.getCmp('east-panel');
			east_panel.body.mask();
			east_panel.getHeader().setDisabled(true);
		}catch(e){}
	});

	$(window).bind('agrender_hideLoading'+self.event_namespace,function(){
		Ext.getCmp('render-panel').getDockedComponent('render-panel-toolbar').setDisabled(false);
		try{
			var parts_panel = Ext.getCmp('parts-panel');
			parts_panel.body.unmask();
			parts_panel.getHeader().setDisabled(false);
		}catch(e){}
		try{
			var east_panel = Ext.getCmp('east-panel');
			east_panel.body.unmask();
			east_panel.getHeader().setDisabled(false);
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

		var pickSearchAllStore = Ext.data.StoreManager.lookup('pickSearchAllStore');

		if(Ext.isEmpty(o) || Ext.isEmpty(route)){
			pickSearchAllStore.removeAll();
			Ext.data.StoreManager.lookup('pickSearchStore').removeAll();

			store.suspendEvents(false);
			store.each(function(record){
				record.set('target_record', false);
				record.commit();
			});
			store.resumeEvents();
			pallet_grid.getView().refresh();
			return false;
		}

		var selMode = pallet_grid.getSelectionModel();
		selMode.deselectAll();

		var eastTabPanel = Ext.getCmp('east-tab-panel');
		var pickPanel = Ext.getCmp('pick-panel');
		var pickSearchPanel = Ext.getCmp('pick-search-panel');

		if(pickSearchPanel && pickSearchPanel.rendered && !pickSearchPanel.isDisabled()){
			if(eastTabPanel.getActiveTab().id==pickSearchPanel.id){
				var p = pickSearchAllStore.getProxy();
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
						if(Ext.isEmpty(o.object.record.data.grouppath)){
	//						if(record.data.path==o.object.record.data.path) return true;
							if(record.data.rep_id==o.object.record.data.rep_id) return true;
						}else{
							if(
								record.data.path==o.object.record.data.path &&
								record.data.grouppath==o.object.record.data.grouppath
							) return true;
						}
					});
					if(idx>=0){
						var record = store.getAt(idx);
						p.extraParams.art_id = record.data.art_id;
					}
				}
				if(!Ext.isEmpty(p.extraParams.art_id)){
					var b = Ext.getCmp('pick-search-conditions-button');
					if(b) b.fireEvent('click',b);
					if(false){
						pickSearchPanel.setLoading(true);
						pickSearchAllStore.loadPage(1,{
							callback:function(rs, operation, success){
								var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');
								if(!success){
									pickSearchStore.removeAll();
									pickSearchPanel.setLoading(false);
									return;
								}
								pickSearchStore.on({
									load: function(){
										pickSearchPanel.setLoading(false);
									},
									single: true
								});
								pickSearchStore.loadPage(1);
							}
						});
					}
				}
			}
		}else{
			if(pickPanel && pickPanel.rendered && !pickPanel.isDisabled()){
				if(eastTabPanel.getActiveTab().id!=pickPanel.id) eastTabPanel.setActiveTab(pickPanel);
				var pickPageStore = Ext.data.StoreManager.lookup('pickPageStore');

				var pageData = [];
				Ext.each(route,function(v,i,a){
					pageData.push([i+1,i+1,v]);
				});
				try{
					pickPageStore.suspendEvents(false);
					pickPageStore.loadData(pageData);
					pickPageStore.resumeEvents();
					if(pickPanel && pickPanel.rendered){
						pickPanel.getView().refresh();
					}
				}catch(e){
					console.error(e);
					return false;
				}
			}
		}

		//Pallet上のオブジェクトを選択
		var store = pallet_grid.getStore();
		var p = store.getProxy();
		p.extraParams = p.extraParams || {};
		delete p.extraParams._pickIndex;

		var idx = store.findBy(function(record,id){
			if(Ext.isEmpty(o.object.record.data.grouppath)){
//				if(record.data.path==o.object.record.data.path) return true;
				if(record.data.rep_id==o.object.record.data.rep_id) return true;
			}else{
				if(
					record.data.path==o.object.record.data.path &&
					record.data.grouppath==o.object.record.data.grouppath
				) return true;
			}
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
		self.update_pallet_store([record],true,true);
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

//		self.update_pallet_store([record],true,true);
		var recs = self.find_pallet_store([record]);
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

	self.updateUIValueTask = new Ext.util.DelayedTask(function(){
		self.updateUIValue();
	});

	self.setHashTask = new Ext.util.DelayedTask(function(render,store,records,callback){

		var hashStr = null;
		if(render && Ext.isFunction(render.getLocationHash)) hashStr = render.getLocationHash()

		var agRender = render || self.AgRender;
		var pallet_store = store || Ext.data.StoreManager.lookup('palletPartsStore');
		var pallet_records = records || pallet_store.getRange();

		var jsonObj = self.getLocaleHashObj(hashStr);
		jsonObj = jsonObj || {};
//		console.log(jsonObj.Camera);

		//Common
		jsonObj.Common = jsonObj.Common || AgURLParser.newCommon();

		jsonObj.Common.Model = DEF_MODEL;
		var modelCombo = Ext.getCmp('model-combobox');
		if(modelCombo){
			var r = modelCombo.findRecordByValue(modelCombo.getValue());
			if(r && r.data.model) jsonObj.Common.Model = r.data.model;
		}

		jsonObj.Common.Version = DEF_VERSION;
		var versionCombo = Ext.getCmp('version-combobox');
		if(versionCombo){
			var r = versionCombo.findRecordByValue(versionCombo.getValue());
			if(r && r.data.version) jsonObj.Common.Version = r.data.version;
		}

		jsonObj.Common.TreeName = DEF_TREE;
		var treeCombo = Ext.getCmp('tree-combobox');
		if(treeCombo){
			var r = treeCombo.findRecordByValue(treeCombo.getValue());
			if(r && r.data.tree) jsonObj.Common.TreeName = r.data.tree;
		}


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
		{
			Ext.each(pallet_records,function(record,i,a){
				if(!record.get('selected')) return true;
//				if(Ext.isEmpty(record.get('rep_id')) || Ext.isEmpty(record.get('version'))) return true;
				if(Ext.isEmpty(record.get('rep_id')) || Ext.isEmpty(record.get('version')) || !Ext.isEmpty(record.get('artg_name'))) return true;

//				console.log("atrg_name=["+record.get('artg_name')+"]");
//				console.log(record.data);

				var part = AgURLParser.newPart();
				var color = record.get('color');
				if(color.substr(0,1) == '#') color = color.substr(1);
				part.PartColor = color;

//			part.PartID = record.get('b_id');
				part.PartID = record.get('cdi_name');
				part.PartName = record.get('cdi_name_e');
				part.PartOpacity = record.get('opacity');
				part.UseForBoundingBoxFlag = record.get('focused');
				part.PartDeleteFlag = record.get('remove');
				part.PartRepresentation = record.get('representation');

				part.PartScalarFlag = false;
				if(Ext.isNumber(record.get('scalar'))){
					part.PartScalar = record.get('scalar');
					part.PartScalarFlag = jsonObj.Common.ColorbarFlag;
				}

				part.PartModel = record.get('model');
				part.PartVersion = record.get('version');

//			part.PartPath = record.get('path');
				part.PartMTime = (new Date(record.get('mtime'))).getTime();

				parts.push(part);
			});
		}
//		console.log("parts=["+parts.length+"]");

		var ext_parts_hash = {};
		var ext_parts = [];
		{
			Ext.each(pallet_records,function(record,i,a){
				if(!record.get('selected')) return true;

				var groupid = record.get('artg_id');
				var groupname = record.get('artg_name');
				var grouppath = record.get('grouppath');
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
				part.PartName = record.get('name');
//				part.PartName = record.get('cdi_name_e');
				part.PartOpacity = record.get('opacity');
				part.UseForBoundingBoxFlag = record.get('focused');
//			console.log("record.get('focused')=["+record.get('focused')+"]");
				part.PartDeleteFlag = record.get('remove');
				part.PartRepresentation = record.get('representation');

				part.PartScalarFlag = false;
				if(Ext.isNumber(record.get('scalar'))){
					part.PartScalar = record.get('scalar');
					part.PartScalarFlag = jsonObj.Common.ColorbarFlag;
				}

				part.PartPath = record.get('path');
				part.PartMTime = (new Date(record.get('mtime'))).getTime();

				ext_parts_hash[groupid].PartGroupItems.push(part);
			});
			for(var groupid in ext_parts_hash){
				ext_parts.push(ext_parts_hash[groupid]);
			}
		}
//		console.log("ext_parts=["+ext_parts.length+"]");

		{/*Focus情報をクリア*/
			pallet_store.suspendEvents(false);
			pallet_store.clearFilter();
			pallet_store.filterBy(function(record,id){
				if(Ext.isEmpty(record.data.focused)) return false;
				return true;
			});
			pallet_store.each(function(record,i,a){
				record.beginEdit();
				record.set('focused',null);
				record.commit(false);
				record.endEdit(false,['focused']);
			});
			pallet_store.clearFilter();
			pallet_store.resumeEvents();
		}

		var legend = AgURLParser.newLegend();
		try{
			legend.LegendTitle    = Ext.getCmp('legend-title-textfield').getValue();
			legend.Legend         = Ext.getCmp('legend-legend-textareafield').getValue();
			legend.LegendAuthor   = Ext.getCmp('legend-author-textfield').getValue();
			legend.DrawLegendFlag = Ext.getCmp('legend-draw-checkbox').getValue();
		}catch(e){
		}

		var PinDescriptionDrawFlag = Ext.getCmp('pin-description-checkbox').getValue();
		var PinIndicationLineDrawFlag = Ext.getCmp('pin-line-combobox').getValue();
		var PinShape = Ext.getCmp('pin-shape-combobox').getValue();
		var pins = [];
		Ext.data.StoreManager.lookup('pinStore').each(function(record,i,a){
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

	self.parts_grid_selectionchange_task = new Ext.util.DelayedTask(function(){
		var parts_grid = Ext.getCmp('parts-grid');
		if(parts_grid && parts_grid.rendered){
			AgWiki.unload();
			var records = parts_grid.getSelectionModel().getSelection();
			if(records.length>0){
				var record = records[0];
				var rep_id = record.get('rep_id');
				if(rep_id){
					var tree;
					var treeCombo = Ext.getCmp('tree-combobox');
					if(treeCombo){
						var r = treeCombo.findRecordByValue(treeCombo.getValue());
						if(r && r.data.tree) tree = r.data.tree;
					}
					AgWiki.load(rep_id,tree);
				}
			}
		}
	});

	self.bp3d_search_grid_selectionchange_task = new Ext.util.DelayedTask(function(){
		var bp3d_search_grid = Ext.getCmp('bp3d-search-grid');
		if(bp3d_search_grid && bp3d_search_grid.rendered){
			AgWiki.unload();
			var records = bp3d_search_grid.getSelectionModel().getSelection();
			if(records.length>0){
				var record = records[0];
				var cdi_name = record.get('cdi_name');
				if(cdi_name){
					var tree;
					var treeCombo = Ext.getCmp('tree-combobox');
					if(treeCombo){
						var r = treeCombo.findRecordByValue(treeCombo.getValue());
						if(r && r.data.tree) tree = r.data.tree;
					}
					AgWiki.load(cdi_name,tree);
				}
			}
		}
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
			button.setDisabled(idx<0? true : false);
		}
/*
		var button = Ext.getCmp('ag-pallet-edit-button-ver2');
		button.setDisabled(true);
		if(selCount>=1){
			var idx=-1;
			Ext.each(selModel.getSelection(),function(r,i,a){
				if(Ext.isEmpty(r.get('art_id'))) return true;
				idx = i;
				return false;
			});
			button.setDisabled(idx<0? true : false);
		}
*/
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

	var model = DEF_MODEL;
	var version = DEF_VERSION;
	var tree = DEF_TREE;
	var ag_data = DEF_AG_DATA;

	var md_id;
	var mv_id;
	var mr_id;
	var ci_id;
	var cb_id;
	var bul_id;

	var field = Ext.getCmp('version-combobox');
	if(field && field.rendered){
		try{
			var record = field.findRecordByValue(field.getValue());
			if(record){
				model = record.get('model');
				version = record.get('version');
				ag_data = record.get('data');
				md_id = record.get('md_id');
				mv_id = record.get('mv_id');
				mr_id = record.get('mr_id');
				ci_id = record.get('ci_id');
				cb_id = record.get('cb_id');
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

	var field = Ext.getCmp('tree-combobox');
	if(field && field.rendered){
		try{
			var record = field.findRecordByValue(field.getValue());
			if(!record && field.getStore().getCount()){
				record = field.getStore().getAt(0);
			}
			if(record){
				tree = record.get('tree');
//				if(Ext.isEmpty(ci_id)) ci_id = record.get('ci_id');
//				if(Ext.isEmpty(cb_id)) cb_id = record.get('cb_id');
				bul_id = record.get('bul_id');
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

	var ExtVersion = Ext.getVersion()

	var current_datas = null;
	if(params.current_datas) current_datas = self.getCurrentDatas();

	return {
		model: model,
		version: version,
		ag_data: ag_data,
		tree: tree,
		md_id: md_id,
		mv_id: mv_id,
		mr_id: mr_id,
		ci_id: ci_id,
		cb_id: cb_id,
		bul_id: bul_id,
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
};

window.AgApp.prototype.getConfigLinkedUploadPartsButton = function(){
	var self = this;
	return {
		hidden: true,
		id: 'linked-upload-parts-button',
		text: '選択パーツとアップロードパーツを連動する',
		iconCls: 'pallet_link',
		enableToggle: true,
		pressed: false
	};
};

window.AgApp.prototype.getLinkedUploadPartsButton = function(){
	var self = this;
	var button = undefined;
	try{
		var config = self.getConfigLinkedUploadPartsButton();
		button = Ext.getCmp(config.id);
	}catch(e){}
	return button;
};

window.AgApp.prototype.getPressedLinkedUploadPartsButton = function(){
	var self = this;
	var config = self.getConfigLinkedUploadPartsButton();
	var pressed = config.pressed;
	try{
		var button = self.getLinkedUploadPartsButton();
		if(button && Ext.isBoolean(button.pressed)) pressed = button.pressed;
	}catch(e){}
	return pressed;
};

//他のstoreのrecordに、pallet_storeの内容を反映
window.AgApp.prototype.load_pallet_store_records = function(records,grid_store,grid){
	var self = this;

	var isCommit = false;
	var pallet_store = Ext.data.StoreManager.lookup('palletPartsStore');
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
				idx = pallet_store.findBy(function(r,id){
					if(art_id == r.get('art_id')) return true;
					return false;
				});
			}else if(rep_id !== undefined && rep_id){
				idx = pallet_store.findBy(function(r,id){
					if(rep_id == r.get('rep_id')) return true;
					return false;
				});
			}else{
				if(idx<0 && f_id && version){
					idx = pallet_store.findBy(function(r,id){
						if(f_id == r.get('f_id') && version == r.get('version')) return true;
						return false;
					});
				}
				if(idx<0 && name && group){
					idx = pallet_store.findBy(function(r,id){
						if(name == r.get('name') && group == r.get('group')) return true;
						return false;
					});
				}
			}
			var r=null;
			if(idx>=0) r = pallet_store.getAt(idx);
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
};

window.AgApp.prototype.find_pallet_store = function(records){
	var self = this;

	var pallet_store = Ext.data.StoreManager.lookup('palletPartsStore');


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

		pallet_store.each(function(r,i,a){
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

//他のstoreのrecordを使用して、pallet_storeの内容を更新
window.AgApp.prototype.update_pallet_store = function(records,queueSuspended,after_selected){
	var self = this;

	var pallet_store = Ext.data.StoreManager.lookup('palletPartsStore');

	if(Ext.isEmpty(queueSuspended)) queueSuspended = true;
	if(Ext.isEmpty(after_selected)) after_selected = false;


	var add_records = [];
	var pallet_store_add_records = [];
	var pallet_store_del_records = [];
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
		pallet_store.each(function(r,i,a){
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
			n_records.push(Ext.create(Ext.getClassName(pallet_store.model),Ext.apply({}, record.data)));
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
						pallet_store_add_records.push(n_record);
					}
					add_records.push(n_record);
				});
			}else{
				pallet_store_del_records = pallet_store_del_records.concat(n_records);
			}
		}
	});

	if(pallet_store_add_records.length){
		try{
			pallet_store.suspendEvents(queueSuspended);
			pallet_store.add(pallet_store_add_records);
			pallet_store.resumeEvents();
		}catch(e){
			console.error(e);
		}
	}
	if(pallet_store_del_records.length){
		try{
			pallet_store.suspendEvents(queueSuspended);
			pallet_store.remove(pallet_store_del_records);
			pallet_store.resumeEvents();
		}catch(e){
			console.error(e);
		}
	}


	if(after_selected){
		var pallet_grid = Ext.getCmp('pallet-grid');
		var selMode = pallet_grid.getSelectionModel();
		selMode.select(add_records);
	}

	var store;

//		store = Ext.data.StoreManager.lookup('uploadObjectAllStore');
//		store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('uploadObjectStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('partsGridStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('bp3dSearchStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('pickStore');
	store.fireEvent('datachanged',store);

	var treupd_records = [];
	store = Ext.data.StoreManager.lookup('treePanelStore');
	store.getRootNode().findChildBy(function(node){
		if(Ext.isBoolean(node.data.checked)) treupd_records.push(node);
	},this,true);
	var parts_tree_panel = Ext.getCmp('parts-tree-panel');
	self.load_pallet_store_records(treupd_records,store,parts_tree_panel);
};

window.AgApp.prototype.updata_grid_store_record = function(record,grid_store,grid){
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
};

window.AgApp.prototype.store_find_group = function(store,group){
	var self = this;

	var records = [];
	store.each(function(r,i,a){
		if(r.get('artg_name') != group) return;
		records.push(r);
	});
	return records;
};

window.AgApp.prototype.record_update = function(keys,s_record,d_record){
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
};

window.AgApp.prototype.extension_parts_store_update = function(record,addRec,queueSuspended){
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

	if(!queueSuspended) self.update_pallet_store(upd_records.concat(add_records));

};

window.AgApp.prototype.store_find = function(store,records,createNewRecord){
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
};

//pallet_storeの内容をlocalStorageに保存
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
	var self = this;
	window.location.reload(true);
};

window.AgApp.prototype.upload_group_store_load = function(store,records){
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
		if(true || self.getPressedLinkedUploadPartsButton()){
			o_store = uploadObjectAllStore;
		}else{
			o_store = upload_object_store;
		}
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
//							if(self.glb_localdb_init) self.update_pallet_store([record],false);
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
//							if(self.glb_localdb_init) self.update_pallet_store([record],false);
							upd_records.push(record);

						}

//						extension_parts_store.resumeEvents();

					}
				}
			}

			self.extension_parts_store_update(upd_records,true);
			if(self.glb_localdb_init) self.update_pallet_store(upd_records,false);

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
	var self = this;

	var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');
	var records = self.store_find_group(extension_parts_store,group);
	if(records.length>0) extension_parts_store.remove(records);
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
window.AgApp.prototype.remove_select_records_pallet_store = function(queueSuspended){
	var self = this;

	var pallet_store = Ext.data.StoreManager.lookup('palletPartsStore');

	if(Ext.isEmpty(queueSuspended)) queueSuspended = true;
	var pallet_grid = Ext.getCmp('pallet-grid');
	var selMode = pallet_grid.getSelectionModel();
	var selCount = selMode.getCount();
	if(selCount>0){
		pallet_grid.setLoading(true);
		Ext.defer(function(){

			var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');

			var records = selMode.getSelection().reverse();
			selMode.deselect(records);
			var upd_records = self.store_find(extension_parts_store,records,false);
			if(!Ext.isEmpty(upd_records)){
				extension_parts_store.suspendEvents(false);
				extension_parts_store.remove(upd_records);
				extension_parts_store.resumeEvents();
			}

			if(true || self.getPressedLinkedUploadPartsButton()){
				var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
				var upd_records = self.store_find(uploadObjectAllStore,records,false);
				if(!Ext.isEmpty(upd_records)){
					Ext.each(upd_records,function(r,i,a){
						if(!r.get('selected')) return true;
						r.beginEdit();
						r.set('selected',false)
						r.commit(true);
						r.endEdit(true,['selected']);
					});
				}
			}

			pallet_store.suspendEvents(false);
			pallet_store.remove(records);
			pallet_store.resumeEvents();
			pallet_grid.getView().refresh();

			pallet_store.fireEvent('datachanged',pallet_store);

			self.setHashTask.delay(0);
			self.update_localdb_pallet();

			var store;

			store = Ext.data.StoreManager.lookup('uploadObjectStore');
			store.fireEvent('datachanged',store);

			store = Ext.data.StoreManager.lookup('pickStore');
			store.fireEvent('datachanged',store);

			if(!self.getPressedLinkedUploadPartsButton()){
				store = Ext.data.StoreManager.lookup('partsGridStore');
				store.fireEvent('datachanged',store);

				store = Ext.data.StoreManager.lookup('bp3dSearchStore');
				store.fireEvent('datachanged',store);

				store = Ext.data.StoreManager.lookup('pickSearchStore');
				store.fireEvent('datachanged',store);

				var treupd_records = [];
				store = Ext.data.StoreManager.lookup('treePanelStore');
				store.getRootNode().findChildBy(function(node){
					if(Ext.isBoolean(node.data.checked)) treupd_records.push(node);
				},this,true);

				var parts_tree_panel = Ext.getCmp('parts-tree-panel');
				self.load_pallet_store_records(treupd_records,store,parts_tree_panel);
			}

			pallet_grid.setLoading(false);
		},100);
	}
	return selCount;
};

//pallet_storeの内容を他のstoreに反映
window.AgApp.prototype.update_other_pallet_store = function(records){
	var self = this;

//		console.log("update_other_pallet_store():["+records.length+"]");

	var extension_parts_store = Ext.data.StoreManager.lookup('extensionPartsStore');

	Ext.iterate(records,function(record,index,arr){
		if(record.get('group') && record.get('name')){
			var e_record = self.store_find(extension_parts_store,record);
			if(!e_record) e_record = Ext.create(Ext.getClassName(extension_parts_store.model),{});
			if(e_record && !e_record.get('selected')){
				extension_parts_store.suspendEvents(false);
				e_record.beginEdit();
				var modifiedFieldNames = [];
				if(Ext.isEmpty(e_record.store)){
					Ext.iterate(e_record.data,function(key,i,a){
						e_record.set(key,record.get(key));
						modifiedFieldNames.push(key);
					});
				}else{
					e_record.set('selected',true);
					modifiedFieldNames.push('selected');
				}
				e_record.commit(true);
				e_record.endEdit(true,modifiedFieldNames);
				if(Ext.isEmpty(e_record.store)) extension_parts_store.add(e_record);
				extension_parts_store.resumeEvents();
			}
		}
	});

	var store;

	store = Ext.data.StoreManager.lookup('uploadObjectStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('partsGridStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('bp3dSearchStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('pickStore');
	store.fireEvent('datachanged',store);

	store = Ext.data.StoreManager.lookup('pickSearchStore');
	store.fireEvent('datachanged',store);

	var treupd_records = [];
	store = Ext.data.StoreManager.lookup('treePanelStore');
	store.getRootNode().findChildBy(function(node){
		if(Ext.isBoolean(node.data.checked)) treupd_records.push(node);
	},this,true);

	var parts_tree_panel = Ext.getCmp('parts-tree-panel');
	self.load_pallet_store_records(treupd_records,store,parts_tree_panel);

};

window.AgApp.prototype.recalculation = function(records,force){
	var self = this;
	if(!Ext.isBoolean(force)) force = false;
	if(Ext.isEmpty(records)) records = [];
	var cdi_names = [];
	Ext.each(records,function(record,i,a){
		if(Ext.isEmpty(record.data.cdi_name)) return true;
		cdi_names.push(record.data.cdi_name);
	});
	self.openRecalculationList({
		title: force ? AgLang.recalculation_force : AgLang.recalculation,
		modal: true,
		store_params: {
			timeout: 30000*2*5,
			params: {
//				limit: 500,
				force: force,
				cdi_names: Ext.encode(cdi_names)
			}
		}
	});
};

window.AgApp.prototype.recalculation_progress_save = function(config,sessionID){
	var self = this;
	var recalcStore = Ext.data.StoreManager.lookup('recalcStore');
	config = config || {};
	config.params = config.params || {};
	var value = Ext.Object.merge({},recalcStore.getProxy().extraParams || {},config.params,{sessionID:sessionID})
	self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode(value));
};

window.AgApp.prototype.recalculation_progress = function(config,b,json){
	var self = this;
	if(Ext.isEmpty(json)){
		if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)) json = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY));
	}
	if(Ext.isEmpty(json)) return;
//	self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode(json));
//	self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode({sessionID:json.sessionID}));
	self.recalculation_progress_save(config,json.sessionID);

	var progress_msg = json.progress && json.progress.msg ? json.progress.msg : config.title + '...';
	var _progress = Ext.Msg.show({
		closable : false,
		modal    : true,
		msg      : progress_msg,
		progress : true,
		title    : config.title+'...'
	});
	_progress.updateProgress(0,'0%',progress_msg);
	_progress.center();

	if(useEventSource && EventSource){
		var evtSource = new EventSource('api-recalculation.cgi?'+Ext.Object.toQueryString({cmd: 'recalc-progress',sessionID:json.sessionID}));
		evtSource.onerror = function(e) {
			console.error(e);
		};
		evtSource.onmessage = function(e) {
			var gridpanel = b.up('window').down('gridpanel');
			var store = gridpanel.getStore();
			var view = gridpanel.getView();
			var idx;
			do{
				idx = store.findBy(function(r,id){
					return r.data.target_record;
				});
				if(idx>=0){
					var r = store.getAt(idx);
					if(r){
						r.beginEdit();
						r.set('target_record',false);
						r.commit(true);
						r.endEdit(true,['target_record']);
					}
				}
			}while(idx>=0);
			view.refresh();

			var json;
			try{json = Ext.decode(e.data)}catch(e){};
			if(success == false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
				b.up('toolbar').getComponent('ok').setDisabled(false);
				_progress.close();
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)){
					console.log('remove:'+self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
					self.AgLocalStorage.remove(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
				}
				evtSource.close();
				return;
			}
//			self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode(json));
//			self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode({sessionID:json.sessionID}));
			self.recalculation_progress_save(config,json.sessionID);

			if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
				b.up('toolbar').getComponent('ok').setDisabled(true);

				_progress.close();
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)){
					console.log('remove:'+self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
					self.AgLocalStorage.remove(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
				}
				evtSource.close();

				var tabPanle = Ext.getCmp('parts-tab-panel');
				if(tabPanle && tabPanle.rendered){
					tabPanle.items.each(function(item,index,len){
						var selRecs = item.getSelectionModel().getSelection();
						var options;
						if(selRecs.length){
							options = {
								scope: item,
								callback: function(records,operation,success){
									if(!success) return;
									var item = this;
									var selModel = item.getSelectionModel();
									selModel.select(selRecs);
								}
							};
						}
						var store = item.getStore();
						if(store.loadPage){
							var current = store.currentPage;
							store.loadPage(current,options);
						}else{
							store.load(options);
						}
						return true;

						if(tabPanel.getActiveTab().id == item.id){
						}else{
							item.on({
								activate: {
									fn: function(comp,eOpts){
									},
									single: true
								}
							});
						}
					});
				}
				self.updateArtInfo(function(){
					self.updateArtInfo();
				},Ext.data.StoreManager.lookup('uploadObjectStore'));

			}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
				b.up('toolbar').getComponent('ok').setDisabled(false);
				_progress.close();
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)){
					console.log('remove:'+self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
					self.AgLocalStorage.remove(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
				}
				evtSource.close();

				var p = {};
				p.cmd = 'recalc-cancel';
				p.sessionID = json.sessionID;
				Ext.Ajax.abort();
				Ext.Ajax.request({
					url: 'api-recalculation.cgi',
					method: 'POST',
//												timeout: 30000*2*5,
					timeout: 30000*2*5*2,
					params: p
				});

				Ext.defer(function(){
					Ext.Msg.show({
						title: config.title,
						msg: json.progress.msg,
						buttons: Ext.Msg.OK,
						icon: Ext.Msg.ERROR
					});
				},100);

				return;

			}else{
				_progress.updateProgress(json.progress.value,Math.floor(json.progress.value*100)+'%',json.progress.msg);
				_progress.center();

				idx = -1;
				var recalc_data = json.progress.recalc_data;
				if(recalc_data){
					idx = store.findBy(function(r,id){
						if(
							r.data.ci_id == recalc_data.ci_id-0  &&
							r.data.cb_id == recalc_data.cb_id-0  &&
							r.data.md_id == recalc_data.md_id-0  &&
							r.data.mv_id == recalc_data.mv_id-0  &&
							r.data.mr_id == recalc_data.mr_id-0  &&
							r.data.bul_id== recalc_data.bul_id-0 &&
							r.data.cdi_id== recalc_data.cdi_id-0
						){
							return true;
						}else{
							return false;
						}
					});
				}
				if(idx>=0){
					var r = store.getAt(idx);
					if(r){
						r.beginEdit();
						r.set('target_record',true);
						r.commit(false);
						r.endEdit(false,['target_record']);
						if(Ext.isEmpty(view.getNode(r))){
							var plugin = gridpanel.getPlugin('bufferedrenderer');
							if(plugin){
								plugin.scrollTo(idx,true,function(recordIdx,record){
										view.focusRow(recordIdx);
										view.getSelectionModel().select([record]);
//										console.log('render record: '+recordIdx);
									}
								);
							}else{
//								console.log('unknown plugin');
							}
						}else{
							view.focusRow(idx);
							view.getSelectionModel().select([r]);
//							console.log('exists record: '+idx);
						}
					}else{
//						console.log('unknown record:',idx);
					}
				}else{
//					console.log('unknown record:',recalc_data);
				}
			}
		};
	}else{
		if(Ext.isEmpty(self._TaskRunner)) self._TaskRunner = new Ext.util.TaskRunner();
		var task = self._TaskRunner.newTask({
			run: function(){
				task.stop();
				var p = {};
				p.cmd = 'recalc-progress';
				p.sessionID = json.sessionID;
				Ext.Ajax.abort();
				Ext.Ajax.request({
					url: 'api-recalculation.cgi',
					method: 'POST',
					timeout: 30000*2*5*2,
					params: p,
					callback: function(options,success,response){

						var gridpanel = b.up('window').down('gridpanel');
						var store = gridpanel.getStore();
						var view = gridpanel.getView();
						var idx;
						do{
							idx = store.findBy(function(r,id){
								return r.data.target_record;
							});
							if(idx>=0){
								var r = store.getAt(idx);
								if(r){
									r.beginEdit();
									r.set('target_record',false);
									r.commit(true);
									r.endEdit(true,['target_record']);
								}
							}
						}while(idx>=0);
						view.refresh();

						try{json = Ext.decode(response.responseText)}catch(e){};
						if(success == false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false){
							b.up('toolbar').getComponent('ok').setDisabled(false);
							_progress.close();
							if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)){
								console.log('remove:'+self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
								self.AgLocalStorage.remove(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
							}
							task.stop();
							return;
						}
//						self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode(json));
//						self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode({sessionID:json.sessionID}));
						self.recalculation_progress_save(config,json.sessionID);

						if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase()=='end'){
							b.up('toolbar').getComponent('ok').setDisabled(true);
							task.stop();
							_progress.close();
							if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)){
//								console.log('remove:'+self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
								self.AgLocalStorage.remove(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
							}

							var tabPanle = Ext.getCmp('parts-tab-panel');
							if(tabPanle && tabPanle.rendered){
								tabPanle.items.each(function(item,index,len){
									var selRecs = item.getSelectionModel().getSelection();
									var options;
									if(selRecs.length){
										options = {
											scope: item,
											callback: function(records,operation,success){
												if(!success) return;
												var item = this;
												var selModel = item.getSelectionModel();
												selModel.select(selRecs);
											}
										};
									}
									var store = item.getStore();
									if(store.loadPage){
										var current = store.currentPage;
										store.loadPage(current,options);
									}else{
										store.load(options);
									}
									return true;

									if(tabPanel.getActiveTab().id == item.id){
									}else{
										item.on({
											activate: {
												fn: function(comp,eOpts){
												},
												single: true
											}
										});
									}
								});
							}
							self.updateArtInfo(function(){
								self.updateArtInfo();
							},Ext.data.StoreManager.lookup('uploadObjectStore'));

						}else if(json.progress && Ext.isString(json.progress.msg) && json.progress.msg.toLowerCase().indexOf('error')==0){
							b.up('toolbar').getComponent('ok').setDisabled(false);
							_progress.close();
							if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)){
//								console.log('remove:'+self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
								self.AgLocalStorage.remove(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY);
							}
							task.stop();

							var p = {};
							p.cmd = 'recalc-cancel';
							p.sessionID = json.sessionID;
							Ext.Ajax.abort();
							Ext.Ajax.request({
								url: 'api-recalculation.cgi',
								method: 'POST',
								timeout: 30000*2*5*2,
								params: p
							});

							Ext.defer(function(){
								Ext.Msg.show({
									title: config.title,
									msg: json.progress.msg,
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.ERROR
								});
							},100);

							return;

						}else{
							_progress.updateProgress(json.progress.value,Math.floor(json.progress.value*100)+'%',json.progress.msg);
							_progress.center();

							idx = -1;
							var recalc_data = json.progress.recalc_data;
							if(recalc_data){
								idx = store.findBy(function(r,id){
									if(
										r.data.ci_id  == recalc_data.ci_id-0  &&
										r.data.cb_id  == recalc_data.cb_id-0  &&
										r.data.md_id  == recalc_data.md_id-0  &&
										r.data.mv_id  == recalc_data.mv_id-0  &&
										r.data.mr_id  == recalc_data.mr_id-0  &&
										r.data.bul_id == recalc_data.bul_id-0 &&
										r.data.cdi_id == recalc_data.cdi_id-0
									){
										return true;
									}else{
										return false;
									}
								});
							}
							if(idx>=0){
								var r = store.getAt(idx);
								if(r){
									r.beginEdit();
									r.set('target_record',true);
									r.commit(false);
									r.endEdit(false,['target_record']);
									if(Ext.isEmpty(view.getNode(r))){
										var plugin = gridpanel.getPlugin('bufferedrenderer');
										if(plugin){
											plugin.scrollTo(idx,true,function(recordIdx,record){
													view.focusRow(recordIdx);
													view.getSelectionModel().select([record]);
//													console.log('render record: '+recordIdx);
												}
											);
										}else{
//											console.log('unknown plugin');
										}
									}else{
										view.focusRow(idx);
										view.getSelectionModel().select([r]);
//										console.log('exists record: '+idx);
									}
								}else{
//									console.log('unknown record:',idx);
								}
							}else{
//								console.log('unknown record:',recalc_data);
							}
							task.start();
						}
					}
				});
			},
			interval: config.interval
		});
		task.start();
	}
};

window.AgApp.prototype.getSelectedSorters = function(){
	return [{
		property: 'selected',
		direction: 'DESC'
	},{
		property: 'artg_name',
		direction: 'ASC'
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
	var object_all_datas = [];
	var object_datas = [];
	var dir_datas = [];
	try{
		Ext.data.StoreManager.lookup('palletPartsStore').each(function(r){
			pallet_datas.push(Ext.apply({},r.data));
		});
	}catch(e){}
	try{
		Ext.data.StoreManager.lookup('uploadObjectAllStore').each(function(r){
			object_all_datas.push({
				art_id:r.get('art_id'),
				selected:r.get('selected')
			});
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
	try{
		Ext.data.StoreManager.lookup('uploadGroupStore').each(function(r){
			dir_datas.push({
				name:r.get('name'),
				selected:r.get('selected')
			});
		});
	}catch(e){}
	return Ext.encode({
		pallet_datas:pallet_datas,
		object_all_datas:object_all_datas,
		object_datas:object_datas,
		dir_datas:dir_datas
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

	var params = self.getExtraParams() || {};
	delete params.current_datas;
	params.art_ids = Ext.encode(art_ids);

	Ext.Ajax.request({
		url: 'get-upload-obj-info.cgi',
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

	var hideNoUse = Ext.getCmp('hide-no-use-checkbox').getValue();
	if(hideNoUse) params.cm_use = true;

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
				palletPartsStore.suspendEvents(true);
				try{palletPartsStore.add(addrecs);}catch(e){console.error(e);}
				palletPartsStore.resumeEvents();
			}

			var artg_names_selected = [];
			var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
			uploadGroupStore.suspendEvents(true);
			try{
				var filters = uploadGroupStore._getFilters();
				uploadGroupStore._setFilters([{
					anyMatch: false,
					caseSensitive: false,
					exactMatch: true,
					property: 'artg_delcause',
					value: null
				}]);

				Ext.each(json.datas,function(data,i,a){
					var r = uploadGroupStore.findRecord('artg_name',data.artg_name,0,false,true,true);
					if(r && !r.get('selected')){
						r.beginEdit();
						r.set('selected',true);
						r.endEdit(false,['selected']);
						r.commit(false);
						artg_names_selected.push(r);
					}
				});

				uploadGroupStore._setFilters(filters);

			}catch(e){console.error(e);}
			uploadGroupStore.resumeEvents();

			var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
			var sorters = self.getSelectedSorters();
			var selected_art_ids = self.getSelectedArtIds();
			if(artg_names_selected.length){
				uploadObjectStore.setLoadUploadObjectAllStoreFlag();
			}
			else{
				var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
				uploadObjectAllStore.suspendEvents(true);
				try{
					Ext.each(json.datas,function(data,i,a){
						var r = uploadObjectAllStore.findRecord('art_id',data.art_id,0,false,true,true);
						if(r && !r.get('selected')){
							r.beginEdit();
							r.set('selected',true);
							r.endEdit(false,['selected']);
							r.commit(false);
						}
					});
				}catch(e){console.error(e);}
				uploadObjectAllStore.resumeEvents();
				uploadObjectAllStore.sort(sorters);
			}
			if(options.success){
				uploadObjectStore.on({
					load: function(store,records,successful,eOpts){
						options.success(success_records);
					},
					buffer: 250,
					single: true
				});
			}
			uploadObjectStore.loadPage(1,{
				params: { selected_art_ids: Ext.encode(selected_art_ids) },
				sorters: sorters
			});
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

window.AgApp.prototype.checkedUploadGroup = function(records,keepExisting,b){
	var self = this;

	if(Ext.isEmpty(records)) return;
	if(Ext.isEmpty(keepExisting)) keepExisting = false;
	if(Ext.isEmpty(b)) b = {text: 'checkedUploadGroup'};

	if(Ext.isString(records)) records = [records];

	var panel;
	if(records[0].getOwnerTree){
		panel = records[0].getOwnerTree();
	}else{
		panel = Ext.getCmp('parts-tab-panel').getActiveTab();
	}
	if(panel){
		var loadMessage = AgLang.parts_find;
		if(records.length===1){
			var cdi_name = records[0].get('cdi_name');
			if(Ext.isString(cdi_name) && cdi_name.length ) loadMessage += ':['+cdi_name+']';
		}
		loadMessage += '...';
		panel.setLoading(loadMessage);
	}

	var rep_ids = [];
	var cdi_names = [];
	Ext.each(records,function(record,i,a){
		if(!Ext.isEmpty(record.data.cdi_name)){
			cdi_names.push({cdi_name:record.data.cdi_name});
		}
		else if(!Ext.isEmpty(record.data.rep_id)){
			rep_ids.push({rep_id:record.data.rep_id});
		}
	});

//	var params = self.getExtraParams();
	var params = {};
	if(cdi_names.length){
		params.cdi_names = Ext.encode(cdi_names);
	}else if(rep_ids.length){
		params.rep_ids = Ext.encode(rep_ids);
	}
	params.cm_use = true;

	self.getUploadObjInfo(params,{
		emptyMsg: {
			title: b.text,
			iconCls: b.iconCls,
			msg: '対応するPartsはありません',
			buttons: Ext.Msg.OK,
			icon: Ext.Msg.WARNING
		},
		empty: function(){
			if(panel) panel.setLoading(false);
		},
		success: function(){
			if(panel) panel.setLoading(false);
		},
		failure: function(){
			if(panel) panel.setLoading(false);
		}
	});

	if(keepExisting) return;

	var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
	uploadGroupStore.suspendEvents(true);

	uploadGroupStore.each(function(record){
		if(!record.get('selected')) return true;
		record.beginEdit();
		record.set('selected',false);
		record.commit(false);
		record.endEdit(false,['selected']);
	});
	uploadGroupStore.resumeEvents();

	//既存のデータをクリア
	Ext.each(['palletPartsStore','extensionPartsStore','uploadObjectStore'],function(id,i,a){
		Ext.data.StoreManager.lookup(id).removeAll(true);
	});
	var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
	palletPartsStore.fireEvent('datachanged',palletPartsStore);

	//ビューを再表示
	Ext.each(['pallet-grid','upload-object-grid'],function(id,i,a){
		var gridpanel = Ext.getCmp(id);
		gridpanel.getView().refresh();
	});

	//pallet_storeの内容をlocalStorageに保存
	self.setHashTask.delay(0);
	self.update_localdb_pallet();

};

window.AgApp.prototype.openRendererHostsMngWin = function(aOpt){
	var self = this;
	aOpt = Ext.apply({},aOpt||{},{
		iconCls: 'gear-btn',
		title: AgLang.renderer_mng,
		modal: true,
		width: 400,
		height: 250
	});

	var setDisabledSaveButton = function(gridpanel){
		var store = gridpanel.getStore();
		var num = 0;
		num += store.getModifiedRecords().length;
		num += store.getNewRecords().length;
		num += store.getRemovedRecords().length;
		num += store.getUpdatedRecords().length;
		var disable = false;
		if(!disable) disable = num===0;
		try{
			gridpanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('save').setDisabled(disable);
		}catch(e){
//			console.error(e);
		}
	};

	var renderer_mng_win = Ext.create('Ext.window.Window', {
		animateTarget: aOpt.animateTarget,
		iconCls: aOpt.iconCls,
		title: aOpt.title,
		modal: aOpt.modal,
		width: aOpt.width,
		height: aOpt.height,
		autoShow: true,
		border: false,
		closeAction: 'destroy',
		layout: 'fit',
		items: [{
			xtype: 'aggridpanel',
			store: 'rendererHostsMngStore',
			columns: [{
				xtype: 'rownumberer'
			},{
				text: AgLang.ip,
				dataIndex: 'rh_ip',
				hidden: false,
				hideable: false,
				draggable: false,
				width: 100,
				editor: {
					xtype: 'textfield',
					allowBlank: false,
					selectOnFocus: true,
					listeners: {
						specialkey: function(field, e, eOpts){
							e.stopPropagation();
						}
					}
				}
			},{
				xtype: 'checkcolumn',
				text: AgLang.use,
				dataIndex: 'rh_use',
				hidden: false,
				hideable: false,
				draggable: false,
				align: 'center',
				width: 30
			},{
				text: AgLang.comment,
				dataIndex: 'rh_comment',
				hidden: false,
				hideable: false,
				draggable: false,
				flex: 1,
				editor: {
					xtype: 'textfield',
					allowBlank: true,
					selectOnFocus: true,
					listeners: {
						specialkey: function(field, e, eOpts){
							e.stopPropagation();
						}
					}
				}
			}],
			plugins: [
				Ext.create('Ext.grid.plugin.CellEditing', {
					clicksToEdit: 1
				})
			],
			viewConfig: {
				stripeRows: true,
				enableTextSelection: false,
				loadMask: true
			},
			selType: 'rowmodel',
			selModel: {
				mode: 'SINGLE'
			},
			tbar: [{
				text: AgLang.add,
				itemId: 'add',
				iconCls: 'pallet_plus',
				listeners: {
					click: function(b){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var rec = store.add([{}]);
						gridpanel.getSelectionModel().select(rec);
					}
				}
			},'-','->','-',{
				disabled: true,
				text: AgLang.remove,
				itemId: 'remove',
				iconCls: 'pallet_delete',
				listeners: {
					click: function(b){
						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var rec = selModel.getSelection()[0]();
						if(rec){
							var store = gridpanel.getStore();
							store.remove(rec);
						}
						selModel.deselectAll();
					}
				}
			}],
			buttons: [{
				disabled: true,
				text: AgLang.save,
				itemId: 'save',
				listeners: {
					click: {
						fn: function(b){
							var win = b.up('window');
							var gridpanel = win.down('gridpanel');
							win.setLoading(true);
							var store = gridpanel.getStore();
							store.sync({
								callback: function(batch,options){
//									console.log('callback()');
									gridpanel.getSelectionModel().deselectAll();
									win.setLoading(false);
								},
								success: function(batch,options){
//									console.log('success()');
									b.setDisabled(true);
								},
								failure: function(batch,options){
//									console.log('failure()');
									var msg = AgLang.error_save;
									var proxy = this;
									var reader = proxy.getReader();
									if(reader && reader.rawData && reader.rawData.msg){
										msg += ' ['+reader.rawData.msg+']';
									}
									Ext.Msg.show({
										title: b.text,
										iconCls: b.iconCls,
										msg: msg,
										buttons: Ext.Msg.OK,
										icon: Ext.Msg.ERROR,
										fn: function(buttonId,text,opt){
										}
									});
								}
							});
						},
						buffer: 0
					}
				}
			},{
				text: AgLang.cancel,
				listeners: {
					click: function(b){
						var gridpanel = b.up('window').down('gridpanel');
						gridpanel.getSelectionModel().deselectAll();
						var store = gridpanel.getStore();
						var newRecords = store.getNewRecords();
						store.rejectChanges();
						b.previousSibling('button').setDisabled(true);

					}
				}
			}],
			listeners: {
				render: function(grid,eOpts){
//					grid.getView().on({
//						beforeitemkeydown: function(view, record, item, index, e, eOpts){
//							e.stopPropagation();
//							return false;
//						}
//					});
					grid.getStore().on({
						add: function(store,records,index,eOpts){
//							console.log('add');
							setDisabledSaveButton(this);
						},
						remove: function(store,record,index,eOpts){
							setDisabledSaveButton(this);
						},
						update: function(store,record,operation,modifiedFieldNames,eOpts){
							setDisabledSaveButton(this);
						},
						scope: grid
					});
				},
				selectionchange: function(selModel,records){
					var gridpanel = this;
					gridpanel.getDockedItems('toolbar[dock="top"]')[0].getComponent('remove').setDisabled(records[0]?false: true);
				}
			}
		}],
		buttons: [{
			text: 'Webサーバ再起動',
			iconCls: 'pallet_restart',
			listeners: {
				click: function(b){
					Ext.Msg.show({
						title: b.text,
						msg: 'Webサーバを再起動してよろしいですか？',
						iconCls: b.iconCls,
						buttons: Ext.MessageBox.OKCANCEL,
						icon: Ext.MessageBox.WARNING,
						modal: true,
						animateTarget: b.el,
						fn: function(buttonId){
							if(buttonId != 'ok') return;
							Ext.Ajax.request({
								url: 'restart_server.cgi',
								autoAbort: true,
								method: 'POST'
							})
						}
					});
				}
			}
		},'->',{
			text: AgLang.close,
			listeners: {
				click: function(b){
					b.up('window').close();
				}
			}
		}],
		listeners: {
			show: function(comp){
				comp.down('gridpanel').getStore().loadPage(1);
			}
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

	var parts_grid_column_hidden = false;
	var parts_grid_column_hideable = true;

	var parts_grid_renderer = function(value,metaData,record){
		metaData.tdCls += (record.data.rep_entry && !record.data.cm_max_entry_cdi) ? 'delete_node' : ((!record.data.rep_entry && record.data.cm_max_entry_cdi) ? 'insert_node' : '');
		return value;
	};

	var parts_grid_contextmenu = null;
	var parts_grid = Ext.create('Ext.ag.GridPanel',{
		id: 'parts-grid',
		title: AgLang.rep_list,
		border: false,
		columnLines: true,
		store: 'partsGridStore',
		stateful: true,
		stateId: 'parts-grid',
		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
		loadMask: true,
		columns: [
			{xtype: 'rownumberer',                             stateId: 'rownumberer', draggable: false},
//			{text: '&#160;',  dataIndex: 'selected', xtype: 'agselectedcheckcolumn', width: 30, hidden: true, hideable: false, sortable: true},

//			{text: 'Child',   dataIndex: 'c_num',    xtype: 'agnumbercolumn', format: self.FORMAT_INT_NUMBER, width: 32, hidden: true, hideable: true},

			{
				text: '&#160;',
				dataIndex: 'rep_density',
				stateId: 'rep_density',
				width: 30,
				hidden: false,
				hideable: false,
				resizable: false,
				draggable: false,
				renderer: function(value,metaData,record){
					return Ext.isEmpty(value) && Ext.isEmpty(record.data.rep_density_iconCls) ? '-' : '<div class="'+record.data.rep_density_iconCls+'" style="width:16px;height:16px;"> </div>';
				}
			},


			{text: 'Model', dataIndex: 'model',   stateId: 'model', width: 40, hidden: true, hideable: false, renderer: parts_grid_renderer},
			{text: 'Ver',   dataIndex: 'version', stateId: 'version', width: 40, hidden: true, hideable: false, renderer: parts_grid_renderer},

			{text: AgLang.rep_id,     dataIndex: 'rep_id',   stateId: 'rep_id', width: 80, hidden: false, hideable: true, renderer: parts_grid_renderer},
			{text: AgLang.cdi_name,   dataIndex: 'cdi_name', stateId: 'cdi_name', width: 80, hidden: false, hideable: true, renderer: parts_grid_renderer},

			{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e', stateId: 'cdi_name_e', flex: 1, minWidth: 70, hidden: false, hideable: true, renderer: parts_grid_renderer},
			{
				text: AgLang.timestamp,
				dataIndex: 'rep_entry',
				stateId: 'rep_entry',
				width: 114,
				hidden: true,
				hideable: true,
				xtype: 'datecolumn',
				format: self.FORMAT_DATE_TIME
			},
			{
				text: AgLang.modified,
				dataIndex: 'cm_max_entry_cdi',
				stateId: 'cm_max_entry_cdi',
				width: 114,
				hidden: true,
				hideable: true,
				xtype: 'datecolumn',
				format: self.FORMAT_DATE_TIME
			},
			{
				text: 'time diff',
				dataIndex: 'time_diff',
				stateId: 'time_diff',
				width: 76,
				minWidth: 76,
				hidden: true,
				hideable: true,
				xtype: 'agnumbercolumn',
				format: self.FORMAT_INT_NUMBER
			},
			{
				text: 'thumbnail',
				dataIndex: 'rep_thumb',
				stateId: 'rep_thumb',
				width: 30,
				align: 'center',
				hidden: true,
				hideable: true,
				resizable: false,
				sortable: false,
				renderer: function(value,metaData,record){
					return Ext.isEmpty(value) ? '-' : '<img src="'+value+'" style="width:16px;height:16px;" />';
				}
			},

			{
				text: AgLang.seg_name,
				dataIndex: 'seg_name',
				stateId: 'seg_name',
				width: 50,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false
			},{
				text: AgLang.seg_color,
				dataIndex: 'seg_color',
				stateId: 'seg_color',
				width: 40,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false,
				xtype: 'agcolorcolumn'
			},{
				text: AgLang.seg_thum_bgcolor,
				dataIndex: 'seg_thum_bgcolor',
				stateId: 'seg_thum_bgcolor',
				width: 40,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false,
				xtype: 'agcolorcolumn'
			},{
				text: AgLang.seg_thum_fgcolor,
				dataIndex: 'seg_thum_fgcolor',
				stateId: 'seg_thum_fgcolor',
				width: 40,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false,
				xtype: 'agcolorcolumn'
			}
		],
		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: false
		},
		selType: 'rowmodel',
		selModel: {
			mode: 'MULTI',
			listeners: {
				beforedeselect : function(rowModel,record,index,eOpts){
//					console.log("parts_grid.selmodel.beforedeselect()");
				},
				beforeselect : function(rowModel,record,index,eOpts){
//					console.log("parts_grid.selmodel.beforeselect()");
				},
				selectionchange : function(selModel,records,eOpts){
//					console.log("parts_grid.selmodel.selectionchange():["+records.length+"]");
					self.parts_grid_selectionchange_task.delay(250);
				}
			}
		},
		dockedItems: [{
			xtype: 'agpagingtoolbar',
			store: 'partsGridStore',
			dock: 'bottom',
			items: ['-',{
				id: 'parts-grid-recalculation-button',
				xtype: 'button',
				iconCls: 'pallet_calculator',
				text: AgLang.recalculation,
				listeners: {
					afterrender: function(b,eOpts){
						try{
							var combobox = Ext.getCmp('version-combobox');
							var store = combobox.getStore();
							var cb = function(){
								var mv_publish = true;
								var current_record = combobox.findRecord(combobox.valueField,combobox.getValue());
								if(current_record) mv_publish = current_record.get('mv_publish');
								b.setDisabled(mv_publish);
							};
							combobox.on('change',function(combobox, newValue, oldValue, eOpts ){
								cb();
							});
							store.on('update',function( store, record, operation, eOpts ){
								if(operation!=Ext.data.Model.COMMIT) return;
								cb();
							});
							cb();
						}catch(e){}
					},
					click: function(b){
						self.recalculation(null,false);
					}
				}
			},'-',{
				id: 'parts-grid-recalculation-force-button',
				xtype: 'button',
				iconCls: 'pallet_calculator_error',
				text: AgLang.recalculation_force,
				listeners: {
					afterrender: function(b,eOpts){
						try{
							var combobox = Ext.getCmp('version-combobox');
							var store = combobox.getStore();
							var cb = function(){
								var mv_publish = true;
								var current_record = combobox.findRecord(combobox.valueField,combobox.getValue());
								if(current_record) mv_publish = current_record.get('mv_publish');
								b.setDisabled(mv_publish);
							};
							combobox.on('change',function(combobox, newValue, oldValue, eOpts ){
								cb();
							});
							store.on('update',function( store, record, operation, eOpts ){
								if(operation!=Ext.data.Model.COMMIT) return;
								cb();
							});
							cb();
						}catch(e){}
					},
					click: function(b){
						self.recalculation(null,true);
					}
				}
			},'-']
		}],
		listeners: {
			//selectionchangeだと改ページでイベントが発生する為、itemclick時に処理を行う
			itemclick: {
				fn: function(view,record,item,index,e,eOpts){
					if(self.getPressedLinkedUploadPartsButton()) self.checkedUploadGroup(view.up('gridpanel').getSelectionModel().getSelection());
				},
				buffer:100
			},

			activate: function(gridpanel,eOpts){
				//render時に定義するactivateイベントがrenderイベント後に発生しない為、空でも定義する

				try{
					var columns = gridpanel.view.getGridColumns();
					columns.forEach(function(column){
						if(column.getXType()=='rownumberer'){
							gridpanel.view.autoSizeColumn(column);
						}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
							gridpanel.view.autoSizeColumn(column);
						}
					});
				}catch(e){
					console.error(e);
				}
			},
			render: function(grid,eOpts){
//				grid.setLoading(true);
//				grid.getView().on({
//					beforeitemkeydown: function(view, record, item, index, e, eOpts){
//						return false;
//					}
//				});

				var toggle = function(button,pressed,eOpts){
					Ext.each(grid.columns,function(column,i,a){
						if(column.dataIndex!='selected') return true;
						if(pressed){
							column.hide();
						}else{
							column.show();
						}
						return false;
					});
					grid._PressedLinkedUploadPartsButton = pressed;
				};
				var button = self.getLinkedUploadPartsButton();

				grid._PressedLinkedUploadPartsButton = self.getPressedLinkedUploadPartsButton();
				grid.on({
					activate : function(grid,eOpts){
						button.on({
							toggle: {
								fn: toggle,
								buffer: 100,
								scope: self
							}
						});
						var pressed = self.getPressedLinkedUploadPartsButton();
						if(grid._PressedLinkedUploadPartsButton == pressed) return;
						toggle(button,pressed);
					},
					deactivate : function(grid,eOpts){
						button.un({
							toggle: {
								fn: toggle,
								buffer: 100,
								scope: self
							}
						});
					}
				});
				toggle(button,grid._PressedLinkedUploadPartsButton);

			},
			containercontextmenu : function(view,e,eOpts){
				e.stopEvent();
				return false;
			},
			itemcontextmenu : {
				fn: self.showBp3dItemContextmenu,
				scope: self
			},
			afterrender: function( gridpanel, eOpts ){
				try{
					var columns = gridpanel.view.getGridColumns();
					columns.forEach(function(column){
						if(column.getXType()=='rownumberer'){
							gridpanel.view.autoSizeColumn(column);
						}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
							gridpanel.view.autoSizeColumn(column);
						}
					});
				}catch(e){
					console.error(e);
				}
				var store = gridpanel.getStore();
				store.on('load',function(store, records, successful, eOpts){
					try{
						if(successful && records.length>0){
							var columns;
							try{columns = gridpanel.view.getGridColumns();}catch(e){}
							if(Ext.isEmpty(columns)) return;
							columns.forEach(function(column){
								if(column.getXType()=='rownumberer'){
									gridpanel.view.autoSizeColumn(column);
								}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
									gridpanel.view.autoSizeColumn(column);
								}
							});
						}
					}catch(e){
						console.error(e);
					}
				},store,{
					buffer: 100
				});
			}
		}
	});



	var bp3d_search_grid_exists_parts_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		metadata.css += ' x-grid3-check-col-td';
		return '<div class="x-grid3-cc-b_id"><img src="css/bullet_'+(Ext.isEmpty(value)? 'delete' : 'picture')+'.png" width="16" height="16"/></div>';
	};


	var bp3d_search_grid_renderer = function(value,metaData,record,rowIndex,colIndex,store){
		if(Ext.isObject(metaData) && Ext.isString(metaData.tdCls)){
			metaData.tdCls += (record.data.rep_entry && !record.data.cm_max_entry_cdi) ? 'delete_node' : ((!record.data.rep_entry && record.data.cm_max_entry_cdi) ? 'insert_node' : '');
			if(self.bp3d_search_grid_renderer_params.searchRegExp !== null && !Ext.isEmpty(value)){
				value = value.replace(self.bp3d_search_grid_renderer_params.searchRegExp, function(m){
					return '<span class="' + self.bp3d_search_grid_renderer_params.matchCls + '">' + m + '</span>';
				});
			}
		}
		return value;
	};


	var bp3d_search_grid = Ext.create('Ext.ag.GridPanel',{
		id: 'bp3d-search-grid',
//		title: 'Search',
		title: 'Filtered List',
		columnLines: true,
		border: false,
		stripeRows: true,
		store: 'bp3dSearchStore',
		stateful: true,
		stateId: 'bp3d-search-grid',
		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
//		features: [get_grid_filters()],
		loadMask: false,
		columns: [
			{xtype: 'rownumberer',                             stateId: 'rownumberer', draggable: false},
//			{text: '&#160;',            dataIndex: 'selected',    width: 30, minWidth: 30, hidden: true, hideable: false, sortable: false, xtype: 'agselectedcheckcolumn'},
//			{text: '&#160',             dataIndex: 'rep_id',      width: 30, minWidth: 30, hidden: false, hideable: false, sortable: true,  renderer:bp3d_search_grid_exists_parts_renderer},
			{
				text: '&#160;',
				dataIndex: 'rep_density',
				stateId: 'rep_density',
				width: 30,
				hidden: false,
				hideable: false,
				resizable: false,
				draggable: false,
				renderer: function(value,metaData,record){
					return Ext.isEmpty(value) && Ext.isEmpty(record.data.rep_density_iconCls) ? '-' : '<div class="'+record.data.rep_density_iconCls+'" style="width:16px;height:16px;"> </div>';
				}
			},

			{text: 'Model', dataIndex: 'model',   stateId: 'model', width: 40, hidden: true, hideable: false, renderer: parts_grid_renderer},
			{text: 'Ver',   dataIndex: 'version', stateId: 'version', width: 40, hidden: true, hideable: false, renderer: parts_grid_renderer},

			{text: AgLang.rep_id,     dataIndex: 'rep_id',   stateId: 'rep_id', width: 80, hidden: false, hideable: true, renderer: parts_grid_renderer},
			{text: AgLang.cdi_name,   dataIndex: 'cdi_name', stateId: 'cdi_name', width: 80, hidden: false, hideable: true, renderer: parts_grid_renderer},

			{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e', stateId: 'cdi_name_e', flex: 1, minWidth: 70, hidden: false, hideable: true, renderer: parts_grid_renderer},
			{
				text: AgLang.timestamp,
				dataIndex: 'rep_entry',
				stateId: 'rep_entry',
				width: 114,
				hidden: true,
				hideable: true,
				xtype: 'datecolumn',
				format: self.FORMAT_DATE_TIME
			},
			{
				text: AgLang.modified,
				dataIndex: 'cm_max_entry_cdi',
				stateId: 'cm_max_entry_cdi',
				width: 114,
				hidden: true,
				hideable: true,
				xtype: 'datecolumn',
				format: self.FORMAT_DATE_TIME
			},
			{
				text: 'time diff',
				dataIndex: 'time_diff',
				stateId: 'time_diff',
				width: 76,
				minWidth: 76,
				hidden: true,
				hideable: true,
				xtype: 'agnumbercolumn',
				format: self.FORMAT_INT_NUMBER
			},

			{
				text: AgLang.seg_name,
				dataIndex: 'seg_name',
				stateId: 'seg_name',
				width: 50,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false
			},{
				text: AgLang.seg_color,
				dataIndex: 'seg_color',
				stateId: 'seg_color',
				width: 40,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false,
				xtype: 'agcolorcolumn'
			},{
				text: AgLang.seg_thum_bgcolor,
				dataIndex: 'seg_thum_bgcolor',
				stateId: 'seg_thum_bgcolor',
				width: 40,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false,
				xtype: 'agcolorcolumn'
			},{
				text: AgLang.seg_thum_fgcolor,
				dataIndex: 'seg_thum_fgcolor',
				stateId: 'seg_thum_fgcolor',
				width: 40,
				hidden: true,
				hideable: true,
				sortable: true,
				resizable: false,
				xtype: 'agcolorcolumn'
			}

		],


		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: false
		},

		selType: 'rowmodel',
		selModel: {
			mode: 'MULTI',
			listeners: {
				beforedeselect : function(rowModel,record,index,eOpts){
//					console.log("bp3d_search_grid.selmodel.beforedeselect()");
				},
				beforeselect : function(rowModel,record,index,eOpts){
//					console.log("bp3d_search_grid.selmodel.beforeselect()");
				},
				selectionchange : function(selModel,records,eOpts){
//					console.log("bp3d_search_grid.selmodel.selectionchange():["+records.length+"]");
					self.bp3d_search_grid_selectionchange_task.delay(250);
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
				listeners: {
					beforerender: function(searchfield, eOpt){
					},
					afterrender: function(searchfield, eOpt){
						searchfield.inputEl.set({autocomplete: 'on'});
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
			xtype: 'agpagingtoolbar',
			store: 'bp3dSearchStore',
			dock: 'bottom',
			items: ['-',{
				id: 'bp3d-search-grid-recalculation-button',
				xtype: 'button',
				iconCls: 'pallet_calculator',
				text: AgLang.recalculation,
				listeners: {
					afterrender: function(b,eOpts){
						try{
							var combobox = Ext.getCmp('version-combobox');
							var store = combobox.getStore();
							var cb = function(){
								var mv_publish = true;
								var current_record = combobox.findRecord(combobox.valueField,combobox.getValue());
								if(current_record) mv_publish = current_record.get('mv_publish');
								b.setDisabled(mv_publish);
							};
							combobox.on('change',function(combobox, newValue, oldValue, eOpts ){
								cb();
							});
							store.on('update',function( store, record, operation, eOpts ){
								if(operation!=Ext.data.Model.COMMIT) return;
								cb();
							});
							cb();
						}catch(e){}
					},
					click: function(b){
						self.recalculation(null,false);
					}
				}
			},'-',{
				id: 'bp3d-search-grid-recalculation-force-button',
				xtype: 'button',
				iconCls: 'pallet_calculator_error',
				text: AgLang.recalculation_force,
				listeners: {
					afterrender: function(b,eOpts){
						try{
							var combobox = Ext.getCmp('version-combobox');
							var store = combobox.getStore();
							var cb = function(){
								var mv_publish = true;
								var current_record = combobox.findRecord(combobox.valueField,combobox.getValue());
								if(current_record) mv_publish = current_record.get('mv_publish');
								b.setDisabled(mv_publish);
							};
							combobox.on('change',function(combobox, newValue, oldValue, eOpts ){
								cb();
							});
							store.on('update',function( store, record, operation, eOpts ){
								if(operation!=Ext.data.Model.COMMIT) return;
								cb();
							});
							cb();
						}catch(e){}
					},
					click: function(b){
						self.recalculation(null,true);
					}
				}
			},'-']
		}],

		listeners: {
			itemclick: {
				fn: function(view,record,item,index,e,eOpts){
					if(self.getPressedLinkedUploadPartsButton()) self.checkedUploadGroup(view.up('gridpanel').getSelectionModel().getSelection());
				},
				buffer:100
			},

			activate: function(gridpanel,eOpts){
				//render時に定義するactivateイベントがrenderイベント後に発生しない為、空でも定義する

				try{
					var columns = gridpanel.view.getGridColumns();
					columns.forEach(function(column){
						if(column.getXType()=='rownumberer'){
							gridpanel.view.autoSizeColumn(column);
						}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
							gridpanel.view.autoSizeColumn(column);
						}
					});
				}catch(e){
					console.error(e);
				}
			},
			render: function(grid,eOpts){
//				grid.getView().on({
//					beforeitemkeydown: function(view, record, item, index, e, eOpts){
//						return false;
//					}
//				});

				var toggle = function(button,pressed,eOpts){
					Ext.each(grid.columns,function(column,i,a){
						if(column.dataIndex!='selected') return true;
						if(pressed){
							column.hide();
						}else{
							column.show();
						}
						return false;
					});
					grid._PressedLinkedUploadPartsButton = pressed;
				};
				var button = self.getLinkedUploadPartsButton();

				grid._PressedLinkedUploadPartsButton = self.getPressedLinkedUploadPartsButton();
				grid.on({
					activate : function(grid,eOpts){
						button.on({
							toggle: {
								fn: toggle,
								buffer: 100,
								scope: self
							}
						});
						var pressed = self.getPressedLinkedUploadPartsButton();
						if(grid._PressedLinkedUploadPartsButton == pressed) return;
						toggle(button,pressed);
					},
					deactivate : function(grid,eOpts){
						button.un({
							toggle: {
								fn: toggle,
								buffer: 100,
								scope: self
							}
						});
					}
				});
				toggle(button,grid._PressedLinkedUploadPartsButton);

			},
			containercontextmenu : function(view,e,eOpts){
				e.stopEvent();
				return false;
			},
			itemcontextmenu : {
				fn: self.showBp3dItemContextmenu,
				scope: self
			},
			afterrender: function( gridpanel, eOpts ){
				try{
					var columns = gridpanel.view.getGridColumns();
					columns.forEach(function(column){
						if(column.getXType()=='rownumberer'){
							gridpanel.view.autoSizeColumn(column);
						}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
							gridpanel.view.autoSizeColumn(column);
						}
					});
				}catch(e){
					console.error(e);
				}
				var store = gridpanel.getStore();
				store.on('load',function(store, records, successful, eOpts){
					try{
						if(successful && records.length>0){
							var columns;
							try{columns = gridpanel.view.getGridColumns();}catch(e){}
							if(Ext.isEmpty(columns)) return;
							columns.forEach(function(column){
								if(column.getXType()=='rownumberer'){
									gridpanel.view.autoSizeColumn(column);
								}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
									gridpanel.view.autoSizeColumn(column);
								}
							});
						}
					}catch(e){
						console.error(e);
					}
				},store,{
					buffer: 100
				});
			}
		}
	});

	var parts_tree_panel_column_renderer = function(value,metaData,record,rowIndex,colIndex,store){
		metaData.tdCls += (record.data.rep_entry && !record.data.cm_max_entry_cdi) ? 'delete_node' : ((!record.data.rep_entry && record.data.cm_max_entry_cdi) ? 'insert_node' : '');
		if(Ext.isDate(value)) value = Ext.util.Format.date(value,self.FORMAT_DATE_TIME);
		return value;
	};

	var parts_tree_panel = Ext.create('Ext.tree.Panel',{
		id: 'parts-tree-panel',
		title: 'Tree',
		rootVisible: false,
		rowLines: false,
		border: false,
		animate: false,
		store: 'treePanelStore',
		stateful: true,
		stateId: 'parts-tree-panel',
		selModel: {
			allowDeselect: true,
			mode: 'SINGLE'
		},
		viewConfig: {
			loadMask: false
		},
		plugins: [{
			ptype: 'bufferedrenderer'
		}],
		hideHeaders: false,
		columns: [{
			xtype: 'treecolumn',
			text: AgLang.cdi_name_e,
			flex: 1,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			dataIndex: 'text',
			stateId: 'text'
		},{
			text: AgLang.rep_id,
			width: 60,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			dataIndex: 'rep_id',
			stateId: 'rep_id',
			renderer: parts_tree_panel_column_renderer
		},{
			text: AgLang.cdi_name,
			width: 80,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			dataIndex: 'cdi_name',
			stateId: 'cdi_name',
			renderer: parts_tree_panel_column_renderer
		},{
			text: AgLang.timestamp,
			dataIndex: 'rep_entry',
			stateId: 'rep_entry',
			width: 114,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			xtype: 'datecolumn',
			renderer: parts_tree_panel_column_renderer
		},{
			text: AgLang.modified,
			dataIndex: 'cm_max_entry_cdi',
			stateId: 'cm_max_entry_cdi',
			width: 114,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			xtype: 'datecolumn',
			renderer: parts_tree_panel_column_renderer
		},{
			text: AgLang.seg_name,
			dataIndex: 'seg_name',
			stateId: 'seg_name',
			width: 50,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false
		},{
			text: AgLang.seg_color,
			dataIndex: 'seg_color',
			stateId: 'seg_color',
			width: 40,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			xtype: 'agcolorcolumn'
		},{
			text: AgLang.seg_thum_bgcolor,
			dataIndex: 'seg_thum_bgcolor',
			stateId: 'seg_thum_bgcolor',
			width: 40,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			xtype: 'agcolorcolumn'
		},{
			text: AgLang.seg_thum_fgcolor,
			dataIndex: 'seg_thum_fgcolor',
			stateId: 'seg_thum_fgcolor',
			width: 40,
			hidden: true,
			hideable: true,
			sortable: false,
			resizable: false,
			xtype: 'agcolorcolumn'
		}],
		dockedItems: [{
			dock: 'bottom',
			xtype: 'toolbar',
			items: [{
				disabled: true,
				id: 'parts-tree-collapse-all-button',
				xtype: 'button',
				text: 'Collapse All',
				listeners: {
					click: function(b){
						var toolbar = b.up('toolbar');
						b.setDisabled(true);
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						if(selModel) selModel.deselectAll();
						treepanel.collapseAll(function(){

							var treeCombo = Ext.getCmp('tree-combobox');
							var record = treeCombo.findRecordByValue(treeCombo.getValue());
							if(record){
								var bul_id = record.get('bul_id');
								if(bul_id){
									var obj = {};
									if(self.AgLocalStorage.exists(self.DEF_LOCALDB_TREE_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_TREE_INFO));
									obj['expand'] = obj['expand'] || {};
									obj['selected'] = obj['selected'] || {};
									obj['selected'][bul_id] = {};
									obj['expand'][bul_id] = {};
									self.AgLocalStorage.save(self.DEF_LOCALDB_TREE_INFO,Ext.encode(obj));
								}
							}

//							b.setDisabled(false);
						});
					}
				}
			},'-','->','-',{
				id: 'parts-tree-recalculation-button',
				xtype: 'button',
				iconCls: 'pallet_calculator',
				text: AgLang.recalculation,
				listeners: {
					afterrender: function(b,eOpts){
						try{
							var combobox = Ext.getCmp('version-combobox');
							var store = combobox.getStore();
							var cb = function(){
								var mv_publish = true;
								var current_record = combobox.findRecord(combobox.valueField,combobox.getValue());
								if(current_record) mv_publish = current_record.get('mv_publish');
								b.setDisabled(mv_publish);
							};
							combobox.on('change',function(combobox, newValue, oldValue, eOpts ){
								cb();
							});
							store.on('update',function( store, record, operation, eOpts ){
								if(operation!=Ext.data.Model.COMMIT) return;
								cb();
							});
							cb();
						}catch(e){}
					},
					click: function(b){
						self.recalculation(null,false);
					}
				}
			},'-',{
				id: 'parts-tree-recalculation-force-button',
				xtype: 'button',
				iconCls: 'pallet_calculator_error',
				text: AgLang.recalculation_force,
				listeners: {
					afterrender: function(b,eOpts){
						try{
							var combobox = Ext.getCmp('version-combobox');
							var store = combobox.getStore();
							var cb = function(){
								var mv_publish = true;
								var current_record = combobox.findRecord(combobox.valueField,combobox.getValue());
								if(current_record) mv_publish = current_record.get('mv_publish');
								b.setDisabled(mv_publish);
							};
							combobox.on('change',function(combobox, newValue, oldValue, eOpts ){
								cb();
							});
							store.on('update',function( store, record, operation, eOpts ){
								if(operation!=Ext.data.Model.COMMIT) return;
								cb();
							});
							cb();
						}catch(e){}
					},
					click: function(b){
						self.recalculation(null,true);
					}
				}
			},'-','-',{
				xtype: 'button',
				iconCls: 'x-tbar-loading',
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
//						var viewDom = treepanel.getView().el.dom;
//						var scX = viewDom.scrollLeft;
//						var scY = viewDom.scrollTop;
						var store = treepanel.getStore();
//						var reload_result = function(records,operation,success){
//							if(!success) return;
//							console.log(this.tree.treeStore.isLoading());
//							console.log(this);
//							if(this.isLoading()){
//								this.on({
//									load: reload_result,
//									single: true
//								});
//							}
//							else{
//								console.log('OK!!');
//							}
//						};
//						store.load({
//							callback: reload_result,
//							scope: store
//						});

//						store.load();

						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							store.load({node:node});
						}else{
							store.load();
						}

					}
				}
			}]
		}],
		listeners: {
			activate: function(comp,eOpts){
				//render時に定義するactivateイベントがrenderイベント後に発生しない為、空でも定義する
			},
			afterrender: function(comp,eOpts){
//				console.log('afterrender():['+comp.id+']');
			},
			beforerender: function(comp,eOpts){
//				console.log('beforerender():['+comp.id+']');
			},
			beforeload: function(store,eOpts){
//				console.log('beforeload():['+this.id+']');
			},
			load: function(store, node, records, successful, eOpts){
//				console.log('load():['+this.id+']');
			},
			render: function(comp,eOpts){
//				console.log('render():['+comp.id+']');
				var toggle = function(button,pressed,eOpts){
					comp.getStore().load();
					comp._PressedLinkedUploadPartsButton = pressed;
				};
				var button = self.getLinkedUploadPartsButton();
				comp._PressedLinkedUploadPartsButton = self.getPressedLinkedUploadPartsButton();
				comp.on({
					activate : function(comp,eOpts){
						button.on({
							toggle: {
								fn: toggle,
								buffer: 100,
								scope: self
							}
						});
						var pressed = self.getPressedLinkedUploadPartsButton();
						if(comp._PressedLinkedUploadPartsButton == pressed) return;
						toggle(button,pressed);
					},
					deactivate : function(comp,eOpts){
						button.un({
							toggle: {
								fn: toggle,
								buffer: 100,
								scope: self
							}
						});
					}
				});
			},
			checkchange: {
				fn: function(node, checked, eOpts){
					if(self.getPressedLinkedUploadPartsButton()){
						self.checkedUploadGroup([node]);
					}else{
						self.update_pallet_store([node]);
//						self.checkedUploadGroup([node],true);
					}
				},
				buffer:100
			},
			selectionchange: {
				fn: function(selModel, records, eOpts){
//					AgWiki.unload();
//					if(records.length>0){
//						var record = records[0];
//						var cdi_name = record.get('cdi_name');
//						if(cdi_name){
//							var tree;
//							var treeCombo = Ext.getCmp('tree-combobox');
//							if(treeCombo){
//								var r = treeCombo.findRecordByValue(treeCombo.getValue());
//								if(r && r.data.tree) tree = r.data.tree;
//							}
//							AgWiki.load(cdi_name,tree);
//						}
//					}
					if(self.getPressedLinkedUploadPartsButton()) self.checkedUploadGroup(records);
				},
				buffer:100
			},
			deselect: function(selModel,record,index,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_TREE_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_TREE_INFO));
				obj['selected'] = obj['selected'] || {};
				var bul_id = record.get('bul_id');
				delete obj['selected'][bul_id];
				self.AgLocalStorage.save(self.DEF_LOCALDB_TREE_INFO,Ext.encode(obj));
			},
			select: function(selModel,record,index,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_TREE_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_TREE_INFO));
				obj['selected'] = obj['selected'] || {};
				var bul_id = record.get('bul_id');
				obj['selected'][bul_id] = record.getPath('cdi_name');
				self.AgLocalStorage.save(self.DEF_LOCALDB_TREE_INFO,Ext.encode(obj));
			},
			itemappend: function(node,newNode,index,eOpts){
				if(!newNode.isExpanded()){
					var obj = {};
					if(self.AgLocalStorage.exists(self.DEF_LOCALDB_TREE_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_TREE_INFO));
					obj['expand'] = obj['expand'] || {};
					obj['selected'] = obj['selected'] || {};
					var bul_id = newNode.get('bul_id');
					obj['expand'][bul_id] = obj['expand'][bul_id] || {};
					if(obj['expand'][bul_id][newNode.getPath('cdi_name')] || node.internalId=='root'){
//						newNode.expand();
					}
				}
			},
			itemcollapse: function(node,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_TREE_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_TREE_INFO));
				obj['expand'] = obj['expand'] || {};
				var bul_id = node.get('bul_id');
				obj['expand'][bul_id] = obj['expand'][bul_id] || {};
				delete obj['expand'][bul_id][node.getPath('cdi_name')];
				self.AgLocalStorage.save(self.DEF_LOCALDB_TREE_INFO,Ext.encode(obj));

				Ext.defer(function(){
					node.collapseChildren(true);
				},100);
			},
			itemexpand: function(node,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_TREE_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_TREE_INFO));
				obj['expand'] = obj['expand'] || {};
				var bul_id = node.get('bul_id');
				obj['expand'][bul_id] = obj['expand'][bul_id] || {};
				obj['expand'][bul_id][node.getPath('cdi_name')] = true;
				self.AgLocalStorage.save(self.DEF_LOCALDB_TREE_INFO,Ext.encode(obj));

				Ext.getCmp('parts-tree-collapse-all-button').setDisabled(false);
			},
			iteminsert: function(node,insNode,refNode,eOpts){
			},
			itemcontextmenu : {
				fn: self.showBp3dItemContextmenu,
				scope: self
			}
		}
	});

	north_panel = {
		id: 'north-panel',
		region: 'north',
		height:26,
		border: false,
		dockedItems: [{
			hidden: false,
			xtype: 'toolbar',
			dock: 'top',
			layout: {
				overflowHandler: 'Menu'
			},
			items:[{
				hidden: true,
				id: 'model-combobox',
				fieldLabel: AgLang.model,
				labelWidth: 32,
				width: 200,
				xtype: 'combobox',
				editable: false,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				value: DEF_MODEL,
				store: 'modelStore',
				listeners: {
					afterrender: function(field, eOpts){
//						console.log("afterrender():["+field.id+"]");
					},
					select: function(field, records, eOpts){
//						console.log("select():["+field.id+"]["+field.getValue()+"]");
						var value = field.getValue();

						var versionCombo = Ext.getCmp('version-combobox');
						var versionStore = Ext.data.StoreManager.lookup('versionStore');
						versionCombo.suspendEvents(true);
						versionCombo.setValue('');
						versionStore.clearFilter(true);
						versionStore.filter([{
							property: 'model',
							value: value
						}]);
						var r = versionStore.getAt(0);
						versionCombo.setDisabled(Ext.isEmpty(r));
						if(!versionCombo.isDisabled()) versionCombo.setValue(r.data.value);
						versionCombo.resumeEvents();

						var treeCombo = Ext.getCmp('tree-combobox');
						var treeStore = Ext.data.StoreManager.lookup('treeStore');
						treeCombo.suspendEvents(true);
						treeCombo.setValue('');
//						treeStore.clearFilter(true);
//						treeStore.filter([{
//							property: 'model',
//							value: value
//						}]);
						var r = treeStore.getAt(0);
						treeCombo.setDisabled(Ext.isEmpty(r));
						if(!treeCombo.isDisabled()) treeCombo.setValue(r.data.value);
						treeCombo.resumeEvents();


//						var Ext.getCmp('version-combobox').getStore();
//						var Ext.getCmp('tree-combobox').getStore();
						var store = Ext.data.StoreManager.lookup('partsGridStore');
						store.load();

						Ext.defer(function(){Ext.data.StoreManager.lookup('fmaAllStore').loadPage(1);},250);
					}
				}
			},{
				hidden: false,
				id: 'version-combobox',
				fieldLabel: AgLang.version,
//				labelWidth: 38,
				labelWidth: 46,
//				width: 88,
//				width: 120,
//				width: 128,
//				width: 230,
//				width: 250,
				width: 350,
				xtype: 'combobox',
				editable: false,
				matchFieldWidth: false,
				listConfig: {
//					minWidth: 60,
//					width: 60
//					width: 179
//					width: 199
					minWidth: 300
				},
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
//				store: 'datasetStore',
				store: 'datasetMngStore',
				listeners: {
					afterrender: function(field, eOpts){
//						console.log("afterrender():["+field.id+"]");

						var modelValue = DEF_MODEL;
						var rec;
						var modelCombo = Ext.getCmp('model-combobox');
						if(modelCombo) modelValue = modelCombo.getValue();
						if(modelValue) rec = modelCombo.findRecordByValue(modelValue);
						var store = field.getStore();

//						field.suspendEvents(true);
//						field.setValue('');
						store.clearFilter(true);
						if(rec){
							store.filter([{
								property: 'md_id',
								value: rec.data.md_id
							}]);
						}else{
							store.filter([{
								property: 'model',
								value: modelValue
							}]);
						}
//						var r = store.getAt(0);
//						field.setDisabled(Ext.isEmpty(r));
//						if(!field.isDisabled()) field.setValue(r.data.value);
//						field.resumeEvents();

						store.on({
							load: function(store,records,successful,eOpts){
								var field = this;
								field.fireEvent('change',field,field.getValue());
							},
							update: function(store,record,operation,modifiedFieldNames,eOpts){
								var field = this;
								field.fireEvent('change',field,field.getValue());
							},
							scope: field
						});

						store.load({
							scope: this,
							callback: function(records,operation,success){
								var r = records[0];
								field.setDisabled(Ext.isEmpty(r));
								if(!field.isDisabled()){
									field.setValue(r.data.value);
//									field.fireEvent('select',field,[r]);

									field = Ext.getCmp('tree-combobox');
									var treeStore = field.getStore();
//									Ext.data.StoreManager.lookup('treeStore').load({
									treeStore.removeAll();
									field.setValue('');
									field.clearInvalid();
									treeStore.load({
										scope: this,
										callback: function(records,operation,success){
											var r = records ? records[0] : null;
											field.setDisabled(Ext.isEmpty(r));
											if(!field.isDisabled()){
//												field.setValue(r.data.value);
												if(self.glb_localdb_init){
													field.setValue(r.data.value);
//													Ext.data.StoreManager.lookup('treePanelStore').load();
//													Ext.data.StoreManager.lookup('partsGridStore').load();

													field.fireEvent('select',field,[r]);
												}else{
//													field.up('toolbar').getComponent('mv_frozen').update(r.get('mv_frozen') ?  AgLang.not_editable_state : AgLang.editable);
//													field.up('toolbar').getComponent('mv_publish').update(r.get('mv_publish') ? AgLang.publish_state : AgLang['private']);
												}
											}else{
												field.setValue('');
											}

											Ext.defer(function(){Ext.data.StoreManager.lookup('fmaAllStore').loadPage(1);},250);


										}
									});
								}
							}
						});
					},
					change: function(field,newValue,oldValue,eOpts){
//						console.log("change():["+field.id+"]");

						var toolbar = field.up('toolbar');
						if(toolbar){
							var r = field.findRecordByValue(newValue);
							if(r){
								toolbar.getComponent('mv_frozen').update(r.get('mv_frozen') ?  AgLang.not_editable_state : AgLang.editable);
								toolbar.getComponent('mv_publish').update(r.get('mv_publish') ? AgLang.publish_state : AgLang['private']);
							}else{
								toolbar.getComponent('mv_frozen').update('');
								toolbar.getComponent('mv_publish').update('');
							}
						}
					},
					select: function(field, records, eOpts){
//						console.log("select():["+field.id+"]");
						self.setHashTask.delay(0);
						Ext.data.StoreManager.lookup('treePanelStore').load();
						Ext.data.StoreManager.lookup('partsGridStore').loadPage(1);
						Ext.data.StoreManager.lookup('bp3dSearchStore').loadPage(1);
						Ext.data.StoreManager.lookup('fmaAllStore').loadPage(1);
//						Ext.data.StoreManager.lookup('conflictListStore').loadPage(1);
						Ext.data.StoreManager.lookup('mapListStore').loadPage(1);

						var waitPalletMask;
						var grid = Ext.getCmp('pallet-grid');
						if(grid && grid.rendered){
							waitPalletMask = new Ext.LoadMask({target:grid,msg:"Please wait..."});
							waitPalletMask.show();
						}
						self.updateArtInfo(function(){
							var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
							var selected_art_ids = self.getSelectedArtIds();
							if(waitPalletMask){
								uploadObjectStore.on({
									load: function(store,records,successful,eOpts){
										waitPalletMask.hide();
									},
									single: true,
									scope: self
								});
							}
							uploadObjectStore.loadPage(1,{
								params: { selected_art_ids: Ext.encode(selected_art_ids) },
								sorters: uploadObjectStore.getUploadObjectLastSorters()
							});
						});
					}
				}
			},{
				hidden: false,
				xtype: 'tbseparator'
			},{
				hidden: false,
				xtype: 'tbtext',
				itemId: 'mv_frozen'
			},{
				hidden: false,
				xtype: 'tbseparator'
			},{
				hidden: false,
				xtype: 'tbtext',
				itemId: 'mv_publish'
			},{
				hidden: false,
				xtype: 'tbseparator'
			},{
				disabled: false,
				xtype: 'button',
				iconCls: 'gear-btn',
				text: AgLang.concept_mng,
				listeners: {
					click: {
						fn: function(b,e,o){
							self.openConceptMngWin({
								animateTarget: b.el,
								iconCls: b.iconCls,
								title: b.text
							});
						},
						buffer:0
					}
				}
			},{
				hidden: false,
				xtype: 'tbseparator'
			},{
				disabled: false,
				xtype: 'button',
				iconCls: 'gear-btn',
				text: AgLang.dataset_mng,
				listeners: {
					click: {
						fn: function(b,e,o){
							self.openDatasetMngWin({
								animateTarget: b.el,
								iconCls: b.iconCls,
								title: b.text
							});
						},
						buffer:0
					}
				}
			},{
				hidden: false,
				xtype: 'tbseparator'
			},{

				id: 'tree-combobox',
				fieldLabel: AgLang.tree,
				labelWidth: 26,
//				width: 150,
				width: 100,
				xtype: 'agcombobox',
				editable: false,
				matchFieldWidth: false,
				listConfig: {
//					minWidth: 102,
//					width: 102
					minWidth: 52,
					width: 52
				},
//						value: DEF_TREE_COMBO,
				value: null,
				store: 'treeStore',
				listeners: {
					afterrender: function(field, eOpts){
						var store = field.getStore();
						store.load({
							scope: this,
							callback: function(records,operation,success){
								var r = records[0];
								field.setDisabled(Ext.isEmpty(r));
								if(!field.isDisabled()){
									if(self.glb_localdb_init){
										field.setValue(r.data.value);
										Ext.data.StoreManager.lookup('treePanelStore').load();
										Ext.data.StoreManager.lookup('partsGridStore').loadPage(1);
									}
								}
							}
						});

//						Ext.data.StoreManager.lookup('treePanelStore').load();
//						Ext.data.StoreManager.lookup('partsGridStore').load();
////								Ext.data.StoreManager.lookup('bp3dSearchStore').load();

					},
					select: function(field, records, eOpts){
//								console.log("select():["+field.id+"]");

						var store = field.getStore();
						if(store.getCount()>0){
							self.setHashTask.delay(0);
							Ext.data.StoreManager.lookup('treePanelStore').load();
							Ext.data.StoreManager.lookup('partsGridStore').loadPage(1);
							Ext.data.StoreManager.lookup('bp3dSearchStore').loadPage(1);

							var waitPalletMask;
							var grid = Ext.getCmp('pallet-grid');
							if(grid && grid.rendered){
								waitPalletMask = new Ext.LoadMask({target:grid,msg:"Please wait..."});
								waitPalletMask.show();
							}
							self.updateArtInfo(function(){
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
								var selected_art_ids = self.getSelectedArtIds();
								if(waitPalletMask){
									uploadObjectStore.on({
										load: function(store,records,successful,eOpts){
											waitPalletMask.hide();
										},
										single: true,
										scope: self
									});
								}
								uploadObjectStore.loadPage(1,{
									params: { selected_art_ids: Ext.encode(selected_art_ids) },
									sorters: uploadObjectStore.getUploadObjectLastSorters()
								});
							});

						}else{
							store.load({
								scope: this,
								callback: function(records,operation,success){
									self.setHashTask.delay(0);
									Ext.data.StoreManager.lookup('treePanelStore').load();
									Ext.data.StoreManager.lookup('partsGridStore').loadPage(1);
									Ext.data.StoreManager.lookup('bp3dSearchStore').loadPage(1);
								}
							});
						}
					}
				}



			},'-',{
				disabled: true,
				id: 'error-twitter-button',
				text: AgLang.error_twitter,
				iconCls: 'btweet',
				listeners: {
					render: function(b){
						var treeCombobox = Ext.getCmp('tree-combobox');
						var treeStore = treeCombobox.getStore();
						if(treeStore.getCount()==0){
							b.setDisabled(true);
							treeStore.on({
								load: {
									fn: function(){
										b.setDisabled(false);
									},
									buffer: 100,
									single: true
								}
							});
						}else{
							b.setDisabled(false);
						}
					},
					click: function(b){
						if(b.isDisabled()) return;
						b.setDisabled(true);
						Ext.defer(function(){
							self.openErrorTwitter({
								title: b.text,
								iconCls: b.iconCls,
								animateTarget: b.getId(),
								callback: function(comp){
									b.setDisabled(false);
								}
							});
						},10);
					}
				}
			},'-',

			{
				xtype: 'tbspacer',
				hidden: false
//			},{
//				xtype: 'tbseparator',
//				hidden: false
			},{
				hidden: false,
				disabled: true,
				id: 'fma-edit-list-button',
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
							var win = window.open("get-info.cgi?"+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
						}
					}
				},'-',{
					text: AgLang.export,
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
					disabled: true,
					text: AgLang['import'],
					itemId: 'import',
					iconCls: 'pallet_upload',
					handler: function(b,e){
						var p = self.getExtraParams({current_datas:0});
						p.cmd = 'import-fma-all-list';
						self.openImportWindow({
							title: b.text + ' ('+ b.up('button').text +')',
							iconCls: b.iconCls,
							params: p
						});
					}
				},'-',{
					disabled: false,
					text: 'History Mapping All List',
					itemId: 'tree',
					iconCls: 'pallet_table',
					handler: function(b,e){
						var w = $(window).width() - 20;
						var h = $(window).height() - 0;
						var p = self.getExtraParams({current_datas:0});
						delete p.model;
						delete p.version;
						delete p.ag_data;
						delete p.tree;
						delete p.current_datas;
						delete p.mv_id;
						delete p.mr_id;
						delete p.cb_id;
						delete p.bul_id;
						delete p._ExtVerMajor;
						delete p._ExtVerMinor;
						delete p._ExtVerPatch;
						delete p._ExtVerBuild;
						delete p._ExtVerRelease;
						p.cmd = 'fma-history-mapping-all-list';
						p.title = 'FMA History Mapping All List';
						self.openSelectDatasetWindow({
							params:p,
							callback:function(p){
								var win = window.open("get-info.cgi?"+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
							}
						});
					}
				}],
				listeners: {
					render: function(b){
						var treeCombobox = Ext.getCmp('tree-combobox');
						var treeStore = treeCombobox.getStore();
						if(treeStore.getCount()==0){
							b.setDisabled(true);
							treeStore.on({
								load: {
									fn: function(){
										b.setDisabled(false);
									},
									buffer: 100,
									single: true
								}
							});
						}else{
							b.setDisabled(false);
						}
					},
					menushow: function(b,menu,eOpts){
						var import_menu = menu.getComponent('import');
						var versionCombobox = Ext.getCmp('version-combobox');
						var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
						var mv_frozen = r.data.mv_frozen;
						import_menu.setDisabled(mv_frozen);
					}
				}
			},'-',{
				disabled: true,
				text: AgLang.subclass_list,
				iconCls: 'pallet_download',
				handler: function(b,e){
					var p = self.getExtraParams({current_datas:0});
//					console.log(p);
					var href = Ext.String.format('./api-concept-data-info-user-data.cgi?md_id={0}&mv_id={1}&mr_id={2}&ci_id={3}&cb_id={4}&cmd=download',p.md_id,p.mv_id,p.mr_id,p.ci_id,p.cb_id);
//					console.log(href);
					window.location.href = href;
				},
				listeners: {
					render: function(b){
						var treeCombobox = Ext.getCmp('tree-combobox');
						var treeStore = treeCombobox.getStore();
						if(treeStore.getCount()==0){
							b.setDisabled(true);
							treeStore.on({
								load: {
									fn: function(){
										b.setDisabled(false);
									},
									buffer: 100,
									single: true
								}
							});
						}else{
							b.setDisabled(false);
						}
					}
				}
			},{
				xtype: 'tbseparator',
				hidden: true
			},{
				hidden: true,
				disabled: true,
//				id: 'all-fma-list-button',
//				iconCls: 'pallet_table_list',
				text: AgLang.all_fma_list,
//				href: 'get-info.cgi',
				listeners: {
					render: function(b){
						var treeCombobox = Ext.getCmp('tree-combobox');
						var treeStore = treeCombobox.getStore();
						if(treeStore.getCount()==0){
							b.setDisabled(true);
							treeStore.on({
								load: {
									fn: function(){
										b.setDisabled(false);
									},
									buffer: 100,
									single: true
								}
							});
						}else{
							b.setDisabled(false);
						}
					},
					click: function(b){
						var w = $(window).width() - 20;
						var h = $(window).height() - 0;
						var p = self.getExtraParams({current_datas:0});
						p.cmd = 'fma-all-list';
						p.title = b.text;
//						b.setParams(p);
//						return;
						var win = window.open("get-info.cgi?"+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
					}
				}
			},{
				xtype: 'tbspacer',
				hidden: false
			},{
				xtype: 'tbseparator',
				hidden: false
			},

			'->',

			'-',{
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
			}
/*
			,'-',{
				text: AgLang.window_alignment,
				iconCls: 'gear-btn',
				menu: [{
					iconCls: 'pallet_delete',
					text: 'Clear',
					listeners: {
						click: function(b){
						}
					}
				}]
			}
*/
			]
		}]
	};

	var parts_tab_panel = Ext.create('Ext.tab.Panel',{
		id: 'parts-tab-panel',
		region: 'center',
		border: false,
//		stateId: 'parts-tab-panel',
//		stateful: true,
		items: [parts_tree_panel,parts_grid,bp3d_search_grid],
		activeTab: parts_grid,
		deferredRender: true
	});

	var parts_wiki_panel = Ext.create('Ext.form.Panel',{
		title: 'Details of parts',
		region: 'south',
//		autoScroll : true,
		collapsible: true,
		collapsed  : true,
		split: true,
		height: 300,
//		bodyPadding: 5,
		listeners: {
			afterrender: function(panel){
//				console.log('parts_wiki_panel.afterrender()');
				AgWiki.init({
					panel: panel,
					dom:panel.body.dom
				});
			},
			expand : function(panel){
//				console.log('parts_wiki_panel.expand()');
				var view = parts_grid.getView();
				var selModel = parts_grid.getSelectionModel();
				var records = selModel.getSelection();
				if(records.length>0){
					var record = records[0];
					view.focusRow(records[0]);
				}
			}
		}
	});

	var getCookiesPath = function(){
		return (window.location.pathname.split("/").splice(0,window.location.pathname.split("/").length).join("/"));
	};

	var getCookiesExpires = function(){
		var xDay = new Date;
		xDay.setTime(xDay.getTime() + (30 * 24 * 60 * 60 * 1000)); //30 Days after
		return xDay;
	};



	var parts_panel;
	if(self.DEF_LAYOUT==self.DEF_LAYOUT_BORDER){
		var configLinkedUploadPartsButton = self.getConfigLinkedUploadPartsButton();
		parts_panel = Ext.create('Ext.panel.Panel',{
			id: 'parts-panel',
			region: 'west',
			collapsible: true,
			split: true,
			border: false,
//		width: 454,
			width: self.panelWidth,
			layout: 'border',
			items:[parts_tab_panel],
//		items:[parts_tab_panel,parts_wiki_panel],
			dockedItems: [{
				hidden: configLinkedUploadPartsButton.hidden,
				xtype: 'toolbar',
				dock: 'top',
				items: ['->','-',configLinkedUploadPartsButton]
			}],
			listeners: {
				render: function(panel,eOpts){
				}
			}
		});
	}

	var all_upload_parts_list_menu = {
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
					var win = window.open("get-info.cgi?"+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
				}
			}
		},'-',{
			text: AgLang.export,
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
					var version = 'unknown';
					var field = Ext.getCmp('version-combobox');
					if(field && field.rendered){
						try{
							var record = field.findRecordByValue(field.getValue());
							if(record) version = Ext.util.Format.format('{0}-{1}',record.get('version'),record.get('mr_version')).replace(Ext.form.field.VTypes.filenameReplaceMask,'_');
						}catch(e){
							console.error(e);
						}
					}
/*
					self.export({
						cmd: 'export-concept-art-map',
						format: 'zip',
						title: b.text,
						iconCls: b.iconCls,
						filename: Ext.util.Format.format('{0}_{1}_{2}','mapping',version,Ext.util.Format.date(new Date(),'YmdHis'))
					});
*/
					var params = self.getExtraParams({current_datas:0});
					delete params._ExtVerBuild;
					delete params._ExtVerMajor;
					delete params._ExtVerMinor;
					delete params._ExtVerPatch;
					delete params._ExtVerRelease;
					delete params.ag_data;
					delete params.bul_id;
					delete params.mr_id;
					delete params.mv_id;
					delete params.current_datas;
					delete params.model;
					delete params.tree;
					delete params.version;
//					delete params.cb_id;
//					delete params.ci_id;
//					delete params.md_id;

					params.cmd = 'export-concept-art-map';
					params.format = 'zip';
					params.filename = Ext.util.Format.format('{0}_{1}_{2}','mapping',version,Ext.util.Format.date(new Date(),'YmdHis'));

					self.openExportSelectDatasetWindow({
						title: b.text,
						iconCls: b.iconCls,
						params: params,
						callback: function(params){
							self._export(params);
						}
					});
				}
			}]
		},{
			disabled: true,
			text: AgLang['import'],
			itemId: 'import',
			iconCls: 'pallet_upload',
/*
			handler: function(b,e){
				var p = self.getExtraParams();
				p.cmd = 'import-upload-all-list';
				self.openImportWindow({
					title: b.text + ' ('+ b.up('button').text +')',
					iconCls: b.iconCls,
					params: p
				});
			}
*/
			menu: [{
				text: AgLang.all_upload_parts_list,
				iconCls: 'pallet_table',
				handler: function(b,e){
					var p = self.getExtraParams({current_datas:0});
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
					p.cmd = 'import-concept-art-map';
					self.openImportWindow({
						title: AgLang['import'] + ' ('+ b.text +')',
						iconCls: b.iconCls,
						params: p
					});
				}
			}]
		},'-',{
			iconCls: 'pallet_table_list',
			text: 'History Mapping All List',
			listeners: {
				click: function(b){
					var w = $(window).width() - 10;
					var h = $(window).height() - 10;
					var p = self.getExtraParams({current_datas:0});
					delete p.model;
					delete p.version;
					delete p.ag_data;
					delete p.tree;
					delete p.current_datas;
					delete p.mv_id;
					delete p.mr_id;
					delete p.cb_id;
					delete p.bul_id;
					delete p._ExtVerMajor;
					delete p._ExtVerMinor;
					delete p._ExtVerPatch;
					delete p._ExtVerBuild;
					delete p._ExtVerRelease;
					p.cmd = 'upload-history-mapping-all-list';
					p.title = 'Upload History Mapping All List';
					self.openSelectDatasetWindow({
						params:p,
						callback:function(p){
							var win = window.open("get-info.cgi?"+ Ext.Object.toQueryString(p),"_blank","width="+w+",height="+h+",dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no");
						}
					});
				}
			}



		}],
		listeners: {
			render: function(b){
				var treeCombobox = Ext.getCmp('tree-combobox');
				var treeStore = treeCombobox.getStore();
				if(treeStore.getCount()==0){
					b.setDisabled(true);
					treeStore.on({
						load: {
							fn: function(){
								b.setDisabled(false);
							},
							buffer: 100,
							single: true
						}
					});
				}else{
					b.setDisabled(false);
				}
			},
			menushow: function(b,menu,eOpts){
				var import_menu = menu.getComponent('import');
				var versionCombobox = Ext.getCmp('version-combobox');
				var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
				var mv_frozen = r.data.mv_frozen;
				import_menu.setDisabled(mv_frozen);
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
						closeAction: 'hide',
						modal: true,
//								resizable: false,
						resizable: true,
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
							xtype: 'form',
							bodyPadding: 5,
							defaults: {
								hideLabel: false,
								labelAlign: 'right',
								labelStyle: 'font-weight:bold;',
								labelWidth: 70
							},
							items: [{
								xtype: 'combobox',
								name: 'md_id',
								itemId: 'md_id',
								fieldLabel: AgLang.model,
								store: 'modelStore',
								queryMode: 'local',
								displayField: 'display',
								valueField: 'md_id',
								value: DEF_MODEL_ID,
								editable: false
							},{
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
								name: 'artf_id',
								fieldLabel: 'Folder',
//								store: 'uploadFolderTreePanelStore',
								store: Ext.data.StoreManager.lookup('uploadFolderTreePanelStore'),
								displayField: 'text',
								valueField: 'artf_id',
								editable: false,
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
								xtype: 'fieldset',
								itemId: 'file_fieldset',
								title: 'Upload Object file',
								minHeight: 100,
								defaults: {
									hideLabel: false,
									labelAlign: 'right',
									labelStyle: 'font-weight:bold;',
									labelWidth: 70
								},
								listeners: {
									afterrender: function( fieldset, eOpts ){
										return;
										var el = fieldset.getEl();
										el.on({
											dragleave: function(event){
//												console.log('dragleave()');
												var el = this.getEl();
												el.scrollChildFly.attach(el.dom).stopAnimation();
											},
											dragenter: function(event){
//												console.log('dragenter()');
												var el = this.getEl();
												el.scrollChildFly.attach(el.dom).highlight(null,{stopAnimation: true});
												self.fileDragenter(event);
												return false;
											},
											dragover: function(event){
												self.fileDragover(event);
												return false;
											},
											drop: function(event){
												var fieldset = this;
												var el = fieldset.getEl();
												el.scrollChildFly.attach(el.dom).stopAnimation();
												self.fileDrop(event,{
													callback: Ext.bind(function(files,folders){
														console.log(files);
														console.log(folders);

														var formPanel = this.up('form');
														var submit_btn = formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit');
														var fieldset = formPanel.getComponent('file_fieldset');
														fieldset.getComponent('file_name').setValue('').hide();
														fieldset.getComponent('file_size').setValue('').hide();
														fieldset.getComponent('file_last').setValue('').hide();
														fieldset.getComponent('file_error').hide();

														var file_gridpanel = fieldset.getComponent('file_gridpanel');
														var file_gridpanel_store = file_gridpanel.getStore();
														var records = [];
														Ext.each(files,function(file){
															records.push([file.name,file.size,file.lastModifiedDate,file]);
														});
														file_gridpanel_store.loadRawData(records);
														file_gridpanel.show();
														fieldset.getComponent('file_num').setValue(Ext.util.Format.number(files.length,self.FORMAT_INT_NUMBER)).show();
														fieldset.getComponent('file_group_name').setDisabled(false).setValue(folders && folders.length ? folders[0].name : '').show().focus();

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
									layout: 'hbox',
									items: [{
									xtype: 'filefield',
										name: 'file',
										hideLabel: true,
										buttonOnly: true,
										buttonText: 'Select File...',
										listeners: {
											change: function(field,value,eOpts){
												var formPanel = field.up('form');
												var submit_btn = formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit');
												var fieldset = formPanel.getComponent('file_fieldset');
												fieldset.getComponent('file_group_name').setDisabled(true).hide();
												fieldset.getComponent('file_num').hide();
												fieldset.getComponent('file_gridpanel').hide();

												if(field.fileInputEl.dom.files && field.fileInputEl.dom.files.length){
													var file = field.fileInputEl.dom.files[0];
													fieldset.getComponent('file_name').setValue(file.name).show();
													fieldset.getComponent('file_size').setValue(Ext.util.Format.fileSize(file.size)).show();
													fieldset.getComponent('file_last').setValue(Ext.util.Format.date(file.lastModifiedDate,self.FORMAT_DATE_TIME)).show();

													var error = false;
													var error_msg = '';
													if(file.size>DEF_UPLOAD_FILE_MAX_SIZE){
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
										hidden: true,
										xtype: 'label',
										text: 'または、ここにファイル(複数可)'+(Ext.isChrome?'、フォルダ': '')+'をドロップ',
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
									xtype: 'textfield',
									fieldLabel: AgLang.group,
									labelWidth: 80,
									itemId: 'file_group_name',
									name: 'file_group_name',
									allowBlank: false,
									allowOnlyWhitespace: false,
									selectOnFocus: true,
									anchor: '100%'
								},{
									xtype: 'displayfield',
									fieldLabel: '#File',
									labelWidth: 80,
									itemId: 'file_num',
									value: 0
								},{
									xtype: 'gridpanel',
									itemId: 'file_gridpanel',
									store: 'dropFileStore',
									maxHeight: 100,
									margin: '0 0 10 0',
									columns: [
										{ text: AgLang.file_name, dataIndex: 'name', flex: 1 },
										{ text: AgLang.file_size, dataIndex: 'size', xtype: 'agfilesizecolumn', width: 60},
										{ text: AgLang.timestamp, dataIndex: 'lastModified', width: 114, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME }
									],


								}]
							},{
								xtype: 'fieldset',
								title: 'Original Object file Information',
								checkboxToggle: true,
								checkboxName: 'art_org_info',
								collapsed: true,
								anchor: '100% -234',
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
									labelWidth: self.USE_UPLOAD_MULTI_ORIGINAL_OBJECT ? 56 : 72,
									enableKeyEvents: true,
									selectOnFocus: true
								},
								items: [{
									disabled: true,
									xtype: 'textfield',
									fieldLabel: self.USE_UPLOAD_MULTI_ORIGINAL_OBJECT ? AgLang.art_ids : AgLang.art_id,
									itemId: 'arto_id',
									name: 'arto_id',
									anchor: '100%',
									emptyText: self.USE_UPLOAD_MULTI_ORIGINAL_OBJECT ? '複数のIDを指定する場合は、英数字以外の文字で区切ってください。' : null,
									validator: function(value){
										var field = this;
										var fieldset = field.up('fieldset');
										var isExpand = fieldset.checkboxCmp.getValue();
										if(!isExpand){
											return true;
										}
										var rtn = AgLang.error_arto_id;
										if(Ext.isString(value)){
											var s = Ext.String.trim(value);
											if(Ext.isEmpty(s)){
												return rtn;
											}
										}else if(Ext.isEmpty(value)){
											return rtn;
										}

										var fieldcontainer = field.next('fieldcontainer');
										if(Ext.isEmpty(fieldcontainer.getComponent('arto_group').getValue()) || Ext.isEmpty(fieldcontainer.getComponent('arto_filename').getValue())){
											return rtn;
										}

										return true;
									},
									listeners: {
										change: function(field,newValue,oldValue,eOpts){

											var fieldset = field.up('fieldset');
											var fieldcontainer = field.next('fieldcontainer');
											var arto_group = fieldcontainer.getComponent('arto_group');
											var arto_filename = fieldcontainer.getComponent('arto_filename');
											var arto_comment = fieldset.getComponent('arto_comment');
											var gridpanel = field.next('gridpanel');

											var art_id = Ext.String.trim(newValue);
											if(Ext.isEmpty(art_id)){
												arto_group.setValue('');
												arto_filename.setValue('');
												originalObjectStore.removeAll();
												field.focus(false);
												return;
											}

											fieldcontainer.setLoading(true);
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
													fieldcontainer.setLoading(false);
													gridpanel.setLoading(false);
//														if(!success) return;
													var json;
													try{json = Ext.decode(response.responseText)}catch(e){};
													if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
														arto_group.setValue('');
														arto_filename.setValue('');
														originalObjectStore.removeAll();
														field.focus(false);
														return;
													}
													var data = json.datas[0];
													arto_group.setValue(data.artg_name);
													arto_filename.setValue(data.art_filename);
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
									hidden: self.USE_UPLOAD_MULTI_ORIGINAL_OBJECT,
									xtype: 'fieldcontainer',
									defaults: {
										labelAlign: 'right',
										labelWidth: 72
									},
									items: [{
										xtype: 'displayfield',
										fieldLabel: AgLang.group,
										itemId: 'arto_group'
									},{
										xtype: 'displayfield',
										fieldLabel: AgLang.file_name,
										itemId: 'arto_filename'
									}]
								},{
									hidden: !self.USE_UPLOAD_MULTI_ORIGINAL_OBJECT,
									xtype: 'gridpanel',
									store: Ext.data.StoreManager.lookup('originalObjectStore'),
									columns: [
										{text: AgLang.art_id,    dataIndex: 'art_id',       width: 60},
										{text: AgLang.group,     dataIndex: 'artg_name',    flex: 1 },
										{text: AgLang.file_name, dataIndex: 'art_filename', flex: 2 }
									],
									minHeight: 100,
									anchor: '100% -97',
								},{
									xtype: 'textareafield',
									fieldLabel: AgLang.comment,
									itemId: 'arto_comment',
									name: 'arto_comment',
									anchor: '100%',
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
/*
										form.clearListeners();
										form.on({
											actioncomplete : function(form,action,eOpts){
//													console.log("actioncomplete()");
											},
											actionfailed : function(form,action,eOpts){
//													console.log("actionfailed()");
											},
											beforeaction : function(form,action,eOpts){
//													console.log("beforeaction()");
											},
											dirtychange : function(form,dirty,eOpts){
//													console.log("dirtychange()");
											},
											validitychange : function(form,valid,eOpts){
//													console.log("validitychange()");
											},
										});
*/
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
													if(callback) (callback)(close_progress_msg? true : false);
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
															Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
																callback: function(records, operation, success) {
																	var selected_art_ids = self.getSelectedArtIds();
																	var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
																	uploadObjectStore.setLoadUploadObjectAllStoreFlag();
																	uploadObjectStore.loadPage(1,{
																		params: { selected_art_ids: Ext.encode(selected_art_ids) },
																		sorters: uploadObjectStore.getUploadObjectLastSorters()
																	});
																}
															});
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
								formPanel.getComponent('md_id').setValue(DEF_MODEL_ID);
								formPanel.getComponent('prefix_id').setValue(DEF_PREFIX_ID);

								var fieldset = formPanel.getComponent('file_fieldset');
								fieldset.getComponent('file_name').hide();
								fieldset.getComponent('file_size').hide();
								fieldset.getComponent('file_last').hide();
								fieldset.getComponent('file_group_name').hide();
								fieldset.getComponent('file_num').hide();
								fieldset.getComponent('file_gridpanel').hide();
							},
							hide: function(comp){
								var formPanel = comp.down('form');
								formPanel.getForm().reset();
								formPanel.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('submit').setDisabled(true);

								var fieldset = formPanel.getComponent('file_fieldset');
								fieldset.getComponent('file_error').hide();
							}
						}
					});
				}
				self._uploadWin.show();
			}
		}
	};







	var upload_group_grid = Ext.create('Ext.ag.GridPanel',{
		title: self.TITLE_UPLOAD_GROUP,
		id: 'upload-group-grid',
//		region: 'north',
		region: 'center',
//		split: true,
//		height: self.panelHeight-150,
		minHeight: 150,
		collapsible: false,
//		height: 250,
		columnLines: true,
		store: 'uploadGroupStore',
		stateful: true,
		stateId: 'upload-group-grid',
		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
//		features: [get_grid_filters()],
		columns: [
			{text: '&#160;',         dataIndex: 'selected',            stateId: 'selected',            width: 30,  minWidth: 30,  hidden: false, hideable: false, sortable: true, draggable: false, xtype: 'agselectedcheckcolumn'},

			{text: AgLang.group,     dataIndex: 'artg_name',           stateId: 'artg_name',           flex:  2,   minWidth: 80,  hidden: false, hideable: false},
			{text: 'Path',           dataIndex: 'path',                stateId: 'path',                flex:  1,   minWidth: 80,  hidden: true,  hideable: false},
			{text: '#File',          dataIndex: 'art_count',           stateId: 'art_count',           width: 40,  minWidth: 40,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_INT_NUMBER},
			{text: '#Unmap',         dataIndex: 'nomap_count',         stateId: 'nomap_count',         width: 40,  minWidth: 40,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_INT_NUMBER},
			{text: '#Unchk',         dataIndex: 'nochk_count',         stateId: 'nochk_count',         width: 40,  minWidth: 40,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_INT_NUMBER},
			{text: '#Use',           dataIndex: 'use_map_count',       stateId: 'use_map_count',       width: 40,  minWidth: 40,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_INT_NUMBER},
			{text: AgLang.timestamp, dataIndex: 'artg_timestamp',      stateId: 'artg_timestamp',      width: 114, minWidth: 112, hidden: false, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME},
			{text: 'group id',       dataIndex: 'artg_id',             stateId: 'artg_id',             width: 40,  minWidth: 40,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_ID_NUMBER},
			{text: 'Use',            dataIndex: 'all_cm_map_versions', stateId: 'all_cm_map_versions', flex: 1,    minWidth: 40,  hidden: true,  hideable: true, renderer:function(value){
				if(Ext.isArray(value)){
					return value.map(function(v){return Ext.isObject(v) ? v.mv_name_e : v;}).join(',');
				}else{
					return value;
				}
			}},
			{text: 'folder id',      dataIndex: 'artf_id',             stateId: 'artf_id',             width: 40, minWidth: 40,   hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_ID_NUMBER},
			{text: 'folder',         dataIndex: 'artf_name',          stateId: 'artf_name',            flex:  2,  minWidth: 80,   hidden: true,  hideable: true},
		],

		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: true,
			plugins: {
//				ddGroup: 'upload_group_grid-to-upload_folder_tree',
				ddGroup: 'dd-upload_folder_tree',
				ptype: 'gridviewdragdrop',
				enableDrop: false
			}
		},
		selType: 'rowmodel',
		selModel: {
			mode: 'MULTI',
			listeners: {
				selectionchange : function(selModel,selected,eOpts){
//					console.log("upload_group_grid:selectionchange()");
					if(selModel.getCount()>0){
						Ext.getCmp('uploadDeleteBtn').enable();
						Ext.getCmp('uploadDownloadBtn').enable();
//						Ext.getCmp('uploadFolderBtn').enable();


						Ext.getCmp('uploadFolderCombo').enable();
//						Ext.getCmp('uploadFolderCombo').setValue(selected[0].get('artf_id'));

						var artf_id = selected[0].get('artf_id');
						var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
						var record = artf_id ? (store.findRecord ? store.findRecord( 'artf_id', artf_id, 0, false, false, false) : store.getRootNode().findChild('artf_id',artf_id,true)) : store.getRootNode();
						Ext.getCmp('uploadFolderCombo').setValue(record ? record.getId() : undefined);
					}else{
						Ext.getCmp('uploadDeleteBtn').disable();
						Ext.getCmp('uploadDownloadBtn').disable();
//						Ext.getCmp('uploadFolderBtn').disable();
						Ext.getCmp('uploadFolderCombo').disable();
						Ext.getCmp('uploadFolderCombo').setValue('');
					}
					if(selModel.getCount()==1){
						Ext.getCmp('uploadRenameBtn').enable();
					}else{
						Ext.getCmp('uploadRenameBtn').disable();
					}
				}
			}
		},
		listeners: {
			render: function(grid,eOpts){
			},
			itemcontextmenu: {
				fn: self.showPalletItemContextmenu,
				scope: self
			}
		},
		dockedItems: [{
			hidden: false,
			xtype: 'toolbar',
			dock: 'top',
			layout: {
				overflowHandler: 'Menu'
			},
			items:[
			{
				xtype: 'button',
				iconCls: 'pallet_checked',
				text: 'check all',
				listeners: {
					click: function(b){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var records = [];
						store.suspendEvent('update');
						try{
							store.each(function(record){
								if(record.get('selected')) return true;
								record.beginEdit();
								record.set('selected',true);
								record.endEdit(false,['selected']);
								record.commit(false,['selected']);
								records.push(record);
							});
						}catch(e){
							console.error(e);
						}
						store.resumeEvent('update');
						gridpanel.view.refresh();
						if(records.length===0) return;

						Ext.defer(function(){
							var selected_art_ids = self.getSelectedArtIds();
							var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
							uploadObjectStore.setLoadUploadObjectAllStoreFlag();
							uploadObjectStore.loadPage(1,{
								params: { selected_art_ids: Ext.encode(selected_art_ids) },
								sorters: uploadObjectStore.getUploadObjectLastSorters()
							});
						},0);
					}
				}
			},
			'-',
			{
				iconCls: 'pallet_unchecked',
				text: 'uncheck all',
				listeners: {
					click: function(b){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						var records = [];
						store.suspendEvent('update');
						try{
							store.each(function(record){
								if(!record.get('selected')) return true;
								record.beginEdit();
								record.set('selected',false);
								record.endEdit(false,['selected']);
								record.commit(false,['selected']);
								records.push(record);
							});
						}catch(e){
							console.error(e);
						}
						store.resumeEvent('update');
						gridpanel.view.refresh();
						if(records.length===0) return;

						Ext.defer(function(){
							var selected_art_ids = self.getSelectedArtIds();
							var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
							uploadObjectStore.setLoadUploadObjectAllStoreFlag();
							uploadObjectStore.loadPage(1,{
								params: { selected_art_ids: Ext.encode(selected_art_ids) },
								sorters: uploadObjectStore.getUploadObjectLastSorters()
							});
						},0);
					}
				}
			},
			'-',
			'->','-',{
				xtype: 'tbspacer',
				hidden: true
			},
			{
				id: 'uploadDownloadBtn',
				xtype: 'button',
				text: 'Download',
				iconCls: 'pallet_download',
				disabled: true,
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

						var filename;
						if(recs.length==1) filename = Ext.util.Format.format('{0}_{1}',recs[0].get('artg_name'),Ext.util.Format.date(new Date(),'YmdHis'));

						self.downloadObjectsTask.delay(10,self.downloadObjects,self,[{
							type: 'groups',
							records: recs,
							filename: filename,
							callback: function(){
								b.setDisabled(false);
							}
						}]);
					}
				}
			},
			'-',{
				id: 'uploadRenameBtn',
				xtype: 'button',
				text: 'Rename',
				iconCls: 'pallet_rename',
				disabled: true,
				listeners: {
					click: function(b){
						var records = upload_group_grid.getSelectionModel().getSelection();
						if(records.length != 1) return;

						Ext.Msg.show({
							title: b.text + ' [ '+records[0].get('name')+' ]',
							msg: 'Please enter new group name: ',
							iconCls: b.iconCls,
							buttons: Ext.Msg.OKCANCEL,
							prompt: true,
							value: records[0].get('name'),
							fn: function(btn, text){
								if(btn != 'ok') return;
								var group_name = Ext.String.trim(text);
								if(group_name.length==0) return;

								upload_group_grid.setLoading(true);
								Ext.defer(function(){
									var dateStr = (new Date()).toString();
									var store = records[0].store;
									store.suspendEvents(true);
									Ext.each(records,function(r,i,a){
										r.beginEdit();
										r.set('artg_name',group_name);
										r.endEdit(false,['artg_name']);
									});
									store.resumeEvents();
									store.sync({
										success: function(batch,options){
											Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
												callback: function(records, operation, success) {
													var selected_art_ids = self.getSelectedArtIds();
													var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
													uploadObjectStore.setLoadUploadObjectAllStoreFlag();
													uploadObjectStore.loadPage(1,{
														params: { selected_art_ids: Ext.encode(selected_art_ids) },
														sorters: uploadObjectStore.getUploadObjectLastSorters()
													});
												}
											});
										},
										failure: function(batch,options){
											var msg = 'リネームに失敗しました';
											var proxy = this;
											var reader = proxy.getReader();
											if(reader && reader.rawData && reader.rawData.msg){
												msg += ' ['+reader.rawData.msg+']';
											}
											Ext.Msg.show({
												title: b.text,
												iconCls: b.iconCls,
												msg: msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												fn: function(buttonId,text,opt){
												}
											});
										},
										callback: function(batch,options){
											upload_group_grid.setLoading(false);
										}
									});
								},250);

							}
						});
					}
				}
			},


			'-',{
				disabled: true,
				xtype: 'tbtext',
				text: 'Move Selected Group(s) To'
			},{
				disabled: true,
				id: 'uploadFolderCombo',
				iconCls: 'tfolder_property',
//				xtype: 'treecombo',
				xtype: 'treepicker',
//				store: 'uploadFolderTreePanelStore',
				store: Ext.data.StoreManager.lookup('uploadFolderTreePanelStore'),
				editable: false,
				displayField: 'text',
				valueField: 'artf_id',
				width: 100,
				listeners: {
					select: function(treecombo,record){//,item,index,e,eOpts,records,ids){
//						console.log(record.get('artf_id'),record.get('artf_name'));
						var grid = treecombo.up('grid');
						var records = grid ? grid.getSelectionModel().getSelection() : [];
						if(Ext.isEmpty(records)) return;
						changeUploadFolder(record,records);
					}
				}


			},{
				hidden: !self.USE_OBJ_UPLOAD,
				xtype: 'tbseparator'
			},{
				hidden: !self.USE_OBJ_UPLOAD,
				id: 'uploadDeleteBtn',
				xtype: 'button',
				text: 'Delete',
				iconCls: 'pallet_delete',
				disabled: true,
				listeners: {
					click: function(b){
						b.setDisabled(true);
						var selModel = upload_group_grid.getSelectionModel();
						var records = selModel.getSelection();
						if(Ext.isEmpty(records)){
							b.setDisabled(false);
							return;
						}

						var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
						var delete_records = records.filter(function(r, i, a){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx>=0;
							});
							return (all_cm_map_versions.length===0);
						});
						var exclusion_records = records.filter(function(r, i, a){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx>=0;
							});
							return (all_cm_map_versions.length!==0);
						});
						selModel.deselectAll();

						var delete_mv_names = [];
						var delete_cm_names = [];
						delete_records.forEach(function(r){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx<0;
							});
							if(Ext.isArray(all_cm_map_versions)){
								all_cm_map_versions.forEach(function(v){
									delete_mv_names.push(v.mv_name_e);
									if(Ext.isArray(v.cm_names)){
										v.cm_names.forEach(function(c){
											delete_cm_names.push(v.mv_name_e + "\t" + c.art_id + "\t" + c.cdi_name);
										});
									}
								});
							}
						});


						var exclusion_mv_names = [];
						var exclusion_cm_names = [];
						exclusion_records.forEach(function(r){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx>=0;
							});
							if(Ext.isArray(all_cm_map_versions)){
								all_cm_map_versions.forEach(function(v){
									exclusion_mv_names.push(v.mv_name_e);
									if(Ext.isArray(v.cm_names)){
										v.cm_names.forEach(function(c){
											exclusion_cm_names.push(v.mv_name_e + "\t" + c.art_id + "\t" + c.cdi_name);
										});
									}
								});
							}
						});

						if(Ext.isEmpty(delete_records)){
							var msg = '';
							if(exclusion_mv_names.length) msg += '['+Ext.Array.unique(exclusion_mv_names).join(',')+']で';
							msg += '使用中のデータが含まれる為、削除できません';

							Ext.Msg.show({
								title: b.text,
								iconCls: b.iconCls,
								msg: msg,
								animateTarget: b.el,
								buttons: Ext.Msg.OK,
								icon: Ext.Msg.WARNING,
							});
							b.setDisabled(false);
							return;
						}
						selModel.select(delete_records);

						var msg = '';
						if(exclusion_records.length){
							if(exclusion_mv_names.length) msg += '['+Ext.Array.unique(exclusion_mv_names).join(',')+']で';
							msg += '使用中のデータが含まれるものは除外しました。<br>';
						}
						if(delete_mv_names.length){
//							if(delete_mv_names.length) msg += '['+Ext.Array.unique(delete_mv_names).join(',')+']で';
							msg += 'FMAIDに対応済みのデータが含まれています。<br>';
							var t = ['<div style="max-height:10em;overflow:auto;margin:0.5em 0em;padding-left:1em;background:white;"><table>'];
							delete_cm_names.forEach(function(v){
								var va = v.split(/\t/);
								t.push('<tr>');
								var tr = [];
								v.split(/\t/).forEach(function(v){
									tr.push('<td>'+v+'</td>');
								});
								t.push(tr.join('<td>:</td>'));
								t.push('</tr>');
							});
							t.push('</table></div>');
							msg += t.join('');
						}
						msg += '選択されているアップロードデータを削除してよろしいですか？';

						Ext.Msg.show({
							title: b.text,
							iconCls: b.iconCls,
							msg: msg,
							animateTarget: 'uploadDeleteBtn',
							buttons: Ext.Msg.YESNO,
							icon: Ext.Msg.QUESTION,
							defaultFocus: 'no',
							fn: function(buttonId,text,opt){
								if(buttonId != 'yes'){
									b.setDisabled(false);
									return;
								}

								upload_group_grid.setLoading(true);
								Ext.defer(function(){
									var isReload = false;
									var dateStr = (new Date()).toString();
									var store = delete_records[0].store;
									store.suspendEvents(true);
									Ext.each(delete_records,function(r,i,a){
										if(r.get('selected')) isReload=true;
	//									r.beginEdit();
	//									r.set('selected',false);
	//									r.set('artg_delcause','DELETE['+dateStr+']');
	//									r.endEdit(false,['selected','artg_delcause']);
									});
									store.remove(delete_records);
									store.resumeEvents();
//									console.log("uploadGroupStore.sync()");
									store.sync({
										success: function(batch,options){
//											console.log("uploadGroupStore.sync.success()");
											var filters = Ext.Array.clone(store.filters.getRange());
											store.clearFilter(true);
											store.filter(filters);
											upload_group_grid.setLoading(false);
											if(isReload){
												var selected_art_ids = self.getSelectedArtIds();
												var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
												uploadObjectStore.setLoadUploadObjectAllStoreFlag();
												uploadObjectStore.loadPage(1,{
													params: { selected_art_ids: Ext.encode(selected_art_ids) },
													sorters: uploadObjectStore.getUploadObjectLastSorters()
												});
											}
										},
										failure: function(batch,options){
//											console.log("uploadGroupStore.sync.failure()");
											upload_group_grid.setLoading(false);
											var msg = AgLang.error_delete;
											var proxy = this;
											var reader = proxy.getReader();
											if(reader && reader.rawData && reader.rawData.msg){
												msg += ' ['+reader.rawData.msg+']';
											}
											Ext.Msg.show({
												title: b.text,
												iconCls: b.iconCls,
												msg: msg,
												buttons: Ext.Msg.OK,
												icon: Ext.Msg.ERROR,
												fn: function(buttonId,text,opt){
													Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
														callback: function(records, operation, success) {
															var selected_art_ids = self.getSelectedArtIds();
															var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
															uploadObjectStore.setLoadUploadObjectAllStoreFlag();
															uploadObjectStore.loadPage(1,{
																params: { selected_art_ids: Ext.encode(selected_art_ids) },
																sorters: uploadObjectStore.getUploadObjectLastSorters()
															});
														}
													});
												}
											});
										}
									});
								},250);

							}
						});
					}
				}
			}]
		}]
	});


	var cdi_renderer = function(value,metaData,record){
		if(!record.data.cm_use){
			metaData.style += "color:red;";
		}
		return value;
	};

	var upload_object_grid_contextmenu = null;
	upload_object_grid = Ext.create('Ext.ag.GridPanel',{
		title: self.TITLE_UPLOAD_OBJECT,
		id: 'upload-object-grid',
//		region: 'center',
		region: 'south',
		split: true,
//		height: self.panelHeight-100,
		height: 250,
		minHeight: 150,
		columnLines: true,
		store: 'uploadObjectStore',
		stateful: true,
		stateId: 'upload-object-grid',
		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
		columns: [
			{text: '&#160;',            dataIndex: 'selected',     stateId: 'selected',      width: 30, minWidth: 30, hidden: false, hideable: false, sortable: true, draggable: false, xtype: 'agselectedcheckcolumn'},

			{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 60, minWidth: 60, hidden: false, hideable: false},
			{text: AgLang.rep_id,       dataIndex: 'rep_id',       stateId: 'rep_id',        width: 60, minWidth: 60, hidden: false, hideable: true, renderer: function(value,metaData,record){
				if(record.data.rep_id!=record.data.use_rep_id) metaData.style += 'color:red;';
				return value;
			}},
			{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdiname' },
			{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdinamee' },
			{text: AgLang.category,     dataIndex: 'art_category', stateId: 'art_category',  flex: 1.0, minWidth: 50, hidden: false, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'art_class',    stateId: 'art_class',     width: 36, minWidth: 36, hidden: false, hideable: true},
			{text: AgLang.comment,      dataIndex: 'art_comment',  stateId: 'art_comment',   flex: 2.0, minWidth: 80, hidden: false, hideable: true},
			{text: AgLang.judge,        dataIndex: 'art_judge',    stateId: 'art_judge',     flex: 1.0, minWidth: 50, hidden: false, hideable: true},

			{text: AgLang.file_name,    dataIndex: 'filename',     stateId: 'filename',      flex: 2.0, minWidth: 80, hidden: false, hideable: true},
			{text: 'Sort',              dataIndex: 'sortname',     stateId: 'sortname',      flex: 1.0, minWidth: 50, hidden: true,  hideable: false},
			{text: AgLang.group,        dataIndex: 'group',        stateId: 'group',         flex: 2.0, minWidth: 50, hidden: true,  hideable: true},
			{text: 'Path',              dataIndex: 'path',         stateId: 'path',          flex: 1.0, minWidth: 50, hidden: true,  hideable: false},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true,  hideable: true},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true,  hideable: true},
			{text: AgLang.artog_name,   dataIndex: 'artog_name',   stateId: 'artog_name',    flex: 2.0, minWidth: 50, hidden: true,  hideable: true},

			{text: 'Color',             dataIndex: 'color',        stateId: 'color',         width: 40, minWidth: 40, hidden: true,  hideable: false, xtype: 'agcolorcolumn'},
			{text: 'Opacity',           dataIndex: 'opacity',      stateId: 'opacity',       width: 44, minWidth: 44, hidden: true,  hideable: false, xtype: 'agopacitycolumn'},
			{text: 'Hide',              dataIndex: 'remove',       stateId: 'remove',        width: 40, minWidth: 40, hidden: true,  hideable: false, xtype: 'agcheckcolumn'},
			{text: 'Scalar',            dataIndex: 'scalar',       stateId: 'scalar',        width: 40, minWidth: 40, hidden: true,  hideable: false, xtype: 'agnumbercolumn', format: '0', editor : 'numberfield'},

			{text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 60,               hidden: false, hideable: true, xtype: 'agfilesizecolumn'},

			{text: AgLang.xmax,         dataIndex: 'xmax',         stateId: 'xmax',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xmin,         dataIndex: 'xmin',         stateId: 'xmin',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xcenter,      dataIndex: 'xcenter',      stateId: 'xcenter',       width: 59, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymax,         dataIndex: 'ymax',         stateId: 'ymax',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymin,         dataIndex: 'ymin',         stateId: 'ymin',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ycenter,      dataIndex: 'ycenter',      stateId: 'ycenter',       width: 59, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmax,         dataIndex: 'zmax',         stateId: 'zmax',          width: 55, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmin,         dataIndex: 'zmin',         stateId: 'zmin',          width: 55, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zcenter,      dataIndex: 'zcenter',      stateId: 'zcenter',       width: 59, hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.volume,       dataIndex: 'volume',       stateId: 'volume',        width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

			{text: AgLang.timestamp,    dataIndex: 'mtime',        stateId: 'mtime',         width: 112, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME},
			{text: '#AllMap',           dataIndex: 'all_cm_count', stateId: 'all_cm_count',  width: 40,  hidden: true, hideable: true, xtype: 'agnumbercolumn', format: '0'},
			{text: 'AllMap',            dataIndex: 'all_cm_map_versions', stateId: 'all_cm_map_versions', flex: 1, minWidth: 40, hidden: true, hideable: true, renderer:function(value){
				if(Ext.isArray(value)){
					return value.map(function(v){return Ext.isObject(v) ? v.mv_name_e : v;}).join(',');
				}else{
					return value;
				}
			}}
		],

		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: true,
//			plugins: {
//				ptype: 'gridviewdragdrop',
//				dragText: 'Drag and drop to reorganize'
//			}
		},
		selType: 'rowmodel',
		selModel: {
			mode: 'MULTI'
		},

		dockedItems: [{
			xtype: 'toolbar',
			dock: 'top',
			items:[{
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
								var recs = [];

								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');

								if(true || self.getPressedLinkedUploadPartsButton()){

									var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
									uploadObjectAllStore.suspendEvents(false);
									try{
										uploadObjectAllStore.each(function(r,i,a){
											if(r.get('selected')) return true;
											r.beginEdit();
											r.set('selected',true)
											r.commit(true);
											r.endEdit(true,['selected']);
											recs.push(r);
										});
									}catch(e){console.error(e);}
									uploadObjectAllStore.resumeEvents();

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

									var art_ids = [];
									var art_id_hash = {};
									Ext.each(recs,function(r,i,a){
										var art_id = r.get('art_id');
										if(Ext.isEmpty(art_id)) return true;
										if(Ext.isEmpty(art_id_hash[art_id])){
											art_id_hash[art_id] = art_id;
											var data = {};
											for(var key in r.data){
												if(Ext.isDate(r.data[key])){
													data[key] = r.data[key].getTime()/1000;
												}else{
													data[key] = r.data[key];
												}
											}
											art_ids.push(data);
										}
									});
									if(art_ids.length){
										var params = self.getExtraParams() || {};
										params.art_ids = Ext.encode(art_ids);

										Ext.Ajax.request({
											url: 'get-upload-obj-info.cgi',
											method: 'POST',
											params: params,
											callback: function(options, success, response){
												upload_object_grid.setLoading(false);
												pallet_grid.setLoading(false);
												b.setDisabled(false);
											},
											success: function(response, options){

												var json;
												var records;
												try{json = Ext.decode(response.responseText)}catch(e){};
												if(Ext.isEmpty(json) || Ext.isEmpty(json.datas)){
													if(Ext.isEmpty(json.datas)){
														Ext.Msg.show({
															title: 'WARNING',
															msg: 'データの取得に失敗しました',
															buttons: Ext.Msg.OK,
															icon: Ext.Msg.WARNING
														});
													}
													uploadObjectAllStore.suspendEvents(false);
													try{
														uploadObjectAllStore.each(function(r,i,a){
															if(!r.get('selected')) return true;
															r.beginEdit();
															r.set('selected',false)
															r.commit(true);
															r.endEdit(true,['selected']);
															recs.push(r);
														});
													}catch(e){console.error(e);}
													uploadObjectAllStore.resumeEvents();

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

													return;
												}

												var recs = [];

												Ext.iterate(json.datas,function(data){
													var modifiedFieldNames = [];
													var n_record = Ext.create(Ext.getClassName(uploadObjectAllStore.model),data);
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

													recs.push(n_record);
												});
												self.extension_parts_store_update(recs,true,false);

											}
										});


									}else{
										Ext.defer(function(){
											self.extension_parts_store_update(recs,true,false);
											upload_object_grid.setLoading(false);
											pallet_grid.setLoading(false);
											b.setDisabled(false);
										},250);
									}

								}else{

									uploadObjectStore.suspendEvents(false);
									try{
										uploadObjectStore.each(function(r,i,a){
											if(r.get('selected')) return true;
											r.beginEdit();
											r.set('selected',true)
											r.commit(true);
											r.endEdit(true,['selected']);
											recs.push(r);
										});
									}catch(e){console.error(e);}
									uploadObjectStore.resumeEvents();
									upload_object_grid.getView().refresh();

									Ext.defer(function(){
										self.extension_parts_store_update(recs,true,false);
										upload_object_grid.setLoading(false);
										pallet_grid.setLoading(false);
										b.setDisabled(false);
									},250);

								}
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
								var recs = [];
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');

								if(true || self.getPressedLinkedUploadPartsButton()){

									var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
									uploadObjectAllStore.suspendEvents(false);
									try{
										uploadObjectAllStore.each(function(r,i,a){
											if(!r.get('selected')) return true;
											r.beginEdit();
											r.set('selected',false)
											r.commit(true);
											r.endEdit(true,['selected']);
											recs.push(r);
										});
									}catch(e){console.error(e);}
									uploadObjectAllStore.resumeEvents();

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
									Ext.defer(function(){
										self.extension_parts_store_update(recs,true,false);
										upload_object_grid.setLoading(false);
										pallet_grid.setLoading(false);
										b.setDisabled(false);
									},250);

								}else{

									uploadObjectStore.suspendEvents(false);
									try{
										uploadObjectStore.each(function(r,i,a){
											if(!r.get('selected')) return true;
											r.beginEdit();
											r.set('selected',false)
											r.commit(true);
											r.endEdit(true,['selected']);
											recs.push(r);
										});
									}catch(e){console.error(e);}
									uploadObjectStore.resumeEvents();

									upload_object_grid.getView().refresh();

									Ext.defer(function(){
										self.extension_parts_store_update(recs,true,false);
										upload_object_grid.setLoading(false);
										pallet_grid.setLoading(false);
										b.setDisabled(false);
									},250);

								}
							}catch(e){
								upload_object_grid.setLoading(false);
								pallet_grid.setLoading(false);
								b.setDisabled(false);
							}
						},100);
					}
				}
			},'-',' ','-',{
				xtype: 'checkboxfield',
				boxLabel: 'hide no use',
				id: 'hide-no-use-checkbox',
				listeners: {
					change: function(b,newValue,oldValue,eOpts){
						upload_object_grid.setLoading(true);
						b.setDisabled(true);

						var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
						var filters = [];
//						uploadObjectStore.clearFilter();
						if(newValue){
							uploadObjectStore.clearFilter(true);
							uploadObjectStore.filter('cm_use',true);
//							filters.push({
//								property: 'cm_use',
//								value: true
//							});
						}
						else{
							uploadObjectStore.clearFilter();
						}
						uploadObjectStore.on({
							load: {
								fn: function(store,records,successful,eOpts){
									upload_object_grid.setLoading(false);
									b.setDisabled(false);
								},
								single: true,
								scope: self
							}
						});
						var selected_art_ids = self.getSelectedArtIds();
						uploadObjectStore.setLoadUploadObjectAllStoreFlag();
						uploadObjectStore.loadPage(1,{
							params: { selected_art_ids: Ext.encode(selected_art_ids) },
//							filters: filters,
							sorters: uploadObjectStore.getUploadObjectLastSorters()
						});

					}
				}
			},'-',
			,' ','-',{
				itemId: 'download',
				xtype: 'button',
				text: 'Download',
				iconCls: 'pallet_download',
				disabled: true,
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
			'-','->',{
				hidden: !self.USE_OBJ_UPLOAD,
				xtype: 'tbseparator'
			},{
				hidden: !self.USE_OBJ_UPLOAD,
				itemId: 'delete',
				xtype: 'button',
				text: 'Delete',
				iconCls: 'pallet_delete',
				disabled: true,
				listeners: {
					click: function(b){
						b.setDisabled(true);

						var gridpanel = b.up('gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var records = selModel.getSelection();
						if(Ext.isEmpty(records)){
							b.setDisabled(false);
							return;
						}

						var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
						var delete_records = records.filter(function(r, i, a){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx>=0;
							});
							return (all_cm_map_versions.length===0);
						});
						var exclusion_records = records.filter(function(r, i, a){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx>=0;
							});
							return (all_cm_map_versions.length!==0);
						});
						selModel.deselectAll();

						var delete_mv_names = [];
						var delete_cm_names = [];
						delete_records.forEach(function(r){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx<0;
							});
							if(Ext.isArray(all_cm_map_versions)){
								all_cm_map_versions.forEach(function(v){
									delete_mv_names.push(v.mv_name_e);
									if(Ext.isArray(v.cm_names)){
										v.cm_names.forEach(function(c){
											delete_cm_names.push(v.mv_name_e + "\t" + c.art_id + "\t" + c.cdi_name);
										});
									}
								});
							}
						});


						var exclusion_mv_names = [];
						var exclusion_cm_names = [];
						exclusion_records.forEach(function(r){
							var all_cm_map_versions = (r.get('all_cm_map_versions') || []).filter(function(v){
								var idx = datasetMngStore.findBy(function(r){
									return r.get('md_id')==v.md_id && r.get('mv_id')==v.mv_id && r.get('md_id') && r.get('mv_frozen')
								});
								return idx>=0;
							});
							if(Ext.isArray(all_cm_map_versions)){
								all_cm_map_versions.forEach(function(v){
									exclusion_mv_names.push(v.mv_name_e);
									if(Ext.isArray(v.cm_names)){
										v.cm_names.forEach(function(c){
											exclusion_cm_names.push(v.mv_name_e + "\t" + c.art_id + "\t" + c.cdi_name);
										});
									}
								});
							}
						});

						if(Ext.isEmpty(delete_records)){
							var msg = '';
							if(exclusion_mv_names.length) msg += '['+Ext.Array.unique(exclusion_mv_names).join(',')+']で';
							msg += '使用中のデータは、削除できません';

							Ext.Msg.show({
								title: b.text,
								iconCls: b.iconCls,
								msg: msg,
								animateTarget: b.el,
								buttons: Ext.Msg.OK,
								icon: Ext.Msg.WARNING,
							});
							b.setDisabled(false);
							return;
						}
						selModel.select(delete_records);

						var msg = '';
						if(exclusion_records.length){
							if(exclusion_mv_names.length) msg += '['+Ext.Array.unique(exclusion_mv_names).join(',')+']で';
							msg += '使用中のデータは除外しました。<br>';
						}
						if(delete_mv_names.length){
//							if(delete_mv_names.length) msg += '['+Ext.Array.unique(delete_mv_names).join(',')+']で';
							msg += 'FMAIDに対応済みのデータが含まれています。<br>';
							var t = ['<div style="max-height:10em;overflow:auto;margin:0.5em 0em;padding-left:1em;background:white;"><table>'];
							delete_cm_names.forEach(function(v){
								var va = v.split(/\t/);
								t.push('<tr>');
								var tr = [];
								v.split(/\t/).forEach(function(v){
									tr.push('<td>'+v+'</td>');
								});
								t.push(tr.join('<td>:</td>'));
								t.push('</tr>');
							});
							t.push('</table></div>');
							msg += t.join('');
						}
						msg += '選択されているアップロードデータを削除してよろしいですか？';

						Ext.Msg.show({
							title: b.text,
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

								store.remove(delete_records);
								store.sync({
									callback: function(batch,options){
										b.setDisabled(false);
									},
									success: function(batch,options){
										var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
										palletPartsStore.suspendEvents(true);
										var find_recs = [];
										Ext.each(delete_records,function(r,i,a){
											var find_rec = palletPartsStore.findRecord( 'art_id', r.get('art_id'), 0, false, false, true ) ;
											if(find_rec) find_recs.push(find_rec);
										});
										if(find_recs.length) palletPartsStore.remove(find_recs);
										palletPartsStore.resumeEvents();
										Ext.getCmp('pallet-grid').getView().refresh();

										var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
										uploadGroupStore.loadPage(1);
									},
									failure: function(batch,options){
										var msg = AgLang.error_delete;
										var proxy = this;
										var reader = proxy.getReader();
										if(reader && reader.rawData && reader.rawData.msg){
											msg += ' ['+reader.rawData.msg+']';
										}
										Ext.Msg.show({
											title: b.text,
											iconCls: b.iconCls,
											msg: msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR,
											fn: function(buttonId,text,opt){
											}
										});
										store.loadPage(1);
									}
								});
							}
						});

					}
				}
			}


			]
		},{
			xtype: 'agpagingtoolbar',
			store: 'uploadObjectStore',   // same store GridPanel is using
			dock: 'bottom'
		}],
		listeners: {
			selectionchange: function(selModel,selected,eOpts){
				var grid = this;
				var toolbar = selModel.view.up('gridpanel').getDockedItems('toolbar[dock="top"]')[0];
				var disabled = Ext.isEmpty(selected);
				try{toolbar.getComponent('find').setDisabled(disabled);}catch(e){}
				toolbar.getComponent('download').setDisabled(disabled);
				toolbar.getComponent('delete').setDisabled(disabled);
			},

			render: function(grid,eOpts){
//				grid.getView().on({
//					beforeitemkeydown: function(view, record, item, index, e, eOpts){
//						return false;
//					}
//				});
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

	//pallet_storeをlocalStorageの内容で初期化
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
		id: 'pallet-grid',
		region: 'south',
		title: 'Pallet',
		split: true,
		height: self.panelHeight,
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
					var isCommit = false;
					if(e.field=='cdi_name'){
						if(Ext.isString(e.record.getChanges()['cdi_name']) || (!e.record.get('cm_use') && Ext.isString(e.record.get('cdi_name')) && e.record.get('cdi_name').length)){
							var cdi_name = Ext.String.trim(e.record.getChanges()['cdi_name'] || e.record.get('cdi_name') || '');
							var cdi_name_e = null;
							var cm_use = false;
							//2016-03-31用 START
							var conceptArtMapPartStore = Ext.data.StoreManager.lookup('conceptArtMapPartStore');
							var cmp_id = e.record.getChanges()['cmp_id'] || e.record.get('cmp_id') || 0;
//							var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', '', 0, false, false, true );
//							if(cmp_record) cmp_id = cmp_record.get('cmp_id');
							//2016-03-31用 END
							if(cdi_name.length){
								var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
								//2016-03-31用 START
								var m = self.regexpCdiNameLR.exec(cdi_name);
								if(Ext.isArray(m) && m.length){
									var tmp_cdi_name = m[1];
									var cmp_abbr = m[2].toUpperCase();
									cdi_name = tmp_cdi_name;
									var cmp_record = conceptArtMapPartStore.findRecord('cmp_abbr', cmp_abbr, 0, false, false, true );
									if(cmp_record) cmp_id = cmp_record.get('cmp_id');
								}
								//2016-03-31用 END
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
									cm_use = true;
								}
							}else{
								cdi_name = null;
//								cdi_name = (Ext.isObject(e.record.modified) && Ext.isString(e.record.modified.cdi_name) && e.record.modified.cdi_name.length) ? e.record.modified.cdi_name : null;
								if(cdi_name) cdi_name_e = e.record.get('cdi_name_e');
							}
//							var cm_use = Ext.isString(cdi_name_e);
							e.record.set('cm_use', cm_use);
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
								cm_use: cm_use,
								cmp_id: cmp_id
							}]);
							extraParams.comment = AgLang.fma_corresponding_change;

//							console.log(extraParams);
//							console.log(Ext.Object.toQueryString(extraParams,true));

							Ext.Ajax.request({
								url: 'api-upload-file-list.cgi?cmd=update_concept_art_map',
								method: 'POST',
								params: extraParams,
								callback: function(options,success,response){
//									console.log(options);
//									console.log(success);
//									console.log(response);
									if(!success){
										Ext.Msg.show({
											title: AgLang.fma_corresponding_change,
											msg: '['+response.status+'] '+response.statusText,
											iconCls: 'pallet_link',
											icon: Ext.Msg.ERROR,
											buttons: Ext.Msg.OK
										});
										e.record.reject();
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
										return;
									}

									var rep_id = null;
									e.record.set('cdi_name', cdi_name);
									e.record.set('cdi_name_e', cdi_name_e);
									e.record.set('cm_use', cm_use);
									e.record.set('rep_id', rep_id);
									e.record.set('cmp_id', cmp_id);
									e.record.commit();
//									self.update_localdb_pallet();

									Ext.each([Ext.data.StoreManager.lookup('uploadObjectStore'),Ext.data.StoreManager.lookup('uploadObjectAllStore')],function(store){
										if(Ext.isEmpty(store)) return true;
//										store.each(function(record){
//											if(record.get('art_id')!==art_id) return true;
//											record.set('cdi_name', cdi_name);
//											record.set('cdi_name_e', cdi_name_e);
//											record.set('cm_use', cm_use);
//											record.set('rep_id', rep_id);
//											record.set('cmp_id', cmp_id);
//											record.commit();
//										});

										store.suspendEvents(false);
										try{
											var startIdx = 0;
											var find_record;
											while(record = store.findRecord('art_id', art_id, startIdx, false, false, true)){
												record.set('cdi_name', cdi_name);
												record.set('cdi_name_e', cdi_name_e);
												record.set('cm_use', cm_use);
												record.set('rep_id', rep_id);
												record.set('cmp_id', cmp_id);
												record.commit();
												startIdx = store.indexOf(record);
												if(startIdx<0) break;
												startIdx++;
											}
										}catch(e){
											console.error(e);
										}
										store.resumeEvents();

									});
									Ext.getCmp('upload-object-grid').getView().refresh();
									Ext.getCmp('pallet-grid').getView().refresh();
//tree,list,filterも？

									if(Ext.isArray(json.art_group_datas)){
										var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
										var filters = uploadGroupStore._getFilters();
										uploadGroupStore.suspendEvents(true);
										Ext.each(json.art_group_datas,function(data){
											uploadGroupStore._setFilters([{
												anyMatch: false,
												caseSensitive: false,
												exactMatch: true,
												property: 'artg_delcause',
												value: null
											},{
												anyMatch: false,
												caseSensitive: false,
												exactMatch: true,
												property: 'artg_id',
												value: data.artg_id
											}]);
											uploadGroupStore.each(function(record){
												record.set('nomap_count',data.nomap_count);
												record.set('use_map_count',data.use_map_count);
												record.set('all_cm_map_versions',data.all_cm_map_versions);
												record.commit();
											});
										});
										uploadGroupStore.resumeEvents();
										uploadGroupStore._setFilters(filters);
									}
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
//			{text: '&#160;',  dataIndex: 'selected', xtype: 'agselectedcheckcolumn', width: 30, hidden: true, hideable: false, sortable: true},

			{text: 'Model',       dataIndex: 'model',   stateId: 'model', width: 40, hidden: true, hideable: false, xtype: 'agcolumn'},
			{text: 'Ver',         dataIndex: 'version', stateId: 'version', width: 40, hidden: true, hideable: false, xtype: 'agcolumn'},

			{text: AgLang.art_id, dataIndex: 'art_id',  stateId: 'art_id', width: 60, minWidth: 60, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.rep_id, dataIndex: 'rep_id',  stateId: 'rep_id', width: 60, minWidth: 60, hidden: false, hideable: true, xtype: 'agcolumn'},
			{
				text: AgLang.cdi_name,
				dataIndex: 'cdi_name',
				stateId: 'cdi_name',
//				xtype: 'agcolumncdi',
//				width: 70,
//				minWidth: 70,
				//2016-03-31用 START
				xtype: 'agcolumncdiname',
				width: 80,
				minWidth: 80,
				//2016-03-31用 END
				hidden: false,
				hideable: true,
				editor : {
					xtype: 'textfield',
					allowBlank: true,
					allowOnlyWhitespace: true,
					selectOnFocus: true,
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
			//2016-03-31用 START
			{
				text: 'Part',
				dataIndex: 'cmp_id',
				stateId: 'cmp_id',
				xtype: 'agcolumnconceptartmappart',
				width: 50,
				minWidth: 50,
				hidden: true,
				hideable: false,
				editor : {
					allowBlank: true,
					allowOnlyWhitespace: true,
//					selectOnFocus: true,
					editable: false,
					xtype: 'combobox',
					store: 'conceptArtMapPartStore',
					queryMode: 'local',
					displayField: 'cmp_title',
					valueField: 'cmp_id',
				}
			},
			//2016-03-31用 END
			{
				text: AgLang.cdi_name_e,
				dataIndex: 'cdi_name_e',
				stateId: 'cdi_name_e',
				flex: 2.0,
				minWidth: 80,
//				xtype: 'agcolumncdi',
				xtype: 'agcolumncdinamee',	//2016-03-31用
				//2016-03-31用 END
				hidden: false,
				hideable: true
			},
			{text: AgLang.category,      dataIndex: 'arta_category', stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.class_name,    dataIndex: 'arta_class',    stateId: 'arta_class',    width: 36, minWidth: 36, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.comment,       dataIndex: 'arta_comment',  stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.judge,         dataIndex: 'arta_judge',    stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: false, hideable: true, xtype: 'agcolumn'},

			{text: AgLang.file_name,     dataIndex: 'filename',      stateId: 'filename',      flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumn'},
			{text: AgLang.group_version, dataIndex: 'group',         stateId: 'group',         flex: 1,   minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumn'},

			{text: AgLang.file_size,     dataIndex: 'art_data_size', stateId: 'art_data_size', width: 60, hidden: true,  hideable: true,   xtype: 'agfilesizecolumn'},

			{text: AgLang.xmax,          dataIndex: 'xmax',       stateId: 'xmax',             width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xmin,          dataIndex: 'xmin',       stateId: 'xmin',             width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xcenter,       dataIndex: 'xcenter',    stateId: 'xcenter',          width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymax,          dataIndex: 'ymax',       stateId: 'ymax',             width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymin,          dataIndex: 'ymin',       stateId: 'ymin',             width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ycenter,       dataIndex: 'ycenter',    stateId: 'ycenter',          width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmax,          dataIndex: 'zmax',       stateId: 'zmax',             width: 55, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmin,          dataIndex: 'zmin',       stateId: 'zmin',             width: 55, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zcenter,       dataIndex: 'zcenter',    stateId: 'zcenter',          width: 59, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.volume,        dataIndex: 'volume',     stateId: 'volume',           width: 60, hidden: true, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

			{text: AgLang.timestamp,     dataIndex: 'mtime',      stateId: 'mtime',            width: 112, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME},

			{text: 'Color',              dataIndex: 'color',         stateId: 'color',         width: 40, hidden: false, hideable: false, xtype: 'agcolorcolumn'},
			{text: 'Opacity',            dataIndex: 'opacity',       stateId: 'opacity',       width: 44, hidden: false, hideable: false, xtype: 'agopacitycolumn'},
			{text: 'Hide',               dataIndex: 'remove',        stateId: 'remove',        width: 40, hidden: false, hideable: false, xtype: 'agcheckcolumn'},
			{text: 'Scalar',             dataIndex: 'scalar',        stateId: 'scalar',        width: 40, hidden: true,  hideable: false, xtype: 'agnumbercolumn', format: '0', editor: 'numberfield'}
		],

		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: true,
//			plugins: {
//				ptype: 'gridviewdragdrop',
//				dragText: 'Drag and drop to reorganize'
//			}
		},
		selType: 'rowmodel',
		selModel: {
			mode: 'MULTI',
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
															cm_use:     c_record.get('cm_use'),
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
													c_record.set('cm_use',false);
												}
												else if(cdi_name_regexp.test(arr[i])){

													var cdi_name = arr[i];
													var cmp_id = 0;
													if(Ext.isString(arr[i]) && arr[i].length){
														var m = self.regexpCdiNameLR.exec(cdi_name);
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
																c_record.set('rep_id', null);
															}
															if(c_record.get('cdi_name_e')!==f_record.get('cdi_name_e')) c_record.set('cdi_name_e', f_record.get('cdi_name_e'));
															if(!c_record.get('cm_use')) c_record.set('cm_use', true);
														}else{
															if(c_record.get('cm_use')) c_record.set('cm_use', false);
														}
													}else{
														if(c_record.get('cm_use')) c_record.set('cm_use', false);
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
												cm_use:     c_record.get('cm_use'),
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
/*
													Ext.each(records,function(record){
														datas.push({
															art_id:   record.get('art_id'),
															cdi_name: record.get('cdi_name'),
															cm_use:   record.get('cm_use')
														});
													});
*/
//													console.log(map_records);
													Ext.each(map_records,function(record){
														var p_record = palletPartsStore.findRecord( 'art_id', record.get('art_id'), 0, false, false, true );
														if(Ext.isEmpty(p_record)) return true;
														datas.push({
															art_id:   record.get('art_id'),
															cdi_name: record.get('cdi_name'),
															cm_use:   record.get('cm_use'),
															cmp_id:   record.get('cmp_id')
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

															var stores = [palletPartsStore, Ext.data.StoreManager.lookup('uploadObjectStore'),Ext.data.StoreManager.lookup('uploadObjectAllStore')];
															var rep_id = null;
															Ext.each(map_records,function(record){
																var art_id     = record.get('art_id');
																var cdi_name   = record.get('cdi_name');
																var cdi_name_e = record.get('cdi_name_e');
																var cm_use     = record.get('cm_use');
																var cmp_id     = record.get('cmp_id');
																Ext.each(stores,function(store){
																	if(Ext.isEmpty(store)) return true;
																	store.each(function(record){
																		if(record.get('art_id')!==art_id) return true;
																		record.set('cdi_name', cdi_name);
																		record.set('cdi_name_e', cdi_name_e);
																		record.set('cm_use', cm_use);
																		record.set('cmp_id', cmp_id);
																		record.set('rep_id', rep_id);
																		record.commit();
																	});
																});
															});

															if(Ext.isArray(json.art_group_datas)){
																var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
																var filters = uploadGroupStore._getFilters();
																uploadGroupStore.suspendEvents(true);
																Ext.each(json.art_group_datas,function(data){
																	uploadGroupStore._setFilters([{
																		anyMatch: false,
																		caseSensitive: false,
																		exactMatch: true,
																		property: 'artg_delcause',
																		value: null
																	},{
																		anyMatch: false,
																		caseSensitive: false,
																		exactMatch: true,
																		property: 'artg_id',
																		value: data.artg_id
																	}]);
																	uploadGroupStore.each(function(record){
																		record.set('nomap_count',data.nomap_count);
																		record.set('use_map_count',data.use_map_count);
																		record.set('all_cm_map_versions',data.all_cm_map_versions);
																		record.commit();
																	});
																});
																uploadGroupStore.resumeEvents();
																uploadGroupStore._setFilters(filters);
															}
															gridpanel.setLoading(false);
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
				xtype: 'tbspacer',
				width: 16
			},
			'-',
			{
				id: 'ag-pallet-edit-button-ver2',
				tooltip: 'Edit Selected',
				iconCls: 'pallet_edit',
				text: AgLang.file_info ,//+ '(New)',
				disabled: true,
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
								b.setDisabled(idx<0? true : false);
							}
						});
					},
					click: function(b,e,eOpts){
						if(b.isDisabled()) return;
						b.setDisabled(true);
						Ext.defer(function(){
							var grid = b.up('gridpanel');
							var selModel = grid.getSelectionModel();
							var records = [];
							Ext.each(selModel.getSelection(),function(r,i,a){
								if(Ext.isEmpty(r.data.art_id)) return true;
								records.push(r);
//								console.log(r.getData());
							});
							if(Ext.isEmpty(records)){
								b.setDisabled(false);
							}else{
								self.openObjEditWindow({
									title: b.text,
									iconCls: b.iconCls,
									records: records,
									callback: function(){
//										b.setDisabled(false);
									}
								});
								b.setDisabled(false);
							}
						},100);
					}
				}
			},
			{
				xtype: 'tbseparator',
				hidden: true
			},
			{
				hidden: true,
				id: 'ag-pallet-edit-button',
				tooltip: 'Edit Selected',
				iconCls: 'pallet_edit',
				text: AgLang.file_info,
				disabled: true,
				listeners: {
					click: function(b,e,eOpts){
						if(b.isDisabled()) return;
						b.setDisabled(true);
						Ext.defer(function(){
							var grid = b.up('gridpanel');
							var selModel = grid.getSelectionModel();
							var records = [];
							Ext.each(selModel.getSelection(),function(r,i,a){
								if(Ext.isEmpty(r.data.art_id)) return true;
								records.push(r);
							});
							if(Ext.isEmpty(records)){
								b.setDisabled(false);
							}else{
								show_obj_edit_window({
									title: b.text,
									iconCls: b.iconCls,
									records: records,
									callback: function(){
//										b.setDisabled(false);
									}
								});
								b.setDisabled(false);
							}
						},100);
					}
				}
			},

			{
				hidden: false,
				xtype: 'tbseparator',
			},{
				hidden: false,
				id : 'ag-pallet-download-button',
				xtype: 'button',
				text: 'Download',
				iconCls: 'pallet_download',
				disabled: true,
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
							type: 'pallet',
							records: recs,
							callback: function(){
								b.setDisabled(false);
							}
						}]);
					}
				}
			},

			'-',
			{
				id : 'ag-pallet-copy-button',
				tooltip   : 'Copy Selected',
				iconCls  : 'pallet_copy',
				disabled : true,
				listeners: {
					click : function(b,e,eOpts){
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
				}
			},
			'-',
			{
				tooltip   : 'Paste',
				iconCls   : 'pallet_paste',
				listeners: {
					click : function(b,e,eOpts){
						var gridpanel = b.up('gridpanel');
						if(gridpanel && gridpanel.rendered){
							var waitMask = new Ext.LoadMask({target:gridpanel,msg:"Please wait..."});
							waitMask.show();
							AgPalletUtils.pasteList(self,gridpanel.getStore(),function(records){
								var scrollTop = gridpanel.body.dom.scrollTop;
								gridpanel.getView().refresh();
								gridpanel.body.dom.scrollTop = scrollTop;
								waitMask.hide();
								if(records && records.length>0){
									Ext.defer(function(){
										self.update_other_pallet_store(records);
									},250);
								}
							});
						}
					}
				}
			},
			'-',
			{
				id : 'ag-pallet-delete-button',
				tooltip   : 'Delete Selected',
				iconCls  : 'pallet_delete',
				disabled : true,
				listeners: {
					click : function(b,e,eOpts){
						self.remove_select_records_pallet_store();
					}
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
//					beforeitemkeydown: function(view, record, item, index, e, eOpts){
//						if(e.getKey()==e.DELETE || (e.ctrlKey && e.getKey()==e.A)) return true;
//						return false;
//					},
					itemkeydown : function(view,record,item,index,e,eOpts){
						if(e.getKey()==e.DELETE){
							e.stopEvent();
							self.remove_select_records_pallet_store();
//						}else if(e.ctrlKey && e.getKey()==e.A){
//							e.stopEvent();
//							var selMode = pallet_grid.getSelectionModel();
//							selMode.selectAll();
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
			},
			itemcontextmenu: {
				fn: self.showPalletItemContextmenu,
				scope: self
			}
		}
	});


	var show_obj_edit_window = function(config){

		config = config || {};
		config.records = config.records || [];
		var aCB = config.callback;
		config.title = config.title || AgLang.file_info;
		config.iconCls = config.iconCls || 'pallet_edit';
		config.height = config.height || 667;
		config.width = config.width || 667;
		config.modal = config.modal || true;

		var maxHeight = $(document.body).height();
		var maxWidth = $(document.body).width();

		if(config.height>maxHeight) config.height = maxHeight;
		if(config.width>maxWidth) config.width = maxWidth;

		if(Ext.isEmpty(config.records)){
			if(aCB) (aCB)();
			return;
		}

		var window_id = 'obj-edit-window';
		var setDisabledSaveButton = function(){
			var win = Ext.getCmp(window_id);
			if(!win) return;
			var gridpanel = win.down('gridpanel');
			var store = gridpanel.getStore();
			var num = 0;
			num += store.getModifiedRecords().length;
			num += store.getNewRecords().length;
			num += store.getRemovedRecords().length;
			num += store.getUpdatedRecords().length;
			var formPanel = win.down('form');
			var disable = !formPanel.getForm().isValid();
			if(!disable) disable = num===0;
			win.getDockedItems('toolbar[dock="bottom"]')[0].down('button').setDisabled(disable);
		};
		var updateField = function(field){
			var name = field.getName();
			var value = field.getValue();
			if(!Ext.isEmpty(value) && Ext.isString(value)) value = Ext.String.trim(value);
			if(Ext.isEmpty(value)) value = null;
			var gridpanel = field.up('window').down('gridpanel');
			var select_recs = gridpanel.getSelectionModel().getSelection();
			Ext.each(gridpanel.getSelectionModel().getSelection(),function(rec){
				rec.beginEdit();
				rec.set(name,value);
				rec.endEdit(false,[name]);
			});
			setDisabledSaveButton();
		};

		var historyMappingStore = Ext.data.StoreManager.lookup('historyMappingStore');
		if(Ext.isEmpty(historyMappingStore)){
			historyMappingStore = Ext.create('Ext.data.Store', {
				storeId: 'historyMappingStore',
				model: 'HISTORY_MAPPING',
				proxy: {
					type: 'ajax',
					url: 'get-info.cgi?cmd=history-mapping',
					pageParam: undefined,
					startParam: undefined,
					limitParam: undefined,
					noCache: false,
					actionMethods : {
						create : 'POST',
						read   : 'POST',
						update : 'POST',
						destroy: 'POST'
					},
					reader: {
						type: 'json',
						root: 'datas'
					}
				},
				listeners: {
					beforeload: function(store,operation,eOpts){
						if(store.loading && store.getLastRequestOptions()) {
							var requests = Ext.Ajax.requests;
							var id;
							for(id in requests){
								if(requests.hasOwnProperty(id) && requests[id].options == store.getLastRequestOptions()){
									Ext.Ajax.abort(requests[id]);
//									console.log("historyMappingStore.beforeload():Ext.Ajax.abort()");
								}
							}
						}
						var beforerequest = function(conn,options,eOpts){
							store.setLastRequestOptions(options);
						};
						Ext.Ajax.on({
							beforerequest: beforerequest,
							single: true,
							scope: self
						});
					},
					add: function(store,records,index,eOpts){
					},
					remove: function(store,record,index,eOpts){
					},
					update: function(store,record,operation){
					}
				}
			});
			historyMappingStore.setLastRequestOptions = function(options){
				historyMappingStore._LastRequestOptions = options;
			};
			historyMappingStore.getLastRequestOptions = function(){
				return historyMappingStore._LastRequestOptions;
			};
		}

		var objEditStore = Ext.data.StoreManager.lookup('objEditStore');
		if(Ext.isEmpty(objEditStore)){
			objEditStore = Ext.create('Ext.data.ArrayStore', {
				storeId: 'objEditStore',
				model: 'PALLETPARTS',
				listeners: {
					add: function(store,records,index,eOpts){
//						console.log("objEditStore.add()");
					},
					remove: function(store,record,index,eOpts){
//						console.log("objEditStore.remove()");
					},
					update: function(store,record,operation){
//						console.log("objEditStore.update():"+operation);
						setDisabledSaveButton();
					}
				}
			});
		}

		var loadRecords = [];
		Ext.each(config.records,function(r,i,a){
			var rec = r.copy();
			Ext.data.Model.id(rec);
			loadRecords.push(rec);
		});

		objEditStore.loadRecords(loadRecords);
		var record = config.records[0];

		var versionCombobox = Ext.getCmp('version-combobox');
		var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
		var mv_frozen = r.data.mv_frozen;

		var obj_edit_window = Ext.create('Ext.window.Window', {
			id: window_id,
			title: config.title,
			iconCls: config.iconCls,
			modal: config.modal,
			height: config.height,
			width: config.width,
			buttons: [{
				text: AgLang.save,
				disabled: true,//mv_frozen,
				listeners: {
					click: function(b,e,eOpts){
						var formPanel = b.up('form');
						if(Ext.isEmpty(formPanel)) formPanel = b.up('window').down('form');
						if(Ext.isEmpty(formPanel)) return;

						if(b.isDisabled()) return;
						b.up('window').setLoading(true);
						b.setDisabled(true);

						var form = formPanel.getForm();
						var win = b.up('window');
						var art_ids = [];
						objEditStore.each(function(r){
							art_ids.push(r.data.art_id)
						});
//						var versionCombobox = Ext.getCmp('version-combobox');
//						var v_rec = versionCombobox.findRecordByValue(versionCombobox.getValue());
//						var treeCombobox = Ext.getCmp('tree-combobox');
//						var t_rec = treeCombobox.findRecordByValue(treeCombobox.getValue());

						var p = self.getExtraParams();
						p.art_ids = Ext.encode(art_ids);

						form.submit({
							clientValidation: true,
							params: p,
							success: function(form,action){

								var fieldValues = form.getFieldValues(false);
								var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
								var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
								var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');

								var values = b.up('window').down('form').getForm().getFieldValues();
								var art_datas = [];

								objEditStore.each(function(r){
									var idx = -1;
									do{
										idx = palletPartsStore.findBy(function(findRec,id){
											return (findRec.data.art_id===r.data.art_id);
										},self,idx+1);
										if(idx>=0){
											var rec = palletPartsStore.getAt(idx);
											if(rec){
												var names = [];
												rec.beginEdit();
												Ext.Object.each(fieldValues,function(key,val){
													if(rec.get(key) == val) return true;
													rec.set(key,val);
													names.push(key);
												});
												if(names.length){
													rec.commit(false,names);
												}else{
													rec.cancelEdit();
												}
											}
										}
									}while(idx>=0);


									idx = -1;
									do{
										idx = uploadObjectAllStore.findBy(function(findRec,id){
											return (findRec.data.art_id===r.data.art_id);
										},self,idx+1);
										if(idx>=0){
											var rec = uploadObjectAllStore.getAt(idx);
											if(rec){
												art_datas.push({
													art_id: rec.data.art_id,
													artg_id: rec.data.artg_id
												});
											}
										}
									}while(idx>=0);


									if(values['mirror']){
										var art_mirroring_id = r.data.art_id;
										if(art_mirroring_id.match(/^(.+)M$/)){
											art_mirroring_id = RegExp.$1;
										}else{
											art_mirroring_id += 'M';
										}
										var idx = uploadObjectAllStore.findBy(function(findRec,id){
											return (findRec.data.art_id===art_mirroring_id);
										},self,0);
										if(idx<0){
											art_datas.push({
												art_id: art_mirroring_id,
												artg_id: r.data.artg_id
											});
										}
										while(idx>=0){
											var rec = uploadObjectAllStore.getAt(idx);
											if(rec){
												art_datas.push({
													art_id: rec.data.art_id,
													artg_id: rec.data.artg_id
												});
											}
											idx = uploadObjectAllStore.findBy(function(findRec,id){
												return (findRec.data.art_id===art_mirroring_id);
											},self,idx+1);
										};
									}
								});

								var viewDom = Ext.getCmp('upload-group-grid').getView().el.dom;
								var scX = viewDom.scrollLeft;
								var scY = viewDom.scrollTop;

								Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
									callback: function(records, operation, success){

										Ext.getCmp('upload-group-grid').getView().scrollBy(scX,scY,false);

//										var values = b.up('window').down('form').getForm().getFieldValues();
//										if(!values['mirror']){
//											b.setDisabled(false);
//											b.up('window').setLoading(false);
//											b.up('window').close();
//											return;
//										}

										var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
										var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');

										if(!self.beforeloadStore(uploadObjectStore)) return false;
										var p = uploadObjectStore.getProxy();
										var extraParams = Ext.Object.merge({art_datas:Ext.encode(art_datas)},p.extraParams||{});
//										console.log(extraParams);

//										console.log('Ext.Ajax.request():api-upload-file-list.cgi?cmd=read');
										Ext.Ajax.request({
											url: 'api-upload-file-list.cgi?cmd=read',
											method: 'POST',
											params: Ext.Object.toQueryString(extraParams,true),
											callback: function(options,success,response){
//												uploadObjectStore.fireEvent('load', uploadObjectStore, uploadObjectStore.getRange(), true);
											},
											success: function(response,options){
//												console.log(response);
												var json;
												var records;
												try{json = Ext.decode(response.responseText)}catch(e){};
												if(Ext.isEmpty(json) || Ext.isEmpty(json.datas) || json.success==false) return;
//												console.log(json);
												uploadObjectAllStore.suspendEvents(true);
												var addrecs = [];
												Ext.each(json.datas,function(data,i){
													var idx = uploadObjectAllStore.findBy(function(findRec,id){
														return (findRec.data.art_id==data.art_id && findRec.data.artg_id==data.artg_id) ? true : false;
													},self,0);

													if(idx<0){
														addrecs.push(Ext.apply({},{selected: true},data));
													}else{
														while(idx>=0){
															var rec = uploadObjectAllStore.getAt(idx);
															if(rec){
																var names = [];
																rec.beginEdit();
																Ext.Object.each(data,function(key,val){
																	if(key=='selected' || rec.get(key) == val) return true;
																	rec.set(key,val);
																	names.push(key);
																});
																if(names.length){
																	rec.commit(false,names);
																}else{
																	rec.cancelEdit();
																}
															}
															idx = uploadObjectAllStore.findBy(function(findRec,id){
																return (findRec.data.art_id==data.art_id && findRec.data.artg_id==data.artg_id) ? true : false;
															},self,idx+1);
														}
													}
												});
												if(addrecs.length){
													uploadObjectAllStore.add(addrecs);

													var palletPartsStore = Ext.data.StoreManager.lookup('palletPartsStore');
													palletPartsStore.suspendEvents(true);
													palletPartsStore.add(addrecs);
													palletPartsStore.resumeEvents();
												}
												uploadObjectAllStore.resumeEvents();

												var viewDom = Ext.getCmp('upload-object-grid').getView().el.dom;
												var scX = viewDom.scrollLeft;
												var scY = viewDom.scrollTop;
												var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
												uploadObjectStore.on({
													load: {
														fn: function(store,records,successful,eOpts){
															var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
//															self.extension_parts_store_update(uploadObjectAllStore.getRange(),false,false);

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

															b.setDisabled(false);
															b.up('window').setLoading(false);
															b.up('window').close();

															Ext.getCmp('upload-object-grid').getView().scrollBy(scX,scY,false);
														},
														single: true,
														scope: self
													}
												});
												uploadObjectStore.loadPage(uploadObjectStore.currentPage);


											},
											failure: function(response,options){
//												console.log(response);
											}
										});
									}
								});



							},
							failure: function(form,action){
//								console.log('failure()');
//								console.log(form);
//								console.log(action);
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
										Ext.data.StoreManager.lookup('datasetMngStore').loadPage(1);
								}
								b.setDisabled(false);
								b.up('window').setLoading(false);
							}
						});
					}
				}
			},{
				text: AgLang.close,
				listeners: {
					click: function(b,e,eOpts){
						if(aCB) (aCB)();
						b.up('window').close();
					}
				}
			}],
			layout: 'border',
			items: [{
				region: 'north',
				split: true,
				height: 100,
				xtype: 'gridpanel',
				columnLines: true,
				store: 'objEditStore',
				stateful: true,
				stateId: 'objedit-north-grid',
				columns: [
					{xtype: 'rownumberer'},
					{text: '&#160;',         dataIndex: 'selected', stateId: 'selected', width: 30, minWidth: 30, hidden: true,  hideable: false, xtype: 'agselectedcheckcolumn'},
					{text: AgLang.art_id,    dataIndex: 'art_id',   stateId: 'art_id',   width: 60, minWidth: 60, hidden: false, hideable: true},
					{text: AgLang.group,     dataIndex: 'group',    stateId: 'group',    flex: 1,   minWidth: 80, hidden: false, hideable: true},
					{text: AgLang.file_name, dataIndex: 'filename', stateId: 'filename', flex: 1,   minWidth: 80, hidden: false, hideable: true},
					{text: AgLang.cdi_name,  dataIndex: 'cdi_name', stateId: 'cdi_name', width: 80, minWidth: 80, hidden: true,  hideable: false, xtype: 'agcolumncdiname'},
					{text: AgLang.use,       dataIndex: 'cm_use',   stateId: 'cm_use',   width: 34, minWidth: 34, hidden: true,  hideable: false, draggable: false, xtype: 'agbooleancolumn', disabled:mv_frozen}
				],
				selType: 'rowmodel',
				selModel: {
					mode: 'SINGLE'
//					mode: 'MULTI'
				},
				listeners: {
					afterrender: function(comp){
//						console.log("afterrender()");
						var selModel = comp.getSelectionModel();
						if(selModel.getSelectionMode() == 'MULTI'){
							selModel.selectAll();
						}else{
							selModel.select(comp.getStore().getAt(0));
						}
					},
					selectionchange: function(selModel,selected,eOpts){
//						console.log("selectionchange()");
						var grid = this;
						var toolbar = grid.getDockedItems('toolbar[dock="top"]')[0];
						var disabled = Ext.isEmpty(selected);
						toolbar.getComponent('find').setDisabled(disabled);

						var record = selected[0];
						if(Ext.isEmpty(record)) return;

						var form = selModel.view.up('window').down('form');
						var basicForm = form.getForm();
						var fields = basicForm.getFields();
						fields.each(function(field,index,len){
							field.suspendEvents(false);
						});
						try{basicForm.loadRecord(record);}catch(e){console.error(e);}
						fields.each(function(field,index,len){
							field.resumeEvents();
						});

						var historyMappingStore = Ext.data.StoreManager.lookup('historyMappingStore');
						if(Ext.isEmpty(historyMappingStore)) return;
						if(selected.length>1){
							historyMappingStore.removeAll();
							if(!mv_frozen){
								fields.each(function(field,index,len){
									field.setDisabled(true);
								});
								var button = form.down('button');
								while(button){
									button.setDisabled(true);
									button = button.next('button');
								}
								var gridpanel = form.down('gridpanel');
								while(gridpanel){
									gridpanel.setDisabled(true);
									gridpanel = gridpanel.next('gridpanel');
								}
							}
						}
						else{
							historyMappingStore.loadPage(1,{
								params: {
									art_id: record.data.art_id
								},
								sorters: [{
									property: 'hist_timestamp',
									direction: 'DESC'
								}]
							});
							if(!mv_frozen){
								fields.each(function(field,index,len){
									field.setDisabled(false);
								});
								var button = form.down('button');
								while(button){
									button.setDisabled(false);
									button = button.next('button');
								}
								var gridpanel = form.down('gridpanel');
								while(gridpanel){
									gridpanel.setDisabled(false);
									gridpanel = gridpanel.next('gridpanel');
								}
							}
						}

						if(!mv_frozen){
							var mirrorfield = basicForm.findField('mirror');
							if(mirrorfield) mirrorfield.setDisabled((selected.length>1 || record.data.art_id.match(/M$/))? true : false);
						}

					}
				}
			},{
				region: 'center',
				xtype: 'form',
				url: 'api-upload-file-list.cgi?cmd=update',
				method: 'POST',
				autoScroll: true,
				border: false,
				bodyStyle: 'background:transparent;padding:10px 10px 0px 10px;',
				defaults: {
					labelAlign: 'right',
					labelWidth: 56,
					anchor: '100%'
				},
				items: [
				{
					xtype: 'fieldset',
					title: 'Concept',
//					checkboxToggle: true,
//					collapsed: false,
//					checkboxName: 'map_concept',
					defaults: {
						labelAlign: 'right',
						labelWidth: 56,
						anchor: '100%'
					},
					items: [{
						xtype: 'displayfield',
						fieldLabel: AgLang.version,
						name: 'mv_name_e',
						value: record.data.mv_name_e
					},{
						xtype: 'fieldcontainer',
						fieldLabel: AgLang.cdi_name,
						bodyStyle: 'background:transparent;',
						border: false,
						layout: {
							type: 'hbox',
							pack: 'start'
						},
						items: [{
							disabled: mv_frozen,
							width: 88,
//							xtype: 'textfield',
							xtype: 'combobox',
							store: 'fmaAllStore',
							queryMode: 'local',
							displayField: 'cdi_name',
							valueField: 'cdi_name',
							hideTrigger: true,
							anyMatch: true,

							itemId: 'cdi_name',
							name: 'cdi_name',
							value: record.data.cdi_name,
							selectOnFocus: true,
							enableKeyEvents: true,
							validator: function(value){
								var field = this;
								if(Ext.isString(value)){
									var s = Ext.String.trim(value);
									if(Ext.isEmpty(s)) return true;
								}else{
									if(Ext.isEmpty(s)) return true;
								}
								var displayfield = field.up('fieldset').getComponent('cdi_name_e');
								if(Ext.isEmpty(displayfield.getValue())) return AgLang.error_cdi_name;
								return true;
							},
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
//									if(field.getXType()!=='textfield') return;

									if(Ext.isString(newValue)) newValue = Ext.String.trim(newValue);
									field.clearInvalid();
									var displayfield = field.up('fieldset').getComponent('cdi_name_e');
									if(Ext.isEmpty(newValue)){
										displayfield.setValue('');
//										field.focus(false);
										updateField(field);
									}else{
										var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
										if(fmaAllStore.isLoading()){
											var params = self.getExtraParams() || {};
											params.cmd = 'read';
											params.cdi_name = newValue;
											displayfield.setLoading(true);
											Ext.Ajax.request({
												url: 'get-fma-list.cgi',
												autoAbort: true,
												method: 'POST',
												params: params,
												callback: function(options,success,response){
													displayfield.setLoading(false);
													var json;
													try{json = Ext.decode(response.responseText)}catch(e){};
													if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
														displayfield.setValue('');
													}
													else{
														var data = json.datas[0];
														displayfield.setValue(data.cdi_name_e);
													}
													field.validate();
//													field.focus(false);
													updateField(field);
												}
											});
										}else{
											var record = fmaAllStore.findRecord('cdi_name', newValue, 0, false, false, true );
											if(Ext.isEmpty(record)){
												displayfield.setValue('');
											}else{
												displayfield.setValue(record.get('cdi_name_e'));
											}
											field.validate();
//											field.focus(false);
											updateField(field);
										}
									}
								},
								beforequery: function( queryPlan, eOpts ){
									var field = queryPlan.combo;
									if(field.getXType()!=='combobox') return;
									queryPlan.cancel = (queryPlan.query.length<4);
									if(!field.getValue() || Ext.String.trim(field.getValue()).length==0){
										var displayfield = field.up('fieldset').getComponent('cdi_name_e');
										displayfield.setValue('');
										updateField(field);
									}
								},
								select: function( field, records, eOpts ){
									return;
									if(field.getXType()!=='combobox') return;
									var newValue = Ext.String.trim(field.getValue());

									field.clearInvalid();
									var displayfield = field.up('fieldset').getComponent('cdi_name_e');
									if(Ext.isEmpty(newValue)){
										displayfield.setValue('');
//										field.focus(false);
										updateField(field);
									}else{
										var record;
										if(Ext.isArray(records)){
											record = records[0];
										}else{
											record = records;
										}
										if(Ext.isEmpty(record)){
											displayfield.setValue('');
										}else{
											displayfield.setValue(record.get('cdi_name_e'));
										}
										field.validate();
//										field.focus(false);
										updateField(field);
									}
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
							disabled: mv_frozen,
							width: 100,
							xtype: 'button',
							iconCls: 'pallet_find',
							text: 'FMA Search',
							listeners: {
								click: function(b,e,eOpts){
									self.openFMASearch({
										title: b.text,
										iconCls: b.iconCls,
										query: Ext.String.trim(b.prev('textfield').getValue()),
										callback: function(record){
											if(Ext.isEmpty(record)) return;
											var basicForm = b.up('form').getForm();

											var mirroring = false;
											var mirror_fieldset = b.up('fieldset').nextSibling('fieldset');
//											console.log(mirror_fieldset);
											if(!mirror_fieldset.collapsed) mirroring = true;

											var same_concept = false;
											if(mirroring){
												var same_concept_checkbox = basicForm.findField('mirror_same_concept');
												if(same_concept_checkbox) same_concept = same_concept_checkbox.getValue();
											}

											Ext.each(['cdi_name','cdi_name_e'],function(name,index,arr){
												var field = basicForm.findField(name);
												if(Ext.isEmpty(field)) return true;
//												field.setValue(record.get(name));
												field.suspendEvents(false);
												field.setValue(record.get(name));
												field.resumeEvents();
												if(field.clearInvalid) field.clearInvalid();
												updateField(field);

												if(!same_concept) return true;

												var mirror_field = basicForm.findField('mirror_'+name);
												if(Ext.isEmpty(mirror_field)) return true;
//												mirror_field.setValue(field.getValue());
												mirror_field.suspendEvents(false);
												mirror_field.setValue(field.getValue());
												mirror_field.resumeEvents();
												if(mirror_field.clearInvalid) mirror_field.clearInvalid();
												updateField(mirror_field);

											});
										}
									});
								}
							}
						},{
							disabled: mv_frozen,
							width: 110,
							xtype: 'button',
							iconCls: 'pallet_table_list',
							text: AgLang.all_fma_list,
							listeners: {
								click: function(b,e,eOpts){
									var btn = Ext.getCmp('all-fma-list-button');
									btn.fireEvent('click',btn);
								}
							}
						},{
							disabled: mv_frozen,
							width: 22,
							xtype: 'button',
							iconCls: 'pallet_delete',
							listeners: {
								click : function(b,e,eOpts){
									var field = b.up('fieldcontainer').getComponent('cdi_name');
									if(field.getValue()){
										field.setValue('');
										field.clearInvalid();
										updateField(field);
									}
									var displayfield = field.up('fieldset').getComponent('cdi_name_e');
									displayfield.setValue('');
									field.focus(false);
								}
							}
						}]
					},{
						xtype: 'displayfield',
						fieldLabel: AgLang.cdi_name_e,
						name: 'cdi_name_e',
						itemId: 'cdi_name_e',
						value: record.data.cdi_name_e,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							}
						}
					},{
						disabled: mv_frozen,
						xtype: 'textfield',
						fieldLabel: AgLang.comment,
						name: 'cm_comment',
						value: record.data.cm_comment,
						listeners: {
							change: function(field,newValue,oldValue,eOpts){
								updateField(field);
							},
							buffer: 100
						}
					},{
						xtype: 'fieldcontainer',
						bodyStyle: 'background:transparent;',
						border: false,
						layout: {
							type: 'hbox',
							pack: 'start'
						},
						defaults: {
							labelAlign: 'right',
							labelWidth: 62
						},
						items: [{
							disabled: mv_frozen,
							xtype: 'checkboxfield',
							fieldLabel: AgLang.use,
							inputValue: 'true',
							name: 'cm_use',
							checked: record.data.cm_use,
							value: record.data.cm_use,
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									updateField(field);
								},
								buffer: 100
							}
						},{
							disabled: mv_frozen,
							xtype: 'checkboxfield',
							hideLabel: true,
							boxLabel: 'Set same use / no-use setting to mirror part.',
							inputValue: 'true',
							margin: '0 0 0 30',
							name: 'set_same_use_setting_mirror_part',
							checked: false,
							value: false,
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									updateField(field);
								},
								buffer: 100
							}
						}]
					},{
						height: 100,
						xtype: 'gridpanel',
						fieldLabel: AgLang.history,

						columnLines: true,
						store: 'historyMappingStore',
						stateful: true,
						stateId: 'objedit-history-grid',
						columns: [
							{xtype: 'rownumberer'},
							{text: AgLang.hist_event, dataIndex: 'he_name',        stateId: 'he_name',        width: 50, minWidth: 50, hidden: false, hideable: true},
							{text: AgLang.version,    dataIndex: 'mv_name_e',      stateId: 'mv_name_e',      width: 40, minWidth: 40, hidden: false, hideable: true},
							{text: AgLang.cdi_name,   dataIndex: 'cdi_name',       stateId: 'cdi_name',       width: 80, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdiname'},
							{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e',     stateId: 'cdi_name_e',     flex: 1,   minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdinamee'},

							{text: AgLang.cdi_name_j, dataIndex: 'cdi_name_j',     stateId: 'cdi_name_j',     flex: 1,    minWidth: 80, hidden: true,  hideable: false, xtype: 'agcolumncdi'},
							{text: AgLang.cdi_name_k, dataIndex: 'cdi_name_k',     stateId: 'cdi_name_k',     flex: 1,    minWidth: 80, hidden: true,  hideable: false, xtype: 'agcolumncdi'},
							{text: AgLang.cdi_name_l, dataIndex: 'cdi_name_l',     stateId: 'cdi_name_l',     flex: 1,    minWidth: 80, hidden: true,  hideable: false, xtype: 'agcolumncdi'},

							{text: AgLang.comment,    dataIndex: 'cm_comment',     stateId: 'cm_comment',     flex: 1,   minWidth: 80, hidden: false, hideable: true},
							{text: AgLang.use,        dataIndex: 'cm_use',         stateId: 'cm_use',         width: 32,  minWidth: 32,  hidden: false, hideable: true, xtype: 'agbooleancolumn'},
							{text: AgLang.user,       dataIndex: 'cm_openid',      stateId: 'cm_openid',      width: 112, minWidth: 112, hidden: true,  hideable: false},
							{text: AgLang.timestamp,  dataIndex: 'hist_timestamp', stateId: 'hist_timestamp', width: 112, minWidth: 112, hidden: false, hideable: true, xtype: 'datecolumn', format: self.FORMAT_DATE_TIME}
						],
						selType: 'rowmodel',
						selModel: {
							mode: 'SINGLE'
						}

					}]
				},{
					fieldLabel: AgLang.category,
					xtype: 'textfield',
					name: 'art_category',
					value: record.data.art_category,
					selectOnFocus: true,
					enableKeyEvents: true,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							updateField(field);
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
					fieldLabel: AgLang.class_name,
					xtype: 'textfield',
					name: 'art_class',
					value: record.data.art_class,
					selectOnFocus: true,
					enableKeyEvents: true,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							updateField(field);
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
					fieldLabel: AgLang.comment,
					xtype: 'textfield',
					name: 'art_comment',
					value: record.data.art_comment,
					selectOnFocus: true,
					enableKeyEvents: true,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							updateField(field);
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
					fieldLabel: AgLang.judge,
					xtype: 'textfield',
					name: 'art_judge',
					value: record.data.art_judge,
					selectOnFocus: true,
					enableKeyEvents: true,
					listeners: {
						change: function(field,newValue,oldValue,eOpts){
							updateField(field);
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
					xtype: 'fieldset',
					title: 'Mirroring',
					checkboxToggle: true,
					collapsed: true,
					checkboxName: 'mirror',
					style: {
						marginBottom: '0px',
						padding: '0px 10px 0px 10px'
					},
					listeners: {
						collapse: function(field, eOpts){
							var f = field.child('fieldset');
							if(f) f.collapse();
						},
						expand: function(field, eOpts){
							var f = field.child('fieldset');
							if(f) f.expand();
						},
						afterrender: {
							fn: function(field, eOpts){
								if(field.collapsed){
									field.fireEvent('collapse',field);
								}
								field.checkboxCmp.on({
									change: function(field,newValue,oldValue,eOpts){
										updateField(field);
									}
								});
							},
							single: true,
							buffer:100
						},
						disable: function(field, eOpts){
//							console.log('disable()');
						},
						enable: function(field, eOpts){
//							console.log('enable()');
						}
					},
					items: [{
						xtype: 'fieldset',
						title: 'Concept',
//						checkboxToggle: true,
//						collapsed: false,
//						checkboxName: 'mirror_map_concept',
						style: {
							padding: '0px 5px 5px 5px'
						},
						defaults: {
							labelAlign: 'right',
							labelWidth: 62
						},
						listeners: {
							collapse: function(field, eOpts){
								if(mv_frozen) return;
								var f = field.child('checkboxfield');
								if(f){
									f.setDisabled(true);
									f = f.nextSibling('fieldcontainer');
									if(f){
										f.setDisabled(true);
										f = field.nextSibling('displayfield');
										if(f) f.setDisabled(true);
									}
								}
							},
							expand: function(field, eOpts){
								if(mv_frozen) return;
								var f = field.child('checkboxfield');
								if(f){
									f.setDisabled(false);
									f.fireEvent('change',f,f.getValue());
								}

								var form = field.up('form').getForm();
								var mirror_cdi_name = form.findField('mirror_cdi_name');
								var mirror_cdi_name_e = form.findField('mirror_cdi_name_e');

								var art_ids = [];
								var gridpanel = field.up('window').down('grid');
								var records = gridpanel.getSelectionModel().getSelection();
								var store = gridpanel.getStore();
								Ext.each(records,function(r){
									var art_id = r.get('art_id');
									if(Ext.isEmpty(art_id)) return true;
									var art_mirror_id = null;
									if(art_id.match(/^([A-Z]+[0-9]+)(M*)$/)){
										art_mirror_id = RegExp.$1;
										if(Ext.isEmpty(RegExp.$2)) art_mirror_id += 'M';
									}
									if(Ext.isEmpty(art_mirror_id)) return true;
									art_ids.push({art_id:art_mirror_id});
								});
								if(Ext.isEmpty(art_ids)){
									if(mirror_cdi_name) mirror_cdi_name.setValue(null);
									if(mirror_cdi_name_e) mirror_cdi_name_e.setValue(null);
									return;
								}

								var params = self.getExtraParams() || {};
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
										if(json.datas[0]['cdi_name'] && mirror_cdi_name){
											mirror_cdi_name.suspendEvents(false);
											mirror_cdi_name.setValue(json.datas[0]['cdi_name']);
											mirror_cdi_name.resumeEvents();
											mirror_cdi_name.clearInvalid();
										}
										if(json.datas[0]['cdi_name_e'] && mirror_cdi_name_e) mirror_cdi_name_e.setValue(json.datas[0]['cdi_name_e']);
									}
								});

							}
						},
						items: [{
							disabled: mv_frozen,
							xtype: 'checkboxfield',
							fieldLabel: 'Concept',
							boxLabel: 'Same Concept',
							name: 'mirror_same_concept',
							listeners: {
								change: function(field, newValue, oldValue, eOpts){
									var f = field.nextSibling('fieldcontainer');
									if(f){
										f.setDisabled(newValue);
										f = field.nextSibling('displayfield');
										if(f) f.setDisabled(newValue);
									}
									if(newValue){
										var scrollTop = field.up('panel').body.dom.scrollTop;
										var basicForm = field.up('form').getForm();
										Ext.each(['cdi_name','cdi_name_e'],function(name,index,arr){
											var field = basicForm.findField(name);
											if(Ext.isEmpty(field)) return true;
											var mirror_field = basicForm.findField('mirror_'+name);
											if(Ext.isEmpty(mirror_field)) return true;
											mirror_field.suspendEvents(false);
											mirror_field.setValue(field.getValue());
											mirror_field.resumeEvents();
											updateField(mirror_field);
										});
										field.up('panel').body.dom.scrollTop = scrollTop;
									}
								}
							}
						},{
							xtype: 'fieldcontainer',
							bodyStyle: 'background:transparent;',
							border: false,
							anchor: '100%',
							layout: {
								type: 'hbox',
								pack: 'start'
							},
							defaults: {
								labelAlign: 'right',
								labelWidth: 62
							},
							listeners: {
								disable: function(field,eOpts){
									var cfield = field.child('textfield');
									while(cfield){
										cfield.setDisabled(true);
										cfield = cfield.nextSibling('button');
									}
								},
								enable: function(field,eOpts){
									var cfield = field.child('textfield');
									while(cfield){
										cfield.setDisabled(false);
										cfield = cfield.nextSibling('button');
									}
								}
							},
							items: [{
								disabled: mv_frozen,
								width: 155,
								fieldLabel: AgLang.cdi_name,

//								xtype: 'textfield',
								xtype: 'combobox',
								store: 'fmaMirrorAllStore',
								queryMode: 'local',
								displayField: 'cdi_name',
								valueField: 'cdi_name',
								hideTrigger: true,
								anyMatch: true,

								itemId: 'mirror_cdi_name',
								name: 'mirror_cdi_name',
								value: record.data.mirror_cdi_name,
								selectOnFocus: true,
								enableKeyEvents: true,
								validator: function(value){
									var field = this;
									if(Ext.isString(value)){
										var s = Ext.String.trim(value);
										if(Ext.isEmpty(s)) return true;
									}else{
										if(Ext.isEmpty(value)) return true;
									}
									var displayfield = field.up('fieldset').getComponent('mirror_cdi_name_e');
									if(Ext.isEmpty(displayfield.getValue())) return AgLang.error_cdi_name;
									return true;
								},
								listeners: {
									change: function(field,newValue,oldValue,eOpts){
//										if(field.getXType()!=='textfield') return;

										if(Ext.isString(newValue)) newValue = Ext.String.trim(newValue);
										field.clearInvalid();

										var displayfield = field.up('fieldset').getComponent('mirror_cdi_name_e');
										if(Ext.isEmpty(newValue)){
											displayfield.setValue('');
//											field.focus(false);
											updateField(field);
											return;
										}else{
											var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
											if(fmaAllStore.isLoading()){

												var params = self.getExtraParams() || {};
												params.cmd = 'read';
												params.cdi_name = newValue;

												displayfield.setLoading(true);
												Ext.Ajax.request({
													url: 'get-fma-list.cgi',
													autoAbort: true,
													method: 'POST',
													params: params,
													callback: function(options,success,response){
														displayfield.setLoading(false);

														var json;
														try{json = Ext.decode(response.responseText)}catch(e){};
														if(!success || Ext.isEmpty(json) || Ext.isEmpty(json.success) || !json.success || Ext.isEmpty(json.datas)){
															displayfield.setValue('');
															field.validate();
//															field.focus(false);
															updateField(field);
															return;
														}
														var data = json.datas[0];
														displayfield.setValue(data.cdi_name_e);
														field.validate();
//														field.focus(false);
														updateField(field);
													}
												});
											}else{
												var record = fmaAllStore.findRecord('cdi_name', newValue, 0, false, false, true );
												if(Ext.isEmpty(record)){
													displayfield.setValue('');
												}else{
													displayfield.setValue(record.get('cdi_name_e'));
												}
												field.validate();
//												field.focus(false);
												updateField(field);
											}
										}
									},
									beforequery: function( queryPlan, eOpts ){
										var field = queryPlan.combo;
										if(field.getXType()!=='combobox') return;
										queryPlan.cancel = (queryPlan.query.length<4);
										if(!field.getValue() || Ext.String.trim(field.getValue()).length==0){
											var displayfield = field.up('fieldset').getComponent('mirror_cdi_name_e');
											displayfield.setValue('');
										}
									},
									select: function( field, records, eOpts ){
										return;
										if(field.getXType()!=='combobox') return;
										var newValue = Ext.String.trim(field.getValue());

										field.clearInvalid();

										var displayfield = field.up('fieldset').getComponent('mirror_cdi_name_e');
										if(Ext.isEmpty(newValue)){
											displayfield.setValue('');
//											field.focus(false);
											updateField(field);
											return;
										}else{
											var record;
											if(Ext.isArray(records)){
												record = records[0];
											}else{
												record = records;
											}
											if(Ext.isEmpty(record)){
												displayfield.setValue('');
											}else{
												displayfield.setValue(record.get('cdi_name_e'));
											}
											field.validate();
//											field.focus(false);
											updateField(field);
										}
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
								disabled: mv_frozen,
								width: 60,
								xtype: 'button',
								text: 'Mirror ID',
								listeners: {
									click: function(b,e,eOpts){

										var basicForm = b.up('form').getForm();
										var field = basicForm.findField('cdi_name_e');
										if(Ext.isEmpty(field)) return;
										var value = field.getValue();
										if(Ext.isEmpty(value)) return;
										var cdi_name_e = '';
										if(value.match(/left/i)){
											cdi_name_e = value.replace(/left/i,'right');
										}else if(value.match(/right/i)){
											cdi_name_e = value.replace(/right/i,'left');
										}
										if(Ext.isEmpty(cdi_name_e)){
											Ext.Msg.alert(b.text, 'None Data');
											return;
										}

										b.setDisabled(true);
										b.up('fieldset').setLoading(true);

										var store = Ext.data.StoreManager.lookup('fmaSearchStore');
										store.clearFilter(true);
										store.load({
											params: {
												cdi_name_e: cdi_name_e
											},
											callback: function(records,operation,success){
												b.setDisabled(false);
												b.up('fieldset').setLoading(false);
												if(!success || Ext.isEmpty(records)){
													Ext.Msg.alert(b.text, 'None Data');
													return;
												}
												var record = records[0];
												var basicForm = b.up('form').getForm();
												Ext.each(['cdi_name','cdi_name_e'],function(name,index,arr){
													var field = basicForm.findField('mirror_'+name);
													if(Ext.isEmpty(field)) return true;
													field.suspendEvents(false);
													field.setValue(record.get(name));
													field.resumeEvents();
													if(field.clearInvalid) field.clearInvalid();
													updateField(field);
												});
											}
										});
									}
								}
							},{
								disabled: mv_frozen,
								width: 100,
								xtype: 'button',
								iconCls: 'pallet_find',
								text: 'FMA Search',
								listeners: {
									click: function(b,e,eOpts){
										self.openFMASearch({
											title: b.text,
											iconCls: b.iconCls,
											query: Ext.String.trim(b.prev('textfield').getValue()),
											callback: function(record){
												if(Ext.isEmpty(record)) return;
												var basicForm = b.up('form').getForm();
												Ext.each(['cdi_name','cdi_name_e'],function(name,index,arr){
													var field = basicForm.findField('mirror_'+name);
													if(Ext.isEmpty(field)) return true;
													field.suspendEvents(false);
													field.setValue(record.get(name));
													field.resumeEvents();
													if(field.clearInvalid) field.clearInvalid();
													updateField(field);
												});
											}
										});
									}
								}
							},{
								disabled: mv_frozen,
								width: 22,
								xtype: 'button',
								iconCls: 'pallet_delete',
								listeners: {
									click : function(b,e,eOpts){
										var field = b.up('fieldcontainer').getComponent('mirror_cdi_name');
										if(field.getValue()){
											field.setValue('');
											field.clearInvalid();
											updateField(field);
										}
										var displayfield = field.up('fieldset').getComponent('mirror_cdi_name_e');
										displayfield.setValue('');
										field.focus(false);
									}
								}
							}]
						},{
							xtype: 'displayfield',
							fieldLabel: AgLang.cdi_name_e,
							name: 'mirror_cdi_name_e',
							itemId: 'mirror_cdi_name_e',
							value: record.data.mirror_cdi_name_e,
							listeners: {
								change: function(field,newValue,oldValue,eOpts){
									updateField(field);
								}
							}
						}]
					}]
				}]
			}],
			listeners: {
				destroy: function(){
//					console.log('destroy()');
//					if(aCB) (aCB)();
				},
				hide: function(){
//					console.log('hide()');

				},
				show: function( comp ){
					var fmaAllStore = Ext.data.StoreManager.lookup('fmaAllStore');
					if(fmaAllStore && fmaAllStore.isLoading()){
						fmaAllStore.on({
							load: function(){
								comp.setLoading(false);
							},
							single: true
						});
						comp.setLoading(true);
					}
				}
			}
		}).show();
	};

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
//				features: [{ftype: 'grouping'}],
//				autoScroll: true,
				columns: [
					{text: AgLang.cdi_name,   dataIndex: 'cdi_name',    width: 80, minWidth: 80, hidden: false, hideable: false, draggable: false, xtype: 'agcolumncdiname'},
					{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e',  flex: 1,   minWidth: 80, hidden: false, hideable: false, draggable: false, xtype: 'agcolumncdinamee'},
					{text: 'mapped obj',      dataIndex: 'mapped_obj',  width: 70, minWidth: 70, hidden: false, hideable: false, draggable: false, xtype: 'agnumbercolumn', format: '0'},
					{text: '&#160;',          dataIndex: 'cdi_name',    width: 40, minWidth: 40, hidden: false, hideable: false, draggable: false, xtype: 'templatecolumn', align: 'center', tpl: '<a href="#" onclick="return false;">show</a>', sortable: false},
				],
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'bottom',
					items: [
						'->','-',{
							xtype: 'button',
							iconCls: 'x-tbar-loading',
							listeners: {
								click: function(b){
//									var gridpanel = b.up('gridpanel');
//									var store = gridpanel.getStore();
									var store = Ext.data.StoreManager.lookup('mapListStore');
									store.loadPage(1);
								}
							}
						}
					]
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
										record.set('grouppath',data.grouppath);
										record.set('path',data.path);
										record.endEdit();
										record.commit();
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
//												console.log('afterrender:uxiframe(): '+uxiframe.id);
											},
											beforedestroy: function(uxiframe,eOpts){
//												console.log('beforedestroy:uxiframe(): '+uxiframe.id);
											},
											load: function(uxiframe,eOpts){
//												console.log('load:uxiframe(): '+uxiframe.id);
											}
										}
									},{
										region: 'south',
										height: 150,
										minHeight: 150,
										split: true,
										xtype: 'gridpanel',
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
										plugins: [self.getCellEditing(),self.getBufferedRenderer()],
										columns: [
											{text: AgLang.use,        dataIndex: 'cm_use',       width: 30, minWidth: 30, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agselectedcheckcolumn'},
											{text: AgLang.art_id,     dataIndex: 'art_id',       width: 60, minWidth: 60, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcolumn'},
											{text: AgLang.cdi_name,   dataIndex: 'cdi_name',     width: 80, minWidth: 80, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcolumncdiname'},
											{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e',   flex: 2,   minWidth: 80, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcolumncdinamee'},
											{text: AgLang.file_name,  dataIndex: 'art_filename', flex :2,   minWidth: 80, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcolumn'},
											{text: 'Group',           dataIndex: 'artg_name',    flex :1,   minWidth: 80, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcolumn'},
											{text: 'Color',           dataIndex: 'color',        width: 40, minWidth: 40, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcolorcolumn'},
											{text: 'Opacity',         dataIndex: 'opacity',      width: 44, minWidth: 44, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agopacitycolumn'},
											{text: 'Hide',            dataIndex: 'remove',       width: 40, minWidth: 40, hidden: false, hideable: false, sortable: false, draggable: false, xtype: 'agcheckcolumn'},
										],
										viewConfig: {
											stripeRows: true,
											enableTextSelection: false,
										},
										selModel: {
											mode: 'MULTI'
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
												listeners: {
													change: function( combobox, newValue, oldValue, eOpts ){
//														console.log("combobox:change()");
//														console.log(newValue);
//														console.log(combobox.getValue());
														Ext.getCmp('ag-conflict-objs-window-add-button').setDisabled(true);
													},
													select: function( combobox, records, eOpts ){
//														console.log("combobox:select()");
//														console.log(records);
														Ext.getCmp('ag-conflict-objs-window-add-button').setDisabled(Ext.isEmpty(records));
													}
												}
											},{
												disabled: true,
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
												disabled: true,
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
												disabled: true,
												id: 'ag-conflict-objs-window-download-button',
												text: 'Download',
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
											var pallet_store = pallet_gridgridpanel.getStore();

											var win = b.up('window');
											var gridpanel = win.down('gridpanel');
											var store = gridpanel.getStore();
											var art_ids = [];
											var datas = [];
											var cdi_name;

											var uploadObjectAllStore = Ext.data.StoreManager.lookup('uploadObjectAllStore');
											var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
											uploadObjectAllStore.suspendEvents(false);
											uploadObjectStore.suspendEvents(false);
											try{
												store.each(function(record){
													var art_id = record.get('art_id');
													art_ids.push({art_id:art_id});

													var find_record = pallet_store.findRecord('art_id', art_id, 0, false, false, true);
//													if(Ext.isEmpty(find_record)) datas.push(record.getData());
													if(Ext.isEmpty(find_record)) datas.push(Ext.create(Ext.getClassName(pallet_store.model),record.getData()));

													Ext.each([uploadObjectAllStore,uploadObjectStore],function(find_store){
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

											uploadObjectAllStore.resumeEvents();
											uploadObjectStore.resumeEvents();
//											Ext.getCmp('upload-object-grid').getView().refresh();
											Ext.each(['upload-object-grid','pallet-grid'], function(id){
												var gridpanel = Ext.getCmp(id);
												gridpanel.getView().refresh();
											});

											if(datas.length){
//												pallet_store.loadData(datas, true);
												pallet_store.loadRecords(datas, {addRecords: true});
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

														uploadObjectAllStore.suspendEvents(false);
														uploadObjectStore.suspendEvents(false);
														try{
															Ext.each(json.datas,function(data){
																var art_id = data.art_id;
																Ext.each([pallet_store,uploadObjectAllStore,uploadObjectStore],function(find_store){
																	var startIdx = 0;
																	var find_record;
																	while(find_record = find_store.findRecord('art_id', art_id, startIdx, false, false, true)){
																		var modifiedFieldNames = [];
																		find_record.beginEdit();
																		Ext.Object.each(data,function(name,value){
																			console.log(name,value,find_record.get(name));
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
														uploadObjectAllStore.resumeEvents();
														uploadObjectStore.resumeEvents();
//														Ext.getCmp('upload-object-grid').getView().refresh();
//														Ext.getCmp('pallet-grid').getView().refresh();
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
										disabled: true,
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
//											console.log('afterrender:win(): '+win.id);
											var uxiframe = win.down('uxiframe');
											var uxiframe_dom = uxiframe.el.dom;
											var uxiframe_iframe = uxiframe.iframeEl.dom;
											uxiframe.AgRender = new AgRender({namespace: uxiframe_namespace.substring(1), hash_key: 'ag-render-uxiframe-hash', use_localstorage: true});
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
														if(Ext.isEmpty(o.object.record.data.grouppath)){
															if(record.data.path==o.object.record.data.path) return true;
														}else{
															if(
																record.data.path==o.object.record.data.path &&
																record.data.grouppath==o.object.record.data.grouppath
															) return true;
														}
													});
												}

												store.suspendEvents(false);
												store.each(function(record){
													record.set('target_record', false);
													record.commit();
												});

												if(idx>=0){
//													p.extraParams._pickIndex = idx;
													var record = store.getAt(idx);
													record.set('target_record', true);
													record.commit();
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
//														console.log('metachange:store(): ');
//														self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
													},
													update: function( store, record, operation, eOpts ){
//														console.log('update:store(): '+operation);
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

															var versionCombobox = Ext.getCmp('version-combobox');
															var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
															var mv_frozen = r.data.mv_frozen;

															Ext.getCmp('ag-conflict-objs-window-save-button').setDisabled(mv_frozen || count===0);
															self.setHashTask.delay(0,null,null,[uxiframe.AgRender,store,null,null]);
														}
													}
												});
											});
											store.loadData(record.data.objs);
										},
										show: function(win,eOpts){
//											console.log('show:win(): '+win.id);
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
//											console.log('hide:win(): '+win.id);

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
/*
					Ext.getCmp('version-combobox').on({
						change: function(combobox, newValue, oldValue, eOpts){
							console.log('change()');
						},
						select: function(combobox, records, eOpts){
							console.log('select()');
						}
					});
*/
				},
				beforedestroy: function(panel, eOpt){
//					console.log('beforedestroy()');
				}
			}
		});
//		};
		return conflict_panel;
	};

	var changeUploadFolder = function(upload_folder_record,upload_group_records){
		var prev_artf_id = upload_group_records[0].get('artf_id');
		var artf_pid = upload_folder_record.get('artf_id');
		var artf_pname = upload_folder_record.get('artf_name') || '/';

		var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
		uploadGroupStore.suspendEvents(false);
		try{
			Ext.each(upload_group_records,function(r){
				r.beginEdit();
				r.set('artf_id',artf_pid);
				r.set('artf_name',artf_pname);
				r.endEdit(false,['artf_id','artf_name']);
			});
		}catch(e){
			console.error(e);
		}
		uploadGroupStore.resumeEvents();

		uploadGroupStore.sync({
			success: function(batch,options){
				uploadGroupStore._setFilters();

				var groupingCount = uploadGroupStore._getGroupingCount('artf_id');
				if(Ext.isObject(groupingCount)){
					var uploadFolderTreePanelStore = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
					uploadFolderTreePanelStore.suspendAutoSync();
					try{
						var rootNode = uploadFolderTreePanelStore.getRootNode();
						if(Ext.isNumber(prev_artf_id)){
							if(Ext.isEmpty(groupingCount[prev_artf_id])){
								var node = rootNode;
								if(prev_artf_id){
									node = rootNode.findChild( 'artf_id', prev_artf_id, true );
								}
								if(node){
									node.set('artg_count',0)
									node.commit(false,['artg_count']);
								}
							}
						}

						Ext.Object.each(groupingCount, function(key, value, myself) {
							var node = rootNode;
							key-=0;
							if(key){
								node = rootNode.findChild( 'artf_id', key, true );
							}
							if(!node) return true;
							node.set('artg_count',value);
							node.commit(false,['artg_count']);
						});
					}catch(e){
						console.error(e);
					}
					uploadFolderTreePanelStore.resumeAutoSync();
				}

			},
			failure: function(batch,options){
				Ext.Msg.show({
					title: 'Drag',
					msg: this.reader.rawData.msg,
					iconCls: b.iconCls,
					icon: Ext.Msg.ERROR,
					buttons: Ext.Msg.OK
				});
			}
		});

	};

	var upload_folder_tree = Ext.create('Ext.tree.Panel', {
		title: self.TITLE_UPLOAD_FOLDER,
		id: 'upload-folder-tree',
//		flex: 1,
		region: 'north',
		height: 150,
		minHeight: 150,
		split: true,
		store: 'uploadFolderTreePanelStore',

		hideHeaders: true,
		columns: [{
			xtype: 'treecolumn',
			text: AgLang.cdi_name_e,
			flex: 1,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			dataIndex: 'text'
		},{
			xtyle: 'agnumbercolumn',
			width: 40,
			hidden: false,
			hideable: false,
			sortable: false,
			resizable: false,
			format: '0',
			align: 'right',
			dataIndex: 'artg_count'
		}],
		viewConfig: {
			plugins: {
				ptype: 'treeviewdragdrop',
				appendOnly: true,
				containerScroll: true,
				ddGroup: 'dd-upload_folder_tree'
			},
			listeners: {
				beforedrop: function( node, data, overModel, dropPosition, dropHandlers, eOpts ){
//					console.log('beforedrop()');
					var p = overModel.getProxy ? overModel.getProxy() : overModel.store.getProxy();
					p.extraParams = p.extraParams || {};
					delete p.extraParams.artf_pid;

					if(data.records[0] && Ext.getClassName(data.records[0])=='EXTENSIONPARTS'){
//						console.log('beforedrop()');
//						console.log(data.records[0].$className);
						dropHandlers.wait = true;
						Ext.defer(function(){
							dropHandlers.cancelDrop();
							changeUploadFolder(overModel,data.records);
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
//					console.log('drop()');
//					console.log(node);
//					console.log(data);
//					console.log(overModel);
//					console.log(dropPosition);
//					console.log(eOpts);
//					var p = overModel.store.getProxy();
//					p.extraParams = p.extraParams || {};
//					delete p.extraParams.artf_pid;

					var artf_pid;
					if(dropPosition=='append'){
						artf_pid = overModel.get('artf_id');
					}else{
						artf_pid = overModel.get('artf_pid');
					}
					var record;
					Ext.each(data.records,function(r){
						r.beginEdit();
						r.set('artf_pid',artf_pid);
						r.endEdit(false,['artf_pid']);
						record = r;
					});
//					console.log('drop()');

					var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
					if(store.autoSync) return;

//					return;

					Ext.defer(function(){
						var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
						if(store.isLoading()){
							store.on('load',{
								fn: function(){
									store.sync({
										success: function(batch,options){
											console.log('success()');
											console.log(record.getPath('artf_name'));
											upload_folder_tree.selectPath(record.getPath('artf_name'),'artf_name');
										},
										failure: function(batch,options){
											Ext.Msg.show({
												title: 'Drag',
												msg: this.reader.rawData.msg,
												iconCls: 'tfolder',
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
										}
									});
								},
								buffer: 250,
								single: true
							});
						}else{
							store.sync({
								success: function(batch,options){
//									console.log('success()');
//									console.log(record.getPath('artf_name'));
//									upload_folder_tree.selectPath(record.getPath('artf_name'),'artf_name');
								},
								failure: function(batch,options){
									Ext.Msg.show({
										title: 'Drag',
										msg: this.reader.rawData.msg,
										iconCls: 'tfolder',
										icon: Ext.Msg.ERROR,
										buttons: Ext.Msg.OK
									});
								}
							});
						}
					},250);
				},
				afterrender: function( treeview, eOpts ){
					if(!self.USE_OBJ_UPLOAD) return;
//					console.log('afterrender()');
//					console.log(treeview.getNodes());
//					return;
					var el = treeview.getEl();
					el.on({
						dragenter: function(event){
							self.fileDragenter(event);
//							console.log(Ext.get(event.currentTarget));
//							console.log(treeview.getNode(treeview.panel.store.getRootNode()));

							var tr = Ext.get(event.target).up('tr.x-grid-data-row',el) || Ext.get(treeview.getNode(treeview.panel.store.getRootNode()));
/*
							tr.highlight(null,{duration:0, stopAnimation: true});

							if(treeview.__animFly) treeview.__animFly.stopAnimation();
							var fly = tr.scrollChildFly.attach(tr.dom);
							fly.stopAnimation();
							fly.highlight(null,{duration:0, stopAnimation: true});
							treeview.__animFly = fly;
*/
							treeview.panel.getSelectionModel().select(treeview.getRecord(tr));
							return false;
						},
						dragover: function(event){
							self.fileDragover(event);
							return false;
						},
						drop: function(event){

//							if(treeview.__animFly) treeview.__animFly.stopAnimation();
//							delete treeview.__animFly;

//							self.fileDropCancel(event);
							var tr = Ext.get(event.target).up('tr.x-grid-data-row',el) || Ext.get(treeview.getNode(treeview.panel.store.getRootNode()));
//							console.log(tr);
//							console.log(treeview.getRecord(tr));

							self.fileDrop(event,{
								callback: function(files,folders){
//									console.log(files);
//									console.log(folders);

									var rec = treeview.panel.getSelectionModel().getSelection()[0] || treeview.panel.store.getRootNode();

									var fd = new FormData();
									fd.append('md_id',DEF_MODEL_ID);
									fd.append('prefix_id',DEF_PREFIX_ID);
									fd.append('artf_id',rec.get('artf_id'));
									if(files.length==1){
										fd.append('file',files[0]);
									}else{
										Ext.each(files,function(file,i){
											fd.append('file'+(i+1),file);
										});
									}

									var _upload_progress = Ext.Msg.show({
										closable : false,
										modal    : true,
										msg      : 'Upload...',
										progress : true,
										title    : 'Upload...'
									});

									$.ajax({
										url: 'upload-object.cgi',
										type: "POST",
										data: fd,
										processData: false,
										contentType: false,
										dataType: 'json',
										xhr : function(){
											var XHR = $.ajaxSettings.xhr();
											if(XHR.upload){
												XHR.upload.addEventListener('progress',function(e){
//													console.log(e) ;
													var value = e.loaded/e.total;
//													var progre = parseInt(e.loaded/e.total*10000)/100 ;
//													console.log(progre+"%") ;
													_upload_progress.updateProgress(value,Math.floor(value*100)+'%','Upload...');
												});
											}
											return XHR;
										}
									})
									.done(function( data, textStatus, jqXHR ){
										_upload_progress.close();
//										console.log(data);
//										console.log(textStatus);
//										console.log(jqXHR);

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


//										var url = 'upload-object.cgi?sessionID='+window.encodeURIComponent(data.sessionID);
										var url = 'upload-object.cgi?'+Ext.Object.toQueryString({sessionID: data.sessionID, mtime: data.mtime, mfmt: data.mfmt});

										var cb = function(json,callback){
											if(Ext.isEmpty(json)) return;
//											console.log(json);

											if(Ext.isObject(json) && Ext.isObject(json.progress) && Ext.isNumber(json.progress.value)){
												var value = json.progress.value;
												if(Ext.isString(value)) value = parseFloat(value);
												_progress.updateProgress(value,Math.floor(value*100)+'%',json.progress.msg);
											}
//											_progress.center();
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
											if(callback) (callback)(close_progress_msg? true : false);
											if(close_progress_msg){
												_progress.close();
//												Ext.Msg.alert(close_progress_title, close_progress_msg);
												Ext.Msg.show({
													title: close_progress_title,
													msg: close_progress_msg,
													buttons: Ext.Msg.OK,
													icon: close_progress_icon
												});
												if(json.file || json.files){
													Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
														callback: function(records, operation, success) {
															var selected_art_ids = self.getSelectedArtIds();
															var uploadObjectStore = Ext.data.StoreManager.lookup('uploadObjectStore');
															uploadObjectStore.setLoadUploadObjectAllStoreFlag();
															uploadObjectStore.loadPage(1,{
																params: { selected_art_ids: Ext.encode(selected_art_ids) },
																sorters: uploadObjectStore.getUploadObjectLastSorters()
															});
														}
													});
												}
//												if(self._uploadWin) self._uploadWin.hide();
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
			mode: 'SINGLE',
			listeners: {
				selectionchange : function(selModel,selected,eOpts){
					var treepanel = selModel.view.panel;
					var toolbar = treepanel.getDockedItems('toolbar[dock="top"]')[0];

					if(selModel.getCount()>0 && selected[0].getId()!='root'){
						toolbar.getComponent('delete').enable();
						toolbar.getComponent('rename').enable();
					}else{
						toolbar.getComponent('delete').disable();
						toolbar.getComponent('rename').disable();
					}
				}
			}
		},
		dockedItems: [{
			dock: 'top',
			xtype: 'toolbar',
			items: [
				Ext.Object.merge({},update_object_button,{hidden:!self.USE_OBJ_UPLOAD}),
				{
					hidden: !self.USE_OBJ_UPLOAD,
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
									modal: true,
									resizable: true,
									width: 220,
									minWidth: 220,
									height: 120,
									minHeight: 120,
									layout: 'fit',
									border: false,
									autoShow: true,
									items:[{
										xtype: 'form',
										bodyPadding: 5,
										defaults: {
											hideLabel: false,
											labelAlign: 'right',
											labelStyle: 'font-weight:bold;',
											labelWidth: 40
										},
										items: [{
											xtype: 'combobox',
											name: 'md_id',
											itemId: 'md_id',
											fieldLabel: AgLang.model,
											store: 'modelStore',
											queryMode: 'local',
											displayField: 'display',
											valueField: 'md_id',
											value: DEF_MODEL_ID,
											editable: false
										},{
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
										}]
									}],
									buttons: [{
										disabled: false,
										text: 'OK',
										handler: function(b,e) {
											var win = b.up('window');
											var formPanel = win.down('form');
											DEF_MODEL_ID = formPanel.getComponent('md_id').getValue();
											DEF_PREFIX_ID = formPanel.getComponent('prefix_id').getValue();
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
				},{
					hidden: !self.USE_OBJ_UPLOAD,
					xtype: 'tbseparator'
				},{
					hidden: !self.USE_CLICK_TO_GROUOP_SELECTED,
					id: 'ag-folder-click-to-group-button',
					text: 'Click to Group SELECTED',
					enableToggle: true,
					pressed: self.USE_CLICK_TO_GROUOP_SELECTED,
					handler: function(b, e){
//						console.log(b);
					}
				},
				{
					hidden: !self.USE_CLICK_TO_GROUOP_SELECTED,
					xtype: 'tbseparator'
				},
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
							var treeCombobox = Ext.getCmp('tree-combobox');
							var treeStore = treeCombobox.getStore();
							if(treeStore.getCount()==0){
								b.setDisabled(true);
								treeStore.on({
									load: {
										fn: function(){
											b.setDisabled(false);
										},
										buffer: 100,
										single: true
									}
								});
							}else{
								b.setDisabled(false);
							}
						}
					}
				},
				{
					hidden: !self.USE_CONFLICT_LIST || self.USE_CONFLICT_LIST_TYPE == 'tab',
					xtype: 'tbseparator'
				},
				,'->','-',all_upload_parts_list_menu,'-',{ xtype: 'tbspacer', width: 16 }
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
											Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1);
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
				text: 'Add',
				iconCls: 'tfolder_add',
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							var title = b.text;
							Ext.Msg.show({
								title: title,
								msg: 'Please enter new folder name: ',
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
//											console.log('artf_pid: '+node.get('artf_id'));

											var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
											if(store.autoSync){
												var proxy = store.getProxy();
												Ext.Ajax.request({
													url: proxy.api.create,
													method: proxy.actionMethods.create,
													params: {
														datas: Ext.encode([{artf_pid: node.get('artf_id'),artf_name: artf_name}])
													},
													callback: function(options,success,response){
														var json;
														try{json = Ext.decode(response.responseText)}catch(e){};
														if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false || !Ext.isArray(json.datas) || Ext.isEmpty(json.datas)){
															if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
															Ext.Msg.show({
																title: title,
																msg: json.msg,
																buttons: Ext.Msg.OK,
																icon: Ext.Msg.ERROR
															});
															return;
														}
														Ext.each(json.datas,function(data){
															node.appendChild({
																text: data.artf_name,
																leaf: false,
																iconCls: 'tfolder',
																artf_id: data.artf_id,
																artf_pid: data.artf_pid,
																artf_name: data.artf_name,
																artf_timestamp: Ext.Date.parse(data.artf_timestamp,'timestamp'),
																artf_entry: Ext.Date.parse(data.artf_entry,'timestamp')
															}, false, true );
														});

													}
												});
											}
											else{


												node.appendChild({
													text: artf_name,
													leaf: false,
													iconCls: 'tfolder',
													artf_pid: node.get('artf_id'),
													artf_name: artf_name
												}, false, false );

	//											var store = node.store;
	//											var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
	//											if(store.autoSync) return;

	//											return;
												console.log('getNewRecords()     : '+store.getNewRecords().length);
												console.log('getModifiedRecords(): '+store.getModifiedRecords().length);
												console.log('getRemovedRecords() : '+store.getRemovedRecords().length);
												console.log('getUpdatedRecords() : '+store.getUpdatedRecords().length);

												var parentNode = node.parentNode;
												var loadTask = new Ext.util.DelayedTask(function(){
													console.log('exec DelayedTask()');
	//												parentNode.store.load({node:parentNode});
													store.load({node:parentNode});
												});
												loadTask.delay(1000);
												store.sync({
													callback: function(batch,options){
														console.log('callback()');
														store.load({node:node});
													},
													success: function(batch,options){
														console.log('success()');
														loadTask.cancel();
													},
													failure: function(batch,options){
														console.log('failure()');
														Ext.Msg.show({
															title: title,
															msg: this.reader.rawData.msg,
															iconCls: b.iconCls,
															icon: Ext.Msg.ERROR,
															buttons: Ext.Msg.OK
														});
													}
												});
											}
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
				text: 'Rename',
				iconCls: 'tfolder_rename',
				disabled: true,
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							var title = b.text;
							var old_artf_name = node.get('artf_name');
							Ext.Msg.show({
								title: title,
								msg: 'Please enter new folder name: ',
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

									var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
									uploadGroupStore.suspendEvents(true);
//									var filters = uploadGroupStore.getFilters();
									var filters = uploadGroupStore._getFilters();

									uploadGroupStore._setFilters([{
										anyMatch: false,
										caseSensitive: false,
										exactMatch: true,
										property: 'artg_delcause',
										value: null
									},{
										anyMatch: false,
										caseSensitive: false,
										exactMatch: true,
										property: 'artf_id',
										value: node.get('artf_id')
									}]);
									uploadGroupStore.each(function(r){
										r.beginEdit();
										r.set('artf_name',artf_name);
										r.endEdit(false,['artf_name']);
									});
									uploadGroupStore.resumeEvents();
									uploadGroupStore._setFilters(filters);

									var records = upload_group_grid.getSelectionModel().getSelection();
									if(records.length){
//										var artf_id = records[0].get('artf_id');
//										Ext.getCmp('uploadFolderCombo').setValue(artf_id ? artf_id : undefined);

										var artf_id = records[0].get('artf_id');
										var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
										var record = artf_id ? store.findRecord( 'artf_id', artf_id, 0, false, false, false) : store.getRoot();
										Ext.getCmp('uploadFolderCombo').setValue(record ? record.getId() : undefined);

									}

//									var store = node.store;
									var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
									store.on({
										write: {
											fn: function(){
												uploadGroupStore.sync({
													success: function(batch,options){
													},
													failure: function(batch,options){
														Ext.Msg.show({
															title: title,
															msg: this.reader.rawData.msg,
															iconCls: iconCls,
															icon: Ext.Msg.ERROR,
															buttons: Ext.Msg.OK
														});
													}
												});
											},
											single: true
										}
									});
									if(store.autoSync) return;

									store.sync({
										callback: function(batch,options){
											store.load({node:node});
										},
										failure: function(batch,options){
											Ext.Msg.show({
												title: title,
												msg: this.reader.rawData.msg,
												iconCls: b.iconCls,
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
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
				text: 'Delete',
				iconCls: 'pallet_delete',
				disabled: true,
				listeners: {
					click: function(b){
						var treepanel = b.up('treepanel');
						var selModel = treepanel ? treepanel.getSelectionModel() : null;
						var node = selModel ? selModel.getSelection()[0] : null;
						if(node){
							var title = b.text;
							var iconCls = b.iconCls;
							Ext.Msg.show({
								title: title,
								msg: '選択されているフォルダを削除してよろしいですか？',
								iconCls: iconCls,
								buttons: Ext.Msg.OKCANCEL,
								fn: function(btn){
									if(btn != 'ok') return;

									var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
									uploadGroupStore.suspendEvents(true);
//									var filters = uploadGroupStore.getFilters();
									var filters = uploadGroupStore._getFilters();

									var removeChildNodes = function(node){
										if(node.hasChildNodes()){
											node.eachChild(function(c){
												removeChildNodes(c);
											});
										}

										uploadGroupStore._setFilters([{
											anyMatch: false,
											caseSensitive: false,
											exactMatch: true,
											property: 'artg_delcause',
											value: null
										},{
											anyMatch: false,
											caseSensitive: false,
											exactMatch: true,
											property: 'artf_id',
											value: node.get('artf_id')
										}]);
										uploadGroupStore.each(function(r){
											r.beginEdit();
											r.set('artf_id',0);
											r.endEdit(false,['artf_id']);
										});

										node.remove();
									};

									var parentNode = node.parentNode;
									removeChildNodes(node);

									uploadGroupStore.resumeEvents();
									uploadGroupStore._setFilters(filters);

//									var parentNode = node.parentNode;
//									if(node.hasChildNodes()){
//										node.removeAll();
//									}
//									node.remove();

									selModel.select(parentNode);
//									return;

//									var store = parentNode.store;
									var store = Ext.data.StoreManager.lookup('uploadFolderTreePanelStore');
									store.on({
										write: {
											fn: function(){
												uploadGroupStore.sync({
													success: function(batch,options){
													},
													failure: function(batch,options){
														Ext.Msg.show({
															title: title,
															msg: this.reader.rawData.msg,
															iconCls: iconCls,
															icon: Ext.Msg.ERROR,
															buttons: Ext.Msg.OK
														});
													}
												});
											},
											single: true
										}
									});
									if(store.autoSync){
										return;
									}

									store.sync({
										callback: function(batch,options){
											store.load({node:parentNode});
										},
										failure: function(batch,options){
											Ext.Msg.show({
												title: title,
												msg: this.reader.rawData.msg,
												iconCls: iconCls,
												icon: Ext.Msg.ERROR,
												buttons: Ext.Msg.OK
											});
										}
									});
								}
							});
						}
					}
				}
			}]
		}],
		listeners: {
			beforeload: function( store, operation, eOpts ){
//				console.log('beforeload()');
//				console.log(this);
//				console.log(operation);
//				console.log(eOpts);

				var p = store.getProxy();
				p.extraParams = p.extraParams || {};
				p.extraParams.artf_pid = operation.node.get('artf_id');

			},
			load: function(/* store, node, records, successful, eOpts */){
//				console.log('load()');
//				console.log(node);
//				console.log(records);
//				console.log(successful);
//				console.log(eOpts);

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

//					var obj = {};
//					if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
//					var path = obj['selected'] || '/root';
					var path = node.getPath('artf_name');

					upload_folder_tree.getSelectionModel().deselectAll();

					upload_folder_tree.selectPath(path,'artf_name',null,function(bSuccess, oLastNode){
//						console.log('upload_folder_tree.selectPath():['+path+']:['+bSuccess+']');
						if(bSuccess){
//							console.log('selectPath CB(): '+oLastNode.get('artf_id'));
							var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
							uploadGroupStore.loadPage(1,{
								callback: function(records,operation,success){
//									console.log('uploadGroupStore.loadPage():callback():['+success+']');
									if(success){
										uploadGroupStore._setFilters([{
											anyMatch: false,
											caseSensitive: false,
											exactMatch: true,
											property: 'artg_delcause',
											value: null
										},{
											anyMatch: false,
											caseSensitive: false,
											exactMatch: true,
											property: 'artf_id',
											value: oLastNode.get('artf_id')
										}]);
									}else{
										console.warn('upload_folder_tree.loadPage():['+success+']');
									}
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
			select: {
				fn: function( selModel, record, index, eOpts ){
					var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
					var button_pressed;
					if(self.USE_CLICK_TO_GROUOP_SELECTED){
						button_pressed = Ext.getCmp('ag-folder-click-to-group-button').pressed;
					}else{
						button_pressed = false;
					}
					if(record.isRoot()) button_pressed = false;

					var _setFilters = function(){
						if(button_pressed){
							uploadGroupStore._setFilters([{
								property: 'selected',
								value: true
							}]);
							uploadGroupStore.each(function(record){
								record.beginEdit();
								record.set('selected',false);
								record.endEdit(false,['selected']);
								record.commit(false,['selected']);
							});
						}

						uploadGroupStore._setFilters([{
							anyMatch: false,
							caseSensitive: false,
							exactMatch: true,
							property: 'artg_delcause',
							value: null
						},{
							anyMatch: false,
							caseSensitive: false,
							exactMatch: true,
							property: 'artf_id',
							value: record.get('artf_id')
						}]);


						if(button_pressed){
							var filter = uploadGroupStore._getFilters();
							uploadGroupStore.each(function(record){
								record.beginEdit();
								record.set('selected',true);
								record.endEdit(false,['selected']);
								record.commit(false,['selected']);
							});
							uploadGroupStore.resumeEvents();
						}
					};

					if(uploadGroupStore.isLoading()){// || uploadGroupStore.getTotalCount()==0){
						uploadGroupStore.on('load',{
							fn: function(store, records, successful, eOpts){
								if(successful){
									_setFilters();
								}
							},
							single: true
						});
					}else{
						_setFilters();
					}

					var obj = {};
					if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
					obj['selected'] = record.getPath('artf_name');
					self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));
				},
//				buffer: 100
			},


			itemappend: function(node,newNode,index,eOpts){
//				console.log('itemappend()');
//				console.log(this.getView().getNodes());

				if(!newNode.isExpanded()){
					var obj = {};
					if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
					obj['expand'] = obj['expand'] || {};
//					obj['selected'] = obj['selected'] || {};
					var artf_id = newNode.get('artf_id');
//					obj['expand'][artf_id] = obj['expand'][artf_id] || {};
//					if(obj['expand'][artf_id][newNode.getPath('artf_name')]){// || node.internalId=='root'){
					if(obj['expand'][artf_id]){// || node.internalId=='root'){
						newNode.expand();
					}
				}
			},
			itemcollapse: function(node,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['expand'] = obj['expand'] || {};
				var artf_id = node.get('artf_id');
//				obj['expand'][artf_id] = obj['expand'][artf_id] || {};
//				delete obj['expand'][artf_id][node.getPath('artf_name')];
				delete obj['expand'][artf_id];
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));

				Ext.defer(function(){
					node.collapseChildren(true);
				},100);
			},
			itemexpand: function(node,eOpts){
				var obj = {};
				if(self.AgLocalStorage.exists(self.DEF_LOCALDB_FOLDER_INFO)) obj = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_FOLDER_INFO));
				obj['expand'] = obj['expand'] || {};
				var artf_id = node.get('artf_id');
//				obj['expand'][artf_id] = obj['expand'][artf_id] || {};
//				obj['expand'][artf_id][node.getPath('artf_name')] = true;
				obj['expand'][artf_id] = true;
				self.AgLocalStorage.save(self.DEF_LOCALDB_FOLDER_INFO,Ext.encode(obj));
			},
/*
				beforerender: function( treepanel, eOpts ){
					console.log('beforerender()');
					console.log(treepanel.getView().getNodes());
				},
				render: function( treepanel, eOpts ){
					console.log('render()');
					console.log(treepanel.getView().getNodes());
				},
				beforeshow: function( treepanel, eOpts ){
					console.log('beforeshow()');
					console.log(treepanel.getView().getNodes());
				},
				show: function( treepanel, eOpts ){
					console.log('show()');
					console.log(treepanel.getView().getNodes());
				},
*/
			itemcontextmenu: function(treepanel, record, item, index, e, eOpts){
				e.stopEvent();
				var xy = e.getXY();
				xy[0] += 2;
				xy[1] += 2;
				self.contextMenu.upload_folder.showAt(xy);
			}
		}
	});



/*
	var upload_panel = Ext.create('Ext.panel.Panel',{
		id: 'upload-panel',
		layout: 'border',
		title: 'Upload Parts List',
		border: false,
		items:[upload_group_grid,upload_object_grid],
		dockedItems: [{
			hidden: true,
			dock: 'top',
			xtype: 'toolbar',
			items: {
				width: 60,
				fieldLabel: AgLang.filter,
				labelWidth: 30,
				xtype: 'searchfield',
				selectOnFocus: true,
				store: 'uploadGroupStore',
				listeners: {
					beforerender: function(searchfield, eOpt){
					},
					afterrender: function(searchfield, eOpt){
						searchfield.inputEl.set({autocomplete: 'on'});
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
		}]
	});
*/
	var upload_panel = Ext.create('Ext.panel.Panel',{
		id: 'upload-panel',
		layout: 'border',
		title: 'Upload Parts List',
		border: false,
		items:[upload_folder_tree,upload_group_grid,upload_object_grid]
	});

	var pick_panel = Ext.create('Ext.ag.GridPanel',{
		disabled: true,
		id: 'pick-panel',
		title: 'Pick',
		iconCls: 'tab_pick',
		store: 'pickStore',
		columns: [
			{text: '&#160;',             dataIndex: 'selected', xtype: 'agselectedcheckcolumn', width: 30, hidden: false, hideable: false, sortable: false },
			{text: 'Name',               dataIndex: 'name',     flex: 1.5, minWidth: 80, hidden: false, hideable: false,sortable:  false },
			{text: AgLang.group_version, dataIndex: 'group',    flex: 1,   minWidth: 80, hidden: false, hideable: false, sortable: false },
		],
		plugins: [self.getCellEditing(),self.getBufferedRenderer()],
		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: true,
//			plugins: {
//				ptype: 'gridviewdragdrop',
//				dragText: 'Drag and drop to reorganize'
//			}
		},
		selType: 'rowmodel',
		selModel: {
			mode: 'SINGLE',
		},
		listeners: {
			render: function(grid,eOpts){
//				grid.getView().on({
//					beforeitemkeydown: function(view, record, item, index, e, eOpts){
//						return false;
//					}
//				});
			}
		},
		dockedItems: [{
			id: 'pick-top-toolbar',
			xtype: 'toolbar',
			dock: 'top',
			items:[{
				id: 'pick-page-first-btn',
				iconCls: 'x-tbar-page-first',
				listeners: {
					click : function(button,e,eOpts){
						var pickPageCombo = Ext.getCmp('pick-page-combobox');
						pickPageCombo.setValue(1);
					}
				}
			},{
				id: 'pick-page-prev-btn',
				iconCls: 'x-tbar-page-prev',
				listeners: {
					click : function(button,e,eOpts){
						var pickPageCombo = Ext.getCmp('pick-page-combobox');
						pickPageCombo.setValue(pickPageCombo.getValue()-1);
					}
				}
			},'-',{
				id: 'pick-page-combobox',
				fieldLabel: 'Page',
				labelSeparator: '',
				labelWidth: 28,
				width: 74,
				xtype: 'combobox',
				editable: false,
				matchFieldWidth: false,
				listConfig: {
					minWidth: 42,
					width: 42
				},
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
//				value: 0,
				store: 'pickPageStore',
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
//						console.log("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
						var store = field.getStore();
						var count = store.getCount();
						var firstBtn = Ext.getCmp('pick-page-first-btn');
						var prevBtn = Ext.getCmp('pick-page-prev-btn');
						var nextBtn = Ext.getCmp('pick-page-next-btn');
						var lastBtn = Ext.getCmp('pick-page-last-btn');
						if(newValue<=1){
							if(firstBtn) firstBtn.setDisabled(true);
							if(prevBtn) prevBtn.setDisabled(true);
						}else{
							if(firstBtn) firstBtn.setDisabled(count<=1? true : false);
							if(prevBtn) prevBtn.setDisabled(count<=1? true : false);
						}
						if(newValue>=count){
							if(nextBtn) nextBtn.setDisabled(true);
							if(lastBtn) lastBtn.setDisabled(true);
						}else{
							if(nextBtn) nextBtn.setDisabled(count<=1? true : false);
							if(lastBtn) lastBtn.setDisabled(count<=1? true : false);
						}
						var pickStore = Ext.data.StoreManager.lookup('pickStore');
						pickStore.loadData(newValue>=1 ? field.findRecordByValue(newValue).get('records') : []);
					},
					disable: function(field, eOpts){
//						console.log("disable():["+field.id+"]");
						var firstBtn = Ext.getCmp('pick-page-first-btn');
						var prevBtn = Ext.getCmp('pick-page-prev-btn');
						var nextBtn = Ext.getCmp('pick-page-next-btn');
						var lastBtn = Ext.getCmp('pick-page-last-btn');
						if(firstBtn) firstBtn.setDisabled(true);
						if(prevBtn) prevBtn.setDisabled(true);
						if(nextBtn) nextBtn.setDisabled(true);
						if(lastBtn) lastBtn.setDisabled(true);
					},
					enable: function(field, eOpts){
//						console.log("enable():["+field.id+"]");
						var count = field.getStore().getCount();
						var firstBtn = Ext.getCmp('pick-page-first-btn');
						var prevBtn = Ext.getCmp('pick-page-prev-btn');
						var nextBtn = Ext.getCmp('pick-page-next-btn');
						var lastBtn = Ext.getCmp('pick-page-last-btn');

						if(firstBtn) firstBtn.setDisabled(true);
						if(prevBtn) prevBtn.setDisabled(true);
						if(nextBtn) nextBtn.setDisabled(count<=1? true : false);
						if(lastBtn) lastBtn.setDisabled(count<=1? true : false);

					},
					render: function(field, eOpts){
//						console.log("render():["+field.id+"]");
						var store = field.getStore();
						if(store.getCount()==0) store.loadData([]);
					}
				}
			},'-',{
				id: 'pick-page-next-btn',
				iconCls: 'x-tbar-page-next',
				listeners: {
					click : function(button,e,eOpts){
						var pickPageCombo = Ext.getCmp('pick-page-combobox');
						pickPageCombo.setValue(pickPageCombo.getValue()+1);
					}
				}
			},{
				id: 'pick-page-last-btn',
				iconCls: 'x-tbar-page-last',
				listeners: {
					click : function(button,e,eOpts){
						var pickPageCombo = Ext.getCmp('pick-page-combobox');
						pickPageCombo.setValue(pickPageCombo.getStore().getCount());
					}
				}
			},'-']
		}]
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
				labelAlign: 'right',
//				labelWidth: 64,
//				labelWidth: 70,
				labelWidth: 120,
				labelStyle: 'font-weight:bold;'
			},
			items: [{
				xtype: 'radiogroup',
				fieldLabel: 'Parts Type',
				vertical: false,
				width: 350,
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
				hidden: true,
				disabled: true,
				xtype: 'fieldset',
				title: '検索条件',
				collapsible: false,
				defaultType: 'fieldcontainer',
				defaults: {
					defaultType: 'checkboxfield',
					layout: 'hbox',
					labelAlign: 'right',
					labelWidth: 46
				},
				layout: 'vbox',
				items :[{
					fieldLabel: AgLang.version,
					listeners: {
						afterrender: function(comp,eOpts){
							var field = Ext.getCmp('version-combobox');
							if(Ext.isEmpty(field)) return;
							var store_load = function(store,records,successful,eOpts){
								var item_width = 50;
								var item_name = 'version';
								comp.add({
									xtype: 'checkboxfield',
									width: item_width,
									name: item_name+'_all',
									boxLabel: '全て',
									inputValue: null,
									listeners: {
										change: function(checkbox,newValue,oldValue,eOpts){
											if(newValue){
												var n = checkbox.nextSibling('checkboxfield');
												while(n){
													n.setValue(newValue);
													n = n.nextSibling('checkboxfield');
												}
											}
											Ext.getCmp('pick-search-conditions-button').setDisabled(false);
										}
									}
								});
								var value = field.getValue();
								Ext.each(records,function(r,i,a){
									comp.add({
										xtype: 'checkboxfield',
										width: item_width,
										name: item_name,
										boxLabel: r.get('display'),
										inputValue: r.get('value'),
										checked: value===r.get('value'),
										listeners: {
											change: function(checkbox,newValue,oldValue,eOpts){
												if(!newValue){
													var n = checkbox.up('fieldcontainer').child('checkboxfield');
													if(n) n.setValue(newValue);
												}
												Ext.getCmp('pick-search-conditions-button').setDisabled(false);
											}
										}
									});
								});
							};
							var store = field.getStore();
							if(store.getCount()){
								store_load(store,store.getRange(),true,{});
							}else{
								store.on('load',store_load,self,{delay:100});
							}
						}
					}
				}, {
					fieldLabel: AgLang.tree,
					listeners: {
						afterrender: function(comp,eOpts){
							var field = Ext.getCmp('tree-combobox');
							if(Ext.isEmpty(field)) return;
							var store_load = function(store,records,successful,eOpts){
								var item_width = 110;
								var item_name = 'tree';
								comp.add({
									xtype: 'checkboxfield',
									width: 50,
									name: item_name+'_all',
									boxLabel: '全て',
									inputValue: null,
									listeners: {
										change: function(checkbox,newValue,oldValue,eOpts){
											if(newValue){
												var n = checkbox.nextSibling('checkboxfield');
												while(n){
													n.setValue(newValue);
													n = n.nextSibling('checkboxfield');
												}
											}
											Ext.getCmp('pick-search-conditions-button').setDisabled(false);
										}
									}
								});
								var value = field.getValue();
								Ext.each(records,function(r,i,a){
									comp.add({
										xtype: 'checkboxfield',
										width: item_width,
										name: item_name,
										boxLabel: r.get('display'),
										inputValue: r.get('value'),
										checked: value===r.get('value'),
										listeners: {
											change: function(checkbox,newValue,oldValue,eOpts){
												if(!newValue){
													var n = checkbox.up('fieldcontainer').child('checkboxfield');
													if(n) n.setValue(newValue);
												}
												Ext.getCmp('pick-search-conditions-button').setDisabled(false);
											}
										}
									});
								});
							};
							var store = field.getStore();
							if(store.getCount()){
								store_load(store,store.getRange(),true,{});
							}else{
								store.on('load',store_load,self,{delay:100});
							}
						}
					}
				}]
			},{
				xtype: 'fieldcontainer',
				fieldLabel: 'Pick',
				itemId: 'pick',
				layout: {
					type: 'hbox',
					align: 'top',
					pack: 'start',
					defaultMargins: {top: 0, right: 4, bottom: 0, left: 8}
				},
				defaultType: 'displayfield',
				defaults: {
					labelWidth: 12
				},
				items:[{
					fieldLabel: AgLang.art_id,
//					labelWidth: 104,
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

									var pickSearchAllStore = Ext.data.StoreManager.lookup('pickSearchAllStore');

									var p = pickSearchAllStore.getProxy();
									p.extraParams = p.extraParams || {};
									delete p.extraParams.conditions;
/*
									var set_version_info = function(value){
										var field = Ext.getCmp('version-combobox');
										var record = field.findRecordByValue(value);
										return {
											md_id : record.get('md_id'),
											mv_id : record.get('mv_id'),
											mr_id : record.get('mr_id'),
											ci_id : record.get('ci_id'),
											cb_id : record.get('cb_id')
										};
									};
									var set_tree_info = function(value){
										var field = Ext.getCmp('tree-combobox');
										var record = field.findRecordByValue(value);
										return {
//											ci_id : record.get('ci_id'),
//											cb_id : record.get('cb_id'),
											bul_id : record.get('bul_id')
										};
									};
*/
									var values = form.getValues(false,false,false,false);
		/*
									if(values.parts_map){
										if(Ext.isArray(values.version)){
											Ext.each(values.version,function(v,i,a){
												a[i] = set_version_info(v);
											});
										}else if(Ext.isString(values.version)){
											values.version = [set_version_info(values.version)];
										}
										if(Ext.isArray(values.tree)){
											Ext.each(values.tree,function(v,i,a){
												a[i] = set_tree_info(v);
											});
										}else if(Ext.isString(values.tree)){
											values.tree = [set_tree_info(values.tree)];
										}
										p.extraParams.conditions = Ext.encode(values);
									}
		*/

									//非表示時に現在の表示内容のパラメータを設定する
									p.extraParams.conditions = Ext.encode({
										parts_map: Ext.isEmpty(values.parts_map) ? true : values.parts_map,
//										version: set_version_info(Ext.getCmp('version-combobox').getValue()),
//										tree: set_tree_info(Ext.getCmp('tree-combobox').getValue())
									});

									var pick = formPanel.getComponent('pick');
									pick.getComponent('art_id').setValue(p.extraParams.art_id);

									var art_point = Ext.decode(p.extraParams.art_point);
									pick.getComponent('x').setValue(Ext.util.Format.number(art_point.x,self.FORMAT_FULL_FLOAT_NUMBER));
									pick.getComponent('y').setValue(Ext.util.Format.number(art_point.y,self.FORMAT_FULL_FLOAT_NUMBER));
									pick.getComponent('z').setValue(Ext.util.Format.number(art_point.z,self.FORMAT_FULL_FLOAT_NUMBER));

									var voxel_range = formPanel.getComponent('voxel_range');
									voxel_range.getComponent('value').setValue(Ext.util.Format.number(p.extraParams.voxel_range,self.FORMAT_INT_NUMBER));

									pickSearchAllStore.loadPage(1,{
										callback:function(rs, operation, success){
											var p = pickSearchAllStore.getProxy();
											var art_id = p.extraParams.art_id;

											var pickSearchStore = Ext.data.StoreManager.lookup('pickSearchStore');
											var p = pickSearchStore.getProxy();
											p.extraParams = p.extraParams || {};
											delete p.extraParams._pickIndex;

											if(!success){
												pickSearchStore.removeAll();
												pickSearchPanel.setLoading(false);
												return;
											}

											var idx = pickSearchAllStore.findBy(function(record,id){
												if(record.data.art_id==art_id) return true;
											});

											pickSearchAllStore.suspendEvents(false);
											pickSearchAllStore.each(function(record){
												record.set('target_record', false);
												record.commit();
											});
											if(idx>=0){
//												p.extraParams._pickIndex = idx;
												var record = pickSearchAllStore.getAt(idx);
												record.set('target_record', true);
												record.commit();
											}
											pickSearchAllStore.resumeEvents();

											pickSearchStore.on({
												load: function(store, records, successful, eOpts){
													pickSearchPanel.setLoading(false);

													var p = pickSearchAllStore.getProxy();
													Ext.getCmp('pick-search-more-button').setDisabled(p.extraParams.voxel_range<DEF_PICK_SEAECH_MAX_RANGE?false: true);
												},
												single: true
											});
											pickSearchStore.loadPage(1);


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
				itemId: 'voxel_range',
				layout: {
					type: 'hbox',
					align: 'top',
					pack: 'start',
					defaultMargins: {top: 0, right: 4, bottom: 0, left: 8}
				},
				defaultType: 'displayfield',
				items:[{
//					fieldLabel: 'Voxel Range',
//					labelWidth: 72,
					itemId: 'value'
				},{
					width: 70,
					xtype: 'button',
					disabled: true,
					id: 'pick-search-more-button',
					text: 'More',
					listeners: {
						click: function(b){
							b.setDisabled(true);
							var pickSearchAllStore = Ext.data.StoreManager.lookup('pickSearchAllStore');
							var p = pickSearchAllStore.getProxy();
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
			region: 'center',
			border: true,
			xtype: 'aggridpanel',
			store: 'pickSearchStore',
			stateful: true,
			stateId: 'pick-search-grid',
			columns: [
				{text: '&#160;',            dataIndex: 'selected',     stateId: 'selected',      width: 30, minWidth: 30, hidden: false, hideable: false, sortable: true, draggable: false, xtype: 'agselectedcheckcolumn'},
				{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 60, minWidth: 60, hidden: false, hideable: false},

				{text: AgLang.rep_id,       dataIndex: 'rep_id',       stateId: 'rep_id',        width: 60, minWidth: 60, hidden: false, hideable: true, xtype: 'agcolumn'},

				{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 80, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdiname' },
				{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdinamee' },

				{text: AgLang.category,     dataIndex: 'art_category', stateId: 'art_category',  flex: 1.0, minWidth: 50, hidden: false, hideable: true},
				{text: AgLang.class_name,   dataIndex: 'art_class',    stateId: 'art_class',     width: 36, minWidth: 36, hidden: false, hideable: true},
				{text: AgLang.comment,      dataIndex: 'art_comment',  stateId: 'art_comment',   flex: 2.0, minWidth: 80, hidden: false, hideable: true},
				{text: AgLang.judge,        dataIndex: 'art_judge',    stateId: 'art_judge',     flex: 1.0, minWidth: 50, hidden: false, hideable: true},

				{text: AgLang.file_name,    dataIndex: 'filename',     stateId: 'filename',      flex: 2.0, minWidth: 80, hidden: false, hideable: true},
				{text: AgLang.group,        dataIndex: 'group',        stateId: 'group',         flex: 2.0, minWidth: 50, hidden: true,  hideable: true},

				{text: AgLang.xmax,         dataIndex: 'xmax',         stateId: 'xmax',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.xmin,         dataIndex: 'xmin',         stateId: 'xmin',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.xcenter,      dataIndex: 'xcenter',      stateId: 'xcenter',       width: 59, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.ymax,         dataIndex: 'ymax',         stateId: 'ymax',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.ymin,         dataIndex: 'ymin',         stateId: 'ymin',          width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.ycenter,      dataIndex: 'ycenter',      stateId: 'ycenter',       width: 59, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.zmax,         dataIndex: 'zmax',         stateId: 'zmax',          width: 55, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.zmin,         dataIndex: 'zmin',         stateId: 'zmin',          width: 55, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.zcenter,      dataIndex: 'zcenter',      stateId: 'zcenter',       width: 59, hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
				{text: AgLang.volume,       dataIndex: 'volume',       stateId: 'volume',        width: 60, hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

				{text: AgLang.timestamp,    dataIndex: 'mtime',        stateId: 'mtime',         width: 112, hidden: true, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME},

				{
					text: AgLang.distance_voxel,
					dataIndex: 'distance_voxel',
					stateId: 'distance_voxel',
					itemId: 'distance_voxel',
					width:76,
					minWidth:76,
					hidden: false,
					hideable: true,
					sortable: false,
					align: 'right',
					xtype: 'agnumbercolumn',
					format: self.FORMAT_FULL_FLOAT_NUMBER
				}
			],
			plugins: [self.getCellEditing(),self.getBufferedRenderer()],
			viewConfig: {
				stripeRows: true,
				enableTextSelection: false,
				loadMask: true
			},
			selType: 'rowmodel',
			selModel: {
				mode: 'MULTI',
			},
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'top',
				items:['->','-',{
					itemId: 'download',
					xtype: 'button',
					text: 'Download',
					iconCls: 'pallet_download',
					disabled: true,
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
					grid.getStore().on({
						datachanged: {
							fn: function(store,options){
								var grid = this;
								self.load_pallet_store_records(store.getRange(),store,grid);
							},
							scope: grid
						},
						update: {
							fn: function(store,record,operation){
								if(operation==Ext.data.Record.EDIT){
								}else if(operation==Ext.data.Record.COMMIT){
									self.extension_parts_store_update(record,true,false);
								}
							},
							delay: 100,
							scope: grid
						}
					});
//					grid.getView().on({
//						beforeitemkeydown: function(view, record, item, index, e, eOpts){
//							return false;
//						}
//					});
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

	//選択されているrecordsを削除
	var remove_select_records_pin_store = function(queueSuspended){
		if(Ext.isEmpty(queueSuspended)) queueSuspended = true;
		var selMode = pin_panel.getSelectionModel();
		var selCount = selMode.getCount();
		if(selCount>0){
			var store = Ext.data.StoreManager.lookup('pinStore');
			store.suspendEvents(true);
			var records = selMode.getSelection().reverse();
			store.remove(records);
			store.each(function(record,i,a){
				var PinPartID = (i+1)+"";
				if(record.data.PinPartID == PinPartID) return true;
				record.beginEdit();
				record.set('PinPartID',PinPartID);
				record.commit(false);
				record.endEdit(false,['PinPartID']);
			});

			store.resumeEvents();
		}
		return selCount;
	};

	var pin_panel = Ext.create('Ext.ag.GridPanel',{
		hidden: true,
		id: 'pin-panel',
		iconCls: 'tab_pin',
		title: 'Pin',
		store: 'pinStore',
		columns: [
			{text: 'No',                 dataIndex: 'PinPartID',      width: 30, align: 'right'},
			{text: 'ID',                 dataIndex: 'PinOrganID',     width: 80, hidden: true},
			{text: 'Name',               dataIndex: 'PinOrganName',   flex: 1,   minWidth:80},
			{text:AgLang.group_version, dataIndex: 'PinOrganGroup',  flex: 1,   minWidth:80},
			{text: 'Color',              dataIndex: 'PinColor',       width: 40, xtype: 'agcolorcolumn'},
			{text: 'Description',        dataIndex: 'PinDescription', flex: 1}
		],
		viewConfig: {
			stripeRows: true,
			enableTextSelection: false,
			loadMask: true,
//			plugins: {
//				ptype: 'gridviewdragdrop',
//				dragText: 'Drag and drop to reorganize'
//			}
		},
		selType: 'rowmodel',
		selModel: {
			mode: 'MULTI',
			listeners: {
				selectionchange : function(selModel,selected,eOpts){
					Ext.getCmp('pin-delete-button').setDisabled(Ext.isEmpty(selected));
				}
			}
		},
		listeners: {
			render: function(grid,eOpts){
				grid.getView().on({
//					beforeitemkeydown: function(view, record, item, index, e, eOpts){
//						if(e.getKey()==e.DELETE || (e.ctrlKey && e.getKey()==e.A)) return true;
//						return false;
//					},
					itemkeydown : function(view,record,item,index,e,eOpts){
						if(e.getKey()==e.DELETE){
							e.stopEvent();
							remove_select_records_pin_store();
//						}else if(e.ctrlKey && e.getKey()==e.A){
//							e.stopEvent();
//							var selMode = pin_panel.getSelectionModel();
//							selMode.selectAll();
						}
					}
				});
			}
		},
		dockedItems: [{
			id: 'pin-top-toolbar',
			xtype: 'toolbar',
			dock: 'top',
			items:[{
				id: 'pin-depth-combobox',
				fieldLabel: 'Depth',
				labelWidth: 34,
				width: 80,

				xtype: 'numberfield',
				value: 1,
//				maxValue: 16,
				minValue: 1,
				keyNavEnabled: false,
				mouseWheelEnabled: false,

/*
				xtype: 'combobox',
				editable: false,
				matchFieldWidth: false,
				listConfig: {
					minWidth: 42,
					width: 42
				},
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				value: 1,
				store: Ext.create('Ext.data.ArrayStore', {
					storeId: 'pinDepathStore',
					fields: [{
						name: 'display',
						type: 'string'
					},{
						name: 'value',
						type: 'int'
					}],
					data:[
						[1,1],
						[2,2],
						[3,3],
						[4,4],
						[5,5],
						[6,6],
						[7,7],
						[8,8],
						[9,9],
						[10,10],
						[11,11],
						[12,12],
						[13,13],
						[14,14],
						[15,15],
						[16,16]
					]
				}),
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
//						console.log("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
//						self.setHashTask.delay(0);
					}
				}
*/
			},{
				text: 'Edit',
				disabled: true
			},{
				text: 'Up',
				disabled: true
			},{
				text: 'Down',
				disabled: true
			},{
				id: 'pin-delete-button',
				tooltip: 'Delete Selected',
				iconCls: 'pallet_delete',
				disabled: true,
				listeners: {
					click : function(button,e,eOpts){
						remove_select_records_pin_store();
					}
				}
			},'-',{
				text: 'Add Pin from URL',
				disabled: true
			}]
		},{
			id: 'pin-bottom-toolbar',
			xtype: 'toolbar',
			dock: 'bottom',
			items:[{
				id: 'pin-description-checkbox',
				xtype: 'checkbox',
				boxLabel: 'Description',
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
//						console.log("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
						Ext.getCmp('pin-line-combobox').setDisabled(oldValue);
						self.setHashTask.delay(0);
					}
				}
			},'-',{
				id: 'pin-line-combobox',
				xtype: 'combobox',
				disabled: true,
				editable: false,
				fieldLabel: 'Line',
				labelWidth: 23,
				matchFieldWidth: false,
				listConfig: {
					minWidth: 42,
					width: 42
				},
				width: 82,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				value: 0,
				store: Ext.create('Ext.data.ArrayStore', {
					storeId: 'pinLineStore',
					fields: [{
						name: 'display',
						type: 'string'
					},{
						name: 'value',
						type: 'int'
					}],
					data:[
						['None',0],
						['Tip', 1],
						['End', 2]
					]
				}),
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
//						console.log("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
						if(!field.isDisabled() && Ext.getCmp('pin-description-checkbox').getValue()) self.setHashTask.delay(0);
					}
				}
			},'-',{
				id: 'pin-shape-combobox',
				xtype: 'combobox',
				disabled: false,
				editable: false,
				fieldLabel: 'Shape',
				labelWidth: 34,
				matchFieldWidth: false,
				listConfig: {
					minWidth: 38,
					width: 38
				},
				width: 94,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
//				value: 'CIRCLE',
				value: 'PIN_LONG',
				store: Ext.create('Ext.data.ArrayStore', {
					storeId: 'pinShapeStore',
					fields: [{
						name: 'display',
						type: 'string'
					},{
						name: 'value',
						type: 'string'
					}],
					data:[
						['Circle','CIRCLE'],
						['Corn',  'CONE'],
						['Pin L', 'PIN_LONG'],
						['Pin M', 'PIN_MIDIUM'],
						['Pin S', 'PIN_SHORT']
					]
				}),
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
//						console.log("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
						if(!field.isDisabled()) self.setHashTask.delay(0);
					}
				}
			}]
		}]
	});
	var legend_panel = Ext.create('Ext.panel.Panel',{
		hidden: true,
		id: 'legend-panel',
		title: 'Legend',
		bodyStyle: 'padding: 5px;',
		layout: 'form',
		defaultType: 'textfield',
		defaults: {
			anchor: '100%',
			labelAlign: 'right',
			labelWidth: 45,
			selectOnFocus: true,
			validateOnChange: false
		},
		items: [{
			id: 'legend-title-textfield',
			fieldLabel: 'Title',
			listeners: {
				specialkey: function(field, e, eOpts){
					e.stopPropagation();
				},
				validitychange: function(field, isValid, eOpts){
//					console.log("validitychange():["+field.id+"]["+isValid+"]");
					if(!isValid) return;
					if(!Ext.getCmp('legend-draw-checkbox').getValue()) return;
					self.setHashTask.delay(0);
				}
			}
		},{
			id: 'legend-legend-textareafield',
			xtype: 'textareafield',
			fieldLabel: 'Legend',
			height: 80,
			listeners: {
				specialkey: function(field, e, eOpts){
					e.stopPropagation();
				},
				validitychange: function(field, isValid, eOpts){
//					console.log("validitychange():["+field.id+"]["+isValid+"]");
					if(!isValid) return;
					if(!Ext.getCmp('legend-draw-checkbox').getValue()) return;
					self.setHashTask.delay(0);
				}
			}
		},{
			id: 'legend-author-textfield',
			fieldLabel: 'Author',
			listeners: {
				specialkey: function(field, e, eOpts){
					e.stopPropagation();
				},
				validitychange: function(field, isValid, eOpts){
//					console.log("validitychange():["+field.id+"]["+isValid+"]");
					if(!isValid) return;
					if(field.getValue()==$(field.inputEl.dom).attr('defaultValue')) return;
					self.setHashTask.delay(0);
				}
			}
		}],
		dockedItems: [{
			id: 'legend-toolbar',
			xtype: 'toolbar',
			dock: 'bottom',
			items:[{
				id: 'legend-draw-checkbox',
				xtype: 'checkbox',
				boxLabel: 'Draw legend',
				listeners: {
					change: function(field, newValue, oldValue, eOpts){
//						console.log("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
						self.setHashTask.delay(0);
					}
				}
			}]
		}]
	});


	var east_tab_panel = Ext.create('Ext.tab.Panel',{
		id: 'east-tab-panel',
		region: 'center',
//		collapsible: false,
//		bodyStyle: 'background:transparent;',
		border: false,
		items: [
			upload_panel,
			pick_panel,
			pin_panel,
			legend_panel,
			pick_search_panel,
			(self.USE_CONFLICT_LIST && self.USE_CONFLICT_LIST_TYPE == 'tab') ? self.getConflictPanel() : null
		],
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

	var east_panel = Ext.create('Ext.panel.Panel',{
		id: 'east-panel',
		region: 'east',
		layout: 'border',
		collapsible: true,
		split: true,
		border: false,
		width: self.eastPanelWidth,
		items:[east_tab_panel,pallet_grid]
	});

/*
	var gridColorPicker = Ext.create('Ext.menu.ColorPicker', {
		renderTo: Ext.getBody(),
		id: 'options-grid-color',
		value: '00ff00',
		listeners: {
			select: function(picker, color, eOpts){
				self.setHashTask.delay(0);
			}
		}
	});
*/

	var render_panel = Ext.create('Ext.panel.Panel',{
		id: 'render-panel',
		region: 'center',
		autoDestroy: false,
		listeners: {
			afterrender: function(panel){
				panel.setLoading(true);
				var body = Ext.get(panel.id+'-innerCt');
				if(Ext.isEmpty(body)) body = panel.body;

				self.AgRender.open({
					dom:body.dom,
					loadMask: false
				});
			},
			render: function(panel){
//				panel.setLoading(true);
			},
			resize: function(panel,adjWidth,adjHeight,rawWidth,rawHeight){
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
				xtype: 'numberfield',
				id: 'rotateH',
				fieldLabel: 'H',
				labelWidth: 10,
				allowBlank: false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
//						readOnly: true,
//						width: 30,
				maxValue: 355,
				minValue: 0,
				selectOnFocus: false,
				step: 5,
				width: 64,
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
				xtype: 'numberfield',
				id: 'rotateV',
				fieldLabel: 'V',
				labelWidth: 10,
				allowBlank: false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
//						readOnly: true,
//						width: 30,
				maxValue: 355,
				minValue: 0,
				selectOnFocus: false,
				step: 5,
				width: 64,
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
				xtype: 'tbspacer',
				width: 5,
				hidden: true
			},{
				xtype: 'numberfield',
				id: 'zoom-value-text',
				fieldLabel: 'Zoom',
				labelWidth: 30,
				allowBlank: false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
//						readOnly: true,
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
				xtype: 'numberfield',
				id: 'camera-near',
				fieldLabel: 'Near',
				labelWidth: 28,
				allowBlank: false,
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
				xtype: 'numberfield',
				id: 'camera-far',
				fieldLabel: 'Far',
				labelWidth: 20,
				allowBlank: false,
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
				xtype: 'cycle',
				iconCls: 'plus-btn',
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
										fieldLabel: 'Max',
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
										fieldLabel: 'Min',
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

	var south_panel = {
		hidden: true,
		id: 'south-panel',
		region: 'south',     // position for region
		height: 100,
		split: true,         // enable resizing
		minSize: 75,         // defaults to 50
		maxSize: 150
	};

	var viewport_items = [];

	if(self.DEF_LAYOUT==self.DEF_LAYOUT_BORDER){
		viewport_items = [
			render_panel,
			parts_panel,
			east_panel,
			north_panel,
			south_panel
		];
	}

	if(self.DEF_LAYOUT==self.DEF_LAYOUT_WINDOW){

		var arrange_windows = function(force){
			if(Ext.isEmpty(force)) force = false;

			var size = Ext.getCmp('window-panel').getSize();
			var adjWidth = size.width;
			var adjHeight = size.height;

			if(false){//Original layout
				var left = 0;
				var top = 0;
				var width = Math.floor(adjWidth/4);
				var height = adjHeight;

				if(force || !parts_window.stateful){
					if(force && parts_window.maximized) parts_window.restore();
					parts_window.setPosition(left,top);
					parts_window.setSize(width,height);
				}else if(parts_window.stateful){
					var state = parts_window.getState();
					if(Ext.isEmpty(state.width) || Ext.isEmpty(state.height)){
						parts_window.setPosition(left,top);
						parts_window.setSize(width,height);
					}else if(state.maximized){
						parts_window.setSize(adjWidth,adjHeight);
					}
				}

				left+=width;
				width = Math.floor(adjWidth/3);

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
				height = Math.floor(adjHeight/3)*2;

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

				top = height;
				height = adjHeight-height;

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
			if(true){//New layout
				var left = 0;
				var top = 0;
				var width = Math.floor(adjWidth/4);
				var height = adjHeight;

				if(force || !parts_window.stateful){
					if(force && parts_window.maximized) parts_window.restore();
					parts_window.setPosition(left,top);
					parts_window.setSize(width,height);
				}else if(parts_window.stateful){
					var state = parts_window.getState();
					if(Ext.isEmpty(state.width) || Ext.isEmpty(state.height)){
						parts_window.setPosition(left,top);
						parts_window.setSize(width,height);
					}else if(state.maximized){
						parts_window.setSize(adjWidth,adjHeight);
					}
				}

				left+=width;
				width = Math.floor(adjWidth/3);
				height = Math.floor(adjHeight/4)*3;

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
				height = Math.floor(adjHeight/4)*3;

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

				left = Math.floor(adjWidth/4);
				width = adjWidth-left;
				top = height;
				height = adjHeight-height;

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

		};

		var render_window = Ext.create('Ext.window.Window', {
			title: 'Render',
			id: 'render-window',
			border: false,
			closable: false,
			maximizable: true,
			stateId: 'render-window',
			stateEvents: ['resize','move'],
			stateful: true,
			layout: 'fit',
			width: 100,
			height: 100,
			items: render_panel,
			listeners: {
				afterrender: function(comp){
				},
				render: function(comp){
				},
				beforestaterestore: function(stateful,state,eOpts){
				},
				beforestatesave: function(stateful,state,eOpts){
					if(!state.maximized){
						state.pos[0] -= 1;
						state.pos[1] -= (Ext.getCmp('window-panel').getPosition()[1] + 1);
					}
				},
				staterestore: function(stateful,state,eOpts){
				},
				statesave: function(stateful,state,eOpts){
				}
			}
		});

		var configLinkedUploadPartsButton = self.getConfigLinkedUploadPartsButton();
		var parts_window = Ext.create('Ext.window.Window', {
			id: 'parts-window',
			border: false,
			closable: false,
			maximizable: true,
			stateId: 'parts-window',
			stateEvents: ['resize','move'],
			stateful: true,
			layout: 'fit',
			width: 100,
			height: 100,
			items: parts_tab_panel,
			dockedItems: [{
				hidden: configLinkedUploadPartsButton.hidden,
				xtype: 'toolbar',
				dock: 'top',
				items: ['->','-',configLinkedUploadPartsButton]
			}],
			listeners: {
				afterrender: function(comp){
//					console.log('afterrender:['+comp.id+"]");
					parts_tab_panel.setBorder(0);
				},
				beforestatesave: function(stateful,state,eOpts){
					if(!state.maximized){
						state.pos[0] -= 1;
						state.pos[1] -= (Ext.getCmp('window-panel').getPosition()[1] + 1);
					}
				},
				render: function(comp){
//					console.log('render:['+comp.id+"]");
				},
				resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
//					console.log('resize:['+comp.id+"]");
				}
			}
		});

		var upload_window = Ext.create('Ext.window.Window', {
			id: 'upload-window',
			border: false,
			closable: false,
			maximizable: true,
			stateId: 'upload-window',
			stateEvents: ['resize','move'],
			stateful: true,
			layout: 'fit',
			width: 100,
			height: 100,
			items: east_tab_panel,
			listeners: {
				afterrender: function(comp){
//					console.log('afterrender:['+comp.id+"]");
				},
				beforestatesave: function(stateful,state,eOpts){
					if(!state.maximized){
						state.pos[0] -= 1;
						state.pos[1] -= (Ext.getCmp('window-panel').getPosition()[1] + 1);
					}
				},
				render: function(comp){
//					console.log('render:['+comp.id+"]");
				},
				resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
//					console.log('resize:['+comp.id+"]");
				},
				move: function(comp){
//					console.log('move:['+comp.id+"]");
				},
				beforestaterestore: function(comp){
//					console.log('beforestaterestore:['+comp.id+"]");
				},
//				beforestatesave: function(comp){
//					console.log('beforestatesave:['+comp.id+"]");
//				},
				staterestore: function(comp){
//					console.log('staterestore:['+comp.id+"]");
				},
				statesave: function(comp){
//					console.log('statesave:['+comp.id+"]");
				}
			}
		});

		var pallet_window = Ext.create('Ext.window.Window', {
			id: 'pallet-window',
			title: 'Pallet',
			border: false,
			closable: false,
			maximizable: true,
			stateId: 'pallet-window',
			stateEvents: ['resize','move'],
			stateful: true,
			layout: 'fit',
			width: 100,
			height: 100,
			items: pallet_grid,
			listeners: {
				afterrender: function(comp){
//					console.log('afterrender:['+comp.id+"]");
					pallet_grid.setBorder(0);
					pallet_grid.getHeader().hide();
				},
				beforestatesave: function(stateful,state,eOpts){
					if(!state.maximized){
						state.pos[0] -= 1;
						state.pos[1] -= (Ext.getCmp('window-panel').getPosition()[1] + 1);
					}
				},
				render: function(comp){
//					console.log('render:['+comp.id+"]");
				},
				resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
//					console.log('resize:['+comp.id+"]");
				}
			}
		});

		//layout:window
		viewport_items = [north_panel,{
			id: 'window-panel',
			region: 'center',
			bodyStyle: 'background:#aaa;',
			listeners: {
				afterrender: function(comp){
//					console.log('comp.afterrender');
					comp.add(render_window);
					comp.add(parts_window);
					comp.add(pallet_window);
					comp.add(upload_window);

					render_window.show();
					parts_window.show();
					pallet_window.show();
					upload_window.show();

//					render_panel.setBorder(0);
//					pallet_grid.setBorder(0);
//					pallet_grid.setTitle('');
				},
				render: function(comp){
//					console.log('comp.render');
				},
				resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
//					console.log('resize:['+comp.id+']['+adjWidth+']['+adjHeight+']');
					arrange_windows();
				}
			}
		}];
	}

	var viewport = Ext.create('Ext.container.Viewport', {
		id: 'main-viewport',
		layout: 'border',
		items: viewport_items,
		listeners: {
			afterrender: function(viewport){
//				console.log('viewport.afterrender');
//					init(Ext.getCmp('render-panel').body.dom);
//					animate();
//					render();
			},
			beforedestroy: function(viewport){
//				alert('viewport.beforedestroy');
//				console.log('viewport.beforedestroy');
			},
			destroy: function(viewport){
//				alert('viewport.destroy');
//				console.log('viewport.destroy');
			},
			render: function(viewport){
//				console.log('viewport.render');
			},
			resize: function(viewport,adjWidth,adjHeight,rawWidth,rawHeight){
//				console.log('viewport.resize');
			}
		}
	});
};

window.AgApp.prototype.export = function(config){
	var self = this;
	config = config || {};
	config.title = config.title || 'Export';
	config.iconCls = config.iconCls || 'pallet_download';
	config.msg = config.msg || 'Please enter download file name: ';
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
			config.filename = filename;
			self._export(Ext.apply(self.getExtraParams({current_datas:0}),config||{}));
		}
	});
};
window.AgApp.prototype._export = function(config){
	var self = this;
	window.location.href = 'get-info.cgi?'+ Ext.Object.toQueryString(config);
};

window.AgApp.prototype.downloadObjects = function(config){
	var self = this;
	config = config || {};
	config.title = config.title || 'Download';
	config.iconCls = config.iconCls || 'pallet_download';
	config.msg = config.msg || 'Please enter download file name: ';
	config.filename = config.filename || 'objects_'+Ext.util.Format.date(new Date(),'YmdHis');
	config.records = config.records || [];

	var records = [];
	Ext.each(config.records,function(r,i,a){
		if(Ext.isEmpty(r.data.artg_id) && Ext.isEmpty(r.data.art_id) && Ext.isEmpty(r.data.rep_id)) return true;
		records.push({
			artg_id: r.data.artg_id,
			art_id: r.data.art_id,
			rep_id: r.data.rep_id
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

window.AgApp.prototype.openRecalculationList = function(config){
	var self = this;

	config = config || {};
	config.title = config.title || AgLang.recalculation;
	config.iconCls = config.iconCls || 'pallet_calculator';
	config.height = config.height || 400;
	config.width = config.width || 400;
	config.minHeight = config.minHeight || 400;
	config.minWidth = config.minWidth || 400;
	config.maximizable = Ext.isEmpty(config.maximizable) ? true : config.maximizable;
	config.modal = Ext.isEmpty(config.modal) ? true : config.modal;
	config.id = config.id || 'recalculation-list-window';
	config.stateful = config.stateful || true;
	config.stateId = config.stateId || config.id;
	config.interval = config.interval || 2000;
//	config.interval = config.interval || 1000;

	var win = Ext.getCmp(config.id);
	if(Ext.isEmpty(win)){
		win = Ext.create('Ext.window.Window', {
			id: config.id,
			stateful: config.stateful,
			stateId: config.stateId,
			title: config.title,
			iconCls: config.iconCls,
			modal: config.modal,
			maximizable: config.maximizable,
			height: config.height,
			width: config.width,
			minHeight: config.minHeight,
			minWidth: config.minWidth,
			animateTarget: config.animateTarget,
			autoShow: false,
			layout: 'fit',
			items: [{
				border: false,
				xtype: 'gridpanel',
				store: 'recalcStore',
				stateful: config.stateful,
				stateId: config.id+'-gridpanel',
				plugins: [self.getBufferedRenderer()],
				viewConfig: {
					loadMask: false
				},
				columns: [
					{xtype: 'rownumberer',                             stateId: 'rownumberer', draggable: false},
					{text: AgLang.rep_id,     dataIndex: 'rep_id',     stateId: 'rep_id',     width: 70, minWidth: 70, hidden: false, hideable: false, draggable: false, xtype: 'agrecalccolumn'},
					{text: AgLang.cdi_name,   dataIndex: 'cdi_name',   stateId: 'cdi_name',   width: 70, minWidth: 70, hidden: false, hideable: false, draggable: false, xtype: 'agcolumn'},
					{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e', stateId: 'cdi_name_e', flex: 1,   minWidth: 70, hidden: false, hideable: false, draggable: false, xtype: 'agcolumn'},
					{text: AgLang.tree,       dataIndex: 'bul_name_e', stateId: 'bul_name_e', width: 50, minWidth: 50, hidden: false, hideable: false, draggable: false, xtype: 'agcolumn'},
					{text: 'Depth',           dataIndex: 'but_depth',  stateId: 'but_depth',  width: 40, minWidth: 40, hidden: true,  hideable: true,  draggable: false, xtype: 'agnumbercolumn', format: self.FORMAT_INT_NUMBER}
				],
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'bottom',
					items: ['->','-',{itemId: 'count',xtype: 'tbtext',text: ' '}]
				}],
				listeners: {
					afterrender: function( gridpanel, eOpts ){
						try{
							gridpanel.view.getGridColumns().forEach(function(column){
								if(column.getXType()=='rownumberer'){
									gridpanel.view.autoSizeColumn(column);
								}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
									gridpanel.view.autoSizeColumn(column);
								}
							});
						}catch(e){
							console.error(e);
						}
						return;

						var store = gridpanel.getStore();
						store.on('load',function(store, records, successful, eOpts){
							try{
								if(successful && records.length>0){
									var columns;
									try{columns = gridpanel.view.getGridColumns();}catch(e){}
									if(Ext.isEmpty(columns)) return;
									columns.forEach(function(column){
										if(column.getXType()=='rownumberer'){
											gridpanel.view.autoSizeColumn(column);
										}else if(Ext.isEmpty(column.flex) && column.isVisible() && column.resizable){
											gridpanel.view.autoSizeColumn(column);
										}
									});
								}
							}catch(e){
								console.error(e);
							}
						},store,{
							buffer: 100
						});
					},
					columnhide: function( ct, column, eOpts ){
					},
					columnshow: function( ct, column, eOpts ){
					}
				}
			}],
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				ui: 'footer',
				defaults: {minWidth: 75},
				defaultType: 'button',
				items: [{
					itemId: 'debug',
					text: 'debug',
					listeners: {
						click: function(b){
							Ext.Msg.prompt('sessionID', 'Please enter sessionID:', function(btn, text){
								if(btn != 'ok') return;
								self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode({sessionID:text}));
								var json;
								if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)) json = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY));
								if(Ext.isEmpty(json)) return;
								var ok_button = b.up('toolbar').getComponent('ok');
								ok_button.setDisabled(true);
								self.recalculation_progress(config,ok_button,json);
							});
						}
					}
				},'->',{
					disabled: true,
					itemId: 'ok',
					text: AgLang.recalculation,
					listeners: {
						click: function(b){
							b.up('toolbar').getComponent('ok').setDisabled(true);

							var recalcStore = Ext.data.StoreManager.lookup('recalcStore');
							var rawData = recalcStore.getProxy().getReader().rawData;
							Ext.Ajax.request({
								url: 'api-recalculation.cgi?cmd=recalc',
								method: 'POST',
								timeout: 30000*2*5*2,
								params: {
									all_datas: Ext.encode(rawData.all_datas)
								},
								callback: function(options,success,response){

									try{json = Ext.decode(response.responseText)}catch(e){};
									if(success==false || Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false || Ext.isEmpty(json.sessionID)){
										b.up('toolbar').getComponent('ok').setDisabled(false);
										if(Ext.isEmpty(json) || Ext.isEmpty(json.msg)) return;
										Ext.Msg.show({
											title: b.text,
											msg: json.msg,
											buttons: Ext.Msg.OK,
											icon: Ext.Msg.ERROR
										});
										return;
									}

									self.recalculation_progress(config,b,json);
								}
							});

						}
					}
				},{
					hidden: true,
					text: AgLang.cancel,
					itemId: 'cancel',
					listeners: {
						click: function(b){

							b.up('toolbar').getComponent('ok').setDisabled(false);
							b.up('toolbar').getComponent('cancel').hide();
							b.up('toolbar').getComponent('close').show();

							Ext.Ajax.request({
								url: 'api-recalculation.cgi?cmd=cancel',
								method: 'POST',
								timeout: 30000*2*5*2,
								params: config.store_params.params,
								callback: function(options,success,response){

									try{json = Ext.decode(response.responseText)}catch(e){};
									if(Ext.isEmpty(json) || Ext.isEmpty(json.success) || json.success==false) return;

									b.up('window').close();
								}
							});
						}
					}
				},{
					text: AgLang.close,
					itemId: 'close',
					listeners: {
						click: function(b){
							b.up('window').close();
						}
					}
				}]
			}],
			listeners: {
				afterrender: function( comp, eOpts ){
					comp.setLoading(true);
				},
				show: function(comp,eOpts){
					comp.down('gridpanel').getStore().removeAll();
				}
			}

		});
	}
	win.show(null,function(){
		var toolbar = win.getDockedItems('toolbar[dock="bottom"]')[0];
		toolbar.getComponent('ok').setDisabled(true);

		Ext.defer(function(){
			var comp = this;
			if(config.callback) (config.callback)(comp);

			var store = comp.down('gridpanel').getStore();
			store.on({
				load: {
					fn: function(store,records){
						var comp = this;
						var gridpanel = comp.down('gridpanel');
						if(gridpanel){
							var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
							if(toolbar) toolbar.getComponent('count').setText(store.getCount()+' / '+store.getTotalCount());
						}

						var toolbar = comp.getDockedItems('toolbar[dock="bottom"]')[0];
						var ok_button = toolbar.getComponent('ok');
						ok_button.setDisabled(store.getTotalCount()>0?false: true);

						comp.setLoading(false);

//						self.AgLocalStorage.save(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY,Ext.encode({sessionID:'21c9186d4dc0008ba07ba9af4a38b93e'}));

						var json;
						if(self.AgLocalStorage.exists(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY)) json = Ext.decode(self.AgLocalStorage.load(self.DEF_LOCALDB_PROGRESS_RECALC_SESSION_KEY));
						if(Ext.isEmpty(json)) return;
						ok_button.setDisabled(true);
						self.recalculation_progress(config,ok_button,json);

					},
					single: true,
					scope: win
				}
			});
			store.loadPage(1,config.store_params);

		},2000,win);

	});


};

window.AgApp.prototype.openFMAEditList = function(config){
	var self = this;

	config = config || {};
	config.title = config.title || AgLang.error_twitter;
	config.iconCls = config.iconCls || 'btweet';
	config.height = config.height || Ext.getBody().getHeight(true) - 100;
	config.width = config.width || Ext.getBody().getWidth(true) - 100;
	config.minHeight = config.minHeight || 540;
	config.minWidth = config.minWidth || 540;
	config.maximizable = Ext.isEmpty(config.maximizable) ? true : config.maximizable;
	config.modal = Ext.isEmpty(config.modal) ? true : config.modal;
	config.id = config.id || 'fma-edit-list-window';
//	config.stateful = config.stateful || true;
//	config.stateId = config.stateId || config.id;

	var win = Ext.getCmp(config.id);
	if(Ext.isEmpty(win)){
		win = Ext.create('Ext.window.Window', {
			id: config.id,
			stateful: config.stateful,
			stateId: config.stateId,
			title: config.title,
			iconCls: config.iconCls,
			modal: config.modal,
			maximizable: config.maximizable,
			height: config.height,
			width: config.width,
			minHeight: config.minHeight,
			minWidth: config.minWidth,
			animateTarget: config.animateTarget,
			autoShow: false,
			layout: 'fit',
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				items: ['->','-',configLinkedUploadPartsButton]
			}],
			listeners: {
				show: {
					fn: function(comp,eOpts){
						if(config.callback) (config.callback)(win);
					},buffer:100
				}
			}

		});
	}
	win.show();
};

window.AgApp.prototype.openErrorTwitter = function(config){
	var self = this;

	config = config || {};
	config.title = config.title || AgLang.error_twitter;
	config.iconCls = config.iconCls || 'btweet';
	config.height = config.height || 540;
	config.width = config.width || Ext.getBody().getWidth(true) - 100;
	config.minHeight = config.minHeight || 540;
	config.minWidth = config.minWidth || 540;
	config.maximizable = Ext.isEmpty(config.maximizable) ? true : config.maximizable;
	config.modal = Ext.isEmpty(config.modal) ? false : config.modal;
	config.id = config.id || 'error-twitter-window';
//	config.stateful = config.stateful || true;
//	config.stateId = config.stateId || config.id;

	var win = Ext.getCmp(config.id);
	if(Ext.isEmpty(win)){

		var toggle_selected_column = function(button,pressed,eOpts){
			var grid = this;
			Ext.each(grid.columns,function(column,i,a){
				if(column.dataIndex!='selected') return true;
				if(pressed){
					column.hide();
				}else{
					column.show();
				}
				return false;
			});

			var toolbar = grid.up('window').getDockedItems('toolbar[dock="bottom"]')[0];
			if(pressed){
				toolbar.getComponent('show').show();
			}else{
				toolbar.getComponent('show').hide();
			}

			grid.getSelectionModel().deselectAll();
		};

		var datachanged_store = function(store,options){
			var grid = this;
			self.load_pallet_store_records(store.getRange(),store,grid);
		};

		var update_store = function(store,record,operation){
			if(operation==Ext.data.Record.EDIT){
			}else if(operation==Ext.data.Record.COMMIT){
				Ext.defer(function(){
					if(self.getPressedLinkedUploadPartsButton()){
						self.checkedUploadGroup([record]);
					}else{
						if(!record.data.selected){
							self.update_pallet_store([record]);
							return;
						}
						var treeCombobox = Ext.getCmp('tree-combobox');
						var value = treeCombobox.getValue();
						var cur_rec = treeCombobox.findRecordByValue(value);
						if(record.data.bul_id==cur_rec.data.bul_id){
							self.update_pallet_store([record]);
							return;
						}
						var find_rec = treeCombobox.findRecord('bul_id',record.data.bul_id);
						treeCombobox.select(find_rec);
						treeCombobox.fireEvent('select',treeCombobox,[find_rec]);
						self.update_pallet_store([record]);
					}
				},100);
			}
		};

		var renderer_string = function(value){
			return Ext.isEmpty(value) ? '' : '<div class="cell-renderer-string">' + value + '</div>';
		};
		var renderer_date = function(value){
			return Ext.isEmpty(value) ? '' : '<div class="cell-renderer-date">' + Ext.util.Format.date(value,self.FORMAT_DATE_TIME) + '</div>';
		};
		var renderer_boolean = function(value){
			return Ext.isEmpty(value) ? '' : '<div class="cell-renderer-boolean">' + (value?'Y': 'N') + '</div>';
		};
		var renderer_image = function(value){
			return Ext.isEmpty(value) ? '' : '<a href="'+ DEF_IMG_BASE_URL + '?i=' + value + '" target="_blank">'+value+' <img src="css/external.png"></a>';
		};
		var renderer_link = function(value){
			return Ext.isEmpty(value) ? '' : '<div class="cell-renderer-link"><img src="'+ DEF_IMG_BASE_URL + 'icon.cgi?i=' + value + '&s=S&p=rotate" width=40 height=40></div>';
		};

		var errorTwitterStore = Ext.data.StoreManager.lookup('errorTwitterStore');
		errorTwitterStore.clearFilter(true);

		win = Ext.create('Ext.window.Window', {
			id: config.id,
			stateful: config.stateful,
			stateId: config.stateId,
			title: config.title,
			iconCls: config.iconCls,
			modal: config.modal,
			maximizable: config.maximizable,
			height: config.height,
			width: config.width,
			minHeight: config.minHeight,
			minWidth: config.minWidth,
			autoShow: false,
			layout: 'fit',
			buttons: [{
				disabled: true,
				itemId: 'fix',
				text: 'Fix',
				listeners: {
					click: function(b){
						var gridpanel = b.up('window').down('gridpanel');
						var view = gridpanel.getView();
						var selModel = gridpanel.getSelectionModel();
						var selRec = selModel.getSelection()[0];
						if(selRec){
							selModel.deselectAll(true);
							selModel.select([selRec],false);
							view.focusRow(selRec);
						}else{
							selModel.deselectAll();
						}
						if(selRec){
							var fix_win = Ext.create('Ext.window.Window', {
								title: AgLang.error_twitter_fix_title,
								iconCls: config.iconCls,
								modal: true,
								width: 400,
								height: 340,
								autoShow: false,
								layout: 'fit',
								buttons: [{
									disabled: true,
									itemId: 'ok',
									text: AgLang.ok,
									listeners: {
										click: function(b){
											var formPanel = b.up('window').down('form');
											var form = formPanel.getForm();
											if(form.isValid()){
												b.setDisabled(true);

												var values = form.getFieldValues();
												if(values.rtw_fixed_date && values.rtw_fixed_time){
													var dateStr = Ext.util.Format.date(values.rtw_fixed_date,self.FORMAT_DATE) + ' ' + Ext.util.Format.date(values.rtw_fixed_time,self.FORMAT_TIME);
													values.rtw_fixed_date = Ext.Date.parse(dateStr,self.FORMAT_DATE_TIME);
												}else if(values.rtw_fixed_time){
													values.rtw_fixed_date = Ext.Date.clone(values.rtw_fixed_time);
												}
												if(values.rtw_fixed_date){
													values.rtw_fixed_epoc = values.rtw_fixed_date.getTime();
												}else{
													values.rtw_fixed_date = null;
													values.rtw_fixed_time = null;
													values.rtw_fixed_epoc = null;
												}
												if(Ext.isEmpty(values.rtw_fixed_version)) values.rtw_fixed_version=null;
												if(Ext.isEmpty(values.rtw_fixed_comment)) values.rtw_fixed_comment=null;
												if(values.tw_text) delete values.tw_text;

												var rec = form.getRecord();
												if(rec){
													rec.beginEdit();
													for(var key in values){
														rec.set(key,values[key]);
													}
													rec.endEdit();

													var isModified = false;
													for(var key in values){
														if(!rec.isModified(key)) continue;
														isModified = true;
														break;
													}
													if(isModified){
														rec.store.sync({
															callback: function(){
//																console.log('callback');
															},
															success: function(){
//																console.log('success');
																b.up('window').close();
															},
															failure: function(){
//																console.log('failure');
																var msg = '更新に失敗しました';
																var proxy = this;
																var reader = proxy.getReader();
																if(reader && reader.rawData && reader.rawData.msg){
																	msg += ' ['+reader.rawData.msg+']';
																}
																b.setDisabled(false);
																Ext.Msg.show({
																	title: b.text,
																	iconCls: b.iconCls,
																	msg: msg,
																	buttons: Ext.Msg.OK,
																	icon: Ext.Msg.ERROR,
																	fn: function(buttonId,text,opt){
																	}
																});
															}
														});
													}else{
														b.up('window').close();
													}
												}

//												console.log(values);
//												console.log(form.getRecord());
//												console.log(form.getValues());

//											b.up('window').close();
											}
										}
									}
								},{
									text: AgLang.cancel,
									listeners: {
										click: function(b){
											var formPanel = b.up('window').down('form');
											var form = formPanel.getForm();
											var rec = form.getRecord();
											if(rec) rec.store.rejectChanges();
											b.up('window').close();
										}
									}
								}],
								items: [{
									xtype: 'form',
									bodyPadding: 5,
									defaults: {
										labelAlign: 'right',
										labelWidth: 74,
										selectOnFocus: true
									},
									items: [{
										xtype: 'textareafield',
										name: 'tw_text',
										readOnly: true,
										fieldLabel: 'Tweet',
										labelAlign: 'top',
										anchor: '100%'
									},{
										xtype: 'checkbox',
										name: 'rtw_fixed',
										itemId: 'rtw_fixed',
										boxLabel: 'Error fixed',
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												var formPanel = field.up('form');
												var rtw_fixed_date = formPanel.getComponent('rtw_fixed_date');
												var rtw_fixed_time = formPanel.getComponent('rtw_fixed_time');
												var rtw_fixed_version = formPanel.getComponent('rtw_fixed_version');
												if(newValue){
													var d = new Date();
													rtw_fixed_date.setValue(d);
													rtw_fixed_date.setDisabled(false);
													rtw_fixed_time.setValue(d);
													rtw_fixed_time.setDisabled(false);

													var versionRec = Ext.getCmp('version-combobox').getStore().getAt(0);
													rtw_fixed_version.setValue(versionRec.data.display);
													rtw_fixed_version.setDisabled(false);
												}else{
													rtw_fixed_date.setDisabled(true);
													rtw_fixed_time.setDisabled(true);
													rtw_fixed_version.setDisabled(true);
												}
												field.up('window').getDockedItems('toolbar[dock="bottom"]')[0].getComponent('ok').setDisabled(false);
											}
										}
									},{
										xtype: 'textfield',
										name: 'rtw_fixed_version',
										itemId: 'rtw_fixed_version',
										fieldLabel: 'Fixed version',
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												field.up('window').getDockedItems('toolbar[dock="bottom"]')[0].getComponent('ok').setDisabled(false);
											}
										}
									},{
										xtype: 'datefield',
										name: 'rtw_fixed_date',
										itemId: 'rtw_fixed_date',
										fieldLabel: 'Fixed date',
										format: self.FORMAT_DATE,
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												field.up('window').getDockedItems('toolbar[dock="bottom"]')[0].getComponent('ok').setDisabled(false);
											}
										}
									},{
										xtype: 'timefield',
										name: 'rtw_fixed_time',
										itemId: 'rtw_fixed_time',
										fieldLabel: 'Fixed time',
										format: self.FORMAT_TIME,
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												field.up('window').getDockedItems('toolbar[dock="bottom"]')[0].getComponent('ok').setDisabled(false);
											}
										}
									},{
										xtype: 'textareafield',
										name: 'rtw_fixed_comment',
										fieldLabel: 'Fixed comment',
										labelAlign: 'top',
										anchor: '100%',
										listeners: {
											change: function(field,newValue,oldValue,eOpts){
												field.up('window').getDockedItems('toolbar[dock="bottom"]')[0].getComponent('ok').setDisabled(false);
											}
										}
									}]
								}]
							});
							fix_win.show(b.el,function(){
								var formPanel = fix_win.down('form');
								var from = formPanel.getForm();
//								form.getFields().each(function(field,index,len){
//									field.suspendEvents(false);
//								});
								from.loadRecord(selRec);

								var rtw_fixed_date = formPanel.getComponent('rtw_fixed_date');
								var rtw_fixed_time = formPanel.getComponent('rtw_fixed_time');
								var rtw_fixed_version = formPanel.getComponent('rtw_fixed_version');
								rtw_fixed_date.setDisabled(!selRec.data.rtw_fixed);
								rtw_fixed_time.setDisabled(!selRec.data.rtw_fixed);
								rtw_fixed_version.setDisabled(!selRec.data.rtw_fixed);

//								form.getFields().each(function(field,index,len){
//									field.resumeEvents();
//								});

								fix_win.getDockedItems('toolbar[dock="bottom"]')[0].getComponent('ok').setDisabled(true);
							});


						}
					}
				}
			},'->',{
				disabled: true,
				hidden: !self.getPressedLinkedUploadPartsButton(),
				itemId: 'show',
				text: 'Show Objects',
				listeners: {
					click: function(b){
						if(self.getPressedLinkedUploadPartsButton()) self.checkedUploadGroup(b.up('window').down('gridpanel').getSelectionModel().getSelection());
					}
				}
			},{
				itemId: 'close',
				text: 'Close',
				listeners: {
					click: function(b){
						b.up('window').close();
					}
				}
			}],
/**/
			items: [{
				xtype: 'aggridpanel',
				columnLines: true,
				border: false,
				viewConfig: {
					stripeRows: true,
					enableTextSelection: false,
					loadMask: true
				},
				store: 'errorTwitterStore',
				stateful: true,
				stateId: 'error-twitter-grid',
				columns: [
					{
						text: '&#160;',
						dataIndex: 'selected',
						stateId: 'selected',
						itemId: 'selected',
						width: 30,
						minWidth: 30,
						hidden: self.getPressedLinkedUploadPartsButton(),
//						hidden: false,
						hideable: false,
						sortable: false,
						resizable: false,
						draggable: false,
						xtype: 'agselectedcheckcolumn'
					},
					{
						text: AgLang.rep_id,
						dataIndex: 'rep_id',
						stateId: 'rep_id',
						itemId: 'rep_id',
						width: 64,
						minWidth: 64,
						hidden: false,
						hideable: true,
						sortable: true,
						renderer: renderer_image
					},
					{
						text: 'Icon',
						dataIndex: 'rep_id',
						stateId: 'rep_id',
						itemId: 'icon',
						width: 44,
						minWidth: 44,
						hidden: false,
						hideable: true,
						sortable: false,
						resizable: false,
						renderer: renderer_link
					},
					{
						text: AgLang.mca_id,
						dataIndex: 'mca_id',
						stateId: 'mca_id',
						itemId: 'mca_id',
						width: 64,
						minWidth: 64,
						hidden: false,
						hideable: true,
						sortable: true
					},

					{
						text: 'Ver / Tree',
						dataIndex: 'mv_name_e',
						stateId: 'mv_name_e',
						itemId: 'mv_name_e',
						width: 60,
						minWidth: 60,
						hidden: false,
						hideable: true,
						sortable: false,
						renderer: function(value,metaData,record){
							var v = Ext.isEmpty(record.data.mv_name_e) ? '<br />' : record.data.mv_name_e;
							v += '<div class="cell-separator"></div>';
							v += Ext.isEmpty(record.data.bul_abbr) ? '<br />' : record.data.bul_abbr;
							return v;
						}
					},

					{
						text: AgLang.cdi_name + ' / ' + AgLang.cdi_name_e,
						dataIndex: 'cdi_name',
						stateId: 'cdi_name',
						itemId: 'cdi_name',
						flex: 1,
						minWidth: 80,
						hidden: false,
						hideable: true,
						sortable: false,
						renderer: function(value,metaData,record){
							var v = Ext.isEmpty(record.data.cdi_name) ? '<br />' : record.data.cdi_name;
							v += '<div class="cell-separator"></div>';
							v += Ext.isEmpty(record.data.cdi_name_e) ? '<br />' : record.data.cdi_name_e;
							return '<div class="cell-renderer-string">' + v + '</div>';
						}
					},

					{
						text: AgLang.cdi_name_j + ' / ' + AgLang.cdi_name_k + ' / ' + AgLang.cdi_name_l,
						dataIndex: 'cdi_name_j',
						stateId: 'cdi_name_j',
						itemId: 'cdi_name_j',
						flex: 2,
						minWidth: 80,
						hidden: true,
						hideable: true,
						sortable: false,
						renderer: function(value,metaData,record){
							var v = Ext.isEmpty(record.data.cdi_name_j) ? '<br />' : record.data.cdi_name_j;
							v += '<div class="cell-separator"></div>';
							v += Ext.isEmpty(record.data.cdi_name_k) ? '<br />' : record.data.cdi_name_k;
							v += '<div class="cell-separator"></div>';
							v += Ext.isEmpty(record.data.cdi_name_l) ? '<br />' : record.data.cdi_name_l;
							return '<div class="cell-renderer-string">' + v + '</div>';
						}
					},

					{
						text: 'Tweet User' + ' / ' + 'Date',
						dataIndex: 'tw_user',
						stateId: 'tw_user',
						itemId: 'tw_user',
						flex: 1,
						minWidth: 70,
						hidden: false,
						hideable: true,
						sortable: false,
						renderer: function(value,metaData,record){
							var v = Ext.isEmpty(record.data.tw_user) ? '<br />' : '<div class="cell-renderer-string">' + record.data.tw_user +'</div>';
							v += '<div class="cell-separator"></div>';
							v += Ext.isEmpty(record.data.tw_date) ? '<br />' : '<div class="cell-renderer-date"><div style="float:left;">'+Ext.util.Format.date(record.data.tw_date,self.FORMAT_DATE)+'</div>' + ' <div style="float:right;">'+Ext.util.Format.date(record.data.tw_date,self.FORMAT_TIME)+'</div></div>';

//							return '<div class="cell-renderer-string">' + v + '</div>';
							return v;
						}
					},

					{
						text: 'Tweet',
						dataIndex: 'tw_text',
						stateId: 'tw_text',
						itemId: 'tw_text',
						flex: 2,
						minWidth:230,
						hidden: false,
						hideable: true,
						renderer: renderer_string
					},

					{
						text: 'Fixed / Date',
						dataIndex: 'rtw_fixed',
						stateId: 'rtw_fixed',
						itemId: 'rtw_fixed',
						width: 70,
						minWidth: 70,
						hidden: false,
						hideable: true,
						sortable: false,
						renderer: function(value,metaData,record){
							var v = '';
							if(Ext.isEmpty(record.data.rtw_fixed)){
								v += '<div class="cell-renderer-boolean">-</div>';
								v += '<div class="cell-separator"></div>';
							}else{
								v += '<div class="cell-renderer-boolean">'+(record.data.rtw_fixed?'Y': 'N')+'</div>';
								v += '<div class="cell-separator"></div>';
							}
							if(Ext.isEmpty(record.data.rtw_fixed_date)){
								v += '<div class="cell-renderer-date"><div style="float:center;">-/-/- &nbsp;-:-:-</div></div>';
							}else{
								v += '<div class="cell-renderer-date"><div style="float:left;">'+Ext.util.Format.date(record.data.rtw_fixed_date,self.FORMAT_DATE)+'</div>' + ' <div style="float:right;">'+Ext.util.Format.date(record.data.rtw_fixed_date,self.FORMAT_TIME)+'</div></div>';
							}
							return v;
						}
					},
					{
						text: 'Fixed Ver',
						dataIndex: 'rtw_fixed_version',
						stateId: 'rtw_fixed_version',
						itemId: 'rtw_fixed_version',
						width: 60,
						minWidth: 60,
						hidden: false,
						hideable: true
					},
					{
						text: 'Fixed Comment',
						dataIndex: 'rtw_fixed_comment',
						stateId: 'rtw_fixed_comment',
						itemId: 'rtw_fixed_comment',
						flex: 2,
						minWidth: 70,
						hidden: false,
						hideable: true,
						renderer: renderer_string
					}
				],
				dockedItems: [{
					dock: 'top',
					xtype: 'toolbar',
					items: {
						disabled: false,
						width: 60,
						fieldLabel: AgLang.filter,
						labelWidth: 30,
						xtype: 'searchfield',
						selectOnFocus: true,
						store: 'errorTwitterStore',
						listeners: {
							beforerender: function(searchfield, eOpt){
							},
							afterrender: function(searchfield, eOpt){
								searchfield.inputEl.set({autocomplete: 'on'});
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
					xtype: 'agpagingtoolbar',
					store: 'errorTwitterStore',
					dock: 'bottom'
				}],
				listeners: {

//					itemclick: {
//						fn: function(view,record,item,index,e,eOpts){
//							if(self.getPressedLinkedUploadPartsButton()) self.checkedUploadGroup(view.up('gridpanel').getSelectionModel().getSelection());
//						},
//						buffer:100
//					},

					destroy: function(grid,eOpts){
						grid.getStore().un({
							datachanged: {
								fn: datachanged_store,
								scope: grid
							},
							update: {
								fn: update_store,
								scope: grid
							}
						});
						var button = self.getLinkedUploadPartsButton();
						button.un({
							toggle: {
								fn: toggle_selected_column,
								buffer: 100,
								scope: grid
							}
						});
					},
					render: function(grid,eOpts){

						grid.getStore().on({
							datachanged: {
								fn: datachanged_store,
								scope: grid
							},
							update: {
								fn: update_store,
								scope: grid
							}
						});

//						grid.getView().on({
//							beforeitemkeydown: function(view, record, item, index, e, eOpts){
//								return false;
//							}
//						});

						var button = self.getLinkedUploadPartsButton();
						button.on({
							toggle: {
								fn: toggle_selected_column,
								buffer: 100,
								scope: grid
							}
						});
					},
					selectionchange: function(selModel,selected,eOpts){
						var grid = this;
						var toolbar = selModel.view.up('window').getDockedItems('toolbar[dock="bottom"]')[0];
						var disabled = Ext.isEmpty(selected);
						toolbar.getComponent('fix').setDisabled(disabled);
						toolbar.getComponent('show').setDisabled(disabled);
					}
				}
			}],
			listeners: {
				show: {
					fn: function(comp,eOpts){
						comp.down('gridpanel').getStore().loadPage(1);
					}//,buffer:100
				}
			}
		});
		win.show(config.animateTarget,function(){
			win.toFront();
			if(config.callback) (config.callback)(win);
		});
	}else{
		win.toFront();
		if(config.callback) (config.callback)(win);
	}
};

window.AgApp.prototype.initContextmenu = function(){
	var self = this;

	self.contextMenu = self.contextMenu || {};

	self.contextMenu.bp3d = Ext.create('Ext.menu.Menu', {
		items: [{
			iconCls: 'pallet_copy',
			text: AgLang.copy,
			itemId: 'pallet_copy'
		},'-',{
			iconCls: 'pallet_find',
			text: AgLang.parts_find,
			itemId: 'pallet_find'
		},'-',{
			iconCls: 'pallet_folder_find',
			text: AgLang.tree_find,
			itemId: 'pallet_folder_find'
		},'-',{
			hidden: false,
			iconCls: 'pallet_calculator',
			text: AgLang.recalculation,
			itemId: 'recalculation'
		},'-',{
			hidden: false,
			iconCls: 'pallet_calculator_error',
			text: AgLang.recalculation_force,
			itemId: 'recalculation_force'
		},'-',{
			iconCls: 'color_pallet',
			text: AgLang.properties,
			itemId: 'properties'
		},'-',{
			iconCls: 'thumbnail_background_part',
			text: AgLang.thumbnail_background_part,
			itemId: 'thumbnail_background_part'
		}]
	});

	self.bp3dItemContextmenuFunc = {
		click_parts_find: function(item,e,eOpts){
			var panel = this;

			var selModel = panel.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record)) return;

			self.checkedUploadGroup([record],true,Ext.apply({},item));
		},
		show: function(menu,eOpts){
			var panel = this;

			var selModel = panel.getSelectionModel();
			var record = selModel.getSelection()[0];

			var disabled_select = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || (Ext.isEmpty(record.data.rep_id) && Ext.isEmpty(record.data.cm_max_entry_cdi))){
				disabled_select = true;
			}else{
				cdi_name = record.data.cdi_name;
			}
			if(self.getPressedLinkedUploadPartsButton()) disabled_select = true;


			var disabled_pallet_folder_find = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.cdi_name)){
				disabled_pallet_folder_find = true;
			}else{
				cdi_name = record.data.cdi_name;
			}
			if(self.getPressedLinkedUploadPartsButton()) disabled_pallet_folder_find = true;
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

			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				if(disabled_pallet_folder_find){
					pallet_folder_find.setText(AgLang.tree_find);
					pallet_folder_find.setDisabled(true);
				}else{
//			if(panel instanceof Ext.tree.Panel) disabled_pallet_folder_find = true;

					pallet_folder_find.setText(AgLang.tree_find+':['+cdi_name+']');
					pallet_folder_find.setDisabled(false);
//					pallet_folder_find.on('click',self.palletItemContextmenuFunc.click_folder_find,panel,{delay:100});
					pallet_folder_find.on('click',self.palletItemContextmenuFunc.click_folder_find,panel);
				}
			}

			var versionCombobox = Ext.getCmp('version-combobox');
			var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
			var mv_publish = r.data.mv_publish;

			var recalculation = menu.getComponent('recalculation');
			if(recalculation){
				recalculation.setDisabled(mv_publish);
				if(mv_publish){
					recalculation.setText(AgLang.error_recalculation_is_publish);
				}else{
					recalculation.setText(AgLang.recalculation);
					recalculation.on('click',self.palletItemContextmenuFunc.click_recalculation,panel);
				}
			}

			var recalculation_force = menu.getComponent('recalculation_force');
			if(recalculation_force){
				recalculation_force.setDisabled(mv_publish);
				if(mv_publish){
					recalculation_force.setText(AgLang.error_recalculation_is_publish);
				}else{
					recalculation_force.setText(AgLang.recalculation_force);
					recalculation_force.on('click',self.palletItemContextmenuFunc.click_recalculation_force,panel);
				}
			}

			var reload = menu.getComponent('reload');
			if(reload){
				reload.on('click',self.palletItemContextmenuFunc.click_reload,panel);
			}

			var pallet_copy = menu.getComponent('pallet_copy');
			if(pallet_copy){
//				pallet_copy.on('click',self.bp3dItemContextmenuFunc.click_copy,panel,{delay:100});
				pallet_copy.on('click',self.palletItemContextmenuFunc.click_copy,panel);
			}

			var properties = menu.getComponent('properties');
			if(properties){
				properties.on('click',self.palletItemContextmenuFunc.click_properties,panel);
			}

			var thumbnail_background_part = menu.getComponent('thumbnail_background_part');
			if(thumbnail_background_part){
				thumbnail_background_part.on('click',self.palletItemContextmenuFunc.click_thumbnail_background_part,panel);
			}
		},
		hide: function(menu,eOpts){
			var panel = this;

//			self.contextMenu.bp3d.un('show',self.bp3dItemContextmenuFunc.show,panel);
			self.contextMenu.bp3d.un('beforeshow',self.bp3dItemContextmenuFunc.show,panel);
			self.contextMenu.bp3d.un('hide',self.bp3dItemContextmenuFunc.hide,panel);

			var selModel = panel.getSelectionModel();
			var record = selModel.getSelection()[0];
			var disabled_select = false;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.rep_id)) disabled_select = true;
			if(self.getPressedLinkedUploadPartsButton()) disabled_select = true;

			var disabled_pallet_folder_find = false;
			var cdi_name = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.cdi_name)) disabled_pallet_folder_find = true;
			if(self.getPressedLinkedUploadPartsButton()) disabled_pallet_folder_find = true;
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

			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				if(disabled_pallet_folder_find){
					pallet_folder_find.setDisabled(true);
				}else{
					pallet_folder_find.setDisabled(false);
					pallet_folder_find.un('click',self.palletItemContextmenuFunc.click_folder_find,panel);
				}
			}

			var versionCombobox = Ext.getCmp('version-combobox');
			var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
			var mv_frozen = r.data.mv_frozen;

			var recalculation = menu.getComponent('recalculation');
			if(recalculation){
				recalculation.setText(AgLang.recalculation);
				recalculation.setDisabled(mv_frozen);
				if(!mv_frozen) recalculation.un('click',self.palletItemContextmenuFunc.click_recalculation,panel);
			}

			var recalculation_force = menu.getComponent('recalculation_force');
			if(recalculation_force){
				recalculation_force.setText(AgLang.recalculation_force);
				recalculation_force.setDisabled(mv_frozen);
				if(!mv_frozen) recalculation_force.un('click',self.palletItemContextmenuFunc.click_recalculation_force,panel);
			}

			var reload = menu.getComponent('reload');
			if(reload){
				if(!reload.isDisabled()) reload.un('click',self.palletItemContextmenuFunc.click_reload,panel);
			}

			var pallet_copy = menu.getComponent('pallet_copy');
			if(pallet_copy){
				pallet_copy.un('click',self.palletItemContextmenuFunc.click_copy,panel);
			}

			var properties = menu.getComponent('properties');
			if(properties){
				properties.un('click',self.palletItemContextmenuFunc.click_properties,panel);
			}

			var thumbnail_background_part = menu.getComponent('thumbnail_background_part');
			if(thumbnail_background_part){
				thumbnail_background_part.un('click',self.palletItemContextmenuFunc.click_thumbnail_background_part,panel);
			}
		}
	};

	self.contextMenu.pallet = Ext.create('Ext.menu.Menu', {
		items: [{
			iconCls: 'pallet_copy',
			text: AgLang.copy,
			itemId: 'pallet_copy'
		},'-',{
			iconCls: 'pallet_find',
			text: AgLang.parts_mirroring_find,
			itemId: 'parts_mirroring_find'
		},{
			iconCls: 'pallet_find',
			text: AgLang.parts_org_find,
			itemId: 'parts_org_find'
		},'-',{
			iconCls: 'pallet_folder_find',
			text: AgLang.tree_find,
			itemId: 'pallet_folder_find'
		},'-',{
			hidden: false,
			iconCls: 'pallet_calculator',
			text: AgLang.recalculation,
			itemId: 'recalculation'
		},'-',{
			hidden: false,
			iconCls: 'pallet_calculator_error',
			text: AgLang.recalculation_force,
			itemId: 'recalculation_force'
		}]
	});

	self.palletItemContextmenuFunc = {
		click_parts_mirroring_find: function(item,e,eOpts){
			var grid = this;
			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.art_id)) return;

			var art_mirroring_id = record.data.art_id;
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
						var plugin = grid.getPlugin('bufferedrenderer');
						if(plugin){
							var idxs = [];
							var store = grid.getStore();
							records.forEach(function(record){
								var idx = store.indexOf(record);
								if(idx>=0) idxs.push(idx);
							});
							if(idxs.length) plugin.scrollTo(idxs.sort().shift(),true);
						}
					}
				});
			},0);
		},

		click_parts_org_find: function(item,e,eOpts){
			var grid = this;
			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data) || Ext.isEmpty(record.data.artog_id)) return;

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
					var plugin = grid.getPlugin('bufferedrenderer');
					if(plugin){
						var idxs = [];
						var store = grid.getStore();
						records.forEach(function(record){
							var idx = store.indexOf(record);
							if(idx>=0) idxs.push(idx);
						});
						if(idxs.length) plugin.scrollTo(idxs.sort().shift(),true);
					}
				}
			});
		},

		click_folder_find: function(item,e,eOpts){
			var grid = this;
			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];
			if(Ext.isEmpty(record)) return;

			var isTreePanel = false;
			if(grid instanceof Ext.tree.Panel) isTreePanel = true;

			self.getTreePath({cdi_name:record.data.cdi_name},function(treePath,nodeList){
				if(Ext.isEmpty(treePath)) return;
				var partsTreePanel = Ext.getCmp('parts-tree-panel');
//				if(partsTreePanel && partsTreePanel.rendered){
				if(partsTreePanel){

					var tabPanel = partsTreePanel.up('tabpanel');
					if(tabPanel && tabPanel.getActiveTab().id != partsTreePanel.id){
						tabPanel.setActiveTab(partsTreePanel)
					}

					Ext.defer(function(){

						partsTreePanel.getSelectionModel().deselectAll();

						partsTreePanel.selectPath(treePath,'cdi_name','/',function(bSuccess, oLastNode){
							if(bSuccess){
								Ext.defer(function(){

									var task = new Ext.util.DelayedTask(function(){
										partsTreePanel.un('beforeitemexpand',beforeitemexpand,partsTreePanel);
										partsTreePanel.un('itemexpand',itemexpand,partsTreePanel);
										partsTreePanel.getView().focusRow(oLastNode);
										console.log(oLastNode);
									});

									var beforeitemexpand = function(node,eOpts){
										task.cancel()
									};
									var itemexpand = function(node,eOpts){
										task.delay(2000);
									};

									partsTreePanel.on('beforeitemexpand',beforeitemexpand,partsTreePanel);
									partsTreePanel.on('itemexpand',itemexpand,partsTreePanel);
									task.delay(500);
								},250,this);

							}else{
								Ext.Msg.show({
									title: item.text,
									msg: Ext.String.format(AgLang.error_folder_find,record.data.cdi_name,Ext.getCmp('tree-combobox').getRawValue()),
									iconCls: item.iconCls,
									buttons: Ext.MessageBox.OK,
									icon: Ext.MessageBox.WARNING,
									modal: true
								});
							}
						},partsTreePanel);

					},100)
				}
			});
		},
		click_recalculation: function(item,e,eOpts){
			var panel = this;
			var selModel = panel.getSelectionModel();
			var records = selModel.getSelection();
			if(Ext.isEmpty(records)) return;
			self.recalculation(records);
		},
		click_recalculation_force: function(item,e,eOpts){
			var panel = this;
			var selModel = panel.getSelectionModel();
			var records = selModel.getSelection();
			if(Ext.isEmpty(records)) return;
			self.recalculation(records,true);
		},
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
		show: function(menu,eOpts){
			var grid = this;

			var selModel = grid.getSelectionModel();
			var record = selModel.getSelection()[0];


			var disabled_parts_mirroring_find = false;
			var art_mirroring_id = undefined;
			if(Ext.isEmpty(record) || Ext.isEmpty(record.data.art_id)){
				disabled_parts_mirroring_find = true;
			}else{
				art_mirroring_id = record.data.art_id;
				if(art_mirroring_id.match(/^(.+)M$/)){
					art_mirroring_id = RegExp.$1;
				}else{
					art_mirroring_id += 'M';
				}
			}
			if(self.getPressedLinkedUploadPartsButton()) disabled_parts_mirroring_find = true;

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
			if(self.getPressedLinkedUploadPartsButton()) disabled_parts_org_find = true;

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
			if(self.getPressedLinkedUploadPartsButton()) disabled_pallet_folder_find = true;

			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				if(disabled_pallet_folder_find){
					pallet_folder_find.setText(AgLang.tree_find);
					pallet_folder_find.setDisabled(true);
				}else{
					pallet_folder_find.setText(AgLang.tree_find+':['+cdi_name+']');
					pallet_folder_find.setDisabled(false);
//					pallet_folder_find.on('click',self.palletItemContextmenuFunc.click_folder_find,grid,{delay:100});
					pallet_folder_find.on('click',self.palletItemContextmenuFunc.click_folder_find,grid);
				}
			}

			var versionCombobox = Ext.getCmp('version-combobox');
			var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
			var mv_publish = r.data.mv_publish;

			var recalculation = menu.getComponent('recalculation');
			if(recalculation){
				if(mv_publish || Ext.isEmpty(cdi_name)){
					if(mv_publish){
						recalculation.setText(AgLang.error_recalculation_is_publish);
					}else{
						recalculation.setText(AgLang.recalculation);
					}
					recalculation.setDisabled(true);
				}else{
					recalculation.setText(AgLang.recalculation);
					recalculation.setDisabled(false);
					recalculation.on('click',self.palletItemContextmenuFunc.click_recalculation,grid);
				}
			}

			var recalculation_force = menu.getComponent('recalculation_force');
			if(recalculation_force){
				if(mv_publish || Ext.isEmpty(cdi_name)){
					if(mv_publish){
						recalculation_force.setText(AgLang.error_recalculation_is_publish);
					}else{
						recalculation_force.setText(AgLang.recalculation_force);
					}
					recalculation_force.setDisabled(true);
				}else{
					recalculation_force.setText(AgLang.recalculation_force);
					recalculation_force.setDisabled(false);
					recalculation_force.on('click',self.palletItemContextmenuFunc.click_recalculation_force,grid);
				}
			}

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
			if(self.getPressedLinkedUploadPartsButton()) disabled_parts_org_find = true;

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
			if(self.getPressedLinkedUploadPartsButton()) disabled_pallet_folder_find = true;

			self.contextMenu.pallet.un('beforeshow',self.palletItemContextmenuFunc.show,grid);
			self.contextMenu.pallet.un('hide',self.palletItemContextmenuFunc.hide,grid);

			var pallet_folder_find = menu.getComponent('pallet_folder_find');
			if(pallet_folder_find){
				pallet_folder_find.setDisabled(disabled_pallet_folder_find);
				pallet_folder_find.un('click',self.palletItemContextmenuFunc.click_folder_find,grid);
			}

			var versionCombobox = Ext.getCmp('version-combobox');
			var r = versionCombobox.findRecordByValue(versionCombobox.getValue());
			var mv_frozen = r.data.mv_frozen;

			var recalculation = menu.getComponent('recalculation');
			if(recalculation){
				recalculation.setText(AgLang.recalculation);
				recalculation.setDisabled((mv_frozen || Ext.isEmpty(cdi_name)));
				recalculation.un('click',self.palletItemContextmenuFunc.click_recalculation,grid);
			}

			var recalculation_force = menu.getComponent('recalculation_force');
			if(recalculation_force){
				recalculation_force.setText(AgLang.recalculation_force);
				recalculation_force.setDisabled((mv_frozen || Ext.isEmpty(cdi_name)));
				recalculation_force.un('click',self.palletItemContextmenuFunc.click_recalculation_force,grid);
			}

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
					var text = button.getText();
					if(text) item.setText(button.getText());
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

window.AgApp.prototype.getTreePath = function(params,aCB){
	var self = this;
	params = Ext.apply({},params || {},self.getExtraParams() || {});
	delete params.current_datas;
	delete params.model;
	delete params.version;
	delete params.ag_data;
	delete params.tree;
	delete params.md_id;
	delete params.mv_id;
	delete params.mr_id;
	delete params._ExtVerMajor;
	delete params._ExtVerMinor;
	delete params._ExtVerPatch;
	delete params._ExtVerBuild;
	delete params._ExtVerRelease;
	Ext.Ajax.request({
		url: 'get-info.cgi',
		method: 'POST',
		params: {
			cmd: 'tree-path',
			params: Ext.encode(params)
		},
		success: function(response){
			var json;
			try{json = Ext.decode(response.responseText)}catch(e){};
			if(aCB) (aCB)(json?json.treepath:undefined,json?json.nodelist:undefined);
		}
	});
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
			xtype: 'form',
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
				hideLabel: true,
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
						var form = this.up('form').getForm();
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
												if(callback) (callback)(close_progress_msg? true : false);
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
														var uploadGroupStore = Ext.data.StoreManager.lookup('uploadGroupStore');
														uploadGroupStore.loadPage(1);
													}
													var treePanelStore = Ext.data.StoreManager.lookup('treePanelStore');
													treePanelStore.load();

													var partsGridStore = Ext.data.StoreManager.lookup('partsGridStore');
													partsGridStore.loadPage(1);

													var bp3dSearchStore = Ext.data.StoreManager.lookup('bp3dSearchStore');
													bp3dSearchStore.loadPage(1);
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
	//													console.log("actioncomplete()");
											},
											actionfailed : function(form,action,eOpts){
	//													console.log("actionfailed()");
											},
											beforeaction : function(form,action,eOpts){
	//													console.log("beforeaction()");
											},
											dirtychange : function(form,dirty,eOpts){
	//													console.log("dirtychange()");
											},
											validitychange : function(form,valid,eOpts){
	//													console.log("validitychange()");
											},
										});
										form.submit({
											url: 'import.cgi',
											params: config.params,
											waitMsg: AgLang['import']+' your data...',
											success: function(fp, o) {
												win.hide();
												self.updateArtInfo(function(){
													var viewDom = Ext.getCmp('upload-group-grid').getView().el.dom;
													var scX = viewDom.scrollLeft;
													var scY = viewDom.scrollTop;
													Ext.data.StoreManager.lookup('uploadGroupStore').loadPage(1,{
														callback: function(records, operation, success){
															Ext.getCmp('upload-group-grid').getView().scrollBy(scX,scY,false);

															viewDom = Ext.getCmp('upload-object-grid').getView().el.dom;
															scX = viewDom.scrollLeft;
															scY = viewDom.scrollTop;
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

														}
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
				{text: AgLang.cdi_name,   dataIndex: 'cdi_name',   width: 80, minWidth: 80, hidden: false, hideable: true, draggable: false},
				{text: AgLang.cdi_name_e, dataIndex: 'cdi_name_e', flex: 1,   minWidth: 80, hidden: false, hideable: true, draggable: false}
			],
			selType: 'rowmodel',
			selModel: {
				mode: 'SINGLE',
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
							searchfield.inputEl.set({autocomplete: 'on'});
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
		self.__EventSource = new EventSource('eventsource.cgi',{withCredentials: true});
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
	var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
	var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
	var func_load = function(){
		if(datasetMngStore.getCount()==0 || conceptBuildStore.getCount()==0) return;
		datasetMngStore.un('load',func_load);
		conceptBuildStore.un('load',func_load);
		self.openExportSelectDatasetWindow();
	};
	datasetMngStore.on('load',func_load);
	conceptBuildStore.on('load',func_load);
/**/

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
