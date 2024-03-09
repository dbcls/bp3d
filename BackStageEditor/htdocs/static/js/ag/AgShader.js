//テスト用
var AgShader = {
	_shader : [],
	getMaterial : function(color,opacity){
		var r,g,b;
		if(typeof color == "string"){
			if(color.length==7 && color.substr(0,1) == '#' && color.substr(1).match(/^[0-9A-F]+$/i)) color = '0x'+color.substr(1);
			if(color.length==6 && color.match(/^[0-9A-F]+$/i)) color = '0x'+color;
			color = Number(color);
		}
		if(typeof color == "number"){
			color = new THREE.Color(color);
		}
		if(color instanceof THREE.Color){
			r = color.r;
			g = color.g;
			b = color.b;
		}
		if(opacity===undefined) opacity = 1;
		if(typeof opacity == "string") opacity = Number(opacity);
		if(typeof r == "number" && typeof g == "number" && typeof b == "number" && typeof opacity == "number"){
			var shaderKey = r + '_' + g + '_' + b + '_' + opacity;
			if(!AgShader._shader[shaderKey]){
				AgShader._shader[shaderKey] = new THREE.ShaderMaterial({
					uniforms: {},
					vertexShader: [
						"void main() {",
							"gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );",
						"}"
					].join("\n"),
					fragmentShader: [
						"void main() {",
							"gl_FragColor = vec4("+r+","+g+","+b+","+opacity+");",
						"}"
					].join("\n"),
					transparent: true
				});
			}
			return AgShader._shader[shaderKey];
		}else{
			return undefined;
		}
	}
};
