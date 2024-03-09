///////////////////////////////////////////////////////////////////////////////
//ピック、ピン操作時のクリック位置即時反映
///////////////////////////////////////////////////////////////////////////////
window.ag_extensions = window.ag_extensions || {};
ag_extensions.pick_point = ag_extensions.pick_point || {};
///////////////////////////////////////////////////////////////////////////////
//初期化
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pick_point._init = function(){
	var self = this;
	self.__images_src__ = [{
		name:"select_A.png",
		css: {
			'margin-top':'-13px',
			'margin-left':'-11px'
		}
	},{
		name:"select_B.png",
		css: {
			'margin-top':'-11px',
			'margin-left':'-9px'
		}
	},{
		name:"select_C.png",
		css: {
			'margin-top':'-24px',
			'margin-left':'-11px'
		}
	},{
		name:"select_D.png",
		css: {
			'margin-top':'-16px',
			'margin-left':'-1px'
		}
	},{
		name:"select_E.png",
		css: {
			'margin-top':'-11px',
			'margin-left':'-4px'
		}
	}];
	self.__images_src__ = [{
		name:"select_B.png",
		css: {
			'margin-top':'-11px',
			'margin-left':'-9px'
		}
	}];
	self.__images__ = [];
	self.__images_pos__ = 0;

	self.$__element__ =
		$('<div>')
			.css({
				'position':'absolute',
				'top':'0px',
				'left':'0px',

// 背景色で位置を表示する場合
//				'width':'5px',
//				'height':'5px',
//				'margin-top':'-2px',
//				'margin-left':'-2px',
//				'background-color':'red',

// 背景画像で位置を表示する場合
//				'width':'16px',
//				'height':'16px',
//				'margin-top':'-14px',
//				'margin-left':'-2px',
//				'background':'url(css/pin.png) no-repeat top left',

//				'opacity':'0.5',
				'-webkit-border-radius':'2px',
				'-moz-border-radius':'2px',
				'-ms-border-radius':'2px',
				'-o-border-radius':'2px',
				'border-radius':'2px'
			})
			.hide()
			.appendTo('div#anatomography-image-contentEl');


	$.each(self.__images_src__, function(){
		var name = this.name;
		var image = new Image();
		image.isLoaded = false;
		$(image).one('load',function(){
			this.isLoaded = true;
		});
		image.src = "css/pick-point/"+name;

		self.__images__.push({
			name : name,
			image : image
		})
	});


	if(self.__images__.length==0){
// 背景色で位置を表示する場合
		self.$__element__.css({
			'width':'5px',
			'height':'5px',
			'margin-top':'-2px',
			'margin-left':'-2px',
			'background-color':'red'
		});
	}else{
// 背景画像で位置を表示する場合
		self.$__element__.css({
			'width':'16px',
			'height':'16px',
			'margin-top':'-14px',
			'margin-left':'-2px',
			'background':'url(css/pin.png) no-repeat top left'
		});
	}


	$('img#ag_img')
		.bind('load',ag_extensions.pick_point.hide)
		.bind('abort',ag_extensions.pick_point.hide)
		.bind('error',ag_extensions.pick_point.hide)
		.bind('mousedown',ag_extensions.pick_point._mousedown);
};
///////////////////////////////////////////////////////////////////////////////
//イメージへのマウスダウン時の処理
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pick_point._mousedown = function(e){
	if(e.which != 1) return;
	ag_extensions.pick_point.__mousedown__ = e;
	$('img#ag_img')
		.bind('mousemove',ag_extensions.pick_point._mousemove)
		.bind('mouseup',ag_extensions.pick_point._mouseup)
};
///////////////////////////////////////////////////////////////////////////////
//イメージへのマウスムーブ時の処理
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pick_point._mousemove = function(e){
	if(
		ag_extensions.pick_point.__mousedown__
	){
		var left = 0;
		var top = 0;
		if(e.offsetX !== undefined && e.offsetY !== undefined){
			left = ag_extensions.pick_point.__mousedown__.offsetX - e.offsetX;
			top  = ag_extensions.pick_point.__mousedown__.offsetY - e.offsetY;
		}
		else if(e.layerX !== undefined && e.layerY !== undefined){
			left = ag_extensions.pick_point.__mousedown__.layerX - e.layerX;
			top  = ag_extensions.pick_point.__mousedown__.layerY - e.layerY;
		}
		if(left || top){
			$('img#ag_img')
				.unbind('mousemove',ag_extensions.pick_point._mousemove)
				.unbind('mouseup',ag_extensions.pick_point._mouseup)
			delete ag_extensions.pick_point.__mousedown__;
		}
	}
};
///////////////////////////////////////////////////////////////////////////////
//イメージへのマウスアップ時の処理
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pick_point._mouseup = function(e){
	if(
		ag_extensions.pick_point.__mousedown__
	){
		var left = undefined;
		var top = undefined;
		if(e.offsetX !== undefined && e.offsetY !== undefined &&
			ag_extensions.pick_point.__mousedown__.offsetX == e.offsetX &&
			ag_extensions.pick_point.__mousedown__.offsetY == e.offsetY
		){
			left = e.offsetX;
			top  = e.offsetY;
		}
		else if(e.layerX !== undefined && e.layerY !== undefined &&
			ag_extensions.pick_point.__mousedown__.layerX == e.layerX &&
			ag_extensions.pick_point.__mousedown__.layerY == e.layerY
		){
			left = e.layerX;
			top  = e.layerY;
		}
		if(left !== undefined && top !== undefined){
// 背景色で位置を表示する場合
			if(ag_extensions.pick_point.__images__.length==0){
				var background = ag_extensions.pick_point.$__element__.css('background-color');
				if(window.glb_point_color && typeof window.glb_point_color == 'string'){
					background = window.glb_point_color;
					if(background.match(/^#*([A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9][A-F0-9])$/i)){
						background = '#'+RegExp.$1;
					}else if(background.match(/^#*([A-F0-9][A-F0-9][A-F0-9])$/i)){
						background = '#'+RegExp.$1;
					}
				}
				ag_extensions.pick_point.$__element__.css({
					'background-color':background
				});
			}else{
				ag_extensions.pick_point.__images_pos__++;
				if(ag_extensions.pick_point.__images_pos__ > ag_extensions.pick_point.__images__.length) ag_extensions.pick_point.__images_pos__ = 1;
				var image = ag_extensions.pick_point.__images__[ag_extensions.pick_point.__images_pos__-1].image;
				var css = ag_extensions.pick_point.__images_src__[ag_extensions.pick_point.__images_pos__-1].css;
//				console.log(image.src);
//				console.log(css);
				ag_extensions.pick_point.$__element__.css({
					'background-image':'url('+ image.src +')',
					width: image.width,
					height: image.height
				}).css(css);
			}
			ag_extensions.pick_point.$__element__.css({
				'left':left,
				'top' :top
			});
			ag_extensions.pick_point.show();
		}
		delete ag_extensions.pick_point.__mousedown__;
	}
	$('img#ag_img')
		.unbind('mousemove',ag_extensions.pick_point._mousemove)
		.unbind('mouseup',ag_extensions.pick_point._mouseup);
};
///////////////////////////////////////////////////////////////////////////////
//表示
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pick_point.show = function(){
	ag_extensions.pick_point.$__element__.show();
};
///////////////////////////////////////////////////////////////////////////////
//非表示
///////////////////////////////////////////////////////////////////////////////
ag_extensions.pick_point.hide = function(){
	ag_extensions.pick_point.$__element__.hide();
};
///////////////////////////////////////////////////////////////////////////////
//初期化処理コール
///////////////////////////////////////////////////////////////////////////////
$(document).ready(function(){
	ag_extensions.pick_point._init();
});
