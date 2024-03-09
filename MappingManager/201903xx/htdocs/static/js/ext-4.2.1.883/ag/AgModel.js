Ext.define('PARTS', {
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
		name: 'art_upload_modified',
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
		name: 'artl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'artl_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artc_id',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			if(Ext.isEmpty(value)) return record.get('art_id');
			return value;
		}
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
		name: 'cd_exists',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'cmp_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cp_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cl_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cm_use',
		type: 'boolean',
		defaultValue:true
	},{
		name: 'current_use',
		type: 'boolean',
		defaultValue:true
	},{
		name: 'current_use_reason',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'never_current',
		type: 'boolean',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = !r.get('cm_use');
			return v;
		}
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
		name: 'seg_name',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isString(v)) v = v.toUpperCase();
			return v;
		}
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
		name: 'artf_names',
		useNull: true,
		defaultValue: null,
		type: 'auto'
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
		name: 'depth',
		type: 'int'
	},
	{
		name: 'is_exists',
		defaultValue: false,
		type: 'boolean'
	},{
		name: 'is_virtual',
		defaultValue: false,
		type: 'boolean'
	},{
		name: 'virtual_current_use',
		useNull: true,
		defaultValue: null,
		type: 'boolean'
	},{
		name: 'virtual_current_use_reason',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'virtual_cm_use',
		useNull: true,
		defaultValue: null,
		type: 'boolean'
	},{
		name: 'virtual_never_current',
		useNull: true,
		defaultValue: null,
		type: 'boolean'
	},{
		name: 'virtual_cdi_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: 'cm_edited',
		defaultValue: false,
		type: 'boolean'
	}]
});

Ext.define('FMA', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'wait',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'loaded',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'visibled',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'selected',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'focused',
		type: 'boolean',
		useNull: true,
		defaultValue: null
	},{
		name: 'disabled',
		type: 'boolean',
		defaultValue:false,
		convert: function(v,r){
			return r.get('art_num')===0;
		}
	},

	{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cdi_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name_j',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name_k',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name_l',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.data.art_xmax) && Ext.isNumber(r.data.art_xmin)) v = (r.data.art_xmax + r.data.art_xmin)/2;
			return v;
		}
	},{
		name: 'art_ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.data.art_ymax) && Ext.isNumber(r.data.art_ymin)) v = (r.data.art_ymax + r.data.art_ymin)/2;
			return v;
		}
	},{
		name: 'art_zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'art_zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.data.art_zmax) && Ext.isNumber(r.data.art_zmin)) v = (r.data.art_zmax + r.data.art_zmin)/2;
			return v;
		}
	},{
		name: 'art_num',
		type: 'int',
//		useNull: true,
//		defaultValue: null
		defaultValue: 0
	},{
		name: 'art_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	}]
});

Ext.define('PALLETPARTS', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'sortname',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'color',
		mapping: 'Color',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'opacity',
		mapping: 'Opacity',
		type: 'float',
		defaultValue:1.0
	},{
		name: 'remove',
		mapping: 'Hide',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'focused',
		type: 'boolean',
		useNull: true,
		defaultValue: null
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
		name: 'art_volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
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
		name: 'seg_name',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isString(v)) v = v.toUpperCase();
			return v;
		}
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
		name: 'selected',
		type: 'boolean',
		defaultValue:true
	},

	{
		name: 'art_id',
		mapping : 'FJID',
		sortType: 'asFJID',
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
		mapping : 'FMAID',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name_e',
		mapping : 'Name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_comment',
		mapping: 'Comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_comment',
		mapping: 'Comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_class',
		mapping: 'Class',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_category',
		mapping: 'Category',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arta_judge',
		mapping: 'Judge',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'artl_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artc_id',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			if(Ext.isEmpty(value)) return record.get('art_id');
			return value;
		}
	},{
		name: 'cm_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_data_size',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'art_filename',
		mapping: 'Filename',
		useNull: true,
		defaultValue: null,
		type: 'string'

	},{
		name: 'artf_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'artf_name',
		mapping: 'Folder',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_timestamp',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'art_upload_modified',
		type: 'date',
		dateFormat:'timestamp'
	},

	{
		name: 'arto_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arto_filename',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'arto_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}

	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cm_entry',
		type: 'date',
		dateFormat:'timestamp',
	}
	,{
		name: 'art_serial',
		type: 'int'
	},{
		name: 'prefix_id',
		type: 'int'
	},{
		name: 'prefix_char',
		type: 'string'
	}
	,{
		name: 'target_record',
		defaultValue: false,
		type: 'boolean'
	}

	,{
		name: 'current_use',
		type: 'boolean',
		defaultValue:true
	}
	,{
		name: 'current_use_reason',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: 'cm_edited',
		defaultValue: false,
		type: 'boolean'
	}

	]
});

Ext.define('OBJ_EDIT', {
	extend: 'PALLETPARTS',
	fields: [{
		name: 'mirror',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'mirror_same_concept',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'mirror_cdi_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mirror_cdi_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mirror_cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'mirror_type',
		defaultValue: 'mirror',
		type: 'string'
	},{
		name: 'mirror_art_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}]
});

Ext.define('PREFIX', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'display',
		type: 'string'
	},{
		name: 'value',
		type: 'string'
	},{
		name: 'prefix_id',
		type: 'int'
	},{
		name: 'prefix_char',
		type: 'string'
	}]
});

