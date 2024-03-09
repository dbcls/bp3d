Ext.define('BP3D', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'b_id',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_id;
			return v;
		}
	},{
		name: 'f_id',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name;
			return v;
		}
	},{
		name: 'model',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.md_abbr;
			return v;
		}
	},{
		name: 'version',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.mv_name_e;
			return v;
		}
	},{
		name: 'tree',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.bul_abbr;
			return v;
		}
	},{
		name: 'b_name_j',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_j;
			return v;
		}
	},{
		name: 'b_name_e',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_e;
			return v;
		}
	},{
		name: 'name',
		type: 'string',
		useNull: true,
		defaultValue: null,
		convert: function(v,r){
			if(Ext.isEmpty(v)) v= r.data.cdi_name_e;
			return v;
		}
	},{
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
		name: 'focused',
		type: 'boolean',
		useNull: true,
		defaultValue: null
	},{
		name: 'filesize',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'conv_size',
		useNull: true,
		defaultValue: null,
		type: 'int'
//	},{
//		name: 'json_size',
//		type: 'int'
	},{
		name: 'org_points',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'org_polys',
		useNull: true,
		defaultValue: null,
		type: 'int'
//	},{
//		name: 'org_edges',
//		type: 'int'
	},{
		name: 'points',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'polys',
		useNull: true,
		defaultValue: null,
		type: 'int'
//	},{
//		name: 'edges',
//		type: 'int'
//	},{
//		name: 'reduction_rate',
//		type: 'float'
	},{
		name: 'reduction',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
//			return r.data.org_points && r.data.points ? 1 - r.data.points / r.data.org_points : '-';
			return r.data.org_polys && r.data.polys ? 1 - r.data.polys / r.data.org_polys : null;
		}
	},{
		name: 'xmin',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_xmin)) v = r.data.rep_xmin;
			return v;
		}
	},{
		name: 'xmax',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_xmax)) v = r.data.rep_xmax;
			return v;
		}
	},{
		name: 'xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_xmax) && !Ext.isEmpty(r.data.rep_xmin)) v = (r.data.rep_xmax + r.data.rep_xmin)/2;
			return v;
		}
	},{
		name: 'ymin',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_ymin)) v = r.data.rep_ymin;
			return v;
		}
	},{
		name: 'ymax',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_ymax)) v = r.data.rep_ymax;
			return v;
		}
	},{
		name: 'ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_ymax) && !Ext.isEmpty(r.data.rep_ymin)) v = (r.data.rep_ymax + r.data.rep_ymin)/2;
			return v;
		}
	},{
		name: 'zmin',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_zmin)) v = r.data.rep_zmin;
			return v;
		}
	},{
		name: 'zmax',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_zmax)) v = r.data.rep_zmax;
			return v;
		}
	},{
		name: 'zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_zmax) && !Ext.isEmpty(r.data.rep_zmin)) v = (r.data.rep_zmax + r.data.rep_zmin)/2;
			return v;
		}
	},{
		name: 'volume',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_volume)) v = r.data.rep_volume;
			return v;
		}
	},{
		name: 'modified',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v,r){
			if(Ext.isEmpty(v)){
				if(!Ext.isEmpty(r.data.rep_entry) && !Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi>r.data.rep_entry ? r.data.cm_max_entry_cdi : r.data.rep_entry;
				}
				else if(!Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi;
				}
				else if(!Ext.isEmpty(r.data.mtime)){
					v = r.data.mtime;
				}
				else if(!Ext.isEmpty(r.data.rep_entry)){
					v = r.data.rep_entry;
				}
			}
			if(!Ext.isEmpty(v) && !Ext.isDate(v)){
				var d = new Date();
				d.setTime(v*1000);
				v=d;
			}
			return v;
		}
	},{
		name: 'mtime',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v,r){
			if(Ext.isEmpty(v)){
				if(!Ext.isEmpty(r.data.rep_entry) && !Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi>r.data.rep_entry ? r.data.cm_max_entry_cdi : r.data.rep_entry;
				}
				else if(!Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi;
				}
				else if(!Ext.isEmpty(r.data.rep_entry)){
					v = r.data.rep_entry;
				}
			}
			if(!Ext.isEmpty(v) && !Ext.isDate(v)){
				var d = new Date();
				d.setTime(v*1000);
				v=d;
			}
			return v;
		}
	},{
		name: 'cm_max_num_cdi',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cm_max_entry_cdi',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'path',
		type: 'string'
	},{
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
		name: 'disabled',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'c_num',
//		type: 'int',
		convert: function(v,r){
//			return r.data.children ? r.data.children.length : 0;
			if(r.data.children){
				var c_num = {};
				for(var key in r.data.children){
					c_num[key] = r.data.children[key].length;
				}
				return c_num;
			}else{
				return null;
			}
		}
	},{
		name: 'c_num_bp3d',
		type: 'int',
		convert: function(v,r){
			return r.data.children && r.data.children.bp3d ? r.data.children.bp3d.length : 0;
		}
	},{
		name: 'c_num_isa',
		type: 'int',
		convert: function(v,r){
			return r.data.children && r.data.children.isa ? r.data.children.isa.length : 0;
		}
	},{
		name: 'c_num_partof',
		type: 'int',
		convert: function(v,r){
			return r.data.children && r.data.children.partof ? r.data.children.partof.length : 0;
		}
	},{
		name: 'depth_bp3d',
		type: 'int',
		convert: function(v,r){
			return r.data.depth && r.data.depth.bp3d ? r.data.depth.bp3d : 0;
		}
	},{
		name: 'depth_isa',
		type: 'int',
		convert: function(v,r){
			return r.data.depth && r.data.depth.isa ? r.data.depth.isa : 0;
		}
	},{
		name: 'depth_partof',
		type: 'int',
		convert: function(v,r){
			return r.data.depth && r.data.depth.partof ? r.data.depth.partof : 0;
		}
	},{
		name: 'children'
	},

	{
		name: 'rep_id',
		type: 'string'
//	},{
//		name: 'art_id',
//		type: 'string'
	},{
		name: 'c_art_id',
		type: 'string'
	},{
		name: 'md_id',
		type: 'int'
	},{
		name: 'mv_id',
		type: 'int'
	},{
		name: 'mr_id',
		type: 'int'
	},{
		name: 'bul_id',
		type: 'int'
	},{
		name: 'bul_abbr',
		type: 'string'
	},{
		name: 'cdi_name',
		type: 'string'
	},{
		name: 'cdi_name_j',
		type: 'string'
	},{
		name: 'cdi_name_e',
		type: 'string'
	},{
		name: 'cdi_name_k',
		type: 'string'
	},{
		name: 'cdi_name_l',
		type: 'string'
	},{
		name: 'md_abbr',
		type: 'string'
	},{
		name: 'mv_name_e',
		type: 'string'
	},{
		name: 'rep_xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_xmax) && !Ext.isEmpty(r.data.rep_xmin)) v = (r.data.rep_xmax + r.data.rep_xmin)/2;
			return v;
		}
	},{
		name: 'rep_ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_ymax) && !Ext.isEmpty(r.data.rep_ymin)) v = (r.data.rep_ymax + r.data.rep_ymin)/2;
			return v;
		}
	},{
		name: 'rep_zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_zmax) && !Ext.isEmpty(r.data.rep_zmin)) v = (r.data.rep_zmax + r.data.rep_zmin)/2;
			return v;
		}
	},{
		name: 'rep_volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_entry',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'artg_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
		name: 'art_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'

	},{
		name: 'rep_primitive',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'rep_density',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_density_iconCls',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: 'seg_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'seg_name',
		type: 'string',
		useNull: true,
		defaultValue: null,
	},{
		name: 'seg_color',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'seg_thum_bgcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'seg_thum_fgcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	},

	//ここ以下は、Tree用
	{
		name: 'text',
		type: 'string'
	},{
		name: 'vcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'vopacity',
		type: 'float',
		defaultValue:1.0
	},{
		name: 'vremove',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'vfocused',
		type: 'boolean',
		defaultValue:false
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
		name: 'time_diff',
		type: 'int',
		convert: function(v,r){
			if(Ext.isEmpty(v)){
				var cm_max_entry_cdi = r.get('cm_max_entry_cdi');
				var rep_entry = r.get('rep_entry');
				if(Ext.isEmpty(cm_max_entry_cdi)){
					cm_max_entry_cdi = 0;
				}else{
					cm_max_entry_cdi = cm_max_entry_cdi.getTime();
				}
				if(Ext.isEmpty(rep_entry)){
					rep_entry = 0;
				}else{
					rep_entry = rep_entry.getTime();
				}
				return (rep_entry-cm_max_entry_cdi)/1000;
			}else{
				return v;
			}
		}
	}

	,{
		name: 'rep_thumb',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}

	]
});

