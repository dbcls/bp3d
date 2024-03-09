(function($){
	$(document).ready(function(){
//		return;
		var version_name = '20211201il500';
		$.ajax({
			type: 'GET',
			cache: true,
			url: 'renderer_file/renderer_file/'+version_name+'.jgz',
			dataType: 'json',
			success: function(data, dataType){
				console.log(data, dataType);
				if(
					$.isPlainObject(data) &&
					$.isPlainObject(data[version_name]) &&
					$.isPlainObject(data[version_name].art_ids)
				){
				var urls = [];
					Object.keys(data[version_name].art_ids).forEach(function(value,index){
						var i = index%20;
						if(!$.isArray(urls[i])) urls[i] = [];
						urls[i].push('../../../art_file/'+value+'.ogz');
					});
					if(urls.length){

						var buffer_to_string = function(buf){
							return String.fromCharCode.apply("", new Uint16Array(buf))
						};
						var large_buffer_to_string = function(buf){
							var tmp = [];
							var len = 1024;
							for (var p = 0; p < buf.byteLength; p += len) {
								tmp.push(buffer_to_string(buf.slice(p, p + len)));
							}
							return tmp.join("");
						};
						urls.forEach(function(value,index){
							var worker = new Worker('static/js/worker/worker.js?1');
							var i = 0;
							var l = value.length;
							worker.postMessage({urls:value});
							worker.addEventListener('message', function(event) {
								var command = event.data.command;
								if (command === 'download') {
									var filename = event.data.filename;
									console.log(index + ':' + command + ':'+ (++i) + ':' + Math.ceil((i/l)*100) + '%:' + filename);
//									console.log(large_buffer_to_string(event.data.arrayBuffer));
								}
								if (command === 'complete') {
									console.log(index + ':' + command);
									worker.terminate();
								}
							});
						});

					}
				}
			}
		});
	});
})(jQuery);