Ext.define('CONCEPT_INFO', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'display',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'value',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_name',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_order',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_use',
		type: 'boolean',
		defaultValue: false
	}]
});
Ext.define('CONCEPT_BUILD', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'display',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'value',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_name',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_name',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_comment',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_release',
		type: 'date',
		dateFormat:'timestamp',
		useNull: true,
		defaultValue: null,
		serialize: function(v,rec){
			return Ext.Date.format(v, 'Y-m-d');
		}
	},{
		name: 'cb_order',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_use',
		type: 'boolean',
		defaultValue: false
	}]
});

Ext.define('VERSION', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'display',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'value',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'version',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'md_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'md_name_e',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'md_abbr',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_entry',
		type: 'date',
		dateFormat:'timestamp',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_modified',
		type: 'date',
		dateFormat:'timestamp',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'ci_name',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_name',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_comment',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_release',
		type: 'date',
		dateFormat:'timestamp',
		useNull: true,
		defaultValue: null
	},{
		name: 'cb_display',
		type: 'string',
		useNull: true,
		defaultValue: null
	}]
});

Ext.define('TREE', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'display',
		type: 'string'
	},{
		name: 'value',
		type: 'string'
	},{
		name: 'model',
		type: 'string'
	},{
		name: 'bul_abbr',
		type: 'string'
	},{
		name: 'bul_id',
		type: 'int'
	},{
		name: 'bul_name',
		type: 'string'
	},{
		name: 'ci_id',
		type: 'int'
	},{
		name: 'ci_name',
		type: 'string'
	},{
		name: 'cb_id',
		type: 'int'
	},{
		name: 'cb_name',
		type: 'string'
	},{
		name: 'tree',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('bul_abbr');
			return v;
		}
	}]
});

Ext.define('HISTORY_MAPPING', {
	extend: 'Ext.data.Model',
	fields: [{
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
		name: 'art_upload_modified',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'art_volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
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
		name: 'ci_id',
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
		name: 'cm_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cm_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cm_openid',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'hist_event',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'he_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'hist_serial',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'hist_timestamp',
		useNull: true,
		defaultValue: null,
		type: 'date',
//		dateFormat:'timestamp'
		dateFormat:'time'
	},{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cm_entry',
		type: 'date',
//		dateFormat:'timestamp',
		dateFormat:'time',
	}
	]
});

Ext.define('ORIGINAL_OBJECT', {
	extend: 'Ext.data.Model',
	fields: [{
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
		name: 'art_ext',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_filename',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}]
});

Ext.define('UPLOAD_FOLDER_TREE', {
	extend: 'Ext.data.TreeModel',
//	idProperty: 'artf_id',
	fields: [{
		name: 'id',
		convert: function(value, record) {
			if(Ext.isEmpty(value)) value = record.internalId;
			return value;
		},
		serialize: function(value, record) {
			if(Ext.isEmpty(value)) value = record.internalId;
			return value;
		}
	},{
		name: 'text',
		type: 'string',
		convert: function(value, record) {
			if(Ext.isEmpty(value)) value = record.get('artf_name');
			return value;
		},
	},{
		name: 'artf_id',
		type: 'int'
	},{
		name: 'artf_pid',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'artf_name',
		type: 'string'
	},{
		name: 'artf_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artf_timestamp',
		type: 'date',
		dateFormat:'timestamp',
	},{
		name: 'artf_entry',
		type: 'date',
		dateFormat:'timestamp',
	},{
		name: 'art_count',
		type: 'int',
		defaultValue: 0
	}]
});

Ext.define('DROP_FILE', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'name',
		type: 'string'
	},{
		name: 'size',
		type: 'int'
	},{
		name: 'lastModified',
		type: 'date'
	},{
		name: 'file',
		type: 'auto'
	}]
});

Ext.define('FMA_LIST', {
	extend: 'Ext.data.Model',
	fields: [
	{
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
	}

	]
});

Ext.define('CONFILICT_LIST', {
	extend: 'Ext.data.Model',
	fields: [
	{
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
		name: 'mapped_obj',
		useNull: true,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'mapped_obj_c',
		useNull: true,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'objs',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	,{
		name: 'cp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	,{
		name: 'cl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}

	]
});

Ext.define('CONFILICT_LIST_PALLET', {
	extend: 'Ext.data.Model',
	fields: [
	{
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
		name: 'artf_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artf_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'seg_name',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isString(v)) v = v.toUpperCase();
			return v;
		}
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
		name: 'art_entry',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'art_timestamp',
		type: 'date',
		dateFormat:'timestamp'
	},
	{
		name: 'cm_use',
		type: 'boolean',
		defaultValue: true
	},{
		name: 'selected',
		type: 'boolean',
		defaultValue: true
	},{
		name: 'color',
		mapping: 'Color',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'opacity',
		mapping: 'Opacity',
		type: 'float',
		defaultValue:1.0
	},{
		name: 'remove',
		mapping: 'Hide',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'focused',
		defaultValue: true,
		type: 'boolean'
	},{
		name: 'representation',
		type: 'string',
		defaultValue:'surface'
	},{
		name: 'target_record',
		defaultValue: false,
		type: 'boolean'
	},{
		name: 'is_temporary',
		defaultValue: false,
		type: 'boolean'
	},
	{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cm_entry',
		type: 'date',
		dateFormat:'timestamp',
	}

	]
});

Ext.define('CONCEPT_ART_MAP_PART', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: 'cmp_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'cmp_title',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cmp_abbr',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cmp_prefix',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cmp_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'crl_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'crl_abbr',
			useNull: false,
			defaultValue: '',
			type: 'string'
		}
	]
});

