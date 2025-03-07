var AgLocalStorage = function(){
	var self = this;
};

AgLocalStorage.prototype._getkey = function(key,pos){
	var self = this;
	return key+'-'+pos;
};

AgLocalStorage.prototype.save = function(key,value){
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
};

AgLocalStorage.prototype.load = function(key){
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
};

AgLocalStorage.prototype._remove = function(key,value){
	var self = this;
	if(!Ext.isString(value) || Ext.isNumeric(value)){
		var i=0;
		var l = Ext.isString(value) ? parseInt(value) : value;
		for(i=0;i<l;i++){
			window.localStorage.removeItem(self._getkey(key,i));
		}
	}
	window.localStorage.removeItem(key);
};

AgLocalStorage.prototype.remove = function(key){
	var self = this;
	self._remove(key,window.localStorage[key]);
};

AgLocalStorage.prototype.exists = function(key){
	var self = this;
	if(window.localStorage[key]){
		return true;
	}else{
		return false;
	}
};