Ext.define('EXTENSIONPARTS', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'name',
		type: 'string'
	},{
		name: 'filename',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('name');
			return v;
		}
	},{
		name: 'sortname',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
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
		name: 'filesize',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'conv_size',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'json_size',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'org_points',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'org_polys',
		useNull: true,
		defaultValue: null,
		type: 'int'
//	},{
//		name: 'org_edges',
//		type: 'int'
	},{
		name: 'points',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'polys',
		useNull: true,
		defaultValue: null,
		type: 'int'
//	},{
//		name: 'edges',
//		type: 'int'
//	},{
//		name: 'reduction_rate',
//		type: 'float'
	},{
		name: 'reduction',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			return r.data.org_points && r.data.points ? 1 - r.data.points / r.data.org_points : null;
		}
	},{
		name: 'xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('xmax')) && Ext.isNumber(r.get('xmin'))) v = (r.get('xmax')+r.get('xmin'))/2;
			return v;
		}
	},{
		name: 'ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('ymax')) && Ext.isNumber(r.get('ymin'))) v = (r.get('ymax')+r.get('ymin'))/2;
			return v;
		}
	},{
		name: 'zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('zmax')) && Ext.isNumber(r.get('zmin'))) v = (r.get('zmax')+r.get('zmin'))/2;
			return v;
		}
	},{
		name: 'volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'mtime',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'modified',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'group',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('artg_name');
			return v;
		}
	},{
		name: 'grouppath',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'path',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: 'model',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('md_abbr');
			return v;
		}
	},{
		name: 'version',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('mv_name_e');
			return v;
		}
	},{
		name: 'tree',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.bul_abbr;
			return v;
		}
	},

	{
		name: 'artg_id',
		type: 'int'
	},{
		name: 'artg_name',
		type: 'string'
	},{
		name: 'artg_timestamp',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'atrg_use',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'artg_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artg_delcause',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artg_entry',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'artg_openid',
		type: 'string'
	},{
		name: 'art_count',
		type: 'int'
	},{
		name: 'nomap_count',
		type: 'int'
	},{
		name: 'nochk_count',
		type: 'int'
	},{
		name: 'use_map_count',
		type: 'int'
	},{
		name: 'all_cm_map_versions',
		type: 'auto'
	},

	{
		name: 'artog_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'artog_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
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
	},

	{
		name: 'artf_id',
		type: 'int'
	},{
		name: 'artf_name',
		type: 'string'
	},

	{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cb_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'rep_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'use_rep_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'art_id',
		sortType: 'asFJID',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_hist_serial',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'art_thumb',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_mirroring',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'art_category',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_judge',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_class',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cm_use',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'cm_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'all_cm_count',
		type: 'int'
	},{
		name: 'all_cm_map_versions',
		type: 'auto'
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
	},

	{
		name: 'diff_volume',
		type: 'float',
		useNull: true,
		defaultValue: null
	},{
		name: 'diff_cube_volume',
		type: 'float',
		useNull: true,
		defaultValue: null
	},{
		name: 'diff_cube_volume_sum',
		type: 'float',
		useNull: true,
		defaultValue: null,
		convert: function(v,r){
			if(Ext.isEmpty(v) && (!Ext.isEmpty(r.data.diff_volume) || !Ext.isEmpty(r.data.diff_cube_volume))){
				v = 0;
				if(!Ext.isEmpty(r.data.diff_volume)) v += r.data.diff_volume;
				if(!Ext.isEmpty(r.data.diff_cube_volume)) v += r.data.diff_cube_volume;
			}
			return v;
		}
	},{
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
		name: 'collision_rate',
		type: 'float',
		useNull: true,
		defaultValue: null
	},{
		name: 'collision_rate_obj',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: 'num',
		type: 'int'
	},{
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
		defaultValue:false
	},{
		name: 'dropobject',
		type: 'boolean',
		defaultValue:false
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	]
});


