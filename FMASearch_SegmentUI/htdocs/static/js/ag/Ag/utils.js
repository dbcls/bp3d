//var Ag = Ag || {};
Ext.define('Ag.Utils', {
	singleton: true,
	constructor: function (config) {
		var self = this;
		self.__config = config || {};
	},
	makeCopyListText : function(copy_type,grid,records){
		try{
			var copy_type_obj;
			if(copy_type=='csv'){
				copy_type_obj = Ag.Utils.CSVData;
			}else if(copy_type=='tab'){
				copy_type_obj = Ag.Utils.TabData;
			}

			var copyText = "";
			if(copy_type_obj){
				var column = [];

				if(grid instanceof Ext.grid.GridPanel){
					var dataIndex;
					var data;
					var columnModel = grid.columns;
					var columnCount = columnModel.length;
					for(var colIndex=0;colIndex<columnCount;colIndex++){
						if(columnModel[colIndex].isHidden()) continue;
						dataIndex = columnModel[colIndex].dataIndex;
						if(dataIndex=='selected' || dataIndex=='rep_density') continue;
						column.push(copy_type_obj.escape(columnModel[colIndex].text));
					}
					copyText = column.join(copy_type_obj.colDelimiter)+"\n";

					for(var i=0;i<records.length;i++){
						column = [];
						for(var colIndex=0;colIndex<columnCount;colIndex++){
							if(columnModel[colIndex].isHidden()) continue;
							dataIndex = columnModel[colIndex].dataIndex;
							if(dataIndex=='selected' || dataIndex=='rep_density') continue;
							if(records[i].data){
								data = records[i].data[dataIndex];
							}else{
								data = records[i][dataIndex];
							}
							try{
								if(Ext.isFunction(columnModel[colIndex].renderer)) data = columnModel[colIndex].renderer(data,{},records[i],i,colIndex,records[i].store);
							}catch(e){
								console.log(dataIndex,data);
								console.error(e);
							}

							column.push(copy_type_obj.escape(data));
						}
						copyText += column.join(copy_type_obj.colDelimiter)+"\n";
					}
				}else if(grid instanceof Ext.tree.Panel){
					for(var i=0;i<records.length;i++){
						column = [];
						Ext.each(['rep_id','cdi_name','cdi_name_e'],function(dataIndex){
							if(records[i].data){
								data = records[i].data[dataIndex];
							}else{
								data = records[i][dataIndex];
							}
							column.push(copy_type_obj.escape(data));
						});
						copyText += column.join(copy_type_obj.colDelimiter)+"\n";
					}
				}
			}
			return copyText;
		}catch(e){
			console.error(e);
		}
	},

	copyListGrid : null,
	copyListRecords : null,
	copyListWindow : null,
	copyListTextareafield : null,
	copyListCB : function(grid,records,title){
		var self = this;
		self.copyListGrid = grid;
		self.copyListRecords = records;
		if(!self.copyListWindow){
			if(!title) title = 'Copy';
			self.copyListWindow = Ext.create('Ext.window.Window', {
				title       : title,
				width       : 600,
				height      : 300,
				layout      : 'form',
//				plain       : true,
				bodyStyle   : 'padding:5px;text-align:right;',
				buttonAlign : 'center',
				modal       : true,
				resizable   : true,
				closeAction : 'hide',
				layout      : 'anchor',
				items       : [{
					xtype      : 'radiogroup',
					fieldLabel : 'Copy Type',
					labelWidth  : 68,
					columns    : 2,
					height     : 22,
					anchor     : '100%',
					defaults   : {
						name:'copy-list-type'
					},
					items      : [{
						boxLabel   : 'Tab-Separated Values',
						inputValue : 'tab',
						checked    : true
					},{
						boxLabel   : 'Comma-Separated Values',
						inputValue : 'csv'
					}],
					listeners  : {
						change : function(field,newValue,oldValue,eOpts){
							self.copyListTextareafield.setValue(self.makeCopyListText(newValue['copy-list-type'],self.copyListGrid,self.copyListRecords));
							self._dump(newValue);
						}
					}
				},{
					xtype         : 'textareafield',
					hideLabel     : true,
					anchor        : '100% -25',
					selectOnFocus : true,
					disabled      : false,
					value         : "",
					listeners  : {
						specialkey : function(f, e){
							e.stopPropagation();
						}
					}
				}],
				buttons : [{
					text    : 'OK',
					handler : function(){
						self.copyListWindow.hide();
					}
				}],
				listeners : {
					beforeshow : function(win,eOpts){
						try{
							var textareafield;
							var radiofield;
							var num1 = win.items.getCount();
							for(var i=0;i<num1;i++){
								var item1 = win.items.getAt(i);
								if(item1.getXType()=='radiogroup'){
									var num2 = item1.items.getCount();
									for(var j=0;j<num2;j++){
										var item2 = item1.items.getAt(j);
										if(item2.getXType()=='radiofield'){
											if(item2.getValue()){
												self._dump("item2.getValue()=["+item2.getValue()+"]");
												self._dump("item2.getRawValue()=["+item2.getRawValue()+"]");
												radiofield = item2;
												break;
											}
										}
									}
								}else if(item1.getXType()=='textareafield' || item1.getXType()=='textarea'){
									textareafield = item1;
								}
							}
							if(radiofield && textareafield){
								textareafield.setValue(self.makeCopyListText(radiofield.inputValue,self.copyListGrid,self.copyListRecords));
								self.copyListTextareafield = textareafield;
							}
						}catch(e){
							self._dump(e);
						}
					}
				}
			});
		}
		setTimeout(function(){
			try{
				self.copyListWindow.show();
			}catch(e){
				self._dump(e);
			}
		},250);
	},

	_dump : function(aStr){
//		if(window.dump) window.dump("AgUtils.js:"+aStr+"\n");
//		try{if(console && console.log) console.log("AgUtils.js:"+aStr);}catch(e){}
	}

});

