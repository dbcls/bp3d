Ext.app.IncrementalSearchField = Ext.extend(Ext.form.ComboBox, {
	store : new Ext.data.JsonStore({
		url:'ag-incremental-search-term.cgi',
//		url:'ag-incremental-search-word.cgi',
		totalProperty : 'total',
		root: 'records',
		fields: [
			{name:'f_id',type:'string'},
			{name:'keyword',type:'string'},
			{name:'markup',type:'string'},
			{name:'src',type:'string'},
			{name:'parts_exists',type:'boolean'}
		],
		remoteSort: true,
		listeners: {
			'beforeload' : function(self,options){
				self.baseParams = self.baseParams || {};
				try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){return false;}
				self.baseParams.version = bp3d_version;
			},
			'load' : function(self,records,options){
			},
			scope:this
		}
	}),
	displayField:'keyword',
	typeAhead: false,
	loadingText: 'Searching...',
	width: 570,
	listWidth: 570,
	pageSize:10,
	minChars:0,
	triggerAction:'all',
	hideTrigger:true,
	selectOnFocus:true,
	tpl: new Ext.XTemplate(
		'<tpl for="."><div class="search-item" ',
			'<tpl if="parts_exists == true">style="height:30px"><img src="{src}" width="30" height="30" align="right"/></tpl>',
			'<tpl if="parts_exists == false">style="height:24px"><img src="icon/inprep_S.png" width="30" height="24" align="right"/></tpl>',
			'<h3>',
//			'<span>',
//			'<tpl if="parts_exists == true"><img src="css/bullet_picture.png" width="16" height="16"/></tpl>',
//			'<tpl if="parts_exists == false"><img src="css/bullet_delete.png" width="16" height="16"/></tpl>',
//			'</span>',
			'{markup}</h3>',
			'{f_id}',
		'</div></tpl>'
	),

	tpl_word: new Ext.XTemplate(
		'<tpl for="."><div class="search-item">',
			'<h3>{markup}</h3>',
		'</div></tpl>'
	),

	itemSelector: 'div.search-item',

	paramName : 'query',

	// private
	initComponent : function(){
		Ext.app.IncrementalSearchField.superclass.initComponent.call(this);
		this.on('specialkey', function(f, e){
			_dump("this.specialkey");
			if(e.getKey() == e.ENTER){
				this.specialkey=true;
				this.onTrigger2Click();
			}
		}, this);
		this.on('render', function(c){
			this.el.on('keyup', this.onElKeyUp, this);
		},this);
	},

	// private
	initList : function(){
		if(this.list) return;

		var cls = 'x-combo-list';

		this.list = new Ext.Layer({
			shadow: this.shadow, cls: [cls, this.listClass].join(' '), constrain:false
		});

		var lw = this.listWidth || Math.max(this.wrap.getWidth(), this.minListWidth);
		this.list.setWidth(lw);
		this.list.swallowEvent('mousewheel');
		this.assetHeight = 0;

		if(this.title){
			this.header = this.list.createChild({cls:cls+'-hd', html: this.title});
			this.assetHeight += this.header.getHeight();
		}

		this.innerList = this.list.createChild({cls:cls+'-inner'});
		this.innerList.on('mouseover', this.onViewOver, this);
		this.innerList.on('mousemove', this.onViewMove, this);
		this.innerList.setWidth(lw - this.list.getFrameWidth('lr'));

		if(this.pageSize){
			this.footer = this.list.createChild({cls:cls+'-ft'});
			this.pageTb = new Ext.PagingToolbar({
				store:this.store,
				pageSize: this.pageSize,
				renderTo:this.footer,
				items:['-','->','-',{
					xtype:'tbtext',
					text:'-'
				},{
					xtype:'tbtext',
					text:'Terms'
				}]
			});
			this.assetHeight += this.footer.getHeight();
		}

		if(!this.tpl){
			this.tpl = '<tpl for="."><div class="'+cls+'-item">{' + this.displayField + '}</div></tpl>';
		}

		this.view = new Ext.DataView({
			applyTo: this.innerList,
			tpl: this.tpl,
			singleSelect: true,
			selectedClass: this.selectedClass,
			itemSelector: this.itemSelector || '.' + cls + '-item'
		});

		this.view.on('click', this.onViewClick, this);

		this.bindStore(this.store, true);

		if(this.resizable){
			this.resizer = new Ext.Resizable(this.list,  {
				pinned:true,
				handles:'se'
			});
			this.resizer.on('resize', function(r, w, h){
				this.maxHeight = h-this.handleHeight-this.list.getFrameWidth('tb')-this.assetHeight;
				this.listWidth = w;
				this.innerList.setWidth(w - this.list.getFrameWidth('lr'));
				this.restrictHeight();
			}, this);
			this[this.pageSize?'footer':'innerList'].setStyle('margin-bottom', this.handleHeight+'px');
		}

	},

	// private
	initEvents : function(){
		Ext.form.ComboBox.superclass.initEvents.call(this);
		this.keyNav = new Ext.KeyNav(this.el, {
			"up" : function(e){
				this.inKeyMode = true;
				this.selectPrev();
			},
			"down" : function(e){
				if(!this.isExpanded()){
					this.onTriggerClick();
				}else{
					this.inKeyMode = true;
					this.selectNext();
				}
			},
			"enter" : function(e){
				if(!this.onViewClick()){
					this.collapse();
					this.el.focus();
					this.onFocus();
					this.fireEvent("specialkey", this, e);
					return;
				}
				this.specialkey=true;
				this.delayedCheck = true;
				this.unsetDelayCheck.defer(10, this);
			},
			"esc" : function(e){
				this.collapse();
			},
			"tab" : function(e){
				this.onViewClick(false);
				return true;
			},
			scope : this,
			doRelay : function(foo, bar, hname){
				if(hname == 'down' || this.scope.isExpanded()){
					return Ext.KeyNav.prototype.doRelay.apply(this, arguments);
				}
				return true;
			},
			forceKeyDown : true
		});
		this.queryDelay = Math.max(this.queryDelay || 10, this.mode == 'local' ? 10 : 250);
		this.dqTask = new Ext.util.DelayedTask(this.initQuery, this);
		if(this.typeAhead){
			this.taTask = new Ext.util.DelayedTask(this.onTypeAhead, this);
		}
		if(this.editable !== false){
			this.el.on("keyup", this.onKeyUp, this);
		}
		if(this.forceSelection){
			this.on('blur', this.doForce, this);
		}
	},

	// private
	onBeforeLoad : function(){
		if(this.pageTb){
			var items = this.pageTb.items;
			var item = items.get(items.getCount()-2);
			if(item) item.el.innerHTML = '-';
		}
		if(!this.hasFocus){
			return;
		}
		this.innerList.update(this.loadingText ? '<div class="loading-indicator">'+this.loadingText+'</div>' : '');
		this.restrictHeight();
		this.selectedIndex = -1;
	},

	// private
	onLoad : function(){
		if(this.pageTb){
			var items = this.pageTb.items;
			var item = items.get(items.getCount()-2);
			if(item) item.el.innerHTML = this.store.getTotalCount();
		}
		if(!this.hasFocus){
			return;
		}
		if(this.store.getCount() > 0){
			this.expand();
			this.restrictHeight();
			if(this.lastQuery == this.allQuery){
				if(this.editable){
					this.el.dom.select();
				}
				if(!this.selectByValue(this.value, true)){
					_dump("onLoad():4");
					this.select(0, true);
				}
			}else{
//				this.selectNext();
				this.view.clearSelections();
				this.selectedIndex = -1;

				if(this.typeAhead && this.lastKey != Ext.EventObject.BACKSPACE && this.lastKey != Ext.EventObject.DELETE){
					this.taTask.delay(this.typeAheadDelay);
				}
			}
		}else{
			this.onEmptyResults();
		}
//	this.el.focus();
	},

	// private
	onViewClick : function(doFocus){
		var rtn = false;
		var index = this.view.getSelectedIndexes()[0];
		var r = this.store.getAt(index);
		if(r){
			this.onSelect(r, index);
			rtn = true;
		}
		if(doFocus !== false){
			this.el.focus();
		}
		return rtn;
	},

	// private
	selectPrev : function(){
		var ct = this.store.getCount();
		if(ct > 0){
			if(this.selectedIndex <= 0){
				this.view.clearSelections();
				this.selectedIndex = -1;
			}else if(this.selectedIndex > 0){
				this.select(this.selectedIndex-1);
			}
		}
	},

	onSelect: function(record){
		this.setRawValue(record.data.keyword);
		this.collapse();
		this.el.focus();
		this.onFocus();
	},

	onElKeyUp : function(e,t,o){
		if(e.getKey() !== e.ENTER) return;
		_dump("onElKeyUp():"+this.specialkey);
		if(this.specialkey){
			this.specialkey = false;
			return;
		}
		this.onFocus();
		this.dqTask.delay(10);
	},

	onTrigger2Click : function(){
		try{
			var v = this.getRawValue();
			if(v.length < 1){
				return;
			}
			var urlOBj = Ext.urlDecode(_location.location.search.substr(1));
			urlOBj.node = 'search';
			urlOBj[this.paramName] = v;
			_location.location.search = Ext.urlEncode(urlOBj);
		}catch(e){
			_dump("Ext.app.IncrementalSearchField.onTrigger2Click():"+e);
		}
	}
});
