/*
function getCurrentImageSide(){
//	console.log('getCurrentImageSide()');
	return Ext.isEmpty(window.RepresentationManagerImageCurrentImageSide) ? 1: window.RepresentationManagerImageCurrentImageSide;
}
function setCurrentImageSide(imageSide){
	window.RepresentationManagerImageCurrentImageSide = imageSide;
}
*/
Ext.define('RepresentationManager', {
	constructor: function(config){
		var self = this;
		config = config || {};
		self.viewport = Ext.create('RepresentationManager.Viewport',Ext.apply({id:'rmviewport', itemId: 'rmviewport'},config));
	}
});

Ext.define('RepresentationManager.model.IMAGE_SIDE', {
	extend: 'Ext.data.Model',
	fields: [{
		name:'value',
		type:'int'
	},{
		name: 'display',
		type:'string'
	}]
});

Ext.define('RepresentationManager.model.DATA_COMBOBOX_MODEL', {
	extend: 'Ext.data.Model',
	fields: [{
		name:'value',
		type:'string'
	},{
		name: 'display',
		type:'string'
	}]
});

Ext.define('RepresentationManager.model.CONCEPT_TERM', {
	extend: 'Ext.data.Model',
	fields: [{
		name:'src',
		type:'string',
		convert:function(v, record){
			if(Ext.isEmpty(v)){
				var img_paths = record.get('img_paths');
				if(Ext.isArray(img_paths['imgsM']) && img_paths['imgsM'].length){
					return Ext.String.htmlEncode(img_paths['imgsM'][RepresentationManager.CurrentImageSide.get()]);
				}
			}
			return v;
		}
	},{
		name:'caption',
		type:'string',
		convert:function(v, record){
			if(Ext.isEmpty(v)){
				return Ext.String.htmlEncode(Ext.util.Format.format('{0} : {1}',record.get('cdi_id'),record.get('cdi_name')));
			}else{
				return v;
			}
		}
	},{
		name:'alt',
		type:'string',
		convert:function(v, record){
			if(Ext.isEmpty(v)){
				return Ext.String.htmlEncode(Ext.util.Format.format('{0} : {1}',record.get('cdi_id'),record.get('cdi_name')));
			}else{
				return v;
			}
		}
	},{
		name:'cdi_id',
		type:'string'
	},{
		name:'cdi_name',
		type:'string'
	},{
		name:'cdi_synonym',
		type:'auto',
		useNull:true
	},{
		name:'cdi_definition',
		type:'string',
		useNull:true
	},{
		name:'img_paths',
		type:'auto',
		useNull:true
	},{
		name:'bgcolor',
		type:'string',
		defaultValue: '#F0D2A0'
	},{
		name:'primitive',
		type:'boolean',
		defaultValue: false
	},{
		name:'density',
		type:'float',
		defaultValue: 0
	},{
		name:'density_icon',
		type:'string',
		useNull:true
	},{
		name:'volume',
		type:'float',
		defaultValue: 0
	},{
		name:'xmax',
		type:'float',
		defaultValue: 0
	},{
		name:'xmin',
		type:'float',
		defaultValue: 0
	},{
		name:'ymax',
		type:'float',
		defaultValue: 0
	},{
		name:'ymin',
		type:'float',
		defaultValue: 0
	},{
		name:'zmax',
		type:'float',
		defaultValue: 0
	},{
		name:'zmin',
		type:'float',
		defaultValue: 0
	},{
		name: 'modified',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name:'draggable_data',
		type:'string',
		convert:function(v, record){
			return Ext.String.htmlEncode(Ext.encode({
				id: record.get('cdi_id'),
				name: record.get('cdi_name'),
				synonym: record.get('cdi_synonym'),
				definition: record.get('cdi_definition'),
			}));
		}
	}]
});

Ext.define('RepresentationManager.model.PARTS', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'color',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'opacity',
		type: 'float',
		defaultValue:1.0
	},{
		name: 'remove',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'representation',
		type: 'string',
		defaultValue:'surface'
	},{
		name: 'scalar',
		type: 'float',
		useNull: true,
		defaultValue: null
	},{
		name: 'scalar_flag',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'disabled',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'selected',
		type: 'boolean',
		defaultValue:false
	},

	{
		name: 'art_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_timestamp',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'art_modified',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'art_data_size',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'art_xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('art_xmax')) && Ext.isNumber(r.get('art_xmin'))) v = (r.get('art_xmax')+r.get('art_xmin'))/2;
			return v;
		}
	},{
		name: 'art_ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('art_ymax')) && Ext.isNumber(r.get('art_ymin'))) v = (r.get('art_ymax')+r.get('art_ymin'))/2;
			return v;
		}
	},{
		name: 'art_zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('art_zmax')) && Ext.isNumber(r.get('art_zmin'))) v = (r.get('art_zmax')+r.get('art_zmin'))/2;
			return v;
		}
	},{
		name: 'art_volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_mirroring',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'art_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_category',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_judge',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_class',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arto_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arto_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arto_filename',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cdi_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cmp_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cm_use',
		type: 'boolean',
		defaultValue:true
	},{
		name: 'cm_entry',
		type: 'date',
		dateFormat:'timestamp',
	},{
		name: 'art_filename',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_path',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_tmb_path',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'seg_color',
		useNull: true,
		defaultValue: null,
		type: 'string',
		defaultValue:'#F0D2A0',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = '#F0D2A0';
			return v;
		}
	},{
		name: 'artf_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'artf_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_serial',
		type: 'int'
	},{
		name: 'prefix_id',
		type: 'int'
	},{
		name: 'prefix_char',
		type: 'string'
	},{
		name: 'group_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'group_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'group_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'group',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)){
				return Ext.util.Format.format('{0} : {1}',r.get('group_name'),r.get('group_name_e'));
			}else{
				return v;
			}
		}
	},{
		name: 'current_use',
		type: 'boolean',
		defaultValue: false
	}]
});

Ext.define('RepresentationManager.store.ConceptSegment', {
	extend: 'Ext.data.Store',
	alias: 'store.rmconceptsegment',
	model: 'RepresentationManager.model.CONCEPT_TERM',
	proxy: {
		type: 'ajax',
		url: 'get-zrange-object.cgi',
		extraParams: {
			md_id:1,
//			mv_id:-1,
			crl_id:0,
			degenerate_same_shape_icons:true,
			representation_type: Ext.encode({
				element: true,
				complete_compound: true,
				incomplete_compound: true,
				only_taid: false
			})
		},
		reader: {
			type: 'json',
			root: 'datas'
		}
	}
});

Ext.define('RepresentationManager.store.ConceptTerm', {
	extend: 'Ext.data.Store',
	alias: 'store.rmconceptterm',
	model: 'RepresentationManager.model.CONCEPT_TERM',
	sorters    : [{
		property: 'volume',
		direction: 'DESC'
	}],
	proxy: {
		type: 'ajax',
		url: 'get-zrange-object.cgi',
		extraParams: {
			md_id:1,
//			mv_id:-1,
		},
		reader: {
			type: 'json',
			root: 'datas'
		}
	}
});

