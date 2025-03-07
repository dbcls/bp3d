Ext.define('Ag.data.Model.CONCEPT_TERM', {
	extend: 'Ext.data.Model',
	fields: [
	{
		name: Ag.Def.MODEL_DATA_FIELD_ID,
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},
	{
		name: Ag.Def.MODEL_VERSION_DATA_FIELD_ID,
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},
	{
		name: Ag.Def.CONCEPT_INFO_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID,
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
		name: Ag.Def.ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: Ag.Def.NAME_DATA_FIELD_ID,
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
		name: Ag.Def.SYNONYM_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
//		name: 'cdi_def_e',
		name: Ag.Def.DEFINITION_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'snippet_cdi_name',
		name: Ag.Def.SNIPPET_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'snippet_cdi_name_e',
		name: Ag.Def.SNIPPET_NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'snippet_cdi_syn_e',
		name: Ag.Def.SNIPPET_SYNONYM_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	}]
});


Ext.define('Ag.data.Model.CONCEPT_TERM_PALLET', {
	extend: 'Ext.data.Model',
	fields: [
	{
		name: Ag.Def.MODEL_DATA_FIELD_ID,
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},
	{
		name: Ag.Def.MODEL_VERSION_DATA_FIELD_ID,
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},
	{
		name: Ag.Def.MODEL_REVISION_DATA_FIELD_ID,
		useNull: false,
		defaultValue: null,
		type: 'int'
	},
	{
		name: Ag.Def.CONCEPT_INFO_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},
	{
//		name: 'cdi_id',
		name: Ag.Def.CONCEPT_DATA_INFO_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},
	{
//		name: 'cdi_name',
		name: Ag.Def.ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: Ag.Def.NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: Ag.Def.NAME_DATA_FIELD_ID+'_renderer',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: Ag.Def.NAME_DATA_FIELD_ID+'_renderer',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
//		name: 'cdi_syn_e',
		name: Ag.Def.SYNONYM_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
//		name: 'cdi_syn_e',
		name: Ag.Def.SYNONYM_DATA_FIELD_ID+'_renderer',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: Ag.Def.DEFINITION_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
//		name: 'art_id',
		name: Ag.Def.OBJ_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
//		name: 'art_id',
		name: Ag.Def.OBJ_ID_DATA_FIELD_ID+'_renderer',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
//		name: 'url',
		name: Ag.Def.OBJ_URL_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			if(Ext.isEmpty(value)){
				var obj_id = record.get(Ag.Def.OBJ_ID_DATA_FIELD_ID);
				if(Ext.isString(obj_id) && obj_id.length){
					value = 'art_file/'+obj_id+'.ogz';
				}
			}
			return value;
		}
	},
	{
//		name: 'art_filename',
		name: Ag.Def.OBJ_FILENAME_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
//		name: 'art_timestamp',
		name: Ag.Def.OBJ_TIMESTAMP_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat: 'timestamp'
	},

	{
		name: Ag.Def.OBJ_X_MIN_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'float'
	},
	{
		name: Ag.Def.OBJ_X_MAX_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'float'
	},
	{
		name: Ag.Def.OBJ_Y_MIN_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'float'
	},
	{
		name: Ag.Def.OBJ_Y_MAX_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'float'
	},
	{
		name: Ag.Def.OBJ_Z_MIN_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'float'
	},
	{
		name: Ag.Def.OBJ_Z_MAX_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'float'
	},
	{
		name: Ag.Def.OBJ_POLYS_FIELD_ID,
		useNull: false,
		defaultValue: 0,
		type: 'int'
	},
	{
//		name: 'artc_id',
		name: Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: Ag.Def.OBJ_PREFECTURES_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: Ag.Def.OBJ_CITIES_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: Ag.Def.OBJ_CITIES_FIELD_ID+'_renderer',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: Ag.Def.SEGMENT_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: Ag.Def.SYSTEM_ID_DATA_FIELD_ID,
		type: 'string'
	},
	{
		name: Ag.Def.SYSTEM_ID_DATA_FIELD_ID+'_renderer',
		type: 'string'
	},
	{
		name: Ag.Def.SYSTEM10_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID+'_renderer',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: Ag.Def.CONCEPT_DATA_PICKED_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},
	{
		name: Ag.Def.CONCEPT_DATA_PICKED_TYPE_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: Ag.Def.CONCEPT_DATA_PICKED_ORDER_DATA_FIELD_ID,
		defaultValue: 0,
		type: 'int'
	},
	{
		name: Ag.Def.CONCEPT_DATA_SELECTED_PICK_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},
	{
		name: Ag.Def.CONCEPT_DATA_SELECTED_TAG_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},
	{
		name: Ag.Def.CONCEPT_DATA_SELECTED_WORD_TAG_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: Ag.Def.CONCEPT_DATA_SELECTED_SEGMENT_TAG_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},
	{
		name: Ag.Def.CONCEPT_DATA_SELECTED_CATEGORY_TAG_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},

	{
//		name: 'selected',
		name: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
//		defaultValue: false,
		useNull: true,
		defaultValue: null,
		type: 'boolean'
	},
	{
//		name: 'color',
		name: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
		defaultValue: '#F0D2A0',
		type: 'string'
	},
	{
//		name: 'opacity',
		name: Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,
		defaultValue: 1.0,
		type: 'float'
	},
	{
//		name: 'visible',
		name: Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID,
		defaultValue: true,
		type: 'boolean'
	},
	{
//		name: 'focus',
		name: Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID,
		defaultValue: true,
		type: 'boolean'
	},
	{
//		name: 'PartRepresentation',
		name: Ag.Def.PART_REPRESENTATION,
		defaultValue: 'surface',
		type: 'string'
	},
	{
//		name: 'relation',
		name: Ag.Def.CONCEPT_DATA_RELATION_DATA_FIELD_ID,
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'is_a',
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'is_a'+'_renderer',
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'part_of',
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'part_of'+'_renderer',
		defaultValue: null,
		type: 'auto'
	},
	{
		name: 'systemic_part_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'regional_part_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'branch_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'arterial_supply_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'constitutional_part_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'tributary_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'member_of',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'lexicalsuper',
		defaultValue: null,
		type: 'auto'
/*
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var relation = record.get('relation');
			if(Ext.isObject(relation) && Ext.isObject(relation[field.name])){
				var datas = [];
				Ext.Object.each(relation[field.name], function(k,v){
					datas.push(Ext.String.format('{0} : {1}',k,v));
				});
				value = datas.join("\n");
			}
			return value;
		}
*/
	},
	{
		name: 'sub',
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var cdi_name = record.get(Ag.Def.ID_DATA_FIELD_ID);
			if(Ext.isString(cdi_name) && cdi_name.match(/^FMA[0-9]+([A-Z]*)\-[LRU]+$/)){
				value = RegExp.$1;
			}
			return value;
		}
	},
	{
		name: 'sub'+'_renderer',
		defaultValue: null,
		type: 'string'
	},
	{
		name: 'laterality',
		defaultValue: null,
		type: 'string',
		convert: function(value, record) {
			var field = this;
			var cdi_name = record.get(Ag.Def.ID_DATA_FIELD_ID);
			if(Ext.isString(cdi_name) && cdi_name.match(/^FMA[0-9]+[A-Z]*\-([LRU]+)$/)){
				value = RegExp.$1;
			}
			return value;
		}
	},
	{
		name: 'laterality'+'_renderer',
		defaultValue: null,
		type: 'string'
	}

	]
});

