Ext.define('Ag.Component', {
	override: 'Ag.Main',

	getObjDataSelection : function(datas){
		var self = this;
		datas = datas || [];
		var select_datas = Ext.Array.filter(datas, function(data){
			if(Ext.isObject(data) && Ext.isBoolean(data[ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ])) return data[ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ];
			return false;
		});
		return select_datas;
	},

	_createRenderTopDocked : function(config,getObjDatasFunction,getParentPanelFunction){
		var self = this;

		var _drawCanvasGrid = function(panel){
			var renderer = panel.__webglMainRenderer;
			var use_flag = self.DEF_RENDERER_GRID_USE;
			if(use_flag){
				var size      = self.DEF_RENDERER_GRID_SIZE;
				var divisions = self.DEF_RENDERER_GRID_DIVISIONS;
				var color1    = self.DEF_RENDERER_GRID_COLOR;
				var color2    = self.DEF_RENDERER_GRID_COLOR;

				if(color1.substr(0,1) == '#') color1 = color1.substr(1);
				if(color2.substr(0,1) == '#') color2 = color2.substr(1);
				color1 = parseInt(color1,16);
				color2 = parseInt(color2,16);

				renderer.setGrid({
					size:  Ext.isEmpty(size)           ? 10 : size - 0,
					divisions:  Ext.isEmpty(divisions) ? 10 : divisions - 0,
					color1:  Ext.isEmpty(color1)       ? 0x008000 : color1 - 0,
					color2:  Ext.isEmpty(color2)       ? 0x008000 : color2 - 0
				});
			}else{
				renderer.clearGrid();
			}
		};

		return Ext.apply({
			xtype: 'toolbar',
			dock: 'top',
			itemId: 'top',
			items: [{
				xtype: 'numberfield',
				labelWidth: 10,
				width: 74,
				name: 'longitude',
				itemId: 'longitude',
				fieldLabel: 'H',
				allowBlank:false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
				selectOnFocus: false,
				step: 1,
				value: 0,
				maxValue: 359,
				minValue: 0,
				validator: function(){
					var value = Math.round(this.value/this.step)*this.step;
					if(value > this.maxValue) value -= (this.maxValue+this.step);
					if(value < this.minValue) value += (this.maxValue+this.step);
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						var panel = field.up('panel');
						if(panel.__webglMainRenderer){
//							console.log('change',newValue);
							panel.__webglMainRenderer.setHorizontal(newValue);
							if(panel.__webglSubRenderer) panel.__webglSubRenderer.setHorizontal(newValue);
						}
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
				labelWidth: 10,
				width: 74,
				name: 'latitude',
				itemId: 'latitude',
				fieldLabel: 'V',
				allowBlank:false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
				selectOnFocus: false,
				step: 1,
				value: 0,
				maxValue: 359,
				minValue: 0,
				validator: function(){
					var value = Math.round(this.value/this.step)*this.step;
					if(value > this.maxValue) value -= (this.maxValue+this.step);
					if(value < this.minValue) value += (this.maxValue+this.step);
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						var panel = field.up('panel');
						if(panel.__webglMainRenderer){
							panel.__webglMainRenderer.setVertical(newValue);
							if(panel.__webglSubRenderer) panel.__webglSubRenderer.setVertical(newValue);
						}
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
				labelWidth: 34,
				width: 98,
				name: 'zoom',
				itemId: 'zoom',
				fieldLabel: 'Zoom',
				allowBlank:false,
				allowDecimals: false,
				keyNavEnabled: false,
				mouseWheelEnabled: false,
				selectOnFocus: false,
				value: 1,
				maxValue: 100,
				minValue: 1,
				validator: function(){
					var value = Math.round(this.value);
					if(value > this.maxValue) value = this.maxValue;
					if(value < this.minValue) value = this.minValue;
					if(value != this.value) Ext.defer(function(){ this.setValue(value); },50,this);
					return true;
				},
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						var panel = field.up('panel');
						if(panel.__webglMainRenderer){
							panel.__webglMainRenderer.setDispZoom(newValue);
						}
					},
					specialkey: function(field, e, eOpts){
						e.stopPropagation();
					}
				}
			},{xtype: 'tbfill'},{

				hidden: false,
				xtype: 'button',
				iconCls: 'gear-btn',
				tooltip: 'Options [ Renderer ]',

				handler: function(button,e){
					var panel = button.up('panel');

					var _drawCanvasClip = function(canvas_clip_panel){
						var renderer = panel.__webglMainRenderer;
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
					};

					if(Ext.isEmpty(panel.__webglMainRendererOptionsWindow)){

						var rendererOptionsWindowConfig = {};
						var rendererOptionsWindowConstrain = null;
						if(Ext.isFunction(getParentPanelFunction)){
							rendererOptionsWindowConstrain = getParentPanelFunction();
							rendererOptionsWindowConfig.constrain = true;
							rendererOptionsWindowConfig.constrainTo = rendererOptionsWindowConstrain.body;
						}else{
							rendererOptionsWindowConfig.constrain = false;
							rendererOptionsWindowConfig.constrainTo = null;
						}

						panel.__webglMainRendererOptionsWindow = Ext.create('Ext.window.Window',Ext.apply({
							title: button.tooltip || button.text,
							iconCls: button.iconCls,
//							height: 314,
//							height: 360,
							height: 400,
//								width: 230,
//							width: 234,
							width: 304,
							layout: 'fit',
							items: {
								xtype: 'tabpanel',
								defaults: {
									bodyPadding: '2 5 2 5'
								},
								items: [{
									title: 'Select parts',
									layout: {
										type: 'vbox',
										align: 'stretch'
									},
									defaultType:'fieldset',
									defaults: {
									},
									items: [
									{
										hidden: true,
										title: 'Selected parts',
										defaultType: 'fieldcontainer',
										defaults: {
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Color',
												checked: self.USE_SELECTION_RENDERER_PICKED_COLOR,
												handler: function(checkboxfield, checked){
													var label = checkboxfield.next('agcolordisplayfield');
													var button = checkboxfield.next('button');
													label.setVisible(checked);
													button.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_COLOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();

												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_COLOR,
												xtype: 'agcolordisplayfield',
												margin: '0 5px 0 0',
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_COLOR) ? 'transparent' : self.DEF_SELECTION_RENDERER_PICKED_COLOR
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_COLOR,
												xtype: 'button',
												iconCls: 'color_pallet',
												menu: Ext.create('Ext.menu.ColorPicker', {
													hideOnClick: false,
													listeners: {
														select: function( colormenu, color, eOpts ){
															self.DEF_SELECTION_RENDERER_PICKED_COLOR = '#'+color;
															var button = colormenu.up('button');
															button.prev('agcolordisplayfield').setValue(self.DEF_SELECTION_RENDERER_PICKED_COLOR);

															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();

														},
														show: function( colormenu, eOpts ){
															var color = Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_COLOR) ? 'transparent' : self.DEF_SELECTION_RENDERER_PICKED_COLOR;
															if(color.substr(0,1) == '#') color = color.substr(1);
															colormenu.picker.select(color,true);
														}
													}
												})
											}]
										},{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Factor',
												margin: '0 5px 0 0',
												checked: self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR,
												handler: function(checkboxfield, checked){
													var numberfield = checkboxfield.next('numberfield');
													numberfield.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();
												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR,
												xtype: 'numberfield',
												width: 60,
												allowBlank: false,
												allowDecimals: true,
												keyNavEnabled: false,
												mouseWheelEnabled: false,
												selectOnFocus: false,
												step: 0.1,
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR) ? 0 : self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR,
												maxValue: 2,
												minValue: -2,
												listeners: {
													change: function(numberfield, value){
														self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR = value;

														Ext.defer(function(){
															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();
														},500);

													}
												}
											}]
										}]
									}

									,{
										title: 'Parts selected by pick',
										defaultType: 'fieldcontainer',
										defaults: {
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											xtype: 'checkboxfield',
											boxLabel: 'Wireframe',
											margin: '0 5px 0 0',
											checked: self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_WIREFRAME,
											handler: function(checkboxfield, checked){
												self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_WIREFRAME = checked;

												if(panel.__webglMainRenderer){
													var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
													var select_datas = self.getObjDataSelection(datas);
													if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
												}
												self.saveRendererOptions();
											}
										},{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Color',
												checked: self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR,
												handler: function(checkboxfield, checked){
													var label = checkboxfield.next('agcolordisplayfield');
													var button = checkboxfield.next('button');
													label.setVisible(checked);
													button.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();

												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR,
												xtype: 'agcolordisplayfield',
												margin: '0 5px 0 0',
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR) ? 'transparent' : self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR,
												xtype: 'button',
												iconCls: 'color_pallet',
												menu: Ext.create('Ext.menu.ColorPicker', {
													hideOnClick: false,
													listeners: {
														select: function( colormenu, color, eOpts ){
															self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR = '#'+color;
															var button = colormenu.up('button');
															button.prev('agcolordisplayfield').setValue(self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR);

															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();

														},
														show: function( colormenu, eOpts ){
															var color = Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR) ? 'transparent' : self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR;
															if(color.substr(0,1) == '#') color = color.substr(1);
															colormenu.picker.select(color,true);
														}
													}
												})
											}]
										},{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Factor',
												margin: '0 5px 0 0',
												checked: self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR,
												handler: function(checkboxfield, checked){
													var numberfield = checkboxfield.next('numberfield');
													numberfield.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();
												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR,
												xtype: 'numberfield',
												width: 60,
												allowBlank: false,
												allowDecimals: true,
												keyNavEnabled: false,
												mouseWheelEnabled: false,
												selectOnFocus: false,
												step: 0.1,
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR) ? 0 : self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR,
												maxValue: 2,
												minValue: -2,
												listeners: {
													change: function(numberfield, value){
														self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR = value;

														Ext.defer(function(){
															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();
														},500);

													}
												}
											}]
										}]
									}

									,{
										title: 'Parts selected by tag',
										defaultType: 'fieldcontainer',
										defaults: {
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											xtype: 'checkboxfield',
											boxLabel: 'Wireframe',
											margin: '0 5px 0 0',
											checked: self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_WIREFRAME,
											handler: function(checkboxfield, checked){
												self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_WIREFRAME = checked;

												if(panel.__webglMainRenderer){
													var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
													var select_datas = self.getObjDataSelection(datas);
													if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
												}
												self.saveRendererOptions();
											}
										},{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Color',
												checked: self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR,
												handler: function(checkboxfield, checked){
													var label = checkboxfield.next('agcolordisplayfield');
													var button = checkboxfield.next('button');
													label.setVisible(checked);
													button.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();

												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR,
												xtype: 'agcolordisplayfield',
												margin: '0 5px 0 0',
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR) ? 'transparent' : self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR,
												xtype: 'button',
												iconCls: 'color_pallet',
												menu: Ext.create('Ext.menu.ColorPicker', {
													hideOnClick: false,
													listeners: {
														select: function( colormenu, color, eOpts ){
															self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR = '#'+color;
															var button = colormenu.up('button');
															button.prev('agcolordisplayfield').setValue(self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR);

															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();

														},
														show: function( colormenu, eOpts ){
															var color = Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR) ? 'transparent' : self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR;
															if(color.substr(0,1) == '#') color = color.substr(1);
															colormenu.picker.select(color,true);
														}
													}
												})
											}]
										},{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Factor',
												margin: '0 5px 0 0',
												checked: self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR,
												handler: function(checkboxfield, checked){
													var numberfield = checkboxfield.next('numberfield');
													numberfield.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();
												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR,
												xtype: 'numberfield',
												width: 60,
												allowBlank: false,
												allowDecimals: true,
												keyNavEnabled: false,
												mouseWheelEnabled: false,
												selectOnFocus: false,
												step: 0.1,
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR) ? 0 : self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR,
												maxValue: 2,
												minValue: -2,
												listeners: {
													change: function(numberfield, value){
														self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR = value;

														Ext.defer(function(){
															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();
														},500);

													}
												}
											}]
										}]
									}



									,{
										title: 'Unselected parts',
										defaultType: 'fieldcontainer',
										defaults: {
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Opacity',
												margin: '0 5px 0 0',
												checked: self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY,
												handler: function(checkboxfield, checked){
													var numberfield = checkboxfield.next('numberfield');
													numberfield.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();
												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY,
												xtype: 'numberfield',
												width: 60,
												allowBlank: false,
												allowDecimals: true,
												keyNavEnabled: false,
												mouseWheelEnabled: false,
												selectOnFocus: false,
												step: 0.1,
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY) ? 1 : self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY,
												maxValue: 1,
												minValue: 0,
												listeners: {
													change: function(numberfield, value){
														self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY = value;

														Ext.defer(function(){
															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();
														},500);

													}
												}
											}]
										},{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Factor',
												margin: '0 5px 0 0',
												checked: self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR,
												handler: function(checkboxfield, checked){
													var numberfield = checkboxfield.next('numberfield');
													numberfield.setVisible(checked);
													self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR = checked;

													if(panel.__webglMainRenderer){
														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
													}
													self.saveRendererOptions();
												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR,
												xtype: 'numberfield',
												width: 60,
												allowBlank: false,
												allowDecimals: true,
												keyNavEnabled: false,
												mouseWheelEnabled: false,
												selectOnFocus: false,
												step: 0.1,
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR) ? 0 : self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR,
												maxValue: 2,
												minValue: -2,
												listeners: {
													change: function(numberfield, value){
														self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR = value;

														Ext.defer(function(){
															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(select_datas.length) panel.__webglMainRenderer.setObjProperties(datas);
															}
															self.saveRendererOptions();
														},500);

													}
												}
											}]
										}]
									},{
										title: 'Background when selecting parts',
										defaultType: 'fieldcontainer',
										defaults: {
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											items: [{
												xtype: 'checkboxfield',
												boxLabel: 'Factor',
												margin: '0 5px 0 0',
												checked: self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR,
												handler: function(checkboxfield, checked){
													var numberfield = checkboxfield.next('numberfield');
													numberfield.setVisible(checked);
													self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR = checked;

													if(panel.__webglMainRenderer){

														var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
														var select_datas = self.getObjDataSelection(datas);
														if(self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR && select_datas.length){
															panel.__webglMainRenderer.setBackgroundColor(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR);
														}else{
															panel.__webglMainRenderer.setBackgroundColor(self.DEF_RENDERER_BACKGROUND_COLOR);
														}

													}
													self.saveRendererOptions();
												}
											},{
												hidden: !self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR,
												xtype: 'numberfield',
												width: 60,
												allowBlank: false,
												allowDecimals: true,
												keyNavEnabled: false,
												mouseWheelEnabled: false,
												selectOnFocus: false,
												step: 0.1,
												value: Ext.isEmpty(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR) ? 0 : self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR,
												maxValue: 2,
												minValue: -2,
												listeners: {
													change: function(numberfield, value){
														self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR = value;

														Ext.defer(function(){
															if(panel.__webglMainRenderer){

																var rgb = d3.rgb( self.DEF_RENDERER_BACKGROUND_COLOR );
																if(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR>0){
																	self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = rgb.brighter(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR).toString();
																}
																else if(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR<0){
																	self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = rgb.darker(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR*-1).toString();
																}

																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR && select_datas.length){
																	panel.__webglMainRenderer.setBackgroundColor(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR);
																}else{
																	panel.__webglMainRenderer.setBackgroundColor(self.DEF_RENDERER_BACKGROUND_COLOR);
																}

															}
															self.saveRendererOptions();
														},500);

													}
												}
											}]
										}]
									}]
								},{
									title: 'Genaral',
									layout: {
										type: 'vbox',
										align: 'stretch'
									},
									defaultType:'fieldset',
									defaults: {
									},
									items: [{
										title: 'Background',
										defaultType: 'fieldcontainer',
										defaults: {
											labelAlign: 'right',
											labelWidth: 30,
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											fieldLabel: 'Color',
											items: [{
												xtype: 'agcolordisplayfield',
												margin: '0 5px 0 0',
												value: Ext.isEmpty(self.DEF_RENDERER_BACKGROUND_COLOR) ? '#FFFFFF' : self.DEF_RENDERER_BACKGROUND_COLOR
											},{
												xtype: 'button',
												iconCls: 'color_pallet',
												menu: Ext.create('Ext.menu.ColorPicker', {
													hideOnClick: false,
													listeners: {
														select: function( colormenu, color, eOpts ){
															self.DEF_RENDERER_BACKGROUND_COLOR = '#'+color;
															var button = colormenu.up('button');
															button.prev('agcolordisplayfield').setValue(self.DEF_RENDERER_BACKGROUND_COLOR);

															var rgb = d3.rgb( self.DEF_RENDERER_BACKGROUND_COLOR );
															if(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR>0){
																self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = rgb.brighter(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR).toString();
															}
															else if(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR<0){
																self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR = rgb.darker(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR*-1).toString();
															}

															if(panel.__webglMainRenderer){
																var datas = Ext.isFunction(getObjDatasFunction) ? getObjDatasFunction() : [];
																var select_datas = self.getObjDataSelection(datas);
																if(self.USE_SELECTION_RENDERER_BACKGROUND_COLOR_FACTOR && select_datas.length){
																	panel.__webglMainRenderer.setBackgroundColor(self.DEF_SELECTION_RENDERER_BACKGROUND_COLOR);
																}else{
																	panel.__webglMainRenderer.setBackgroundColor(self.DEF_RENDERER_BACKGROUND_COLOR);
																}
															}
															self.saveRendererOptions();

														},
														show: function( colormenu, eOpts ){
															var color = Ext.isEmpty(self.DEF_RENDERER_BACKGROUND_COLOR) ? '#FFFFFF' : self.DEF_RENDERER_BACKGROUND_COLOR;
															if(color.substr(0,1) == '#') color = color.substr(1);
															colormenu.picker.select(color,true);
														}
													}
												})
											}]
										}]
									},{
										hidden: true,
										title: 'Clip',
										itemId: 'clip',
//										checkboxToggle: true,
//										collapsed: false,
//										collapsible: false,
//										listeners: {
//											beforecollapse: function( fieldset, eOpts ){
//												return false;
//											}
//										},
										padding: '0 0 0 0',
										defaultType: 'fieldcontainer',
										defaults: {
											labelAlign: 'right',
											labelWidth: 62,
//											hideLabel: true,
										},
										items: [{
											xtype: 'checkboxfield',
											itemId: 'use',
											boxLabel: 'Use',
											checked: false,
											margin: '0 0 0 4',
											listeners: {
												change: function( field, newValue, oldValue, eOpts ){
													_drawCanvasClip(field.up('fieldset#clip'));
												}
											}

										},{
											layout:'column',
//											columnWidth: 0.33,
											defaultType: 'numberfield',
											defaults: {
												labelAlign: 'right',
												labelWidth: 20,
												columnWidth: 0.33,
												anchor: '100%',
												allowBlank: false,
												allowDecimals: true,
												allowExponential: true,
												allowOnlyWhitespace: false,
												step: 0.01,
//												maxValue:  1,
//												minValue: -1,
												value: 0,
												listeners: {
													change: function( field, newValue, oldValue, eOpts ){
														_drawCanvasClip(field.up('fieldset#clip'));
													}
												}
											},
											items: [{
												fieldLabel: 'X',
												itemId: 'x',
												value: 1
											},{
												fieldLabel: 'Y',
												itemId: 'y'
											},{
												fieldLabel: 'Z',
												itemId: 'z'
											}]
										},{
											xtype: 'numberfield',
											fieldLabel: 'Constant',
											itemId: 'constant',
											width: 130,
											allowBlank: false,
											allowDecimals: true,
											allowExponential: true,
											allowOnlyWhitespace: false,
											maxValue:  1800,
											minValue: -1800,
											value: 0,
											listeners: {
												change: function( field, newValue, oldValue, eOpts ){
													_drawCanvasClip(field.up('fieldset#clip'));
												}
											}
										}]
									},{
										hidden: true,
										title: 'Grid',
										itemId: 'grid',
										padding: '0 0 0 0',
										defaultType: 'fieldcontainer',
										defaults: {
											labelAlign: 'right',
											labelWidth: 40,
											layout: {
												type: 'hbox',
												align: 'middle',
												pack: 'start'
											},
										},
										items: [{
											xtype: 'checkboxfield',
											itemId: 'use',
											boxLabel: 'Use',
											checked: Ext.isEmpty(self.DEF_RENDERER_GRID_USE) ? false : (self.DEF_RENDERER_GRID_USE ? true : false),
											margin: '0 0 0 4',
											listeners: {
												afterrender: function(field){
//													console.log(field.getValue());
												},
												change: function( field, newValue, oldValue, eOpts ){
													self.DEF_RENDERER_GRID_USE = newValue;
													_drawCanvasGrid(panel);
													self.saveRendererOptions();
												}
											}
										},{
											fieldLabel: 'Color',
											items: [{
												xtype: 'agcolordisplayfield',
												margin: '0 5px 0 0',
												value: Ext.isEmpty(self.DEF_RENDERER_GRID_COLOR) ? '#00FF00' : self.DEF_RENDERER_GRID_COLOR,
												listeners: {
													afterrender: function(field){
//														console.log(field.getValue());
													}
												}
											},{
												xtype: 'button',
												iconCls: 'color_pallet',
												menu: Ext.create('Ext.menu.ColorPicker', {
													hideOnClick: false,
													listeners: {
														select: function( colormenu, color, eOpts ){
															self.DEF_RENDERER_GRID_COLOR = '#'+color;
															var button = colormenu.up('button');
															button.prev('agcolordisplayfield').setValue(self.DEF_RENDERER_GRID_COLOR);
															_drawCanvasGrid(panel);
															self.saveRendererOptions();
														},
														show: function( colormenu, eOpts ){
															var color = Ext.isEmpty(self.DEF_RENDERER_GRID_COLOR) ? '#00FF00' : self.DEF_RENDERER_GRID_COLOR;
															if(color.substr(0,1) == '#') color = color.substr(1);
															colormenu.picker.select(color,true);
														}
													}
												})
											}]
										},{
											xtype: 'hiddenfield',
											itemId: 'size',
											value: Ext.isEmpty(self.DEF_RENDERER_GRID_SIZE) ? 1800 : self.DEF_RENDERER_GRID_SIZE,
										},{
											xtype: 'hiddenfield',
											itemId: 'divisions',
											value: Ext.isEmpty(self.DEF_RENDERER_GRID_DIVISIONS) ? 10 : self.DEF_RENDERER_GRID_DIVISIONS,
										},{
											xtype: 'numberfield',
											fieldLabel: 'Size',
											width: 130,
											allowBlank: false,
											allowDecimals: true,
											allowExponential: true,
											allowOnlyWhitespace: false,
											maxValue: 100,
											minValue:   1,
											value: 10,
											listeners: {
												afterrender: function(field){
													if(Ext.isEmpty(self.DEF_RENDERER_GRID_SIZE)) self.DEF_RENDERER_GRID_SIZE = field.prev('hiddenfield#size').getValue() - 0;
													self.DEF_RENDERER_GRID_DIVISIONS = Math.floor(self.DEF_RENDERER_GRID_SIZE/(field.getValue()-0));
													field.prev('hiddenfield#divisions').setValue(self.DEF_RENDERER_GRID_DIVISIONS);
													self.saveRendererOptions();
												},
												change: function( field, newValue, oldValue, eOpts ){
													self.DEF_RENDERER_GRID_DIVISIONS = Math.floor(self.DEF_RENDERER_GRID_SIZE/(newValue-0));
													field.prev('hiddenfield#divisions').setValue(self.DEF_RENDERER_GRID_DIVISIONS);
													_drawCanvasGrid(panel);
													self.saveRendererOptions();
												}
											}
										}]
									}]
								}]
							},
							listeners: {
								close: function( comp, eOpts ){
									if(rendererOptionsWindowConstrain) rendererOptionsWindowConstrain.remove(panel.__webglMainRendererOptionsWindow);
								},
								destroy: function( comp, eOpts ){
									delete panel.__webglMainRendererOptionsWindow;
								}
							}
						},rendererOptionsWindowConfig||{}));
						if(rendererOptionsWindowConstrain) rendererOptionsWindowConstrain.add(panel.__webglMainRendererOptionsWindow);
						panel.__webglMainRendererOptionsWindow.showBy(button);
					}else{
						panel.__webglMainRendererOptionsWindow.show();
					}
				}
			}],
			listeners: {
				afterrender: function(toolbar){
					if(config.hidden) return;
					var panel = toolbar.up('panel');
					panel.on('afterrender', function(panel){
						_drawCanvasGrid(panel);
					},self,{single:true});
				}
			}
		},config||{});
	},

	_createViewport : function(){
		var self = this;

		var segment_store = Ext.data.StoreManager.lookup('segment-list-store');
		var segment_grid_store = Ext.data.StoreManager.lookup('segment-grid-store');

		var version_store = Ext.data.StoreManager.lookup('version-store');
		var record = null;

		var version_display = Ext.state.Manager.get('version-combobox-display',null);

		let urlparams_hash = {};
		let url = new URL(window.location.href);
		let searchParams = url.searchParams;
		if(searchParams.size>0){
			for(const [name, value] of searchParams.entries()){
				let lname = name.toLowerCase();
				if(Ext.isEmpty(urlparams_hash[lname])) urlparams_hash[lname] = [];
				urlparams_hash[lname].push(value);
			}
			let params_version = 'latest';
			if(Ext.isArray(urlparams_hash['version']) && urlparams_hash['version'].length>0){
				params_version = urlparams_hash['version'][0];
			}
			if(params_version=='latest'){
				record = version_store.last();
				version_display = record.get('display');
			}
			else{
				version_display = params_version;
			}
		}

		if(Ext.isEmpty(version_display) && Ag.Def.DEF_MODEL_VERSION_TERM) version_display = Ag.Def.DEF_MODEL_VERSION_TERM;
		if(Ext.isString(version_display) && version_display.length) record = version_store.findRecord('display',version_display,0,false,false,true);
		var version_display = null;
		var version_value = null;
		if(record){
			version_display = record.get('display');
			version_value = record.get('value');
			self.DEF_MODEL_VERSION_RECORD = record;
		}else{
			record = version_store.last();
			version_display = record.get('display');
			version_value = record.get('value');
			self.DEF_MODEL_VERSION_RECORD = version_store.last();
		}

		var search_store = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_TERM_SEARCH_STORE_ID);
		var match_list_store = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
		var pallet_store = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_TERM_STORE_ID);
		var cities_store = Ext.data.StoreManager.lookup('cities-list-store');

		var renderer_dataIndex_suffix = '';

		var center_width = Ext.getBody().getWidth();
		var class_row_selected = 'bp3d-grid-data-row-selected';
		var class_word_button_selected = 'bp3d-word-button-selected';

		var make_ag_word = function(value,dataIndex,tooltip,className,baseClassName,isSelected){
			if(Ext.isEmpty(tooltip)) tooltip = value;
			if(Ext.isEmpty(className)) className = 'bp3d-word';
			if(Ext.isEmpty(baseClassName)) baseClassName = 'bp3d-word-button';
//			var replace_array_value = (className==='bp3d-category' || className==='bp3d-segment') ? [value.trim()] : value.replace(/([^a-z0-9\s]+)/ig,' $1 ').trim().split(/\s+/);
//			var replace_array_value = (className==='bp3d-category' || className==='bp3d-segment' || className==='bp3d-relation') ? [value.trim()] : value.replace(/([^a-z0-9\s]+)/ig,' $1 ').trim().split(/\s+/);
			var replace_array_value = [value.trim()];
			var selected_values;
			if(Ext.isObject(isSelected)){
				selected_values = [];
				if(Ext.isArray(isSelected.value)){
					if(Ext.isString(isSelected.dataIndex)){
						if(isSelected.dataIndex===dataIndex) selected_values = Ext.Array.clone(isSelected.value);
					}
					else if(Ext.isArray(isSelected.dataIndex)){
						Ext.Array.each(isSelected.dataIndex, function(d){
							if(d===dataIndex) selected_values = Ext.Array.clone(isSelected.value);
						});
					}
				}
				isSelected = selected_values.length>0 ? true : false;
			}
			else if(Ext.isArray(isSelected)){
//				selected_values = isSelected.concat([]);
				selected_values = [];
//				Ext.Array.each(isSelected, function(v){
//					Ext.Array.each(v.replace(/([^a-z0-9\s]+)/ig,' $1 ').trim().split(/\s+/), function(v2){
//						selected_values.push(v2);
//					});
//				});
				selected_values = Ext.Array.clone(isSelected);
				isSelected = selected_values.length>0 ? true : false;
			}
			else{
				isSelected = isSelected===true;
			}
			return Ext.util.Format.format(
				'<div class="bp3d-term" data-qtip="{0}">{1}</div>',Ext.String.htmlEncode(tooltip),
				Ext.Array.map(
					replace_array_value,
					function(str){
//						if(Ext.isString(str) && str.length && str.match(/[a-z0-9]+/i)){
						if(Ext.isString(str) && str.length){
							var isSel = false;
							if(Ext.isArray(selected_values) && selected_values.length && isSelected){
//								isSel = Ext.Array.contains(selected_values, str.toLowerCase());
								isSel = Ext.Array.contains(selected_values, str);
							}
							else{
								isSel = isSelected;
							}
							return Ext.util.Format.format(
								'<a href="#" class="{0} {1}" data-value="{2}" data-dataIndex="{3}" style="{4}">{5}</a>'
								,baseClassName
								,className
//								,str.toLowerCase()
								,Ext.String.htmlEncode(str)
								,Ext.String.htmlEncode(dataIndex)
								,(isSel ? 'box-shadow:0px 0px 0px 3px '+self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR : '')
								,str
							);
						}
						else{
							return str;
						}
					}
				).join(' ')
			);
		};

		var relation_column_renderer = function(value, metaData, record, rowIdx, colIndex, store, view) {
			if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
			var rtn = '';
			metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-relation';
			if(Ext.isString(value) && value.length){
				rtn = Ext.util.Format.nl2br(value.replace(/(.*)FMA([0-9]+)(.+)/g,'$1$2$3'));
				metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
			}
			else if(Ext.isArray(value) && value.length){
				var dataIndex = view.getGridColumns()[colIndex].dataIndex;

				var selected_tag = record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID);
				//					return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));

				var rtn = [];
				Ext.Array.each(value, function(v,i){
					if(Ext.isString(v) && v.length){
						rtn.push(make_ag_word(v,dataIndex,null,'bp3d-relation',null,selected_tag));
					}
					else if(Ext.isObject(v) && Ext.isString(v[Ag.Def.NAME_DATA_FIELD_ID]) && v[Ag.Def.NAME_DATA_FIELD_ID].length){
						rtn.push(make_ag_word(v[Ag.Def.NAME_DATA_FIELD_ID],dataIndex,Ext.util.Format.format('{0} : {1}',v['id'],v[Ag.Def.NAME_DATA_FIELD_ID]),'bp3d-relation',null,selected_tag));
					}
				});
				return rtn.join('');
			}
			return rtn;
		};
		var get_relation_column = function(dataIndex, text, hidden){
			if(Ext.isBoolean(text)){
				hidden = text;
				text = dataIndex;
			}
			if(Ext.isEmpty(text)) text = dataIndex;
			return {
				text: text,
				tooltip: text,
				dataIndex: dataIndex,
				flex: 1,
				hidden: hidden,
				hideable: !hidden,//true,
				lockable: false,
				draggable: false,
				renderer: relation_column_renderer
			};
		};

		var findRecords = self._findRecords = function(store,fieldName,value,scope,options){
			if(Ext.isEmpty(options)) options = {};
			var records = [];
			if(Ext.isArray(value) || Ext.isPrimitive(value)){
				if(!Ext.isArray(value)) value = [value];
				var index=0;
				var re_value_arr = null;
				if(fieldName===Ag.Def.NAME_DATA_FIELD_ID){
					re_value_arr = Ext.Array.map(value, function(v){ return new RegExp("\\b"+v+"\\b","i");});
				}
				while((index = store.findBy(function(record,record_id){
					var fieldValue = record.get(fieldName);
					var rtn = false;
					if(fieldName===Ag.Def.NAME_DATA_FIELD_ID){
						Ext.Array.each(re_value_arr, function(re_value){
							rtn = re_value.test(fieldValue);
							return rtn ? false : true;
						});
						return rtn===true;
					}
					else if(Ext.isArray(fieldValue)){
						Ext.Array.each(fieldValue,function(fv){
							Ext.Array.each(value, function(v){
								rtn = (Ext.isNumeric(fv)?parseFloat(fv):fv)===(Ext.isNumeric(v)?parseFloat(v):v);
								return rtn ? false : true;
							});
							return rtn ? false : true;
						});
						return rtn===true;
					}
					else{
						Ext.Array.each(value, function(v){
							rtn = (Ext.isNumeric(fieldValue)?parseFloat(fieldValue):fieldValue)===(Ext.isNumeric(v)?parseFloat(v):v);
							return rtn ? false : true;
						});
						return rtn===true;
					}
				},scope, index))>=0){
					var record = store.getAt(index);
					index++;
					if(record) records.push(record);
				}
			}
			return records;
		};

		var findWordRecords = self._findWordRecords = function(store,fieldName,value,scope,options){
			if(Ext.isEmpty(options)) options = {};
			var records = [];
			if(Ext.isArray(value) || Ext.isPrimitive(value)){
				if(!Ext.isArray(value)) value = [value];
				var index=0;
				var re_value_arr = null;
//				if(fieldName===Ag.Def.NAME_DATA_FIELD_ID){
//					re_value_arr = Ext.Array.map(value, function(v){ return new RegExp("\\b"+v+"\\b","i");});
//				}
				re_value_arr = Ext.Array.map(value, function(v){ return new RegExp("^"+v+"$","i");});

				var fn2 = function(record,fieldName){
					var fieldValue = record.get(fieldName);
					var rtn = 0;
					if(fieldName===Ag.Def.NAME_DATA_FIELD_ID){
						Ext.Array.each(re_value_arr, function(re_value){
							if(re_value.test(fieldValue)) rtn++;
							return rtn>0 ? false : true;
						});
						return rtn>0;
					}
					else if(Ext.isArray(fieldValue) && (fieldName==='is_a' || fieldName==='part_of' || fieldName==='lexicalsuper')){
						Ext.Array.each(fieldValue,function(fv){
							Ext.Array.each(value, function(v){
								if((Ext.isNumeric(fv[Ag.Def.NAME_DATA_FIELD_ID])?parseFloat(fv[Ag.Def.NAME_DATA_FIELD_ID]):fv[Ag.Def.NAME_DATA_FIELD_ID])===(Ext.isNumeric(v)?parseFloat(v):v)) rtn++;
								return rtn>0 ? false : true;
							});
							return rtn>0 ? false : true;
						});
						return rtn>0;
					}
					else if(Ext.isArray(fieldValue)){
						Ext.Array.each(fieldValue,function(fv){
							Ext.Array.each(value, function(v){
								if((Ext.isNumeric(fv)?parseFloat(fv):fv)===(Ext.isNumeric(v)?parseFloat(v):v)) rtn++;
								return rtn>0 ? false : true;
							});
							return rtn>0 ? false : true;
						});
						return rtn>0;
					}
					else{
						Ext.Array.each(value, function(v){
							if((Ext.isNumeric(fieldValue)?parseFloat(fieldValue):fieldValue)===(Ext.isNumeric(v)?parseFloat(v):v)) rtn++;
							return rtn>0 ? false : true;
						});
						return rtn>0;
					}
				};
				var fn = function(record,record_id){
					if(Ext.isEmpty(fieldName)){
						var rtn = false;
						Ext.Object.each(record.getData(), function(key){
							rtn = fn2(record,key);
//							if(rtn) console.log(key,rtn);
							return rtn ? false : true;
						});
						return rtn;
					}
					else{
						return fn2(record,fieldName);
					}
				};

				while((index = store.findBy(fn, scope, index))>=0){
					var record = store.getAt(index);
					index++;
					if(record){
						if(Ext.isFunction(options.callback)){
							Ext.callback(options.callback,self,[store,fieldName,value,re_value_arr,record]);
						}
						records.push(record);
					}
				}
			}
			return records;
		};

		var clearPickedInfoRecord = self._clearPickedInfoRecord = function(record,silent){
			silent = silent === true;
			if(record){
//				console.trace('clearPickedInfoRecord()',record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
				record.beginEdit();
				record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,false);
				record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,null);
				record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,0);
				record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
				record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,false);
				record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,null);
				record.set(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,null);
				record.set(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,false);
				record.commit(silent,[
					Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,
					Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID
				]);
			}
		};

		var render_dockedItems = [self._createRenderTopDocked({})];
		var segment_render_dockedItems = [
			self._createRenderTopDocked({hidden:true,dock:'bottom'})
		];

		var get_match_list_gridpanel_top_toolbar = function(){
			return Ext.create('Ext.toolbar.Toolbar', {
				hidden: true,
				dock: 'top',
				minHeight: 29,
				items: [{
					hidden: true,
					xtype: 'tbtext',
					text: ' ',
					style:{'cursor':'default','user-select':'none'}
				},{
					xtype: 'tbtext',
					style:{'cursor':'default','user-select':'none'},
					listeners: {
						afterrender: function(field){
							var viewport = Ext.getCmp('main-viewport');
							var window_panel = viewport.down('panel#window-panel');
//							var window_panel_toolbar = window_panel.getDockedItems('toolbar[dock="top"]')[0];
							var window_panel_toolbar = window_panel.down('panel#north-panel');

							var version_combobox = window_panel_toolbar.down('combobox#version-combobox');
							var segment_treepicker = window_panel_toolbar.down('treepicker#segment-treepicker');
							var segment_filtering_combobox = window_panel_toolbar.down('combobox#segment-filtering-combobox');

							var searchfield = window_panel_toolbar.down('searchfield#searchfield');

							var search_target_radiogroup = window_panel_toolbar.down('radiogroup#search-target');

							search_store.on({
								beforeload: function(store, operation, eOpts){
									var texts = [];
									texts.push(version_combobox.findRecordByValue(version_combobox.getValue()).get(version_combobox.displayField));
									texts.push(segment_treepicker.getValue());
									if(segment_filtering_combobox && segment_filtering_combobox.isVisible()) texts.push(segment_filtering_combobox.findRecordByValue(segment_filtering_combobox.getValue()).get(segment_filtering_combobox.displayField));
									if(search_target_radiogroup && search_target_radiogroup.isVisible()){
										var search_target_index = search_target_radiogroup.items.findIndex('inputValue', search_target_radiogroup.getValue()['searchTarget'], 0, true, true);
										texts.push( search_target_radiogroup.items.getAt(search_target_index).boxLabel );
									}
									texts.push(searchfield.getValue());
									field.setText(texts.join(' > '));
								}
							});

							var all_item_button = window_panel_toolbar.down('button#all-item-button');
							all_item_button.on({
								click: function(button, eOpts){
									var texts = [];
									texts.push(version_combobox.findRecordByValue(version_combobox.getValue()).get(version_combobox.displayField));
									texts.push(segment_treepicker.getValue());
									texts.push(segment_filtering_combobox.findRecordByValue(segment_filtering_combobox.getValue()).get(segment_filtering_combobox.displayField));
									texts.push(all_item_button.text);
									field.setText(texts.join(' > '));
								}
							});

						}
					}
				}]
			});
		};

		var system_gridpanel_config = {
			maxHeight: 460+36,//+100,
			itemId: 'system-gridpanel',
			title: 'System',
			xtype: 'gridpanel',
			store: Ext.data.StoreManager.lookup('system-list-store'),
			hideHeaders: true,
			columns: [
				{
					text: 'text',
					dataIndex: 'text',
					flex: 1,
					minWidth: 98,
					hideable: false,
					renderer: function(value,metaData,record){
						metaData.style += 'border:1px solid #ddd;padding:2px 2px 2px 1em;margin:1px 2px;';
						metaData.style += 'background-color:'+record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)+';';
						if(Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getGrayscale()<128) metaData.style += 'color:#FFFFFF;';
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
						return value;
					}
				},
				{
					text: self.DEF_COLOR_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH,
					hidden: true,
					hideable: false,
					renderer: function(value){
						return Ext.String.format('<div style="border:1px solid gray;background:{0};width:{1}px;height:{2}px;"> </div>',value,self.DEF_COLOR_COLUMN_WIDTH-22,24-11);
					}
				},
				{
					text: 'element',
					dataIndex: 'element_count',
					xtype: 'numbercolumn',
					format:'0,000',
					align: 'right',
					width: 32,
					hideable: false,
					renderer: function(value,metaData,record){
						metaData.style += 'padding:1px 2px;margin:3px;';
						return value;
					}
				}
			],
			selModel: {
				mode: 'SIMPLE'
			},
			listeners: {
				beforeselect: function(selmodel, record, index){
				},
				deselect: function(selmodel, record, index, eOpts ){
					record.beginEdit();
					record.set(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID, false);
					record.commit(true,[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]);
					record.endEdit(true,[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]);
				},
				select: function(selmodel, record, index, eOpts ){
					record.beginEdit();
					record.set(Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID, true);
					record.commit(true,[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]);
					record.endEdit(true,[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID]);
				}
			}
		};

		var segment_render_panel_config = {
//			title: 'Segment',
			border: false,
			itemId: 'segment-render-panel',
			layout: 'fit',
			dockedItems: segment_render_dockedItems,
			listeners: {
				afterrender: function(panel, eOpts){

					var render_panel           = panel.up('panel#window-panel').down('panel#main-render-panel');
					var render_top_toolbar     = panel.down('toolbar#top');
					var render_longitude_field = render_top_toolbar.down('numberfield#longitude');
					var render_latitude_field  = render_top_toolbar.down('numberfield#latitude');
					var render_zoom_field      = render_top_toolbar.down('numberfield#zoom');

					var segment_render_panel           = panel;
					var segment_render_top_toolbar     = segment_render_panel.down('toolbar#top');
					var segment_render_longitude_field = segment_render_top_toolbar.down('numberfield#longitude');
					var segment_render_latitude_field  = segment_render_top_toolbar.down('numberfield#latitude');

					panel.__webglMainRenderer = new Ag.MainRenderer({
						width:108,
						height:108,
						rate:1,
						minZoom: 1,
						maxZoom: 1,
						usePan: false,
						backgroundColor: self.DEF_RENDERER_BACKGROUND_COLOR,
						listeners: {
							rotate: function(ren,value){

								if(render_longitude_field){
									if(render_longitude_field.getValue() !== value.H){
										render_longitude_field.suspendEvent('change');
										try{
											render_longitude_field.setValue(value.H);
										}catch(e){
											console.error(e);
										}
										render_longitude_field.resumeEvent('change');
										if(render_panel.__webglMainRenderer) render_panel.__webglMainRenderer.setHorizontal(value.H);
									}
								}
								if(render_latitude_field){
									if(render_latitude_field.getValue() !== value.V){
										render_latitude_field.suspendEvent('change');
										try{
											render_latitude_field.setValue(value.V);
										}catch(e){
											console.error(e);
										}
										render_latitude_field.resumeEvent('change');
										if(render_panel.__webglMainRenderer) render_panel.__webglMainRenderer.setVertical(value.V);
									}
								}

								if(segment_render_longitude_field){
									if(segment_render_longitude_field.getValue() !== value.H){
										segment_render_longitude_field.suspendEvent('change');
										try{
											segment_render_longitude_field.setValue(value.H);
										}catch(e){
											console.error(e);
										}
										segment_render_longitude_field.resumeEvent('change');
									}
								}
								if(segment_render_latitude_field){
									if(segment_render_latitude_field.getValue() !== value.V){
										segment_render_latitude_field.suspendEvent('change');
										try{
											segment_render_latitude_field.setValue(value.V);
										}catch(e){
											console.error(e);
										}
										segment_render_latitude_field.resumeEvent('change');
									}
								}
							}
						}
					});
					panel.body.dom.appendChild( panel.__webglMainRenderer.domElement() );


					var $div = $('<div>').css({
						position:'absolute',
						width:'5px',
						top:'0px',
						right:'0px',
						bottom:'0px',
						'border-left': '1px solid #1D7BCA',
					}).appendTo($(panel.body.dom));
					var $canvas = $('<canvas>')
					.attr({id:'choropleth'})
					.appendTo($div);
					var resize_canvas = function(){
						var width = $div.width();
						var height = $div.height();
						$canvas.attr({
							width:width,
							height:height
						});

						var canvas = $canvas.get(0);
						if(canvas && canvas.getContext){
							var ctx = canvas.getContext('2d');
							ctx.beginPath();
							var grad  = ctx.createLinearGradient(0,0, 0,height);
							grad.addColorStop(0,   '#FF0000');
							grad.addColorStop(0.25,'#FFFF00');
							grad.addColorStop(0.5, '#66FF66');
							grad.addColorStop(0.75,'#00FFFF');
							grad.addColorStop(1,   '#0000FF');
							ctx.fillStyle = grad;
							ctx.rect(0,0, width,height);
							ctx.fill();
						}
					};
					panel.on('resize', resize_canvas);
					resize_canvas();


					var intervalID = setInterval(function(){
						if(cities_store.isLoading()) return;
						var cities = Ext.Array.map(cities_store.getRange(),function(record){ return record.getData(); });
						panel.__webglMainRenderer.loadObj(cities);
						clearInterval(intervalID);
					},250);

					var update_segment_render = new Ext.util.DelayedTask(function(){

						var p = match_list_store.getProxy();
						p.extraParams = p.extraParams || {};
						var version = p.extraParams['version'];
						if(Ext.isEmpty(version) && self.DEF_MODEL_VERSION_RECORD) version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);

						var SEG2ART = p.extraParams['SEG2ART']==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;
						if(Ext.isObject(SEG2ART) && Ext.isObject(SEG2ART.CITIES)){
							var CITIES2ART_COUNT = {};
							Ext.Object.each(SEG2ART.CITIES, function(cities_name,art_infos){
								CITIES2ART_COUNT[cities_name] = {count:0,total:Ext.Object.getKeys(art_infos).length};
							});

							var ids;
							var art_ids;
							if(Ag.data.renderer && version){
								ids = Ag.data.renderer[version]['ids'];
								art_ids = Ag.data.renderer[version]['art_ids'];
							}
							if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
								if(Ext.isEmpty(ids)) console.warn('ids is empty!!');
								if(Ext.isEmpty(art_ids)) console.warn('art_ids is empty!!');
								return;
							}
							var id2cities = {};
							var name2cities = {};
							var cities = Ext.Array.map(cities_store.getRange(),function(record){
								var data = record.getData();
								id2cities[data['cities_id']] = data;
								name2cities[data['name']] = data;
								return data;
							});

							var max_count = 0;
							match_list_store.each(function(record){
								var art_cities = record.get('art_cities');
								if(Ext.isArray(art_cities) && art_cities.length){
									Ext.Array.each(art_cities, function(cities_id){
										if(Ext.isObject(id2cities[cities_id]) && Ext.isString(id2cities[cities_id]['name'])){
											var cities_name = id2cities[cities_id]['name'];
											if(Ext.isObject(CITIES2ART_COUNT[cities_name]) && Ext.isNumber(CITIES2ART_COUNT[cities_name]['count'])){
												CITIES2ART_COUNT[cities_name]['count']++;
												if(max_count<CITIES2ART_COUNT[cities_name]['count']) max_count = CITIES2ART_COUNT[cities_name]['count'];
											}
										}
									});
								}
							});

							var canvas = $canvas.get(0);
							if(canvas && canvas.getContext){
								var height = $canvas.height();
								var x = 0;
								var y = 0;
								var ctx = canvas.getContext('2d');
								Ext.Object.each(CITIES2ART_COUNT, function(cities_name,cities_value){
									if(cities_value['count']<=0) return true;

									var rate = cities_value['count']/max_count;

									var y = height-Math.floor(rate*height);
									var imagedata = ctx.getImageData(x,y,1,1);
									var color_array = Array.prototype.slice.apply(imagedata.data);
									var color = new Ext.draw.Color( color_array[0], color_array[1], color_array[2] );

									name2cities[cities_name][Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
									name2cities[cities_name][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = color.toString();
								});
							}
							panel.__webglMainRenderer.setObjProperties(cities);

						}
					});
					match_list_store.on({
						load: function(store,records,successful,eOpts){
							if(successful){
								update_segment_render.delay(250);
							}
						},
						add: function( store, records, index, eOpts ){
							update_segment_render.delay(250);
						},
						bulkremove: function( store, records, indexes, isMove, eOpts ){
							update_segment_render.delay(250);
						},
						update: function( store, record, operation, eOpts ){
							update_segment_render.delay(250);
						}
					});

				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
					panel.__webglMainRenderer._setSize(10,10);
					var $dom = $(panel.body.dom);
					width = $dom.width()-6;
					height = $dom.height();
					panel.__webglMainRenderer.setSize(width,height);
				}
			}
		};

		var main_render_panel_config = {
			itemId: 'main-render-panel',
			flex: 1,
			layout: 'fit',
			dockedItems: render_dockedItems,
			listeners: {
				afterrender: function(panel, eOpts){
					var render_panel           = panel;
					var render_top_toolbar     = panel.down('toolbar#top');
					var render_longitude_field = render_top_toolbar.down('numberfield#longitude');
					var render_latitude_field  = render_top_toolbar.down('numberfield#latitude');
					var render_zoom_field      = render_top_toolbar.down('numberfield#zoom');

					var segment_render_panel           = panel.up('panel#window-panel').down('panel#segment-render-panel');
					var segment_render_top_toolbar     = segment_render_panel ? segment_render_panel.down('toolbar#top') : null;
					var segment_render_longitude_field = segment_render_top_toolbar ? segment_render_top_toolbar.down('numberfield#longitude') : null;
					var segment_render_latitude_field  = segment_render_top_toolbar ? segment_render_top_toolbar.down('numberfield#latitude') : null;


					var window_panel         = panel.up('panel#window-panel');

					var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
					var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
					var match_list_store     = match_list_gridpanel.getStore();
					var match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
					if(!match_list_gridpanel.rendered){
						match_list_gridpanel.on({
							afterrender: function(gridpanel){
								match_list_gridpanel = gridpanel;
								match_list_selmodel  = match_list_gridpanel.getSelectionModel();
								match_list_store     = match_list_gridpanel.getStore();
								match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
							},
							single: true
						});
					}

					var pallet_gridpanel = window_panel.down('gridpanel#pallet-gridpanel');
					var pallet_selmodel  = pallet_gridpanel.getSelectionModel();
					var pallet_store     = pallet_gridpanel.getStore();
					var pallet_plugin    = pallet_gridpanel.getPlugin(pallet_gridpanel.getItemId()+'-plugin');

					var selectKeepExisting = match_list_selmodel.getSelectionMode()==='SIMPLE' ? true : false;//e.ctrlKey;

					var category_tag_panel = window_panel.down('panel#category-tag-panel');
					var segment_tag_panel = window_panel.down('panel#segment-tag-panel');


					search_store.on({
						beforeload: function(store, operation, eOpts){
							panel.setLoading(true);
						},
						load: function(store,records,successful,eOpts){
							if(!successful || records.length==0) panel.setLoading(false);
						}
					});

					var update_render;
					window_panel._update_render = update_render = new Ext.util.DelayedTask(function(is_update){
						panel.setLoading(false);
						panel.__webglMainRenderer.hideAllObj();
//						return;

						$('div.category-tag-dot[data-fmaid]').css({'box-shadow':''});

						var datas_hash = {};
						var is_selected = false;
						if(self.DEF_MATCH_LIST_DRAW){
							match_list_store.each(function(match_list_record){
								var id = match_list_record.get(Ag.Def.ID_DATA_FIELD_ID);
								var record;
//										var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, id, 0, false, false, true);	//palletにレコードが存在する場合は、そのレコードの情報を使用する
//										if(pallet_record){
//											record = pallet_record;
//										}
//										else{
									record = match_list_record;
//										}

								var picked = record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID);
								if(picked){
									var picked_type = record.get(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID);
									if(picked_type===Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS){
									}
									else if(picked_type===Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS){
									}
								}

								datas_hash[ id ] = record.getData();
								datas_hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ] = picked;//match_list_selmodel.isSelected(record);
								if(is_selected) return true;
								if(datas_hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ]) is_selected = true;
							});
						}

						if(self.DEF_PALLET_DRAW){
							pallet_store.each(function(record){
								var id = record.get(Ag.Def.ID_DATA_FIELD_ID);

								var picked = record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID);
								if(picked){
									var picked_type = record.get(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID);
									if(picked_type===Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS){
									}
									else if(picked_type===Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS){
									}
								}

								datas_hash[ id ] = record.getData();
								datas_hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ] = picked;//pallet_selmodel.isSelected(record);
								if(is_selected) return true;
								if(datas_hash[ id ][ Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID ]) is_selected = true;
							});
						}

						//wireframe
						var first_options;
						var second_options;
						if(self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR || self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR || self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_WIREFRAME){
							first_options = {picked:{}};
							if(self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR) first_options.picked.color = self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR;
							if(self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR) first_options.picked.factor = self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR_FACTOR;
							if(self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR_WIREFRAME) first_options.picked.wireframe = true;
						}
						if(self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR || self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR || self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_WIREFRAME){
							second_options = {picked:{}};
							if(self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR) second_options.picked.color = self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR;
							if(self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR) second_options.picked.factor = self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR_FACTOR;
							if(self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR_WIREFRAME) second_options.picked.wireframe = true;
						}

						var datas = [];
						Ext.Object.each(datas_hash,function(id,data){
							var options;
							var picked = data[ Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID ];
							if(picked){
								var picked_type = data[ Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID ];
								if(picked_type===Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS){
									options = first_options;

									if(self.USE_SELECTION_RENDERER_PICKED_FIRST_COLOR) $('div.category-tag-dot[data-fmaid="'+data[ Ag.Def.ID_DATA_FIELD_ID ]+'"]').css({'box-shadow':'0px 0px 2px 2px'+self.DEF_SELECTION_RENDERER_PICKED_FIRST_COLOR});
								}
								else if(picked_type===Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS){
									options = second_options;

									if(self.USE_SELECTION_RENDERER_PICKED_SECOND_COLOR) $('div.category-tag-dot[data-fmaid="'+data[ Ag.Def.ID_DATA_FIELD_ID ]+'"]').css({'box-shadow':'0px 0px 2px 2px'+self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR});
								}
								else{
									$('div.category-tag-dot[data-fmaid="'+data[ Ag.Def.ID_DATA_FIELD_ID ]+'"]').css({'box-shadow':''});
								}
							}
							datas.push(self._getFilterObjDataFromRecord(Ext.Object.merge({},data),is_selected,options));
						});



						if(datas.length){
							if(is_update){
								panel.__webglMainRenderer.setObjProperties(datas);
								category_tag_panel.setLoading(false);
								segment_tag_panel.setLoading(false);
							}
							else{
								panel.__webglMainRenderer.loadObj(datas);
							}
						}
						else{
							category_tag_panel.setLoading(false);
							segment_tag_panel.setLoading(false);
						}
					});
					match_list_store.on({
						load: function(store,records,successful,eOpts){
							if(successful){
								update_render.cancel();
								update_render.delay(0,null,null,[false]);
							}
						},
						add: function( store, records, index, eOpts ){
							update_render.cancel();
							update_render.delay(250,null,null,[false]);
						},
						bulkremove: function( store, records, indexes, isMove, eOpts ){
							update_render.cancel();
							update_render.delay(250,null,null,[true]);
						},
						update: function( store, record, operation, eOpts ){
							update_render.cancel();
							update_render.delay(250,null,null,[true]);
						}
					});
					pallet_store.on({
						add: function( store, records, index, eOpts ){
							update_render.cancel();
							update_render.delay(250,null,null,[false]);
						},
						bulkremove: function( store, records, indexes, isMove, eOpts ){
							update_render.cancel();
							update_render.delay(250,null,null,[true]);
						},
						update: function( store, record, operation, eOpts ){
							update_render.cancel();
							update_render.delay(250,null,null,[true]);
						}
					});