Ext.define('RepresentationManager.store.Objs', {
	extend: 'Ext.data.Store',
	alias: 'store.rmobjs',
	model: 'RepresentationManager.model.PARTS',
//	groupField: 'group',
	remoteGroup: false,
	remoteSort: false,
	remoteFilter: false,
	sorters    : [{
		property: 'art_name',
		direction: 'ASC'
	}],
	filters: [{
		property: 'current_use',
		value: true
	}],
	proxy: {
		type: 'ajax',
		timeout: 300000,
		pageParam: undefined,
		startParam: undefined,
		limitParam: undefined,
		filterParam: undefined,
		sortParam: undefined,
		groupDirectionParam: undefined,
		groupParam: undefined,
		extraParams: {
			ci_id: 1,
//			mv_id: -1
			crl_id:0,

			hideChildrenTerm: 1,
//			hideDescendantsTerm: 1,
			hideAncestorTerm: 1,
			hideParentTerm: 1,

//			hidePairTerm: 1,

		},
		api: {
			read    : 'api-upload-file-list.cgi?cmd=read',
			update  : 'api-upload-file-list.cgi?cmd=update_concept_art_map'
		},
		actionMethods : {
			create : 'POST',
			read   : 'POST',
			update : 'POST',
			destroy: 'POST'
		},
		reader: {
			type: 'json',
			root: 'datas',
			totalProperty: 'total',
			listeners: {
				exception : function(){
				}
			}
		},
		writer: {
			type: 'json',
			root: 'datas',
			allowSingle: false,
			encode: true
		}
	}
});

