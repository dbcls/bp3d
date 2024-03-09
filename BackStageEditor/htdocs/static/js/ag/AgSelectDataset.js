window.AgApp = window.AgApp || function(config){};

window.AgApp.prototype.openSelectDatasetWindow = function(config){
	var self = this;

	config = config || {};
	config.title = config.title || 'Dataset Select';
	config.iconCls = config.iconCls || 'pallet_download';
	config.height = config.height || 400;
	config.width = config.width || 600;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

	var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
	var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
	if(Ext.isEmpty(config.concept_datas)) config.concept_datas = conceptBuildStore.getRange().map(function(r){return r.getData();});
	if(Ext.isEmpty(config.dataset_datas)) config.dataset_datas = datasetMngStore.getRange().map(function(r){return r.getData();});

	var select_window = Ext.create('Ext.ag.SelectDatasetWindow', {
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		minWidth: config.width,
		minHeight: config.height,
		animateTarget: config.animateTarget,
		params: config.params,
		callback: config.callback,
		concept_datas: config.concept_datas || [],
		dataset_datas: config.dataset_datas || [],
/*
		items: [{
			xtype: 'label',
			text: 'aaa'
		}]
*/
	}).show();
};


window.AgApp.prototype.openExportSelectDatasetWindow = function(config){
	var self = this;

	config = config || {};
	config.title = config.title || 'Export';
	config.iconCls = config.iconCls || 'pallet_download';
	config.height = config.height || 400;
	config.width = config.width || 600;
	config.modal = config.modal || true;

	var maxHeight = $(document.body).height();
	var maxWidth = $(document.body).width();

	if(config.height>maxHeight) config.height = maxHeight;
	if(config.width>maxWidth) config.width = maxWidth;

	var datasetMngStore = Ext.data.StoreManager.lookup('datasetMngStore');
	var conceptBuildStore = Ext.data.StoreManager.lookup('conceptBuildStore');
	if(Ext.isEmpty(config.concept_datas)) config.concept_datas = conceptBuildStore.getRange().map(function(r){return r.getData();});
	if(Ext.isEmpty(config.dataset_datas)) config.dataset_datas = datasetMngStore.getRange().map(function(r){return r.getData();});

	var export_window = Ext.create('Ext.ag.ExportSelectDatasetWindow', {
		title: config.title,
		iconCls: config.iconCls,
		modal: config.modal,
		height: config.height,
		width: config.width,
		minWidth: config.width,
		minHeight: config.height,
		animateTarget: config.animateTarget,
		params: config.params,
		callback: config.callback,
		concept_datas: config.concept_datas || [],
		dataset_datas: config.dataset_datas || [],
		filename: config.filename
	}).show();
};
