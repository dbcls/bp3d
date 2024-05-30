var global = self;
//importScripts("/path/to/jszip.js");
//importScripts("/path/to/promise-3.2.0.js");

//var zip = new JSZip();

self.addEventListener('message', function (event) {
	var urls = event.data.urls.concat([]);
/*
	var promises = urls.map(function (url) {
		return new Promise(function (resolve, reject) {
			var xhr = new XMLHttpRequest();
			xhr.open("GET", url);
			xhr.responseType = "arraybuffer";

			xhr.onload = function (event) {
				var arrayBuffer = xhr.response;
				var filename = url.replace(/^(.*)\//, '');
				postMessage({
					command: 'download',
					filename: filename,
					arrayBuffer: arrayBuffer
				});
				resolve(true);
			};
			xhr.onerror = function (event) {
				resolve(false);
			};
			xhr.send();
		});
	});
	Promise.all(promises).then(function () {
		postMessage({
			command: 'complete',
		});
	});
*/
	var a = function(){
		if(urls.length){
			var url = urls.shift();
			f(url);
		}
		else{
			postMessage({
				command: 'complete',
			});
		}
	};
	var f = function(url){
		var xhr = new XMLHttpRequest();
		xhr.open("GET", url);
//		xhr.responseType = "arraybuffer";

		xhr.onload = function (event) {
//			var arrayBuffer = xhr.response;
			var filename = url.replace(/^(.*)\//, '');
			postMessage({
				command: 'download',
				filename: filename,
//				arrayBuffer: arrayBuffer
			});
			a();
		};
		xhr.onerror = function (event) {
			console.error(event);
			a();
		};
		xhr.send();
	};
	a();

});