/*
					match_list_gridpanel.on({
						deselect: function( selmodel, record, index, eOpts ){
							update_render.delay(250,null,null,[true]);
						},
						select: function( selmodel, record, index, eOpts ){
							update_render.delay(250,null,null,[true]);
						}
					});
					pallet_gridpanel.on({
						deselect: function( selmodel, record, index, eOpts ){
							update_render.delay(250,null,null,[true]);
						},
						select: function( selmodel, record, index, eOpts ){
							update_render.delay(250,null,null,[true]);
						}
					});
*/

					var update_selected_pallet_rows = function(){
						var toolbar = pallet_gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							var tbtext = toolbar.down('tbtext#items-selected-tbtext');
							tbtext.setText(Ext.util.Format.format('{0} / {1} items selected.',Ext.util.Format.number(pallet_selmodel.getCount(),'0,000'),Ext.util.Format.number(pallet_store.getCount(),'0,000')));

							var disabled = pallet_selmodel.getSelection().length ? false : true;
							Ext.Array.each(toolbar.items.items, function(item){
								if(
									!item.isXType('button') ||
									item.getItemId()=='select-all' ||
									item.getItemId()=='deselect-all' ||
									item.getItemId()=='items-selected-tagged' ||
									item.getItemId()=='items-selected-picked' ||
									item.getItemId()=='items-selected-all' ||
									item.getItemId()=='items-title-checkboxfield'
								) return true;
								item.setDisabled(disabled);
							});
						}

					};

					var $pick_point = $('img#pick-point');
					if($pick_point.length == 0){
						$pick_point = $('<img>')
										.attr({'id':'pick-point','src':'./static/css/pick-point/select_B.png'})
										.css({'position':'absolute','margin-top':'-10px','margin-left':'-10px','z-index':'20000'})
										.appendTo($(document.body))
										;
					}
					$pick_point.hide();

					panel.__webglMainRenderer = new Ag.MainRenderer({
						width:108,
						height:108,
						rate:1,
						minZoom: render_zoom_field.minValue,
						maxZoom: render_zoom_field.maxValue,
						backgroundColor: self.DEF_RENDERER_BACKGROUND_COLOR,
						listeners: {
							pick: function(ren,intersects,e){
//								console.log(ren,intersects,e);
								var $pick_point = $('img#pick-point');
								if($pick_point.length == 0){
									$pick_point = $('<img>')
													.attr({'id':'pick-point','src':'./static/css/pick-point/select_B.png'})
													.css({'position':'absolute','margin-top':'-10px','margin-left':'-10px','z-index':'20000'})
													.appendTo($(document.body))
													;
								}
								$pick_point.hide();

								var gridpanels = [];
								if(self.DEF_MATCH_LIST_DRAW) gridpanels.push(match_list_gridpanel);
								if(true || self.DEF_PALLET_DRAW) gridpanels.push(pallet_gridpanel);


								if(Ext.isArray(intersects) && intersects.length){
									var mesh = intersects[0].object;

									if(self.DEF_NEIGHBOR_SEARCH_PICK){
										return;
									}

									$pick_point.css({'left':e.pageX,'top':e.pageY}).show();


									var _pick = function(){
										var clearCount = 0;
										var matchCount = 0;
										Ext.Array.each(gridpanels, function(gridpanel){
											gridpanel.getStore().suspendEvents(false);
											if(gridpanel.getView().isVisible()) gridpanel.suspendEvents(false);
										});
										Ext.Array.each(gridpanels, function(gridpanel){
											try{
												var store     = gridpanel.getStore();
												var selmodel  = gridpanel.getSelectionModel();
												var gridview  = gridpanel.getView();
												var plugin    = gridpanel.getPlugin(gridpanel.getItemId()+'-plugin');
												var max_order = store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;

												var record = store.findRecord(Ag.Def.OBJ_ID_DATA_FIELD_ID, mesh[ Ag.Def.OBJ_ID_DATA_FIELD_ID ], 0, false, false, true);
												if(record){
	//												var node = gridview.getNode(record);

													if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)){
														if(gridview.isVisible()){
															selmodel.deselect(record,false);
														}
														var word_values = record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID);
														console.log('word_values',word_values);
														clearPickedInfoRecord(record, true);
														var fn = function(store,fieldName,value,re_value_arr,record){
//															if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return;
															var fieldValue = record.get(fieldName);
															var match_values = [];
															Ext.Array.each(re_value_arr, function(re_value,index){
																if(re_value.test(fieldValue)) match_values.push(value[index]);
															});
															if(match_values.length>0){
																if(value.length != match_values.length){
																	clearPickedInfoRecord(record, true);
																}
																else if(record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID) != null){
																	matchCount++;
																}
															}
														};
														if(Ext.isArray(word_values) && word_values.length){
															self._findWordRecords(store,Ag.Def.NAME_DATA_FIELD_ID,word_values,self,{callback:fn});
														}
														else if(Ext.isObject(word_values) && Ext.isString(word_values.dataIndex) && Ext.isArray(word_values.value) && word_values.value.length){
															self._findWordRecords(store,word_values.dataIndex,word_values.value,self,{callback:fn});
														}
														clearCount++;
													}
													else{
														if(gridview.isVisible()){
															if(plugin){
																plugin.scrollTo( store.indexOf(record), false, function(){
																	if(gridpanel.fireEvent('beforeselect', selmodel, record, store.indexOf(record), {})){
																		selmodel.select(record,selectKeepExisting,true);
//																		gridview.saveScrollState();
//																		gridview.refresh();
//																		gridview.restoreScrollState();
																	}
																});
															}
															else{
																gridview.focusRow(record);
																if(gridpanel.fireEvent('beforeselect', selmodel, record, store.indexOf(record), {})){
																	selmodel.select(record,selectKeepExisting,true);
																}
															}
														}

														max_order++;
														record.beginEdit();
														record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
														record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS);
														record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_order);
														record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,true);
														record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,false);
														record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,null);
														record.set(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,null);
														record.set(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,false);
														record.commit(true,[
															Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,
															Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID
														]);
														console.log(record.getData());
													}

												}
												else{
												}
											}catch(e){
												console.error(e);
											}
										});
										Ext.Array.each(gridpanels, function(gridpanel){
											var gridview = gridpanel.getView();
											gridpanel.getStore().resumeEvents();
											if(gridpanel.getView().isVisible()){
												gridpanel.resumeEvents();
												gridview.saveScrollState();
												gridview.refresh();
												gridview.restoreScrollState();
											}
										});

										pallet_gridpanel.getView().headerCt.clearOtherSortStates();
										pallet_store.sort(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,'DESC');

										if(clearCount>0 && matchCount == 0){
											$('div.ad-hoc-tag-selected').remove();
										}
										$pick_point.hide();
									};
									setTimeout(_pick,150);






								}
								else{

									Ext.Array.each(gridpanels, function(gridpanel){
										var store = gridpanel.getStore();
										var gridview = gridpanel.getView();
										var selmodel = gridpanel.getSelectionModel();
										store.suspendEvents(false);
										store.each(function(record){
											if(!record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return true;
											clearPickedInfoRecord(record, true);
										});
										store.resumeEvents();
										if(gridview.isVisible()){
											selmodel.deselectAll();
											gridview.saveScrollState();
											gridview.refresh();
											gridview.restoreScrollState();
										}
									});

									$('div.segment-tag-selected').removeClass('segment-tag-selected').css({'box-shadow':''});
									$('div.category-tag-selected').removeClass('category-tag-selected').css({'box-shadow':''});
									$('div.ad-hoc-tag-selected').remove();

								}

								update_selected_pallet_rows();

								update_render.cancel();
								update_render.delay(0,null,null,[true]);
							},
							rotate: function(ren,value){
								if(render_longitude_field){
									if(render_longitude_field.getValue() !== value.H){
										render_longitude_field.suspendEvent('change');
										try{
											render_longitude_field.setValue(value.H);
										}catch(e){
											console.error(e);
										}
										render_longitude_field.resumeEvent('change');
									}
								}
								if(render_latitude_field){
									if(render_latitude_field.getValue() !== value.V){
										render_latitude_field.suspendEvent('change');
										try{
											render_latitude_field.setValue(value.V);
										}catch(e){
											console.error(e);
										}
										render_latitude_field.resumeEvent('change');
									}
								}

								if(Ext.isEmpty(segment_render_panel))           segment_render_panel           = render_panel.up('panel#window-panel').down('panel#segment-render-panel');
								if(Ext.isEmpty(segment_render_top_toolbar))     segment_render_top_toolbar     = segment_render_panel ? segment_render_panel.down('toolbar#top') : null;
								if(Ext.isEmpty(segment_render_longitude_field)) segment_render_longitude_field = segment_render_top_toolbar ? segment_render_top_toolbar.down('numberfield#longitude') : null;
								if(Ext.isEmpty(segment_render_latitude_field))  segment_render_latitude_field  = segment_render_top_toolbar ? segment_render_top_toolbar.down('numberfield#latitude') : null;

								if(segment_render_longitude_field){
									if(segment_render_longitude_field.getValue() !== value.H){
										segment_render_longitude_field.suspendEvent('change');
										try{
											segment_render_longitude_field.setValue(value.H);
										}catch(e){
											console.error(e);
										}
										segment_render_longitude_field.resumeEvent('change');
										if(segment_render_panel.__webglMainRenderer) segment_render_panel.__webglMainRenderer.setHorizontal(value.H);
									}
								}
								if(segment_render_latitude_field){
									if(segment_render_latitude_field.getValue() !== value.V){
										segment_render_latitude_field.suspendEvent('change');
										try{
											segment_render_latitude_field.setValue(value.V);
										}catch(e){
											console.error(e);
										}
										segment_render_latitude_field.resumeEvent('change');
										if(segment_render_panel.__webglMainRenderer) segment_render_panel.__webglMainRenderer.setVertical(value.V);
									}
								}


							},
							zoom: function(ren,value){
//										console.log('zoom',ren,value);
								if(render_zoom_field){
									if(render_zoom_field.getValue() !== value){
										render_zoom_field.suspendEvent('change');
										try{
											render_zoom_field.setValue(value);
										}catch(e){
											console.error(e);
										}
										render_zoom_field.resumeEvent('change');
									}
								}
							},
							load: function(ren,successful){
//										console.log('load()',successful);
								category_tag_panel.setLoading(false);
								segment_tag_panel.setLoading(false);
							}
						}
					});
					panel.body.dom.appendChild( panel.__webglMainRenderer.domElement() );


//match_list_store
				},
				resize: function( panel, width, height, oldWidth, oldHeight, eOpts){
					panel.__webglMainRenderer._setSize(10,10);
					var $dom = $(panel.body.dom);
					width = $dom.width();
					height = $dom.height();
					panel.__webglMainRenderer.setSize(width,height);
				}
			}
		};

		var segment_tag_panel_config = {
			border: true,
//			maxHeight: 200,
			itemId: 'segment-tag-panel',
/*
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'start'
			},
*/
			layout: 'fit',
			autoScroll: true,
			listeners: {
				afterrender: function(panel){

					search_store.on({
						beforeload: function(store, operation, eOpts){
							$(panel.body.dom).empty();
						}
					});

					var window_panel         = panel.up('panel#window-panel');

					var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
					var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
					var match_list_store     = match_list_gridpanel.getStore();
					var match_list_gridview  = match_list_gridpanel.getView();
					var match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
					var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
					var pallet_selmodel      = pallet_gridpanel.getSelectionModel();
					var pallet_store         = pallet_gridpanel.getStore();
					var pallet_plugin        = pallet_gridpanel.getPlugin(pallet_gridpanel.getItemId()+'-plugin');
					var selectKeepExisting   = match_list_selmodel.getSelectionMode()==='SIMPLE' ? true : false;//e.ctrlKey;

					var segment_tag_panel   = window_panel.down('panel#segment-tag-panel');


//					var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
					var segment_store = Ext.data.StoreManager.lookup('segment-list-store');


					var gridpanels = [];
					var selmodels = [];
					var plugins = [];
					var stores = [];
					if(self.DEF_MATCH_LIST_DRAW){
						gridpanels.push(match_list_gridpanel);
						selmodels.push(match_list_selmodel);
						plugins.push(match_list_plugin);
						stores.push(match_list_store);
					}
					if(true || self.DEF_PALLET_DRAW){
						gridpanels.push(pallet_gridpanel);
						selmodels.push(pallet_selmodel);
						plugins.push(pallet_plugin);
						stores.push(pallet_store);
					}

					var update_segment_dot_task = self._update_segment_dot_task = new Ext.util.DelayedTask(function(){

						$(panel.body.dom).empty();
						var $bodydiv = $('<div>')
						.addClass('segment-tag-body')
						.appendTo($(panel.body.dom));

						var max_count = 0;

						segment_store.getRootNode().cascadeBy(function(record){
							if(!record.isLeaf()) return true;
							var element_count = record.get('element_count');
//							console.log('element_count',element_count);
//							if(element_count<=0) return true;
							if(max_count<element_count) max_count = element_count;

//							var background_color = '#5B9BD5';

							var data_value = record.get(Ag.Def.SEGMENT_DATA_FIELD_ID);
							if(Ext.isString(data_value)){
								if(data_value.match(/^[0-9]+(.+)$/)) data_value = RegExp.$1;
								if(data_value.match(/^_+(.+)$/)) data_value = RegExp.$1;
								data_value = data_value.toLowerCase();
							}
							else{
								data_value = '';
							}

							var background_color_hex = '#5B9BD5';

							var border_color = Ext.draw.Color.fromString(Ext.draw.Color.fromString(background_color_hex).getGrayscale()<128 ? background_color_hex : '#999999').getRGB();
							border_color.push(element_count<=0 ? 0.2 : 1);

							var background_color = Ext.draw.Color.fromString(background_color_hex).getRGB();
							background_color.push(element_count<=0 ? 0.2 : 1);
//							console.log('background_color',background_color);

							var color = Ext.draw.Color.fromString(Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getGrayscale()<128 ? '#FFFFFF' : '#000000').getRGB();
							color.push(element_count<=0 ? 0.2 : 1);

							var $div = $('<div>')
							.addClass('segment-tag')
							.css({
								'border-color': Ext.util.Format.format('rgba({0})',border_color.join(',')),
								'background-color': Ext.util.Format.format('rgba({0})',background_color.join(',')),
								'color': Ext.util.Format.format('rgba({0})',color.join(',')),
								'display': element_count<=0 ? 'none' : ''
							})
							.attr({'data-value':data_value})
							.data({'data':record.getData()})
//							.appendTo($td)
							.appendTo($bodydiv)
							.click(function(e){
								return self._clickSegmentTag($(this).attr('data-value'),e);
							})
							;
/*
							var $checked_div = $('<div>')
							.addClass('segment-tag-checked')
							.appendTo($div)
							;

							var $checked_span = $('<span>')
							.addClass('segment-tag-checked-icon')
							.addClass('glyphicon glyphicon-unchecked')
							.attr({'aria-hidden':'true'})
							.attr({'data-qtip':'SELECT '+record.get('text')})
							.appendTo($checked_div)
							;
*/
							$('<label>')
							.addClass('segment-tag-label')
							.text(record.get('segment')+'('+element_count+')')
							.appendTo($div)

							var $unload_div = $('<div>')
							.addClass('segment-tag-unload')
							.appendTo($div)
							;

							$('<span>')
							.addClass('segment-tag-unload-icon')
							.addClass('glyphicon glyphicon-remove-circle')
							.attr({'aria-hidden':'true'})
							.attr({'data-qtip':'UNLOAD '+record.get('segment')})
							.appendTo($unload_div)
							.click(function(e){
								var $this = $(this);
								var data = $this.closest('div.segment-tag').data('data');
								if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
//											console.log(data);
									var match_list_remove_records = [];
									Ext.Array.each(data.element, function(element){
										var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, element[ Ag.Def.ID_DATA_FIELD_ID ], 0, false, false, true);
										if(pallet_record){
											clearPickedInfoRecord(pallet_record, true);
										}
										var match_list_record = match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, element[ Ag.Def.ID_DATA_FIELD_ID ], 0, false, false, true);
										if(match_list_record) match_list_remove_records.push(match_list_record);
									});
									if(match_list_remove_records.length) match_list_store.remove(match_list_remove_records);

								}
								e.preventDefault();
								e.stopPropagation();
								return false;
							})
							;
						});

						if(max_count>0){

							var segment_render_panel = window_panel.down('panel#segment-render-panel');
							var $choropleth_canvas;
							if(segment_render_panel && segment_render_panel.rendered) $choropleth_canvas = $(segment_render_panel.body.dom).find('canvas#choropleth');
							if($choropleth_canvas){
								var choropleth_canvas = $choropleth_canvas.get(0);
								if(choropleth_canvas && choropleth_canvas.getContext){

									var height = $choropleth_canvas.height();
									var x = 0;
									var y = 0;
									var ctx = choropleth_canvas.getContext('2d');

									$('div.segment-tag').each(function(){
										var $this = $(this);
										var data = $this.data('data');
										var segment = data['segment'];
										var element_count = data['element_count'] - 0;

										var rate = element_count/max_count;

										var y = height-Math.floor(rate*height);
										var imagedata = ctx.getImageData(x,y,1,1);
										var background_color_arr = Array.prototype.slice.apply(imagedata.data);
										var background_color_obj = new Ext.draw.Color( background_color_arr[0], background_color_arr[1], background_color_arr[2] );
										var grayscale = background_color_obj.getGrayscale();

										var border_color = (grayscale<128 ? background_color_obj : Ext.draw.Color.fromString('#999999')).getRGB();
										border_color.push(element_count<=0 ? 0.2 : 1);

										var background_color = background_color_obj.getRGB();
										background_color.push(element_count<=0 ? 0.2 : 0.9);
//										console.log(element_count,background_color,Ext.util.Format.format('rgba({0})', background_color.join(',')),Ext.util.Format.format('rgba({0},{1},{2},0.9)', background_color_arr[0], background_color_arr[1], background_color_arr[2]));

										var color = Ext.draw.Color.fromString(grayscale<128 ? '#FFFFFF' : '#000000').getRGB();
										color.push(element_count<=0 ? 0.2 : 1);

										$this
										.css({
											'border-color': Ext.util.Format.format('rgba({0})', border_color.join(',')),
											'background-color': Ext.util.Format.format('rgba({0})', background_color.join(',')),
											'color': Ext.util.Format.format('rgba({0})', color.join(',')),
		//								'display': element_count<=0 ? 'none' : ''
										});

									});
								}
							}
						}

						setTimeout(function(){
							segment_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
						},250);

						segment_tag_panel.show();
						segment_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
						segment_tag_panel.setLoading(false);

					});

					segment_store.on({
						update: function( store, record, operation, eOpts ){
//									console.log('update');
							segment_tag_panel.setLoading(true);
							$(panel.body.dom).empty();
							update_segment_dot_task.cancel();
							update_segment_dot_task.delay(250);
						}
					});
					window_panel.on({
						resize: function(){
							segment_tag_panel.setHeight($('div.segment-tag-body').outerHeight(true)+4);
						}
					});
					segment_tag_panel.hide();
				}
			}

		};

		var category_tag_panel_config = {
//			border: true,
			maxHeight: 200,
			itemId: 'category-tag-panel',
/*
			layout: {
				type: 'vbox',
				align: 'stretch',
				pack: 'start'
			},
*/
			layout: 'fit',
			autoScroll: true,
			listeners: {
				afterrender: function(panel){

					search_store.on({
						beforeload: function(store, operation, eOpts){
							$(panel.body.dom).empty();
						}
					});

					var window_panel         = panel.up('panel#window-panel');

					var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
					var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
					var match_list_store     = match_list_gridpanel.getStore();
					var match_list_gridview  = match_list_gridpanel.getView();
					var match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
					var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
					var pallet_selmodel      = pallet_gridpanel.getSelectionModel();
					var pallet_store         = pallet_gridpanel.getStore();
					var pallet_plugin        = pallet_gridpanel.getPlugin(pallet_gridpanel.getItemId()+'-plugin');
					var selectKeepExisting   = match_list_selmodel.getSelectionMode()==='SIMPLE' ? true : false;//e.ctrlKey;

					var category_tag_panel   = window_panel.down('panel#category-tag-panel');

					var system_list_store = Ext.data.StoreManager.lookup('system-list-store');

					var gridpanels = [];
					var selmodels = [];
					var plugins = [];
					var stores = [];
					if(self.DEF_MATCH_LIST_DRAW){
						gridpanels.push(match_list_gridpanel);
						selmodels.push(match_list_selmodel);
						plugins.push(match_list_plugin);
						stores.push(match_list_store);
					}
					if(true || self.DEF_PALLET_DRAW){
						gridpanels.push(pallet_gridpanel);
						selmodels.push(pallet_selmodel);
						plugins.push(pallet_plugin);
						stores.push(pallet_store);
					}

					var update_category_dot_task = self._update_category_dot_task = new Ext.util.DelayedTask(function(){

						$(panel.body.dom).empty();
						var $bodydiv = $('<div>')
						.addClass('category-tag-body')
						.appendTo($(panel.body.dom));

						system_list_store.each(function(record){
							var element_count = record.get('element_count');
//							if(element_count<=0) return true;

							var data_value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
							if(Ext.isString(data_value)){
								if(data_value.match(/^[0-9]+(.+)$/)) data_value = RegExp.$1;
								if(data_value.match(/^_+(.+)$/)) data_value = RegExp.$1;
								data_value = data_value.toLowerCase();
							}
							else{
								data_value = '';
							}

							var border_color = Ext.draw.Color.fromString(Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getGrayscale()<128 ? record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID) : '#999999').getRGB();
							border_color.push(element_count<=0 ? 0.2 : 1);

							var background_color = Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getRGB();
							background_color.push(element_count<=0 ? 0.2 : 1);

							var color = Ext.draw.Color.fromString(Ext.draw.Color.fromString(record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID)).getGrayscale()<128 ? '#FFFFFF' : '#000000').getRGB();
							color.push(element_count<=0 ? 0.2 : 1);


							var $div = $('<div>')
							.addClass('category-tag')
							.css({
								'border-color': Ext.util.Format.format('rgba({0})',border_color.join(',')),
								'background-color': Ext.util.Format.format('rgba({0})',background_color.join(',')),
								'color': Ext.util.Format.format('rgba({0})',color.join(',')),
								'display': element_count<=0 ? 'none' : ''
							})
							.attr({'data-value':data_value})
							.data({'data':record.getData()})
//							.appendTo($td)
							.appendTo($bodydiv)
							.click(function(e){
								return self._clickCategoryTag($(this).attr('data-value'),e);
							})
							;

							$('<label>')
							.addClass('category-tag-label')
							.text(record.get('text')+'('+element_count+')')
							.appendTo($div)

							var $unload_div = $('<div>')
							.addClass('category-tag-unload')
							.appendTo($div)
							;

							$('<span>')
							.addClass('category-tag-unload-icon')
							.addClass('glyphicon glyphicon-remove-circle')
							.attr({'aria-hidden':'true'})
							.attr({'data-qtip':'UNLOAD '+record.get('text')})
							.appendTo($unload_div)
							.click(function(e){
								var $this = $(this);
								var data = $this.closest('div.category-tag').data('data');
								if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
//											console.log(data);
									var match_list_remove_records = [];
									var selected_items_remove_records = [];
									var selected_tags_remove_records = [];
									Ext.Array.each(data.element, function(element){
										var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, element[ Ag.Def.ID_DATA_FIELD_ID ], 0, false, false, true);
										if(pallet_record){
											clearPickedInfoRecord(pallet_record, true);
										}
										var match_list_record = match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, element[ Ag.Def.ID_DATA_FIELD_ID ], 0, false, false, true);
										if(match_list_record) match_list_remove_records.push(match_list_record);
									});
									if(match_list_remove_records.length) match_list_store.remove(match_list_remove_records);

								}
								e.preventDefault();
								e.stopPropagation();
								return false;
							})
							;

						});