Ext.define('FMA', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'b_id',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_id;
			return v;
		}
	},{
		name: 'f_id',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v =  r.data.cdi_name;
			return v;
		}
	},{
		name: 'model',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.md_abbr;
			return v;
		}
	},{
		name: 'version',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.mv_name_e;
			return v;
		}
	},{
		name: 'tree',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.bul_abbr;
			return v;
		}
	},{
		name: 'name_j',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_j;
			return v;
		}
	},{
		name: 'name_e',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_e;
			return v;
		}
	},{
		name: 'name_k',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_k;
			return v;
		}
	},{
		name: 'name_l',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_l;
			return v;
		}
	},{
		name: 'b_name_j',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_j;
			return v;
		}
	},{
		name: 'b_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_e;
			return v;
		}
	},{
		name: 'b_name_k',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_k;
			return v;
		}
	},{
		name: 'b_name_l',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_l;
			return v;
		}
	},{
		name: 'name',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_name_e;
			return v;
		}
	},{
		name: 'syn_j',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_syn_j;
			return v;
		}
	},{
		name: 'syn_e',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_syn_e;
			return v;
		}
	},{
		name: 'sort_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'taid',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cdi_taid;
			return v;
		}
	},{
		name: 'xmin',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_xmin;
			return v;
		}
	},{
		name: 'xmax',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_xmax;
			return v;
		}
	},{
		name: 'xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.data.rep_xmin) && Ext.isNumber(r.data.rep_xmax)) v = (r.data.rep_xmin+r.data.rep_xmax)/2;
			return v;
		}
	},{
		name: 'ymin',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_ymin;
			return v;
		}
	},{
		name: 'ymax',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_ymax;
			return v;
		}
	},{
		name: 'ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.data.rep_ymin) && Ext.isNumber(r.data.rep_ymax)) v = (r.data.rep_ymin+r.data.rep_ymax)/2;
			return v;
		}
	},{
		name: 'zmin',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_zmin;
			return v;
		}
	},{
		name: 'zmax',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_zmax;
			return v;
		}
	},{
		name: 'zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.data.rep_zmin) && Ext.isNumber(r.data.rep_zmax)) v = (r.data.rep_zmin+r.data.rep_zmax)/2;
			return v;
		}
	},{
		name: 'volume',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_volume;
			return v;
		}
	},{
		name: 'ctime',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.rep_entry;
			return v;
		}
	},{
		name: 'mtime',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v,r){
			if(Ext.isEmpty(v)){
				if(!Ext.isEmpty(r.data.rep_entry) && !Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi>r.data.rep_entry ? r.data.cm_max_entry_cdi : r.data.rep_entry;
				}
				else if(!Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi;
				}
				else{
					v = r.data.rep_entry;
				}
			}
			if(!Ext.isEmpty(v) && !Ext.isDate(v)){
				var d = new Date();
				d.setTime(v*1000);
				v=d;
			}
			return v;
		}
	},{
		name: 'ord',
		type: 'int'
	},{
		name: 'path',
		type: 'string'
	},{
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
		defaultValue:false
	},

	{
		name: 'rep_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
//	},{
//		name: 'art_id',
//		useNull: true,
//		defaultValue: null,
//		type: 'string'
	},{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cb_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'md_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mv_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'rep_xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_xmax) && !Ext.isEmpty(r.data.rep_xmin)) v = (r.data.rep_xmax + r.data.rep_xmin)/2;
			return v;
		}
	},{
		name: 'rep_ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_ymax) && !Ext.isEmpty(r.data.rep_ymin)) v = (r.data.rep_ymax + r.data.rep_ymin)/2;
			return v;
		}
	},{
		name: 'rep_zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v,r){
			if(Ext.isEmpty(v) && !Ext.isEmpty(r.data.rep_zmax) && !Ext.isEmpty(r.data.rep_zmin)) v = (r.data.rep_zmax + r.data.rep_zmin)/2;
			return v;
		}
	},{
		name: 'rep_volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_entry',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'artg_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
		name: 'art_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'

	},{
		name: 'rep_primitive',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'rep_density',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'rep_density_iconCls',
		useNull: true,
		defaultValue: null,
		type: 'string'

	},{
		name: 'cm_max_num_cdi',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cm_max_entry_cdi',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'
	},

	{
		name: 'seg_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'seg_name',
		type: 'string',
		useNull: true,
		defaultValue: null,
	},{
		name: 'seg_color',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'seg_thum_bgcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'seg_thum_fgcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END

	]
});

