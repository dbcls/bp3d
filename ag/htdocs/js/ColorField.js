/**
 * @class Ext.ux.ColorField
 * @extends Ext.form.TriggerField
 * Provides a color input field with a {@link Ext.ColorPalette} dropdown.
* @constructor
* Create a new ColorField
 * <br />Example:
 * <pre><code>
var color_field = new Ext.ux.ColorField({
	fieldLabel: 'Color',
	id: 'color',
	width: 175,
	allowBlank: false
});
</code></pre>
* @param {Object} config
 */

Ext.ux.ColorField = Ext.extend(Ext.form.TriggerField,  {
	/**
	 * @cfg {String} invalidText
	 * The error to display when the color in the field is invalid (defaults to
	 * '{value} is not a valid color - it must be in the format {format}').
	 */
	invalidText : "'{0}' is not a valid color - it must be in a the hex format (# followed by 3 or 6 letters/numbers 0-9 A-F)",
	/**
	 * @cfg {String} triggerClass
	 * An additional CSS class used to style the trigger button.  The trigger will always get the
	 * class 'x-form-trigger' and triggerClass will be <b>appended</b> if specified (defaults to 'x-form-color-trigger'
	 * which displays a color wheel icon).
	 */
	triggerClass : 'x-form-color-trigger',
	/**
	 * @cfg {String/Object} autoCreate
	 * A DomHelper element spec, or true for a default element spec (defaults to
	 * {tag: "input", type: "text", size: "10", autocomplete: "off"})
	 */

	// private
	defaultAutoCreate : {tag: "input", type: "text", size: "10", maxlength: "7", autocomplete: "off"},

	// Limit input to hex values
	maskRe: /[#a-f0-9]/i,

	menu : null,
	menuOption : null,

	// private
	validateValue : function(value){
		if(!Ext.ux.ColorField.superclass.validateValue.call(this, value)){
			return false;
		}
		if(value.length < 1){ // if it's blank and textfield didn't flag it then it's valid
			this.setColor('');
			return true;
		}

		var parseOK = this.parseColor(value);

		if(!value || (parseOK == false)){
			this.markInvalid(String.format(this.invalidText,value));
			return false;
		}
		this.setColor(value);
		return true;
	},

	/**
	 * Sets the current color and changes the background.
	 * Does *not* change the value of the field.
	 * @param {String} hex The color value.
	 */
	setColor : function(color) {
		if (color=='' || color==undefined)
		{
			if (this.emptyText!='' && this.parseColor(this.emptyText))
				color=this.emptyText;
			else
				color='transparent';
		}
		if (this.trigger)
			this.trigger.setStyle( {
				'background-color': color
			});
		else
		{
			this.on('render',function(){this.setColor(color)},this);
		}
	},
	
	// private
	// Provides logic to override the default TriggerField.validateBlur which just returns true
	validateBlur : function(){
		return !this.menu || !this.menu.isVisible();
	},

	/**
	 * Returns the current value of the color field
	 * @return {String} value The color value
	 */
	getValue : function(){
		return Ext.ux.ColorField.superclass.getValue.call(this) || "";
	},

	/**
	 * Sets the value of the color field.  You can pass a string that can be parsed into a valid HTML color
	 * <br />Usage:
	 * <pre><code>
		colorField.setValue('#FFFFFF');
	 </code></pre>
	 * @param {String} color The color string
	 */
	setValue : function(color){
		Ext.ux.ColorField.superclass.setValue.call(this, this.formatColor(color));
		this.setColor( this.formatColor(color));
	},

	// private
	parseColor : function(value){
		return (!value || (value.substring(0,1) != '#')) ? false : (value.length==4 || value.length==7 );
	},

	// private
	formatColor : function(value){
		if (!value || this.parseColor(value))
			return value.toUpperCase();
		if (value.length==3 || value.length==6) {
			return '#' + value.toUpperCase();
		}
		return '';
	},

	// private
	menuListeners : {
		select: function(e, c){
			this.setValue(c);
			this.fireEvent('select',this,c);
		},
		show : function(){ // retain focus styling
			this.onFocus();
		},
		hide : function(){
			this.focus.defer(10, this);
			var ml = this.menuListeners;
			this.menu.un("select", ml.select,  this);
			this.menu.un("show", ml.show,  this);
			this.menu.un("hide", ml.hide,  this);
		},
		beforeshow : function(menu) {
			try {
				if (this.value != "") {
					this.menu.palette.select(this.value);
				}else{
					this.setValue("");
					var el = this.menu.palette.el;
					if(this.menu.palette.value){
						try{el.child("a.color-"+this.menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
						this.menu.palette.value = null;
					}
				}
			}catch(ex){}
		}
	},

	// private
	menuOptionListeners : {
		select: function(e, c){
			this.setValue(c);
			this.fireEvent('select',this,c);
		},
		show : function(){ // retain focus styling
			this.onFocus();
		},
		hide : function(){
			this.focus.defer(10, this);
		},
		beforeshow : function(menu) {
			try {
				if (this.value != "") {
					this.menu.palette.select(this.value);
				}else{
					this.setValue("");
					var el = this.menu.palette.el;
					if(this.menu.palette.value){
						try{el.child("a.color-"+this.menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
						this.menu.palette.value = null;
					}
				}
			}catch(ex){}
		}
	},

	// private
	// Implements the default empty TriggerField.onTriggerClick function to display the ColorPalette
	onTriggerClick : function(){
		var self = this;
		if(self.disabled){
			return;
		}
		if(self.menu == null){
			var config = Ext.applyIf({
				colors: self.initialConfig.colors,
				itemCls: self.initialConfig.colorsItemCls,
				colorsOptionMenu: self.initialConfig.colorsOptionMenu
			},{
				colors:palette_color,
				itemCls:"x-color-palette",
				colorsOptionMenu:true
			});
			_dump(config);
//			try{config.colors = palette_color;}catch(e){}

			var optionMenu;
			if(config.colorsOptionMenu){
				optionMenu = {
					text:'Option...',
					iconCls:'color_pallet',
					listeners: {
						click: {
							fn: function(){
								self.onMenuOptionClick();
							},
							buffer:100,
							scope:self
						}
					}
				};
			}
			self.menu = new Ext.ux.ColorMenu(config,optionMenu);
		}
		self.menu.on(Ext.apply({}, self.menuListeners, {
			scope:self
		}));
		self.menu.show(self.el, "tl-bl?");
	},


	onMenuOptionClick : function(){
		if(this.disabled){
			return;
		}
		if(this.menuOption == null){
			var config = {
				closeAction:'hide',
				modal : true,
				buttons : [{
					text : 'OK',
					handler : function(b,e){
						try{
							this.menuOption.fireEvent('select',b,this.menuOption.getColor(1));
							this.menuOption.hide();
						}catch(e){
							_dump(e);
						}
					},
					scope : this
				},{
					text : 'Cancel',
					handler : function(b,e){
						try{
							this.menuOption.hide();
						}catch(e){
							_dump(e);
						}
					},
					scope : this
				}]
			};
			try{
				var color = this.getValue();
				if(color.substr(0,1) == '#') color = color.substr(1);
				config.color = color;
			}catch(e){}
			this.menuOption = new Ext.ux.ColorDialog(config);
			this.menuOption.on(Ext.apply({}, this.menuOptionListeners, {
				scope:this
			}));
		}
		var body_box = Ext.getBody().getBox();
		body_box.width -= 30;
		var menu_box = this.menuOption.getBox();
		var x = this.el.getX();
		var y = this.el.getY()+this.el.getHeight();
		if(x+menu_box.width>body_box.width) x = (x+this.el.getWidth()+17) - menu_box.width;
		if(y+menu_box.height>body_box.height) y = y - this.el.getHeight() - menu_box.height;

		if(x<0) x = 0;
		if(y<0) y = 0;

		this.menuOption.setPosition(x,y);

		try{
			var color = this.getValue();
			if(color.substr(0,1) == '#') color = color.substr(1);
			this.menuOption.setColor(color);
		}catch(e){}

		this.menuOption.show(this.el);
	}



});

Ext.reg('colorfield',Ext.ux.ColorField);

Ext.ux.ColorMenu = function(config,options){
	Ext.ux.ColorMenu.superclass.constructor.call(this, config);
	this.plain = true;
	var ci = new Ext.menu.ColorItem(config);
	this.add(ci);
	if(options){
		this.add('-');
		this.add(options);
	}
	this.palette = ci.palette;
	this.relayEvents(ci, ["select"]);
};
Ext.extend(Ext.ux.ColorMenu, Ext.menu.Menu, {
	//private
	beforeDestroy: function(){
		this.palette.destroy();
	}
});