//						console.log($bodydiv.outerHeight(true)+4);
						setTimeout(function(){
//							console.log($bodydiv.outerHeight(true)+4);
							category_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
						},250);
						category_tag_panel.show();
						category_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
						category_tag_panel.setLoading(false);
					});

					system_list_store.on({
						update: function( store, record, operation, eOpts ){
//									console.log('update');
							category_tag_panel.setLoading(true);
							$(panel.body.dom).empty();
							update_category_dot_task.cancel();
							update_category_dot_task.delay(250);
						}
					});
					window_panel.on({
						resize: function(){
							category_tag_panel.setHeight($('div.category-tag-body').outerHeight(true)+4);
						}
					});
					category_tag_panel.hide();
				}
			}

		};

		var ad_hoc_tag_config = {
			border: true,
			itemId: 'ad-hoc-tag-panel',
			layout: 'fit',
			autoScroll: true,
			listeners: {
				afterrender: function(panel){
					var window_panel         = panel.up('panel#window-panel');
					var ad_hoc_tag_panel   = window_panel.down('panel#ad-hoc-tag-panel');
					var system_list_store = Ext.data.StoreManager.lookup('system-list-store');

					var update_ad_hoc_dot_task = self._update_ad_hoc_dot_task = new Ext.util.DelayedTask(function(){
						$(panel.body.dom).empty();
						var $bodydiv = $('<div>')
						.addClass('ad-hoc-tag-body')
						.appendTo($(panel.body.dom));

						ad_hoc_tag_panel.show();
					});


					segment_store.on({
						update: function( store, record, operation, eOpts ){
							$(panel.body.dom).empty();
							update_ad_hoc_dot_task.cancel();
							update_ad_hoc_dot_task.delay(250);
						}
					});
					system_list_store.on({
						update: function( store, record, operation, eOpts ){
							$(panel.body.dom).empty();
							update_ad_hoc_dot_task.cancel();
							update_ad_hoc_dot_task.delay(250);
						}
					});

				}

			}
		};

