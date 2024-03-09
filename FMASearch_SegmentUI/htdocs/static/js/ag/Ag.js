
Ext.define('Ag', {
//	singleton: true,
	constructor: function (config) {
		var self = this;
		self.__config = config || {};
		self.__main = new Ag.Main();
	}
});
/*
(function() {
	new Ag();
}());
*/