Ext.define('PALLETPARTS', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'b_id',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('rep_id');
			return v;
		}
	},{
		name: 'f_id',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v =  r.get('cdi_name');
			return v;
		}
	},{
		name: 'model',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('md_abbr');
			return v;
		}
	},{
		name: 'version',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('mv_name_e');
			return v;
		}
	},{
		name: 'tree',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('bul_abbr');
			return v;
		}
	},{
		name: 'b_name_j',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name_j');
			return v;
		}
	},{
		name: 'b_name_e',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name_e');
			return v;
		}
	},{
		name: 'name',
		type: 'string'
	},{
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
		name: 'filesize',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('xmax')) && Ext.isNumber(r.get('xmin'))) v = (r.get('xmax')+r.get('xmin'))/2;
			return v;
		}
	},{
		name: 'ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('ymax')) && Ext.isNumber(r.get('ymin'))) v = (r.get('ymax')+r.get('ymin'))/2;
			return v;
		}
	},{
		name: 'zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('zmax')) && Ext.isNumber(r.get('zmin'))) v = (r.get('zmax')+r.get('zmin'))/2;
			return v;
		}
	},{
		name: 'volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'mtime',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'group',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('artg_name');
			if(Ext.isEmpty(v)) v = r.get('mv_name_e');
			return v;
		}
	},{
		name: 'grouppath',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'path',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'selected',
		type: 'boolean',
		defaultValue:true
	},

	{
		name: 'rep_id',
		mapping : 'BPID',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_id',
		mapping : 'FJID',
		sortType: 'asFJID',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_thumb',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'cdi_name_j',
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
		name: 'art_class',
		mapping: 'Class',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_category',
		mapping: 'Category',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'art_judge',
		mapping: 'Judge',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cm_use',
		type: 'boolean',
		defaultValue:false
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
		name: 'filename',
		mapping: 'Filename',
		useNull: true,
		defaultValue: null,
		type: 'string'

	},{
		name: 'artg_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'artg_name',
		mapping: 'Group / Version',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

	{
		name: 'artog_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'artog_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
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

	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END

	]
});

