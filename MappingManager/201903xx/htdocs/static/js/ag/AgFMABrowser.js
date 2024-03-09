window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.openFMABrowser = function(cdi_name){
	var self = this;

//	var FMABrowser_URL = '../FMABrowser/160616/';
	var FMABrowser_URL = '../FMABrowser/';
	if(window.location.pathname.match(/\/[0-9]+\/$/)) FMABrowser_URL = '../'+FMABrowser_URL;	//DEBUG環境の場合

	if(Ext.isEmpty(cdi_name)) cdi_name = '';

	if(Ext.isEmpty(self.__FMABrowser) || self.__FMABrowser.closed){
		if(Ext.isEmpty(self.__FMABrowser)){
			console.warn('empty self.__FMABrowser.$');
		}else{
			console.warn('closed self.__FMABrowser.$');
		}

		var w = $(window).width() - 10;
		var h = $(window).height() - 10;
		var url = FMABrowser_URL + (Ext.isEmpty(cdi_name) ? '' : '#id=' + cdi_name);
		self.__FMABrowser = window.open(url,'__FMABrowser','width='+w+',height='+h+',dependent=yes,directories=no,menubar=no,resizable=yes,status=no,toolbar=no');
		console.log(self.__FMABrowser);

		var message = function(event){
			console.log('message',event.data);
		};
		self.__FMABrowser.addEventListener('message', message);

		var updatelastrecord = function(e,data){
			console.log('updatelastrecord');
			console.log(data);
		};

		var unload = function(event){
			console.log('unload');
			Ext.defer(function(){
				if(self.__FMABrowser.$){
					self.__FMABrowser.$(self.__FMABrowser).on('updatelastrecord',updatelastrecord);
					$(self.__FMABrowser).on('unload',unload);
				}else{
					console.warn('undefined self.__FMABrowser.$');
				}
				self.__FMABrowser.addEventListener('message', message);
			},1000);
		};

		if(self.__FMABrowser.$){
			self.__FMABrowser.$(self.__FMABrowser).on('updatelastrecord',updatelastrecord);

			$(self.__FMABrowser).on('unload',unload);
		}else{
			console.warn('wait self.__FMABrowser.$');
			Ext.defer(function(){
				if(self.__FMABrowser.$){
					self.__FMABrowser.$(self.__FMABrowser).on('updatelastrecord',updatelastrecord);
				}else{
					console.warn('undefined self.__FMABrowser.$');
				}
			},1000);
		}
	}else if(cdi_name){
		var obj = Ext.Object.fromQueryString(self.__FMABrowser.location.hash.substr(1));
		obj.id = cdi_name;
		self.__FMABrowser.location.hash = Ext.Object.toQueryString(obj);
	}
	self.__FMABrowser.focus();
};