Ext.define('RepresentationManager.Panel.Segment', {
	extend: 'Ext.panel.Panel',
	alias: 'rmsegmentpanel',
	title: 'Segment',
	value: {
		range: 'H',
		segment: 'all',
		volume: '100-inf'
	},
	autoScroll: true,
	tpl: [
'<div id="navigate-segment-content" align="center" class=" ">',
	'<div id="navigate-range-panel-base" class=" x-unselectable">',
		'<div id="navigate-range-panel-base-fx">',
			'<table border="0" cellspacing="0" cellpadding="0" class="range_base" style=""><tbody>',
				'<tr><td align="center">',
					'<table border="0" cellspacing="0" cellpadding="0" class="range_show_only" style="" align="center"><tbody>',
						'<tr>',
							'<td class="range_show_only_label" style="width:25px;display:none;"><label style="display:none;">Show Only</label></td>',
							'<td class="range_show_only_image range_show_only_image_bone" data-segment="bone"><img src="css/Bone_60x60.png"><br>Bone</td>',
							'<td class="range_show_only_image range_show_only_image_muscle" data-segment="muscle"><img src="css/Muscle_60x60.png"><br>Muscle</td>',
							'<td class="range_show_only_image range_show_only_image_vessel" data-segment="vessel"><img src="css/Vessel_60x60.png"><br>Vessel</td>',
							'<td class="range_show_only_image range_show_only_image_internal" data-segment="internal"><img src="css/Internal_60x60.png"><br>Internal</td>',
							'<td class="range_show_only_image range_show_only_image_all" data-segment="all"><img src="css/All_60x60.png"><br>All</td>',
						'</tr>',
					'</tbody></table>',
				'</td></tr>',
				'<tr style="display:none;"><td align="center">',
					'<div style="background:#ffffff;border:1px solid #cccccc;width: 210px;margin:0px auto;padding: 2px;">',
						'<table border="0" cellspacing="0" cellpadding="0" align="center"><tbody>',
							'<tr>',
								'<td valign="top"><input type="checkbox" name="only_taid" id="navigate-segment-only-taid" value="true"></td>',
								'<td valign="top" class="navigate_range_panel_only_taid"><label for="navigate-segment-only-taid" style="font-size:11px;">Show only TA matches(*)</label></td>',
							'</tr>',
							'<tr>',
								'<td valign="top" colspan="2" class="navigate_range_panel_only_taid"><label for="navigate-range-panel-only-taid">* listed in Terminologia Anatomica</label></td>',
							'</tr>',
						'</tbody></table>',
					'</div>',
				'</td></tr>',
				'<tr><td>',
					'<table border="0" cellspacing="0" cellpadding="0" style="border-width:0px;padding:0px;margin:4px;"><tbody>',
						'<tr><td colspan="2"></td><td colspan="5" class="range_BCV_title"><div style="font-weight:bold;margin-bottom:2px;">Volume [cc]</div></td></tr>',
						'<tr class="range_BCV_label">',
							'<td></td><td style="width:4px;"></td>',
							'<td><div>&lt;0.1</div></td>',
							'<td><div>0.1<br>-<br>0.35</div></td>',
							'<td><div>0.35<br>-<br>1</div></td>',
							'<td><div>1<br>-<br>10</div></td>',
							'<td><div>10&lt;</div></td>',
							'<td><div>Any</div></td>',
						'</tr>',
						'<tr>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_border range_border_left range_border_right range_border_top"><tbody>',
									'<tr><td class="range_segment range_segment_label">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">Segment<br>Range</div>',
											'<div class="range_segment range_segment_H"><img src="css/H_50x50.png"></div>',
											'<div class="range_segment range_segment_U"><img src="css/U_50x50.png"></div>',
											'<div class="range_segment range_segment_L"><img src="css/L_50x50.png"></div>',
											'<div class="range_segment_label" style="height:36px;margin:0 0;padding:6px 0 0;"><label>Bridging</label><br><label>more than</label><br><label>one seg.</label></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_right range_border_bottom"><tbody>',
									'<tr><td class="range_segment range_segment_label"><div class="range_segment_base"><div class="range_segment range_segment_ANY">Any</div></div></td></tr>',
								'</tbody></table>',
							'</td>',
							'<td></td>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_top range_segment_inf-01 range_segment_area_O"><tbody>',
									'<tr><td class="range_segment range_segment_inf-01 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">&nbsp;</div>',
											'<div class="range_segment range_segment_H range_value" data-volume="inf-01" data-range="H"></div>',
											'<div class="range_segment range_segment_U range_value" data-volume="inf-01" data-range="U"></div>',
											'<div class="range_segment range_segment_L range_value" data-volume="inf-01" data-range="L"></div>',
											'<div class="range_segment range_segment_O range_value" data-volume="inf-01" data-range="O"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_bottom range_segment_inf-01 range_segment_area_ANY"><tbody>',
									'<tr><td class="range_segment range_segment_inf-01 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment range_segment_ANY range_value" data-volume="inf-01" data-range="ANY"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
							'</td>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_top range_segment_01-1 range_segment_area_O"><tbody>',
									'<tr><td class="range_segment range_segment_01-1 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">&nbsp;</div>',
											'<div class="range_segment range_segment_H range_value" data-volume="01-1" data-range="H"></div>',
											'<div class="range_segment range_segment_U range_value" data-volume="01-1" data-range="U"></div>',
											'<div class="range_segment range_segment_L range_value" data-volume="01-1" data-range="L"></div>',
											'<div class="range_segment range_segment_O range_value" data-volume="01-1" data-range="O"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_bottom range_segment_01-1 range_segment_area_ANY"><tbody>',
									'<tr><td class="range_segment range_segment_01-1 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment range_segment_ANY range_value" data-volume="01-1" data-range="ANY"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
							'</td>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_top range_segment_1-10 range_segment_area_O"><tbody>',
									'<tr><td class="range_segment range_segment_1-10 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">&nbsp;</div>',
											'<div class="range_segment range_segment_H range_value" data-volume="1-10" data-range="H"></div>',
											'<div class="range_segment range_segment_U range_value" data-volume="1-10" data-range="U"></div>',
											'<div class="range_segment range_segment_L range_value" data-volume="1-10" data-range="L"></div>',
											'<div class="range_segment range_segment_O range_value" data-volume="1-10" data-range="O"></div>',
											'</div>',
										'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_left range_border_bottom range_segment_1-10 range_segment_area_ANY"><tbody>',
									'<tr><td class="range_segment range_segment_1-10 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment range_segment_ANY range_value" data-volume="1-10" data-range="ANY"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
							'</td>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_top range_segment_10-100 range_segment_area_O"><tbody>',
									'<tr><td class="range_segment range_segment_10-100 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">&nbsp;</div>',
											'<div class="range_segment range_segment_H range_value" data-volume="10-100" data-range="H"></div>',
											'<div class="range_segment range_segment_U range_value" data-volume="10-100" data-range="U"></div>',
											'<div class="range_segment range_segment_L range_value" data-volume="10-100" data-range="L"></div>',
											'<div class="range_segment range_segment_O range_value" data-volume="10-100" data-range="O"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_bottom range_segment_10-100 range_segment_area_ANY"><tbody>',
									'<tr><td class="range_segment range_segment_10-100 range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment range_segment_ANY range_value" data-volume="10-100" data-range="ANY"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
							'</td>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_top range_segment_100-inf range_segment_area_O"><tbody>',
									'<tr><td class="range_segment range_segment_100-inf range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">&nbsp;</div>',
											'<div class="range_segment range_segment_H range_value" data-volume="100-inf" data-range="H"></div>',
											'<div class="range_segment range_segment_U range_value" data-volume="100-inf" data-range="U"></div>',
											'<div class="range_segment range_segment_L range_value" data-volume="100-inf" data-range="L"></div>',
											'<div class="range_segment range_segment_O range_value" data-volume="100-inf" data-range="O"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_bottom range_segment_100-inf range_segment_area_ANY"><tbody>',
									'<tr><td class="range_segment range_segment_100-inf range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment range_segment_ANY range_value" data-volume="100-inf" data-range="ANY"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
							'</td>',
							'<td align="center" class="">',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_right range_border_top range_segment_any range_segment_area_O"><tbody>',
									'<tr><td class="range_segment range_segment_any range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment_label">&nbsp;</div>',
											'<div class="range_segment range_segment_H range_value" data-volume="any" data-range="H"></div>',
											'<div class="range_segment range_segment_U range_value" data-volume="any" data-range="U"></div>',
											'<div class="range_segment range_segment_L range_value" data-volume="any" data-range="L"></div>',
											'<div class="range_segment range_segment_O range_value" data-volume="any" data-range="O"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
								'<table border="0" cellspacing="0" cellpadding="0" class="range_value range_border range_border_right range_border_bottom range_segment_any range_segment_area_ANY"><tbody>',
									'<tr><td class="range_segment range_segment_any range_value">',
										'<div class="range_segment_base">',
											'<div class="range_segment range_segment_ANY range_value" data-volume="any" data-range="ANY"></div>',
										'</div>',
									'</td></tr>',
								'</tbody></table>',
							'</td>',
						'</tr>',
					'</tbody></table>',
				'</td></tr>',
				'<tr><td>',
					'<table border="0" cellspacing="0" cellpadding="0" class="navigate_range_panel_density" style=""><tbody>',
						'<tr><td><label class=" x-unselectable">Representation Type</label><a href="#"><img src="css/information.png" style="width:12px;height:12px;"></a></td></tr>',
						'<tr><td style="text-align:center;">',
							'<table border="0" cellspacing="0" cellpadding="0" align="center" style="width:230px;text-align:center;"><tbody><tr><td><table border="0" cellspacing="0" cellpadding="0" class="navigate_range_panel_density_item" style=""><tbody>',
								'<tr>',
									'<td><input type="checkbox" name="element" id="navigate-segment-element" value="element" checked=""></td>',
									'<td><label for="navigate-segment-element" class=" x-unselectable">ELEMENT</label>&nbsp;<img src="css/16x16/primitive.png" align="center"></td>',
								'</tr>',
							'</tbody></table>',
						'</td></tr>',
						'<tr><td>',
							'<table border="0" cellspacing="0" cellpadding="0" class="navigate_range_panel_density_item" style=""><tbody>',
								'<tr>',
									'<td><input type="checkbox" name="complete_compound" id="navigate-segment-complete-compound" value="complete-compound" checked=""></td>',
									'<td><label for="navigate-segment-complete-compound" class=" x-unselectable">Complete COMPOUND</label>&nbsp;<img src="css/16x16/100.png" align="center"></td>',
								'</tr>',
							'</tbody></table>',
						'</td></tr>',
						'<tr><td>',
							'<table border="0" cellspacing="0" cellpadding="0" class="navigate_range_panel_density_item" style=""><tbody>',
								'<tr>',
									'<td><input type="checkbox" name="incomplete_compound" id="navigate-segment-incomplete-compound" value="incomplete-compound" checked=""></td>',
									'<td><label for="navigate-segment-incomplete-compound" class=" x-unselectable">Incomplete COMPOUND</label>&nbsp;<img src="css/16x16/075.png" align="center"></td>',
								'</tr>',
							'</tbody></table>',
						'</td></tr>',
					'</tbody></table>',
				'</td></tr>',
			'</tbody></table>',
		'</div>',
	'</div>',
'</div>'
	],

	rangeKeys: ['H','U','L','O','ANY'],
	volumeKeys: ['inf-01','01-1','1-10','10-100','100-inf','ANY'],
	loadingHTML: '<div class="x-grid-tree-loading" style="padding:8px 0 0 2px;"><span class="x-tree-icon" style="padding:16px 0 0 16px;">&nbsp;</span></div>',

	constructor: function(config){
		var self = this;
		self.addEvents('beforeload','load');
		if(Ext.isString(self.tpl) || Ext.isArray(self.tpl)){
			self.tpl = new Ext.XTemplate(self.tpl);
		}
//		self.store = Ext.data.StoreManager.lookup('ConceptSegmentStore') || Ext.create('store.rmconceptsegment', {storeId:'ConceptSegmentStore'});
		self.store = Ext.create('store.rmconceptsegment', {});
//		self.callParent(arguments);
		self.callParent([config]);
	},
	afterRender: function(){
		var self = this;
		console.log('afterRender', self.itemId);
		self.callParent();
		self.update({});

		self.body.query('div#navigate-segment-content input[type=checkbox][name]').forEach(function(dom){
			var elem = Ext.get(dom);
//			console.log(elem.getAttribute('name'),elem.getAttribute('checked'));
			Ext.EventManager.on( elem, 'click', function(e){
				var elem = Ext.get(e.target);
//				console.log(elem.getAttribute('name'),elem.getAttribute('checked'));
				var proxy = self.store.getProxy();
				proxy.extraParams = proxy.extraParams || {};
				if(Ext.isEmpty(proxy.extraParams.representation_type)){
					proxy.extraParams.representation_type = {};
				}else if(Ext.isString(proxy.extraParams.representation_type)){
					proxy.extraParams.representation_type = Ext.decode(proxy.extraParams.representation_type);
				}
				proxy.extraParams.representation_type[elem.getAttribute('name')] = elem.getAttribute('checked') ? true : false;
				proxy.extraParams.representation_type = Ext.encode(proxy.extraParams.representation_type);
				self.loadCounts();

			}, self );
		});
//		self.loadCounts();
	},
	loadCounts: function(){
		var self = this;
		self.load({segment: self.value.segment});
	},
	clickElem: function(e){
		var self = this;
		e.stopEvent();
		var elem = Ext.get(e.target);
//		if(elem.findParent('.range_select')) return;
		if(elem.findParent('.data_select')){
			try{var segment = elem.findParent('td[data-segment]',undefined,true).getAttribute('data-segment');}catch(e){}
			try{var range = elem.findParent('div[data-range]',undefined,true).getAttribute('data-range');}catch(e){}
			try{var volume = elem.findParent('div[data-volume]',undefined,true).getAttribute('data-volume');}catch(e){}
			if(segment){
				self.setValue({segment: segment});
				self.load({segment: segment});
			}else if(range && volume){
				self.setValue({range: range, volume, volume});
				self.load();
			}
		};
	},

	setDegenerateSameShapeIcons: function(degenerate_same_shape_icons){
		var self = this;
		if(!Ext.isBoolean(degenerate_same_shape_icons)) degenerate_same_shape_icons = degenerate_same_shape_icons ? true : false;

		var proxy = self.store.getProxy();
		proxy.extraParams = proxy.extraParams || {};
		if(proxy.extraParams.degenerate_same_shape_icons != degenerate_same_shape_icons){
			proxy.extraParams.degenerate_same_shape_icons = degenerate_same_shape_icons;
			self.load();
		}

	},

	load: function(params){
		var self = this;
		params = params || self.value;

		Ext.Ajax.abortAll();

		self.body.query('td[data-segment]').forEach(function(dom){
			var elem = Ext.get(dom);
			if(elem.hasCls('data_select')){
				elem.removeCls('data_select');
				Ext.EventManager.un( elem, 'click', self.clickElem, self );
			}
		});
		if(params.range && params.volume){
			self.rangeKeys.forEach(function(range){
				self.volumeKeys.forEach(function(volume){
					self.body.query('div.range_value[data-range='+range+'][data-volume='+volume.toLocaleLowerCase()+']').forEach(function(dom){
						var elem = Ext.get(dom);
						if(elem.hasCls('data_select')){
							elem.removeCls('data_select');
							Ext.EventManager.un( elem, 'click', self.clickElem, self );
						}
					});
				});
			});
		}else{
			self.rangeKeys.forEach(function(range){
				self.volumeKeys.forEach(function(volume){
					self.body.query('div.range_value[data-range='+range+'][data-volume='+volume.toLocaleLowerCase()+']').forEach(function(dom){
						var elem = Ext.get(dom);
						elem.setHTML(self.loadingHTML);
						if(elem.hasCls('data_select')){
							elem.removeCls('data_select');
							Ext.EventManager.un( elem, 'click', self.clickElem, self );
						}
					});
				});
			});
			self.setLoading(true);
		}

		self.fireEvent('beforeload', self.store);

		self.deselectAll();
		self.select(params);

		self.store.load({
			params: params,
			callback: function(records,operation,success){
				self.body.query('td[data-segment]').forEach(function(dom){
					var elem = Ext.get(dom);
					elem.addCls('data_select');
					Ext.EventManager.on( elem, 'click', self.clickElem, self );
				});
				if(!(params.range && params.volume)){
					self.rangeKeys.forEach(function(range){
						self.volumeKeys.forEach(function(volume){
							self.body.query('div.range_value[data-range='+range+'][data-volume='+volume.toLocaleLowerCase()+']').forEach(function(dom){
								var elem = Ext.get(dom);
								elem.setHTML('0');
							});
						});
					});
				}
				if(success){
					var json;
					try{json = Ext.decode(operation.response.responseText);}catch(e){}
					if(!Ext.isObject(json)) return;
					if(Ext.isObject(json.counts)){
						Ext.Object.each(json.counts,function(rangeKey,volumes){
							if(!Ext.isObject(volumes)) return true;
							Ext.Object.each(volumes,function(volumeKey, value){
								self.body.query('div.range_value[data-range='+rangeKey+'][data-volume='+volumeKey.toLocaleLowerCase()+']').forEach(function(dom){
									var elem = Ext.get(dom);
									elem.setHTML(value);
									elem.addCls('data_select');
									Ext.EventManager.on( elem, 'click', self.clickElem, self );
								});
							});
						});

						if(Ext.isNumeric(json.ci_id) && Ext.isNumeric(json.cb_id) && Ext.isNumeric(json.md_id) && Ext.isNumeric(json.mv_id)){
							var proxy = self.store.getProxy();
							proxy.extraParams = Ext.apply(proxy.extraParams || {},{
								ci_id: json.ci_id,
								cb_id: json.cb_id,
								md_id: json.md_id,
								mv_id: json.mv_id
							});
						}

						Ext.defer(function(){
							var select_elem = self.select(self.value);
							if(select_elem){
								var e = new Ext.EventObjectImpl();
								e.target = select_elem.dom;
								select_elem.removeCls('range_select');
								self.clickElem(e);
								select_elem.addCls('range_select');
							}
						},0);
					}else if(records && records.length){

						self.rangeKeys.forEach(function(range){
							self.volumeKeys.forEach(function(volume){
								self.body.query('div.range_value[data-range='+range+'][data-volume='+volume.toLocaleLowerCase()+']').forEach(function(dom){
									var elem = Ext.get(dom);
									if(elem.getHTML() != '0'){
										elem.addCls('data_select');
										Ext.EventManager.on( elem, 'click', self.clickElem, self );
									}
								});
							});
						});
					}
				}
				self.setLoading(false);
				self.fireEvent('load', self.store, records, success, operation);
			}
		});
	},
	deselectAll: function(){
		var self = this;
		self.body.select('td.range_select[data-segment]').each(function(elem){elem.removeCls('range_select');});
		self.body.select('div.range_value.range_select').each(function(elem){elem.removeCls('range_select');});
	},
	select: function(value){
		var self = this;
		var select_elem;
		value = value || {};
		if(!Ext.isEmpty(value.range)   && Ext.isString(value.range)   && value.range.trim().length)   value.range   = value.range.trim().toLocaleUpperCase();
		if(!Ext.isEmpty(value.segment) && Ext.isString(value.segment) && value.segment.trim().length) value.segment = value.segment.trim().toLocaleLowerCase();
		if(!Ext.isEmpty(value.volume)  && Ext.isString(value.volume)  && value.volume.trim().length)  value.volume  = value.volume.trim().toLocaleLowerCase();
		if(!Ext.isEmpty(value.segment)) self.body.query('td[data-segment='+value.segment+']').forEach(function(dom){var elem = Ext.get(dom);elem.addCls('range_select');});
		if(!Ext.isEmpty(value.range) && !Ext.isEmpty(value.volume)) self.body.query('div.range_value[data-range='+value.range+'][data-volume='+value.volume+']').forEach(function(dom){select_elem=Ext.get(dom);select_elem.addCls('range_select');});
		return select_elem;
	},
	setValue: function(value){
		var self = this;
		value = value || {};
		self.value = self.value || {};
		if(!Ext.isEmpty(value.range)   && Ext.isString(value.range)   && value.range.trim().length)   self.value.range   = value.range.trim().toLocaleUpperCase();
		if(!Ext.isEmpty(value.segment) && Ext.isString(value.segment) && value.segment.trim().length) self.value.segment = value.segment.trim().toLocaleLowerCase();
		if(!Ext.isEmpty(value.volume)  && Ext.isString(value.volume)  && value.volume.trim().length)  self.value.volume  = value.volume.trim().toLocaleLowerCase();

		self.deselectAll();
		self.select(self.value);

//		self.store.loadPage(1,{
//			params: self.value
//		});
	}
});

