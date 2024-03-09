window.AgApp = window.AgApp || function(config){};
window.AgApp.prototype.fileDragover = function(event){
//	console.log('fileDragover()');
	if(event && event.stopEvent) event.stopEvent();
	return false;
};
window.AgApp.prototype.fileDragenter = function(event){
//	console.log('fileDragenter()');
	if(event && event.stopEvent) event.stopEvent();
	return false;
};
window.AgApp.prototype.fileDropCancel = function(event){
//	console.log('fileDropCancel()');
	if(event && event.stopEvent) event.stopEvent();
	return false;
};
window.AgApp.prototype.fileDrop = function(event, eOpt){
	var self = this;
	try{
		delete self.__dropfile_total;
		delete self.__dropfile_count;
		delete self.__dropfiles;
		delete self.__dropfolders;
		delete self.__dropreaders;
		delete self.__dropfile_callback;

		self.__dropfile_total = 0;
		self.__dropfile_count = 0;
		self.__dropfiles = [];
		self.__dropfolders = [];
		self.__dropreaders = [];
		self.__dropfile_callback = (eOpt || {}).callback;

		var dataTransfer;
		if(Ext.isObject(event)){
			if(event.browserEvent && event.browserEvent.dataTransfer){
				dataTransfer = event.browserEvent.dataTransfer;
			}else if(event.dataTransfer){
				dataTransfer = event.dataTransfer;
			}
		}
		if(dataTransfer){

			if(dataTransfer.items && dataTransfer.items.length>0){
//				console.log('START drop');
				var items = dataTransfer.items,
						len = items.length,
						i;
//				if(len>0) len = 1;	//ドロップするファイル数は一つとする
				self.__dropfile_total = len;
				for(i=0;i<len;i++){
					var item = items[i], entry;
					if(item.getAsEntry){
						entry = item.getAsEntry();
					}else if(item.webkitGetAsEntry){
						entry = item.webkitGetAsEntry();
					}
					if(entry) self._fileDropEntry(entry);
				}
//				console.log('END drop');
			}
			else if(dataTransfer.files && dataTransfer.files.length>0){

//				self.__dropfiles = [].cancat(dataTransfer.files);

/*
				self.__dropfiles = dataTransfer.files;
				if(Ext.isFunction(self.__dropfile_callback)){
					Ext.defer(function(){
						self.__dropfile_callback.apply(self,[self.__dropfiles]);
					},0);
				}
*/


				var files = dataTransfer.files,
						len = files.length,
						i;
//				if(len>0) len = 1;	//ドロップするファイル数は一つとする
				self.__dropfile_total = len;
				for(i=0;i<len;i++){
//					self.__dropfile_count++;
					var reader = new FileReader();
					reader.__file = files[i];
//					console.log(reader.__file);

					reader.onload = function(e) {
//						console.log('onload()');
//						console.log(e.target.result);
//						console.log(e);
//						console.log(e.target);
					};
					reader.onabort = function(e) {
//						console.log('onabort()');
//						console.log(e);
//						console.log(e.target);
					};
					reader.onerror = function(e) {
//						console.log('onerror()');
//						console.log(e);
//						console.log(e.target);
						console.error(e.target.error);
						var msg = e.target.error.name;
						if(e.target.error.message) msg += ' : ' + e.target.error.message;
						Ext.Msg.show({
							title: e.target.__file.name,
							msg: msg,
							buttons: Ext.Msg.OK,
							icon: Ext.Msg.ERROR
						});

					};
					reader.onloadend = function(e) {
//						console.log('onloadend()');
//						console.log(e);
//						console.log(e.target);

//						--self.__dropfile_count;
						self.__dropfile_count++;

						if(e.target.result) self.__dropfiles.push(e.target.__file);
						self.__dropreaders.push(e.target);
//						if(self.__dropfile_count===0){
						if(self.__dropfile_count===self.__dropfile_total){
							if(Ext.isFunction(self.__dropfile_callback)){
								Ext.defer(function(){
									self.__dropfile_callback.apply(self,[self.__dropfiles,self.__dropfolders,self.__dropreaders]);
								},0);
							}
						}

					};
					reader.onloadstart = function(e) {
//						console.log('onloadstart()');
//						console.log(e);
//						console.log(e.target);
					};
					reader.onprogress = function(e) {
//						console.log('onprogress()');
//						console.log(e);
//						console.log(e.target);
					};
					reader.readAsText(files[i]);
				}

			}
		}
	}catch(e){
		console.error(e);
	}
	if(event && event.stopEvent) event.stopEvent();
	return false;
};
window.AgApp.prototype._fileDropEntry = function(entry,directoryEntry){
	var self = this;
	if(entry.isFile){
//		console.log(entry);
//		self.__dropfile_count++;
		entry.file(function(file){
//			console.log(file);
//			console.log();
//			--self.__dropfile_count;
//			self.__dropfiles.push(file);
//			if(self.__dropfile_count===0){
//				if(Ext.isFunction(self.__dropfile_callback)){
//					Ext.defer(function(){
//						self.__dropfile_callback.apply(self,[self.__dropfiles,self.__dropfolders]);
//					},0);
//				}
//			}
//			return;
			var reader = new FileReader();
			file.__directoryEntry = directoryEntry;
			reader.__file = file;
//			console.log(reader.__file);

			reader.onload = function(e) {
//				console.log('onload()');
//				console.log(e.target.result);
//				console.log(e);
//				console.log(e.target);
			};
			reader.onabort = function(e) {
//				console.log('onabort()');
//				console.log(e);
//				console.log(e.target);
			};
			reader.onerror = function(e) {
//				console.log('onerror()');
//				console.log(e);
//				console.log(e.target);

				console.error(e.target.error);
				var msg = e.target.error.name;
				if(e.target.error.message) msg += ' : ' + e.target.error.message;
				Ext.Msg.show({
					title: e.target.__file.name,
					msg: msg,
					buttons: Ext.Msg.OK,
					icon: Ext.Msg.ERROR
				});

			};
			reader.onloadend = function(e) {
//				console.log('onloadend()');
//				console.log(e);
//				console.log(e.target);


				self.__dropfile_count++;
				if(e.target.result) self.__dropfiles.push(e.target.__file);
				self.__dropreaders.push(e.target);
				if(self.__dropfile_count===self.__dropfile_total){
					if(Ext.isFunction(self.__dropfile_callback)){
						Ext.defer(function(){
							self.__dropfile_callback.apply(self,[self.__dropfiles,self.__dropfolders,self.__dropreaders]);
						},0);
					}
				}


			};
			reader.onloadstart = function(e) {
//				console.log('onloadstart()');
//				console.log(e);
//				console.log(e.target);
			};
			reader.onprogress = function(e) {
//				console.log('onprogress()');
//				console.log(e);
//				console.log(e.target);
			};
			reader.readAsText(file);

		});
	}
	else if(entry.isDirectory){
		self.__dropfolders.push(entry);
		var reader = entry.createReader();
		reader.readEntries(
			function(results){
				var len = results.length,
						i;
				self.__dropfile_total--;//Directory分
				self.__dropfile_total += len;

//				console.log('START isDirectory:['+len+']');
				for(i=0;i<len;i++){
					self._fileDropEntry(results[i],entry);
				}
//				console.log('END isDirectory');
			},
			function(error) {
				console.error(error);
				alert("読み込みに失敗しました。");
			}
		);
	}
},
window.AgApp.prototype.initFileDrop = function(){
	var self = this;

//<!--<body ondragover="return AgApp.fileDragover(event);" dragenter="return AgApp.fileDragenter(event);" ondrop="return AgApp.fileDrop(event);">-->
/*
	Ext.getBody().on({
		dragover: self.fileDragover,
		dragenter: self.fileDragenter,
		drop: self.fileDrop,
		scope: self
	});
*/
	Ext.getBody().on({
		dragover: self.fileDragover,
		dragenter: self.fileDragenter,
		drop: self.fileDropCancel,
		scope: self
	});


};
/*
// Taking care of the browser-specific prefixes.
window.requestFileSystem  = window.requestFileSystem || window.webkitRequestFileSystem;
window.directoryEntry = window.directoryEntry || window.webkitDirectoryEntry;

function errorHandler(e) {
  var msg = '';

  switch (e.code) {
    case FileError.QUOTA_EXCEEDED_ERR:
      msg = 'QUOTA_EXCEEDED_ERR';
      break;
    case FileError.NOT_FOUND_ERR:
      msg = 'NOT_FOUND_ERR';
      break;
    case FileError.SECURITY_ERR:
      msg = 'SECURITY_ERR';
      break;
    case FileError.INVALID_MODIFICATION_ERR:
      msg = 'INVALID_MODIFICATION_ERR';
      break;
    case FileError.INVALID_STATE_ERR:
      msg = 'INVALID_STATE_ERR';
      break;
    default:
      msg = 'Unknown Error';
      break;
  };
  console.log('Error: ' + msg);
}

function toArray(list) {
  return Array.prototype.slice.call(list || [], 0);
}

function listResults(entries) {
	entries.forEach(function(entry, i) {
		console.log(entry.name);
	});
}

function onInitFs(fs) {

  var dirReader = fs.root.createReader();
  var entries = [];

  // Keep calling readEntries() until no more results are returned.
  var readEntries = function() {
     dirReader.readEntries (function(results) {
      if (!results.length) {
        listResults(entries.sort());
      } else {
        entries = entries.concat(toArray(results));
        readEntries();
      }
    }, errorHandler);
  };

// Start reading the directory.

  readEntries();

}
window.requestFileSystem(window.TEMPORARY, 1024*1024, onInitFs, errorHandler);
*/
