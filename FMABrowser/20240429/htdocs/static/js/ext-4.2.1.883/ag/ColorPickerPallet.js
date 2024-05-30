Ext.define('Ext.ag.ColorPickerPallet', {
	extend: 'Ext.Component',
	alias: 'widget.colorpickerpallet',
	config:{
		floating:true,
		// help for convert hexa
		HCHARS: '0123456789ABCDEF',
		bodyStyle : {'padding':'3px'},
		width  : 378,
//		height : 294,
//		height : 313,
		height : 441,
//		colors : [
//			"000000", "993300", "333300", "003300", "003366", "000080",
//			"333399", "333333", "800000", "FF6600", "808000", "008000",
//			"008080", "0000FF", "666699", "808080", "FF0000", "FF9900",
//			"99CC00", "339966", "33CCCC", "3366FF", "800080", "969696",
//			"FF00FF", "FFCC00", "FFFF00", "00FF00", "00FFFF", "00CCFF",
//			"993366", "C0C0C0", "FF99CC", "FFCC99", "F0D2A0", "FFFF99",
//			"CCFFCC", "CCFFFF", "99CCFF", "CC99FF", "FFFFFF"
//		]

		colors : [
			"FFFFFF","FFCCCC","FFE6CC","FFFFCC","E6FFCC","CCFFCC","CCFFE6","CCFFFF","CCE6FF","CCCCFF","E6CCFF","FFCCFF","FFCCE6",
			"E6E6E6","FF9999","FFCC99","FFFF99","CCFF99","99FF99","99FFCC","99FFFF","99CCFF","9999FF","CC99FF","FF99FF","FF99CC",
			"CCCCCC","FF6666","FFB366","FFFF66","B3FF66","66FF66","66FFB3","66FFFF","66B3FF","6666FF","B366FF","FF66FF","FF66B3",
			"B3B3B3","FF3333","FF9933","FFFF33","99FF33","33FF33","33FF99","33FFFF","3399FF","3333FF","9933FF","FF33FF","FF3399",
			"999999","FF0000","FF8000","FFFF00","80FF00","00FF00","00FF80","00FFFF","0080FF","0000FF","8000FF","FF00FF","FF0080",
			"808080","CC0000","CC6600","CCCC00","66CC00","00CC00","00CC66","00CCCC","0066CC","0000CC","6600CC","CC00CC","CC0066",
			"666666","990000","994D00","999900","4D9900","009900","00994D","009999","004D99","000099","4D0099","990099","99004D",
			"4D4D4D","660000","663300","666600","336600","006600","006633","006666","003366","000066","330066","660066","660033",
			"333333","330000","331A00","333300","1A3300","003300","00331A","003333","001A33","000033","1A0033","330033","33001A",
			"000000","F0D2A0"
		]

	},
	requires: [
		'Ext.form.Panel',
		'Ext.form.FieldSet',
		'Ext.form.field.Text',
		'Ext.form.field.Number',
		'Ext.picker.Color'
	],
// initialization
//	constructor: function (config) {
	initComponent: function() {
		var me = this;

		me.listeners = me.listeners||{};

		me.callParent(arguments);
//		this.callParent();

		// register events
		me.addEvents({
			/**
			 * @event pickcolor
			 * Fires when a new color selected
			 * @param {Ext.util.ColorPicker} this
			 * @param {String} color
			 */
			pickcolor: true,
			select: true,
			/**
			 * @event changergb
			 * Fires when change rgb input
			 * @param {Ext.util.ColorPicker} this
			 * @param {Object} color ({ r: redvalue, g: greenvalue, b: bluevalue })
			 */
			changergb: true,
			/**
			 * @event changehsv
			 * Fires when change hsv input
			 * @param {Ext.util.ColorPicker} this
			 * @param {Object} color ({ h: huevalue, s: saturationvalue, v: brightnessvalue })
			 */
			changehsv: true,
			/**
			 * @event changehexa
			 * Fires when change hexa input
			 * @param {Ext.util.ColorPicker} this
			 * @param {String} color
			 */
			changehexa: true
		});
		if(me.rendered===undefined) me.rendered = false;
		if(me.value!==undefined) me._HEX = me.value;
	},

	// create internal DOM objects
	cpCreateDomObjects: function() {

		var config = {
			cls: 'x-colorpickerpalette-pallet',
			renderTo:this.el,
			handler : function(palette,color){
				if(this.getColor()!=color) this.setColor(color);
			},
			scope:this
		};
		if(this.config.colors) config.colors = this.config.colors;
		this.colorPalette = Ext.create('Ext.picker.Color',config);

		this.rgbPicker = Ext.DomHelper.append( this.el, {
			tag: 'div',
			cls: 'x-colorpickerpalette-rgb-msk'
		}, true );
		this.rgbPointer = Ext.DomHelper.append( this.rgbPicker, {
			tag: 'div',
			cls: 'x-colorpickerpalette-rgb-picker'
		}, true );
		this.rgbPointer.setXY( [ this.rgbPicker.getLeft()-this.config.pickerHotPoint.x, this.rgbPicker.getTop()-this.config.pickerHotPoint.y ] );
		this.huePicker = Ext.DomHelper.append( this.el, {
			tag: 'div',
			cls: 'x-colorpickerpalette-hue-msk'
		}, true );
		this.huePointer = Ext.DomHelper.append( this.huePicker, {
			tag: 'div',
			cls: 'x-colorpickerpalette-hue-picker'
		}, true );
		this.huePointer.setXY( [ this.huePicker.getLeft()+(this.huePointer.getWidth() / 2)+1, this.huePicker.getTop()-this.config.pickerHotPoint.y ] );
		this.formContainer = Ext.DomHelper.append( Ext.DomHelper.append( this.el, {
			tag: 'div',
			cls: 'x-colorpickerpalette-control-container x-unselectable'
		}, true ), {
			tag: 'div',
			cls: 'x-colorpickerpalette-rgb-container x-unselectable',
			style: 'clear:both'
		}, true );
		this.colorContainer = Ext.DomHelper.append( this.formContainer, {
			cls: 'x-colorpickerpalette-coloro-container x-unselectable'
		}, true ).update( this.config.captions.color || 'Color' );
		this.form = Ext.create('Ext.form.Panel',{
			frame:true,
//			autoWidth: true,
//			width: 100,
//			height: 227,
			width: 98,
			height: 235,
			cls: 'x-colorpickerpalette-form',
			labelWidth : 28,
			labelAlign : 'left',
			defaults : {
				xtype:'fieldset',
				autoHeight:true,
				defaultType: 'numberfield',
				labelWidth : 28,
				defaults : {
					hideTrigger:true,
					labelAlign : 'right',
					labelWidth : 34,
					width : 82
				},
			},
			items: [{
				title: 'RGB',
				items :[{
					fieldLabel: 'Red',
					id: 'redValue' + this.el.id
				},{
					fieldLabel: 'Green',
					id: 'greenValue' + this.el.id
				},{
					fieldLabel: 'Blue',
					id: 'blueValue' + this.el.id
				}]
			},{
				title: 'HSV',
				items :[{
					fieldLabel: 'Hue',
					id: 'hueValue' + this.el.id
				},{
					fieldLabel: 'Satur.',
					id: 'saturationValue' + this.el.id
				},{
					fieldLabel: 'Bright.',
					id: 'brightnessValue' + this.el.id
				}]
			},{
				title: 'Color',
				items :[{
					xtype: 'textfield',
					fieldLabel: 'Color',
					id: 'colorValue' + this.el.id
				}]
			}]
		});

		this.form.render(this.formContainer);
		var temp = Ext.DomHelper.append( this.form.body, {
			cls: 'x-colorpickerpalette-colors-container x-unselectable'
		}, true);
		this.wsColorContainer = Ext.DomHelper.append( temp, {
			cls: 'x-colorpickerpalette-color-container x-unselectable'
		}, true ).update( this.config.captions.websafe || 'Websafe' );
		this.inColorContainer = Ext.DomHelper.append( temp, {
			cls: 'x-colorpickerpalette-color-container x-unselectable'
		}, true ).update( this.config.captions.inverse || 'Inverse' );
		Ext.DomHelper.append( temp, { tag: 'div', style: 'height:0px;border:none;clear:both;font-size:1px;' });
//		this.form.render( this.formContainer );
		Ext.DomHelper.append( this.el, { tag: 'div', style: 'height:0px;border:none;clear:both;font-size:1px;' });
	},
	/**
	 * Convert a float to decimal
	 * @param {Float} n
	 * @return {Integer}
	 */
	realToDec: function( n ) {
		return Math.min( 255, Math.round( n * 256 ) );
	},
	/**
	 * Convert HSV color format to RGB color format
	 * @param {Integer/Array( h, s, v )} h
	 * @param {Integer} s (optional)
	 * @param {Integer} v (optional)
	 * @return {Array}
	 */
	hsvToRgb: function( h, s, v ) {
		if( h instanceof Array ) { return this.hsvToRgb.call( this, h[0], h[1], h[2] ); }
		var r, g, b, i, f, p, q, t;
		i = Math.floor( ( h / 60 ) % 6 );
		f = ( h / 60 ) - i;
		p = v * ( 1 - s );
		q = v * ( 1 - f * s );
		t = v * ( 1 - ( 1 - f ) * s );
		switch(i) {
			case 0: r=v; g=t; b=p; break;
			case 1: r=q; g=v; b=p; break;
			case 2: r=p; g=v; b=t; break;
			case 3: r=p; g=q; b=v; break;
			case 4: r=t; g=p; b=v; break;
			case 5: r=v; g=p; b=q; break;
		}
		return [this.realToDec( r ), this.realToDec( g ), this.realToDec( b )];
	},
	/**
	 * Convert RGB color format to HSV color format
	 * @param {Integer/Array( r, g, b )} r
	 * @param {Integer} g (optional)
	 * @param {Integer} b (optional)
	 * @return {Array}
	 */
	rgbToHsv: function( r, g, b ) {
		if( r instanceof Array ) { return this.rgbToHsv.call( this, r[0], r[1], r[2] ); }
		r = r / 255;
		g = g / 255;
		b = b / 255;
		var min, max, delta, h, s, v;
		min = Math.min( Math.min( r, g ), b );
		max = Math.max( Math.max( r, g ), b );
		delta = max - min;
		switch (max) {
			case min:
				h = 0;
				break;
			case r:
				h = 60 * ( g - b ) / delta;
				if ( g < b ) { h += 360; }
				break;
			case g:
				h = ( 60 * ( b - r ) / delta ) + 120;
				break;
			case b:
				h = ( 60 * ( r - g ) / delta ) + 240;
				break;
		}
		s = ( max === 0 ) ? 0 : 1 - ( min / max );
		return [Math.round( h ), s, max];
	},
	/**
	 * Convert RGB color format to Hexa color format
	 * @param {Integer/Array( r, g, b )} r
	 * @param {Integer} g (optional)
	 * @param {Integer} b (optional)
	 * @return {String}
	 */
	rgbToHex: function( r, g, b ) {
		if( r instanceof Array ) { return this.rgbToHex.call( this, r[0], r[1], r[2] ); }
		return this.decToHex( r ) + this.decToHex( g ) + this.decToHex( b );
	},
	/**
	 * Convert an integer to hexa
	 * @param {Integer} n
	 * @return {String}
	 */
	decToHex: function( n ) {
		n = parseInt(n, 10);
		n = ( !isNaN( n )) ? n : 0;
		n = (n > 255 || n < 0) ? 0 : n;
		return this.HCHARS.charAt( ( n - n % 16 ) / 16 ) + this.HCHARS.charAt( n % 16 );
	},
	/**
	 * Return with position of a character in this.HCHARS string
	 * @private
	 * @param {Char} c
	 * @return {Integer}
	 */
	getHCharPos: function( c ) {
		return this.HCHARS.indexOf( c.toUpperCase() );
	},
	/**
	 * Convert a hexa string to decimal
	 * @param {String} hex
	 * @return {Integer}
	 */
	hexToDec: function( hex ) {
		var s = hex.split('');
		return ( ( this.getHCharPos( s[0] ) * 16 ) + this.getHCharPos( s[1] ) );
	},
	/**
	 * Convert a hexa string to RGB color format
	 * @param {String} hex
	 * @return {Array}
	 */
	hexToRgb: function( hex ) {
		if(hex && hex.charAt(0)=='#' && hex.length==7) hex = hex.substr(1)
		return [ this.hexToDec( hex.substr(0, 2) ), this.hexToDec( hex.substr(2, 2) ), this.hexToDec( hex.substr(4, 2) ) ];
	},
	/**
	 * Not documented yet
	 */
	checkSafeNumber: function( v ) {
		if ( !isNaN( v ) ) {
			v = Math.min( Math.max( 0, v ), 255 );
			var i, next;
			for( i=0; i<256; i=i+51 ) {
				next = i + 51;
				if ( v>=i && v<=next ) { return ( v - i > 25 ) ? next : i; }
			}
		}
		return v;
	},
	/**
	 * Not documented yet
	 */
	websafe: function( r, g, b ) {
		if( r instanceof Array ) { return this.websafe.call( this, r[0], r[1], r[2] ); }
		return [this.checkSafeNumber( r ), this.checkSafeNumber( g ), this.checkSafeNumber( b )];
	},
	/**
	 * Not documented yet
	 */
	invert: function( r, g, b ) {
		if( r instanceof Array ) { return this.invert.call( this, r[0], r[1], r[2] ); }
		return [255-r,255-g,255-b];
	},
	/**
	 * Convert Y coordinate to HUE value
	 * @private
	 * @param {Integer} y
	 * @return {Integer}
	 */
	getHue: function( y ) {
		var hue = 360 - Math.round( ( ( this.huePicker.getHeight() - y ) / this.huePicker.getHeight() ) * 360 );
		return hue === 360 ? 0 : hue;
	},
	/**
	 * Convert HUE value to Y coordinate
	 * @private
	 * @param {Integer} hue
	 * @return {Integer}
	 */
	getHPos: function( hue ) {
		//return this.huePicker.getHeight() - ( ( hue * this.huePicker.getHeight() ) / 360 );
		return hue * ( this.huePicker.getHeight() / 360 );
	},
	/**
	 * Convert X coordinate to Saturation value
	 * @private
	 * @param {Integer} x
	 * @return {Integer}
	 */
	getSaturation: function( x ) {
		return x / this.rgbPicker.getWidth();
	},
	/**
	 * Convert Saturation value to Y coordinate
	 * @private
	 * @param {Integer} saturation
	 * @return {Integer}
	 */
	getSPos: function( saturation ) {
		return saturation * this.rgbPicker.getWidth();
	},
	/**
	 * Convert Y coordinate to Brightness value
	 * @private
	 * @param {Integer} y
	 * @return {Integer}
	 */
	getValue: function( y ) {
		return ( this.rgbPicker.getHeight() - y ) / this.rgbPicker.getHeight();
	},
	/**
	 * Convert Brightness value to Y coordinate
	 * @private
	 * @param {Integer} value
	 * @return {Integer}
	 */
	getVPos: function( value ) {
		return this.rgbPicker.getHeight() - ( value * this.rgbPicker.getHeight() );
	},
	/**
	 * Update colors from the position of picker
	 */
	updateColorsFromRGBPicker: function() {
		this._HSV = { h: this._HSV.h, s: this.getSaturation( this.lastXYRgb.x ), v: this.getValue( this.lastXYRgb.y ) };
	},
	/**
	 * Update colors from the position of HUE picker
	 */
	updateColorsFromHUEPicker: function() {
		this._HSV.h = this.getHue( this.lastYHue );
		var temp = this.hsvToRgb( this._HSV.h, 1, 1 );
		temp =  this.rgbToHex( temp[0], temp[1], temp[2] );
		this.rgbPicker.setStyle( { backgroundColor: '#' + temp } );
	},
	/**
	 * Update colors from RGB input fields
	 */
	updateColorsFromRGBFields: function() {
		var temp = this.rgbToHsv( Ext.getCmp( 'redValue' + this.el.id ).getValue(), Ext.getCmp( 'greenValue' + this.el.id ).getValue(), Ext.getCmp( 'blueValue' + this.el.id ).getValue() );
		this._HSV = { h: temp[0], s: temp[1], v: temp[2] };
	},
	/**
	 * Update colors from HEXA input fields
	 */
	updateColorsFromHexaField: function() {
		var temp = this.hexToRgb( this._HEX );
		this._RGB = { r: temp[0], g: temp[1], b: temp[2] };
		temp = this.rgbToHsv( temp[0], temp[1], temp[2] );
		this._HSV = { h: temp[0], s: temp[1], v: temp[2] };
	},
	/**
	 * Update colors from HSV input fields
	 */
	updateColorsFromHSVFields: function() {
		var temp = this.hsvToRgb( this._HSV.h, this._HSV.s, this._HSV.v );
		this._RGB = { r: temp[0], g: temp[1], b: temp[2] };
	},
	/**
	 * Update RGB color from HSV color
	 */
	updateRGBFromHSV: function() {
		var temp = this.hsvToRgb( this._HSV.h, this._HSV.s, this._HSV.v );
		this._RGB = { r: temp[0], g: temp[1], b: temp[2] };
	},
	/**
	 * Update all inputs from internal color
	 */
	updateInputFields: function() {
		var me = this;

		Ext.getCmp('redValue'        + me.el.id ).suspendEvents(false);
		Ext.getCmp('greenValue'      + me.el.id ).suspendEvents(false);
		Ext.getCmp('blueValue'       + me.el.id ).suspendEvents(false);
		Ext.getCmp('hueValue'        + me.el.id ).suspendEvents(false);
		Ext.getCmp('saturationValue' + me.el.id ).suspendEvents(false);
		Ext.getCmp('brightnessValue' + me.el.id ).suspendEvents(false);
		Ext.getCmp('colorValue'      + me.el.id ).suspendEvents(false);

		Ext.getCmp( 'redValue' + this.el.id ).setValue( this._RGB.r );
		Ext.getCmp( 'greenValue' + this.el.id ).setValue( this._RGB.g );
		Ext.getCmp( 'blueValue' + this.el.id ).setValue( this._RGB.b );
		Ext.getCmp( 'hueValue' + this.el.id ).setValue( this._HSV.h );
		Ext.getCmp( 'saturationValue' + this.el.id ).setValue( Math.round( this._HSV.s * 100 ) );
		Ext.getCmp( 'brightnessValue' + this.el.id ).setValue( Math.round( this._HSV.v * 100 ) );
		Ext.getCmp( 'colorValue' + this.el.id ).setValue( this._HEX );

		Ext.getCmp('redValue'        + me.el.id ).resumeEvents();
		Ext.getCmp('greenValue'      + me.el.id ).resumeEvents();
		Ext.getCmp('blueValue'       + me.el.id ).resumeEvents();
		Ext.getCmp('hueValue'        + me.el.id ).resumeEvents();
		Ext.getCmp('saturationValue' + me.el.id ).resumeEvents();
		Ext.getCmp('brightnessValue' + me.el.id ).resumeEvents();
		Ext.getCmp('colorValue'      + me.el.id ).resumeEvents();
	},
	/**
	 * Update color container
	 */
	updateColor: function() {
		var me = this;

		// update hexa
		this._HEX = this.rgbToHex( this._RGB.r, this._RGB.g, this._RGB.b );
		// update color container
		this.colorContainer.setStyle( { backgroundColor: '#'+this._HEX } );
		this.colorContainer.set({ title: '#'+this._HEX });
		try{this.colorPalette.select(this._HEX);}catch(e){}
		// update websafe color
		var temp = this.rgbToHex( this.websafe( this._RGB.r, this._RGB.g, this._RGB.b ) );
		this.wsColorContainer.setStyle( { backgroundColor: '#'+temp } );
		this.wsColorContainer.set({ title: '#'+temp });
		this.wsColorContainer.setStyle( { color: '#'+this.rgbToHex( this.invert( this.websafe( this._RGB.r, this._RGB.g, this._RGB.b ) ) ) } );
		// update invert color
		var temp = this.rgbToHex( this.invert( this._RGB.r, this._RGB.g, this._RGB.b ) );
		this.inColorContainer.setStyle( { backgroundColor: '#'+temp } );
		this.inColorContainer.setStyle( { color: '#'+this._HEX } );
		this.inColorContainer.set({ title: '#'+temp });
		this.colorContainer.setStyle( { color: '#'+temp } );
		// update input boxes
		this.updateInputFields();

		// fire the pickcolor event
		me.fireEvent( 'pickcolor', me, me._HEX );
		me.fireEvent( 'select', me, me._HEX );
	},
	/**
	 * Update position of both picker from the internal color
	 */
	updatePickers: function() {
		this.lastXYRgb = { x: this.getSPos( this._HSV.s ), y: this.getVPos( this._HSV.v ) };
		this.rgbPointer.setXY( [this.lastXYRgb.x-this.config.pickerHotPoint.x + this.rgbPicker.getLeft(), this.lastXYRgb.y-this.config.pickerHotPoint.y+this.rgbPicker.getTop()], this.config.animate );
		this.lastYHue = this.getHPos( this._HSV.h );
		this.huePointer.setXY( [this.huePicker.getLeft()+(this.huePointer.getWidth() / 2)+1, this.lastYHue + this.huePicker.getTop()-this.config.pickerHotPoint.y ], this.config.animate );
		var temp = this.hsvToRgb( this._HSV.h, 1, 1 );
		temp =  this.rgbToHex( temp[0], temp[1], temp[2] );
		this.rgbPicker.setStyle( { backgroundColor: '#' + temp } );
	},
	/**
	 * Internal event
	 * Catch the RGB picker click
	 */
	rgbPickerClick: function( event, cp ) {
		this.lastXYRgb = { x: event.getPageX() - this.rgbPicker.getLeft(), y: event.getPageY() - this.rgbPicker.getTop() };
		this.rgbPointer.setXY( [event.getPageX()-this.config.pickerHotPoint.x, event.getPageY()-this.config.pickerHotPoint.y], this.config.animate );
		this.updateColorsFromRGBPicker();
		this.updateRGBFromHSV();
		this.updateColor();
	},
	/**
	 * Internal event
	 * Catch the HUE picker click
	 */
	huePickerClick: function( event, cp ) {
		this.lastYHue = event.getPageY() - this.huePicker.getTop();
		this.huePointer.setY( [event.getPageY()-3], this.config.animate );
		this.updateColorsFromHUEPicker();
		this.updateRGBFromHSV();
		this.updateColor();
	},
	/**
	 * Internal event
	 * Catch the change event of RGB input fields
	 */
	changeRGBField: function( element, newValue, oldValue ) {
		if( !(newValue instanceof String) ) { newValue = element.getValue(); }
		if( newValue < 0 ) { newValue = 0; }
		if( newValue > 255 ) { newValue = 255; }

		if( element == Ext.getCmp( 'redValue' + this.el.id ) ) { this._RGB.r = newValue; }
		else if( element == Ext.getCmp( 'greenValue' + this.el.id ) ) { this._RGB.g = newValue; }
		else if( element == Ext.getCmp( 'blueValue' + this.el.id ) ) { this._RGB.b = newValue; }
		this.updateColorsFromRGBFields();
		this.updateColor();
		this.updatePickers();
		// fire the changergb event
		this.fireEvent( 'changergb', this, this._RGB );
	},
	/**
	 * Internal event
	 * Catch the change event of HSV input fields
	 */
	changeHSVField: function( element, newValue, oldValue ) {
		if( !(newValue instanceof String) ) { newValue = element.getValue(); }
		if( element == Ext.getCmp( 'hueValue' + this.el.id ) ) {
			if( newValue < 0 ) { newValue = 0; }
			if( newValue > 360 ) { newValue = 360; }
			this._HSV.h = newValue;
		} else {
			if( newValue < 0 ) { newValue = 0; }
			if( newValue > 100 ) { newValue = 100; }
			if( element == Ext.getCmp( 'saturationValue' + this.el.id ) ) { this._HSV.s = ( newValue / 100 ); }
			else if( element == Ext.getCmp( 'brightnessValue' + this.el.id ) ) { this._HSV.v = ( newValue / 100 ); }
		}
		this.updateColorsFromHSVFields();
		this.updateColor();
		this.updatePickers();
		// fire the changehsv event
		this.fireEvent( 'changehsv', this, this._HSV );
	},
	/**
	 * Internal event
	 * Catch the change event of HEXA input field
	 */
	changeHexaField: function( element, newValue, oldValue ) {
		if(!Ext.isString(newValue)){
//			newValue = element.getValue();
			if(newValue.getKey() == newValue.ENTER){
				newValue = element.getValue();
			}else{
//				newValue.stopEvent();
				return;
			}
		}
		if( element == Ext.getCmp( 'colorValue' + this.el.id ) ) {
			if( newValue.length > 9 ) { newValue = newValue.substr(0,5); }
//			if( !newValue.match( /^[0-9a-f]{6}$/i ) ) { newValue = '000000'; }
			if( !newValue.match( /^[0-9a-f]{6}$/i ) ) return;
			this._HEX = newValue;
			this.updateColorsFromHexaField();
			this.updateColor();
			this.updatePickers();
			// fire the changehexa event
			this.fireEvent( 'changehexa', this, this._HEX );
		}
	},
	/**
	 *
	 */
	setColorFromWebsafe: function() {
		this.setColor( this.wsColorContainer.getColor( 'backgroundColor','','' ) );
	},
	/**
	 *
	 */
	setColorFromInvert: function() {
		this.setColor( this.inColorContainer.getColor( 'backgroundColor','','' ) );
	},
	/**
	 * Set initial color if config contains
	 * @private
	 */
	checkConfig: function() {
		if( this.config ) {
			if( this.config.color ) { this.setColor( this.config.color ); }
			else if( this.config.hsv ) { this.setHSV( this.config.hsv ); }
			else if( this.config.rgb ) { this.setRGB( this.config.rgb ); }
		}
	},

	// PUBLIC methods

	/**
	 * Change color with hexa value
	 * @param {String} hexa (eg.: 9A4D5F )
	 */
	setColor: function( hexa ) {
		var me = this;
		if(!Ext.isEmpty(hexa)){
			var temp = me.hexToRgb( hexa );
			me._RGB = { r:temp[0], g:temp[1], b:temp[2] }
			var temp = me.rgbToHsv( temp );
			me._HSV = { h:temp[0], s:temp[1], v:temp[2] };
		}
		if(me.rendered===true){
			try{
				me.updateColor();
				me.updatePickers();
			}catch(e){}
		}else{
			me.value = hexa;
		}
	},
	/**
	 * Change color with a RGB Object
	 * @param {Object} rgb (eg.: { r:255, g:200, b:111 })
	 */
	setRGB: function( rgb ) {
		this._RGB = rgb;
		var temp = this.rgbToHsv( rgb.r, rgb.g, rgb.b );
		this._HSV = { h: temp[0], s: temp[1], v: temp[2] };
		this.updateColor();
		this.updatePickers();
	},
	/**
	 * Change color with a HSV Object
	 * @param {Object} hsv (eg.: { h:359, s:10, v:100 })
	 */
	setHSV: function( hsv ) {
		this._HSV = { h: hsv.h, s: ( hsv.s / 100 ), v: ( hsv.v / 100 ) };
		var temp = this.hsvToRgb( hsv.h, ( hsv.s / 100 ), ( hsv.v / 100 ) );
		this._RGB = { r: temp[0], g: temp[1], b: temp[2] };
		this.updateColor();
		this.updatePickers();
	},
	/**
	 * Get the color from the internal store
	 * @param {Boolean} hash If it is true, the color prepended with '#'
	 * @return {String} hexa color format
	 */
	getColor: function( hash ) {
		var me = this;
		if(me.rendered===true){
			return ( hash ? '' : '#' ) + this._HEX;
		}else{
			return me.value;
		}
	},
	/**
	 * Get the color from the internal store in RGB object format
	 * @return {Object} format: { r: redvalue, g: greenvalue, b: bluevalue }
	 */
	getRGB: function() {
		return this._RGB;
	},
	/**
	 * Get the color from the internal store in HSV object format
	 * @return {Object} format: { h: huevalue, s: saturationvalue, v: brightnessvalue }
	 */
	getHSV: function() {
		return this._HSV;
	},
	/**
	 * Make input panel visible/hidden
	 * @param {Boolean} show Turns panel hidden or visible
	 * @param {Boolean/Object} animate Show/hide with animation or not
	 */
	setPanelVisible: function( show, animate ) {
		return this.formContainer.setVisible( show, animate );
	},
	/**
	 * Returns with boolean, input panel is visible or not
	 * @return {Boolean}
	 */
	isPanelVisible: function() {
		return this.formContainer.isDisplayed();
	},
	/**
	 * Make ColorPicker visible if it is not
	 * note: in ColorDialog it changed to the show method of BasicDialog
	 */
	showPicker: function() {
		this.show();
	},
	show: function() {//add tyamamot
		try{
			var me = this;
			me.el.show();
			if(me.zIndexParent && me.zIndexParent.el && me.zIndexParent.el.zindex){
				me.el.setStyle({zIndex:me.zIndexParent.el.zindex+1});
			}
		}catch(e){
			console.error(e);
		}
	},
	/**
	 * Make ColorPicker hidden if it is visible
	 * note: in ColorDialog it changed to the hide method of BasicDialog
	 */
	hidePicker: function() {
		this.hide();
	},
	hide: function() {//add tyamamot
		try{
			this.el.hide();
		}catch(e){
			console.error(e);
		}
	},

	onRender: function(ct, position) {
		var me = this;
		me.callParent(arguments);
		me.el.unselectable();
		var config = Ext.applyIf({},me.initialConfig);

		this.config = Ext.applyIf(this.config,config);
		this.config.captions = this.config.captions || {};
		this.config.pickerHotPoint = this.config.pickerHotPoint || { x:3, y:3 };
		this._HSV = { h: 0, s: 100, v: 100 };
		this._RGB = { r: 255, g: 255, b: 255 };
		this._HEX = '000000';
		this.lastXYRgb = { x: 0, y: 0 };
		this.lastYHue = 0;

		this.el.addCls('x-colorpickerpalette-panel x-layer x-unselectable');
		this.el.setStyle({
			width:this.config.width+'px',
			height:this.config.height+'px',
			border:'1px solid #8ba3c2',
			backgroundColor:'#dfe8f6'
		});
		this.cpCreateDomObjects();
		if( this.config.hidePanel ) { this.formContainer.hide(); }
		// initial color check
		this.checkConfig();

		if(!Ext.isEmpty(this.value)) this.setColor(this.value);
		if(me.rendered!==true) me.rendered = true;
	},
	initEvents: function(){
		var me = this;
		me.callParent();
		// init internal events
		me.rgbPicker.on( 'mousedown', me.rgbPickerClick, me );
		me.huePicker.on( 'mousedown', me.huePickerClick, me );
		me.wsColorContainer.on( 'mousedown', me.setColorFromWebsafe, me );
		me.inColorContainer.on( 'mousedown', me.setColorFromInvert, me );
		Ext.getCmp('redValue'        + me.el.id ).on('change', me.changeRGBField, me );
		Ext.getCmp('greenValue'      + me.el.id ).on('change', me.changeRGBField, me );
		Ext.getCmp('blueValue'       + me.el.id ).on('change', me.changeRGBField, me );
		Ext.getCmp('hueValue'        + me.el.id ).on('change', me.changeHSVField, me );
		Ext.getCmp('saturationValue' + me.el.id ).on('change', me.changeHSVField, me );
		Ext.getCmp('brightnessValue' + me.el.id ).on('change', me.changeHSVField, me );
		Ext.getCmp('colorValue'      + me.el.id ).on('change', me.changeHexaField, me );

		Ext.getCmp('redValue'        + me.el.id ).on('specialkey', me.changeRGBField, me );
		Ext.getCmp('greenValue'      + me.el.id ).on('specialkey', me.changeRGBField, me );
		Ext.getCmp('blueValue'       + me.el.id ).on('specialkey', me.changeRGBField, me );
		Ext.getCmp('hueValue'        + me.el.id ).on('specialkey', me.changeHSVField, me );
		Ext.getCmp('saturationValue' + me.el.id ).on('specialkey', me.changeHSVField, me );
		Ext.getCmp('brightnessValue' + me.el.id ).on('specialkey', me.changeHSVField, me );
		Ext.getCmp('colorValue'      + me.el.id ).on('specialkey', me.changeHexaField, me );
	}
});