Ext.define('Ag.data.Model.CONCEPT_TERM_TREE', {
	extend: 'Ext.data.TreeModel',
	fields: [
/*
	{
		name: Ag.Def.CONCEPT_INFO_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID,
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
		name: Ag.Def.TERM_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
//		name: 'cdi_name_e',
		name: Ag.Def.TERM_NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'text',
		useNull: false,
		type: 'string',
		convert: function(value, record) {
			if(Ext.isString(value)) value = record.get(Ag.Def.TERM_ID_DATA_FIELD_ID) + ' : ' + record.get(Ag.Def.TERM_NAME_DATA_FIELD_ID);
			return value;
		}
	}]
});

Ext.define('Ag.data.Model.CONCEPT_INFO', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: Ag.Def.CONCEPT_INFO_DATA_FIELD_ID,
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
				if(Ext.isEmpty(value)) value = record.get(Ag.Def.CONCEPT_INFO_DATA_FIELD_ID);
				return value;
			}
		}
	]
});

Ext.define('Ag.data.Model.CONCEPT_BUILD', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: Ag.Def.CONCEPT_INFO_DATA_FIELD_ID,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID,
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
				if(Ext.isEmpty(value)) value = Ext.util.Format.format(Ag.Def.FORMAT_CONCEPT_VALUE, record.get(Ag.Def.CONCEPT_INFO_DATA_FIELD_ID),record.get(Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID));
				return value;
			}
		}
	]
});

Ext.define('Ag.data.Model.MODEL_VERSION', {
	extend: 'Ext.data.Model',
	fields: [
		{
			name: Ag.Def.LOCATION_HASH_MDID_KEY,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: Ag.Def.LOCATION_HASH_MVID_KEY,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: Ag.Def.LOCATION_HASH_MRID_KEY,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: Ag.Def.LOCATION_HASH_CIID_KEY,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: Ag.Def.LOCATION_HASH_CBID_KEY,
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'md_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: 'mv_name',
			useNull: false,
			defaultValue: '',
			type: 'string'
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
			name: 'mv_order',
			useNull: false,
			defaultValue: 0,
			type: 'int'
		},
		{
			name: 'mr_version',
			useNull: false,
			defaultValue: '',
			type: 'string'
		},
		{
			name: Ag.Def.VERSION_STRING_FIELD_ID,
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
				if(Ext.isEmpty(value)) value = record.get('mv_name');
				return value;
			}
		},
		{
			name: 'display',
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
				if(Ext.isEmpty(value)) value = record.get('mv_name');
				return value;
			}
		},
		{
			name: 'value',
			useNull: false,
			defaultValue: '',
			type: 'string',
			convert: function(value, record) {
//				if(Ext.isEmpty(value)) value = Ext.util.Format.format(Ag.Def.FORMAT_CONCEPT_VALUE, record.get(Ag.Def.CONCEPT_INFO_DATA_FIELD_ID),record.get(Ag.Def.CONCEPT_BUILD_DATA_FIELD_ID));
				if(Ext.isEmpty(value)) value = Ext.util.Format.format(Ag.Def.FORMAT_MODEL_VERSION_VALUE, record.get(Ag.Def.LOCATION_HASH_MDID_KEY),record.get(Ag.Def.LOCATION_HASH_MVID_KEY));
//				console.log(value);
				return value;
			}
		}
	]
});

Ext.define('Ag.data.Model.SEGMENT_LIST', {
	extend: 'Ext.data.TreeModel',
//	extend: 'Ext.data.Model',

	idProperty: 'segment',
	fields: [{
		name: 'text',
		type: 'string'/*,
		convert: function(value, record) {
//			if(Ext.isEmpty(value)) value = record.get(Ag.Def.SEGMENT_ID_DATA_FIELD_ID);
			if(value.match(/^MM[0-9]+(.+)$/)) value = RegExp.$1;
			if(value.match(/^M_+(.+)$/)) value = RegExp.$1 + '(M)';
			if(value.match(/^_+(.+)$/)) value = RegExp.$1;

			if(value.match(/^(.+)([-_])R\(M\)$/)) value = RegExp.$1 + RegExp.$2 + 'L';
			if(value.match(/^(.+)([0-9]+)R\(M\)$/)) value = RegExp.$1 + RegExp.$2 + 'L';

			if(value.match(/^(.+)(_TRI)\(M\)$/)) value = RegExp.$1 + RegExp.$2 + '-L';
			if(value.match(/^(.+)(_TRI)$/)) value = RegExp.$1 + RegExp.$2 + '-R';

			if(value.match(/^(.+)([0-9]+)R(_\(scapula\))\(M\)$/)) value = RegExp.$1 + RegExp.$2 + 'L' + RegExp.$3;


			if(value.match(/^(.+)-_([LR])$/)) value = RegExp.$1 + '-' + RegExp.$2;
			if(value.match(/^(.+)_([LR])$/)) value = RegExp.$1 + '-' + RegExp.$2;

			return value;
		}
*/
//	},{
//		name: Ag.Def.SEGMENT_ID_DATA_FIELD_ID,
//		type: 'string'
	},{
		name: 'segment',
		type: 'string',
		convert: function(value, record) {
//			console.log(value);
			if(Ext.isEmpty(value)){
				var url_arr = record.get(Ag.Def.OBJ_URL_DATA_FIELD_ID).split('/').reverse();
				value = [url_arr[1],url_arr[0]].join('/').replace(/\.[^\.]+$/,'');
			}
			return value;
		}
	},{
		name: 'expanded',
		type: 'boolean',
		defaultValue: false,
	},{
		name: 'leaf',
		type: 'boolean',
		defaultValue: false,
	},{
		name: Ag.Def.OBJ_ID_DATA_FIELD_ID,
		type: 'string'
	},{
		name: Ag.Def.OBJ_CONCEPT_ID_DATA_FIELD_ID,
		type: 'string'
	},{
		name: Ag.Def.OBJ_URL_DATA_FIELD_ID,
		type: 'string'
	},{
		name: 'xmin',
		type: 'float'
	},{
		name: 'xmax',
		type: 'float'
	},{
		name: 'ymin',
		type: 'float'
	},{
		name: 'ymax',
		type: 'float'
	},{
		name: 'zmin',
		type: 'float'
	},{
		name: 'zmax',
		type: 'float'
	},{
		name: 'prefectures',
		type: 'string'
	},{
		name: 'cities',
		type: 'auto'
	},{
		name: 'cities_ids',
		type: 'string',
		convert: function(value, record) {
			if(Ext.isEmpty(value) && Ext.isArray(record.get('children'))){
				var cities_ids = {};
				var children = record.get('children');
				Ext.Array.each(children, function(c){
					Ext.Array.each(c.cities_ids.split(','), function(a){
						cities_ids[a] = null;
					})
				});
				value = Ext.Array.map(Ext.Object.getKeys(cities_ids), function(v){return v-0;}).sort(function(a,b){
					if(a<b) return -1;
					if(a>b) return  1;
					return 0;
				}).join(',');
			}
			return value;
		}
	},{
		name: 'cities_id',
		type: 'int',
	},{
		name: 'name',
		type: 'string',
	},{
		name: Ag.Def.SEGMENT_ID_DATA_FIELD_ID,
		type: 'string'
//	},{
//		name: Ag.Def.SEGMENT_ORDER_DATA_FIELD_ID,
//		type: 'int'
	},{
		name: 'element_count',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'element',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
		name: Ag.Def.CONCEPT_DATA_DISABLED_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},{
		name: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},{
		name: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
//		defaultValue: '#F0D2A0',
		defaultValue: '#FFFFFF',
		type: 'string'
	},{
		name: Ag.Def.CONCEPT_DATA_OPACITY_DATA_FIELD_ID,
		defaultValue: 0.5,
		type: 'float'
	},{
		name: Ag.Def.CONCEPT_DATA_VISIBLE_DATA_FIELD_ID,
		defaultValue: true,
		type: 'boolean'
	},{
		name: Ag.Def.USE_FOR_BOUNDING_BOX_FIELD_ID,
		defaultValue: true,
		type: 'boolean'
	}]
});