Ext.define('OBJ_EDIT', {
	extend: 'PALLETPARTS',
	fields: [{
		name: 'set_same_use_setting_mirror_part',
		type: 'boolean',
		defaultValue:false
	},{
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
	}
	//2016-03-31 START
	,{
		name: 'mirror_cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	]
});

Ext.define('PIN', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'PinPartID',
		type: 'string'
	},{
		name: 'PinX',
		type: 'float'
	},{
		name: 'PinY',
		type: 'float'
	},{
		name: 'PinZ',
		type: 'float'
	},{
		name: 'PinArrowVectorX',
		type: 'float'
	},{
		name: 'PinArrowVectorY',
		type: 'float'
	},{
		name: 'PinArrowVectorZ',
		type: 'float'
	},{
		name: 'PinUpVectorX',
		type: 'float'
	},{
		name: 'PinUpVectorY',
		type: 'float'
	},{
		name: 'PinUpVectorZ',
		type: 'float'
	},{
		name: 'PinDescription',
		type: 'string'
	},{
		name: 'PinDescriptionDrawFlag',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'PinDescriptionColor',
		type: 'string',
		defaultValue: '#0000FF'
	},{
		name: 'PinIndicationLineDrawFlag',
		type: 'int',
		defaultValue: 0
	},{
		name: 'PinColor',
		type: 'string',
		defaultValue: '#0000FF'
	},{
		name: 'PinShape',
		type: 'string',
		defaultValue: 'CIRCLE'
	},{
		name: 'PinCoordinateSystemName',
		type: 'string',
		defaultValue: 'bp3d'
	},{
		name: 'PinOrganID',
		type: 'string'
	},{
		name: 'PinOrganName',
		type: 'string'
	},{
		name: 'PinOrganGroup',
		type: 'string'
	},{
		name: 'PinOrganGrouppath',
		type: 'string'
	},{
		name: 'PinOrganPath',
		type: 'string'
	},{
		name: 'PinOrganVersion',
		type: 'string'
	}]
});

