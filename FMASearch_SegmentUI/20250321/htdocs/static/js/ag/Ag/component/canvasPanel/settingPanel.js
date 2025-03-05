Ext.define('Ag.Component.Canvas.Setting', {
	override: 'Ag.Main',
	_createCanvasSettingPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
//			width: 162,
//			title: 'Setting'
		},config||{}));
	},
});
