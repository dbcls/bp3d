Ext.define('Ag.Component.Canvas.Legend', {
	override: 'Ag.Main',

	_createCanvasLegendPanel : function(config){
		var self = this;
		return Ext.create('Ext.panel.Panel', Ext.apply({
			title: 'Legend',
			itemId: 'canvas-legend-panel',
			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				itemId: 'bottom',
				items: [{
					xtype: 'checkboxfield',
					itemId: 'draw',
					boxLabel: 'Draw legend',
					checked: false,
					listeners: {
						change: function( field, newValue, oldValue, eOpts ){
							self._drawCanvasLegend();
						}
					}
				}]
			}],
			layout: 'form',
			bodyPadding: 5,
			defaults: {
				labelWidth: 50,
				labelAlign: 'right',
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						self._drawCanvasLegend();
					}
				}
			},
			items: [{
				xtype: 'textfield',
				itemId: 'title',
				fieldLabel: 'Title'
			},{
				xtype: 'textareafield',
				itemId: 'legend',
				fieldLabel: 'Legend'
			},{
				xtype: 'textfield',
				itemId: 'author',
				fieldLabel: 'Author'
			}]
		},config||{}));
	},

	_getCanvasLegendPanel : function(){
		var self = this;
		var canvas_top_panel = self._getCanvasPanel();
		return canvas_top_panel.down('panel#canvas-legend-panel');
	},

	_drawCanvasLegend : function(){
		var self = this;

		var renderer = self.getCanvasRenderer();
		renderer.removeLegend();

		var canvas_legend_panel = self._getCanvasLegendPanel();
		var draw_flag = canvas_legend_panel.down('checkboxfield#draw').getValue();
		if(!draw_flag) return;

		var legend_title = canvas_legend_panel.down('textfield#title').getValue();
		var legend_legend = canvas_legend_panel.down('textareafield#legend').getValue();
		var legend_author = canvas_legend_panel.down('textfield#author').getValue();
		if(Ext.isEmpty(legend_title) && Ext.isEmpty(legend_legend) && Ext.isEmpty(legend_author)) return;

		renderer.addLegend({
			title:  Ext.isEmpty(legend_title)  ? null : legend_title,
			legend: Ext.isEmpty(legend_legend) ? null : legend_legend.split(/[\r\n]/),
			author: Ext.isEmpty(legend_author) ? null : legend_author
		});
	}
});
