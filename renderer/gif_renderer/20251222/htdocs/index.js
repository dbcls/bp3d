//http://192.168.1.139:8000/image?{%22Part%22:[{%22PartID%22:%22FMA5018%22}]}
//{"Method":"image","Part":[{"PartID":"FMA5018"}]}
;(function ($) {

	let hashchange = function(e){
		console.log('hashchange', e);
		if(location.hash.length>1){
			try{
				let hash = JSON.parse(decodeURIComponent(location.hash.substring(1))) || {};
				console.log(hash);
				if(typeof hash['Method'] != 'string') hash['Method'] = 'image';
				let method = hash['Method'];
				delete hash['Method'];
				if(typeof hash['DateTime'] == 'undefined') hash['DateTime'] = (new Date()).getTime();
				let hashstr = JSON.stringify(hash);
				let url = '/'+method+'?'+hashstr;
				console.log(url);
				$('div#wait').show();
				$.getJSON(url,null,function(data){
					$('div#wait').hide();
					console.log(data);
					if($.isPlainObject(data)) $('img').attr('src',data['data']);
				});
			}catch(e){
				console.error(e);
			}
		}
	};

	$(document).ready(function(){
		$('<div>')
		.attr({id:'wait'})
		.css({
			position: 'absolute',
			left: '0px',
			right: '0px',
			top: '0px',
			bottom: '0px',
			'background-color': 'rgba(0,0,0,0.5)'
		})
		.appendTo($('body'))
		.hide();

		$(window).on('hashchange', hashchange);
		hashchange();
		$('img').on('mousedown', function(e){
			console.log('mousedown', e);
			if(location.hash.length>1){
				try{
					let ScreenPosX = e.originalEvent.offsetX;
					let ScreenPosY = e.originalEvent.offsetY;

					let hash = JSON.parse(decodeURIComponent(location.hash.substring(1))) || {};
					console.log(hash);
//					if(typeof hash['Method'] != 'string') hash['Method'] = 'pick';
//					let method = hash['Method'];
					delete hash['Method'];
					delete hash['Pick'];
					hash['Pick'] = {
						ScreenPosX: ScreenPosX,
						ScreenPosY: ScreenPosY
					};
					let hashstr = encodeURIComponent(JSON.stringify(hash));
					let url = '/pick?'+hashstr;
					console.log(url);
					$.getJSON(url,null,function(data){
						console.log(data);
						//if($.isPlainObject(data)) $('img').attr('src',data['data']);
					});

				}catch(e){
					console.error(e);
				}
			}
		});
	});

}(jQuery));
