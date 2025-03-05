Ext.define('Ag.Component.Canvas.Clip', {
	override: 'Ag.Main',

	_createCanvasClipPanel : function(config){
		var self = this;
		var depth_datas = [];
		for(var i=1;i<=16;i++){
			depth_datas.push([i]);
		}
		return Ext.create('Ext.panel.Panel', Ext.apply({
			title: 'Clip',
			itemId: 'canvas-clip-panel',
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				itemId: 'bottom',
				items: [{
					xtype: 'checkboxfield',
					itemId: 'use',
					boxLabel: 'use clip',
					checked: false,
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							self._drawCanvasClip();
						}
					}
				}]
			}],
			layout: 'form',
			bodyPadding: 5,
			defaultType: 'numberfield',
			defaults: {
				labelWidth: 50,
				labelAlign: 'right',
				value: 0,
				maxValue:  1,
				minValue: -1,
				allowBlank: false,
				allowDecimals: true,
				allowExponential: false,
				allowOnlyWhitespace: false,
				step: 0.01,
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						self._drawCanvasClip();
					}
				}
			},
			items: [{
				itemId: 'x',
				fieldLabel: 'X',
				value: 1,
			},{
				itemId: 'y',
				fieldLabel: 'Y'
			},{
				itemId: 'z',
				fieldLabel: 'Z'
			},{
				itemId: 'constant',
				fieldLabel: 'Constant',
				maxValue:  1800,
				minValue: -1800,
				step: 1,
			}]
		},config||{}));
	},

	_getCanvasClipPanel : function(){
		var self = this;
		var canvas_top_panel = self._getCanvasPanel();
		return canvas_top_panel.down('panel#canvas-clip-panel');
	},

	_drawCanvasClip : function(){
		var self = this;

		var renderer = self.getCanvasRenderer();
		var canvas_clip_panel = self._getCanvasClipPanel();
		var use_flag = canvas_clip_panel.down('checkboxfield#use').getValue();
		if(use_flag){

			var clip_x = canvas_clip_panel.down('numberfield#x').getValue();
			var clip_y = canvas_clip_panel.down('numberfield#y').getValue();
			var clip_z = canvas_clip_panel.down('numberfield#z').getValue();
			var clip_constant = canvas_clip_panel.down('numberfield#constant').getValue();

			renderer.setClip([{
				x:  Ext.isEmpty(clip_x)  ? 0 : clip_x - 0,
				y:  Ext.isEmpty(clip_y)  ? 0 : clip_y - 0,
				z:  Ext.isEmpty(clip_z)  ? 0 : clip_z - 0,
				constant:  Ext.isEmpty(clip_constant)  ? 0 : clip_constant - 0
			}]);

		}else{
			renderer.clearClip();
		}
	}
});