Ext.define('RepresentationManager.Panel.Objs', {
	extend: 'Ext.grid.Panel',
//	extend: 'Ext.panel.Panel',
//	extend: 'Ext.panel.Table',
	alias: 'rmobjspanel',
	requires: [
//		'Ext.grid.plugin.BufferedRenderer',
		'Ext.grid.feature.Grouping'
	],
//	title: 'Representation Manager',
	columnLines: true,
//	viewType: 'gridview',

	constructor: function(config){
		var self = this;

		self.FORMAT_FLOAT_NUMBER = '0,0.00';
		self.FORMAT_DATE = 'Y/m/d';
		self.FORMAT_TIME = 'H:i:s';
		self.FORMAT_DATE_TIME = self.FORMAT_DATE+' '+self.FORMAT_TIME;

/**/
//		self.store = Ext.data.StoreManager.lookup('partsStore') || Ext.create('store.rmobjs', {storeId:'partsStore',groupField:'group'});
		if(Ext.isString(config.store)){
			self.store = config.store = Ext.data.StoreManager.lookup(config.store) || Ext.create('store.rmobjs', {storeId:config.store,groupField:'group'});
		}else{
			self.store = Ext.data.StoreManager.lookup('partsStore') || Ext.create('store.rmobjs', {storeId:'partsStore',groupField:'group'});
		}


		self.features = [{
			ftype: 'grouping',
			groupHeaderTpl: [
//				'{name:this.formatName} ({rows.length} obj{[values.rows.length > 1 ? "s" : ""]})',
				'{name:this.formatName}',
				{
					formatName: function(name) {
						return Ext.String.trim(name);
					}
				}
			],
			collapsible: false,
			enableGroupingMenu: false,
			hideGroupedHeader: true,
			startCollapsed: false
		}];
/**/
/*
		if(Ext.isString(config.store)){
			self.store = config.store = Ext.data.StoreManager.lookup(config.store) || Ext.create('store.rmobjs', {storeId:config.store});
		}else{
			self.store = Ext.data.StoreManager.lookup('partsStore') || Ext.create('store.rmobjs', {storeId:'partsStore'});
		}
*/
		self.columns = [
			{xtype: 'rownumberer', text: '#', width: 40},
			{text: '&#160;',            dataIndex: 'selected',     stateId: 'selected',      width: 30, minWidth: 30, hidden: true, hideable: false, sortable: true, draggable: false, resizable: false, xtype: 'agselectedcheckcolumn'},
			{text: AgLang.use,          dataIndex: 'cm_use',       stateId: 'cm_use',        width: 30, minWidth: 30, hidden: false, hideable: false, sortable: true, draggable: false, resizable: false, xtype: 'checkcolumn'},
			{
				text: '&#160;',           dataIndex: 'art_tmb_path',     stateId: 'art_tmb_path',      width: 24, minWidth: 24, hidden: false, hideable: false, sortable: true, draggable: false, resizable: false,
				renderer: function(value,metaData,record,rowIndex,colIndex,store,view){
					if(record.get('seg_color')){
//						metaData.style = 'background:'+record.get('seg_color')+';';
					}
					metaData.innerCls = 'art_tmb_path';
					return value;
				}
			},
			{text: AgLang.art_id,       dataIndex: 'art_id',       stateId: 'art_id',        width: 54, minWidth: 54, hidden: false, hideable: true},
			{text: AgLang.cdi_name,     dataIndex: 'cdi_name',     stateId: 'cdi_name',      width: 70, minWidth: 70, hidden: false,  hideable: true, xtype: 'agcolumncdiname' },
			{text: AgLang.cdi_name_e,   dataIndex: 'cdi_name_e',   stateId: 'cdi_name_e',    flex: 2.0, minWidth: 80, hidden: false, hideable: true, xtype: 'agcolumncdinamee' },
			{text: AgLang.category,     dataIndex: 'arta_category',stateId: 'arta_category', flex: 1.0, minWidth: 50, hidden: true, hideable: true},
			{text: AgLang.class_name,   dataIndex: 'arta_class',   stateId: 'arta_class',    width: 36, minWidth: 36, hidden: true, hideable: true},
			{text: AgLang.comment,      dataIndex: 'arta_comment', stateId: 'arta_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true},
			{text: AgLang.judge,        dataIndex: 'arta_judge',   stateId: 'arta_judge',    flex: 1.0, minWidth: 50, hidden: true, hideable: true},

			{text: AgLang.arto_id,      dataIndex: 'arto_id',      stateId: 'arto_id',       width: 60, minWidth: 60, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_filename,dataIndex: 'arto_filename',stateId: 'arto_filename', flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},
			{text: AgLang.arto_comment, dataIndex: 'arto_comment', stateId: 'arto_comment',  flex: 2.0, minWidth: 80, hidden: true, hideable: true, sortable: false},

			{text: 'Color',             dataIndex: 'color',        stateId: 'color',         width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcolorcolumn'},
			{text: 'Opacity',           dataIndex: 'opacity',      stateId: 'opacity',       width: 44, minWidth: 44, hidden: true,  hideable: false,  xtype: 'agopacitycolumn'},
			{text: 'Hide',              dataIndex: 'remove',       stateId: 'remove',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agcheckcolumn'},
			{text: 'Scalar',            dataIndex: 'scalar',       stateId: 'scalar',        width: 40, minWidth: 40, hidden: true,  hideable: false,  xtype: 'agnumbercolumn', format: '0', editor: 'numberfield'},

			{text: AgLang.file_name,    dataIndex: 'art_filename', stateId: 'art_filename',  flex: 2.0, minWidth: 80, hidden: true, hideable: true},
			{text: 'Path',              dataIndex: 'art_path',     stateId: 'art_path',      flex: 1.0, minWidth: 50, hidden: true,  hideable: false},
			{text: AgLang.file_size,    dataIndex: 'art_data_size',stateId: 'art_data_size', width: 59,  hidden: true, hideable: true, xtype: 'agfilesizecolumn'},

			{text: AgLang.xmax,         dataIndex: 'art_xmax',     stateId: 'art_xmax',      width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xmin,         dataIndex: 'art_xmin',     stateId: 'art_xmin',      width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.xcenter,      dataIndex: 'art_xcenter',  stateId: 'art_xcenter',   width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymax,         dataIndex: 'art_ymax',     stateId: 'art_ymax',      width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ymin,         dataIndex: 'art_ymin',     stateId: 'art_ymin',      width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.ycenter,      dataIndex: 'art_ycenter',  stateId: 'art_ycenter',   width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmax,         dataIndex: 'art_zmax',     stateId: 'art_zmax',      width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zmin,         dataIndex: 'art_zmin',     stateId: 'art_zmin',      width: 77,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.zcenter,      dataIndex: 'art_zcenter',  stateId: 'art_zcenter',   width: 77,  hidden: false, hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},
			{text: AgLang.volume,       dataIndex: 'art_volume',   stateId: 'art_volume',    width: 76,  hidden: true,  hideable: true, xtype: 'agnumbercolumn', format: self.FORMAT_FLOAT_NUMBER},

//			{text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: 112, hidden: true,  hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE_TIME }
			{text: AgLang.timestamp,    dataIndex: 'art_timestamp',stateId: 'art_timestamp', width: 67, hidden: false,  hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE }
//			{text: AgLang.cm_entry,     dataIndex: 'cm_entry',     stateId: 'cm_entry',      width: 112, hidden: false, hideable: true, xtype: 'datecolumn',     format: self.FORMAT_DATE }
		];

		self.viewConfig = self.viewConfig || {};
		self.viewConfig.stripeRows = true;
		self.viewConfig.loadMask = false;

		self.plugins = Ext.create('Ext.grid.plugin.BufferedRenderer',{
			pluginId: 'bufferedrenderer',
			trailingBufferZone: 20,
			leadingBufferZone: 50
		});

		self.dockedItems = [{
			xtype: 'toolbar',
			dock: 'top',
			items: [{
				hidden: false,
				disabled: true,
				xtype: 'button',
				itemId: 'cancel',
				iconCls: 'cancel',
				text: 'cancel',
				listeners: {
					afterrender: function(field){
						var gridpanel = field.up('gridpanel');
						var store = field.up('gridpanel').getStore();
						store.on({
							update: {
								fn: function(store, eOpts){
									field.setDisabled(Ext.isEmpty(store.getModifiedRecords()));
								},
								buffer : 100
							}
						});
					},
					click: function(b){
						var gridpanel = b.up('gridpanel');
						var store = gridpanel.getStore();
						store.rejectChanges();
					}
				}
			},'-','->','-',{
				hidden: false,
				disabled: true,
				xtype: 'button',
				itemId: 'submit',
				iconCls: 'submit',
				text: 'submit',
				listeners: {
					afterrender: function(field){
						var gridpanel = field.up('gridpanel');
						var store = field.up('gridpanel').getStore();
						store.on({
							update: {
								fn: function(store, eOpts){
									field.setDisabled(Ext.isEmpty(store.getModifiedRecords()));
								},
								buffer : 100
							}
						});
					},
					disable: function(b,eOpts){
						self.fireEvent('disable', self);
					},
					enable: function(b,eOpts){
						self.fireEvent('enable', self);
					},
					click: function(field){
						var gridpanel = field.up('gridpanel');
						var store = gridpanel.getStore();
						var proxy = store.getProxy();
						proxy.extraParams = proxy.extraParams || {};


						field.setIconCls('loading-btn');
						field.setDisabled(true);
						gridpanel.setLoading(true);
						store.sync({
							callback: function(batch,options){
								field.setIconCls('submit');
								field.setDisabled(false);
								gridpanel.setLoading(false);
							},
							success: function(batch,options){
								store.reload();
							},
							failure: function(batch,options){
								var msg = AgLang.error_submit;
								var proxy = this;
								var reader = proxy.getReader();
								if(reader && reader.rawData && reader.rawData.msg){
									msg += ' ['+reader.rawData.msg+']';
								}
								Ext.Msg.show({
									title: field.text || 'submit',
									iconCls: 'submit',
									msg: msg,
									buttons: Ext.Msg.OK,
									icon: Ext.Msg.ERROR,
									fn: function(buttonId,text,opt){
									}
								});
							}
						});

					}
				}
			},'-',{
				xtype: 'tbtext',
				text: '- objs',
				listeners: {
					afterrender: function(field){
						var gridpanel = field.up('gridpanel');
						var store = field.up('gridpanel').getStore();
						store.on({
							datachanged: {
								fn: function(store, eOpts){
									var count = store.getCount();
									field.setText((count>0?count:'-')+' objs');
								}
							}
						});
					}
				}
			}]
		}];

//		self.callParent(arguments);
		self.callParent([config]);
	},
	afterRender: function(){
		var self = this;
		console.log('afterRender', self.itemId);
		self.callParent();
		if(Ext.isChrome){
			self.columns.forEach(function(c){if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)) c.autoSize()});
			self.store.on({
				load: {
					fn: function(){
						self.columns.forEach(function(c){
							if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)){
								c.autoSize();
							}else if(c.getXType() === 'rownumberer'){
								c.autoSize();
							}
						});
					},
					buffer: 0
				}
			});
		}
	},
	isSubmitDisabled: function(){
		var self = this;
		return self.down('#submit').isDisabled()
	}
});