Ext.define('MODEL', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'display',
		type: 'string'
	},{
		name: 'value',
		type: 'string'
	},{
		name: 'md_id',
		type: 'int'
	},{
		name: 'md_abbr',
		type: 'string'
	},{
		name: 'model',
		type: 'string',
		convert: function(v, r) {
			if(Ext.isEmpty(v)) v = r.get('md_abbr');
			return v;
		}
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
		name: 'model',
		type: 'string',
		convert: function(v, r) {
			if(Ext.isEmpty(v)) v = r.get('md_abbr');
			return v;
		}
	},{
		name: 'version',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'version.version',
		type: 'int',
		useNull: true,
//		defaultValue: null,
		convert: function(v, r) {
			if(Ext.isEmpty(v)){
				v = r.get('version_version');
			}
			if(Ext.isEmpty(v)){
				var vs = r.get('version');
				if(!Ext.isEmpty(vs)){
					v = parseInt(vs);
				}
				if(isNaN(v)){
					v = r.get('version_version');
				}
			}
			return v;
		}
	},{
		name: 'version.revision',
		type: 'int',
		useNull: true,
//		defaultValue: null,
		convert: function(v, r) {
			if(Ext.isEmpty(v)){
				v = r.get('version_revision');
			}
			if(Ext.isEmpty(v)){
				var vs = r.get('version');
				if(!Ext.isEmpty(vs)){
					v = parseInt((vs.split('.',2))[1]);
				}
				if(isNaN(v)){
					v = r.get('version_revision');
				}
			}
			return v;
		}
	},{
		name: 'data',
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
		name: 'mr_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_publish',
		type: 'boolean',
		defaultValue: false
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
		name: 'mr_entry',
		type: 'date',
		dateFormat:'timestamp',
		useNull: true,
		defaultValue: null
	},{
		name: 'info_takeover',
		type: 'boolean',
		defaultValue: false
	},{
		name: 'prev_mv_id',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_port',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_frozen',
		type: 'boolean',
		defaultValue: false
	},{
		name: 'mv_comment',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_objects_set',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_order',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_use',
		type: 'boolean',
		defaultValue: false
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
		name: 'concept',
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
	},{
		name: 'version_version',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'version_revision',
		type: 'int',
		useNull: true,
		defaultValue: null
	},{
		name: 'fmt_version',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'mr_version',
		type: 'string',
		useNull: true,
		defaultValue: null
	},{
		name: 'mv_priority',
		type: 'int'
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

Ext.define('BP3D_TREE', {
	extend: 'Ext.data.Model',
	idProperty: 'path',
	fields: [{
		name: 'text',
		type: 'string'
	},{
		name: 'f_id',
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name');
			return v;
		}
	},{
		name: 'model',
		type: 'string'
	},{
		name: 'version',
		type: 'string'
	},{
		name: 'b_id',
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('rep_id');
			return v;
		}
	},{
		name: 'b_name_j',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name_j');
			return v;
		}
	},{
		name: 'b_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name_e');
			return v;
		}
	},{
		name: 'name',
		type: 'string',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('filename');
			if(Ext.isEmpty(v)) v = r.get('cdi_name_e');
			if(Ext.isEmpty(v)) v = r.get('cdi_name');
			return v;
		}
	},{
		name: 'filename',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'filesize',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'xmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'xmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'xcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('xmax')) && Ext.isNumber(r.get('xmin'))) v = (r.get('xmax')+r.get('xmin'))/2;
			return v;
		}
	},{
		name: 'ymax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'ymin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'ycenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('ymax')) && Ext.isNumber(r.get('ymin'))) v = (r.get('ymax')+r.get('ymin'))/2;
			return v;
		}
	},{
		name: 'zmax',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'zmin',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'zcenter',
		useNull: true,
		defaultValue: null,
		type: 'float',
		convert: function(v, r){
			if(Ext.isEmpty(v) && Ext.isNumber(r.get('zmax')) && Ext.isNumber(r.get('zmin'))) v = (r.get('zmax')+r.get('zmin'))/2;
			return v;
		}
	},{
		name: 'volume',
		useNull: true,
		defaultValue: null,
		type: 'float'
	},{
		name: 'mtime',
		type: 'date',
		dateFormat:'timestamp'
	},

	{
		name: 'seg_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'seg_name',
		type: 'string',
		useNull: true,
		defaultValue: null,
		convert: function(v, r){
			if(Ext.isString(v)) v = v.toUpperCase();
			return v;
		}
	},{
		name: 'seg_color',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'seg_thum_bgcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	},{
		name: 'seg_thum_fgcolor',
		type: 'string',
		defaultValue:'#F0D2A0'
	},

	{
		name: 'path',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cb_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
//	},{
//		name: 'art_id',
//		useNull: true,
//		defaultValue: null,
//		type: 'string'
	},{
		name: 'rep_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'artg_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'
	},{
		name: 'art_ids',
		useNull: true,
		defaultValue: null,
		type: 'auto'

	},{
		name: 'cm_max_num_cdi',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cm_max_entry_cdi',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'rep_entry',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'

	},{
		name: 'modified',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v,r){
			if(Ext.isEmpty(v)){
				if(!Ext.isEmpty(r.data.rep_entry) && !Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi>r.data.rep_entry ? r.data.cm_max_entry_cdi : r.data.rep_entry;
				}
				else if(!Ext.isEmpty(r.data.cm_max_entry_cdi)){
					v = r.data.cm_max_entry_cdi;
				}
				else if(!Ext.isEmpty(r.data.rep_entry)){
//					v = r.data.rep_entry;
				}
			}
			if(!Ext.isEmpty(v) && !Ext.isDate(v)){
				var d = new Date();
				d.setTime(v*1000);
				v=d;
			}
			return v;
		}
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	]
});

