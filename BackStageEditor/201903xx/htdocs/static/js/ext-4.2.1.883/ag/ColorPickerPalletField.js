Ext.define('Ext.ag.ColorPickerPalletField', {
	extend: 'Ext.form.field.Picker',
	alias: 'widget.colorpickerpalletfield',
	requires: [
		'Ext.ag.ColorPickerPallet'
	],
	invalidText : "'{0}' is not a valid color - it must be in a the hex format (# followed by 3 or 6 letters/numbers 0-9 A-F)",
	triggerClass : 'x-form-color-trigger',
	defaultAutoCreate : {tag: "input", type: "text", size: "10", maxlength: "7", autocomplete: "off"},
	maskRe: /[#a-f0-9]/i,

	// The picker (the dropdown) must have its zIndex managed by the same ZIndexManager which is
	// providing the zIndex of our Container.
	onAdded: function() {
		var me = this,
				picker = me.getPicker();
		me.callParent(arguments);
		if (picker) {
			picker.ownerCt = me.up('[floating]');
			picker.registerWithOwnerCt();
		}
	},

	createPicker: function() {
		var me = this;
		return new Ext.ag.ColorPickerPallet({
			pickerField: me,
			ownerCt: me.ownerCt,
			renderTo: document.body,
			floating: true,
			hidden: true,
			focusOnShow: true,
//			color : me.initialConfig.value,
			listeners: {
				scope: me,
				pickcolor: {
					fn : function(ColorPickerPallet,color){
						me.setValue('#'+color);
						me.fireEvent('select',me,'#'+color);
						if(me.hideOnSelect) me.hide();
					},
					buffer :100
				}
			},
			keyNavConfig: {
				esc: function() {
					me.collapse();
				}
			}

		});
	},
	// private
	validateValue : function(value){
		var me = this;
		if(value.length < 1){
			me.setColor('');
			return true;
		}
		var parseOK = me.parseColor(value);
		if(!value || (parseOK == false)){
			me.markInvalid(String.format(me.invalidText,value));
			return false;
		}
		me.setColor(value);
		return true;
	},
	setColor : function(color) {
		var me = this;
		if (color=='' || color==undefined){
			if (me.emptyText!='' && me.parseColor(me.emptyText))
				color=me.emptyText;
			else
				color='transparent';
		}
		if(me.trigger){
			me.trigger.setStyle( {
				'background-color': color
			});
		}else{
			me.on('render',function(){me.setColor(color)},me);
		}
	},
	parseColor : function(value){
		return (!value || (value.substring(0,1) != '#')) ? false : (value.length==4 || value.length==7 );
	},
	onExpand: function(){
		var me = this;
		var color = me.getValue();
		me.picker.setColor(me.parseColor(color)?color.substr(1):'');
	}
});