Ext.define('RepresentationManager.View.ConceptTerm', {
	extend: 'Ext.view.View',
	alias: 'rmconcepttermview',
	title: 'Data',
	itemSelector: 'div.thumb-wrap',
	emptyText: 'No images available',
	overflowX: 'hidden',
	overflowY: 'auto',
	constructor: function(config){
		var self = this;

//		self.store = Ext.data.StoreManager.lookup('ConceptTermStore') || Ext.create('store.rmconceptterm', {storeId:'ConceptTermStore'});
//		self.store = Ext.create('store.rmconceptterm', {storeId:'ConceptTermStore'});
		self.store = Ext.create('store.rmconceptterm',{});

		self.tpl = new Ext.XTemplate(
			'<tpl for=".">',
				'<div class="thumb-wrap x-unselectable" draggable="true" data-draggable="{draggable_data}">',
					'<div class="thumb" style="background-color:{bgcolor};">',
						'<img src="{src}" width=120 height=120 alt="{alt}"/>',
						'<div class="thumb-density"><img src="{density_icon}"></div>',
					'</div>',
					'<div class="thumb-shortname">',
						'<span>{caption}</span>',
					'</div>',
				'</div>',
			'</tpl>'
		);

//		self.callParent(arguments);
		self.callParent([config]);

		self.store.on({
			load: function(){
			},
			add: function(store, records, index, eOpts){
				if(Ext.isEmpty(records)) return;
				self.getSelectionModel().select(store.getAt(0));
			}
		});
	},
	afterRender: function(){
		var self = this;
		console.log('afterRender', self.itemId);
		self.callParent();
/**/
		self.tip = Ext.create('Ext.tip.ToolTip', {
			target: self.el,
			delegate: self.itemSelector,
			trackMouse: true,
			renderTo: Ext.getBody(),
			tpl: [
				'<table><tbody>',
				'<tr><td>id</td><td>:</td><td>{cdi_id}</td></tr>',
				'<tr><td>name</td><td>:</td><td>{cdi_name}</td></tr>',
				'<tr><td>density</td><td>:</td><td>{density}%</td></tr>',
				'<tr><td>volume</td><td>:</td><td>{volume}cc</td></tr>',
				'<tr><td>z max</td><td>:</td><td>{zmax}mm</td></tr>',
				'<tr><td>z min</td><td>:</td><td>{zmin}mm</td></tr>',
				'<tr><td>last modified</td><td>:</td><td>{modified}</td></tr>',
				'</tbody></table>',
			],
			listeners: {
				beforeshow: function updateTipBody(tip) {
					var record = self.getRecord(tip.triggerElement);
//					self.tip.update('Over term "' + record.get('cdi_name') + '"' + ',<br/>density:'+ Math.round(record.get('density')*100) + '%');
					var data = record.getData();
					self.tip.update({
						cdi_id:   data.cdi_id,
						cdi_name: data.cdi_name,
						volume:   data.volume,
						zmax:     data.zmax,
						zmin:     data.zmin,
						density:  Math.round(data.density*10000)/100,
						zmin:     data.zmin,
						modified: Ext.Date.format(data.modified, 'Y-m-d')
					});
				}
			}
		});
/**/
	}
});