Ext.define('Ag.data.Model.SYSTEM_LIST', {
	extend: 'Ext.data.Model',

	fields: [{
		name: 'text',
		type: 'string',
		convert: function(value, record) {
			if(Ext.isEmpty(value)) value = record.get(Ag.Def.SYSTEM_ID_DATA_FIELD_ID);
			if(value.match(/^[0-9]+(.+)$/)) value = RegExp.$1;
			if(value.match(/^_+(.+)$/)) value = RegExp.$1;
			return value;
		}
	},{
		name: Ag.Def.SYSTEM_ID_DATA_FIELD_ID,
		type: 'string'
	},{
		name: Ag.Def.SYSTEM10_ID_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: Ag.Def.SYSTEM10_NAME_DATA_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: Ag.Def.CONCEPT_DATA_COLOR_DATA_FIELD_ID,
		defaultValue: '#F0D2A0',
		type: 'string'
	},{
		name: 'element_count',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'element',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
		name: Ag.Def.CONCEPT_DATA_SELECTED_DATA_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	}]
});


Ext.define('Ag.data.Model.PIN_PALLET', {
	extend: 'Ext.data.Model',
	idProperty: Ag.Def.PIN_ID_FIELD_ID,
	fields: [
	{
		name: Ag.Def.PIN_ID_FIELD_ID,
		type: 'string'
	},
	{
		name: Ag.Def.PIN_NO_FIELD_ID,
		type: 'int'
	},
	{
		name: Ag.Def.PIN_COORDINATE_X_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_COORDINATE_Y_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_COORDINATE_Z_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_VECTOR_X_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_VECTOR_Y_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_VECTOR_Z_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_UP_VECTOR_X_FIELD_ID,
		defaultValue: 0,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_UP_VECTOR_Y_FIELD_ID,
		defaultValue: 1,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_UP_VECTOR_Z_FIELD_ID,
		defaultValue: 0,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_DESCRIPTION_DRAW_FLAG_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	},
	{
		name: Ag.Def.PIN_DESCRIPTION_COLOR_FIELD_ID,
		defaultValue: '#0000FF',
		type: 'string'
	},
	{
		name: Ag.Def.PIN_DESCRIPTION_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: Ag.Def.PIN_COLOR_FIELD_ID,
		defaultValue: '#0000FF',
		type: 'string'
	},
	{
		name: Ag.Def.PIN_SHAPE_FIELD_ID,
		defaultValue: '',
		type: 'string'
	},
	{
		name: Ag.Def.PIN_SIZE_FIELD_ID,
		defaultValue: 10,
		type: 'float'
	},
	{
		name: Ag.Def.PIN_COORDINATE_SYSTEM_NAME_FIELD_ID,
		defaultValue: 'bp3d',
		type: 'string'
	},
	{
		name: Ag.Def.PIN_PART_ID_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: Ag.Def.PIN_PART_NAME_FIELD_ID,
		useNull: true,
		defaultValue: null,
		type: 'string'
	},
	{
		name: Ag.Def.PIN_VISIBLE_FIELD_ID,
		defaultValue: true,
		type: 'boolean'
	},
	]
});

Ext.define('Ag.data.Model.NEIGHBOR_PARTS', {
	extend: 'Ag.data.Model.CONCEPT_TERM_PALLET',
	fields: [
	{
		name: Ag.Def.DISTANCE_FIELD_ID,
		type: 'float'
	},
	{
		name: Ag.Def.TARGET_RECORD_FIELD_ID,
		defaultValue: false,
		type: 'boolean'
	}
	]
});
