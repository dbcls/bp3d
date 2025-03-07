function agFileUpload(config){
	var self = this;
	self._config = config || {};
	self._config.BYTES_PER_CHUNK = self._config.BYTES_PER_CHUNK || 1024 * 1024 * 5; // 5MB chunk sizes.

	self._path = (window.location.pathname.split("/").splice(0,window.location.pathname.split("/").length).join("/"));

	try{
		var files = self._config.files || [];

		var fileidx = 0;
//										const BYTES_PER_CHUNK = 1024 * 1024 * 10; // 10MB chunk sizes.
		var DEF_TYPE = 'multipart/byteranges';
		var BYTES_PER_CHUNK = 1024 * 1024 * 5; // 5MB chunk sizes.
		var start = 0;
		var end = BYTES_PER_CHUNK;
		var cnt=0;

		function clear() {
			Ext.util.Cookies.clear('upload.name',self._path);
			Ext.util.Cookies.clear('upload.type',self._path);
			Ext.util.Cookies.clear('upload.size',self._path);
			Ext.util.Cookies.clear('upload.modified',self._path);
			Ext.util.Cookies.clear('upload.slice',self._path);
			Ext.util.Cookies.clear('upload.index',self._path);
		}

		function remove() {
			Ext.util.Cookies.set('upload.remove',true,null,self._path);
			var xhr = new XMLHttpRequest();
			xhr.open('POST', 'upload-files.cgi', false);
			xhr.onload = function(e){};
			xhr.send();
			Ext.util.Cookies.clear('upload.remove',self._path);
		}

		function upload(blobOrFile,type,aCB) {
			var xhr = new XMLHttpRequest();
			xhr.open('POST', 'upload-files.cgi', true);
			xhr.onload = function(e) {
				var success = false;
				var totalSize = 0;
				try{
					var json;
					try{json = Ext.decode(e.target.responseText);}catch(e){console.error(e);}
					if(Ext.isObject(json)){
						if(json.success) success = true;
						if(json.totalSize) totalSize = json.totalSize;
					}
				}catch(e){
					console.error(e);
				}
				if(aCB) (aCB)(success,totalSize);
			};
			var blob = new Blob([blobOrFile], {type:DEF_TYPE});//firefox対策
			xhr.send(blob);
		}

		function file_slice(fileidx,start,end,cnt){
			try{
				var file = files[fileidx];
				if(Ext.isEmpty(file)){
					clear();
					if(self._config.success) (self._config.success)();
					return;
				}
				var SIZE = file.size;
				if(start==0){
					if(self._config.progress){
						var rtn = (self._config.progress)(file,0);
						if(Ext.isBoolean(rtn) && rtn==false){
							remove();
							clear();
							return;
						}
					}
					Ext.util.Cookies.set('upload.name',file.name,null,self._path);
					Ext.util.Cookies.set('upload.type',file.type?file.type:DEF_TYPE,null,self._path);
					Ext.util.Cookies.set('upload.size',file.size,null,self._path);
					Ext.util.Cookies.set('upload.modified',file.lastModifiedDate.getTime(),null,self._path);
					Ext.util.Cookies.set('upload.slice',BYTES_PER_CHUNK,null,self._path);
				}

				if(start==0 || start<SIZE){
					var blob;
					if(file.slice){
						blob = file.slice(start, end);
					}else if(file.webkitSlice){
						blob = file.webkitSlice(start, end);
					}else if(file.mozSlice){
						blob = file.mozSlice(start, end);
					}
					if(blob){
						if(self._config.progress){
							var rtn = (self._config.progress)(file,end<SIZE?end:SIZE);
							if(Ext.isBoolean(rtn) && rtn==false){
								remove();
								clear();
								return;
							}
						}
						Ext.util.Cookies.set('upload.index',cnt++,null,self._path);
						upload(blob,file.type,function(success,totalSize){
							if(success){
								if(start<SIZE && totalSize<SIZE){
									start = end;
									end = start + BYTES_PER_CHUNK;
								}else{
									var rtn = (self._config.progress)(file,SIZE);
									if(Ext.isBoolean(rtn) && rtn==false){
										clear();
										return;
									}
									start = 0;
									end = BYTES_PER_CHUNK;
									cnt=0;
									fileidx++;
								}
							}else{
								fileidx = -1;
							}
							file_slice(fileidx,start,end,cnt);
						});
					}
				}
			}catch(e){
				console.error(e);
				remove();
				clear();
				if(self._config.failure) (self._config.failure)(e);
			}
		};

		file_slice(fileidx,start,end,cnt);
	}catch(e){
		console.error(e);
		if(self._config.failure) (self._config.failure)(e);
	}
}