Ext.define('RepresentationManager.Panel.Data', {
	extend: 'Ext.panel.Panel',
	alias: 'rmdataspanel',
	title: 'Data',
	layout: 'fit',
	autoScroll: false,
	bodyStyle: 'padding:0px;',
	constructor: function(config){
		var self = this;
//		self.rmconcepttermview = Ext.create('rmconcepttermview',{id:config.id+'-rmconcepttermview', itemId:'rmconcepttermview'});
		self.rmconcepttermview = Ext.create('rmconcepttermview',{});
		self.items = self.rmconcepttermview;
		self.dockedItems = [{
			xtype: 'toolbar',
			dock: 'top',
			items: [{
				xtype: 'combobox',
				store: Ext.create('Ext.data.Store', {
					storeId: 'ImageSizeStore',
					model: 'RepresentationManager.model.IMAGE_SIDE',
					data : RepresentationManager.CurrentImageSide.getData(),
				}),
				fieldLabel: 'view',
				labelWidth: 24,
				width: 100,
				editable: false,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				value: RepresentationManager.CurrentImageSide.get(),
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						RepresentationManager.CurrentImageSide.set(newValue);
						var store = self.getStore();
						store.suspendEvent('update');
						try{
							store.each(function(record){
								var img_paths = record.get('img_paths');
								record.beginEdit();
								record.set('src',img_paths['imgsM'][newValue]);
								record.commit(false,['src']);
								record.endEdit(false,['src']);
							});
						}catch(e){
							console.error(e);
						}
						store.resumeEvent('update');
						self.rmconcepttermview.refresh();
					}
				}
			},'-',{
				itemId: 'sort_property',
				xtype: 'combobox',
				store: Ext.create('Ext.data.Store', {
					storeId: 'SortPropertyStore',
					model: 'RepresentationManager.model.DATA_COMBOBOX_MODEL',
					data : [
						{'value':'cdi_id', 'display':'Concept ID'},
						{'value':'cdi_name', 'display':'Concept name'},
						{'value':'density', 'display':'Density'},
						{'value':'volume', 'display':'Volume'},
						{'value':'zmax', 'display':'Z max'},
						{'value':'zmin', 'display':'Z min'},
						{'value':'modified', 'display':'last modified'}
					]
				}),
				fieldLabel: 'sort by',
				labelWidth: 38,
				width: 150,
				editable: false,
				queryMode: 'local',
				displayField: 'display',
				valueField: 'value',
				value: 'volume',
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						var direction = field.next('#sort_direction').getValue();
						if(newValue=='density'){
							self.getStore().sort([{
								property: 'density',
								direction: direction
							},{
								property: 'volume',
								direction: direction
							}]);
						}else{
							self.getStore().sort(newValue,direction);
						}
					}
				}
			},{
				itemId: 'sort_direction',
				xtype: 'combobox',
				store: Ext.create('Ext.data.Store', {
					storeId: 'SortDirectionStore',
					model: 'RepresentationManager.model.DATA_COMBOBOX_MODEL',
					data : [
						{'value':'ASC', 'display':'ASC'},
						{'value':'DESC', 'display':'DESC'}
					]
				}),
				hideLabel: true,
				width: 56,
				editable: false,
				queryMode: 'local',
				displayField: 'value',
				valueField: 'value',
				value: 'DESC',
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						var sort_property = field.prev('#sort_property');
						sort_property.fireEvent('change',sort_property,sort_property.getValue());
					}
				}
			},'-',{
				xtype: 'checkboxfield',
				boxLabel: 'Show only Unique models',
				checked: true,
				listeners: {
					change: function( field, newValue, oldValue, eOpts ){
						console.log(newValue);
						self.fireEvent('changedegeneratesameshapeicons', self, newValue, oldValue, eOpts );
					}
				}
			},'-','->','-',{
				xtype: 'tbtext',
				text: '- models',
				listeners: {
					afterrender: function(field){
						self.rmconcepttermview.store.on({
							datachanged: {
								fn: function(store, eOpts){
									var count = store.getCount();
									field.setText((count>0?count:'-')+' models');
								}
							}
						});
					}
				}
			}]
		}];

		self.callParent([config]);

		self.rmconcepttermview.on({
			selectionchange: function(view, selected, eOpts){
				self.fireEvent('selectionchange', view, selected, eOpts);
			},
			itemdblclick: function(view, record, item, index, e, eOpts){
				if(record.get('primitive')) return;
				self.fireEvent('itemdblclick', view, record, item, index, e, eOpts);
			}
		});
	},
	afterRender: function(){
		var self = this;
		console.log('afterRender', self.itemId);
		self.callParent();
	},
	getStore: function(){
		var self = this;
		return self.rmconcepttermview.store;
	}
});

