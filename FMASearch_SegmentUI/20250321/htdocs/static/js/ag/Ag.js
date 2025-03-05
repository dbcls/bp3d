
Ext.define('Ag', {
//	singleton: true,
	constructor: function (config) {
//		console.log(config);
		var self = this;
		self.__config = config || {};
		self.__main = new Ag.Main(config);
	}
});
/*
(function() {
	new Ag();
}());
*/
