var AgRender = function(param){
	var self = this;
	self._iframe = null;
	self._hashRenderStr = null;
	self._src = 'AgRender.cgi';
	self._blank = false;
	self._name = 'ag-render';
	self._namespace = '';
	self._DEBUG = false;
	self._cancel_keybind = false;
	self._iframe_window = null;
	self._iframe_document = null;
	self._use_localstorage = true;

	param = param || {};
	if(param.namespace){
		self._namespace = '.'+param.namespace;
	}
	if(Ext.isBoolean(param.use_localstorage)){
		self._use_localstorage = param.use_localstorage;
	}
	self._DEF_HASH_KEY = AgDef.LOCALDB_PREFIX+(param.hash_key || 'ag-render-hash');

	self.AgLocalStorage = self._use_localstorage ? new AgLocalStorage() : null;

	self.createLocaleHashStrTask = new Ext.util.DelayedTask(function(o){
		if(self._DEBUG) console.log("AgRender.createLocaleHashStrTask()");
		var hashStr = self.getLocationHash();
		if(hashStr == self._hashRenderStr) return;
		try{
			if(self.AgLocalStorage) self.AgLocalStorage.save(self._DEF_HASH_KEY,self._hashRenderStr);
		}catch(e){
			console.error(e);
			console.log(self._hashRenderStr.length);
		}
		$(window).trigger('agrender_hashchange'+self._namespace,[self._hashRenderStr]);
	});

//	self.AgLocalStorage.remove(self._DEF_HASH_KEY);

//	self.init(param);
};

AgRender.prototype.open = function(param){
	var self = this;
	if(self._DEBUG) console.log("AgRender.open()");
	param = param || {};
	if(param.src){
		self._src = param.src;
	}
	if(param.name){
		self._name = param.name;
	}
	if(param.blank){
		self._blank = param.blank;
	}
	if(param.namespace){
		self._namespace = '.'+param.namespace;
	}
	if(param.iframe_window){
		self._iframe_window = param.iframe_window;
	}
	if(param.iframe_document){
		self._iframe_document = param.iframe_document;
	}
	if(param.dom){
		if(param.iframe){
			self._iframe = param.iframe;
		}else{
			if(self._blank){
				self._iframe = window.open(self._src,self._name,"width=800,height=600,alwaysRaised=yes,dependent=yes,menubar=no,resizable=yes,status=no,toolbar=no");
				$(window).bind('unload', function(e){
					if(self._iframe && !self._iframe.closed) self._iframe.close();
				});
			}else{
				self._iframe = $('<iframe id="'+self._name+'" name="'+self._name+'" width="100%" height="100%" frameborder=0 src="'+self._src+'">').appendTo($(param.dom)).get(0);
			}
		}

		var win = self.getWindow();
		if(win){
			var func = Ext.bind(self.iframe_load,self,[param.dom.ownerDocument.defaultView,{window:win}],1);
			Ext.EventManager.on(win,'load',func);
		}
/**/
		$(document).bind('keydown', function(e){
			if(self._cancel_keybind) return;
			if(self._DEBUG) console.log("onDocumentKeyDown");
			var win = self.getWindow();
			if(win) win.$(win.document).trigger('keydown',[e]);
		});
		$(document).bind('keyup',   function(e){
			if(self._cancel_keybind) return;
			if(self._DEBUG) console.log("onDocumentKeyUp");
			var win = self.getWindow();
			if(win) win.$(win.document).trigger('keyup',[e]);
		});
/**/

		self._hashRenderStr = self.getLocationHash();
	}
};