Ext.define('RepresentationManager.Viewport', {
	extend: 'Ext.container.Viewport',
	alias: 'rmviewport',
	layout: 'border',
//	layout: {
//		type: 'hbox',
//		align: 'stretch'
//	},
	autoScroll: false,
	constructor: function(config){
		var self = this;
		config = config || {};
		config.id = config.id || Ext.id();

		self.rmsegmentpanel = Ext.create('rmsegmentpanel',{
			id: config.id+'-rmsegmentpanel',
			itemId: 'rmsegmentpanel',
			width: 286,
//				flex: 1,
//				minWidth: 286,
//				split:true,
//			resizable: false,
//			collapseDirection: Ext.Component.DIRECTION_LEFT,
//			collapsible:true
		});

		self.rmnavigatepanel = Ext.create('Ext.panel.Panel',{
			layout: 'fit',
//		self.rmnavigatepanel = Ext.create('Ext.tab.Panel',{
			id: config.id+'-rmnavigatetabpanel',
			itemId: 'rmnavigatetabpanel',
			title: 'navigate',
			region:'west',
			width: 286,
			minWidth: 286,
			split:true,
			resizable: false,
			collapseDirection: 'left',
			collapsible:true,
			items: [
				self.rmsegmentpanel
			]
		});

		self.rmdataspanel = Ext.create('rmdataspanel',{
			id: config.id+'-rmdataspanel',
			itemId: 'rmdataspanel'
		});

		self.rmdatastabpanel = Ext.create('Ext.tab.Panel',{
			id: config.id+'-rmdatastabpanel',
			itemId: 'rmdatastabpanel',
			region:'center',
			flex: 3,
			minWidth:286,
			minHeight:200,
			items: [
				self.rmdataspanel
			],
			listeners: {
				afterrender: function(tabpanel){
					self.rmdataspanel.on({
						selectionchange: function(view, selected, eOpts){
							self.rmdatastabpanel.fireEvent('selectionchange', view, selected, eOpts);
						},
						itemdblclick: function(view, record, item, index, e, eOpts){
							self.rmdatastabpanel.fireEvent('itemdblclick', view, record, item, index, e, eOpts);
						},
						changedegeneratesameshapeicons: function(field, newValue, oldValue, eOpts){
							self.rmdatastabpanel.fireEvent('changedegeneratesameshapeicons', field, newValue, oldValue, eOpts);
						}
					});
				},
				itemdblclick: function(view, record, item, index, e, eOpts){
					console.log('itemdblclick', view, record, item, index, e, eOpts);
					var cdi_id = record.get('cdi_id');
					var title = Ext.util.Format.format('{0} : {1}',record.get('cdi_id'),record.get('cdi_name'));
					var panel_id = cdi_id+'-rmdatastabpanel';
					var panel = self.rmdatastabpanel.down('#'+panel_id);
					if(Ext.isEmpty(panel)){
						panel = Ext.create('rmdataspanel',{itemId:panel_id, title:title, closable:true});
						self.rmdatastabpanel.add(panel);
						panel.on({
							selectionchange: function(view, selected, eOpts){
								self.rmdatastabpanel.fireEvent('selectionchange', view, selected, eOpts);
							},
							itemdblclick: function(view, record, item, index, e, eOpts){
								self.rmdatastabpanel.fireEvent('itemdblclick', view, record, item, index, e, eOpts);
							},
							changedegeneratesameshapeicons: function(field, newValue, oldValue, eOpts){
//								self.rmdatastabpanel.fireEvent('changedegeneratesameshapeicons', field, newValue, oldValue, eOpts);

								field.getStore().load({
									params: {
										cdi_id: cdi_id,
										degenerate_same_shape_icons: newValue
									}
								});
							}
						});
						panel.getStore().load({
							params: {
								cdi_id: cdi_id,
								degenerate_same_shape_icons: true
							}
						});
					}
					if(panel) self.rmdatastabpanel.setActiveTab(panel);
				}
			}
		});

		self.rmobjspanel = Ext.create('rmobjspanel',{
//			title: 'Representation Manager',
//			id: config.id+'-rmobjspanel',
//			itemId: 'rmobjspanel',
//			region:'south',
			flex: 1,
//			minWidth:286,
//			minHeight: 200,
//			split:true,
//			collapseDirection: 'bottom',//Ext.Component.DIRECTION_BOTTOM,
//			collapsible:true,
			store: 'partsStore'
		});
//		self.rmobjspanel.on({
//			disable: function(){
//				self.rmsegmentpanel.setDisabled(false);
//				self.rmdatastabpanel.setDisabled(false);
//			},
//			enable: function(){
//				self.rmsegmentpanel.setDisabled(true);
//				self.rmdatastabpanel.setDisabled(true);
//			}
//		});

		self.rmobjspanel2 = Ext.create('rmobjspanel',{
//			title: 'Representation Manager',
//			id: config.id+'-rmobjspanel',
//			itemId: 'rmobjspanel',
//			region:'south',
			flex: 1,
//			minWidth:286,
//			minHeight: 200,
//			split:true,
//			collapseDirection: 'bottom',//Ext.Component.DIRECTION_BOTTOM,
//			collapsible:true
			store: 'partsStore2',
			hidden: true
		});
//		self.rmobjspanel2.on({
//			disable: function(){
//				self.rmsegmentpanel.setDisabled(false);
//				self.rmdatastabpanel.setDisabled(false);
//			},
//			enable: function(){
//				self.rmsegmentpanel.setDisabled(true);
//				self.rmdatastabpanel.setDisabled(true);
//			}
//		});

		self.rmobjsvboxpanel = Ext.create('Ext.panel.Panel', {
			title: 'Representation Manager',
			region:'south',
			flex: 1,
			minWidth:286,
			minHeight: 200,
			split:true,
			collapseDirection: 'bottom',//Ext.Component.DIRECTION_BOTTOM,
			collapsible:true,
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
			items:[
				self.rmobjspanel,
				self.rmobjspanel2
			]
		});
		self.rmobjsvboxpanel.on({
			resize: {
				fn: function(panel, width, height, oldWidth, oldHeight, eOpts){
					if(panel.flex){
						panel.setHeight(height);
						delete panel.flex;
					}
				},
				single: true
			}
		});
		self.rmobjspanel.on({
			disable: function(){
				if(self.rmobjspanel.isSubmitDisabled() && self.rmobjspanel2.isSubmitDisabled()){
					self.rmsegmentpanel.setDisabled(false);
					self.rmdatastabpanel.setDisabled(false);
				}else{
					self.rmsegmentpanel.setDisabled(true);
					self.rmdatastabpanel.setDisabled(true);
				}
			},
			enable: function(){
				if(self.rmobjspanel.isSubmitDisabled() && self.rmobjspanel2.isSubmitDisabled()){
					self.rmsegmentpanel.setDisabled(false);
					self.rmdatastabpanel.setDisabled(false);
				}else{
					self.rmsegmentpanel.setDisabled(true);
					self.rmdatastabpanel.setDisabled(true);
				}
			}
		});
		self.rmobjspanel2.on({
			disable: function(){
				if(self.rmobjspanel.isSubmitDisabled() && self.rmobjspanel2.isSubmitDisabled()){
					self.rmsegmentpanel.setDisabled(false);
					self.rmdatastabpanel.setDisabled(false);
				}else{
					self.rmsegmentpanel.setDisabled(true);
					self.rmdatastabpanel.setDisabled(true);
				}
			},
			enable: function(){
				if(self.rmobjspanel.isSubmitDisabled() && self.rmobjspanel2.isSubmitDisabled()){
					self.rmsegmentpanel.setDisabled(false);
					self.rmdatastabpanel.setDisabled(false);
				}else{
					self.rmsegmentpanel.setDisabled(true);
					self.rmdatastabpanel.setDisabled(true);
				}
			}
		});



		self.rmvboxpanel = Ext.create('Ext.panel.Panel', {
			region:'center',
			flex: 3,
			minWidth: 200,
			xtype: 'panel',
			id: config.id+'-rmvboxpanel',
			itemId: 'rmvboxpanel',
			layout: 'border',
/*
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
*/
			items:[
				self.rmdatastabpanel,
				self.rmobjsvboxpanel
			]
		});

		self.items = [
//			self.rmsegmentpanel,
			self.rmnavigatepanel,
			self.rmvboxpanel
		];

		self.rmsegmentpanel.on({
			beforeload: function(){
				self.rmvboxpanel.setLoading(true);
				var store = self.rmdataspanel.getStore();
				if(store) store.removeAll(false);
			},
			load: function(store, records, success, operation){
				self.rmvboxpanel.setLoading(true);
				Ext.defer(function(){
					var store = self.rmdataspanel.getStore();
					if(store){
						if(Ext.isArray(records)){
							store.removeAll(false);
							store.add(records.map(function(record){return record.getData();}));
						}else{
							store.removeAll();
						}
					}
					self.rmvboxpanel.setLoading(false);
					self.rmdatastabpanel.setActiveTab(self.rmdataspanel);
				},100);
			}
		});

		self.rmdatastabpanel.on({
			selectionchange: function(view, selected, eOpts){
//				self.rmobjspanel2.hide();
				var store = self.rmobjspanel.getStore();
				if(Ext.isEmpty(selected)){
//					self.rmobjspanel.collapse();
					store.loadData([]);
					self.rmobjspanel2.hide();
					return;
				}
				Ext.Ajax.abortAll();
//				self.rmobjspanel.expand(true);
				self.rmobjsvboxpanel.setLoading(true);
				var cdi_name = selected[0].get('cdi_id');
				store.load({
					params: {
						cdi_name: cdi_name
					},
					callback: function(records,operation,success){
//						Ext.defer(function(){
							store.clearFilter(true);
							store.filter([{
								filterFn: function(item){
									return item.get('group_name') !== cdi_name;
								}
							},{
								property: 'current_use',
								value: true
							}]);
							var pair_records = store.getRange();
							store.clearFilter();
							store.filter([{
								property: 'current_use',
								value: true
							}]);

							self.rmobjspanel2.hide();
							if(pair_records.length){
								store.remove(pair_records);
								var org_records = store.getRange().map(function(record){return record.getData();});
								store.removeAll();
								store.add(org_records);
								store.commitChanges();
								console.log(store.getCount());

								self.rmobjspanel2.show();
								self.rmobjspanel2.getView().refresh();

								var store2 = self.rmobjspanel2.getStore();
								store2.removeAll();
								store2.add(pair_records.map(function(record){return record.getData();}));
								store2.commitChanges();
								console.log(store2.getCount());

//								self.rmobjspanel2.show();
//								self.rmobjspanel2.getView().refresh();

								if(Ext.isChrome){
									self.rmobjspanel2.columns.forEach(function(c){
										if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)){
											c.autoSize();
										}else if(c.getXType() === 'rownumberer'){
											c.autoSize();
										}
									});
								}

							}else{
							}
							if(Ext.isChrome){
								self.rmobjspanel.columns.forEach(function(c){
									if(!c.hidden && c.resizable && Ext.isEmpty(c.flex)){
										c.autoSize();
									}else if(c.getXType() === 'rownumberer'){
										c.autoSize();
									}
								});
							}

							self.rmobjsvboxpanel.setLoading(false);
//						},250);
					}
				});
			},
			changedegeneratesameshapeicons: function(field, newValue, oldValue, eOpts){
				self.rmsegmentpanel.setDegenerateSameShapeIcons(newValue);
			}
		});

		self.rmobjsvboxpanel.on({
			afterrender: function(){
				self.rmsegmentpanel.loadCounts();
			}
		});

		self.callParent([config]);

	},
	afterRender: function(){
		var self = this;
		console.log('afterRender', self.itemId);
		self.callParent();
	}
});

