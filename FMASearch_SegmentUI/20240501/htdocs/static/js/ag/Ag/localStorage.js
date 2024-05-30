//var Ag = Ag || {};
Ext.define('Ag.LocalStorage', {
	singleton: true,
	constructor: function (config) {
		var self = this;
	},

	_getkey : function(key,pos){
		var self = this;
		return key+'-'+pos;
	},

	save : function(key,value){
		var self = this;

		self.remove(key);

		var QUANTUM = 65536;
		var pos=0;
		var i;

		for(i=0;;i+=QUANTUM){
			var v = value.substr(i,QUANTUM);
			if(Ext.isEmpty(v)) break;
			try{
				window.localStorage[self._getkey(key,pos)] = v;
			}catch(e){
				console.error(e);
				console.warn(key,pos);
				self._remove(key,pos+1);
				pos = null;
				break;
			}
			pos++;
		}
		if(Ext.isEmpty(pos)) return;
		window.localStorage[key] = pos;
	},

	load : function(key){
		var self = this;

		var value = window.localStorage[key];
		if(!Ext.isString(value) || Ext.isNumeric(value)){
			var i=0;
			var l = Ext.isString(value) ? parseInt(value) : value;
			value = '';
			for(i=0;i<l;i++){
				value += window.localStorage[self._getkey(key,i)];
			}
		}
		return value;
	},

	_remove : function(key,value){
		var self = this;
		if(!Ext.isString(value) || Ext.isNumeric(value)){
			var i=0;
			var l = Ext.isString(value) ? parseInt(value) : value;
			for(i=0;i<l;i++){
				window.localStorage.removeItem(self._getkey(key,i));
			}
		}
		window.localStorage.removeItem(key);
	},

	remove : function(key){
		var self = this;
		self._remove(key,window.localStorage[key]);
	},

	exists : function(key){
		var self = this;
		if(window.localStorage[key]){
			return true;
		}else{
			return false;
		}
	}
});