Ext.define('CONCEPT_RELATION_LOGIC', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: 'crl_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'crl_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'crl_abbr',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'crl_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		}
	]
});

Ext.define('CONCEPT_PART', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: 'cp_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'cp_title',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cp_abbr',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cp_prefix',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cp_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'crl_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'crl_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'crl_abbr',
			useNull: false,
			defaultValue: '',
			type: 'string'
		}
	]
});

Ext.define('CONCEPT_LATERALITY', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: 'cl_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'cl_title',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cl_abbr',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cl_prefix',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cl_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		}
	]
});

Ext.define('CONCEPT_INFO', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: 'ci_id',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'ci_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		}
	]
});

Ext.define('PICK_SEARCH', {
	extend: 'PARTS',
	fields: [{
		name: 'distance_xyz',
		type: 'float',
		useNull: true,
		defaultValue: null
	},{
		name: 'distance_voxel',
		type: 'float',
		useNull: true,
		defaultValue: null
	},{
		name: 'target_record',
		defaultValue: false,
		type: 'boolean'
	}]
});

Ext.define('RENDERER', {
	extend: 'PALLETPARTS',
//	extend: 'PARTS',
	fields: [{
		name: 'selected',
		type: 'boolean',
		defaultValue:false
	}]
});

Ext.define('UPLOAD_FOLDER_FILE', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'art_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artf_id',
		useNull: true,
		defaultValue: null,
		type: 'int',
//		serialize: function(v,rec){
//			return v===0 ? null : v;
//		}
	},{
		name: 'artff_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artff_entry',
		type: 'date',
		dateFormat:'timestamp',
		serialize: function(v,rec){
//			return Math.floor(v.getTime()/1000);
			return null;
		}
	},{
		name: 'artff_timestamp',
		type: 'date',
		dateFormat:'timestamp',
		serialize: function(v,rec){
//			return Math.floor(v.getTime()/1000);
			return null;
		}
	}]
});

Ext.define('CONCEPT_TERM', {
	extend: 'Ext.data.Model',
	fields: [{
//		name: 'term_id',
		name: 'id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'term_name',
		name: 'name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'term_synonym',
		name: 'synonym',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
//		name: 'term_definition',
		name: 'definition',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_name',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			return Ext.isEmpty(value) ? record.get('id') : value;
		}
	},{
		name: 'cdi_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			return Ext.isEmpty(value) ? record.get('name') : value;
		}
	},{
		name: 'cdi_syn_e',
		useNull: true,
		defaultValue: null,
		type: 'auto',
		convert: function(value, record) {
			return Ext.isEmpty(value) ? record.get('synonym') : value;
		}
	},{
		name: 'cdi_def_e',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			return Ext.isEmpty(value) ? record.get('definition') : value;
		}
	},{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'display_id',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			return Ext.isEmpty(value) ? (record.get('id') || record.get('cdi_name')) : value;
		}
	},{
		name: 'display_name',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			return Ext.isEmpty(value) ? (record.get('name') || record.get('cdi_name_e')) : value;
		}
	},{
		name: 'display_synonym',
		useNull: true,
		defaultValue: null,
		type: 'auto',
		convert: function(value, record) {
			var synonym = record.get('synonym') || record.get('cdi_syn_e');
			if(Ext.isArray(synonym)){
				return Ext.util.Format.format('<div>{0}</div>',synonym.join('</div><div>'));
			}else{
				return synonym;
			}
		}
	},{
		name: 'display_definition',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			return record.get('definition') || record.get('cdi_def_e');
		}
	}]
});


Ext.define('CONCEPT_DATA_INFO_USER_DATA', {
	extend: 'Ext.data.Model',
	fields: [{
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
		name: 'cdi_syn_e',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
		name: 'cdi_def_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_pid',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cdi_pname',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cp_abbr',
		useNull: false,
		type: 'string'
	},{
		name: 'cl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'cl_abbr',
		useNull: false,
		type: 'string'
	},{
		name: 'crl_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},{
		name: 'crl_name',
		useNull: false,
		defaultValue: '',
		type: 'string'
	},{
		name: 'cdi_super_class_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cdi_super_class_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_super_part_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cdi_super_part_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}]
});

Ext.define('CX_PARTS', {
	extend: 'PARTS',
	fields: [{
		name: 'cx_group_id',
		type: 'string'
	}]
});
