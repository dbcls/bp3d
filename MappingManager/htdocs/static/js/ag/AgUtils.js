var AgUtils = {
	TabData : {
		colDelimiter : '\t',
		parse : function(data){
			data = data.trim();
			var rows = data.split("\n");
			if(rows.length>=1) rows[0] = rows[0].replace(/^#+/g,"").split(AgUtils.TabData.colDelimiter);
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
	},

	CSVData : {
		colDelimiter : ',',
		parse : function(data){
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
				if(c == AgUtils.CSVData.colDelimiter){
					var value = data.substring(colStartIndex, i);
					value = AgUtils.CSVData.unescape(value);
					cols.push(value);
					colStartIndex = i + 1;
				}else if(c == "\r"){
					var value = data.substring(colStartIndex, i);
					value = AgUtils.CSVData.unescape(value);
					cols.push(value);
					i += 1;
					colStartIndex = i + 1;
					rows.push(cols);
					cols = new Array();
				}else if(c == "\n"){
					var value = data.substring(colStartIndex, i);
					value = AgUtils.CSVData.unescape(value);
					cols.push(value);
					colStartIndex = i + 1;
					rows.push(cols);
					cols = new Array();
				}
			}
			if(cols.length>0 && colStartIndex<i-1){
				var value = data.substring(colStartIndex).replace(/\s+\$/g,"");
				value = AgUtils.CSVData.unescape(value);
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
	},

	makeCopyListText : function(copy_type,grid,records){
		try{
			var copy_type_obj;
			if(copy_type=='csv'){
				copy_type_obj = AgUtils.CSVData;
			}else if(copy_type=='tab'){
				copy_type_obj = AgUtils.TabData;
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
						if(dataIndex=='selected' || dataIndex=='rep_density' || dataIndex=='current_use') continue;
						if(columnModel[colIndex].text=='&#160;') continue;
						column.push(copy_type_obj.escape(columnModel[colIndex].text));
					}
					copyText = column.join(copy_type_obj.colDelimiter)+"\n";

					for(var i=0;i<records.length;i++){
						column = [];
						for(var colIndex=0;colIndex<columnCount;colIndex++){
							if(columnModel[colIndex].isHidden()) continue;
							dataIndex = columnModel[colIndex].dataIndex;
							if(dataIndex=='selected' || dataIndex=='rep_density' || dataIndex=='current_use') continue;
							if(columnModel[colIndex].text=='&#160;') continue;
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
//			AgUtils._dump("makeCopyListText():"+e);
			console.error(e);
		}
	},

	copyListGrid : null,
	copyListRecords : null,
	copyListWindow : null,
	copyListTextareafield : null,
	copyListCB : function(grid,records,title){
		AgUtils.copyListGrid = grid;
//		AgUtils.copyListRecords = Ext.Array.clone(records);
		AgUtils.copyListRecords = records;
		if(!AgUtils.copyListWindow){
			if(!title) title = 'Copy';
			AgUtils.copyListWindow = Ext.create('Ext.window.Window', {
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
							AgUtils.copyListTextareafield.setValue(AgUtils.makeCopyListText(newValue['copy-list-type'],AgUtils.copyListGrid,AgUtils.copyListRecords));
							AgUtils._dump(newValue);
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
						AgUtils.copyListWindow.hide();
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
												AgUtils._dump("item2.getValue()=["+item2.getValue()+"]");
												AgUtils._dump("item2.getRawValue()=["+item2.getRawValue()+"]");
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
								textareafield.setValue(AgUtils.makeCopyListText(radiofield.inputValue,AgUtils.copyListGrid,AgUtils.copyListRecords));
								AgUtils.copyListTextareafield = textareafield;
							}
						}catch(e){
							AgUtils._dump(e);
						}
					}
				}
			});
		}
		setTimeout(function(){
			try{
				AgUtils.copyListWindow.show();
			}catch(e){
				AgUtils._dump(e);
			}
		},250);
	},

	_dump : function(aStr){
//		if(window.dump) window.dump("AgUtils.js:"+aStr+"\n");
//		try{if(console && console.log) console.log("AgUtils.js:"+aStr);}catch(e){}
	}

};