//		var _add_tag_list_task = new Ext.util.DelayedTask(function(/*fieldName, value, css*/){
//			var viewport     = self.getViewport();
//			var window_panel = viewport.down('panel#window-panel');
//		});

		var _createCanvasNeighborPartsPanel = function(config){

			var canvas_neighbor_parts_store = Ext.data.StoreManager.lookup('canvas-neighbor-parts-store');
			var p = canvas_neighbor_parts_store.getProxy();
			var extraParams = Ext.Object.merge({},p.extraParams || {});
			var point = Ext.JSON.decode(extraParams[Ag.Def.OBJ_POINT_FIELD_ID]);
			var voxel_range = extraParams[Ag.Def.VOXEL_RANGE_FIELD_ID];

			return Ext.create('Ext.panel.Panel', Ext.apply({
				title: 'Neighbor Parts',
				itemId: 'canvas-neighbor-parts-panel',
				border: false,
				layout: {
					type: 'vbox',
					align: 'stretch'
				},
				items: [{
					height: 60,
					layout: {
						type: 'vbox',
						align: 'stretch',
						pack: 'center'
					},
					defaultType: 'fieldcontainer',
					defaults: {
						labelWidth: 76,
						labelAlign: 'right',
						layout: {
							type: 'hbox',
							align: 'middle',
							pack: 'start'
						}
					},
					items: [{
						flex: 1,
						fieldLabel: 'Origin(mm)',
						defaultType: 'displayfield',
						defaults: {
							labelWidth: 18,
							labelAlign: 'right',
							width: 88,
						},
						items: [{
							itemId: 'x',
							fieldLabel: 'X',
							value: point.x
						},{
							itemId: 'y',
							fieldLabel: 'Y',
							value: point.y
						},{
							itemId: 'z',
							fieldLabel: 'Z',
							value: point.z
						}]
					},{
						fieldLabel: 'Radius(mm)',
						items: [{
							xtype: 'numberfield',
							itemId: Ag.Def.VOXEL_RANGE_FIELD_ID,
							width: 70,
							value: voxel_range,
							maxValue: 50,
							minValue: 5,
							step: 5,
							checkChangeBuffer: 100,
							listeners: {
								change: function(field, value) {
									field.next('button#search').setDisabled(false);
								}
							}
						},{
							xtype: 'button',
							text: 'Search',
							itemId: 'search',
							disabled: true,
							handler: function(b){
								b.setDisabled(true);

								var voxel_range = b.prev('numberfield#'+Ag.Def.VOXEL_RANGE_FIELD_ID).getValue();
								voxel_range = parseInt(voxel_range, 10);

								var canvas_neighbor_parts_store = Ext.data.StoreManager.lookup('canvas-neighbor-parts-store');
								var p = canvas_neighbor_parts_store.getProxy();
								var extraParams = Ext.Object.merge({},p.extraParams || {});
								extraParams[Ag.Def.VOXEL_RANGE_FIELD_ID] = voxel_range;
								p.extraParams = extraParams;
								canvas_neighbor_parts_store.loadPage(1, {
									callback: function(records, operation, success){
										b.setDisabled(success);
									}
								});

							}
						}]
					}]
				},{
					flex: 1,
					xtype: 'gridpanel',


					itemId: 'canvas-neighbor-parts-gridpanel',
					store: canvas_neighbor_parts_store,
					viewConfig: self.getViewConfig(),
					columnLines: true,
					selModel: {
						mode: 'SIMPLE'
					},
					columns: [
						{
							text: 'obj',
							tooltip: 'obj',
							dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
							width: 82,
							lockable: false,
							draggable: false,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
	//								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-obj';
	//								console.log(value, rowIndex, colIndex);
								var rtn;
								var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
								if(Ext.isString(artc_id) && artc_id.length){
									rtn = artc_id;
								}
								else{
									rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
								}
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
								return rtn;
							}
						},
						{
							text: 'FMAID',
							tooltip: 'FMAID',
							dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
							lockable: false,
							draggable: false,
							hideable: false,
							width: 63,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								var rtn = value;
//								if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//								if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//								if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;
								return rtn;

								if(Ext.isString(rtn) && rtn.length){
									var dataIndex = view.getGridColumns()[colIndex].dataIndex;
									return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
								}
								return rtn;

							}
						},
						{
							text: 'SUB',
							tooltip: 'SUB',
							dataIndex: 'sub'+renderer_dataIndex_suffix,
							lockable: false,
							draggable: false,
							hideable: true,
							hidden: false,
							align: 'center',
							width: 42,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
//								return value;
								if(Ext.isString(value) && value.length){
									var dataIndex = view.getGridColumns()[colIndex].dataIndex;
									return make_ag_word(value,dataIndex,null,'bp3d-sub');
								}
								return value;
							}
						},
						{
							text: 'R/L',
							tooltip: 'R/L',
							dataIndex: 'laterality'+renderer_dataIndex_suffix,
							lockable: false,
							draggable: false,
							hideable: true,
							hidden: false,
							align: 'center',
							width: 42,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
								return value;
/*
								if(Ext.isString(value) && value.length){
									var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//									return make_ag_word(value,dataIndex,null,'bp3d-laterality');
									return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
								}
								return value;
*/
							}
						},
						{
							text: Ag.Def.NAME_DATA_FIELD_ID,
							tooltip: Ag.Def.NAME_DATA_FIELD_ID,
							dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
							lockable: false,
							draggable: false,
							hideable: false,
							flex: 1,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
								return value;
/*
								if(Ext.isString(value) && value.length){
//									return make_ag_word(value,null,'bp3d-name');
//									console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
									var dataIndex = view.getGridColumns()[colIndex].dataIndex;
									return make_ag_word(value,dataIndex,null,'bp3d-name',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
								}
								return value;
*/
							}
						},
						{
							text: Ag.Def.SYNONYM_DATA_FIELD_ID,
							tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
							dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
							lockable: false,
							draggable: false,
							hideable: true,
							hidden: true,
							flex: 1,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
								return value;
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								if(Ext.isString(value) && value.length){
									return make_ag_word(value,dataIndex);
								}
								else if(Ext.isArray(value) && value.length){
									var rtn = [];
									Ext.Array.each(value, function(v,i){
										if(Ext.isString(value[i]) && value[i].length){
											rtn.push(make_ag_word(value[i],dataIndex));
										}
									});
									return rtn.join('');
								}
								return value;
							}
						}
						,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',true)
						,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',true)
						,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',true)
						,
						{
							text: 'Segment',
							tooltip: 'Segment',
	//							dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID+renderer_dataIndex_suffix,
							dataIndex: 'segment',
							align: 'center',
							lockable: false,
							draggable: false,
							hideable: true,
							width: 50,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
								return value;
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								if(Ext.isString(value) && value.length){
									return make_ag_word(value,dataIndex,null,'bp3d-segment');
								}
								else if(Ext.isArray(value) && value.length){
									var rtn = [];
									Ext.Array.each(value, function(v,i){
										if(Ext.isString(value[i]) && value[i].length){
											rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment'));
										}
										else if(Ext.isNumber(value[i])){
											rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment'));
										}
									});
									return rtn.join('');
								}
								return value;
							}
						}
						,{
							hidden: true,
							hideable: false,
							text: 'Category',
							tooltip: 'Category',
							dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
							lockable: false,
							draggable: false,
							width: 70,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
								return value;
								if(Ext.isString(value) && value.length){
									var dataIndex = view.getGridColumns()[colIndex].dataIndex;
									return make_ag_word(value,dataIndex,null,'bp3d-category');
								}
								return value;
							}
						}
						,{
	//							text: 'System',
	//							tooltip: 'System',
							text: 'Category',
							tooltip: 'Category',
							dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
							align: 'center',
							lockable: false,
							draggable: false,
							hideable: true,
							width: 70,
							renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
								if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
								value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
								if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
								if(Ext.isString(value) && value.length){
//									if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//									if(value.match(/^_+(.+)$/)) value = RegExp.$1;
									metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
									if(view.getItemId()==='selected-tags-tableview') return value;
									return value;
									var dataIndex = view.getGridColumns()[colIndex].dataIndex;
									return make_ag_word(value,dataIndex,null,'bp3d-system');
								}
								return value;
							}
						}
						,{
							text: self.DEF_COLOR_LABEL,
							tooltip: self.DEF_COLOR_LABEL,
							dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
							width: self.DEF_COLOR_COLUMN_WIDTH + 22,
							minWidth: self.DEF_COLOR_COLUMN_WIDTH + 22,
							hidden: false,
							lockable: false,
							draggable: false,
							hideable: true,
							xtype: 'agcolorcolumn'
						}
						,{
							text: self.DEF_OPACITY_LABEL,
							tooltip: self.DEF_OPACITY_LABEL,
							dataIndex: Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,
							width: self.DEF_OPACITY_COLUMN_WIDTH,
							lockable: false,
							draggable: false,
							hideable: false,
							hidden: false,
							hideable: true,
							xtype: 'agopacitycolumn'
						},
						{
							text: self.DEF_DISTANCE_LABEL,
							dataIndex: Ag.Def.DISTANCE_FIELD_ID,
							width: 60,
							xtype: 'numbercolumn',
							format:'0.0000'
						},
					],
					plugins: [
						Ext.create('Ext.grid.plugin.CellEditing', {
							clicksToEdit: 1,
							listeners: {
								beforeedit: function(editor,e,eOpts){
								},
								edit: function(editor,e,eOpts){
									console.log(e);
								}
							}
						}),
						self.getBufferedRenderer({pluginId: 'canvas-neighbor-parts-gridpanel-plugin'})
					],
					listeners: {
						afterrender: function( panel, eOpts ){
							panel.getView().on({
								itemkeydown: function(view, record, item, index, e, eOpts){
									if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
										self.copyGridColumnsText(view);
									}
								}
							});
						}
					}

				}]
			},config||{}));
		};

		var cell_pick = function(records,gridpanel,e){
			var window_panel         = gridpanel.up('panel#window-panel');

			var store = gridpanel.getStore();
			var selmodel = gridpanel.getSelectionModel();
			var gridview = gridpanel.getView();

			var clearCount = 0;
			var matchCount = 0;
			var plugin    = gridpanel.getPlugin(gridpanel.getItemId()+'-plugin');
			var max_order = store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;
			var selectKeepExisting = selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;

			store.suspendEvents(false);
			gridpanel.suspendEvents(false);
			try{
				Ext.Array.each(records, function(record){

					if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)){
						if(gridview.isVisible()){
							if(gridpanel.fireEvent('beforedeselect', selmodel, record, store.indexOf(record), {})){
								selmodel.deselect(record,false);
							}
						}
						var word_values = record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID);
//						console.log('word_values',word_values);
						clearPickedInfoRecord(record, true);
						var fn = function(store,fieldName,value,re_value_arr,record){
//															if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return;

							var fieldValue = record.get(fieldName);
							var match_values = [];
							Ext.Array.each(re_value_arr, function(re_value,index){
								if(re_value.test(fieldValue)) match_values.push(value[index]);
							});
							if(match_values.length>0){
								if(value.length != match_values.length){
									clearPickedInfoRecord(record, true);
								}
								else if(record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID) != null){
									matchCount++;
								}
							}
						};
						if(Ext.isArray(word_values) && word_values.length){
							self._findWordRecords(store,Ag.Def.NAME_DATA_FIELD_ID,word_values,self,{callback:fn});
						}
						else if(Ext.isObject(word_values) && Ext.isString(word_values.dataIndex) && Ext.isArray(word_values.value) && word_values.value.length){
							self._findWordRecords(store,word_values.dataIndex,word_values.value,self,{callback:fn});
						}
						clearCount++;
					}
					else{
						if(gridview.isVisible()){
							if(plugin){
								plugin.scrollTo( store.indexOf(record), false, function(){
									if(gridpanel.fireEvent('beforeselect', selmodel, record, store.indexOf(record), {})){
										selmodel.select(record,selectKeepExisting,true);
									}
								});
							}
							else{
								gridview.focusRow(record);
								if(gridpanel.fireEvent('beforeselect', selmodel, record, store.indexOf(record), {})){
									selmodel.select(record,selectKeepExisting,true);
								}
							}
						}

						max_order++;
						record.beginEdit();
						record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
						record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS);
						record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_order);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,true);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,false);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,null);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,null);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,false);
						record.commit(true,[
							Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID
						]);
						console.log(record.getData());
					}
				});
			}catch(e){
				console.error(e);
			}

			store.resumeEvents();
			gridpanel.resumeEvents();
			gridview.saveScrollState();
			gridview.refresh();
			gridview.restoreScrollState();

			gridpanel.suspendEvent('beforedeselect');
			gridpanel.suspendEvent('beforeselect');
			try{
				gridpanel.fireEvent('select',gridpanel.getSelectionModel());
			}catch(e){
				console.error(e);
			}
			gridpanel.resumeEvent('beforedeselect');
			gridpanel.resumeEvent('beforeselect');


			if(clearCount>0 && matchCount == 0){
				$('div.ad-hoc-tag-selected').remove();
			}

			window_panel._update_render.cancel();
			window_panel._update_render.delay(0,null,null,[true]);
		};

		var cell_click = function(gridpanel,e){
			var window_panel         = gridpanel.up('panel#window-panel');

			var store = gridpanel.getStore();
			var selmodel = gridpanel.getSelectionModel();
			var gridview = gridpanel.getView();
			var selection_records = selmodel.getSelection();
			var startIndex = 0;
			var tag_records = [];
			while(startIndex>=0){
				startIndex = store.findBy(function(record){
					return record.get(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID) || record.get(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID);
				},this,startIndex);
				if(startIndex>=0){
					tag_records.push(store.getAt(startIndex));
					startIndex++;
				}
			}

			var clearCount = 0;
			var matchCount = 0;
			var plugin    = gridpanel.getPlugin(gridpanel.getItemId()+'-plugin');
			var max_order = store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;
			var selectKeepExisting = selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;

			store.suspendEvents(false);
			gridpanel.suspendEvents(false);
			try{
				var fn = function(store,fieldName,value,re_value_arr,record){
					var fieldValue = record.get(fieldName);
					var match_values = [];
					Ext.Array.each(re_value_arr, function(re_value,index){
						if(re_value.test(fieldValue)) match_values.push(value[index]);
					});
					if(match_values.length>0){
						if(value.length != match_values.length){
							clearPickedInfoRecord(record, true);
						}
						else if(record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID) != null){
							matchCount++;
						}
					}
				};
				if(Ext.isArray(tag_records)){
					Ext.Array.each(tag_records, function(record){
						if(gridpanel.fireEvent('beforedeselect', selmodel, record, store.indexOf(record), {})){
							selmodel.deselect(record,false);
						}
						var word_values = record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID);
						clearPickedInfoRecord(record, true);
						if(Ext.isArray(word_values) && word_values.length){
							self._findWordRecords(store,Ag.Def.NAME_DATA_FIELD_ID,word_values,self,{callback:fn});
						}
						else if(Ext.isObject(word_values) && Ext.isString(word_values.dataIndex) && Ext.isArray(word_values.value) && word_values.value.length){
							self._findWordRecords(store,word_values.dataIndex,word_values.value,self,{callback:fn});
						}
						clearCount++;
					});
				}
				if(Ext.isArray(selection_records)){
					selectKeepExisting = true;
					Ext.Array.each(selection_records, function(record){
						if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return true;
						if(gridview.isVisible()){
							if(gridpanel.fireEvent('beforeselect', selmodel, record, store.indexOf(record), {})){
								selmodel.select(record,selectKeepExisting,true);
							}
						}

						max_order++;
						record.beginEdit();
						record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
						record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS);
						record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_order);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,true);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,false);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,null);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,null);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,false);
						record.commit(true,[
							Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID
						]);
	//					console.log(record.getData());
					});
				}
			}catch(e){
				console.error(e);
			}

			store.resumeEvents();
			gridpanel.resumeEvents();
			gridview.saveScrollState();
			gridview.refresh();
			gridview.restoreScrollState();

			gridpanel.suspendEvent('beforedeselect');
			gridpanel.suspendEvent('beforeselect');
			try{
				gridpanel.fireEvent('select',gridpanel.getSelectionModel());
			}catch(e){
				console.error(e);
			}
			gridpanel.resumeEvent('beforedeselect');
			gridpanel.resumeEvent('beforeselect');


			if(clearCount>0 && matchCount == 0){
				$('div.ad-hoc-tag-selected').remove();
			}

			window_panel._update_render.cancel();
			window_panel._update_render.delay(0,null,null,[true]);
		};

		var match_list_gridpanel_config = {
			title: 'Loaded parts list',
			itemId: 'match-list-gridpanel',
//					region: 'east',
//				width: center_width/5*2,
//				minWidth: center_width/5*2,
//				split: true,
			xtype: 'gridpanel',
//					emptyText: 'Palette',
			store: Ag.Def.CONCEPT_MATCH_LIST_STORE_ID,
			viewConfig: {
				itemId: 'selected-items-tableview'
			},
			dockedItems: [{
				hidden: true,
				xtype: 'toolbar',
				dock: 'top',
				itemId: 'top',
				items: [{
					xtype: 'tbtext',
					style:{'cursor':'default','user-select':'none','font-weight':'bold'},
//							text: 'selected items'
					text: 'Palette'
				}
				,{
					xtype: 'tbtext',
					style:{'cursor':'default','user-select':'none','font-weight':'normal'},
					text: ' '
				}
				]
			}],
			plugins: [
				Ext.create('Ext.grid.plugin.CellEditing', {
					clicksToEdit: 1,
				}),
//				self.getBufferedRenderer({pluginId: 'match-list-gridpanel-plugin'})
			],

			selModel: {
//						mode : 'SIMPLE'
				mode : 'MULTI'
			},
			columnLines: true,
			columns: [
				{
					text: 'obj',
					tooltip: 'obj',
					dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
					width: 82,
					lockable: false,
					draggable: false,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-obj';
//								console.log(value, rowIndex, colIndex);
						var rtn;
						var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
						if(Ext.isString(artc_id) && artc_id.length){
							rtn = artc_id;
						}
						else{
							rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
						}
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
						return rtn;
					}
				},
				{
					text: 'FMAID',
					tooltip: 'FMAID',
					dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: false,
					width: 63,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
//						var rtn = value;
//						if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//						if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//						if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;
////							return rtn;
						var rtn = record.get(Ag.Def.ID_DATA_FIELD_ID+'_renderer');
						if(Ext.isString(rtn) && rtn.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
						}
						return rtn;

					}
				},
				{
					text: 'SUB',
					tooltip: 'SUB',
					dataIndex: 'sub'+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: true,
					hidden: false,
					align: 'center',
					width: 42,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
//						return value;
						if(Ext.isString(value) && value.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-sub',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				},
				{
					text: 'R/L',
					tooltip: 'R/L',
					dataIndex: 'laterality'+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: true,
					hidden: false,
					align: 'center',
					width: 42,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
//								return value;
						if(Ext.isString(value) && value.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//								return make_ag_word(value,dataIndex,null,'bp3d-laterality');
							return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				},
				{
					text: Ag.Def.NAME_DATA_FIELD_ID,
					tooltip: Ag.Def.NAME_DATA_FIELD_ID,
					dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: false,
					flex: 1,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
						if(view.getItemId()==='selected-tags-tableview') return value;
						if(Ext.isString(value) && value.length){
//								return make_ag_word(value,null,'bp3d-name');
//									console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-name',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				},
				{
					text: Ag.Def.SYNONYM_DATA_FIELD_ID,
					tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
					dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: true,
					hidden: true,
					flex: 1,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
						return value;
						var dataIndex = view.getGridColumns()[colIndex].dataIndex;
						if(Ext.isString(value) && value.length){
							return make_ag_word(value,dataIndex);
						}
						else if(Ext.isArray(value) && value.length){
							var rtn = [];
							Ext.Array.each(value, function(v,i){
								if(Ext.isString(value[i]) && value[i].length){
									rtn.push(make_ag_word(value[i],dataIndex));
								}
							});
							return rtn.join('');
						}
						return value;
					}
				}
				,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',false)
				,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',false)
				,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',false)
				,
				{
					text: 'Segment',
					tooltip: 'Segment',
					dataIndex: Ag.Def.SEGMENT_DATA_FIELD_ID+renderer_dataIndex_suffix,
					align: 'center',
					lockable: false,
					draggable: false,
					hideable: true,
					width: 50,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
						if(view.getItemId()==='selected-tags-tableview') return value;
						var dataIndex = view.getGridColumns()[colIndex].dataIndex;
						if(Ext.isString(value) && value.length){
							return make_ag_word(value,dataIndex,null,'bp3d-segment');
						}
						else if(Ext.isArray(value) && value.length){
							var rtn = [];
							Ext.Array.each(value, function(v,i){
								if(Ext.isString(value[i]) && value[i].length){
									rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID)));
								}
								else if(Ext.isNumber(value[i])){
									rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID)));
								}
							});
							return rtn.join('');
						}
						return value;
					}
				}
				,{
					hidden: true,
					hideable: false,
					text: 'Category',
					tooltip: 'Category',
					dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					width: 70,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
						if(view.getItemId()==='selected-tags-tableview') return value;
						if(Ext.isString(value) && value.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-category');
						}
						return value;
					}
				}
				,{
//							text: 'System',
//							tooltip: 'System',
					text: 'Category',
					tooltip: 'Category',
					dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
					align: 'center',
					lockable: false,
					draggable: false,
					hideable: true,
					width: 70,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
						value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
						if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
						if(Ext.isString(value) && value.length){
//							if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//							if(value.match(/^_+(.+)$/)) value = RegExp.$1;
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-category',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				}
				,{
					text: self.DEF_COLOR_LABEL,
					tooltip: self.DEF_COLOR_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH + 22,
					minWidth: self.DEF_COLOR_COLUMN_WIDTH + 22,
					hidden: false,
					lockable: false,
					draggable: false,
					hideable: true,
					xtype: 'agcolorcolumn'
				}
				,{
					text: self.DEF_OPACITY_LABEL,
					tooltip: self.DEF_OPACITY_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,
					width: self.DEF_OPACITY_COLUMN_WIDTH,
					lockable: false,
					draggable: false,
					hideable: false,
					hidden: false,
					hideable: true,
					xtype: 'agopacitycolumn'
				},
				{
					text: 'pick',
					tooltip: 'pick',
//						xtype: 'agcheckcolumn',
					dataIndex: Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
					align: 'center',
					width: 34,
					locked: false,
					lockable: false,
					draggable: false,
					sortable: true,
					hideable: false,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						return Ext.util.Format.format('<span class="glyphicon {0}" aria-hidden="true" data-fmaid="{1}" data-qtip="selected by pick"></span>', value===true ? 'glyphicon-check' :'glyphicon-unchecked', record.get(Ag.Def.ID_DATA_FIELD_ID));
					}
				}
				,{
					text: 'tag',
					tooltip: 'tag',
//						xtype: 'agcheckcolumn',
					dataIndex: Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
					align: 'center',
					width: 34,
					locked: false,
					lockable: false,
					draggable: false,
					sortable: true,
					hideable: false,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						return Ext.util.Format.format('<span class="glyphicon {0}" aria-hidden="true" data-fmaid="{1}" data-qtip="selected by tag"></span>', value===true ? 'glyphicon-check' :'glyphicon-unchecked', record.get(Ag.Def.ID_DATA_FIELD_ID));
					}
				}
				,{
//							text: 'unselect',
					width: 34,
					align: 'center',
					locked: false,
					lockable: false,
					draggable: false,
					sortable: false,
					hideable: false,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						return '<span class="glyphicon glyphicon-remove-circle" aria-hidden="true" data-fmaid="'+record.get(Ag.Def.ID_DATA_FIELD_ID)+'" data-qtip="unselect"></span>';
					}
				}
			],
			listeners: {
				beforecellmousedown: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
//					console.log('beforecellmousedown',$(td).hasClass('bp3d-grid-cell-obj'),$(e.target).hasClass('bp3d-word-button'));
					if($(td).hasClass('bp3d-grid-cell-obj') || $(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforecellmouseup: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
//					console.log('beforecellmouseup',$(td).hasClass('bp3d-grid-cell-obj'),$(e.target).hasClass('bp3d-word-button'));
					if($(td).hasClass('bp3d-grid-cell-obj') || $(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforecellclick: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
//					console.log('beforecellclick',$(td).hasClass('bp3d-grid-cell-obj'),$(e.target).hasClass('bp3d-word-button'));
					if($(td).hasClass('bp3d-grid-cell-obj') || $(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforecelldblclick: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
//					console.log('beforecelldblclick',$(td).hasClass('bp3d-grid-cell-obj'),$(e.target).hasClass('bp3d-word-button'));
					if($(td).hasClass('bp3d-grid-cell-obj') || $(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforeitemmouseenter: function( view, record, item, index, e, eOpts ){
//					console.log('beforeitemmouseenter',$(e.target).hasClass('bp3d-word-button'));
//					if($(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforeitemmouseleave: function( view, record, item, index, e, eOpts ){
//					console.log('beforeitemmouseleave',$(e.target).hasClass('bp3d-word-button'));
//					if($(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
/*
				beforeitemmousedown: function( view, record, item, index, e, eOpts ){
					console.log('beforeitemmousedown',$(e.target).hasClass('bp3d-word-button'));
//					if($(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforeitemmouseup: function( view, record, item, index, e, eOpts ){
					console.log('beforeitemmouseup',$(e.target).hasClass('bp3d-word-button'));
//					if($(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforeitemclick: function( view, record, item, index, e, eOpts ){
					console.log('beforeitemclick',$(e.target).hasClass('bp3d-word-button'));
//					if($(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
				beforeitemdblclick: function( view, record, item, index, e, eOpts ){
					console.log('beforeitemclick',$(e.target).hasClass('bp3d-word-button'));
//					if($(e.target).hasClass('bp3d-word-button')) return true;
					return false;
				},
*/
/*
				cellmousedown: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
					console.log('cellmousedown');
					return false;
				},
				cellmouseup: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
					console.log('cellmouseup');
					return false;
				},
				cellclick: function( view, td, cellIndex, record, tr, rowIndex, e, eOpts ){
					console.log('cellclick');
					return false;
				},
*/
				afterrender: function(gridpanel){
					var window_panel         = gridpanel.up('panel#window-panel');
					var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
					var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
					var match_list_store     = match_list_gridpanel.getStore();
					var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
					var pallet_selmodel      = pallet_gridpanel.getSelectionModel();
					var pallet_store         = pallet_gridpanel.getStore();

					var main_render_panel    = window_panel.down('panel#main-render-panel');
					var category_tag_panel   = window_panel.down('panel#category-tag-panel');
					var segment_tag_panel    = window_panel.down('panel#segment-tag-panel');

					var gridpanels = [];
					if(self.DEF_MATCH_LIST_DRAW) gridpanels.push(match_list_gridpanel);
					if(true || self.DEF_PALLET_DRAW) gridpanels.push(pallet_gridpanel);

					var store = gridpanel.getStore();
					store.removeAll();	//emptyTextが表示されない為、あえてクリアする
					var selmodel = gridpanel.getSelectionModel();
					var gridview = gridpanel.getView();
					var $gridviewdom = $(gridview.el.dom);

					// unselect
					$gridviewdom.on('click','span.glyphicon-remove-circle[data-fmaid]', function(e){
						var $this = $(this);
						var fmaid = $this.data('fmaid');
						var record = store.findRecord(Ag.Def.ID_DATA_FIELD_ID, fmaid, 0, false, false, true);
						if(record){

							let undobutton = gridpanel.down('button#items-undo');
							undobutton._undobuffer = undobutton._undobuffer || [];
							let records = store.getRange();
							if(Ext.isArray(records) && records.length) undobutton._undobuffer.push(Ext.Array.map(records, function(record){ return record.getData(); }));
							undobutton.setDisabled(undobutton._undobuffer.length===0);

							store.remove(record);
/*
							record.beginEdit();
							record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,false);
							record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,null);
							record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,0);
							record.endEdit(false,[Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID]);
*/
							Ext.Array.each(gridpanels, function(gridpanel,i){
								gridpanel.getStore().suspendEvents(false);
								if(gridpanel.getView().isVisible()) gridpanel.suspendEvents(true);
							});
							Ext.Array.each(gridpanels, function(gridpanel,i){
								var store = gridpanel.getStore();
								if(store.getCount()===0) return true;
								var selmodel = gridpanel.getSelectionModel();
								var gridview = gridpanel.getView();

								var record = store.findRecord(Ag.Def.ID_DATA_FIELD_ID, fmaid, 0, false, false, true);
								if(record){
									clearPickedInfoRecord(record, false);
									if(gridview.isVisible()) selmodel.deselect(record,false);
								}
							});
							Ext.Array.each(gridpanels, function(gridpanel,i){
								gridpanel.getStore().resumeEvents();
								if(gridpanel.getView().isVisible()) gridpanel.resumeEvents();
							});
							pallet_gridpanel.getView().headerCt.clearOtherSortStates();
							pallet_store.sort(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,'DESC');

							window_panel._update_render.cancel();
							window_panel._update_render.delay(0,null,null,[true]);
						}
					});
/*
					$gridviewdom.on('click', 'td.bp3d-grid-cell', function(e){
//					$gridviewdom.on('click','a.bp3d-word-button', function(e){
//									console.log('td.click');
						var $tr = $(this).closest('tr');
						if($tr.length){
							var record = gridview.getRecord($tr.get(0));
							if(record){
								if(selmodel.isSelected(record)){
									selmodel.deselect([record],false);
									if(selmodel.getSelection().length==0) selmodel.clearSelections();
								}
								else if(gridpanel.fireEvent('beforeselect', selmodel, record, store.indexOf(record), {})){
									selmodel.select([record],true,false);
								}
								else{
//										gridview.removeRowCls(store.indexOf(record),gridview.focusedItemCls);
								}
							}
						}
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
*/

					$gridviewdom.on('click','td.bp3d-grid-cell.bp3d-grid-cell-obj', function(e){
//						var $tr = $(this).closest('tr.x-grid-data-row');
//							var selected = $(this).hasClass(class_word_button_selected) ? false : true;
//							if(!selected){
//								$tr.find('.'+class_word_button_selected).toggleClass(class_word_button_selected, selected);
//							}
//							$(this).toggleClass(class_word_button_selected, selected);
//							$tr.toggleClass(class_row_selected, selected);

//							button_disabled(e);
/*
						var record = gridview.getRecord($tr.get(0));
						if(record){
							cell_pick([record],gridpanel,e);
						}
*/
						cell_click(gridpanel,e);

						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-fmaid', function(e){
						var $tr = $(this).closest('tr.x-grid-data-row');
//							var selected = $(this).hasClass(class_word_button_selected) ? false : true;
//							if(!selected){
//								$tr.find('.'+class_word_button_selected).toggleClass(class_word_button_selected, selected);
//							}
//							$(this).toggleClass(class_word_button_selected, selected);
//							$tr.toggleClass(class_row_selected, selected);

//							button_disabled(e);
/*
						var record = gridview.getRecord($tr.get(0));
						if(record){
							cell_pick([record],gridpanel,e);
						}
*/
						cell_click(gridpanel,e);

						e.preventDefault();
						e.stopPropagation();
						return false;
					});


					$gridviewdom.on('click','a.bp3d-word-button.bp3d-name', function(e){
//									console.log('a.click');
						var $this = $(this);
						var value = $this.attr('data-value');
						var dataIndex = $(this).attr('data-dataIndex');
/*
						var record = match_list_gridpanel.getView().getRecord($(this).closest('tr').get(0))
						gridpanel._addTagList(Ag.Def.NAME_DATA_FIELD_ID, value, {
							'border-color':$this.css('border-color'),
							'background-color':$this.css('background-color'),
							'color':$this.css('color')
						});
*/
						self._clickWordTag(value,dataIndex);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
					$gridviewdom.on('click','a.bp3d-word-button.bp3d-relation', function(e){
						var $this = $(this);
						var value = $this.attr('data-value');
						var dataIndex = $(this).attr('data-dataIndex');
						self._clickWordTag(value,dataIndex);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
					$gridviewdom.on('click','a.bp3d-word-button.bp3d-sub', function(e){
						var $this = $(this);
						var value = $this.attr('data-value');
						var dataIndex = $(this).attr('data-dataIndex');
						self._clickWordTag(value,dataIndex);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
					$gridviewdom.on('click','a.bp3d-word-button.bp3d-laterality', function(e){
						var $this = $(this);
						var value = $this.attr('data-value');
						var dataIndex = $(this).attr('data-dataIndex');
						self._clickWordTag(value,dataIndex);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
					$gridviewdom.on('click','a.bp3d-word-button.bp3d-segment', function(e){
						var $this = $(this);
						var value = $this.attr('data-value');
						self._clickSegmentTag(value,e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
					$gridviewdom.on('click','a.bp3d-word-button.bp3d-category', function(e){
						var $this = $(this);
						var value = $this.attr('data-value');
						self._clickCategoryTag(value,e);
						e.stopImmediatePropagation();
						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-system', function(e){
						var $this = $(this);
						var value = $this.attr('data-value');
						var record = match_list_gridpanel.getView().getRecord($(this).closest('tr').get(0))
						gridpanel._addTagList(Ag.Def.SYSTEM_ID_DATA_FIELD_ID, record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID), {
							'border-color':$this.css('border-color'),
							'background-color':$this.css('background-color'),
							'color':$this.css('color')
						});
						e.preventDefault();
						e.stopPropagation();
						return false;
					});
/**/
					gridpanel._clearTagText = function(){
						var item = gridpanel.getDockedItems('toolbar[dock="top"]')[0].items.getAt(1);
						if(item.rendered){
							var $dom = $(item.el.dom);
							$dom.empty();
						}
					};
					gridpanel._addTagText = function(text,css,options){
//									return;
						var item = gridpanel.getDockedItems('toolbar[dock="top"]')[0].items.getAt(1);
						if(item.rendered){
							var $dom = $(item.el.dom);
							var $items = $dom.find('div.selected-tag-item');

//										if($items.length===0) $dom.empty();
							if(self.DEF_SELECTED_TAGS_KEEP_LIST===self.DEF_SELECTED_TAGS_KEEP_LIST_REPLACE){
//											$dom.empty();
							}
							else{
								if($items.length===0) $dom.empty();
							}

							var $div = $('<div>').addClass('selected-tag-item').appendTo($dom);
							if(Ext.isObject(css)) $div.css(css);
							$('<span>').addClass('selected-tag-item-text').css({'display':'inline-block'}).text(text).appendTo($div);
							var $span = $('<span>')
							.addClass('selected-tag-item-remove-icon')
							.addClass('glyphicon glyphicon-remove-circle')
							.attr({'aria-hidden':'true'})
//										.css({'top':'2px'})
							.css({'margin-left':'1px'})
							.appendTo($div)
							;
							if(Ext.isObject(options)){
								$span.data('options',options);
								if(Ext.isFunction(options.callback)){
									$span.click(function(e){
										var $this = $(this);
										var options = $this.data('options');
										var $div = $this.closest('div.selected-tag-item');
										Ext.callback(options.callback,$div,[options]);
										$div.remove();
									});
								}
							}

							item.updateLayout();
						}
					};
					gridpanel._getTagTextAll = function(){
						return $('div.selected-tag-item>span.selected-tag-item-text').map(function(){return $(this).text()}).toArray();
					};
					gridpanel._getTagTextCount = function(){
						return $('div.selected-tag-item>span.selected-tag-item-text').map(function(){return $(this).text()}).toArray().length;
					};
					gridpanel._clearTagList = function(records,doUpdate){
						var window_panel         = gridpanel.up('panel#window-panel');
						var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
						var match_list_store     = match_list_gridpanel.getStore();
						var match_list_view      = match_list_gridpanel.getView();
						var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
						var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
						var pallet_store         = pallet_gridpanel.getStore();
						var pallet_view          = pallet_gridpanel.getView();
						var pallet_selmodel      = pallet_gridpanel.getSelectionModel();

						if(records===undefined || records===null){
							records = match_list_store.getRange();
						}else if(!Ext.isArray(records)){
							return;
						}
						match_list_gridpanel.suspendEvents(false);
						match_list_store.suspendEvents(false);
						pallet_gridpanel.suspendEvents(false);
						pallet_store.suspendEvents(false);
						try{
							var remove_records = [];
							Ext.Array.each(records, function(record){
								var match_list_record = match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
								if(match_list_record){
									clearPickedInfoRecord(match_list_record, true);
									if(match_list_view.isVisible()) match_list_selmodel.deselect(match_list_record,false);
								}

								var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
								if(pallet_record){
									clearPickedInfoRecord(pallet_record, true);
									if(pallet_view.isVisible()) pallet_selmodel.deselect(pallet_record,false);
								}

							});
						}catch(e){
							console.error(e)
						}
						match_list_gridpanel.resumeEvents();
						match_list_store.resumeEvents();
						pallet_gridpanel.resumeEvents();
						pallet_store.resumeEvents();

						self.refreshView(match_list_gridpanel.getView());
						self.refreshView(pallet_gridpanel.getView());

						if(doUpdate){
							window_panel._update_render.cancel();
							window_panel._update_render.delay(0,null,null,[true]);
						}
					};

					gridpanel._add_tag_list_task = new Ext.util.DelayedTask(function(/*fieldName, value, css*/){
//									if(Ext.isEmpty(value) || !Ext.isString(value) || Ext.isEmpty(fieldName) || !Ext.isString(fieldName)) return;


						var window_panel         = gridpanel.up('panel#window-panel');
						var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
						var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
						var match_list_store     = match_list_gridpanel.getStore();
						var match_list_view      = match_list_gridpanel.getView();
						var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
						var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
						var pallet_store         = pallet_gridpanel.getStore();
						var pallet_view          = pallet_gridpanel.getView();
						var pallet_selmodel      = pallet_gridpanel.getSelectionModel();

						if(self.DEF_SELECTED_TAGS_KEEP_LIST===self.DEF_SELECTED_TAGS_KEEP_LIST_REPLACE){
							match_list_gridpanel._clearTagText();
							match_list_gridpanel._clearTagList(null,false);
						}

						var $spans = $('div.selected-tag-item>span.selected-tag-item-remove-icon');
						var len = $spans.length;
						if(len===0){
							match_list_gridpanel._clearTagText();
							match_list_gridpanel._clearTagList(null,true);
							return;
						}


						match_list_gridpanel.suspendEvents(false);
						match_list_store.suspendEvents(false);
						pallet_gridpanel.suspendEvents(false);
						pallet_store.suspendEvents(false);
						try{

							var fieldName;
							var value;
							var $span = $spans.eq(len-1);
							var options = $span.data('options');
							if(Ext.isObject(options)){
								fieldName = options['fieldName'];
								value = options['value'];
							}

							match_list_store.each(function(record){
								if(!record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return true;
								if(record.get(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID) != Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS) return true;
								clearPickedInfoRecord(record,true);
							});
							pallet_store.each(function(record){
								if(!record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return true;
								if(record.get(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID) != Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS) return true;
								clearPickedInfoRecord(record,true);
							});

//								$spans.each(function(index){
							var values = [];
							for(var index=0;index<len;index++){
								var $span = $spans.eq(index);
								console.log("index=["+index+"]");
								var options = $span.data('options');
								if(Ext.isObject(options)){
									fieldName = options['fieldName'];
//										value = options['value'];
									values.push(options['value']);
								}
								while(fieldName===Ag.Def.NAME_DATA_FIELD_ID && index<(len-1)){
									var $span = $spans.eq(index+1);
									console.log("index=["+index+"]");
									var options = $span.data('options');
									if(Ext.isObject(options)){
										if(options['fieldName']===Ag.Def.NAME_DATA_FIELD_ID){
											fieldName = options['fieldName'];
											values.push(options['value']);
											index++;
										}
										else{
											break;
										}
									}
									else{
										break;
									}
								}
								console.log("values=["+values+"]");

//											if(Ext.isEmpty($span.data('datas'))){
									var records = Ext.Array.filter(findRecords(match_list_store, fieldName, values, gridpanel), function(record){
										if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return false;
										if(record.get(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID) == Ag.Def.CONCEPT_DATA_PICKED_TYPE_ITEMS) return false;
										return true;
									});
									$span.data('datas', Ext.Array.map(records, function(record){ return record.get(Ag.Def.ID_DATA_FIELD_ID); }));
//											}
								values = [];
							}

							var update_match_list_records = [];
							var datas_arr = [];
							$spans.each(function(){ datas_arr.push($(this).data('datas')); });
							Ext.Array.each(Ext.Array.intersect.apply(this, datas_arr ), function(data){
									var record = match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, data, 0, false, false, true);
									if(!record) return true;
									if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) return true;
									update_match_list_records.push(record);
							});

							var max_pallet_value = pallet_store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;
							var max_match_list_value = match_list_store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;

							Ext.Array.each(update_match_list_records, function(match_list_record){
								var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, match_list_record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
								if(pallet_record){
									max_pallet_value++;
									pallet_record.beginEdit();
									pallet_record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
									pallet_record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
									pallet_record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_pallet_value);
									pallet_record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
									pallet_record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,true);
									pallet_record.commit(false,[
										Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
										Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
										Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
										Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
										Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID
									]);
								}

								max_match_list_value++;
								match_list_record.beginEdit();
								match_list_record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID, true);
								match_list_record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
								match_list_record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_match_list_value);
								match_list_record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID, false);
								match_list_record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID, true);
								match_list_record.commit(false,[
									Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
									Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
									Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
									Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
									Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID
								]);
							});

						}catch(e){
							console.error(e);
						}
						match_list_gridpanel.resumeEvents();
						match_list_store.resumeEvents();
						pallet_gridpanel.resumeEvents();
						pallet_store.resumeEvents();

						self.refreshView(match_list_gridpanel.getView());
						self.refreshView(pallet_gridpanel.getView());

						window_panel._update_render.cancel();
						window_panel._update_render.delay(0,null,null,[true]);
					});
					gridpanel._addTagList = function(fieldName, value, css){
						if(Ext.isEmpty(value) || !Ext.isString(value) || Ext.isEmpty(fieldName) || !Ext.isString(fieldName)) return;
						main_render_panel.setLoading(true);
						category_tag_panel.setLoading(true);
						segment_tag_panel.setLoading(true);

						var tag_text = value;
						if(fieldName === Ag.Def.SYSTEM_ID_DATA_FIELD_ID){
							if(tag_text.match(/^[0-9]+(.+)$/)) tag_text = RegExp.$1;
							if(tag_text.match(/^_+(.+)$/)) tag_text = RegExp.$1;
						}
						gridpanel._addTagText(tag_text,css,{
							callback: function(options){

								main_render_panel.setLoading(true);
								category_tag_panel.setLoading(true);
								segment_tag_panel.setLoading(true);

								gridpanel._add_tag_list_task.cancel();
								gridpanel._add_tag_list_task.delay(100);

							},
							value: value,
							fieldName: fieldName,
							scope: match_list_gridpanel
						});

						gridpanel._add_tag_list_task.cancel();
//									gridpanel._add_tag_list_task.delay(100,null,null,[fieldName, value, css]);
						gridpanel._add_tag_list_task.delay(100);
					};





/*
					var toolbar_bottom_buttons_disabled = new Ext.util.DelayedTask(function(){
						var disabled = selmodel.getCount()===0;
						gridpanel.getDockedItems('toolbar[dock="bottom"]')[0].items.each(function(item){
							if(
								Ext.isObject(item) &&
								Ext.isFunction(item.isXType) &&
//										(item.isXType('button') || item.isXType('agcolorbutton') || item.isXType('agopacitybutton')) &&
								item.isXType('button') &&
								Ext.isFunction(item.getItemId) &&
								item.getItemId()!=='select-all' &&
								item.getItemId()!=='deselect-all' &&
								Ext.isFunction(item.setDisabled)
							) item.setDisabled(disabled);
						});
					});

					selmodel.on({
						select: function(){
//									console.log('select()');
							toolbar_bottom_buttons_disabled.delay(100);
						},
						deselect: function(){
//									console.log('deselect()');
							toolbar_bottom_buttons_disabled.delay(100);
						},
						selectionchange: function(){
//									console.log('selectionchange()');
							toolbar_bottom_buttons_disabled.delay(0);
						}
					});
*/

					var update_selected_records = function(){
						var records = [];
						var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							var tbtext = toolbar.down('tbtext#items-selected-tbtext');
							var combobox = toolbar.down('combobox#items-selected-dataindex-combobox');
							var dataIndex = combobox.getValue();
							var count = 0;
							if(dataIndex=='all'){																								//20210205
								records = store.getRange();																				//20210205
							}																																		//20210205
							else if(dataIndex=='not_selected'){																	//20210205
								records = Ext.Array.filter(store.getRange(), function(record){		//20210205
									return !(																												//20210205
										record.get(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID) ||	//20210205
										record.get(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID)		//20210205
									);																															//20210205
								});																																//20210205
							}																																		//20210205
							else{																																//20210205
								records = Ext.Array.filter(store.getRange(), function(record){
									return record.get(dataIndex);
								});
							}																																	//20210205
						}
						return records;
					};

					var update_selected_rows = function(){
						var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							var tbtext = toolbar.down('tbtext#items-selected-tbtext');
							var combobox = toolbar.down('combobox#items-selected-dataindex-combobox');
							var dataIndex = combobox.getValue();
							var count = update_selected_records().length;												//20210205
/*
							if(dataIndex=='all'){																								//20210205
								count = store.getCount();																					//20210205
							}																																		//20210205
							else if(dataIndex=='not_selected'){																	//20210205
								count = Ext.Array.filter(store.getRange(), function(record){			//20210205
									return !(record.get(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID) || record.get(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID));	//20210205
								}).length;																												//20210205
							}																																		//20210205
							else{																																//20210205
								count = Ext.Array.filter(store.getRange(), function(record){
									return record.get(dataIndex);
								}).length;
							}																																		//20210205
*/

//								tbtext.setText(Ext.util.Format.format('{0} / {1}',Ext.util.Format.number(selmodel.getCount(),'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));
							tbtext.setText(Ext.util.Format.format('{0} / {1}',Ext.util.Format.number(count,'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));

							Ext.defer(function(){
								var disabled = count===0;
								toolbar.items.each(function(item){
									if(
										Ext.isObject(item) &&
										Ext.isFunction(item.isXType) &&
										item.isXType('button') &&
										Ext.isFunction(item.getItemId) &&
										item.getItemId()!=='select-all' &&
										item.getItemId()!=='deselect-all' &&
										item.getItemId()!='items-selected-tagged' &&
										item.getItemId()!='items-selected-picked' &&
										item.getItemId()!='items-selected-all' &&
										item.getItemId()!='items-undo' &&
										Ext.isFunction(item.setDisabled)
									) item.setDisabled(disabled);
								});
								toolbar.down('filefield#items-upload').setDisabled(false);
							},100);

						}
					};

					var func_false = function(){
						return false;
					};
/*
					gridpanel.on({
						beforeitemmousedown: func_false,
						beforeitemmouseenter: func_false,
						beforeitemmouseleave: func_false,
						beforeitemmouseup: func_false,
//							beforeitemclick: func_false,
//							beforeitemdblclick: func_false
					});
*/
/*
					gridpanel.on({
						deselect: update_selected_rows,
						select: update_selected_rows,
						selectionchange: update_selected_rows,
						scope: gridpanel,
						buffer: 250
					});
*/
					gridview.on({
						refresh: update_selected_rows
					});

					store.on({
						add: update_selected_rows,
						bulkremove: update_selected_rows,
//							update: update_selected_rows,
						scope: gridpanel,
						buffer: 250
					});

//					console.log(self.__config);

					gridpanel.addDocked([{
						xtype: 'toolbar',
						dock: 'bottom',
						itemId: 'bottom',
						ui: 'footer',
						layout: {
//							overflowHandler: 'Menu'
						},
						defaults: {
							disabled: true,
						},
						items: [{
							hidden: true,
							itemId: 'select-all',
							tooltip: 'Select',
							iconCls: 'pallet_select',
							disabled: false,
							handler: function(button){
								var gridpanel = button.up('gridpanel');
								var gridview = gridpanel.getView();
								var selmodel = gridpanel.getSelectionModel();
								gridview.saveScrollState();
								selmodel.selectAll();
								gridview.restoreScrollState();
							}
						},{
							hidden: true,
							itemId: 'deselect-all',
							tooltip: 'Unselect',
							iconCls: 'pallet_unselect',
							disabled: false,
							handler: function(button){
								var gridpanel = button.up('gridpanel');
								var gridview = gridpanel.getView();
								var selmodel = gridpanel.getSelectionModel();
								gridview.saveScrollState();
								selmodel.deselectAll();
								gridview.restoreScrollState();
							}
						},{
							hidden: true,
							xtype: 'tbseparator'
						},{
							hidden: true,
							xtype: 'tbtext',
							style:{'cursor':'default','user-select':'none','font-weight':'normal'},
							text: 'selected'
						},{
							hidden: true,
							xtype: 'combobox',
							itemId: 'items-selected-dataindex-combobox',
							disabled: false,
							hideLabel: true,
							store: Ext.create('Ext.data.ArrayStore', {
								fields: ['value','text'],
								data : [
									[Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,'Tagged'],[Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,'Picked']
									,['not_selected','Not selected'],['all','All']	//20210205
								]
							}),
							displayField: 'text',
							valueField: 'value',
							queryMode: 'local',
							editable: false,
							width: 110,
							value: Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
							listeners: {
								change: update_selected_rows
							}
						},{
							text: 'Tagged',
							itemId: 'items-selected-tagged',
							disabled: false,
							enableToggle: true,
							toggleGroup: 'items-selected',
							pressed: true,
							listeners: {
								afterrender: function(button, eOpts){
									var combobox = button.prev('combobox#items-selected-dataindex-combobox');
									var store = combobox.getStore();
									var record = store.findRecord('text', button.text,0,false,false,true);
//									console.log('afterrender',button.text,record);
									button._combobox = combobox;
									button._store = store;
									button._record = record;
									button.fireEvent('toggle',button,button.pressed);
								},
								toggle: function( button, pressed, eOpts ){
									if(pressed){
										Ext.defer(function(){
											try{
												button._combobox.setValue(button._record.get('value'));
											}catch(e){
												console.error(e);
											}
										},100);
									}
								}
							}
						},{
							text: 'Picked',
							itemId: 'items-selected-picked',
							disabled: false,
							enableToggle: true,
							toggleGroup: 'items-selected',
							listeners: {
								afterrender: function(button, eOpts){
									var combobox = button.prev('combobox#items-selected-dataindex-combobox');
									var store = combobox.getStore();
									var record = store.findRecord('text', button.text,0,false,false,true);
//									console.log('afterrender',button.text,record);
									button._combobox = combobox;
									button._store = store;
									button._record = record;
									button.fireEvent('toggle',button,button.pressed);
								},
								toggle: function( button, pressed, eOpts ){
									if(pressed){
										Ext.defer(function(){
											try{
												button._combobox.setValue(button._record.get('value'));
											}catch(e){
												console.error(e);
											}
										},100);
									}
								}
							}
						},{
							text: 'All',
							itemId: 'items-selected-all',
							disabled: false,
							enableToggle: true,
							toggleGroup: 'items-selected',
							listeners: {
								afterrender: function(button, eOpts){
									var combobox = button.prev('combobox#items-selected-dataindex-combobox');
									var store = combobox.getStore();
									var record = store.findRecord('text', button.text,0,false,false,true);
//									console.log('afterrender',button.text,record);
									button._combobox = combobox;
									button._store = store;
									button._record = record;
									button.fireEvent('toggle',button,button.pressed);
								},
								toggle: function( button, pressed, eOpts ){
									if(pressed){
										Ext.defer(function(){
											try{
												button._combobox.setValue(button._record.get('value'));
											}catch(e){
												console.error(e);
											}
										},100);
									}
								}
							}
						},'-','->',{
							hidden: true,	//20210205
							text: 'to Canvas',
							handler: function(button){
								var gridpanel = button.up('gridpanel');
								var gridview = gridpanel.getView();
								var selmodel = gridpanel.getSelectionModel();
								var store = gridpanel.getStore();

//									var selected_records = selmodel.getSelection();
								var combobox = button.prev('combobox#items-selected-dataindex-combobox');
								var selected_dataindex = combobox.getValue();
/*
								var selected_records = Ext.Array.filter(store.getRange(), function(record){
									return record.get(selected_dataindex);
								});
*/
								var selected_records = update_selected_records();

								pallet_store.suspendEvents(true);
								match_list_store.suspendEvents(true);
								store.suspendEvents(true);
								try{
									var pallet_add_datas = [];
									var match_list_remove_records = [];

									pallet_store.each(function(pallet_record){
										clearPickedInfoRecord(pallet_record, true);
									});
									match_list_store.each(function(record){
										clearPickedInfoRecord(record, true);
									});

									Ext.Array.each(selected_records, function(record){
										var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
										if(pallet_record){
//												clearPickedInfoRecord(pallet_record, true);
										}
										else{
//												clearPickedInfoRecord(record, true);
											pallet_add_datas.push(record.getData());
										}
										var match_list_record = match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
										if(match_list_record) match_list_remove_records.push(match_list_record);
									});
//										console.log('pallet_add_datas',pallet_add_datas);
									if(pallet_add_datas.length){
										pallet_gridpanel.suspendEvent('beforedeselect');
										pallet_gridpanel.suspendEvent('beforeselect');
										try{
//												pallet_selmodel.select(pallet_store.add(pallet_add_datas));
											pallet_store.add(pallet_add_datas);
										}catch(e){
											console.error(e);
										}
										pallet_gridpanel.resumeEvent('beforedeselect');
										pallet_gridpanel.resumeEvent('beforeselect');
									}
									if(match_list_remove_records.length) match_list_store.remove(match_list_remove_records);
									store.remove(selected_records);
								}catch(e){
									console.error(e);
								}
								pallet_store.resumeEvents();
								match_list_store.resumeEvents();
								store.resumeEvents();

								self.refreshView(match_list_gridpanel.getView());
/*
								self.refreshView(pallet_gridpanel.getView());

								window_panel._update_render.cancel();
								window_panel._update_render.delay(0,null,null,[true]);

								self._update_category_dot_task.cancel();
								self._update_category_dot_task.delay(250);
								self._update_segment_dot_task.cancel();
								self._update_segment_dot_task.delay(250);
*/
							}
						},{
							text: 'COLOR',
							xtype: 'agcolorbutton',
							listeners: {
								colorchange: function(button,color){
									var gridpanel = button.up('gridpanel');
									var store = gridpanel.getStore();
//										var selmodel = gridpanel.getSelectionModel();
//										var selected_records = selmodel.getSelection();
									var combobox = button.prev('combobox#items-selected-dataindex-combobox');
									var selected_dataindex = combobox.getValue();
/*
									var selected_records = Ext.Array.filter(store.getRange(), function(record){
										return record.get(selected_dataindex);
									});
*/
									var selected_records = update_selected_records();

									store.suspendEvents(true);
									try{
										Ext.Array.each(selected_records, function(record){
											record.beginEdit();
											var modifiedFieldNames = record.set(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,'#'+color);
											record.commit(false,modifiedFieldNames);
										});
									}catch(e){
										console.error(e);
									}
									store.resumeEvents();
								}
							}
						},{
							text: 'OPACITY',
							xtype: 'agopacitybutton',
							listeners: {
								opacitychange: function(button,opacity){
									var gridpanel = button.up('gridpanel');
									var store = gridpanel.getStore();
//										var selmodel = gridpanel.getSelectionModel();
//									var selected_records = selmodel.getSelection();
									var combobox = button.prev('combobox#items-selected-dataindex-combobox');
									var selected_dataindex = combobox.getValue();
/*
									var selected_records = Ext.Array.filter(store.getRange(), function(record){
										return record.get(selected_dataindex);
									});
*/
									var selected_records = update_selected_records();

									store.suspendEvents(true);
									try{
										Ext.Array.each(selected_records, function(record){
											record.beginEdit();
											var modifiedFieldNames = record.set(Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,opacity);
											record.commit(false,modifiedFieldNames);
										});
									}catch(e){
										console.error(e);
									}
									store.resumeEvents();
								}
							}
						},{
							hidden: self.__config.IS_PUBLIC,
							text: 'DOWNLOAD',
							handler: function(button){
								var gridpanel = button.up('gridpanel');
								var store = gridpanel.getStore();
//									var selmodel = gridpanel.getSelectionModel();
//									var selected_records = selmodel.getSelection();
								var combobox = button.prev('combobox#items-selected-dataindex-combobox');
								var selected_dataindex = combobox.getValue();
/*
								var selected_records = Ext.Array.filter(store.getRange(), function(record){
									return record.get(selected_dataindex);
								});
*/
								var selected_records = update_selected_records();
								self._download(selected_records);
							}
						},{
							text: 'UNLOAD',
							handler: function(button){
								var gridpanel = button.up('gridpanel');
								var gridview = gridpanel.getView();
								var selmodel = gridpanel.getSelectionModel();
								var store = gridpanel.getStore();
								var match_list_remove_records = [];

								var undobutton = button.next('button#items-undo');
								undobutton._undobuffer = undobutton._undobuffer || [];
								let records = store.getRange();
								if(Ext.isArray(records) && records.length) undobutton._undobuffer.push(Ext.Array.map(records, function(record){ return record.getData(); }));
								undobutton.setDisabled(undobutton._undobuffer.length===0);

//									var selected_records = selmodel.getSelection();
								var combobox = button.prev('combobox#items-selected-dataindex-combobox');
								var selected_dataindex = combobox.getValue();
/*
								var selected_records = Ext.Array.filter(store.getRange(), function(record){
									return record.get(selected_dataindex);
								});
*/
								var selected_records = update_selected_records();

								match_list_store.suspendEvents(true);
								store.suspendEvents(true);
								try{
									pallet_store.each(function(pallet_record){
										clearPickedInfoRecord(pallet_record, true);
									});
									match_list_store.each(function(record){
										clearPickedInfoRecord(record, true);
									});
									Ext.Array.each(selected_records, function(record){
										var pallet_record = pallet_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
										if(pallet_record){
//												clearPickedInfoRecord(pallet_record, true);
										}
										else{
										}
										var match_list_record = match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true);
										if(match_list_record) match_list_remove_records.push(match_list_record);
									});
									if(match_list_remove_records.length) match_list_store.remove(match_list_remove_records);
									store.remove(selected_records);
								}catch(e){
									console.error(e);
								}
								match_list_store.resumeEvents();
								store.resumeEvents();

								self.refreshView(match_list_gridpanel.getView());
							}
						},{
							text: 'Undo',
							itemId: 'items-undo',
							disabled: true,
							listeners: {
								click: function(button){
									var gridpanel = button.up('gridpanel');
									var store = gridpanel.getStore();
									if(button._undobuffer.length){
										var datas = button._undobuffer.pop();
										store.removeAll(true);
										store.add(datas);
									}
									button.setDisabled(button._undobuffer.length===0);
								}
							}
						},'-',{
							text: 'DL',
							tooltip: 'Download Loaded parts List',
							handler: function(button){
								const gridpanel = button.up('gridpanel');
								const selected_records = update_selected_records();
								let contents = [];
								let column_text_arr = [];
								let column_dataIndex_arr = [];
								let line_feed_code = "\n";
								if(window.navigator.userAgent.toLowerCase().indexOf("windows nt")>=0) line_feed_code = "\r\n";
								Ext.Array.each(gridpanel.headerCt.getVisibleGridColumns(), function(column){
									let text = column.text;
									if(Ext.isEmpty(column.text) || column.text=="&#160;") return true;
									if(column.dataIndex==Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID || column.dataIndex==Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID) return true;
									column_text_arr.push(column.text);
									column_dataIndex_arr.push(column.dataIndex);
								});
//								contents.push('#'+column_text_arr.join("\t"));
								contents.push(column_text_arr.join("\t"));
								Ext.Array.each(selected_records, function(record){
									let datas = [];
									Ext.Array.each(column_dataIndex_arr, function(dataIndex){
										let value = '';
										if(dataIndex==Ag.Def.OBJ_ID_DATA_FIELD_ID){
											value = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
											if(Ext.isEmpty(value)) value = record.get(dataIndex);
										}
										else{
											value =record.get(dataIndex);
										}
										if(Ext.isArray(value)) value = Ext.Array.map(value, function(v){ if(Ext.isObject(v)){return v.id+':'+v.name; }else{ return v; }}).join(';');
										if(Ext.isEmpty(value)) value = '';
										datas.push(value);
									});
									contents.push(datas.join("\t"));
								});
								const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
								const blob = new Blob([bom, contents.join(line_feed_code)+line_feed_code], {type: 'text/tab-separated-values'});
								const url = (window.URL || window.webkitURL).createObjectURL(blob);
								const anchor = document.createElement('a');
								anchor.setAttribute('href', url);
								anchor.setAttribute('download', Ext.util.Format.format('Loaded_parts_list_{0}.tsv',Ext.util.Format.date(new Date(),"Ymd_His")));
								const mouseEvent = new MouseEvent('click', {
									bubbles: true,
									cancelable: true,
									view: window,
								});
								anchor.dispatchEvent(mouseEvent);
								(window.URL || window.webkitURL).revokeObjectURL(url);

							}
						},{
							itemId: 'items-upload',
							buttonText: 'UL',
							tooltip: 'Upload Loaded parts List',
							xtype: 'filefield',
							hideLabel: true,
							buttonOnly: true,
							handler: function(button){
/*
								var gridpanel = button.up('gridpanel');
								var store = gridpanel.getStore();
//									var selmodel = gridpanel.getSelectionModel();
//									var selected_records = selmodel.getSelection();
								var combobox = button.prev('combobox#items-selected-dataindex-combobox');
								var selected_dataindex = combobox.getValue();

								var selected_records = update_selected_records();
								self._download(selected_records);
*/
							},
							listeners: {
								change: function(filefield, value, eOpts){
									console.log('change',value);
								},
								afterrender: function(filefield, eOpts){
									const gridpanel = filefield.up('gridpanel');
									const store = gridpanel.getStore();
									$(filefield.fileInputEl.dom).change(function(e){
										//console.log($(this).val());
										if(this.files.length == 0) return;

										const file = this.files[0];
										const reader = new FileReader();
										reader.onload = function(){
											const content = reader.result;
											//filefield.reset();
											$(filefield.fileInputEl.dom).val('');
											let contents = [];
											if(Ext.isString(content) && content.length) contents = content.split(/[\r\n]+/);
											//console.log(contents);
											if(contents.length==0){
												return;
											}
											const re_head = new RegExp(/^#*(.+)$/);
											const re_fma = new RegExp(/^(FMA[0-9].+?):(.+)$/);
											if(!re_head.test(contents[0])){
												return;
											}
											let header = RegExp.$1;
											contents.shift();
											if(contents.length==0) return;

											let p = store.getProxy();
											p.extraParams = p.extraParams || {};
											let version = p.extraParams['version'];
											if(Ext.isEmpty(version) && self.DEF_MODEL_VERSION_RECORD) version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
											let ids;
											let art_ids;
											let artc_ids = {};
											if(Ag.data.renderer && version){
												ids = Ag.data.renderer[version]['ids'];
												art_ids = Ag.data.renderer[version]['art_ids'];
											}
											if(Ext.isEmpty(art_ids)) return;
											Ext.Object.each(art_ids, function(art_id,art){
												if(Ext.isObject(art) && Ext.isString(art[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID])){
													let artc_id = art[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
													artc_ids[artc_id] = Ext.Object.merge({}, art);
													artc_ids[artc_id][Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
												}
											});

											let header_hash = {};
											let header_arr = [];
											Ext.Array.each(gridpanel.headerCt.getGridColumns(), function(column){
												if(Ext.isEmpty(column.text) || column.text=="&#160;") return true;
												if(column.dataIndex==Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID || column.dataIndex==Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID) return true;
												header_hash[column.text] = column;
											});
											Ext.Array.each(header.split(/\t/), function(text){
												if(Ext.isEmpty(header_hash[text])){
													header_arr.push(undefined);
												}
												else{
													header_arr.push(header_hash[text]);
													//console.log(header_hash[text].dataIndex);
												}
											});
											let add_datas = [];
											Ext.Array.each(contents, function(content){
												if(Ext.isString(content) && Ext.String.trim(content).length==0) return true;
//												if(re_head.test(content)) return;
												let data = {};
												let imp_ids = [];
												Ext.Array.each(content.split(/\t/), function(value,index){
													if(Ext.isEmpty(value)) return true;
													if(Ext.isEmpty(header_arr[index])) return true;
													if(header_arr[index].dataIndex==Ag.Def.OBJ_ID_DATA_FIELD_ID){
														if(Ext.isString(value)) value = Ext.String.trim(value);
														if(Ext.isEmpty(value)) return true;
														if(Ext.isObject(artc_ids[value])){
															data[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = value;
															data[Ag.Def.OBJ_ID_DATA_FIELD_ID] = artc_ids[value][Ag.Def.OBJ_ID_DATA_FIELD_ID];
															data[Ag.Def.ID_DATA_FIELD_ID] = artc_ids[value][Ag.Def.ID_DATA_FIELD_ID];
														}
														else if(Ext.isObject(art_ids[value])){
															data[Ag.Def.OBJ_ID_DATA_FIELD_ID] = value;
															data[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = art_ids[value][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
															data[Ag.Def.ID_DATA_FIELD_ID] = art_ids[value][Ag.Def.ID_DATA_FIELD_ID];
														}
														if(Ext.isDefined(data[Ag.Def.ID_DATA_FIELD_ID])){
															const id = data[Ag.Def.ID_DATA_FIELD_ID];
															if(ids[id]['is_element'] && Ext.isString(ids[id][Ag.Def.NAME_DATA_FIELD_ID]) && ids[id][Ag.Def.NAME_DATA_FIELD_ID].length>0){
																data[Ag.Def.NAME_DATA_FIELD_ID] = ids[id][Ag.Def.NAME_DATA_FIELD_ID];
															}
														}
													}
													else if(header_arr[index].dataIndex==Ag.Def.ID_DATA_FIELD_ID){
														if(Ext.isString(value)) value = Ext.String.trim(value);
														if(Ext.isEmpty(value)) return true;
														if(Ext.isObject(ids[value])){
															imp_ids.push(value);
															return true;

															if(ids[value]['is_element'] && Ext.isArray(ids[value][Ag.Def.OBJ_IDS_DATA_FIELD_ID]) && ids[value][Ag.Def.OBJ_IDS_DATA_FIELD_ID].length==1){
																const art_id = ids[value][Ag.Def.OBJ_IDS_DATA_FIELD_ID][0];
																const name = ids[value][Ag.Def.NAME_DATA_FIELD_ID];
																if(Ext.isObject(art_ids[art_id])){
																	data[Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
																	data[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
																	data[Ag.Def.ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
																	data[Ag.Def.NAME_DATA_FIELD_ID] = name;
																}
															}

														}
													}
													else if(header_arr[index].dataIndex==Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID){
														if(Ext.isString(value)) value = Ext.String.trim(value);
														if(Ext.isEmpty(value)) return true;
														const c = Ext.draw.Color.fromString(value);
														if(Ext.isDefined(c)) data[header_arr[index].dataIndex] = value;
													}
													else if(header_arr[index].dataIndex==Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID){
														if(Ext.isString(value)) value = Ext.String.trim(value);
														if(Ext.isEmpty(value)) return true;
														if(Ext.isNumber(value) || Ext.isNumeric(value)){
															data[header_arr[index].dataIndex] = parseFloat(value);
														}
													}
													else if(
														header_arr[index].dataIndex == 'is_a' ||
														header_arr[index].dataIndex == 'part_of' ||
														header_arr[index].dataIndex == 'lexicalsuper'
													){
														return true;
														if(Ext.isString(value)) value = Ext.String.trim(value);
														if(Ext.isEmpty(value)) return true;
														if(re_fma.test(value)){
															data[header_arr[index].dataIndex] = [];
															Ext.Array.each(value.split(/;/), function(str){
																if(re_fma.test(str)){
																	data[header_arr[index].dataIndex].push({
																		id: RegExp.$1,
																		name: RegExp.$2
																	});
																}
															});
														}
													}
													else{
														return true;
														if(Ext.isString(value)) value = Ext.String.trim(value);
														if(Ext.isEmpty(value)) return true;
														data[header_arr[index].dataIndex] = value;
													}
												});
												if(imp_ids.length>0){
													Ext.Array.each(imp_ids, function(id){
														if(Ext.isArray(ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID]) && ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID].length>0){
															const name = ids[id][Ag.Def.NAME_DATA_FIELD_ID];
															Ext.Array.each(ids[id][Ag.Def.OBJ_IDS_DATA_FIELD_ID], function(art_id){
																if(Ext.isObject(art_ids[art_id])){
																	let hash = {};
																	hash[Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
																	hash[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
																	hash[Ag.Def.ID_DATA_FIELD_ID] = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
																	hash[Ag.Def.NAME_DATA_FIELD_ID] = ids[hash[Ag.Def.ID_DATA_FIELD_ID]].name;
																	add_datas.push(Ext.Object.merge({},data,hash));
																}
															});
														}
													});
												}
												else if(
													Ext.isString(data[Ag.Def.OBJ_ID_DATA_FIELD_ID]) &&
													data[Ag.Def.OBJ_ID_DATA_FIELD_ID].length>0 &&
													Ext.isString(data[Ag.Def.ID_DATA_FIELD_ID]) &&
													data[Ag.Def.ID_DATA_FIELD_ID].length>0
												){
													add_datas.push(data);
												}
											});
											//console.log(add_datas);
											let add_datas_hash = {};
											Ext.Array.each(add_datas, function(data){
												const art_id = data[Ag.Def.OBJ_ID_DATA_FIELD_ID];
												add_datas_hash[art_id] = Ext.Object.merge({},data);
											});

											const upload_store = Ext.data.StoreManager.lookup('canvas-upload-store');
											upload_store.removeAll();
											upload_store.add(add_datas);
											//console.log(upload_store.getRange());
											upload_store.each(function(record){
												const art_id = record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID);
												const color = record.get(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID);
												const opacity = record.get(Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID);
												if(Ext.isObject(add_datas_hash[art_id])){
													if(
														(Ext.isDefined(add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID]) && add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] != color) ||
														(Ext.isDefined(add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID]) && add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] != opacity)
													){
														record.beginEdit();
														if(add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] != color) record.set(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID]);
														if(add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] != opacity) record.set(Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,add_datas_hash[art_id][Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID]);
														record.commit(false,[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID]);
													}
												}
											});

											var exists_datas = {};
											Ext.Array.each(store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });

											let datas = Ext.Array.map(
												Ext.Array.filter(
													upload_store.getRange(),
													function(item){
														return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
													}
												),
												function(item){
													return item.getData();
												}
											);
											if(datas.length) store.add(datas);
											upload_store.removeAll();


										};
										reader.readAsText(file);

									});
								}
							}
						},'-',{
							xtype: 'tbtext',
							itemId: 'items-selected-tbtext',
							style:{'cursor':'default','user-select':'none','font-weight':'normal'},
							text: '0 / 0'
						}]
					}]);
				}
			}
		};

		var search_neighbor_panel_config = {

			title: 'Search Neighbor',
//					itemId: 'search-neighbor-gridpanel',
			itemId: 'search-neighbor-panel',
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
			items: [{
				itemId: 'neighbor-fieldcontainer',
				xtype: 'fieldcontainer',
				layout: 'fit',
				defaults: {
					labelAlign: 'right',
					labelWidth: 80,
				},
				items: [{
					hidden: true,
					xtype: 'fieldcontainer',
					items: [{
						itemId: 'neighbor-radius-numberfield',
						xtype: 'numberfield',
						fieldLabel: 'Set radius of search sphere : Radius(mm)',
						labelAlign: 'right',
						labelWidth: 280,
						width: 346,
						value: 10,
						maxValue: 50,
						minValue: 5,
						step: 5,
					}]
				},{
					xtype: 'fieldcontainer',
					items: [{
						itemId: 'neighbor-radius-radiogroup',
						xtype: 'radiogroup',
						columns: [60,80],
						fieldLabel: 'Set radius of search sphere : Radius',
						labelAlign: 'right',
						labelWidth: 280,
						items: [
							{ boxLabel: '5mm', name: 'neighbor-radius', inputValue: '5', checked: true},
							{ boxLabel: '10mm', name: 'neighbor-radius', inputValue: '10' },
						]
					}]
				},{
					xtype: 'fieldcontainer',
					layout: {
						type: 'hbox',
						align: 'middle'
					},
//							defaultMargins: {top: 0, right: 0, bottom: 0, left: 0},
					defaultType: 'displayfield',
//							defaultType: 'numberfield',
					defaults: {
						labelAlign: 'right',
						labelWidth: 20,
						width: 80,
//							labelStyle: 'color:#FFFFFF;',
//							fieldStyle: 'color:#FFFFFF;'
					},
					fieldLabel: 'Set center for the sphere (by picking on image)',
					labelAlign: 'right',
					labelWidth: 280,
					items: [{
						itemId: 'neighbor-x-numberfield',
						fieldLabel: 'X'
					},{
						itemId: 'neighbor-y-numberfield',
						fieldLabel: 'Y'
					},{
						itemId: 'neighbor-z-numberfield',
						fieldLabel: 'Z'
					}],
					listeners: {
						afterrender: function(fieldcontainer, eOpts){
								var window_panel = fieldcontainer.up('panel#window-panel');
								var render_panel = window_panel.down('panel#main-render-panel');
								var func = function(){
//											console.log(render_panel.rendered,render_panel.__webglMainRenderer);
									if(render_panel.__webglMainRenderer && render_panel.__webglMainRenderer instanceof Ag.MainRenderer){
										render_panel.__webglMainRenderer.on({
											pick: function(ren,intersects,e){
//														console.log(ren,intersects,e);

												var activeTab = fieldcontainer.up('tabpanel').getActiveTab();
												if(activeTab && activeTab.itemId=='search-neighbor-panel'){
													var button = fieldcontainer.up('fieldcontainer#neighbor-fieldcontainer').down('button#load-neighbor-button');
													if(button){
														button.setDisabled(intersects.length==0);
														if(button.isDisabled()){
															fieldcontainer.down('displayfield#neighbor-x-numberfield').setValue('');
															fieldcontainer.down('displayfield#neighbor-y-numberfield').setValue('');
															fieldcontainer.down('displayfield#neighbor-z-numberfield').setValue('');
															return;
														}
														fieldcontainer.down('displayfield#neighbor-x-numberfield').setValue(Ext.util.Format.number(intersects[0].point.x,'0.000'));
														fieldcontainer.down('displayfield#neighbor-y-numberfield').setValue(Ext.util.Format.number(intersects[0].point.y,'0.000'));
														fieldcontainer.down('displayfield#neighbor-z-numberfield').setValue(Ext.util.Format.number(intersects[0].point.z,'0.000'));
														button.fireEvent('click',button);
													}
												}
											}
										});
									}
									else{
										Ext.callback(func,this,null,100);
									}
								};
								if(render_panel.rendered){
									func();
								}
								else{
									render_panel.on({
										afterrender: function(panel, eOpts){
											func();
										},
										single: true
									});
								}
						}
					}

				},{
					hidden: true,
					xtype: 'fieldcontainer',
//							padding: '0 0 0 280',
					layout: 'hbox',
					fieldLabel: 'Load items overlaps the sphere',
					labelAlign: 'right',
					labelWidth: 280,
					items: [{

						hidden: true,
						width: 100,
						editable: false,
						itemId: 'segment-neighbor-filtering-combobox',
						xtype: 'combobox',
						store: Ext.create('Ext.data.Store', {
							fields: ['value', 'display'],
							data : [
								{"value":"SEG2ART", "display":"All Polygon"},
								{"value":"SEG2ART_INSIDE", "display":"Centroid"}
							]
						}),
						queryMode: 'local',
						displayField: 'display',
						valueField: 'value',
						value: self.DEF_SEGMENT_NEIGHBOR_FILTER,
						listeners: {
							change: function( field, newValue, oldValue, eOpts ){
								self.DEF_SEGMENT_NEIGHBOR_FILTER = newValue;
							},
							select: function( field, records, eOpts ){
							}
						}

					},{
						xtype: 'button',
//								text: 'Load items overlaps the sphere',
						text: 'Search',
						itemId: 'load-neighbor-button',
//								width: 346,
						disabled: true,
						listeners: {

							click: function(button){
//										var window_panel = button.up('panel#window-panel');
								var fieldcontainer = button.up('fieldcontainer#neighbor-fieldcontainer');
								if(fieldcontainer.isDisabled()) return;
								var point = {
									x: parseFloat(fieldcontainer.down('displayfield#neighbor-x-numberfield').getValue()),
									y: parseFloat(fieldcontainer.down('displayfield#neighbor-y-numberfield').getValue()),
									z: parseFloat(fieldcontainer.down('displayfield#neighbor-z-numberfield').getValue())
								};
//										var voxel_range = parseInt(fieldcontainer.down('numberfield#neighbor-radius-numberfield').getValue(), 10);
								var voxel_range = parseInt(fieldcontainer.down('radiogroup#neighbor-radius-radiogroup').getValue()['neighbor-radius'], 10);
								var store = Ext.data.StoreManager.lookup('canvas-neighbor-parts-store');
								var p = store.getProxy();
								var extraParams = Ext.Object.merge({},p.extraParams || {});

//										fieldcontainer.setLoading(true);
								fieldcontainer.setDisabled(true);

								extraParams[Ag.Def.OBJ_POINT_FIELD_ID] = Ext.JSON.encode(point);
								extraParams[Ag.Def.VOXEL_RANGE_FIELD_ID] = voxel_range;
//										extraParams['SEG2ART'] = fieldcontainer.down('combobox#segment-neighbor-filtering-combobox').getValue();
//										p.extraParams = extraParams;
								store.loadPage(1, {
									params: extraParams,
									callback: function(records, operation, success){
										console.log(records, operation, success);
//												fieldcontainer.setLoading(false);
										fieldcontainer.setDisabled(false);
										if(success && records.length){
/**/
											var window_panel         = button.up('panel#window-panel');
											var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
											var match_list_store     = match_list_gridpanel.getStore();
											var match_list_view      = match_list_gridpanel.getView();

											store.suspendEvents(false);
											Ext.Array.each(records,function(neighbor_record){
												if(!Ext.isEmpty(match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, neighbor_record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true))){
													neighbor_record.beginEdit();
													neighbor_record.set(Ag.Def.EXISTS_PALETTE_FIELD_ID, true);
													neighbor_record.commit(false,[Ag.Def.EXISTS_PALETTE_FIELD_ID]);
												}
											});
											store.resumeEvents();
											var neighbor_gridpanel = button.up('panel#search-neighbor-panel').down('gridpanel#canvas-neighbor-parts-gridpanel');
											self.refreshView(neighbor_gridpanel.getView());
/**/
										}
									}
								});
							}

						}
					}]
				}]

			},{
				flex: 1,
				xtype: 'gridpanel',
				itemId: 'canvas-neighbor-parts-gridpanel',
				store: Ext.data.StoreManager.lookup('canvas-neighbor-parts-store'),
				viewConfig: self.getViewConfig(),
				columnLines: true,
				selModel: {
	//						mode : 'SIMPLE'
					mode : 'MULTI'
				},
				dockedItems: [{
	//				hidden: true,
					xtype: 'toolbar',
					dock: 'bottom',
					ui: 'footer',
					itemId: 'bottom',
					items: [
					'->'
					,{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'bold'},
						text: 'Load / Render'
					}
					,{
						xtype: 'button',
						text: 'Selected',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#search-neighbor-panel').down('gridpanel#canvas-neighbor-parts-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									add: function(store, records, index, eOpts){
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										if(store.getCount()==0) button.setDisabled(true);
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										button.setDisabled(selected.length==0 ? true : false);
									}
								});
								button.setDisabled(true);
							},
							click: function(button){
								var gridpanel = button.up('panel#search-neighbor-panel').down('gridpanel#canvas-neighbor-parts-gridpanel');
								var segment_grid_store = gridpanel.getStore();
								var selmodel           = gridpanel.getSelectionModel();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												selmodel.getSelection(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										segment_grid_store.removeAll();
									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,{
						xtype: 'button',
						text: 'All',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#search-neighbor-panel').down('gridpanel#canvas-neighbor-parts-gridpanel');
								var store     = gridpanel.getStore();
								store.on({
									load: function(store,records,successful,eOpts){
										button.setDisabled(store.getCount()==0 ? true : false);
									},
									add: function(store, records, index, eOpts){
										button.setDisabled(store.getCount()==0 ? true : false);
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										button.setDisabled(store.getCount()==0 ? true : false);
									}
								});
								button.setDisabled(store.getCount()==0 ? true : false);
							},
							click: function(button){
								var gridpanel = button.up('panel#search-neighbor-panel').down('gridpanel#canvas-neighbor-parts-gridpanel');
								var segment_grid_store = gridpanel.getStore();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												segment_grid_store.getRange(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										segment_grid_store.removeAll();


									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,'-',{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'normal'},
						text: '0 / 0',
						listeners: {
							afterrender: function(tbtext){
	//							console.log('afterrender',tbtext);
								var gridpanel = tbtext.up('panel#search-neighbor-panel').down('gridpanel#canvas-neighbor-parts-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									load: function(store,records,successful,eOpts){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									add: function(store, records, index, eOpts){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										tbtext.setText(Ext.util.Format.format('{0} / {1}',Ext.util.Format.number(selected.length,'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
							}
						}
					}
					]
				}],
				columns: [

					{
						text: 'palette',
						tooltip: 'exists palette',
//						xtype: 'agcheckcolumn',
						dataIndex: Ag.Def.EXISTS_PALETTE_FIELD_ID,
						align: 'center',
						width: 34,
						locked: false,
						lockable: false,
						draggable: false,
						sortable: true,
						hideable: false,
						hidden: true,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							return Ext.util.Format.format('<span class="glyphicon {0} neighbor-gridpanel-column-{2}" aria-hidden="true" data-fmaid="{1}" data-qtip="exists palette" style="cursor:pointer;"></span>', value===true ? 'glyphicon-check' :'glyphicon-unchecked', record.get(Ag.Def.ID_DATA_FIELD_ID), Ag.Def.EXISTS_PALETTE_FIELD_ID);
						}
					},

					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
//								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-obj';
//								console.log(value, rowIndex, colIndex);
							var rtn;
							var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
							if(Ext.isString(artc_id) && artc_id.length){
								rtn = artc_id;
							}
							else{
								rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
							}
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
					{
						text: 'FMAID',
						tooltip: 'FMAID',
						dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: false,
						width: 63,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
//							var rtn = value;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;
//							return rtn;
							var rtn = record.get(Ag.Def.ID_DATA_FIELD_ID+'_renderer');

							if(Ext.isString(rtn) && rtn.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
							}
							return rtn;

						}
					},
					{
						text: 'SUB',
						tooltip: 'SUB',
						dataIndex: 'sub'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-sub');
							}
							return value;
						}
					},
					{
						text: 'R/L',
						tooltip: 'R/L',
						dataIndex: 'laterality'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//									return make_ag_word(value,dataIndex,null,'bp3d-laterality');
								return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.NAME_DATA_FIELD_ID,
						tooltip: Ag.Def.NAME_DATA_FIELD_ID,
						dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: false,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							if(Ext.isString(value) && value.length){
//									return make_ag_word(value,null,'bp3d-name');
//										console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-name',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.SYNONYM_DATA_FIELD_ID,
						tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
						dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: true,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex);
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',false)
					,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',false)
					,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',false)
					,
					{
						text: 'Segment',
						tooltip: 'Segment',
//							dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: 'segment',
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						width: 50,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex,null,'bp3d-segment');
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment'));
									}
									else if(Ext.isNumber(value[i])){
										rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment'));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,{
						hidden: true,
						hideable: false,
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-category');
							}
							return value;
						}
					}
					,{
//							text: 'System',
//							tooltip: 'System',
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
							value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
							if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
							if(Ext.isString(value) && value.length){
//								if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//								if(value.match(/^_+(.+)$/)) value = RegExp.$1;
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
//								return value;
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-system');
							}
							return value;
						}
					}
					,{
						text: self.DEF_DISTANCE_LABEL,
						dataIndex: Ag.Def.DISTANCE_FIELD_ID,
						width: 60,
						xtype: 'numbercolumn',
						format:'0.0000'
					},
				],
				plugins: [
					Ext.create('Ext.grid.plugin.CellEditing', {
						clicksToEdit: 1,
						listeners: {
							beforeedit: function(editor,e,eOpts){
							},
							edit: function(editor,e,eOpts){
								console.log(e);
							}
						}
					}),
					self.getBufferedRenderer({pluginId: 'canvas-neighbor-parts-gridpanel-plugin'})
				],
				listeners: {
					afterrender: function( gridpanel, eOpts ){
						gridpanel.getView().on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							}
						});
						var store = gridpanel.getStore();
						store.removeAll();	//emptyTextが表示されない為、あえてクリアする
						var selmodel     = gridpanel.getSelectionModel();
						var gridview     = gridpanel.getView();
						var $gridviewdom = $(gridview.el.dom);

						$gridviewdom.on('mousedown','a.bp3d-word-button', function(e){
							var $this = $(this);
							gridpanel.setLoading('searching...');
							Ext.defer(function(){

								var value = $this.attr('data-value');
								var dataIndex = $this.attr('data-dataIndex');
								if(dataIndex==Ag.Def.ID_DATA_FIELD_ID) dataIndex = Ag.Def.ID_DATA_FIELD_ID+'_renderer';
								if(dataIndex==Ag.Def.SYSTEM_ID_DATA_FIELD_ID) dataIndex = Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer';
//								console.log(dataIndex,value);
								var $tr = $this.closest('tr.x-grid-data-row');
								var $tbody = $tr.closest('tbody');
								var record = gridview.getRecord($tr.get(0));
								if(record){
//									gridview.saveScrollState();
//									gridpanel.suspendEvents(false);
									try{
	//									var value = record.get(dataIndex);
										var isSelected = selmodel.isSelected(record);
//										console.log(dataIndex,value,isSelected);
										var records = [];
										var startIndex = -1;
										var record;
										do {
											startIndex = store.findBy( function(record,id){
												var f_value = record.get(dataIndex);
												if(Ext.isString(value) && Ext.isString(f_value)){
													return value===f_value;
												}
												else if(Ext.isString(value) && Ext.isArray(f_value)){
													var rtn = false;
													Ext.Array.each( f_value, function(item,index,array){
														if(Ext.isString(item)){
															rtn = item===value;
														}
														else{
															rtn = item.name===value;
														}
														if(rtn) return false;
													});
													return rtn;
												}
											}, self, ++startIndex);
											record = null;
											if(startIndex>=0) record = store.getAt(startIndex);
	//										console.log(startIndex,record,isSelected);
											if(record) records.push(record);
										} while(startIndex>=0)
	//									console.log(records);
										if(isSelected){
											selmodel.select(records,true);
										}
										else{
											selmodel.deselect(records);
										}
									}catch(e){
										console.error(e);
									}
//									gridview.refresh();
//									gridview.restoreScrollState();
								}
								gridpanel.setLoading(false);
							}, 100);

							e.preventDefault();
							e.stopPropagation();
							e.stopImmediatePropagation()
							return false;
						});
					}
				}
			}],
			listeners: {
				afterrender: function( panel, eOpts ){
				},
				activate: function( panel, eOpts ){
				}
			}
		};

		var keyword_search_panel_config = {
			title: 'Keyword Search',
//					itemId: 'search-neighbor-gridpanel',
			itemId: 'keyword-search-panel',
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
			dockedItems: [{
				dock: 'top',
				minHeight: 16,
				items: [{
					xtype: 'tbtext',
					itemId: 'keyword-search-tbtext',
					style:{'cursor':'default','user-select':'none'},
					listeners: {
						afterrender: function(field){
							var viewport = Ext.getCmp('main-viewport');
							var window_panel = viewport.down('panel#window-panel');

							var window_panel_toolbar = window_panel.down('panel#north-panel');
							var version_combobox = window_panel_toolbar.down('combobox#version-combobox');
							var segment_treepicker = window_panel_toolbar.down('treepicker#segment-treepicker');
							var segment_filtering_combobox = window_panel_toolbar.down('combobox#segment-filtering-combobox');
							var search_target_radiogroup = window_panel_toolbar.down('radiogroup#search-target');

							var keyword_search_panel = window_panel.down('panel#keyword-search-panel');
							var searchfield = keyword_search_panel.down('searchfield#keyword-search-searchfield');
							var keyword_search_store = Ext.data.StoreManager.lookup('keyword-search-store')

							keyword_search_store.on({
								beforeload: function(store, operation, eOpts){
									var texts = [];
									texts.push(version_combobox.findRecordByValue(version_combobox.getValue()).get(version_combobox.displayField));
									texts.push(segment_treepicker.getValue());
									if(segment_filtering_combobox && segment_filtering_combobox.isVisible()) texts.push(segment_filtering_combobox.findRecordByValue(segment_filtering_combobox.getValue()).get(segment_filtering_combobox.displayField));
									if(search_target_radiogroup && search_target_radiogroup.isVisible()){
										var search_target_index = search_target_radiogroup.items.findIndex('inputValue', search_target_radiogroup.getValue()['searchTarget'], 0, true, true);
										texts.push( search_target_radiogroup.items.getAt(search_target_index).boxLabel );
									}
									texts.push(searchfield.getValue());
									field.setText(texts.join(' > '));
								},
								load: function(store, records, successful, eOpts){

										if(successful && records.length){
/**/
											var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
											var match_list_store     = match_list_gridpanel.getStore();
											var match_list_view      = match_list_gridpanel.getView();

											store.suspendEvents(false);
											Ext.Array.each(records,function(neighbor_record){
												if(!Ext.isEmpty(match_list_store.findRecord(Ag.Def.ID_DATA_FIELD_ID, neighbor_record.get(Ag.Def.ID_DATA_FIELD_ID), 0, false, false, true))){
													neighbor_record.beginEdit();
													neighbor_record.set(Ag.Def.EXISTS_PALETTE_FIELD_ID, true);
													neighbor_record.commit(false,[Ag.Def.EXISTS_PALETTE_FIELD_ID]);
												}
											});
											store.resumeEvents();
											var neighbor_gridpanel = keyword_search_panel.down('gridpanel#keyword-search-gridpanel');
											self.refreshView(neighbor_gridpanel.getView());
/**/
										}

								}
							});

						}
					}
				}]
			}],
			items: [{
				xtype: 'fieldcontainer',
				layout: {
					type: 'hbox',
					align: 'middle'
				},
				items: [{
					flex: 1,
					itemId: 'keyword-search-searchfield',
					xtype: 'localsearchfield',
					store: Ext.data.StoreManager.lookup('keyword-search-store'),
					margin: '4 4 4 4',
					selectOnFocus: true,
					onTrigger2Click : function(){
						let me = this;
						let value = me.getValue();
						let searchcolumns = me.up('panel#keyword-search-panel').down('checkboxgroup#keyword-search-checkboxgroup').getValue()['searchcolumns'];
						if(Ext.isString(searchcolumns) && searchcolumns.length) searchcolumns = [searchcolumns];
	//					console.log(searchcolumns);
						if (value.length > 0 && self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model && Ext.isArray(searchcolumns) && searchcolumns.length) {

							let gridpanel = me.up('panel#keyword-search-panel').down('gridpanel#keyword-search-gridpanel');
							let checkboxgroup = me.up('panel#keyword-search-panel').down('checkboxgroup#keyword-search-checkboxgroup');
							gridpanel.setLoading('searching...');
							checkboxgroup.setDisabled(true);
							Ext.defer(function(){
								try{

									let display = self.DEF_MODEL_VERSION_RECORD.get('display');
									let tbtext = me.up('panel#keyword-search-panel').down('tbtext#keyword-search-tbtext');

									let texts = [];
									texts.push(display);
									texts.push(value);
									tbtext.setText(texts.join(' > '));

									let filters = [];
									let re_arr = [];
									re_arr.push(new RegExp(/"(.+?)"/));
									re_arr.push(new RegExp(/'(.+?)'/));
									re_arr.push(new RegExp(/\((.+?)\)/));
									let re_sp = new RegExp(/\s+/);
									Ext.Array.each(re_arr, function(re){
										while(re.test(value)){
											console.log(RegExp.lastMatch);
											let text = Ext.String.escapeRegex(RegExp.$1);
											value = RegExp.leftContext + RegExp.rightContext;
											while(re_sp.test(text)){
												text = text.replace(re_sp,'\\s+');
											}
											filters.push(new RegExp('\\b'+text+'\\b','i'));
										}
									});
									Ext.Array.each(value.split(/\s+/), function(v){
										filters.push(new RegExp(Ext.String.escapeRegex(Ext.String.trim(v)),'i'));
									});

									me.store.clearFilter(true);
									me.store.removeAll(true);
									me.store.add(Ext.Object.getValues(Ag.data.keyword_search[display]));
									me.store.filter({
										filterFn: function(record){
											let rtn = false;
											Ext.Array.each(searchcolumns, function(c){
												let vs = record.get(c);
												if(Ext.isString(vs)) vs = [vs];
												Ext.Array.each(vs, function(v){
													if(Ext.isString(v)){
														if(Ext.Array.every(filters, function(f){
			//												console.log(f,v,f.test(v));
															return f.test(v);
														})){
															rtn = true;
															return false;
														}
													}
													else if(Ext.isObject(v)){
														Ext.Array.each(Ext.Object.getValues(v), function(ov){
															if(Ext.Array.every(filters, function(f){
																console.log(f,ov,f.test(ov));
																return f.test(ov);
															})){
																rtn = true;
																return false;
															}
														});
													}
													if(rtn) return false;
												});
											});
			//								if(rtn) console.log(record.get('id'),record.get('name'));
											return rtn;
										}
									});
									me.hasSearch = true;
									me.triggerCell.item(0).setDisplayed(true);
									me.updateLayout();
								}catch(e){
									console.error(e);
								}
								gridpanel.setLoading(false);
								checkboxgroup.setDisabled(false);
							},100);
						}
					}
				},{
					xtype: 'image',
					width: 16,
					height: 16,
					src: 'static/css/16x16/information.png',
					title: Ext.String.htmlEncode('use bracket " " for multi-word term')
				}]
			},{
				itemId: 'keyword-search-checkboxgroup',
				xtype: 'checkboxgroup',
				height: 24,
				fieldLabel: 'Search Columns',
				labelAlign: 'right',
				hideLabel: true,
				bodyStyle: 'white-space:nowrap;',
//				labelWidth: 95,
				columns: [45,65,60,75,48,65,110,75,75],
				defaults: {
					name: 'searchcolumns'
				},
				items: [
					{ boxLabel: 'obj', inputValue: Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID },
					{ boxLabel: 'FMAID', inputValue: Ag.Def.ID_DATA_FIELD_ID, checked: true },
					{ boxLabel: Ag.Def.NAME_DATA_FIELD_ID, inputValue: Ag.Def.NAME_DATA_FIELD_ID, checked: true },
					{ boxLabel: Ag.Def.SYNONYM_DATA_FIELD_ID, inputValue: Ag.Def.SYNONYM_DATA_FIELD_ID },
					{ boxLabel: 'is_a', inputValue: 'is_a' },
					{ boxLabel: 'part_of', inputValue: 'part_of' },
					{ boxLabel: 'nominal super', inputValue: 'lexicalsuper' },
					{ boxLabel: 'Segment', inputValue: 'segment' },
					{ boxLabel: 'Category', inputValue: Ag.Def.SYSTEM_ID_DATA_FIELD_ID }
				]
			},{
				flex: 1,
				xtype: 'gridpanel',
				itemId: 'keyword-search-gridpanel',
				store: Ext.data.StoreManager.lookup('keyword-search-store'),
				viewConfig: self.getViewConfig(),
				columnLines: true,
				selModel: {
	//						mode : 'SIMPLE'
					mode : 'MULTI'
				},
				dockedItems: [{
					xtype: 'toolbar',
					dock: 'bottom',
					ui: 'footer',
					itemId: 'bottom',
					items: [
					{
						hidden: true,
						xtype: 'button',
						text: 'Download',
						minWidth: 68,
						listeners: {
							click: function(button){
								if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
									let display = self.DEF_MODEL_VERSION_RECORD.get('display');
									let cities_store = Ext.data.StoreManager.lookup('cities-list-store');
									let system_list_store = Ext.data.StoreManager.lookup('system-list-store');

									let viewport = self.getViewport();
									let window_panel         = viewport.down('panel#window-panel');
									let segment_filtering_combobox = window_panel.down('combobox#segment-filtering-combobox');
									let segment_filtering_value = segment_filtering_combobox.getValue();
									let SEG2ART = segment_filtering_value==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

									let ids = Ag.data.renderer[display]['ids'];
									let art_ids = Ag.data.renderer[display]['art_ids'];
									if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
										if(Ext.isEmpty(ids)) console.warn('ids is empty!!');
										if(Ext.isEmpty(art_ids)) console.warn('art_ids is empty!!');
										return;
									}

									let name2cities = {};
									let cities = Ext.Array.map(cities_store.getRange(),function(record){
										let data = record.getData();
										name2cities[data['name']] = data;
										return data;
									});
//									console.log('name2cities', name2cities);

									let system_id2name = {};
									system_list_store.each(function(record){
										let system_id = (record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID).split('/'))[0];
										let system_name = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
										if(system_name.match(/^[0-9]+(.+)$/)) system_name = RegExp.$1;
										if(system_name.match(/^_+(.+)$/)) system_name = RegExp.$1;
										system_id2name[system_id] = system_name;
									});
//									console.log('system_id2name', system_id2name);

									let seg2art = {};
									Ext.Object.each(SEG2ART['CITIES'], function(key,value){
										Ext.Array.map(Ext.Object.getKeys(value), function(art_id){ seg2art[art_id] = true; });
									});

									let use_ids;
									Ext.Object.each(ids, function(id, id_data, myself) {
										if(!Ext.isObject(ids[id])) return true;
										if(Ext.isEmpty(use_ids)) use_ids = {};

										if(Ext.isEmpty(use_ids[id])){
											var tempobj = {};
											use_ids[id] = Ext.Object.merge(tempobj, ids[id]);
										}
										let art_id = null;
										let artc_id = null;
										if(Ext.isBoolean(ids[id]['is_element']) && ids[id]['is_element']){
											art_id = ids[id]['art_ids'][0];
											artc_id = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
										}
										use_ids[id][Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
										use_ids[id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = artc_id;

										let system_id = ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID];
										if(Ext.isString(system_id) && system_id.length){
											use_ids[id]['system_name'] = system_id2name[system_id];
										}

//										let synonym = ids[id]['synonym'];
//										if(Ext.isString(synonym) && synonym.length){
//											delete use_ids[id]['synonym'];
//											use_ids[id]['synonym'] = Ext.Array.map(synonym.split(';'), function(str){ return Ext.String.trim(str); });
//										}

										use_ids[id]['segment'] = null;
										if(Ext.isObject(Ag.data.MENU_SEGMENTS_in_art_file[art_id])){
											let segment_hash = {};
											Ext.Array.each(Ext.Object.getKeys(Ag.data.MENU_SEGMENTS_in_art_file[art_id]['CITIES'] || {}), function(cities_name){
												var cities_id = name2cities[cities_name]['cities_id'];
												if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) segment_hash[Ag.data.citiesids2segment[cities_id]] = null;
											});
											let segment = Ext.Object.getKeys(segment_hash);
											if(Ext.isArray(segment) && segment.length) use_ids[id]['segment'] = segment.join('; ');
										}

										if(Ext.isObject(use_ids[id]['relation'])){
											Ext.Object.each(use_ids[id]['relation'], function(relation,value){
												if(Ext.isObject(value)){
													Ext.Object.each(value, function(rid,rname){
														var v = use_ids[id][relation];
														if(Ext.isEmpty(v)){
															v = [rid+':'+rname];
														}
														else{
															v.push(rid+':'+rname);
														}
														use_ids[id][relation] = v;

														if(relation == 'is_a' || relation == 'lexicalsuper') return true;
														v = use_ids[id]['part_of'];
														if(Ext.isEmpty(v)){
															v = [rid+':'+rname];
														}
														else{
															v.push(rid+':'+rname);
														}
														use_ids[id]['part_of'] = v;
													});
												}
											});
											Ext.Array.each(['is_a','part_of','lexicalsuper'],function(relation){
												if(Ext.isArray(use_ids[id][relation])) use_ids[id][relation] = use_ids[id][relation].join('; ');
											});
										}
									});
//									console.log(use_ids);

									let line_feed_code = "\n";
									if(window.navigator.userAgent.toLowerCase().indexOf("windows nt")>=0) line_feed_code = "\r\n";
									const filename = 'mapping.tsv';
									const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
									let mapping_data = ['#obj','FMAID',Ag.Def.NAME_DATA_FIELD_ID,Ag.Def.SYNONYM_DATA_FIELD_ID,'is_a','part_of','nominal super','Segment','Category'].join("\t")+line_feed_code;
									let dataIndexs = [
										 Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID
										,Ag.Def.ID_DATA_FIELD_ID
										,Ag.Def.NAME_DATA_FIELD_ID
										,Ag.Def.SYNONYM_DATA_FIELD_ID
										,'is_a'
										,'part_of'
										,'lexicalsuper'
										,'segment'
										,'system_name'
									];
									Ext.Object.each(use_ids, function(id) {
										let arr = [];
										Ext.Array.each(dataIndexs, function(dataIndex){
											arr.push(use_ids[id][dataIndex] || '');
										});
										mapping_data += arr.join("\t")+line_feed_code;
									});

									const blob = new Blob([bom, mapping_data], { type: 'text/tab-separated-values' });

									const url = (window.URL || window.webkitURL).createObjectURL(blob);
									const download = document.createElement("a");
									download.href = url;
									download.download = filename;
									download.click();
									(window.URL || window.webkitURL).revokeObjectURL(url);

								}
							}
						}
					},
					'->'
					,{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'bold'},
						text: 'Load / Render'
					}
					,{
						xtype: 'button',
						text: 'Selected',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#keyword-search-panel').down('gridpanel#keyword-search-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									add: function(store, records, index, eOpts){
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										if(store.getCount()==0) button.setDisabled(true);
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										button.setDisabled(selected.length==0 ? true : false);
									}
								});
								button.setDisabled(true);
							},
							click: function(button){
								var gridpanel = button.up('panel#keyword-search-panel').down('gridpanel#keyword-search-gridpanel');
								var segment_grid_store = gridpanel.getStore();
								var selmodel           = gridpanel.getSelectionModel();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												selmodel.getSelection(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										segment_grid_store.removeAll();
									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,{
						xtype: 'button',
						text: 'All',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#keyword-search-panel').down('gridpanel#keyword-search-gridpanel');
								var store     = gridpanel.getStore();
								store.on({
									load: function(store,records,successful,eOpts){
										button.setDisabled(store.getCount()==0 ? true : false);
									},
									add: function(store, records, index, eOpts){
										button.setDisabled(store.getCount()==0 ? true : false);
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										button.setDisabled(store.getCount()==0 ? true : false);
									}
								});
								button.setDisabled(store.getCount()==0 ? true : false);
							},
							click: function(button){
								var gridpanel = button.up('panel#keyword-search-panel').down('gridpanel#keyword-search-gridpanel');
								var segment_grid_store = gridpanel.getStore();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												segment_grid_store.getRange(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										segment_grid_store.removeAll();


									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,'-',{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'normal'},
						text: '0 / 0',
						listeners: {
							afterrender: function(tbtext){
	//							console.log('afterrender',tbtext);
								var gridpanel = tbtext.up('panel#keyword-search-panel').down('gridpanel#keyword-search-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									load: function(store,records,successful,eOpts){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									add: function(store, records, index, eOpts){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									filterchange: function( store, filters, eOpts ){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										tbtext.setText(Ext.util.Format.format('{0} / {1}',Ext.util.Format.number(selected.length,'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
							}
						}
					}
					]
				}],
				columns: [

					{
						text: 'palette',
						tooltip: 'exists palette',
//						xtype: 'agcheckcolumn',
						dataIndex: Ag.Def.EXISTS_PALETTE_FIELD_ID,
						align: 'center',
						width: 34,
						locked: false,
						lockable: false,
						draggable: false,
						sortable: true,
						hideable: false,
						hidden: true,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							return Ext.util.Format.format('<span class="glyphicon {0} keyword-search-gridpanel-column-{2}" aria-hidden="true" data-fmaid="{1}" data-qtip="exists palette" style="cursor:pointer;"></span>', value===true ? 'glyphicon-check' :'glyphicon-unchecked', record.get(Ag.Def.ID_DATA_FIELD_ID), Ag.Def.EXISTS_PALETTE_FIELD_ID);
						}
					},
/*
					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
//								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-obj';
//								console.log(value, rowIndex, colIndex);
							var rtn;
							var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
							if(Ext.isString(artc_id) && artc_id.length){
								rtn = artc_id;
							}
							else{
								rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
							}
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
*/
					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							var rtn = value;
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
					{
						text: 'FMAID',
						tooltip: 'FMAID',
						dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: false,
						width: 63,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
//							var rtn = value;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;
//							return rtn;
							var rtn = record.get(Ag.Def.ID_DATA_FIELD_ID+'_renderer');
							if(Ext.isString(rtn) && rtn.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
							}
							return rtn;

						}
					},
					{
						text: 'SUB',
						tooltip: 'SUB',
						dataIndex: 'sub'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-sub');
							}
							return value;
						}
					},
					{
						text: 'R/L',
						tooltip: 'R/L',
						dataIndex: 'laterality'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//									return make_ag_word(value,dataIndex,null,'bp3d-laterality');
								return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.NAME_DATA_FIELD_ID,
						tooltip: Ag.Def.NAME_DATA_FIELD_ID,
						dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: false,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
//							console.log(store);
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							if(Ext.isString(value) && value.length){
//									return make_ag_word(value,null,'bp3d-name');
//										console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-name',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.SYNONYM_DATA_FIELD_ID,
						tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
						dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: true,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
							if(Ext.isArray(value)){
								return value.join('; ');
							}
							else{
								return value;
							}
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex);
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',false)
					,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',false)
					,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',false)
					,
					{
						text: 'Segment',
						tooltip: 'Segment',
//							dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: 'segment',
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: true,
						width: 50,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex,null,'bp3d-segment');
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment'));
									}
									else if(Ext.isNumber(value[i])){
										rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment'));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,{
						hidden: true,
						hideable: false,
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-category');
							}
							return value;
						}
					}
					,{
//							text: 'System',
//							tooltip: 'System',
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
							value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
							if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
							if(Ext.isString(value) && value.length){
//								if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//								if(value.match(/^_+(.+)$/)) value = RegExp.$1;
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
//								return value;
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-system');
							}
							return value;
						}
					}
				],
				plugins: [
					Ext.create('Ext.grid.plugin.CellEditing', {
						clicksToEdit: 1,
						listeners: {
							beforeedit: function(editor,e,eOpts){
							},
							edit: function(editor,e,eOpts){
								console.log(e);
							}
						}
					}),
					self.getBufferedRenderer({pluginId: 'keyword-search-gridpanel-plugin'})
				],
				listeners: {
					afterrender: function( gridpanel, eOpts ){
						gridpanel.getView().on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							}
						});

						var store = gridpanel.getStore();
						store.removeAll();	//emptyTextが表示されない為、あえてクリアする
						var selmodel     = gridpanel.getSelectionModel();
						var gridview     = gridpanel.getView();
						var $gridviewdom = $(gridview.el.dom);

						$gridviewdom.on('mousedown','a.bp3d-word-button', function(e){
							var $this = $(this);
							gridpanel.setLoading('searching...');
							Ext.defer(function(){

								var value = $this.attr('data-value');
								var dataIndex = $this.attr('data-dataIndex');
								if(dataIndex==Ag.Def.ID_DATA_FIELD_ID) dataIndex = Ag.Def.ID_DATA_FIELD_ID+'_renderer';
								if(dataIndex==Ag.Def.SYSTEM_ID_DATA_FIELD_ID) dataIndex = Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer';
//								console.log(dataIndex,value);
								var $tr = $this.closest('tr.x-grid-data-row');
								var $tbody = $tr.closest('tbody');
								var record = gridview.getRecord($tr.get(0));
								if(record){
//									gridview.saveScrollState();
//									gridpanel.suspendEvents(false);
									try{
	//									var value = record.get(dataIndex);
										var isSelected = selmodel.isSelected(record);
//										console.log(dataIndex,value,isSelected);
										var records = [];
										var startIndex = -1;
										var record;
										do {
											startIndex = store.findBy( function(record,id){
												var f_value = record.get(dataIndex);
												if(Ext.isString(value) && Ext.isString(f_value)){
													return value===f_value;
												}
												else if(Ext.isString(value) && Ext.isArray(f_value)){
													var rtn = false;
													Ext.Array.each( f_value, function(item,index,array){
														if(Ext.isString(item)){
															rtn = item===value;
														}
														else{
															rtn = item.name===value;
														}
														if(rtn) return false;
													});
													return rtn;
												}
											}, self, ++startIndex);
											record = null;
											if(startIndex>=0) record = store.getAt(startIndex);
	//										console.log(startIndex,record,isSelected);
											if(record) records.push(record);
										} while(startIndex>=0)
	//									console.log(records);
										if(isSelected){
											selmodel.select(records,true);
										}
										else{
											selmodel.deselect(records);
										}
									}catch(e){
										console.error(e);
									}
//									gridview.refresh();
//									gridview.restoreScrollState();
								}
								gridpanel.setLoading(false);
							}, 100);

							e.preventDefault();
							e.stopPropagation();
							e.stopImmediatePropagation()
							return false;
						});
					}
				}
			}],
			listeners: {
				activate: function( panel, eOpts ){
//					console.log('activate');
					var searchfield = panel.down('searchfield#keyword-search-searchfield');
					if(searchfield) searchfield.focus(true);
				}
			}
		};

		var pallet_gridpanel_config = {
//				title: 'pallet',
//				itemId: 'south-panel',
			region: 'south',
			height: 200,
			minHeight: 200,
			split: true,
			hidden: true,	//20210205

			xtype: 'gridpanel',
			itemId: 'pallet-gridpanel',
			store: pallet_store,
			emptyText: 'Canvas',

			dockedItems: [{
				xtype: 'toolbar',
				dock: 'bottom',
				defaults: {
					disabled: true
				},
				items: [{
					hidden: true,
					xtype: 'tbtext',
					itemId: 'items-title-tbtext',
					text: 'Canvas',
					style:{'cursor':'default','user-select':'none','font-weight':'bold'}
				},{
					xtype: 'checkboxfield',
					itemId: 'items-match-list-checkboxfield',
					boxLabel: 'Palette',
					checked: self.DEF_MATCH_LIST_DRAW,
					disabled: false,
					listeners: {
						change: function(checkboxfield, newValue, oldValue, eOpts){
							self.DEF_MATCH_LIST_DRAW = newValue;
							var window_panel = checkboxfield.up('panel#window-panel');
							window_panel._update_render.cancel();
							window_panel._update_render.delay(0,null,null,[true]);
						}
					}
				},{
					xtype: 'checkboxfield',
					itemId: 'items-title-checkboxfield',
					boxLabel: 'Canvas',
					checked: self.DEF_PALLET_DRAW,
					disabled: false,
					listeners: {
						change: function(checkboxfield, newValue, oldValue, eOpts){
							self.DEF_PALLET_DRAW = newValue;
							var window_panel = checkboxfield.up('panel#window-panel');
							window_panel._update_render.cancel();
							window_panel._update_render.delay(0,null,null,[true]);
						}
					}
				},'-',{
					itemId: 'select-all',
					tooltip: 'Select',
					iconCls: 'pallet_select',
					disabled: false,
					listeners: {
						click: function(button){
							var gridpanel = button.up('gridpanel');
							var gridview = gridpanel.getView();
							var selmodel = gridpanel.getSelectionModel();
							var store = gridpanel.getStore();
							gridpanel.suspendEvent('beforeselect');
							try{
								gridview.saveScrollState();
								selmodel.selectAll();
								store.each(function(record){ $(gridview.getNode(record)).addClass(class_row_selected); });
								gridview.restoreScrollState();
							}catch(e){
								console.error(e)
							}
							gridpanel.resumeEvent('beforeselect');

							var $gridviewdom = $(gridview.el.dom);
							var disabled = $gridviewdom.find('tr.'+class_row_selected).length ? false : true;
							var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
							if(toolbar){
								Ext.Array.each(toolbar.items.items, function(item){
									if(
										!item.isXType('button') ||
										item.getItemId()=='select-all' ||
										item.getItemId()=='deselect-all' ||
										item.getItemId()=='items-selected-tagged' ||
										item.getItemId()=='items-selected-picked' ||
										item.getItemId()=='items-selected-all' ||
										item.getItemId()=='items-title-checkboxfield'
									) return true;
									item.setDisabled(disabled);
								});
							}
						}
					}
				},{
					itemId: 'deselect-all',
					tooltip: 'Unselect',
					iconCls: 'pallet_unselect',
					disabled: false,
					listeners: {
						click: function(button,e){
							var gridpanel = button.up('gridpanel');
							var gridview = gridpanel.getView();
							var selmodel = gridpanel.getSelectionModel();
							var store = gridpanel.getStore();
							gridpanel.suspendEvent('beforedeselect');
							try{
								var records = [];
								store.each(function(record){
									if(record.get(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID)) records.push(record);
								});
								if(Ext.isArray(records) && records.length) cell_pick(records,gridpanel,e);

								gridview.saveScrollState();
								selmodel.deselectAll();
								store.each(function(record){ $(gridview.getNode(record)).removeClass(class_row_selected); });
								gridview.restoreScrollState();
							}catch(e){
								console.error(e)
							}
							gridpanel.resumeEvent('beforedeselect');

							var $gridviewdom = $(gridview.el.dom);
							$gridviewdom.find('.'+class_word_button_selected).removeClass(class_word_button_selected);

							var disabled = $gridviewdom.find('tr.'+class_row_selected).length ? false : true;
							var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
							if(toolbar){
								Ext.Array.each(toolbar.items.items, function(item){
									if(
									!item.isXType('button') ||
									item.getItemId()=='select-all' ||
									item.getItemId()=='deselect-all' ||
									item.getItemId()=='items-selected-tagged' ||
									item.getItemId()=='items-selected-picked' ||
									item.getItemId()=='items-selected-all' ||
									item.getItemId()=='items-title-checkboxfield'
								) return true;
									item.setDisabled(disabled);
								});
							}
						}
					}
				},'-',{
					xtype: 'tbtext',
					itemId: 'items-selected-tbtext',
					text: '0 items selected.',
					style:{'cursor':'default','user-select':'none'}
				},'-','->','-',{
					xtype: 'tbtext',
					text: '<label>selected</label>'
				},{
					text: 'to TRUSH',
					handler: function(button,e) {
						var gridpanel = button.up('gridpanel#pallet-gridpanel');
						var gridview = gridpanel.getView();
						var store = gridpanel.getStore();
						var selmodel = gridpanel.getSelectionModel();
						var remove_records = selmodel.getSelection();
						if(remove_records.length){
							try{
								store.remove(remove_records);
							}catch(e){
								console.error(e);
							}
						}
						self.refreshView(gridview);

						var $gridviewdom = $(gridview.el.dom);
						var disabled = $gridviewdom.find('tr.'+class_row_selected).length ? false : true;
						var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							Ext.Array.each(toolbar.items.items, function(item){
								if(
									!item.isXType('button') ||
									item.getItemId()=='select-all' ||
									item.getItemId()=='deselect-all' ||
									item.getItemId()=='items-selected-tagged' ||
									item.getItemId()=='items-selected-picked' ||
									item.getItemId()=='items-selected-all' ||
									item.getItemId()=='items-title-checkboxfield'
								) return true;
								item.setDisabled(disabled);
							});
						}
					}
				},{
					text: 'COLOR',
					xtype: 'agcolorbutton',
					listeners: {
						colorchange: function(button,color){
						var gridpanel = button.up('gridpanel#pallet-gridpanel');
							var store = gridpanel.getStore();
							var selmodel = gridpanel.getSelectionModel();
							store.suspendEvents(true);
							try{
								Ext.Array.each(selmodel.getSelection(), function(record){
									record.beginEdit();
									var modifiedFieldNames = record.set(Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,'#'+color);
									record.commit(false,modifiedFieldNames);
								});
							}catch(e){
								console.error(e);
							}
							store.resumeEvents();
						}
					}
				},{
					text: 'OPACITY',
					xtype: 'agopacitybutton',
					listeners: {
						opacitychange: function(button,opacity){
							var gridpanel = button.up('gridpanel#pallet-gridpanel');
							var store = gridpanel.getStore();
							var selmodel = gridpanel.getSelectionModel();
							store.suspendEvents(true);
							try{
								Ext.Array.each(selmodel.getSelection(), function(record){
									record.beginEdit();
									var modifiedFieldNames = record.set(Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,opacity);
									record.commit(false,modifiedFieldNames);
								});
							}catch(e){
								console.error(e);
							}
							store.resumeEvents();
						}
					}
				},{
					hidden: true,
					text: 'MAPURL',
					listeners: {
						click: function(button,e) {
							var gridpanel = button.up('gridpanel#pallet-gridpanel');
							var store = gridpanel.getStore();
							var selmodel = gridpanel.getSelectionModel();
							var Part = Ext.Array.map(selmodel.getSelection(), function(record){
								var data = record.getData();
								var PartColor = data[ Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID ];
								return {
									'PartID': data[ Ag.Def.ID_DATA_FIELD_ID ],
									'PartColor': PartColor.substring(PartColor.indexOf('#')+1),
									'PartOpacity': data[ Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID ],
								};
							});
							console.log(Ext.JSON.encode({'Part':Part}));


//										if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){

							console.log(window.location.protocol+window.location.host+window.location.pathname+'#'+window.encodeURIComponent(Ext.JSON.encode({'Part':Part})));
						}
					}
				},{
					text: 'DOWNLOAD',
					listeners: {
						click: function(button,e) {
							var gridpanel = button.up('gridpanel#pallet-gridpanel');
							var store = gridpanel.getStore();
							var selmodel = gridpanel.getSelectionModel();
							var selected_records = selmodel.getSelection();
							self._download(selected_records);
						}
					}
				}]
			}],
			plugins: [
				Ext.create('Ext.grid.plugin.CellEditing', {
					clicksToEdit: 1,
					listeners: {
						beforeedit: function(editor,e,eOpts){
//									console.log('beforeedit',e);
							e.cancel = e.grid.getSelectionModel().isSelected(e.record) ? false : true;
							if(e.cancel){
								var $gridviewdom = $(e.view.el.dom);
								var select_records = [];
								var value = (e.column.dataIndex==='opacity' && Ext.isNumber(e.value) ? Ext.util.Format.number(e.value,e.column.format || '0.00') : e.value);
								$gridviewdom.find('div[data-value="'+value+'"]').closest('tr.x-grid-data-row').addClass(class_row_selected).map(function(){ select_records.push(e.view.getRecord(this)) });
								e.grid.suspendEvent('beforeselect');
								try{
									e.view.saveScrollState();
									e.grid.getSelectionModel().select(select_records,true);
									e.view.restoreScrollState();
								}catch(e){
									console.error(e)
								}
								e.grid.resumeEvent('beforeselect');

								var disabled = $gridviewdom.find('tr.'+class_row_selected).length ? false : true;
								var toolbar = e.grid.getDockedItems('toolbar[dock="bottom"]')[0];
								if(toolbar){
									Ext.Array.each(toolbar.items.items, function(item){
										if(
									!item.isXType('button') ||
									item.getItemId()=='select-all' ||
									item.getItemId()=='deselect-all' ||
									item.getItemId()=='items-selected-tagged' ||
									item.getItemId()=='items-selected-picked' ||
									item.getItemId()=='items-selected-all' ||
									item.getItemId()=='items-title-checkboxfield'
								) return true;
										item.setDisabled(disabled);
									});
								}
							}
						},
						edit: function(editor,e,eOpts){
							console.log(e);
						}
					}
				}),
			],

			selModel: {
				mode : 'SIMPLE'
			},
			columnLines: true,
			columns: [
				{
					text: 'obj',
					tooltip: 'obj',
					dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
					width: 82,
					hideable: true,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						var rtn;
						var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
						if(Ext.isString(artc_id) && artc_id.length){
							rtn = artc_id;
						}
						else{
							rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
						}
						metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
						return rtn;
					}
				},
				{
					text: 'FMAID',
					tooltip: 'FMAID',
					dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
					hideable: false,
					width: 63,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
						var rtn = value;
//						if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//						if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//						if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;

						if(Ext.isString(rtn) && rtn.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
						}
						return rtn;

					}
				},
				{
					text: 'SUB',
					tooltip: 'SUB',
					dataIndex: 'sub'+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: true,
					hidden: false,
					align: 'center',
					width: 42,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
						if(Ext.isString(value) && value.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-sub');
						}
						return value;
					}
				},
				{
					text: 'R/L',
					tooltip: 'R/L',
					dataIndex: 'laterality'+renderer_dataIndex_suffix,
					lockable: false,
					draggable: false,
					hideable: true,
					hidden: false,
					align: 'center',
					width: 42,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
						if(Ext.isString(value) && value.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//								return make_ag_word(value,dataIndex,null,'bp3d-laterality');
							return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				},
				{
					text: Ag.Def.NAME_DATA_FIELD_ID,
					tooltip: Ag.Def.NAME_DATA_FIELD_ID,
					dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
					hideable: false,
					flex: 1,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
						if(Ext.isString(value) && value.length){
//								return make_ag_word(value);
//								console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,null,null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				},
				{
					text: Ag.Def.SYNONYM_DATA_FIELD_ID,
					tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
					dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
					flex: 1,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
						var dataIndex = view.getGridColumns()[colIndex].dataIndex;
						if(Ext.isString(value) && value.length){
							return make_ag_word(value,dataIndex);
						}
						else if(Ext.isArray(value) && value.length){
							var rtn = [];
							Ext.Array.each(value, function(v,i){
								if(Ext.isString(value[i]) && value[i].length){
									rtn.push(make_ag_word(value[i],dataIndex));
								}
							});
							return rtn.join('');
						}
						return value;
					}
				}
				,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',false)
				,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',false)
				,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',false)
				,
				{
					text: 'Segment',
					tooltip: 'Segment',
					dataIndex: Ag.Def.SEGMENT_DATA_FIELD_ID+renderer_dataIndex_suffix,
					align: 'center',
					width: 50,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
						var dataIndex = view.getGridColumns()[colIndex].dataIndex;
						if(Ext.isString(value) && value.length){
							return make_ag_word(value,dataIndex,null,'bp3d-segment');
						}
						else if(Ext.isArray(value) && value.length){
							var rtn = [];
							Ext.Array.each(value, function(v,i){
								if(Ext.isString(value[i]) && value[i].length){
									rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID)));
								}
								else if(Ext.isNumber(value[i])){
									rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID)));
								}
							});
							return rtn.join('');
						}
						return value;
					}
				}
				,{
					hidden: true,
					hideable: false,
					text: 'Category',
					tooltip: 'Category',
					dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
					width: 70,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
						if(Ext.isString(value) && value.length){
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-category');
						}
						return value;
					}
				}
				,{
//							text: 'System',
//							tooltip: 'System',
					text: 'Category',
					tooltip: 'Category',
					dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
					align: 'center',
					width: 70,
					renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
						if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
						metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
						value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
						if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
						if(Ext.isString(value) && value.length){
//							if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//							if(value.match(/^_+(.+)$/)) value = RegExp.$1;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							return make_ag_word(value,dataIndex,null,'bp3d-category',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID));
						}
						return value;
					}
				}
				,{
					text: self.DEF_COLOR_LABEL,
					tooltip: self.DEF_COLOR_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
					width: self.DEF_COLOR_COLUMN_WIDTH + 22,
					minWidth: self.DEF_COLOR_COLUMN_WIDTH + 22,
					hidden: false,
					hideable: true,
					xtype: 'agcolorcolumn'
				}
				,{
					text: self.DEF_OPACITY_LABEL,
					tooltip: self.DEF_OPACITY_LABEL,
					dataIndex: Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,
					width: self.DEF_OPACITY_COLUMN_WIDTH,
					hideable: false,
					hidden: false,
					hideable: true,
					xtype: 'agopacitycolumn'
				},
			],
			listeners: {
				afterrender: function(gridpanel){
					var gridview = gridpanel.getView();
					var selmodel = gridpanel.getSelectionModel();
					var store = gridpanel.getStore();
					store.removeAll();	//emptyTextが表示されない為、あえてクリアする
					var $gridviewdom = $(gridview.el.dom);

					var row_selected = function(e,className){

						if(Ext.isEmpty(className)) className = 'bp3d-word';

						var all_select_text = {};
						var all_select_text_num = 0;
						$gridviewdom.find('.'+class_word_button_selected+'.'+className).each(function(){
							var value = $(this).attr('data-value');
							if(Ext.isEmpty(all_select_text[value])) all_select_text[value] = 0;
							all_select_text[value]++;
						});
						all_select_text_num = Ext.Object.getKeys(all_select_text).length;


						$gridviewdom.find('tr.x-grid-data-row').each(function(){
							var $tr = $(this);

							var select_text = {};
							var select_text_num = 0;
							$tr.find('.'+class_word_button_selected+'.'+className).each(function(){
								var value = $(this).attr('data-value');
								if(Ext.isEmpty(select_text[value])) select_text[value] = 0;
								select_text[value]++;
							});
							select_text_num = Ext.Object.getKeys(select_text).length;

							$tr.toggleClass(class_row_selected, all_select_text_num>0 && all_select_text_num===select_text_num);
						});

					};
					var button_disabled = function(e){

						gridview.saveScrollState();
						var selected_records = $.makeArray( $gridviewdom.find('tr.'+class_row_selected).map(function(){ return gridview.getRecord(this); }) );
						if(selected_records.length){
							gridpanel.suspendEvent('beforedeselect');
							gridpanel.suspendEvent('beforeselect');
							try{
								selmodel.select(selected_records);
							}catch(e){
								console.error(e)
							}
							gridpanel.resumeEvent('beforedeselect');
							gridpanel.resumeEvent('beforeselect');
						}
						else{
							gridpanel.suspendEvent('beforedeselect');
							try{
								selmodel.deselectAll();
							}catch(e){
								console.error(e)
							}
							gridpanel.resumeEvent('beforedeselect');
						}
						gridview.restoreScrollState();


						var disabled = $gridviewdom.find('tr.'+class_row_selected).length ? false : true;
						var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							Ext.Array.each(toolbar.items.items, function(item){
								if(
									!item.isXType('button') ||
									item.getItemId()=='select-all' ||
									item.getItemId()=='deselect-all' ||
									item.getItemId()=='items-selected-tagged' ||
									item.getItemId()=='items-selected-picked' ||
									item.getItemId()=='items-selected-all' ||
									item.getItemId()=='items-title-checkboxfield'
								) return true;
								item.setDisabled(disabled);
							});
						}
					};

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-fmaid', function(e){
						var $tr = $(this).closest('tr.x-grid-data-row');
//							var selected = $(this).hasClass(class_word_button_selected) ? false : true;
//							if(!selected){
//								$tr.find('.'+class_word_button_selected).toggleClass(class_word_button_selected, selected);
//							}
//							$(this).toggleClass(class_word_button_selected, selected);
//							$tr.toggleClass(class_row_selected, selected);

//							button_disabled(e);


						var record = gridview.getRecord($tr.get(0));
						if(record){
							cell_pick([record],gridpanel,e);
						}

						update_selected_rows();

						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-word', function(e){
						var value = $(this).attr('data-value');
						var dataIndex = $(this).attr('data-dataIndex');
						var selected = $(this).hasClass(class_word_button_selected) ? false : true;
						$gridviewdom.find('a.bp3d-word-button.bp3d-word[data-value="'+value+'"]').toggleClass(class_word_button_selected, selected);

						self._clickWordTag(value,dataIndex);

//							row_selected(e,'bp3d-word');
						button_disabled(e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-sub', function(e){
						var value = $(this).attr('data-value');
						var selected = $(this).hasClass(class_word_button_selected) ? false : true;
						$gridviewdom.find('a.bp3d-word-button.bp3d-sub[data-value="'+value+'"]').toggleClass(class_word_button_selected, selected);

						row_selected(e,'bp3d-sub');
						button_disabled(e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-laterality', function(e){
						var value = $(this).attr('data-value');
						var selected = $(this).hasClass(class_word_button_selected) ? false : true;
						$gridviewdom.find('a.bp3d-word-button.bp3d-laterality[data-value="'+value+'"]').toggleClass(class_word_button_selected, selected);

						row_selected(e,'bp3d-laterality');
						button_disabled(e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-segment', function(e){
						var value = $(this).attr('data-value');
//							var selected = $(this).hasClass(class_word_button_selected) ? false : true;
//							$gridviewdom.find('a.bp3d-word-button.bp3d-segment[data-value="'+value+'"]').toggleClass(class_word_button_selected, selected);

//							row_selected(e,'bp3d-segment');
						self._clickSegmentTag(value,e);
						button_disabled(e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-category', function(e){
						var value = $(this).attr('data-value');
//							var selected = $(this).hasClass(class_word_button_selected) ? false : true;
//							$gridviewdom.find('a.bp3d-word-button.bp3d-category[data-value="'+value+'"]').toggleClass(class_word_button_selected, selected);

//							row_selected(e,'bp3d-category');
						self._clickCategoryTag(value,e);
						button_disabled(e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});

					$gridviewdom.on('click','a.bp3d-word-button.bp3d-system', function(e){
						var value = $(this).attr('data-value');
						var selected = $(this).hasClass(class_word_button_selected) ? false : true;
						$gridviewdom.find('a.bp3d-word-button.bp3d-system[data-value="'+value+'"]').toggleClass(class_word_button_selected, selected);

						row_selected(e,'bp3d-system');
						button_disabled(e);
						e.preventDefault();
						e.stopPropagation();
						return false;
					});



					var gridview_scroll = function(){
//								console.log('scroll',gridview);
					};
					gridview.on({
						scroll: {
							fn: gridview_scroll,
							element: 'el',
							scope: gridview
						},
						boxready: gridview_scroll,
						resize: gridview_scroll,
						refresh: gridview_scroll,
						scope: gridview,
						destroyable: true
					});


					var update_selected_rows = function(){
						var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							var tbtext = toolbar.down('tbtext#items-selected-tbtext');
							tbtext.setText(Ext.util.Format.format('{0} / {1} items selected.',Ext.util.Format.number(selmodel.getCount(),'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));
						}

						var disabled = selmodel.getSelection().length ? false : true;
						var toolbar = gridpanel.getDockedItems('toolbar[dock="bottom"]')[0];
						if(toolbar){
							Ext.Array.each(toolbar.items.items, function(item){
								if(
									!item.isXType('button') ||
									item.getItemId()=='select-all' ||
									item.getItemId()=='deselect-all' ||
									item.getItemId()=='items-selected-tagged' ||
									item.getItemId()=='items-selected-picked' ||
									item.getItemId()=='items-selected-all' ||
									item.getItemId()=='items-title-checkboxfield'
								) return true;
								item.setDisabled(disabled);
							});
						}

					};
					var func_false = function(){
						return false;
					};
					gridpanel.on({
//							beforeitemmousedown: func_false,
//							beforeitemmouseenter: func_false,
//							beforeitemmouseleave: func_false,
//							beforeitemmouseup: func_false,
//							beforedeselect: func_false,
//							beforeselect: func_false,
						deselect: update_selected_rows,
						select: update_selected_rows,
						selectionchange: update_selected_rows,
						scope: gridpanel,
						buffer: 250
					});
					store.on({
						add: update_selected_rows,
						bulkremove: update_selected_rows,
					});



				},
				beforedeselect: function(selmodel, record, index, eOpts){
					return false;
				},
				beforeselect: function(selmodel, record, index, eOpts){
//						var node = this.getView().getNode(record);
//						Ext.defer(function(){
//							var focusedItemCls = Ext.baseCSSPrefix + 'grid-row-focused';
//							$(node).removeClass(focusedItemCls);
//						},250);

					return false;
				}
			}
		};

		var segment_panel_config = {
			title: 'Segments',
			itemId: 'segment-panel',
			layout: {
				type: 'hbox',
				align: 'stretch'
			},
			items: [{
				itemId: 'segment-treepanel',
				xtype: 'treepanel',
				store: segment_store,
				width: 250,
				rootVisible: false,


				dockedItems: [{
					hidden: true,
					xtype: 'toolbar',
					dock: 'bottom',
					ui: 'footer',
					itemId: 'bottom',
					items: [{
						xtype: 'button',
						text: 'Download List',
						minWidth: 68,
						disabled: true,
						listeners: {
							afterrender: function(button, eOpts){
								let panel = button.up('panel#segment-panel');
								let treepanel = panel.down('treepanel#segment-treepanel');
								let selmodel = treepanel.getSelectionModel();
								selmodel.on({
									selectionchange: function(selmodel, selected, eOpts){
										button.setDisabled(selmodel.getCount() > 0 ? false : true);
									}
								});
							},
							click: function(button){
/*
								let segment_store = Ext.data.StoreManager.lookup('segment-list-store');
								let rootnode = segment_store.getRootNode();
								if(rootnode){

									const filename = 'segment.tsv';
									const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
									let category_data = ['#segment','','count','ids'].join("\t")+"\n";

									rootnode.cascadeBy(function(){
										var node = this;
										console.log('cascadeBy',node.isLeaf(),node.getData());
										var data = node.getData();
										if(data.id=='root') return true;
										if(!node.isLeaf()) return true;


										var parentId = node.get('parentId');
										var segment = node.get('segment');

//text/tab-separated-values
										var data_count = node.get('data_count');
										var datas = node.get('datas');
										let ids = Ext.Array.map(datas, function(data){
											return data['id'];
										}).join(',');
										if(parentId=='whole'){
											category_data += [segment,'',data_count,ids].join("\t")+"\n";
										}
										else{
											category_data += [parentId,segment,data_count,ids].join("\t")+"\n";
										}
									});

									const blob = new Blob([bom, category_data], { type: 'text/tab-separated-values' });

									const url = (window.URL || window.webkitURL).createObjectURL(blob);
									const download = document.createElement("a");
									download.href = url;
									download.download = filename;
									download.click();
									(window.URL || window.webkitURL).revokeObjectURL(url);

								}
*/
								const fileext = '.tsv';
								const basefilename = 'segment_';
								const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
								let filename = basefilename;
								let download_string;

								let line_feed_code = "\n";
								if(window.navigator.userAgent.toLowerCase().indexOf("windows nt")>=0) line_feed_code = "\r\n";

								const panel = button.up('panel#segment-panel');
								const treepanel = panel.down('treepanel#segment-treepanel');
								const selmodel = treepanel.getSelectionModel();
								const selnode = selmodel.getLastSelected();
								const parentId = selnode.get('parentId');
								const text = selnode.get('segment');
								if(parentId=='whole'){
									filename += text;
								}
								else{
									filename += parentId + '_' + text;
								}
								filename = filename.replace(/[^A-Za-z0-9]+/g,'_');
								filename += fileext;
//								console.log(filename);

								const gridpanel = panel.down('gridpanel#segment-gridpanel');
								const store = gridpanel.getStore();
								let download_columns = [];
								Ext.Array.each(gridpanel.columns, function(column){
									if(!column.isHideable() && column.isHidden()) return true;
//									console.log(column);
									download_columns.push(column);
								});
								download_string = '#' + Ext.Array.map(download_columns, function(column){return column.text;}).join("\t")+line_feed_code;
//								console.log(download_string);


								store.each(function(record){
									let values = [];
									Ext.Array.each(download_columns, function(column){
										let value = record.get(column.dataIndex);
										if(Ext.isArray(value)){
											if(column.dataIndex=='is_a' || column.dataIndex=='part_of' || column.dataIndex=='lexicalsuper'){
												value = Ext.Array.map(value, function(item){
													return item.id+':'+item.name;
												});
											}
											let hash = {};
											Ext.Array.map(value, function(v){ hash[v] = null; });
											value = Ext.Object.getKeys(hash).sort().join(';');
										}
										if(Ext.isEmpty(value)) value = '';
										values.push(value);
									});
									if(values.length) download_string += values.join("\t")+line_feed_code;
								});
//								console.log(download_string);

								const blob = new Blob([bom, download_string], { type: 'text/tab-separated-values' });
								const url = (window.URL || window.webkitURL).createObjectURL(blob);
								const download = document.createElement("a");
								download.href = url;
								download.download = filename;
								download.click();
								(window.URL || window.webkitURL).revokeObjectURL(url);
							}
						}
					}]
				}],
				listeners: {
					afterrender: function(panel, eOpts){
						var viewport = self.getViewport();
						var window_panel         = viewport.down('panel#window-panel');
/*
						var version_combobox         = window_panel.down('combobox#version-combobox');
						if(version_combobox){
							version_combobox.on({
								select: function( field, records, eOpts ){
									console.log('select', field, records);
								}
							})
						}
*/
						var segment_filtering_combobox = window_panel.down('combobox#segment-filtering-combobox');

						var fn = function(){
							if(segment_store.isLoading()) return;
							panel.setLoading(true);

							var version;
							var ids;
							var art_ids;
							if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
								version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
								Ag.data.isLoadingRenderer = Ag.data.isLoadingRenderer || {};
								if(Ag.data.isLoadingRenderer[version]) return;
							}
							else{
								Ext.defer(fn, 250);
								return;
							}
//							console.log('loadrenderer');
							var cities_store = Ext.data.StoreManager.lookup('cities-list-store');
							if(cities_store.isLoading()){
								cities_store.on({
									load: {
										fn: fn,
										single: true
									}
								});
								return;
							}
							var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
							if(system_list_store.isLoading()){
								system_list_store.on({
									load: {
										fn: fn,
										single: true
									}
								});
								return;
							}

							if(Ag.data.renderer && version){
								ids = Ag.data.renderer[version]['ids'];
								art_ids = Ag.data.renderer[version]['art_ids'];
							}
							if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
								if(Ext.isEmpty(ids)) console.warn('ids is empty!!');
								if(Ext.isEmpty(art_ids)) console.warn('art_ids is empty!!');
								panel.setLoading(false);
								return;
							}
							var SEG2ART = segment_filtering_combobox.getValue()==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

							var rootnode = segment_store.getRootNode();
//							console.log('fn',rootnode);
							if(rootnode){
								rootnode.cascadeBy(function(){
									var node = this;
//									console.log('cascadeBy',node.isLeaf(),node.get('segment'),node.get('cities_ids'));
//									if(node.isLeaf() || true){
									if(node.isLeaf()){
										var use_ids;
										var cities_ids = node.get('cities_ids')
										if(Ext.isString(cities_ids) && cities_ids.length){
											Ext.Array.each(cities_ids.split(','), function(cities_id){
												var cities_record = cities_store.getAt(cities_id);	// unfound対応(2019/12/27)
												if(Ext.isEmpty(cities_record)) return true;
												var cities_name = cities_record.get('name');
												if(Ext.isEmpty(cities_name)) return true;
												if(Ext.isObject(SEG2ART) && Ext.isObject(SEG2ART['CITIES']) && Ext.isObject(SEG2ART['CITIES'][cities_name])){
													Ext.Object.each(SEG2ART['CITIES'][cities_name], function(art_id){
														var id;
														var artc_id;
														if(Ext.isObject(art_ids[art_id])){
															if(Ext.isEmpty(use_ids)) use_ids = {};
															id = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
															artc_id = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
														}
														if(Ext.isEmpty(id) || Ext.isEmpty(ids[id])) return true;
														if(Ext.isEmpty(use_ids[id])){
															var tempobj = {};
															tempobj[Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
															tempobj[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = artc_id;
															use_ids[id] = Ext.Object.merge(tempobj, ids[id]);
//															console.log(ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID],ids[id][Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID]);
														}
														if(Ext.isEmpty(use_ids[id]['cities_ids'])){
															use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID] = [cities_id];
															if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'] = [Ag.data.citiesids2segment[cities_id]];
														}
														else{
															use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID].push(cities_id);
															if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'].push(Ag.data.citiesids2segment[cities_id]);
														}

													});
												}
											});
										}
//										console.log(use_ids);
										var add_datas = [];
										if(Ext.isObject(use_ids)){
											var use_system_ids;
											var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
											system_list_store.filter([{
												property: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
												value: true
											}]);
											if(system_list_store.getCount()>0){
												use_system_ids = {};
												system_list_store.each(function(record){
													use_system_ids[record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID)] = record.getData();
												});
											}
											system_list_store.clearFilter();

											Ext.Object.each(use_ids,function(id,data){

												var cdi_name = data[Ag.Def.ID_DATA_FIELD_ID];
												var system_id = data[Ag.Def.SYSTEM_ID_DATA_FIELD_ID];

												if(Ext.isObject(use_system_ids)){
													if(Ext.isEmpty(use_system_ids[system_id])) return true;
												}


												if(Ext.isObject(data['relation'])){
													Ext.Object.each(data['relation'], function(relation,value){
														if(Ext.isObject(value)){
															Ext.Object.each(value, function(id,name){
																var v = data[relation];
																if(Ext.isEmpty(v)){
																	v = [{id:id,name:name}];
																}
																else{
																	v.push({id:id,name:name});
																}
																data[relation] = v;

																if(relation == 'is_a' || relation == 'lexicalsuper') return true;
																v = data['part_of'];
																if(Ext.isEmpty(v)){
																	v = [{id:id,name:name}];
																}
																else{
																	v.push({id:id,name:name});
																}
																data['part_of'] = v;
															});
														}
													});
												}
												add_datas.push(data);
											});

										}

										var len = 0
										if(Ext.isObject(use_ids)) len = Ext.Object.getKeys(use_ids).length;
										node.beginEdit();
										node.set('text',Ext.util.Format.format('{0}({1})',node.get('segment'),Ext.util.Format.number(len,'0,000')));
										node.set('data_count', len);
										node.set('datas', add_datas);
										node.commit(false,['text','data_count','datas']);
										node.endEdit(false,['text','data_count','datas']);

//										console.log(node.get('text'),add_datas.length);
									}
								});
							}
							panel.setLoading(false);
						};

						self.on('loadrenderer',fn,self);

//						console.log('loading', segment_store.isLoading());
						if(segment_store.isLoading()){
							segment_store.on({
								load: {
									fn: function( store, node, records, successful, eOpts ){
//										console.log('load', store, node, records, successful, eOpts);
										fn();
									},
									single: true
								}
							});
						}
						else{
							Ext.defer(fn, 0);
						}
					},
					beforeselect: function( selmodel, record, index, eOpts ){
						return record.isLeaf();
					},
					beforeitemclick: function( view, record, item, index, e, eOpts ){
//						console.log('beforeitemclick',view, record, item, index, e);
						return record.isLeaf();
					},
					beforeitemcollapse: function( node, eOpts ){
//						console.log('beforeitemcollapse',node);
					},
					select: function( selmodel, record, index, eOpts ){
						var segment_grid_store = Ext.data.StoreManager.lookup('segment-grid-store');
						segment_grid_store.removeAll();//add_datas.length?true:false);
						var add_records = segment_grid_store.add(record.get('datas'));
					}
				}
			},{
				flex: 1,
				xtype: 'gridpanel',
				itemId: 'segment-gridpanel',
				store: Ext.data.StoreManager.lookup('segment-grid-store'),
				viewConfig: self.getViewConfig(),
				selModel: {
	//						mode : 'SIMPLE'
					mode : 'MULTI'
				},
				columnLines: true,
				dockedItems: [{
	//				hidden: true,
					xtype: 'toolbar',
					dock: 'bottom',
					ui: 'footer',
					itemId: 'bottom',
					items: [
					{
						xtype: 'button',
						text: 'Download List',
						minWidth: 68,
						disabled: true,
						listeners: {
							afterrender: function(button, eOpts){
								let panel = button.up('panel#segment-panel');
								let treepanel = panel.down('treepanel#segment-treepanel');
								let selmodel = treepanel.getSelectionModel();
								selmodel.on({
									selectionchange: function(selmodel, selected, eOpts){
										button.setDisabled(selmodel.getCount() > 0 ? false : true);
									}
								});
							},
							click: function(button){
/*
								let segment_store = Ext.data.StoreManager.lookup('segment-list-store');
								let rootnode = segment_store.getRootNode();
								if(rootnode){

									const filename = 'segment.tsv';
									const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
									let category_data = ['#segment','','count','ids'].join("\t")+"\n";

									rootnode.cascadeBy(function(){
										var node = this;
										console.log('cascadeBy',node.isLeaf(),node.getData());
										var data = node.getData();
										if(data.id=='root') return true;
										if(!node.isLeaf()) return true;


										var parentId = node.get('parentId');
										var segment = node.get('segment');

//text/tab-separated-values
										var data_count = node.get('data_count');
										var datas = node.get('datas');
										let ids = Ext.Array.map(datas, function(data){
											return data['id'];
										}).join(',');
										if(parentId=='whole'){
											category_data += [segment,'',data_count,ids].join("\t")+"\n";
										}
										else{
											category_data += [parentId,segment,data_count,ids].join("\t")+"\n";
										}
									});

									const blob = new Blob([bom, category_data], { type: 'text/tab-separated-values' });

									const url = (window.URL || window.webkitURL).createObjectURL(blob);
									const download = document.createElement("a");
									download.href = url;
									download.download = filename;
									download.click();
									(window.URL || window.webkitURL).revokeObjectURL(url);

								}
*/
								const fileext = '.tsv';
								const basefilename = 'segment_';
								const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
								let filename = basefilename;
								let download_string;

								let line_feed_code = "\n";
								if(window.navigator.userAgent.toLowerCase().indexOf("windows nt")>=0) line_feed_code = "\r\n";

								const panel = button.up('panel#segment-panel');
								const treepanel = panel.down('treepanel#segment-treepanel');
								const selmodel = treepanel.getSelectionModel();
								const selnode = selmodel.getLastSelected();
								const parentId = selnode.get('parentId');
								const text = selnode.get('segment');
								if(parentId=='whole'){
									filename += text;
								}
								else{
									filename += parentId + '_' + text;
								}
								filename = filename.replace(/[^A-Za-z0-9]+/g,'_');
								filename += fileext;
//								console.log(filename);

								const gridpanel = panel.down('gridpanel#segment-gridpanel');
								const store = gridpanel.getStore();
								let download_columns = [];
								Ext.Array.each(gridpanel.columns, function(column){
									if(!column.isHideable() && column.isHidden()) return true;
//									console.log(column);
									download_columns.push(column);
								});
								download_string = '#' + Ext.Array.map(download_columns, function(column){return column.text;}).join("\t")+line_feed_code;
//								console.log(download_string);


								store.each(function(record){
									let values = [];
									Ext.Array.each(download_columns, function(column){
										let value = record.get(column.dataIndex);
										if(Ext.isArray(value)){
											if(column.dataIndex=='is_a' || column.dataIndex=='part_of' || column.dataIndex=='lexicalsuper'){
												value = Ext.Array.map(value, function(item){
													return item.id+':'+item.name;
												});
											}
											let hash = {};
											Ext.Array.map(value, function(v){ hash[v] = null; });
											value = Ext.Object.getKeys(hash).sort().join(';');
										}
										if(Ext.isEmpty(value)) value = '';
										values.push(value);
									});
									if(values.length) download_string += values.join("\t")+line_feed_code;
								});
//								console.log(download_string);

								const blob = new Blob([bom, download_string], { type: 'text/tab-separated-values' });
								const url = (window.URL || window.webkitURL).createObjectURL(blob);
								const download = document.createElement("a");
								download.href = url;
								download.download = filename;
								download.click();
								(window.URL || window.webkitURL).revokeObjectURL(url);
							}
						}
					},
					'->'
					,{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'bold'},
						text: 'Load / Render'
					}
					,{
						xtype: 'button',
						text: 'Selected',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#segment-panel').down('gridpanel#segment-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									add: function(store, records, index, eOpts){
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										if(store.getCount()==0) button.setDisabled(true);
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										button.setDisabled(selected.length==0 ? true : false);
									}
								});
								button.setDisabled(true);
							},
							click: function(button){
								var gridpanel = button.up('panel#segment-panel').down('gridpanel#segment-gridpanel');
								var segment_grid_store = gridpanel.getStore();
								var selmodel           = gridpanel.getSelectionModel();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												gridpanel.getSelectionModel().getSelection(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										segment_grid_store.removeAll();

										let treepanel = button.up('panel#segment-panel').down('treepanel#segment-treepanel');
										if(treepanel) treepanel.getSelectionModel().deselectAll();
									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,{
						xtype: 'button',
						text: 'All',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#segment-panel').down('gridpanel#segment-gridpanel');
								var store     = gridpanel.getStore();
								store.on({
									add: function(store, records, index, eOpts){
										button.setDisabled(store.getCount()==0 ? true : false);
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										button.setDisabled(store.getCount()==0 ? true : false);
									}
								});
								button.setDisabled(store.getCount()==0 ? true : false);
							},
							click: function(button){
								var gridpanel = button.up('panel#segment-panel').down('gridpanel#segment-gridpanel');
								var segment_grid_store = gridpanel.getStore();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												segment_grid_store.getRange(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										segment_grid_store.removeAll();

										let treepanel = button.up('panel#segment-panel').down('treepanel#segment-treepanel');
										if(treepanel) treepanel.getSelectionModel().deselectAll();
									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,'-',{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'normal'},
						text: '0 / 0',
						listeners: {
							afterrender: function(tbtext){
	//							console.log('afterrender',tbtext);
								var gridpanel = tbtext.up('panel#segment-panel').down('gridpanel#segment-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									add: function(store, records, index, eOpts){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										tbtext.setText(Ext.util.Format.format('{0} / {1}',Ext.util.Format.number(selected.length,'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
							}
						}
					}
					]
				}],
				columns: [

					{
						text: 'palette',
						tooltip: 'exists palette',
//						xtype: 'agcheckcolumn',
						dataIndex: Ag.Def.EXISTS_PALETTE_FIELD_ID,
						align: 'center',
						width: 34,
						locked: false,
						lockable: false,
						draggable: false,
						sortable: true,
						hideable: false,
						hidden: true,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							return Ext.util.Format.format(
											'<span class="glyphicon {0} keyword-search-gridpanel-column-{2}" aria-hidden="true" data-fmaid="{1}" data-qtip="exists palette" style="cursor:pointer;"></span>',
											value===true ? 'glyphicon-check' :'glyphicon-unchecked',
											record.get(Ag.Def.ID_DATA_FIELD_ID),
											Ag.Def.EXISTS_PALETTE_FIELD_ID
										);
						}
					},
/*
					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
//								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-obj';
//								console.log(value, rowIndex, colIndex);
							var rtn;
							var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
							if(Ext.isString(artc_id) && artc_id.length){
								rtn = artc_id;
							}
							else{
								rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
							}
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
*/
					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							console.log(value);
							var rtn = value;
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
					{
						text: 'FMAID',
						tooltip: 'FMAID',
//						dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: Ag.Def.ID_DATA_FIELD_ID+'_renderer',
						lockable: false,
						draggable: false,
						hideable: false,
						width: 63,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
//							var rtn = value;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;
////							return rtn;
//							var rtn = record.get(Ag.Def.ID_DATA_FIELD_ID+'_renderer');
							var rtn = value;

							if(Ext.isString(rtn) && rtn.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
							}
							return rtn;

						}
					},
					{
						text: 'SUB',
						tooltip: 'SUB',
						dataIndex: 'sub'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-sub');
							}
							return value;
						}
					},
					{
						text: 'R/L',
						tooltip: 'R/L',
						dataIndex: 'laterality'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//									return make_ag_word(value,dataIndex,null,'bp3d-laterality');
								return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.NAME_DATA_FIELD_ID,
						tooltip: Ag.Def.NAME_DATA_FIELD_ID,
						dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: false,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
//							console.log(store);
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							if(Ext.isString(value) && value.length){
//									return make_ag_word(value,null,'bp3d-name');
//										console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-name',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.SYNONYM_DATA_FIELD_ID,
						tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
						dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: true,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex);
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',false)
					,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',false)
					,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',false)
					,
					{
						text: 'Segment',
						tooltip: 'Segment',
//							dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: 'segment',
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: false,
						hidden: true,
						width: 50,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex,null,'bp3d-segment');
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment'));
									}
									else if(Ext.isNumber(value[i])){
										rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment'));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,{
						hidden: true,
						hideable: false,
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-category');
							}
							return value;
						}
					}
					,{
//							text: 'System',
//							tooltip: 'System',
						text: 'Category',
						tooltip: 'Category',
//						dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer',
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
//							value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
							if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
							if(Ext.isString(value) && value.length){
//								if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//								if(value.match(/^_+(.+)$/)) value = RegExp.$1;
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
//								return value;
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-system');
							}
							return value;
						}
					}
				],
				plugins: [
					Ext.create('Ext.grid.plugin.CellEditing', {
						clicksToEdit: 1,
						listeners: {
							beforeedit: function(editor,e,eOpts){
							},
							edit: function(editor,e,eOpts){
								console.log(e);
							}
						}
					}),
					self.getBufferedRenderer({pluginId: 'segment-gridpanel-plugin'})
				],
				listeners: {
					afterrender: function( gridpanel, eOpts ){
						gridpanel.getView().on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							}
						});

						var store = gridpanel.getStore();
						store.removeAll();	//emptyTextが表示されない為、あえてクリアする
						var selmodel     = gridpanel.getSelectionModel();
						var gridview     = gridpanel.getView();
						var $gridviewdom = $(gridview.el.dom);

						$gridviewdom.on('mousedown','a.bp3d-word-button', function(e){
							var $this = $(this);
							gridpanel.setLoading('searching...');
							Ext.defer(function(){

								var value = $this.attr('data-value');
								var dataIndex = $this.attr('data-dataIndex');
								if(dataIndex==Ag.Def.ID_DATA_FIELD_ID) dataIndex = Ag.Def.ID_DATA_FIELD_ID+'_renderer';
								if(dataIndex==Ag.Def.SYSTEM_ID_DATA_FIELD_ID) dataIndex = Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer';
//								console.log(dataIndex,value);
								var $tr = $this.closest('tr.x-grid-data-row');
								var $tbody = $tr.closest('tbody');
								var record = gridview.getRecord($tr.get(0));
								if(record){
//									gridview.saveScrollState();
//									gridpanel.suspendEvents(false);
									try{
	//									var value = record.get(dataIndex);
										var isSelected = selmodel.isSelected(record);
//										console.log(dataIndex,value,isSelected);
										var records = [];
										var startIndex = -1;
										var record;
										do {
											startIndex = store.findBy( function(record,id){
												var f_value = record.get(dataIndex);
												if(Ext.isString(value) && Ext.isString(f_value)){
													return value===f_value;
												}
												else if(Ext.isString(value) && Ext.isArray(f_value)){
													var rtn = false;
													Ext.Array.each( f_value, function(item,index,array){
														if(Ext.isString(item)){
															rtn = item===value;
														}
														else{
															rtn = item.name===value;
														}
														if(rtn) return false;
													});
													return rtn;
												}
											}, self, ++startIndex);
											record = null;
											if(startIndex>=0) record = store.getAt(startIndex);
	//										console.log(startIndex,record,isSelected);
											if(record) records.push(record);
										} while(startIndex>=0)
	//									console.log(records);
										if(isSelected){
											selmodel.select(records,true);
										}
										else{
											selmodel.deselect(records);
										}
									}catch(e){
										console.error(e);
									}
//									gridview.refresh();
//									gridview.restoreScrollState();
								}
								gridpanel.setLoading(false);
							}, 100);

							e.preventDefault();
							e.stopPropagation();
							e.stopImmediatePropagation()
							return false;
						});

					}
				}

			}]
		};

		var system_panel_config = {
			title: 'Category / Group',
			itemId: 'system-panel',
			layout: {
				type: 'hbox',
				align: 'stretch'
			},
			items: [{
				itemId: 'system-treepanel',
				xtype: 'treepanel',
				store: 'system-tree-store',
				width: 250,
				rootVisible: false,


				dockedItems: [{
					hidden: true,
					xtype: 'toolbar',
					dock: 'bottom',
					ui: 'footer',
					itemId: 'bottom',
					items: [{
						xtype: 'button',
						text: 'Download List',
						minWidth: 68,
						disabled: true,
						listeners: {
							afterrender: function(button, eOpts){
								let panel = button.up('panel#system-panel');
								let treepanel = panel.down('treepanel#system-treepanel');
								let selmodel = treepanel.getSelectionModel();
								selmodel.on({
									selectionchange: function(selmodel, selected, eOpts){
										button.setDisabled(selmodel.getCount() > 0 ? false : true);
									}
								});
							},
							click: function(button){
/*
								var system_tree_store = Ext.data.StoreManager.lookup('system-tree-store');
								var rootnode = system_tree_store.getRootNode();
								if(rootnode){

									const filename = 'category.tsv';
									const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
									let category_data = ['#category','count','ids'].join("\t")+"\n";

									rootnode.cascadeBy(function(){
										var node = this;
										console.log('cascadeBy',node.isLeaf(),node.getData());
										var data = node.getData();
										if(data.id=='root') return true;

										var category = node.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
										if(category.match(/^[0-9]+(.+)$/)) category = RegExp.$1;
										if(category.match(/^_+(.+)$/)) category = RegExp.$1;
//text/tab-separated-values
										var data_count = node.get('data_count');
										var datas = node.get('datas');
										let ids = Ext.Array.map(datas, function(data){
											return data['id'];
										}).join(',');
										category_data += [category,data_count,ids].join("\t")+"\n";
									});
									const blob = new Blob([bom, category_data], { type: 'text/tab-separated-values' });

									const url = (window.URL || window.webkitURL).createObjectURL(blob);
									const download = document.createElement("a");
									download.href = url;
									download.download = filename;
									download.click();
									(window.URL || window.webkitURL).revokeObjectURL(url);

								}
*/
								const fileext = '.tsv';
								const basefilename = 'category_';
								const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
								let filename = basefilename;
								let download_string;

								let line_feed_code = "\n";
								if(window.navigator.userAgent.toLowerCase().indexOf("windows nt")>=0) line_feed_code = "\r\n";

								const panel = button.up('panel#system-panel');
								const treepanel = panel.down('treepanel#system-treepanel');
								const selmodel = treepanel.getSelectionModel();
								const selnode = selmodel.getLastSelected();
								const parentId = selnode.get('parentId');
								let text = selnode.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
								if(text.match(/^[0-9]+(.+)$/)) text = RegExp.$1;
								if(text.match(/^_+(.+)$/)) text = RegExp.$1;
								if(parentId=='root'){
									filename += text;
								}
								else{
									filename += parentId + '_' + text;
								}
								filename = filename.replace(/[^A-Za-z0-9]+/g,'_');
								filename += fileext;
//								console.log(filename);

								const gridpanel = panel.down('gridpanel#system-gridpanel');
								const store = gridpanel.getStore();
								let download_columns = [];
								Ext.Array.each(gridpanel.columns, function(column){
									if(!column.isHideable() && column.isHidden()) return true;
//									console.log(column);
									download_columns.push(column);
								});
								download_string = '#' + Ext.Array.map(download_columns, function(column){return column.text;}).join("\t")+line_feed_code;
//								console.log(download_string);


								store.each(function(record){
									let values = [];
									Ext.Array.each(download_columns, function(column){
										let value = record.get(column.dataIndex);
										if(Ext.isArray(value)){
											if(column.dataIndex=='is_a' || column.dataIndex=='part_of' || column.dataIndex=='lexicalsuper'){
												value = Ext.Array.map(value, function(item){
													return item.id+':'+item.name;
												});
											}
											let hash = {};
											Ext.Array.map(value, function(v){ hash[v] = null; });
											value = Ext.Object.getKeys(hash).sort().join(';');
										}
										if(Ext.isEmpty(value)) value = '';
										values.push(value);
									});
									if(values.length) download_string += values.join("\t")+line_feed_code;
								});
//								console.log(download_string);

								const blob = new Blob([bom, download_string], { type: 'text/tab-separated-values' });
								const url = (window.URL || window.webkitURL).createObjectURL(blob);
								const download = document.createElement("a");
								download.href = url;
								download.download = filename;
								download.click();
								(window.URL || window.webkitURL).revokeObjectURL(url);
							}
						}
					}]
				}],
				listeners: {
					afterrender: function(panel, eOpts){
						var viewport = self.getViewport();
						var window_panel         = viewport.down('panel#window-panel');
/*
						var version_combobox         = window_panel.down('combobox#version-combobox');
						if(version_combobox){
							version_combobox.on({
								select: function( field, records, eOpts ){
									console.log('select', field, records);
								}
							})
						}
*/
						var segment_filtering_combobox = window_panel.down('combobox#segment-filtering-combobox');

						var cities_store = Ext.data.StoreManager.lookup('cities-list-store');
						var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
						var system_tree_store = Ext.data.StoreManager.lookup('system-tree-store');

						var fn = function(){
							panel.setLoading(true);

							var version;
							var ids;
							var art_ids;
							if(self.DEF_MODEL_VERSION_RECORD && self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
								version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);
								Ag.data.isLoadingRenderer = Ag.data.isLoadingRenderer || {};
								if(Ag.data.isLoadingRenderer[version]) return;
							}
							else{
								Ext.defer(fn, 250);
								return;
							}
//							console.log('loadrenderer');
							if(cities_store.isLoading()){
								cities_store.on({
									load: {
										fn: fn,
										single: true
									}
								});
								return;
							}
							if(system_list_store.isLoading()){
								system_list_store.on({
									load: {
										fn: fn,
										single: true
									}
								});
								return;
							}

							if(Ag.data.renderer && version){
								ids = Ag.data.renderer[version]['ids'];
								art_ids = Ag.data.renderer[version]['art_ids'];
							}
							if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
								if(Ext.isEmpty(ids)) console.warn('ids is empty!!');
								if(Ext.isEmpty(art_ids)) console.warn('art_ids is empty!!');
								panel.setLoading(false);
								return;
							}
							var SEG2ART = segment_filtering_combobox.getValue()==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

							var rootnode = system_tree_store.getRootNode();
//							console.log('fn',rootnode);
							if(rootnode){


								var name2cities = {};
								var cities = Ext.Array.map(cities_store.getRange(),function(record){
									var data = record.getData();
									name2cities[data['name']] = data;
									return data;
								});
//									console.log(name2cities);


								var system2id;
								var use_ids;
								Ext.Object.each(art_ids, function(art_id, data, myself) {
									try{
//										console.log(art_id,data);
										var id = data[Ag.Def.ID_DATA_FIELD_ID];
										var artc_id = data[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
										if(Ext.isEmpty(id) || Ext.isEmpty(ids[id])) return true;
										if(!Ext.isBoolean(ids[id]['is_element']) || !ids[id]['is_element']) return true;
										var system_id = ids[id][Ag.Def.SYSTEM_ID_DATA_FIELD_ID];
										if(Ext.isString(system_id) && system_id.length){
											if(Ext.isEmpty(system2id)) system2id = {};
											if(Ext.isEmpty(system2id[system_id])) system2id[system_id] = [];
											system2id[system_id].push(id);

											if(Ext.isEmpty(use_ids)) use_ids = {};
											if(Ext.isEmpty(use_ids[id])){
												var tempobj = {};
												tempobj[Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
												tempobj[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = artc_id;
												use_ids[id] = Ext.Object.merge(tempobj, ids[id]);
											}

											if(
												Ext.isDefined(Ag.data.MENU_SEGMENTS_in_art_file) &&
												Ext.isDefined(Ag.data.MENU_SEGMENTS_in_art_file[art_id]) &&
												Ext.isObject(Ag.data.MENU_SEGMENTS_in_art_file[art_id])
											){
												Ext.Array.each(Ext.Object.getKeys(Ag.data.MENU_SEGMENTS_in_art_file[art_id]['CITIES'] || {}), function(cities_name){
													var cities_id = name2cities[cities_name]['cities_id'];
													if(Ext.isEmpty(use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID])){
														use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID] = [cities_id];
														if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'] = [Ag.data.citiesids2segment[cities_id]];
													}
													else{
														var temp_hash = {};
														Ext.Array.each(use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID], function(temp_id){
															temp_hash[temp_id] = null;
														});
														temp_hash[cities_id] = null;
														use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID] = Ext.Object.getKeys(temp_hash);
														if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length){
															temp_hash = {};
															Ext.Array.each(use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID], function(temp_id){
																temp_hash[Ag.data.citiesids2segment[temp_id]] = null;
															});
															use_ids[id]['segment'] = Ext.Object.getKeys(temp_hash);
														}
													}
												});
											}

											if(Ext.isObject(use_ids[id]['relation'])){
												Ext.Object.each(use_ids[id]['relation'], function(relation,value){
													if(Ext.isObject(value)){
														Ext.Object.each(value, function(rid,rname){
															var v = use_ids[id][relation];
															if(Ext.isEmpty(v)){
																v = [{id:rid,name:rname}];
															}
															else{
																v.push({id:rid,name:rname});
															}
															use_ids[id][relation] = v;

															if(relation == 'is_a' || relation == 'lexicalsuper') return true;
															v = use_ids[id]['part_of'];
															if(Ext.isEmpty(v)){
																v = [{id:rid,name:rname}];
															}
															else{
																v.push({id:rid,name:rname});
															}
															use_ids[id]['part_of'] = v;
														});
													}
												});
											}

										}
									}catch(e){
										console.error(e);
									}
								});



								if(!rootnode.hasChildNodes()){
									rootnode.appendChild(Ext.Array.map(system_list_store.getRange(), function(record){ return Ext.Object.merge({leaf:true},record.getData()); }));
								}
								rootnode.cascadeBy(function(){
									var node = this;
//									console.log('cascadeBy',node.isLeaf(),node.getData());
//									if(node.isLeaf() || true){
									if(node.isLeaf()){

										var system_id = (node.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID).split('/'))[0];

//										system2id[system_id].push(id);

										var len = 0
										var add_datas;

										if(Ext.isArray(system2id[system_id])){
											add_datas = Ext.Array.map(system2id[system_id], function(id){
												return use_ids[id];
											});
											len = add_datas.length;
										}
										var text = node.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
										if(text.match(/^[0-9]+(.+)$/)) text = RegExp.$1;
										if(text.match(/^_+(.+)$/)) text = RegExp.$1;
										node.beginEdit();
										node.set('text',Ext.util.Format.format('{0}({1})',text,Ext.util.Format.number(len,'0,000')));
										node.set('data_count', len);
										node.set('datas', add_datas);
										node.commit(false,['text','data_count','datas']);
										node.endEdit(false,['text','data_count','datas']);

//										console.log(node.get('text'),add_datas.length);
									}
								});
							}
							panel.setLoading(false);
						};

						self.on('loadrenderer',fn,self);

