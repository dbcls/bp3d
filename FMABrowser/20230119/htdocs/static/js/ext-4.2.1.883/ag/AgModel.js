Ext.define('CONCEPT_TERM', {
	extend: 'Ext.data.Model',
	fields: [
	{
		name: AgDef.CONCEPT_INFO_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: AgDef.CONCEPT_BUILD_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},
/*
	{
		name: 'cdi_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},
*/
	{
//		name: 'cdi_name',
		name: AgDef.ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: AgDef.NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
/*
	{
		name: 'cdi_name_l',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
*/
	{
//		name: 'cdi_syn_e',
		name: AgDef.SYNONYM_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
//		name: 'cdi_def_e',
		name: AgDef.DEFINITION_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'snippet_cdi_name',
		name: AgDef.SNIPPET_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'snippet_cdi_name_e',
		name: AgDef.SNIPPET_NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'snippet_cdi_syn_e',
		name: AgDef.SNIPPET_SYNONYM_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: 'is_a_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'is_a_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'regional_part_of_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'regional_part_of_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'constitutional_part_of_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'constitutional_part_of_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'branch_of_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'branch_of_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'tributary_of_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'tributary_of_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'member_of_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'member_of_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'systemic_part_of_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'systemic_part_of_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'lexicalsuper_up',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'lexicalsuper_down',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: AgDef.IS_SHAPE_FIELD_ID,
		type: 'boolean',
		defaultValue:false
	},
	{
		name: AgDef.IS_MAPED_FIELD_ID,
		type: 'boolean',
		defaultValue:false
	},
	{
		name: AgDef.IS_CURRENT_FIELD_ID,
		type: 'boolean',
		defaultValue:false
	},
]
});

Ext.define('CONCEPT_TERM_TREE', {
	extend: 'Ext.data.TreeModel',
	fields: [
/*
	{
		name: AgDef.CONCEPT_INFO_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: AgDef.CONCEPT_BUILD_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cdi_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},
*/
	{
//		name: 'cdi_name',
		name: AgDef.TERM_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: AgDef.TERM_NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'text',
		useNull: false,
		type: 'string',
		convert: function(value, record) {
			if(Ext.isString(value)) value = record.get(AgDef.TERM_ID_DATA_FIELD_ID) + ' : ' + record.get(AgDef.TERM_NAME_DATA_FIELD_ID);
			return value;
		}
	}]
});

Ext.define('CONCEPT_INFO', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: AgDef.CONCEPT_INFO_DATA_FIELD_ID,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'ci_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'ci_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'display',
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
				if(Ext.isEmpty(value)) value = record.get('ci_name');
				return value;
			}
		},
		{
			name: 'value',
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
				if(Ext.isEmpty(value)) value = record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID);
				return value;
			}
		}
	]
});

Ext.define('CONCEPT_BUILD', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: AgDef.CONCEPT_INFO_DATA_FIELD_ID,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: AgDef.CONCEPT_BUILD_DATA_FIELD_ID,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'ci_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'cb_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},

		{
			name: 'cb_release',
			type: 'date',
			dateFormat:'timestamp'
		},

		{
			name: 'release',
			type: 'string',
			convert: function(value, record) {
				if(Ext.isEmpty(value)) value = Ext.Date.format(record.get('cb_release'),Ext.Date.defaultFormat);	//'Y-m-d'
				return value;
			}
		},

		{
			name: 'cb_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'display',
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
//				if(Ext.isEmpty(value)) value = Ext.util.Format.format('{0} [{1}] {2}', record.get('ci_name'),record.get('cb_name'), Ext.Date.format(record.get('cb_release'),Ext.Date.defaultFormat));	//'Y-m-d'
				if(Ext.isEmpty(value)) value = Ext.util.Format.format('{0} [{1}]', record.get('cb_name'), Ext.Date.format(record.get('cb_release'),Ext.Date.defaultFormat));	//'Y-m-d'
				return value;
			}
		},
		{
			name: 'value',
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
				if(Ext.isEmpty(value)) value = Ext.util.Format.format(AgDef.FORMAT_CONCEPT_VALUE, record.get(AgDef.CONCEPT_INFO_DATA_FIELD_ID),record.get(AgDef.CONCEPT_BUILD_DATA_FIELD_ID));
				return value;
			}
		}
	]
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
		}
	]
});