Ext.define('ERROR_TWITTER', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'selected',
		type: 'boolean',
		defaultValue:false
	},{
		name: 'rep_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cb_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'bul_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'cdi_name_j',
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
		name: 'tw_user',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'tw_date',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'tw_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'tw_text',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'rtw_fixed',
		defaultValue: false,
		type: 'boolean'
	},{
		name: 'rtw_fixed_version',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'rtw_fixed_date',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'rtw_fixed_time',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v, r){
			if(Ext.isEmpty(v)) v = r.get('rtw_fixed_date');
			return v;
		}
	},{
		name: 'rtw_fixed_epoc',
		useNull: true,
		defaultValue: null,
		type: 'int',
		convert: function(v, r){
			if(Ext.isEmpty(v) && r.get('rtw_fixed_date')) v = (r.get('rtw_fixed_date')).getTime();
			return v;
		}
	},{
		name: 'rtw_fixed_comment',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mca_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},

//PALLETPARTS対応
	{
		name: 'b_id',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('rep_id');
			return v;
		}
	},{
		name: 'f_id',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v =  r.get('cdi_name');
			return v;
		}
	},{
		name: 'model',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('md_abbr');
			return v;
		}
	},{
		name: 'version',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('mv_name_e');
			return v;
		}
	},{
		name: 'tree',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('bul_abbr');
			return v;
		}
	},{
		name: 'name',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('cdi_name_e');
			return v;
		}
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	]
});