Ext.define('Ag.Utils.TabData', {
	singleton: true,
	constructor: function (config) {
		var self = this;
		self.__config = config || {};
	},
	colDelimiter : '\t',
	parse : function(data){
		var self = this;
		data = data.trim();
		var rows = data.split("\n");
		if(rows.length>=1) rows[0] = rows[0].replace(/^#+/g,"").split(self.colDelimiter);
		var i;
		for(i=1;i<rows.length;i++){
			rows[i] = rows[i].split("\t");
			rows[i][rows[i].length-1] = rows[i][rows[i].length-1].replace(/\s\$/g,"")
		}
		return rows;
	},
	escape : function(value){
		return value;
	}
});

Ext.define('Ag.Utils.CSVData', {
	singleton: true,
	constructor: function (config) {
		var self = this;
		self.__config = config || {};
	},
	colDelimiter : ',',
	parse : function(data){
		var self = this;
		var rows = new Array();
		var cols = new Array();
		var quated = false;
		var colStartIndex = 0;
		var quateCount = 0;
		var i;
		for(i=0;i<data.length;i++){
			var c = data.charAt(i);
			if(c == '"'){
				quateCount++;
				if(!quated){
					quated = true;
				}else{
					if(quateCount % 2 == 0 ){
						if(i == data.length - 1 || data.charAt(i + 1) != '"'){
							quated = false;
						}
					}
				}
			}
			if(quated) continue;
			if(c == self.colDelimiter){
				var value = data.substring(colStartIndex, i);
				value = self.unescape(value);
				cols.push(value);
				colStartIndex = i + 1;
			}else if(c == "\r"){
				var value = data.substring(colStartIndex, i);
				value = self.unescape(value);
				cols.push(value);
				i += 1;
				colStartIndex = i + 1;
				rows.push(cols);
				cols = new Array();
			}else if(c == "\n"){
				var value = data.substring(colStartIndex, i);
				value = self.unescape(value);
				cols.push(value);
				colStartIndex = i + 1;
				rows.push(cols);
				cols = new Array();
			}
		}
		if(cols.length>0 && colStartIndex<i-1){
			var value = data.substring(colStartIndex).replace(/\s+\$/g,"");
			value = self.unescape(value);
			cols.push(value);
			rows.push(cols);
		}
		return rows;
	},
	escape : function(value){
		if(Ext.isEmpty(value)) return value;
		if(typeof value == "string"){
			value = value.replace(/"/g, '""');
			value = '"' + value + '"';
		}
		return value;
	},
	unescape : function(value){
		if(typeof value == "string"){
			if(value.charAt(0) == '"' && value.charAt(value.length-1) == '"') value = value.substring(1, value.length-1);
			value = value.replace(/""/g, '"');
		}
		return value;
	}
});
