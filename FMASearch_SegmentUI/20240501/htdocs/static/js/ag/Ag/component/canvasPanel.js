Ext.define('Ag.Component.Canvas', {
	override: 'Ag.Main',

	_createCanvasSettingPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasRendererPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasInformationPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
		},config||{}));
	},

	_createCanvasPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			itemId: 'canvas-panel',
			title: 'Canvas',
			tabConfig: {
				cls: 'ag-tab-canvas'
			},
			layout: {
				type: 'hbox',
				align: 'stretch',
				pack: 'start'
			},
			items: [
				self._createCanvasSettingPanel({width: 162, hidden: true}),
				self._createCanvasRendererPanel({flex: 1,minWidth: 162}),
//				self._createCanvasInformationPanel({width: 355})
				self._createCanvasInformationPanel({width: 415})
			],
			listeners: {
				activate: function( panel, eOpts ){
					self._refreshCanvasInformationPanel();
				}
			}
		},config||{}));
	},

	_getCanvasPanel : function(){
		var self = this;
		return self.getViewport().down('panel#canvas-panel');
	}

});


