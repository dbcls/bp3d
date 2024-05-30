Ext.define('Ag.Component.Canvas.Information', {
	override: 'Ag.Main',

	_createCanvasPalletPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasPinPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasLegendPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasClipPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasNeighborPartsPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasInformationPanel : function(config){
		var self = this;
		var disabled = Ext.isBoolean(Ag.Def.DEBUG) ? !Ag.Def.DEBUG : true;
		return Ext.create('Ext.tab.Panel', Ext.apply({
			xtype: 'tabpanel',
			itemId: 'canvas-information-tabpanel',
//			width: 355,
			tabBar : {
				layout: {
					pack : 'end'
				}
			},
			items: [
				self._createCanvasPalletPanel({
					title: 'Pallet',
					itemId: 'canvas-pallet-panel',
				}),
				self._createCanvasPinPanel({
					title: 'Pin',
//					itemId: 'canvas-pin-gridpanel',
					hidden: disabled
				}),
				self._createCanvasLegendPanel({
					title: 'Legend',
//					itemId: 'canvas-legend-panel',
					hidden: disabled
				}),
/*
				self._createCanvasClipPanel({
					title: 'Clip',
//					itemId: 'canvas-pin-gridpanel',
					disabled: disabled
				}),
*/
				self._createCanvasNeighborPartsPanel({
					title: 'Neighbor Parts',
//					itemId: 'canvas-neighbor-parts-panel',
//					disabled: disabled,
//					hidden: true
				})
			]
		},config||{}));
	},

	_getCanvasInformationPanel : function(){
		var self = this;
		return self._getCanvasPanel().down('tabpanel#canvas-information-tabpanel');
	},

	_getCanvasInformationActiveTab : function(){
		var self = this;
		var activeTab = null;
		var canvas_information_tabpanel = self._getCanvasInformationPanel();
		if(canvas_information_tabpanel) activeTab = canvas_information_tabpanel.getActiveTab();
		return activeTab;
	},

	_isCanvasInformationActiveTabPalletPanel : function(){
		var self = this;
		var activeTab = self._getCanvasInformationActiveTab() || {};
		return activeTab.itemId === 'canvas-pallet-panel';
	},

	_setCanvasInformationActiveTabPalletPanel : function(){
		var self = this;
		var canvas_pallet_gridpanel = null;
		var canvas_information_tabpanel = self._getCanvasInformationPanel();
		if(canvas_information_tabpanel) canvas_pallet_gridpanel = canvas_information_tabpanel.setActiveTab('canvas-pallet-panel');
		console.log(canvas_pallet_gridpanel);
	},

	_isCanvasInformationActiveTabPinPanel : function(){
		var self = this;
		var activeTab = self._getCanvasInformationActiveTab() || {};
		return activeTab.itemId === 'canvas-pin-panel';
	},

	_isCanvasInformationActiveTabNeighborPartsPanel : function(){
		var self = this;
		var activeTab = self._getCanvasInformationActiveTab() || {};
		return activeTab.itemId === 'canvas-neighbor-parts-panel';
	},

	_refreshCanvasInformationPanel : function(){
		var self = this;
		var activeTab = self._getCanvasInformationActiveTab();
		if(activeTab){
			if(activeTab.isXType('gridpanel',true)){
				self.refreshView(activeTab.getView());
			}else{
				activeTab = activeTab.down('gridpanel');
				if(activeTab) self.refreshView(activeTab.getView());
			}
		}
	}
});