AgRender.prototype.iframe_load = function(e,t,o){
	var self = this;
	$(window).trigger('iframe_load'+self._namespace);
	var win = o.window ? o.window : self.getWindow();

	self._iframe_window = win;
	self._iframe_document = win.document;

	if(win){
		if(self._DEBUG) console.log("AgRender.iframe_load():"+win);

		var func = Ext.bind(self.iframe_load,self);
		Ext.EventManager.un(win,'load',func);

//			if(win.bp3d_parts_store) win.bp3d_parts_store.on('load',self.store_load);
		setTimeout(function(){
			self.store_load();
		},250);

		var $win = win.$(win);
		$win.bind('showLoading',function(){
			$(window).trigger('agrender_showLoading'+self._namespace);
		});
		$win.bind('hideLoading',function(){
			$(window).trigger('agrender_hideLoading'+self._namespace);
		});

		var trigger = function(){
			var e = arguments[0];
			var data = [];
			for(var i=1,l=arguments.length;i<l;i++){
				data.push(arguments[i]);
			}
			var e2 = new jQuery.Event(e.type+self._namespace);
			$(window).trigger(e2,data);
			if(e2.isDefaultPrevented()) e.preventDefault();
			if(e2.isPropagationStopped()) e.stopPropagation();
			if(e2.isImmediatePropagationStopped()) e.stopImmediatePropagation();
			return e2.result;
		}
		$win.bind('changeLongitudeDegree',trigger);
		$win.bind('changeLatitudeDegree',trigger);
		$win.bind('changeZoom',trigger);
		$win.bind('changeCameraNear',trigger);
		$win.bind('changeCameraFar',trigger);

		$win.bind('dropObject',trigger);
		$win.bind('pickObject',trigger);
		$win.bind('pinObject',trigger);
		$win.bind('addPalletParts',trigger);
		$win.bind('hideParts',trigger);
	}
};

AgRender.prototype.store_load = function(store,records,successful,eOpts){
	var self = this;
	if(self._DEBUG) console.log("AgRender.store_load()");
	var win = self.getWindow();
	var func = Ext.bind(self.createLocaleHashStr,self);

	var $win = win.$(win);
	$win.unbind('createLocaleHashStr',func);
	$win.bind('createLocaleHashStr',func);

	var func = Ext.bind(self.hashChange,self);
	$(window).unbind('hashchange', func);
	$(window).bind('hashchange', func);

	self.hashChange();

	$(window).trigger('agrender_load'+self._namespace,[self._hashRenderStr]);
};

AgRender.prototype.createLocaleHashStr = function(e,o){
	var self = this;
//		if(self._DEBUG) console.log("AgRender.createLocaleHashStr()");

	o = o || {};
	self._hashRenderStr = o.hash;
	self.createLocaleHashStrTask.delay(250);
};

AgRender.prototype.getLocationHash = function(){
	var self = this;
	var hashStr = window.location.hash.substr(1);
	if(Ext.isEmpty(hashStr) && self.AgLocalStorage) hashStr = self.AgLocalStorage.load(self._DEF_HASH_KEY);
	return hashStr;
};

AgRender.prototype.hashChange = function(){
	var self = this;
	if(self._DEBUG) console.log("AgRender.hashChange()");
	var win = self.getWindow();
	if(win){
		var hashStr = self.getLocationHash();
		if(self._DEBUG) console.log("AgRender.hashChange():hashStr=["+hashStr+"]");
		win.$(win).trigger('changeLocaleHashStr',[hashStr]);
	}
};

AgRender.prototype.getWindow = function(){
	var self = this;
	if(self._iframe_window) return self._iframe_window;
	var win;
	var iframe = self._iframe ? self._iframe : document.getElementById('ag-render');
	if(iframe) win = iframe;
	if(iframe && iframe.contentDocument && iframe.contentDocument.defaultView) win = iframe.contentDocument.defaultView;
	return win;
};

AgRender.prototype.setHash = function(hashStr){
	var self = this;
	if(self._DEBUG) console.log("AgRender.setHash()");

	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeLocaleHashStr',[hashStr]);
};

AgRender.prototype.changeGuide = function(checked){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeGuide',[checked]);
};

AgRender.prototype.changeToolTip = function(checked){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeToolTip',[checked]);
};

AgRender.prototype.changeStats = function(checked){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeStats',[checked]);
};

AgRender.prototype.changeLongitudeDegree = function(n,o){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeLongitudeDegree',[n,o]);
};

AgRender.prototype.changeLatitudeDegree = function(n,o){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeLatitudeDegree',[n,o]);
};

AgRender.prototype.changeZoom = function(n,o){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeZoom',[n,o]);
};

AgRender.prototype.changeCameraNear = function(n,o){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeCameraNear',[n,o]);
};

AgRender.prototype.changeCameraFar = function(n,o){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeCameraFar',[n,o]);
};

AgRender.prototype.printImage = function(){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('printImage');
};

AgRender.prototype.printRotatingImage = function(w,h){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('printRotatingImage',[w,h]);
};

AgRender.prototype.changeClickMode = function(clickmode){
	var self = this;
	var win = self.getWindow();
	if(win && win.$) win.$(win).trigger('changeClickMode',[clickmode]);
};