Ext.define('RepresentationManager.CurrentImageSide', {
	singleton: true,
	config: {
		currentImageSide: 1,
		imageSideData:  [
			{'value':0, 'display':'Rotate'},
			{'value':1, 'display':'Front'},
			{'value':3, 'display':'Back'},
			{'value':2, 'display':'Left'},
			{'value':4, 'display':'Right'}
		]
	},
	constructor: function(config){
		var self = this;
		config = config || {};
		self.initConfig(config);
	},
	get: function(){
		var self = this;
		return self.getCurrentImageSide();
	},
	set: function(imageSide){
		var self = this;
		return self.setCurrentImageSide(imageSide);
	},
	getData: function(){
		var self = this;
		return self.getImageSideData();
	},
});

Ext.onReady(function() {
	Ext.QuickTips.init();
//	console.log('onReady()');
	var app = new RepresentationManager();

	$(document).on('dragstart','*[draggable],*[draggable] img',function(e){
		e.originalEvent.dataTransfer.effectAllowed = 'copy';
		var draggable_data = $(this).closest('.thumb-wrap').attr('data-draggable');
		if(Ext.isEmpty(draggable_data)) return false;
		if(Ext.isArray(draggable_data) || Ext.isObject(draggable_data)) draggable_data = Ext.encode(draggable_data);
		if(!Ext.isString(draggable_data)) return false;
		e.originalEvent.dataTransfer.clearData();
		e.originalEvent.dataTransfer.setData('text/plain', draggable_data);
		e.stopPropagation();
	});

});