Ext.define('HISTORY_MAPPING', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'art_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cb_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
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
		name: 'cdi_name_j',
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
		name: 'cm_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cm_use',
		defaultValue: false,
		type: 'boolean'
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
		dateFormat:'timestamp'
	},

//表示用
	{
		name: 'model',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('md_name_e');
			return v;
		}
	},{
		name: 'version',
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.get('mv_name_e');
			return v;
		}
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	]
});


Ext.define('RECALC', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'rep_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'ci_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'cb_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'md_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mv_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'mr_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'bul_name_e',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'bul_abbr',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'cdi_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'but_depth',
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
		name: 'cdi_name_j',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'rep_entry',
		useNull: true,
		defaultValue: null,
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'rep_thumb',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'rep_recal_state',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'target_record',
		defaultValue: false,
		type: 'boolean'
	},{
		name: 'style',
		useNull: true,
		defaultValue: null,
		type: 'string'
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END
	]
});

Ext.define('ORIGINAL_OBJECT', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'artg_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artg_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
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

Ext.define('CONCEPT_SEGMENT', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'seg_id',
		useNull: true,
		defaultValue: null,
		type: 'int'
	},{
		name: 'seg_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'seg_color',
		useNull: true,
		defaultValue:'#F0D2A0',
		type: 'string'
	},{
		name: 'seg_thum_bgcolor',
		useNull: true,
		defaultValue:'#F0D2A0',
		type: 'string'
	},{
		name: 'seg_thum_bocolor',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'seg_thum_fgcolor',
		useNull: true,
		defaultValue:'#F0D2A0',
		type: 'string'
	},{
		name: 'cdi_names',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'seg_delcause',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'seg_entry',
		type: 'date',
		dateFormat:'timestamp',
	},{
		name: 'seg_use',
		type: 'boolean',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = Ext.isEmpty(r.data.seg_delcause);
			return v;
		}
	},{
		name: 'seg_use_disabled',
		type: 'boolean',
		useNull: true,
		defaultValue: null,
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = (r.data.seg_id===0 ? true : false);
			return v;
		}
	}]
});

Ext.define('BP3D_PROPERTY', {
	extend: 'BP3D',
	fields: [{
		name: 'set_segment_recursively',
		type: 'boolean',
		defaultValue:false
	}]
});

Ext.define('UPLOAD_FOLDER_TREE', {
	extend: 'Ext.data.TreeModel',
//	idProperty: 'artf_id',
	fields: [{
		name: 'id',
		convert: function(value, record) {
			if(Ext.isEmpty(value)) value = record.internalId; //record.get('artf_id');
			return value;
		}
	},{
		name: 'text',
		type: 'string'
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
		name: 'artf_timestamp',
		type: 'date',
		dateFormat:'timestamp',
	},{
		name: 'artf_entry',
		type: 'date',
		dateFormat:'timestamp',
	},{
		name: 'artg_count',
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
		name: 'cm_use',
		defaultValue: false,
		type: 'boolean'
	},{
		name: 'artg_id',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'artg_name',
		useNull: true,
		defaultValue: null,
		type: 'string'
	},{
		name: 'grouppath',
		useNull: true,
		defaultValue: 'art_file',
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
		name: 'path',
		useNull: true,
		type: 'string',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.art_path;
			return v;
		}
	},{
		name: 'art_entry',
		type: 'date',
		dateFormat:'timestamp'
	},{
		name: 'mtime',
		type: 'date',
		dateFormat:'timestamp',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.art_entry;
			return v;
		}
	},
	{
		name: 'selected',
		type: 'boolean',
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.cm_use;
			return v;
		}
	},{
		name: 'name',
		type: 'string',
		useNull: true,
		defaultValue: null,
		convert: function(v,r){
			if(Ext.isEmpty(v)) v = r.data.art_filename;
			return v;
		}
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
	}
	//2016-03-31 START
	,{
		name: 'cmp_id',
		useNull: false,
		defaultValue: 0,
		type: 'int'
	}
	//2016-03-31 END

	]
});

//2016-03-31 START
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
		}
	]
});
//2016-03-31 END