//						console.log('loading', segment_store.isLoading());
						if(system_list_store.isLoading()){
							system_list_store.on({
								load: {
									fn: function( store, node, records, successful, eOpts ){
//										console.log('load', store, node, records, successful, eOpts);
										fn();
									},
									single: true
								}
							});
						}
						else{
							Ext.defer(fn, 0);
						}
					},
					beforeselect: function( selmodel, record, index, eOpts ){
						return record.isLeaf();
					},
					beforeitemclick: function( view, record, item, index, e, eOpts ){
//						console.log('beforeitemclick',view, record, item, index, e);
						return record.isLeaf();
					},
					beforeitemcollapse: function( node, eOpts ){
//						console.log('beforeitemcollapse',node);
					},
					select: function( selmodel, record, index, eOpts ){
						var system_grid_store = Ext.data.StoreManager.lookup('system-grid-store');
						system_grid_store.removeAll();//add_datas.length?true:false);
						var add_records = system_grid_store.add(record.get('datas'));
					}
				}
			},{
				flex: 1,
				xtype: 'gridpanel',
				itemId: 'system-gridpanel',
				store: Ext.data.StoreManager.lookup('system-grid-store'),
				viewConfig: self.getViewConfig(),
				selModel: {
	//						mode : 'SIMPLE'
					mode : 'MULTI'
				},
				columnLines: true,
				dockedItems: [{
	//				hidden: true,
					xtype: 'toolbar',
					dock: 'bottom',
					ui: 'footer',
					itemId: 'bottom',
					items: [
					{
						xtype: 'button',
						text: 'Download List',
						minWidth: 68,
						disabled: true,
						listeners: {
							afterrender: function(button, eOpts){
								let panel = button.up('panel#system-panel');
								let treepanel = panel.down('treepanel#system-treepanel');
								let selmodel = treepanel.getSelectionModel();
								selmodel.on({
									selectionchange: function(selmodel, selected, eOpts){
										button.setDisabled(selmodel.getCount() > 0 ? false : true);
									}
								});
							},
							click: function(button){
/*
								var system_tree_store = Ext.data.StoreManager.lookup('system-tree-store');
								var rootnode = system_tree_store.getRootNode();
								if(rootnode){

									const filename = 'category.tsv';
									const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
									let category_data = ['#category','count','ids'].join("\t")+"\n";

									rootnode.cascadeBy(function(){
										var node = this;
										console.log('cascadeBy',node.isLeaf(),node.getData());
										var data = node.getData();
										if(data.id=='root') return true;

										var category = node.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
										if(category.match(/^[0-9]+(.+)$/)) category = RegExp.$1;
										if(category.match(/^_+(.+)$/)) category = RegExp.$1;
//text/tab-separated-values
										var data_count = node.get('data_count');
										var datas = node.get('datas');
										let ids = Ext.Array.map(datas, function(data){
											return data['id'];
										}).join(',');
										category_data += [category,data_count,ids].join("\t")+"\n";
									});
									const blob = new Blob([bom, category_data], { type: 'text/tab-separated-values' });

									const url = (window.URL || window.webkitURL).createObjectURL(blob);
									const download = document.createElement("a");
									download.href = url;
									download.download = filename;
									download.click();
									(window.URL || window.webkitURL).revokeObjectURL(url);

								}
*/
								const fileext = '.tsv';
								const basefilename = 'category_';
								const bom = new Uint8Array([0xef, 0xbb, 0xbf]);
								let filename = basefilename;
								let download_string;

								let line_feed_code = "\n";
								if(window.navigator.userAgent.toLowerCase().indexOf("windows nt")>=0) line_feed_code = "\r\n";

								const panel = button.up('panel#system-panel');
								const treepanel = panel.down('treepanel#system-treepanel');
								const selmodel = treepanel.getSelectionModel();
								const selnode = selmodel.getLastSelected();
								const parentId = selnode.get('parentId');
								let text = selnode.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
								if(text.match(/^[0-9]+(.+)$/)) text = RegExp.$1;
								if(text.match(/^_+(.+)$/)) text = RegExp.$1;
								if(parentId=='root'){
									filename += text;
								}
								else{
									filename += parentId + '_' + text;
								}
								filename = filename.replace(/[^A-Za-z0-9]+/g,'_');
								filename += fileext;
//								console.log(filename);

								const gridpanel = panel.down('gridpanel#system-gridpanel');
								const store = gridpanel.getStore();
								let download_columns = [];
								Ext.Array.each(gridpanel.columns, function(column){
									if(!column.isHideable() && column.isHidden()) return true;
//									console.log(column);
									download_columns.push(column);
								});
								download_string = '#' + Ext.Array.map(download_columns, function(column){return column.text;}).join("\t")+line_feed_code;
//								console.log(download_string);


								store.each(function(record){
									let values = [];
									Ext.Array.each(download_columns, function(column){
										let value = record.get(column.dataIndex);
										if(Ext.isArray(value)){
											if(column.dataIndex=='is_a' || column.dataIndex=='part_of' || column.dataIndex=='lexicalsuper'){
												value = Ext.Array.map(value, function(item){
													return item.id+':'+item.name;
												});
											}
											let hash = {};
											Ext.Array.map(value, function(v){ hash[v] = null; });
											value = Ext.Object.getKeys(hash).sort().join(';');
										}
										if(Ext.isEmpty(value)) value = '';
										values.push(value);
									});
									if(values.length) download_string += values.join("\t")+line_feed_code;
								});
//								console.log(download_string);

								const blob = new Blob([bom, download_string], { type: 'text/tab-separated-values' });
								const url = (window.URL || window.webkitURL).createObjectURL(blob);
								const download = document.createElement("a");
								download.href = url;
								download.download = filename;
								download.click();
								(window.URL || window.webkitURL).revokeObjectURL(url);
							}
						}
					},
					'->'
					,{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'bold'},
						text: 'Load / Render'
					}
					,{
						xtype: 'button',
						text: 'Selected',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#system-panel').down('gridpanel#system-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									add: function(store, records, index, eOpts){
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										if(store.getCount()==0) button.setDisabled(true);
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										button.setDisabled(selected.length==0 ? true : false);
									}
								});
								button.setDisabled(true);
							},
							click: function(button){
								var gridpanel = button.up('panel#system-panel').down('gridpanel#system-gridpanel');
								var store = gridpanel.getStore();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												gridpanel.getSelectionModel().getSelection(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										store.removeAll();

										let treepanel = button.up('panel#system-panel').down('treepanel#system-treepanel');
										if(treepanel) treepanel.getSelectionModel().deselectAll();

									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,{
						xtype: 'button',
						text: 'All',
						minWidth: 68,
						listeners: {
							afterrender: function(button){
								var gridpanel = button.up('panel#system-panel').down('gridpanel#system-gridpanel');
								var store     = gridpanel.getStore();
								store.on({
									add: function(store, records, index, eOpts){
										button.setDisabled(store.getCount()==0 ? true : false);
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										button.setDisabled(store.getCount()==0 ? true : false);
									}
								});
								button.setDisabled(store.getCount()==0 ? true : false);
							},
							click: function(button){
								var gridpanel = button.up('panel#system-panel').down('gridpanel#system-gridpanel');
								var store = gridpanel.getStore();
								var match_list_store   = Ext.data.StoreManager.lookup(Ag.Def.CONCEPT_MATCH_LIST_STORE_ID);
								button.setDisabled(true);
								gridpanel.setLoading('Please wait...');
								Ext.defer(function(){
									try{
										var exists_datas = {};
										Ext.Array.each(match_list_store.getRange(), function(item){ exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)] = item.getData(); });
										var datas = Ext.Array.map(
											Ext.Array.filter(
												store.getRange(),
												function(item){
													return !Ext.isDefined(exists_datas[item.get(Ag.Def.ID_DATA_FIELD_ID)]);
												}
											),
											function(item){
												return item.getData();
											}
										);
										if(datas.length) match_list_store.add(datas);
										store.removeAll();

										let treepanel = button.up('panel#system-panel').down('treepanel#system-treepanel');
										if(treepanel) treepanel.getSelectionModel().deselectAll();

									}catch(e){
										console.error(e);
										button.setDisabled(false);
									}
									gridpanel.setLoading(false);
								},100);
							}
						}
					}
					,'-',{
						xtype: 'tbtext',
						style:{'cursor':'default','user-select':'none','font-weight':'normal'},
						text: '0 / 0',
						listeners: {
							afterrender: function(tbtext){
	//							console.log('afterrender',tbtext);
								var gridpanel = tbtext.up('panel#system-panel').down('gridpanel#system-gridpanel');
								var store     = gridpanel.getStore();
								var selmodel  = gridpanel.getSelectionModel();
								store.on({
									add: function(store, records, index, eOpts){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									},
									bulkremove: function( store, records, indexes, isMove, eOpts ){
										tbtext.setText(Ext.util.Format.format('0 / {0}',Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
								selmodel.on({
									selectionchange: function( selmodel, selected, eOpts ){
										tbtext.setText(Ext.util.Format.format('{0} / {1}',Ext.util.Format.number(selected.length,'0,000'),Ext.util.Format.number(store.getCount(),'0,000')));
									}
								});
							}
						}
					}
					]
				}],
				columns: [

					{
						text: 'palette',
						tooltip: 'exists palette',
//						xtype: 'agcheckcolumn',
						dataIndex: Ag.Def.EXISTS_PALETTE_FIELD_ID,
						align: 'center',
						width: 34,
						locked: false,
						lockable: false,
						draggable: false,
						sortable: true,
						hideable: false,
						hidden: true,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							return Ext.util.Format.format(
											'<span class="glyphicon {0} keyword-search-gridpanel-column-{2}" aria-hidden="true" data-fmaid="{1}" data-qtip="exists palette" style="cursor:pointer;"></span>',
											value===true ? 'glyphicon-check' :'glyphicon-unchecked',
											record.get(Ag.Def.ID_DATA_FIELD_ID),
											Ag.Def.EXISTS_PALETTE_FIELD_ID
										);
						}
					},
/*
					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
//								metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-obj';
//								console.log(value, rowIndex, colIndex);
							var rtn;
							var artc_id = record.get(Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID);
							if(Ext.isString(artc_id) && artc_id.length){
								rtn = artc_id;
							}
							else{
								rtn = Ext.isString(value) ? value.replace(/^([A-Z]+[0-9]+).*$/g,'$1') : value;
							}
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
*/
					{
						text: 'obj',
						tooltip: 'obj',
						dataIndex: Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID,
						width: 82,
						lockable: false,
						draggable: false,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							var rtn = value;
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(rtn) + '"';
							return rtn;
						}
					},
					{
						text: 'FMAID',
						tooltip: 'FMAID',
//						dataIndex: Ag.Def.ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: Ag.Def.ID_DATA_FIELD_ID+'_renderer',
						lockable: false,
						draggable: false,
						hideable: false,
						width: 63,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-fmaid';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
//							var rtn = value;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)[A-Z]*\-[LRU]+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)\-.+$/)) rtn = RegExp.$1;
//							if(Ext.isString(rtn) && rtn.match(/^FMA([0-9]+)$/)) rtn = RegExp.$1;
////							return rtn;
//							var rtn = record.get(Ag.Def.ID_DATA_FIELD_ID+'_renderer');
							var rtn = value;

							if(Ext.isString(rtn) && rtn.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(rtn,dataIndex,value,'bp3d-fmaid');
							}
							return rtn;

						}
					},
					{
						text: 'SUB',
						tooltip: 'SUB',
						dataIndex: 'sub'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-sub';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-sub');
							}
							return value;
						}
					},
					{
						text: 'R/L',
						tooltip: 'R/L',
						dataIndex: 'laterality'+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						align: 'center',
						width: 42,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-laterality';
//							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
//									return make_ag_word(value,dataIndex,null,'bp3d-laterality');
								return make_ag_word(value,dataIndex,null,'bp3d-laterality',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.NAME_DATA_FIELD_ID,
						tooltip: Ag.Def.NAME_DATA_FIELD_ID,
						dataIndex: Ag.Def.NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: false,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
//							console.log(store);
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-name';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							if(Ext.isString(value) && value.length){
//									return make_ag_word(value,null,'bp3d-name');
//										console.log(value,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-name',null,record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID));
							}
							return value;
						}
					},
					{
						text: Ag.Def.SYNONYM_DATA_FIELD_ID,
						tooltip: Ag.Def.SYNONYM_DATA_FIELD_ID,
						dataIndex: Ag.Def.SYNONYM_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: true,
						flex: 1,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-synonym';
							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex);
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,get_relation_column('is_a'+renderer_dataIndex_suffix,'is_a',false)
					,get_relation_column('part_of'+renderer_dataIndex_suffix,'part_of',false)
					,get_relation_column('lexicalsuper'+renderer_dataIndex_suffix,'nominal super',false)
					,
					{
						text: 'Segment',
						tooltip: 'Segment',
//							dataIndex: Ag.Def.OBJ_CITIES_FIELD_ID+renderer_dataIndex_suffix,
						dataIndex: 'segment',
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: true,
						hidden: false,
						width: 50,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-segment';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
//							return value;
							var dataIndex = view.getGridColumns()[colIndex].dataIndex;
							if(Ext.isString(value) && value.length){
								return make_ag_word(value,dataIndex,null,'bp3d-segment');
							}
							else if(Ext.isArray(value) && value.length){
								var rtn = [];
								Ext.Array.each(value, function(v,i){
									if(Ext.isString(value[i]) && value[i].length){
										rtn.push(make_ag_word(value[i],dataIndex,null,'bp3d-segment'));
									}
									else if(Ext.isNumber(value[i])){
										rtn.push(make_ag_word(value[i]+'',dataIndex,null,'bp3d-segment'));
									}
								});
								return rtn.join('');
							}
							return value;
						}
					}
					,{
						hidden: true,
						hideable: false,
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+renderer_dataIndex_suffix,
						lockable: false,
						draggable: false,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-category';
							metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
							if(view.getItemId()==='selected-tags-tableview') return value;
							return value;
							if(Ext.isString(value) && value.length){
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-category');
							}
							return value;
						}
					}
					,{
//							text: 'System',
//							tooltip: 'System',
						text: 'Category',
						tooltip: 'Category',
						dataIndex: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+renderer_dataIndex_suffix,
						align: 'center',
						lockable: false,
						draggable: false,
						hideable: false,
						hidden: true,
						width: 70,
						renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
							if(!Ext.isEmpty(renderer_dataIndex_suffix)) return value;
							metaData.tdCls += 'bp3d-grid-cell bp3d-grid-cell-system';
							value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer');
							if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
							if(Ext.isString(value) && value.length){
//								if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
//								if(value.match(/^_+(.+)$/)) value = RegExp.$1;
								metaData.tdAttr = 'data-qtip="' + Ext.String.htmlEncode(value) + '"';
								if(view.getItemId()==='selected-tags-tableview') return value;
//								return value;
								var dataIndex = view.getGridColumns()[colIndex].dataIndex;
								return make_ag_word(value,dataIndex,null,'bp3d-system');
							}
							return value;
						}
					}
				],
				plugins: [
					Ext.create('Ext.grid.plugin.CellEditing', {
						clicksToEdit: 1,
						listeners: {
							beforeedit: function(editor,e,eOpts){
							},
							edit: function(editor,e,eOpts){
								console.log(e);
							}
						}
					}),
					self.getBufferedRenderer({pluginId: 'system-gridpanel-plugin'})
				],
				listeners: {
					afterrender: function( gridpanel, eOpts ){
						gridpanel.getView().on({
							itemkeydown: function(view, record, item, index, e, eOpts){
								if(e.getKey()===e.C && (e.ctrlKey || e.metaKey)){
									self.copyGridColumnsText(view);
								}
							}
						});

						var store = gridpanel.getStore();
						store.removeAll();	//emptyTextが表示されない為、あえてクリアする
						var selmodel     = gridpanel.getSelectionModel();
						var gridview     = gridpanel.getView();
						var $gridviewdom = $(gridview.el.dom);

						$gridviewdom.on('mousedown','a.bp3d-word-button', function(e){
							var $this = $(this);
							gridpanel.setLoading('searching...');
							Ext.defer(function(){

								var value = $this.attr('data-value');
								var dataIndex = $this.attr('data-dataIndex');
								if(dataIndex==Ag.Def.ID_DATA_FIELD_ID) dataIndex = Ag.Def.ID_DATA_FIELD_ID+'_renderer';
								if(dataIndex==Ag.Def.SYSTEM_ID_DATA_FIELD_ID) dataIndex = Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer';
//								console.log(dataIndex,value);
								var $tr = $this.closest('tr.x-grid-data-row');
								var $tbody = $tr.closest('tbody');
								var record = gridview.getRecord($tr.get(0));
								if(record){
//									gridview.saveScrollState();
//									gridpanel.suspendEvents(false);
									try{
	//									var value = record.get(dataIndex);
										var isSelected = selmodel.isSelected(record);
//										console.log(dataIndex,value,isSelected);
										var records = [];
										var startIndex = -1;
										var record;
										do {
											startIndex = store.findBy( function(record,id){
												var f_value = record.get(dataIndex);
												if(Ext.isString(value) && Ext.isString(f_value)){
													return value===f_value;
												}
												else if(Ext.isString(value) && Ext.isArray(f_value)){
													var rtn = false;
													Ext.Array.each( f_value, function(item,index,array){
														if(Ext.isString(item)){
															rtn = item===value;
														}
														else{
															rtn = item.name===value;
														}
														if(rtn) return false;
													});
													return rtn;
												}
											}, self, ++startIndex);
											record = null;
											if(startIndex>=0) record = store.getAt(startIndex);
	//										console.log(startIndex,record,isSelected);
											if(record) records.push(record);
										} while(startIndex>=0)
	//									console.log(records);
										if(isSelected){
											selmodel.select(records,true);
										}
										else{
											selmodel.deselect(records);
										}
									}catch(e){
										console.error(e);
									}
//									gridview.refresh();
//									gridview.restoreScrollState();
								}
								gridpanel.setLoading(false);
							}, 100);

							e.preventDefault();
							e.stopPropagation();
							e.stopImmediatePropagation()
							return false;
						});

					}
				}

			}]
		};

		var viewport_items = [Ext.create('Ext.panel.Panel', {
			itemId: 'window-panel',
			border: false,
			layout: 'border',
			items: [{
				itemId: 'north-panel',
				region: 'north',
//				height: 70,
				height: 40,
				bodyStyle: 'background-color:#1D7BCA;',
				bodyPadding: '5 0 0 10',
				layout: {
					type: 'hbox',
					align: 'top',
					pack: 'start'
				},
				layout: {
					type: 'hbox',
					align: 'top',
					pack: 'start'
				},
				defaults: {
/*
					layout: {
						type: 'vbox',
						align: 'left',
						pack: 'start',
						defaultMargins: {top: 0, right: 0, bottom: 0, left: 0},
					},
*/
					layout: {
						type: 'hbox',
						align: 'middle',
						pack: 'center',
						defaultMargins: {top: 0, right: 10, bottom: 0, left: 0},
					}
				},
				defaultType: 'fieldcontainer',
				items: [{
					items: [{
						xtype: 'label',
						style: {'color':'#FFFFFF','font-size':'1.6em','font-weight':'bold'},
						html: '<b>BodyParts3D</b>'
					},{
						style: 'margin:5px 0 0 0;',
						itemId: 'version-combobox',
						width: 184,
						xtype: 'combobox',
						labelWidth: 60,
						labelAlign: 'right',
	//					fieldLabel: 'Version',
						store: version_store,
						queryMode: 'local',
						displayField: 'display',
						valueField: 'value',
						editable: false,
						matchFieldWidth: false,
						value: version_value,
						listeners: {
							afterrender: function(field, eOpts){
								field.setValue(version_value);
								field.fireEvent('select', field, self.DEF_MODEL_VERSION_RECORD);
							},
							select: function( field, records, eOpts ){
//								console.log('select', field, self.DEF_MODEL_VERSION_RECORD);
								if(Ext.isEmpty(records)){
									self.DEF_MODEL_VERSION_RECORD = null;
								}
								else if(Ext.isArray(records) && records.length && records[0] instanceof Ext.data.Model){
									self.DEF_MODEL_VERSION_RECORD = records[0];
								}
								else if(records instanceof Ext.data.Model){
									self.DEF_MODEL_VERSION_RECORD = records;
								}
								if(self.DEF_MODEL_VERSION_RECORD instanceof Ext.data.Model){
									Ext.state.Manager.set('version-combobox-display',self.DEF_MODEL_VERSION_RECORD.get('display'));
								}
								else{
									Ext.state.Manager.set('version-combobox-display',null);
								}
								self.loadRendererFile();
							}
						}
					}]
				},{
					hidden: true,
					fieldLabel: 'Body Segment',
					labelAlign: 'right',
					labelStyle: 'color:#FFFFFF;',
					labelWidth: 92,
					items: [{
						itemId: 'segment-treepicker',
						width: 310,
						xtype: 'treepicker',
						name: 'treepicker',
						store: segment_store,
						displayField: 'text',
						valueField: 'segment',
						editable: false,
						matchFieldWidth: true,
						value: 'whole',
						listeners: {
							afterrender: function(field, eOpts){
							},
							select: function( field, record, eOpts ){
								if(record instanceof Ext.data.Model){
									self.DEF_MODEL_SEGMENT_RECORD = record;
								}
								else{
									self.DEF_MODEL_SEGMENT_RECORD = null;
								}
							}
						}
					},{
						hidden: false,
						width: 100,
						editable: false,
						itemId: 'segment-filtering-combobox',
						xtype: 'combobox',
						store: Ext.create('Ext.data.Store', {
							fields: ['value', 'display'],
							data : [
								{"value":"SEG2ART", "display":"All Polygon"},
								{"value":"SEG2ART_INSIDE", "display":"Centroid"}
							]
						}),
						queryMode: 'local',
						displayField: 'display',
						valueField: 'value',
						value: self.DEF_SEGMENT_FILTER,
						listeners: {
							change: function( field, newValue, oldValue, eOpts ){
								self.DEF_SEGMENT_FILTER = newValue;
							},
							select: function( field, records, eOpts ){
							}
						}
					}]
				},{
					hidden: true,
					layout: {
						type: 'vbox',
						align: 'left',
						pack: 'start',
						defaultMargins: {top: 0, right: 0, bottom: 0, left: 0},
					},
					fieldLabel: 'LOAD (add) to Palette',
					labelAlign: 'right',
					labelWidth: 140,
					labelStyle: 'color:#FFFFFF;',
					items: [{
						xtype: 'fieldcontainer',
						layout: {
							type: 'hbox',
							align: 'middle'
						},
						defaultMargins: {top: 0, right: 0, bottom: 0, left: 0},
						items: [{

							xtype: 'button',
							text: 'Load All item',
							itemId: 'all-item-button',
							disabled: true,
							listeners: {
								afterrender: function(button, eOpts){
									var segment_treepicker = button.up('fieldcontainer').up('fieldcontainer').prev('fieldcontainer').down('treepicker#segment-treepicker');
									if(segment_treepicker){
										segment_treepicker.on({
											select: function(field, records, eOpts){
												button.setDisabled(field.getValue()==='whole');
											}
										});
										button.setDisabled(segment_treepicker.getValue()==='whole');
									}
								},
								click: function(button, eOpts){
									if(Ext.isEmpty(self.DEF_MODEL_VERSION_RECORD) || Ext.isEmpty(self.DEF_MODEL_SEGMENT_RECORD)){
										button.setDisabled(true);
										return;
									}
									var cities_ids = self.DEF_MODEL_SEGMENT_RECORD.get('cities_ids')

									if(Ext.isString(cities_ids) && cities_ids.length){
										var segment_filtering_combobox = button.up('fieldcontainer').up('fieldcontainer').prev('fieldcontainer').down('combobox#segment-filtering-combobox');
										var SEG2ART = segment_filtering_combobox.getValue()==='SEG2ART' ? Ag.data.SEG2ART : Ag.data.SEG2ART_INSIDE;

										var version = self.DEF_MODEL_VERSION_RECORD.get(Ag.Def.VERSION_STRING_FIELD_ID);

										var ids;
										var art_ids;
										if(Ag.data.renderer && version){
											ids = Ag.data.renderer[version]['ids'];
											art_ids = Ag.data.renderer[version]['art_ids'];
										}
										if(Ext.isEmpty(ids) || Ext.isEmpty(art_ids)){
											if(Ext.isEmpty(ids)) console.warn('ids is empty!!');
											if(Ext.isEmpty(art_ids)) console.warn('art_ids is empty!!');
											return;
										}

										var use_ids;

										Ext.Array.each(cities_ids.split(','), function(cities_id){
	//										var cities_record = cities_store.getAt(cities_id-1);	// unfound対応(2019/12/27)
											var cities_record = cities_store.getAt(cities_id);	// unfound対応(2019/12/27)
											if(Ext.isEmpty(cities_record)) return true;
											var cities_name = cities_record.get('name');
											if(Ext.isEmpty(cities_name)) return true;
											if(Ext.isObject(SEG2ART['CITIES']) && Ext.isObject(SEG2ART['CITIES'][cities_name])){
												Ext.Object.each(SEG2ART['CITIES'][cities_name], function(art_id){
													var id;
													var artc_id;
													if(Ext.isObject(art_ids[art_id])){
														if(Ext.isEmpty(use_ids)) use_ids = {};
														id = art_ids[art_id][Ag.Def.ID_DATA_FIELD_ID];
														artc_id = art_ids[art_id][Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID];
													}
													if(Ext.isEmpty(id) || Ext.isEmpty(ids[id])) return true;
													if(Ext.isEmpty(use_ids[id])){
														var tempobj = {};
														tempobj[Ag.Def.OBJ_ID_DATA_FIELD_ID] = art_id;
														tempobj[Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID] = artc_id;
														use_ids[id] = Ext.Object.merge(tempobj, ids[id]);
													}
													if(Ext.isEmpty(use_ids[id]['cities_ids'])){
														use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID] = [cities_id];
														if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'] = [Ag.data.citiesids2segment[cities_id]];
													}
													else{
														use_ids[id][Ag.Def.OBJ_CITIES_FIELD_ID].push(cities_id);
														if(Ext.isString(Ag.data.citiesids2segment[cities_id]) && Ag.data.citiesids2segment[cities_id].length) use_ids[id]['segment'].push(Ag.data.citiesids2segment[cities_id]);
													}

												});
											}
										});

										if(Ext.isEmpty(use_ids)){
											match_list_store.removeAll();//add_datas.length?true:false);
											return;
										}

										var use_system_ids;
										var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
										system_list_store.filter([{
											property: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
											value: true
										}]);
										if(system_list_store.getCount()>0){
											use_system_ids = {};
											system_list_store.each(function(record){
												use_system_ids[record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID)] = record.getData();
											});
										}
										system_list_store.clearFilter();


										var add_datas = [];
										Ext.Object.each(use_ids,function(id,data){

											var cdi_name = data[Ag.Def.ID_DATA_FIELD_ID];
											var system_id = data[Ag.Def.SYSTEM_ID_DATA_FIELD_ID];

											if(Ext.isObject(use_system_ids)){
												if(Ext.isEmpty(use_system_ids[system_id])) return true;
											}


											if(Ext.isObject(data['relation'])){
												Ext.Object.each(data['relation'], function(relation,value){
													if(Ext.isObject(value)){
														Ext.Object.each(value, function(id,name){
															var v = data[relation];
															if(Ext.isEmpty(v)){
																v = [{id:id,name:name}];
															}
															else{
																v.push({id:id,name:name});
															}
															data[relation] = v;

															if(relation == 'is_a' || relation == 'lexicalsuper') return true;
															v = data['part_of'];
															if(Ext.isEmpty(v)){
																v = [{id:id,name:name}];
															}
															else{
																v.push({id:id,name:name});
															}
															data['part_of'] = v;
														});
													}
												});
											}
											add_datas.push(data);
										});

										match_list_store.removeAll();//add_datas.length?true:false);
										var add_records = match_list_store.add(add_datas);
									}
								}
							}
						}]
					},{
/*
						width: 200,
						style: 'margin:5px 0 0 0;',
						xtype: 'searchfield',
						name: 'searchfield',
						store: search_store
*/
						xtype: 'fieldcontainer',
						layout: {
							type: 'hbox',
							align: 'middle'
						},
						items: [{
							width: 200,
							style: 'margin:5px 0 0 0;',
							xtype: 'searchfield',
							itemId: 'searchfield',
							name: 'searchfield',
							store: search_store
						},{
							hidden: false,
							style: 'margin:0 5px 5px 5px;',
							xtype: 'radiogroup',
							itemId: 'search-target',
							columns: [77,149],
							defaults: {
								style:{'color':'white'}
							},
							items: [{
								boxLabel:   'Element',
								name:       'searchTarget',
								inputValue: '1',
								checked:    true
							},{
								boxLabel:   'Include HYPERNYM',
								name:       'searchTarget',
								inputValue: '2'
							}]
						}]

					}]
				}]
			},{
//				itemId: 'west-panel',
//				region: 'west',
				itemId: 'center-panel',
				region: 'center',
				split: true,
				width: center_width/5*2,
				minWidth: 475,
				dockedItems: get_match_list_gridpanel_top_toolbar(),
				layout: {
					type: 'hbox',
//					type: 'vbox',
					align: 'stretch'
				},
				defaults: {
					border:0
				},
				items: [
					{
						border: false,
						flex: 1,
						layout: {
							type: 'vbox',
							align: 'stretch'
						},
						items: [
							main_render_panel_config,
							{
								layout: {
									type: 'hbox',
									align: 'stretch'
								},
								defaults: {
									border: 1,
									flex: 1,
									maxHeight: 200,
									hidden: true
								},
								items: [
									category_tag_panel_config,
									segment_tag_panel_config,
									ad_hoc_tag_config
								]
							}
						]
					}
				]
			},
			pallet_gridpanel_config,
			{
				itemId: 'east-tabpanel',
				region: 'west',
//				width: center_width/5*2,
				width: center_width/2,
				minWidth: center_width/5*2,
				split: true,
				xtype: 'tabpanel',
				activeTab: 0,
				deferredRender: false,
				items:[
					segment_panel_config,
					system_panel_config,
					keyword_search_panel_config,
					search_neighbor_panel_config,
					match_list_gridpanel_config,
				]
			}
			],
			listeners: {
				afterrender: function(panel){
				},
				beforeshow: function(panel){
				},
				resize: function(comp,adjWidth,adjHeight,rawWidth,rawHeight){
				}
			}
		})];

		var viewport = Ext.create('Ext.container.Viewport', {
			id: 'main-viewport',
			itemId: 'main-viewport',
			layout: 'fit',
			items: viewport_items,
			listeners: {
				afterrender: function(viewport){
					var show_segment_render_window = function(){
						var main_render_panel = viewport.down('panel#main-render-panel');
						if(main_render_panel){
							var size = main_render_panel.body.getSize();
							var window_width = 150;
							var window_height = 360;
							var segment_render_window= Ext.create('Ext.window.Window', {
								itemId: 'segment-render-window',
								border: false,
								bodyBorder: false,
								width: window_width,
								height: window_height,
								maxWidth: window_width,
								maxHeight: window_height,
								x: size.width-window_width,
								y: size.height-window_height,
								constrain: true,
								closable: false,
								draggable: false,
								header: false,
								resizable: false,
								layout: 'fit',
								items: segment_render_panel_config
							});
							main_render_panel.add(segment_render_window);
							segment_render_window.show();
							main_render_panel.on({
								resize: function(main_render_panel){

									var segment_render_window= main_render_panel.down('window#segment-render-window');
									if(segment_render_window){
										var size = main_render_panel.body.getSize();
										var h = window_height;
										var y = size.height-h;
										if(y<0){
											h = size.height;
											y = 0;
										}
										segment_render_window.setHeight(h);
										segment_render_window.setPosition(size.width-window_width, size.height-window_height);
									}

								}
							});
						}
					};

					viewport.__loadMask = new Ext.LoadMask({
						target: viewport,
						msg: "Please wait...",
						listeners: {
							afterrender: function(loadmask){
								loadmask.on({
									hide: function(loadmask,eOpts){
										show_segment_render_window();
									},
									single: true
								});
							},
							hide: function(){
								var segment_render_window= viewport.down('window#segment-render-window');
								if(segment_render_window){
									segment_render_window.show();
								}

								var hash = window.decodeURIComponent(window.location.hash).substring(1);
								if(Ext.isString(hash) && hash.length){
									try{
										var o = Ext.JSON.decode(hash);
										console.log(o);
										if(Ext.isObject(o) && Ext.isArray(o['Part']) && o['Part'].length){

//mapurl解析
		var url_hash = self.getExtraParams() || {};
										}
									}catch(e){}
								}

							},
							show: function(){
								var segment_render_window= viewport.down('window#segment-render-window');
								if(segment_render_window){
									segment_render_window.hide();
								}
							}
						}
					});
					viewport.__loadMask.show();

				},
				beforedestroy: function(viewport){
				},
				destroy: function(viewport){
				},
				render: function(viewport){
				},
				resize: function(viewport,adjWidth,adjHeight,rawWidth,rawHeight){
				}
			}
		});
	},

	getViewport : function(){
		return Ext.getCmp('main-viewport');
	},

	initComponent : function(){
		var self = this;
		self._createViewport();
	},

	getBufferedRenderer : function(args){
		var self = this;
		args = Ext.apply({},args||{},{
			pluginId: 'bufferedrenderer',
			trailingBufferZone: 1,
			leadingBufferZone: 1,
			variableRowHeight: true
		});
		return Ext.create('Ext.grid.plugin.BufferedRenderer', args);
	},

	refreshView : function(view){
//		console.log('refreshView()', view.ownerCt.getItemId());
		if(view.isVisible()){
			if(view.getStore().getCount()){
				view.saveScrollState();
				view.refresh();
				view.restoreScrollState();
			}else{
				view.refresh();
			}
		}
	},

	_getObjDataFromRecord : function(record,selModel,is_selected){
		var self = this;

		var hash = record.getData();

		hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = null;
		if(selModel){
			if(selModel.isSelected(record)){

				if(self.USE_SELECTION_RENDERER_PICKED_COLOR){
					hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = self.DEF_SELECTION_RENDERER_PICKED_COLOR;
				}
				if(self.USE_SELECTION_RENDERER_PICKED_COLOR_FACTOR){

					var rgb = d3.rgb( hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] );
					var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
					var k = grayscale>127.5 ? true : false;

					if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR>0){
						var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR;
						if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
						hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.brighter(factor).toString();
					}
					else if(self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR<0){
						var factor = self.DEF_SELECTION_RENDERER_PICKED_COLOR_FACTOR * -1;
						if(!self.USE_SELECTION_RENDERER_PICKED_COLOR) factor += k ? 0 : 0.1;
						hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.darker(factor).toString();
					}

				}
				hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = true;
			}
			else if(Ext.isBoolean(is_selected) && is_selected){
				if(hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID]>=1.0) hash[Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID] = false;

				if(self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY || self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR){
					var rgb = d3.rgb( hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] );
					var grayscale = rgb.r * 0.3 + rgb.g * 0.59 + rgb.b * 0.11;
					var k = grayscale>127.5 ? true : false;

					if(self.USE_SELECTION_RENDERER_PICKED_OTHER_OPACITY){

						hash[Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID] = self.DEF_SELECTION_RENDERER_PICKED_OTHER_OPACITY;
					}

					if(self.USE_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR){

						if(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR>0){
							hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.brighter(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR).toString();
						}
						else if(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR<0){
							hash[Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID] = rgb.darker(self.DEF_SELECTION_RENDERER_PICKED_OTHER_COLOR_FACTOR*-1).toString();
						}
					}
				}
			}
		}
		return hash;
	},

	getObjDataFromRecords : function(records,selModel,is_selected){
		var self = this;
		return records.map(Ext.bind(self._getObjDataFromRecord,self,[selModel,is_selected],1));
	},

	_clickWordTag: function(value,dataIndex){
		var self = this;
		if(Ext.isEmpty(value)) value = '';
		if(Ext.isEmpty(dataIndex)) dataIndex = Ag.Def.NAME_DATA_FIELD_ID;
		var viewport = self.getViewport();

		var window_panel         = viewport.down('panel#window-panel');

		var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
		var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
		var match_list_store     = match_list_gridpanel.getStore();
		var match_list_gridview  = match_list_gridpanel.getView();
		var match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
		var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
		var pallet_selmodel      = pallet_gridpanel.getSelectionModel();
		var pallet_store         = pallet_gridpanel.getStore();
		var pallet_plugin        = pallet_gridpanel.getPlugin(pallet_gridpanel.getItemId()+'-plugin');

		var ad_hoc_tag_panel = window_panel.down('panel#ad-hoc-tag-panel');
		var $bodydiv         = $(ad_hoc_tag_panel.body.dom).find('div.ad-hoc-tag-body');
		var $this            = $bodydiv.find('div.ad-hoc-tag');
//		var $ad_hoc_label    = $this.find('label.ad-hoc-tag-label[data-value="'+value+'"][data-dataIndex="'+dataIndex+'"]');
		var $ad_hoc_label    = $this.find('label.ad-hoc-tag-label[data-value="'+value+'"][data-dataIndex]');

		var baseClass = 'ad-hoc-tag';
		var selectedClass = baseClass+'-selected';
		var labelClass = baseClass+'-label';
//		var baseSelector = 'div.'+baseClass;
		var baseSelector = 'div.'+baseClass;
		var selectedSelector = 'div.'+selectedClass;
		var labelNode = 'label';
		var labelSelector = labelNode+'.'+labelClass;

		var categorySelectedClass = 'category-tag-selected';
		var categorySelectedSelector = 'div.'+categorySelectedClass;

		var segmentSelectedClass = 'segment-tag-selected';
		var segmentSelectedSelector = 'div.'+segmentSelectedClass;

		var selectedStyle = {'box-shadow':'0px 0px 0px 3px '+self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR};
		var unselectedStyle = {'box-shadow':''};

		pallet_store.suspendEvents(false);
		match_list_store.suspendEvents(false);
		try{

			$(categorySelectedSelector).each(function(){
				var data = $(this).data('data');
				if(Ext.isObject(data)){
					var records = self._findRecords(pallet_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
					Ext.Array.each(records, function(record){
						self._clearPickedInfoRecord(record,true);
					});
					records = self._findRecords(match_list_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
					Ext.Array.each(records, function(record){
						self._clearPickedInfoRecord(record,true);
					});
				}
			}).removeClass(categorySelectedClass).css(unselectedStyle);

			$(segmentSelectedSelector).each(function(){
				var data = $(this).data('data');
				if(Ext.isObject(data)){
					var records = self._findRecords(pallet_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
					Ext.Array.each(records, function(record){
						self._clearPickedInfoRecord(record,true);
					});
					records = self._findRecords(match_list_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
					Ext.Array.each(records, function(record){
						self._clearPickedInfoRecord(record,true);
					});
				}
			}).removeClass(segmentSelectedClass).css(unselectedStyle);

			$(selectedSelector).removeClass(selectedClass).css(unselectedStyle);

			var pallet_store_records = self._findRecords(pallet_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
			var match_list_store_records = self._findRecords(match_list_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
			Ext.Array.each(pallet_store_records, function(record){
				self._clearPickedInfoRecord(record,true);
			});
			Ext.Array.each(match_list_store_records, function(record){
				self._clearPickedInfoRecord(record,true);
			});

			match_list_selmodel.deselectAll();
			pallet_selmodel.deselectAll();

//			$this.remove();
			if($this.length==0){
				$this = $('<div>')
				.addClass(baseClass)
				.appendTo($bodydiv)
				.click(function(e){
					pallet_store.suspendEvents(false);
					match_list_store.suspendEvents(false);
					try{
						$(baseSelector).remove();
						var pallet_store_records = self._findRecords(pallet_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
						var match_list_store_records = self._findRecords(match_list_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
						Ext.Array.each(pallet_store_records, function(record){
							self._clearPickedInfoRecord(record,true);
						});
						Ext.Array.each(match_list_store_records, function(record){
							self._clearPickedInfoRecord(record,true);
						});
					}catch(e){
						console.error(e);
					}

					match_list_store.resumeEvents();
					pallet_store.resumeEvents();

					self.refreshView(match_list_gridpanel.getView());
					self.refreshView(pallet_gridpanel.getView());

					window_panel._update_render.cancel();
					window_panel._update_render.delay(0,null,null,[true]);

					setTimeout(function(){
						console.log($bodydiv.outerHeight(true)+4);
						ad_hoc_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
					},250);
					ad_hoc_tag_panel.show();
					ad_hoc_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
					ad_hoc_tag_panel.setLoading(false);
				})
				;
			}

			$this
			.addClass(selectedClass)
			.css(selectedStyle);

			if($ad_hoc_label.length==0){
				if(value.length){
					$this.find(labelSelector).remove();
					$ad_hoc_label = $('<'+labelNode+'>')
					.addClass(labelClass)
					.attr({'data-value':value,'data-dataIndex':dataIndex})
					.text(value)
					.appendTo($this)
					;
				}
			}
			else{
				$ad_hoc_label.remove();
			}
			if($this.find(labelSelector).length==0){
				$this.remove();
			}
			else{
				var values = $this.find(labelSelector).map(function(){ return $(this).attr('data-value'); }).toArray();
				var all_value = values.join(' ');
				$this.attr({'data-value':all_value});

				var find_records = {};
				var selected_records = [];
//				var pallet_store_records = self._findWordRecords(pallet_store,Ag.Def.NAME_DATA_FIELD_ID,values);
//				var match_list_store_records = self._findWordRecords(match_list_store,Ag.Def.NAME_DATA_FIELD_ID,values);

				var fn = function(store,fieldName,value,re_value_arr,record){
					var fieldNames = [];
					if(Ext.isEmpty(fieldName)){
						fieldNames = Ext.Object.getKeys(record.getData());
					}
					else if(Ext.isString(fieldName)){
						fieldNames.push(fieldNames);
					}
					var match_fields = [];
					var match_values = [];
					Ext.Array.each(fieldNames, function(fieldName){
						var fieldValue = record.get(fieldName);
						if(Ext.isArray(fieldValue) && (fieldName==='is_a' || fieldName==='part_of' || fieldName==='lexicalsuper')){
							Ext.Array.each(fieldValue, function(field_value,index){
								Ext.Array.each(re_value_arr, function(re_value,index){
									if(re_value.test(field_value[Ag.Def.NAME_DATA_FIELD_ID])){
										match_fields.push(fieldName);
										match_values.push(value[index]);
									}
								});
							});
						}
						else{
							Ext.Array.each(re_value_arr, function(re_value,index){
								if(re_value.test(fieldValue)){
									match_fields.push(fieldName);
									match_values.push(value[index]);
								}
							});
						}
					});
					if(match_values.length>0){
						record.beginEdit();
//						record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,match_values);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,{dataIndex:match_fields,value:match_values});
						record.commit(true,[
							Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID
						]);
					}
				};

//				find_records[pallet_store.storeId] = self._findWordRecords(pallet_store, Ag.Def.NAME_DATA_FIELD_ID, values, self,{callback: fn});
//				find_records[match_list_store.storeId] = self._findWordRecords(match_list_store, Ag.Def.NAME_DATA_FIELD_ID, values, self,{callback: fn});
//				find_records[pallet_store.storeId] = self._findWordRecords(pallet_store, dataIndex, values, self,{callback: fn});
//				find_records[match_list_store.storeId] = self._findWordRecords(match_list_store, dataIndex, values, self,{callback: fn});
				find_records[pallet_store.storeId] = self._findWordRecords(pallet_store, null, values, self,{callback: fn});
				find_records[match_list_store.storeId] = self._findWordRecords(match_list_store, null, values, self,{callback: fn});

//				console.log('values',values);
//				console.log('pallet_store_records',pallet_store_records);
//				console.log('match_list_store_records',match_list_store_records);
//				console.log('find_records',find_records);
//				Ext.Array.each([pallet_store_records,match_list_store_records], function(records){
				Ext.Object.each(find_records, function(storeId,records){
					Ext.Array.each(records, function(record){
						var word_tag_data= record.get(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID) || [];
						var selected = false;
						if(Ext.isArray(word_tag_data)){
							selected = word_tag_data.length===values.length;
						}
						else if(Ext.isObject(word_tag_data)){
							selected = word_tag_data.value.length===values.length;
						}

						record.beginEdit();
						record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,selected);
						record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
//							record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_pallet_value);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
						record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,selected);
//							record.set(Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,values);
						record.commit(true,[
							Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
//								Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
							Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
//								Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID
						]);

						if(storeId==pallet_store.storeId && selected) selected_records.push(record);
					});
				});

				if(selected_records.length){
					pallet_gridpanel.suspendEvent('beforedeselect');
					pallet_gridpanel.suspendEvent('beforeselect');
					try{
						pallet_selmodel.select(selected_records);
					}catch(e){
						console.error(e)
					}
					pallet_gridpanel.resumeEvent('beforedeselect');
					pallet_gridpanel.resumeEvent('beforeselect');
				}

			}
		}catch(e){
			console.error(e);
		}

		match_list_store.resumeEvents();
		pallet_store.resumeEvents();

		self.refreshView(match_list_gridpanel.getView());
		self.refreshView(pallet_gridpanel.getView());

		window_panel._update_render.cancel();
		window_panel._update_render.delay(0,null,null,[true]);

		setTimeout(function(){
//			console.log($bodydiv.outerHeight(true)+4);
			ad_hoc_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
		},250);
		ad_hoc_tag_panel.show();
		ad_hoc_tag_panel.setHeight($bodydiv.outerHeight(true)+4);
		ad_hoc_tag_panel.setLoading(false);
	},

	_clickSegmentTag: function(value,e){
		var self = this;
		var viewport = self.getViewport();

		var window_panel         = viewport.down('panel#window-panel');

		var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
		var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
		var match_list_store     = match_list_gridpanel.getStore();
		var match_list_gridview  = match_list_gridpanel.getView();
		var match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
		var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
		var pallet_selmodel      = pallet_gridpanel.getSelectionModel();
		var pallet_store         = pallet_gridpanel.getStore();
		var pallet_plugin        = pallet_gridpanel.getPlugin(pallet_gridpanel.getItemId()+'-plugin');
//		var selectKeepExisting   = match_list_selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
		var selectKeepExisting   = true;

		var segment_tag_panel   = window_panel.down('panel#segment-tag-panel');
		var $this = $(segment_tag_panel.body.dom).find('div.segment-tag[data-value="'+value+'"]');
//		var $this = $(tag_htmlelement);


//					var system_list_store = Ext.data.StoreManager.lookup('system-list-store');
		var segment_store = Ext.data.StoreManager.lookup('segment-list-store');
		var ad_hoc_tag_panel = window_panel.down('panel#ad-hoc-tag-panel');

		var baseClass = 'segment-tag';
		var selectedClass = baseClass+'-selected';
		var baseSelector = 'div.'+baseClass;
		var selectedSelector = 'div.'+selectedClass;

		var categorySelectedClass = 'category-tag-selected';
		var categorySelectedSelector = 'div.'+categorySelectedClass;

		var adhocClass = 'ad-hoc-tag';
		var adhocSelectedClass = adhocClass+'-selected';
		var adhocSelector = 'div.'+adhocClass;
		var adhocSelectedSelector = 'div.'+adhocSelectedClass;

		var selectedStyle = {'box-shadow':'0px 0px 0px 3px '+self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR};
		var unselectedStyle = {'box-shadow':''};

		match_list_selmodel.deselectAll();
		pallet_selmodel.deselectAll();

								pallet_store.suspendEvents(false);
								match_list_store.suspendEvents(false);
								try{
									var data = $this.data('data');
									var $segment_tag_div = $this.closest(baseSelector);

									var hasClass = $segment_tag_div.hasClass(selectedClass);

									$(selectedSelector).each(function(){
										var data = $(this).data('data');
//										if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
										if(Ext.isObject(data)){
											var records = self._findRecords(pallet_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												self._clearPickedInfoRecord(record,true);
											});
											records = self._findRecords(match_list_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												self._clearPickedInfoRecord(record,true);
											});
										}
									}).removeClass(selectedClass).css(unselectedStyle);

									if(hasClass){

									}
									else{

										$(categorySelectedSelector).each(function(){
											var data = $(this).data('data');
//										if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
											if(Ext.isObject(data)){
												var records = self._findRecords(pallet_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
												Ext.Array.each(records, function(record){
													self._clearPickedInfoRecord(record,true);
												});
												records = self._findRecords(match_list_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
												Ext.Array.each(records, function(record){
													self._clearPickedInfoRecord(record,true);
												});
											}
										}).removeClass(categorySelectedClass).css(unselectedStyle);

//										$(adhocSelectedSelector).removeClass(selectedClass).css(unselectedStyle);
										$(adhocSelector).remove();
										var pallet_store_records = self._findRecords(pallet_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
										var match_list_store_records = self._findRecords(match_list_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
										Ext.Array.each(pallet_store_records, function(record){
											self._clearPickedInfoRecord(record,true);
										});
										Ext.Array.each(match_list_store_records, function(record){
											self._clearPickedInfoRecord(record,true);
										});


										var max_pallet_value = pallet_store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;
										var max_match_list_value = match_list_store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;

										$segment_tag_div.addClass(selectedClass).css(selectedStyle);
//										if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
										if(Ext.isObject(data)){
											var records = self._findRecords(pallet_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												max_pallet_value++;
												record.beginEdit();
												record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_pallet_value);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID, {dataIndex:Ag.Def.SEGMENT_DATA_FIELD_ID, value: [data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]]});
												record.commit(true,[
													Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID
												]);
											});

											records = self._findRecords(match_list_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												max_match_list_value++;
												record.beginEdit();
												record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_match_list_value);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID, {dataIndex:Ag.Def.SEGMENT_DATA_FIELD_ID, value: [data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]]});
												record.commit(true,[
													Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID
												]);
											});
										}
									}
								}catch(e){
									console.error(e);
								}

								match_list_store.resumeEvents();
								pallet_store.resumeEvents();

								self.refreshView(match_list_gridpanel.getView());
								self.refreshView(pallet_gridpanel.getView());

								window_panel._update_render.cancel();
								window_panel._update_render.delay(0,null,null,[true]);
	},

	_clickCategoryTag: function(value,e){
		var self = this;
//		var $this = $(tag_htmlelement);
		var viewport = self.getViewport();

		var window_panel         = viewport.down('panel#window-panel');

		var match_list_gridpanel = window_panel.down('gridpanel#match-list-gridpanel');
		var match_list_selmodel  = match_list_gridpanel.getSelectionModel();
		var match_list_store     = match_list_gridpanel.getStore();
		var match_list_gridview  = match_list_gridpanel.getView();
		var match_list_plugin    = match_list_gridpanel.getPlugin(match_list_gridpanel.getItemId()+'-plugin');
		var pallet_gridpanel     = window_panel.down('gridpanel#pallet-gridpanel');
		var pallet_selmodel      = pallet_gridpanel.getSelectionModel();
		var pallet_store         = pallet_gridpanel.getStore();
		var pallet_plugin        = pallet_gridpanel.getPlugin(pallet_gridpanel.getItemId()+'-plugin');
//		var selectKeepExisting   = match_list_selmodel.getSelectionMode()==='SIMPLE' ? true : e.ctrlKey;
		var selectKeepExisting   = true;

		var category_tag_panel   = window_panel.down('panel#category-tag-panel');
		var $this = $(category_tag_panel.body.dom).find('div.category-tag[data-value="'+value.toLowerCase()+'"]');


		var system_list_store = Ext.data.StoreManager.lookup('system-list-store');

		var baseClass = 'category-tag';
		var selectedClass = baseClass+'-selected';
		var baseSelector = 'div.'+baseClass;
		var selectedSelector = 'div.'+selectedClass;

		var segmentSelectedClass = 'segment-tag-selected';
		var segmentSelectedSelector = 'div.'+segmentSelectedClass;

		var adhocClass = 'ad-hoc-tag';
		var adhocSelectedClass = adhocClass+'-selected';
		var adhocSelector = 'div.'+adhocClass;
		var adhocSelectedSelector = 'div.'+adhocSelectedClass;

		var selectedStyle = {'box-shadow':'0px 0px 0px 3px '+self.DEF_SELECTION_RENDERER_PICKED_SECOND_COLOR};
		var unselectedStyle = {'box-shadow':''};

		match_list_selmodel.deselectAll();
		pallet_selmodel.deselectAll();

								pallet_store.suspendEvents(false);
								match_list_store.suspendEvents(false);
								try{
									var data = $this.data('data');
									var $category_tag_div = $this.closest(baseSelector);


									var hasClass = $category_tag_div.hasClass(selectedClass);

									$(selectedSelector).each(function(){
										var data = $(this).data('data');
//										if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
										if(Ext.isObject(data)){
											var records = self._findRecords(pallet_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												self._clearPickedInfoRecord(record,true);
											});
											records = self._findRecords(match_list_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												self._clearPickedInfoRecord(record,true);
											});
										}
									}).removeClass(selectedClass).css(unselectedStyle);


									if(hasClass){

									}
									else{


										$(segmentSelectedSelector).each(function(){
											var data = $(this).data('data');
//											if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
											if(Ext.isObject(data)){
												var records = self._findRecords(pallet_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
												Ext.Array.each(records, function(record){
													self._clearPickedInfoRecord(record,true);
												});
												records = self._findRecords(match_list_store,Ag.Def.SEGMENT_DATA_FIELD_ID,data[ Ag.Def.SEGMENT_DATA_FIELD_ID ]);
												Ext.Array.each(records, function(record){
													self._clearPickedInfoRecord(record,true);
												});
											}
										}).removeClass(segmentSelectedClass).css(unselectedStyle);

//										$(adhocSelectedSelector).removeClass(selectedClass).css(unselectedStyle);
										$(adhocSelector).remove();
										var pallet_store_records = self._findRecords(pallet_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
										var match_list_store_records = self._findRecords(match_list_store,Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
										Ext.Array.each(pallet_store_records, function(record){
											self._clearPickedInfoRecord(record,true);
										});
										Ext.Array.each(match_list_store_records, function(record){
											self._clearPickedInfoRecord(record,true);
										});

										var max_pallet_value = pallet_store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;
										var max_match_list_value = match_list_store.max(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID) || 0;

										$category_tag_div.addClass(selectedClass).css(selectedStyle);
//										if(Ext.isObject(data) && Ext.isArray(data.element) && data.element.length){
										if(Ext.isObject(data)){
											var records = self._findRecords(pallet_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												max_pallet_value++;
												record.beginEdit();
												record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_pallet_value);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,true);
												record.commit(true,[
													Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID
												]);
											});

											records = self._findRecords(match_list_store,Ag.Def.SYSTEM_ID_DATA_FIELD_ID,data[ Ag.Def.SYSTEM_ID_DATA_FIELD_ID ]);
											Ext.Array.each(records, function(record){
												max_match_list_value++;
												record.beginEdit();
												record.set(Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID, Ag.Def.CONCEPT_DATA_PICKED_TYPE_TAGS);
												record.set(Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID, max_match_list_value);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,false);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,true);
												record.set(Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,true);
												record.commit(true,[
													Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
													Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID
												]);
											});
										}
									}
								}catch(e){
									console.error(e);
								}

								match_list_store.resumeEvents();
								pallet_store.resumeEvents();

								self.refreshView(match_list_gridpanel.getView());
								self.refreshView(pallet_gridpanel.getView());

								window_panel._update_render.cancel();
								window_panel._update_render.delay(0,null,null,[true]);

	},

	_download: function(records){
		var self = this;

		if(Ext.isArray(records) && records.length){
			var url_hash = self.getExtraParams() || {};
			url_hash[Ag.Def.LOCATION_HASH_IDS_KEY] = Ext.JSON.encode(Ext.Array.map(records, function(record){ return record.get(Ag.Def.ID_DATA_FIELD_ID); }));

			if($('iframe#_download_iframe').length==0){
				$('<iframe>')
				.attr({
					'name': '_download_iframe',
					'id'  : '_download_iframe'
				})
				.css({'display':'none'})
				.appendTo($(document.body))
				;
			}

			var $form = $('form#_download_form');
			if($form.length==0){
				$form = $('<form>')
				.attr({
					'action': 'download.cgi',
					'method': 'POST',
					'target': '_download_iframe',
					'id'    : '_download_form'
				})
				.css({'display':'none'})
				.appendTo($(document.body))
				;
			}
			Ext.Object.each(url_hash, function(key,val){
				var $input = $('input[type=hidden][name='+key+']');
				if($input.length==0){
					$input = $('<input>')
					.attr({
						'type': 'hidden',
						'name': key
					})
					.appendTo($form)
					;
				}
				$input.val(val);
			});
			$form.get(0).submit();
		}
	}

});
//2 out of 10 items are selected.
