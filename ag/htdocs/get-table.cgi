#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use File::Basename;
use JSON::XS;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|;

use constant VIEW_PREFIX => qq|reference_|;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
my $query = CGI->new;
&getParams($query,\%FORM,\%COOKIE);
&checkXSS(\%FORM);
&setDefParams(\%FORM,\%COOKIE);
&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.$FORM{'type'}.txt");
#flock(LOG,2);
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

print qq|Content-type: text/html; charset=UTF-8\n\n|;

exit unless(exists $COOKIE{'ag_annotation.session'});
exit unless(defined $FORM{'type'} && defined $FORM{'table'});

my %SQL;
my $view_name = VIEW_PREFIX.qq|representation_art|;
$SQL{$view_name}=<<SQL;
CREATE TEMPORARY VIEW $view_name AS
SELECT distinct
  false::boolean            as download,
  '<img align=center width=16 height=16 src="art_images/'||idp.prefix_char||'/'||substring(art.art_serial_char from 1 for 2)||'/'||substring(art.art_serial_char from 3 for 2)||'/'||idp.prefix_char||art.art_serial||'-'||repa.art_hist_serial||'_16x16.gif">' as thumb,
  rep.rep_id                as representation_id,
  repa2.cdi_name            as represented_concept,
  repa2.cdi_name_e          as english_name,
--  rep.rep_serial            as rep_serial,
--  ci.ci_name||cb.cb_name    as concept,
--  cdi.cdi_name              as concept_id,
  md.md_name_e              as model,
  mv.mv_name_e              as compatibility_version,
  art.art_id                as model_component,
  art.art_serial            as serial,
  art.art_name||art.art_ext as filename,
  art.art_timestamp         as timestamp,
  art.art_xmin              as xmin,
  art.art_xmax              as xmax,
  art.art_ymin              as ymin,
  art.art_ymax              as ymax,
  art.art_zmin              as zmin,
  art.art_zmax              as zmax,
  art.art_volume            as volume,
  art.art_cube_volume       as cube_volume,
  art.art_entry             as entry
--  ,idp.prefix_char           as prefix_char,
--  art.art_serial_char       as art_serial_char
FROM representation rep
LEFT JOIN (
    SELECT *
    FROM representation_art
  ) repa ON repa.rep_id  = rep.rep_id
LEFT JOIN (
    SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name
    FROM concept_data_info
  ) cdi ON cdi.ci_id  = rep.ci_id AND
           cdi.cdi_id = rep.cdi_id
LEFT JOIN (
    SELECT concept_info.ci_id, concept_info.ci_name
    FROM concept_info
  ) ci ON ci.ci_id  = rep.ci_id
LEFT JOIN (
    SELECT concept_build.ci_id, concept_build.cb_id, concept_build.cb_name
    FROM concept_build
  ) cb ON cb.ci_id = rep.ci_id AND
          cb.cb_id = rep.cb_id

LEFT JOIN (
    SELECT *,to_char(art_serial,'FM9999990000') as art_serial_char FROM history_art_file
  ) art ON art.art_id=repa.art_id AND art.hist_serial=repa.art_hist_serial
LEFT JOIN (
    select prefix_char::text,prefix_id from id_prefix
  ) idp on idp.prefix_id=art.prefix_id

LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = art.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = art.md_id AND
          mv.mv_id = art.mv_id

--LEFT JOIN (
--    SELECT repa.*,cdi.cdi_name,cdi.cdi_name_e
--    FROM representation_art as repa
--    LEFT JOIN (
--        SELECT rep_id,ci_id,cdi_id from representation where rep_primitive and rep_delcause is null
--      ) rep on rep.rep_id=repa.rep_id
--    LEFT JOIN (
--        SELECT ci_id,cdi_id,cdi_name,cdi_name_e FROM concept_data_info
--      ) cdi on cdi.ci_id=rep.ci_id AND cdi.cdi_id=rep.cdi_id
--    WHERE rep.cdi_id IS NOT NULL
--  ) repa2 ON repa2.art_id = repa.art_id AND repa2.art_hist_serial = repa.art_hist_serial

LEFT JOIN (
    SELECT
     cm.art_id,
     cm.art_hist_serial,
     cm.ci_id,
     cm.cb_id,
     cdi.cdi_name,
     cdi.cdi_name_e
    FROM
     concept_art_map as cm
    LEFT JOIN (
        SELECT
         ci_id,
         cdi_id,
         cdi_name,
         cdi_name_e
        FROM
         concept_data_info
      ) cdi on
         cdi.ci_id=cm.ci_id AND
         cdi.cdi_id=cm.cdi_id
  ) repa2 ON
     repa2.ci_id = rep.ci_id AND
     repa2.cb_id = rep.cb_id AND
     repa2.art_id = repa.art_id AND
     repa2.art_hist_serial = repa.art_hist_serial

WHERE rep.rep_delcause IS NULL
order by art.art_serial
SQL

my $view_name = VIEW_PREFIX.qq|representation|;
$SQL{$view_name}=<<SQL;
CREATE TEMPORARY VIEW $view_name AS
SELECT
  rep.rep_id    as representation_id,
  ci.ci_name||cb.cb_name    as concept,
  cdi.cdi_name  as concept_id,
  md.md_name_e              as model,
  mv.mv_name_e              as version,
  art.art_id                as art_id,
  art.art_serial                as art_serial,
  art.art_name||art.art_ext as filename,
  art.art_timestamp         as timestamp,
  art.art_xmin              as xmin,
  art.art_xmax              as xmax,
  art.art_ymin              as ymin,
  art.art_ymax              as ymax,
  art.art_zmin              as zmin,
  art.art_zmax              as zmax,
  art.art_volume            as volume,
  art.art_cube_volume       as cube_volume,
  art.art_entry             as entry
FROM representation rep
LEFT JOIN (
    SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name
    FROM concept_data_info
  ) cdi ON cdi.ci_id  = rep.ci_id AND
           cdi.cdi_id = rep.cdi_id
LEFT JOIN (
    SELECT concept_info.ci_id, concept_info.ci_name
    FROM concept_info
  ) ci ON ci.ci_id  = rep.ci_id
LEFT JOIN (
    SELECT concept_build.ci_id, concept_build.cb_id, concept_build.cb_name
    FROM concept_build
  ) cb ON cb.ci_id = rep.ci_id AND
          cb.cb_id = rep.cb_id

LEFT JOIN (
    SELECT * FROM history_art_file
  ) art ON art.art_id=rep.art_id AND art.hist_serial=rep.art_hist_serial
LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = art.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = art.md_id AND
          mv.mv_id = art.mv_id

WHERE rep.rep_delcause IS NULL
order by art.art_serial
SQL

my $view_name = VIEW_PREFIX.qq|art_file|;
$SQL{$view_name}=<<SQL;
CREATE TEMPORARY VIEW $view_name AS
SELECT
  md.md_name_e              as model,
  mv.mv_name_e              as version,
  art.art_id                as art_id,
  art.art_serial                as art_serial,
  art.art_name||art.art_ext as filename,
  art.art_timestamp         as timestamp,
  art.art_xmin              as xmin,
  art.art_xmax              as xmax,
  art.art_ymin              as ymin,
  art.art_ymax              as ymax,
  art.art_zmin              as zmin,
  art.art_zmax              as zmax,
  art.art_volume            as volume,
  art.art_cube_volume       as cube_volume,
  art.art_entry             as entry
FROM art_file art
LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = art.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = art.md_id AND
          mv.mv_id = art.mv_id
WHERE art.art_delcause IS NULL
order by art.art_serial
SQL

my $view_name = VIEW_PREFIX.$FORM{'table'};

#DEBUG
if(&existsView($view_name)){
	$dbh->do(qq|drop view $view_name|) or die $dbh->errstr;
}


unless(&existsView($view_name)){
	$dbh->do($SQL{$view_name}) or die $dbh->errstr if(exists $SQL{$view_name});
}
my $columns = &getDbTableColumns($view_name);
exit unless(defined $columns);

if($FORM{'type'} eq 'schema'){
	my @COLS;
	if(defined $FORM{'rep_id'}){
		foreach my $col (@$columns){
			next if($col->{'column_name'} eq 'rep_id' || $col->{'column_name'} eq 'representation_id');
			push(@COLS,$col);
		}
	}else{
		push(@COLS,@$columns);
	}
	print &JSON::XS::encode_json(\@COLS);

}elsif($FORM{'type'} eq 'data'){
	my @cols;
	my $delcause;
	my %name2type;
	foreach my $col (@$columns){
		next if($col->{'data_type'} eq 'bytea');
#		next if($col->{'column_name'} =~ /openid/);
#		if($col->{'column_name'} =~ /_delcause$/){
#			$delcause = $col->{'column_name'};
#			next;
#		}

		if($col->{'data_type'} =~ /^timestamp/){
			push(@cols,'EXTRACT(EPOCH FROM '.$col->{'column_name'}.') as '.$col->{'column_name'});
		}else{
			push(@cols,$col->{'column_name'});
		}
		$name2type{$col->{'column_name'}} = $col->{'data_type'};
	}
	my $sql = qq|select |.join(",",@cols).qq| from $view_name|;

	my @bind_values;
	my @where;

	push(@where,qq|$delcause is null|) if(defined $delcause);
#	print $sql;

	if(defined $FORM{'hash'}){
		my %hash;
		my @info = split("&",$FORM{'hash'});
		foreach my $i (@info){
			$hash{$1} = &url_decode($2) if($i =~ /^(.+)=(.+)$/);
		}
		foreach my $i (keys(%hash)){
			if($i eq 'art_id'){
				my @a = split(",",$hash{$i});
				my @s = split("","?"x(scalar @a));
				push(@where,qq|art_id in (|.join(",",@s).qq|)|);
				push(@bind_values,@a);
			}else{
				next;
			}
		}
	}elsif(defined $FORM{'rep_id'}){
		push(@where,qq|representation_id='$FORM{'rep_id'}'|);


	}

	if(scalar @where > 0){
		$sql .= qq| where | ;
		$sql .= join(" AND ",@where);
	}

	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	my $rows = $sth->rows();
	$sth->finish;
	undef $sth;

#38:$FORM{sort}=[[{"property":"filename","direction":"ASC"}]]
	if(defined $FORM{'sort'}){
		my $sort_arr;
		eval{$sort_arr = &JSON::XS::decode_json($FORM{'sort'});};
		if(defined $sort_arr){
			my @S;
			foreach my $s (@$sort_arr){
				push(@S,qq|$s->{'property'} $s->{'direction'}|);
			}
			$sql .= qq| order by |.join(",",@S);
		}
	}

	$sql .= qq| limit $FORM{'limit'}| if(defined $FORM{'limit'});
	$sql .= qq| offset $FORM{'start'}| if(defined $FORM{'start'});

#print LOG __LINE__,qq|:\$sql=[$sql]\n|;
#print LOG __LINE__,qq|:\@bind_values=[|,join(",",@bind_values),qq|]\n|;

	my $datas = {
		total => $rows,
		datas=>[]
	};
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values) or die $dbh->errstr;
	}else{
		$sth->execute() or die $dbh->errstr;
	}
	while(my $href = $sth->fetchrow_hashref){
		foreach my $column_name (keys(%$href)){
			$href->{$column_name} += 0 unless($name2type{$column_name} eq 'text' || $name2type{$column_name} =~ /^character/);
		}
		push(@{$datas->{'datas'}},$href);
	}
	$sth->finish;
	undef $sth;
	print &JSON::XS::encode_json($datas) if(defined $datas);

}elsif($FORM{'type'} eq 'html'){
	my $title = defined $FORM{'rep_id'} ? $FORM{'rep_id'} : $FORM{'table'};
	my $EXT_PATH = qq|js/extjs-4.1.1|;
	my @CSS = (
		"$EXT_PATH/resources/css/ext-all.css",
		"$EXT_PATH/ux/css/CheckColumn.css",
	);
	my @JS = (
		"js/jquery.js",
		"$EXT_PATH/ext-all.js",
		"$EXT_PATH/ux/CheckColumn.js",
	);
	push(@JS,"$EXT_PATH/locale/ext-lang-ja.js") if($FORM{lng} eq "ja");
	print <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<!-- CSS -->
HTML
	foreach my $css (@CSS){
		next unless(-e $css);
		my $mtime = (stat($css))[9];
		print qq|<link rel="stylesheet" href="$css?$mtime" type="text/css" media="all">\n|;
	}
	print <<HTML;
<!-- Javascript -->
HTML
	foreach my $js (@JS){
		next unless(-e $js);
		my $mtime = (stat($js))[9];
		print qq|<script type="text/javascript" src="$js?$mtime"></script>\n|;
	}
	print <<HTML;
<title>$title</title>
<style type="text/css">
.download_btn {
	background-image: url(css/ico_dl_b.png) !important;
}
a.external{
	color: #0044cc;
	background: url(css/external.png) no-repeat right center; !important;
	padding-right: 12px;
}
</style>
<script type="text/javascript"><!--
Ext.BLANK_IMAGE_URL = "$EXT_PATH/resources/themes/images/default/tree/s.gif";
Ext.Loader.setConfig({enabled: true});
Ext.require([
	'*'
]);
Ext.onReady(function() {
//	Ext.state.Manager.setProvider(new Ext.state.CookieProvider()); //ソート順とかをCookieに登録する為に必要らしい

	Ext.QuickTips.init();
	bp3d.init();
});
var bp3d = {
	init:function(){
		var self = this;
		Ext.Ajax.request({
			url: '$cgi_name$cgi_ext',
			params: {
				type: 'schema',
				table: '$FORM{'table'}',
				rep_id: '$FORM{'rep_id'}',
				hash: window.location.hash.substr(1)
			},
			success: function(response){
				var json;
				try{json = Ext.decode(response.responseText);}catch(e){}
				if(Ext.isEmpty(json)) return;

				var fields = [];
				var columns = [Ext.create('Ext.grid.RowNumberer',{minWidth:34})];
				Ext.Array.each(json,function(field,i,a){
					var type;
					var column_text = field.column_name.replace("_"," ");
					if(field.column_name=='thumb'){
						fields.push({
							name: field.column_name,
							type:'string'
						});
						columns.push({
							dataIndex: field.column_name,
//							text: column_text,
							menuDisabled:true,
							hideable: false,
							resizable: false,
							width: 28
						});
					}else if(field.data_type=='text'){
						fields.push({
							name: field.column_name,
							type:'string'
						});
						columns.push({
							dataIndex: field.column_name,
							text: column_text,
							hidden: (field.column_name=='filename' ? true : false),
							flex: field.column_name=='filename' ? 4 : (field.column_name=='model' ? 2 : 1),
							minWidth: 70
						});
					}else if(field.data_type=='integer'){
						fields.push({
							name: field.column_name,
							type:'int'
						});
						columns.push({
							dataIndex: field.column_name,
							text: column_text,
							hidden: (field.column_name=='serial' ? true : false),
							xtype: 'numbercolumn',
							format:'0,000',
							align: 'right',
							width: 50
						});
					}else if(field.data_type=='numeric'){
						fields.push({
							name: field.column_name,
							type:'float'
						});
						columns.push({
							dataIndex: field.column_name,
							text: column_text,
							hidden: (field.column_name=='cube_volume' ? true : false),
							xtype: 'numbercolumn',
							format:'0,000.0000',
							align: 'right',
							width: 70
						});
					}else if(field.data_type=='boolean'){
						fields.push({
							name: field.column_name,
							type:'boolean'
						});
						columns.push({
							dataIndex: field.column_name,
//							text: column_text,
							xtype: 'checkcolumn',
							menuDisabled:true,
							hideable: false,
							resizable: false,
							align: 'center',
							width: 26,
							listeners: {
								checkchange: function(column, recordIndex, checked, record){
									var gridpanels = Ext.ComponentQuery.query('gridpanel');
									if(Ext.isEmpty(gridpanels)) return;
									var selModel = gridpanels[0].getSelectionModel();
									if(Ext.isEmpty(selModel)) return;
									var records = selModel.getSelection();
									if(records.length>0) selModel.deselectAll(true);

									record.commit();

									if(records.length>0) selModel.select(records);
								}
							}
						});
					}else if(field.column_name.match(/^timestamp/) && field.data_type.match(/^timestamp/)){
						fields.push({
							name: field.column_name,
							type:'date',
							dateFormat:'timestamp'
						});
						columns.push({
							dataIndex: field.column_name,
							text: column_text,
							xtype: 'datecolumn',
							format:'Y/m/d',
							width: 70
						});
					}else if(field.data_type.match(/^timestamp/)){
						fields.push({
							name: field.column_name,
							type:'date',
							dateFormat:'timestamp'
						});
						columns.push({
							dataIndex: field.column_name,
							text: column_text,
							xtype: 'datecolumn',
							format:'Y/m/d H:i:s',
							width: 120
						});
					}
				});

				var store = new Ext.data.JsonStore({
					autoDestroy: true,
					autoLoad:true,
					remoteSort:true,
					proxy: {
						type: 'ajax',
						url: '$cgi_name$cgi_ext',
						extraParams: {
							type: 'data',
							table: '$FORM{'table'}',
							rep_id: '$FORM{'rep_id'}',
							hash: window.location.hash.substr(1)
						},
						reader: {
							type: 'json',
							root: 'datas',
						},
						actionMethods : {
							create : "POST",
							read   : "POST",
							update : "POST",
							destroy: "POST"
						}
					},
					fields: fields,
					listeners: {
						update: function(store,record,operation){
							if(operation != Ext.data.Model.COMMIT) return;
							var idx = store.findBy(function(r,id){
								if(r.data.download) return true;
							});
							Ext.getCmp('download-btn').setDisabled(idx>=0?false:true);
						}
					}
				});

				Ext.create('Ext.container.Viewport', {
					layout: 'border',
					items: [{
//						title: '$FORM{'table'}',
						region: 'center',
						xtype: 'grid',
						store: store,
						columns: columns,
						selModel: {
							mode: 'MULTI',
							listeners: {
								select: function(sm, record, index, eOpt){
									console.log("select():["+index+"]");
								},
								selectionchange: function(sm, records){
									console.log("selectionchange():["+records.length+"]");
									Ext.getCmp('selected-onoff-btn').setDisabled(sm.getCount()>0?false:true);
								}
							}
						},
						dockedItems: [{
							xtype: 'toolbar',
							dock: 'top',
							items:[{
								text: 'All (<img src=$EXT_PATH/ux/css/checked.gif align=top width=16 height=16>/<img src=$EXT_PATH/ux/css/unchecked.gif align=top width=16 height=16>)',
								id: 'all-onoff-btn',
								listeners: {
									click: {
										fn: function(b){
											var gridpanels = Ext.ComponentQuery.query('gridpanel');
											if(Ext.isEmpty(gridpanels)) return;
											var selModel = gridpanels[0].getSelectionModel();
											if(Ext.isEmpty(selModel)) return;
											var store = gridpanels[0].getStore();
											if(Ext.isEmpty(store)) return;

											var records = selModel.getSelection();
											if(records.length>0) selModel.deselectAll(true);

											var idx = store.findBy(function(r,id){
												if(!r.data.download) return true;
											});
											var checked = idx>=0 ? true : false;
											store.suspendEvents(true);
											Ext.each(store.getRange(),function(r,i,a){
												if(r.data.download == checked) return true;
												r.beginEdit();
												r.set('download',checked);
												r.commit(false);
												r.endEdit(false,['download']);
											});
											store.resumeEvents();

											if(records.length>0) selModel.select(records);
										},
										buffer: 100
									}
								}
							},'-',{
								disabled: true,
								text: 'Selected (<img src=$EXT_PATH/ux/css/checked.gif align=top width=16 height=16>/<img src=$EXT_PATH/ux/css/unchecked.gif align=top width=16 height=16>)',
								id: 'selected-onoff-btn',
								listeners: {
									click: {
										fn: function(b){
											var gridpanels = Ext.ComponentQuery.query('gridpanel');
											if(Ext.isEmpty(gridpanels)) return;
											var selModel = gridpanels[0].getSelectionModel();
											if(Ext.isEmpty(selModel)) return;
											var records = selModel.getSelection();
											selModel.deselectAll(true);
											var checked = false;
											Ext.each(records,function(r,i,a){
												if(r.data.download) return true;
												checked = true;
												return false;
											});

											store.suspendEvents(true);
											Ext.each(records,function(r,i,a){
												if(r.data.download == checked) return true;
												r.beginEdit();
												r.set('download',checked);
												r.commit(false);
												r.endEdit(false,['download']);
											});
											store.resumeEvents();

											selModel.select(records);
										},
										buffer: 100
									}
								}
							},'-']
						},{
							xtype: 'pagingtoolbar',
							store: store,   // same store GridPanel is using
							dock: 'bottom',
							displayInfo: true,
							displayMsg: self.lng.displayMsg,
							items:['-',{
								text: self.lng.all_downloads,
								iconCls: 'download_btn',
								listeners: {
									click: {
										fn: function(b){
											self.download({all_downloads:1});
										},
										buffer: 100
									}
								}
							},'-',{
								disabled: true,
								text: self.lng.download,
								id: 'download-btn',
								iconCls: 'download_btn',
								listeners: {
									click: {
										fn: function(b){
											var gridpanels = Ext.ComponentQuery.query('gridpanel');
											if(Ext.isEmpty(gridpanels)) return;
											var store = gridpanels[0].getStore();
											if(Ext.isEmpty(store)) return;
											var ids = [];
											Ext.each(store.getRange(),function(r,i,a){
												if(!r.data.download) return true;
												ids.push(r.data.model_component);
											});
											self.download({ids:ids});
										},
										buffer: 100
									}
								}
							},'-',{
								xtype: 'tbitem',
								html: '<a class="external" target="_blank" href="http://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html">'+self.lng.license+'</a>'
							},'-']
						}]
					}]
				});
			},
			failure: function(response, opts) {
				console.log('server-side failure with status code ' + response.status);
			}
		});
	},
	download: function(params){
		params = params || {};
		var form_name = 'form_download';
		if(!document.forms[form_name]){
			var form = \$('<form>').attr({
				action: "download.cgi",
				method: "POST",
				name:   form_name,
				id:     form_name,
				style:  "display:none;"
			}).appendTo(\$(document.body));
			var input = \$('<input type="hidden" name="rep_id" value="$FORM{'rep_id'}">').appendTo(form);
			var input = \$('<input type="hidden" name="type" value="art_file">').appendTo(form);
			var input = \$('<input type="hidden" name="all_downloads">').appendTo(form);
			var input = \$('<input type="hidden" name="ids">').appendTo(form);
		}
		document.forms[form_name].all_downloads.value = '';
		document.forms[form_name].all_downloads.ids = '';
		if(params.all_downloads){
			document.forms[form_name].all_downloads.value = 1;
		}else if(params.ids){
			document.forms[form_name].ids.value = Ext.encode(params.ids);
		}else{
			return;
		}
		document.forms[form_name].submit();
	},
	lng : {
		displayMsg: '{0} - {1} / {2}',
HTML
	if($FORM{lng} eq "ja"){
		print <<HTML;
		all_downloads : '一括ダウンロード',
		download : 'ダウンロード',
		license : 'ライセンス事項'
HTML
	}else{
		print <<HTML;
		all_downloads : 'All downloads',
		download : 'Download',
		license : 'License terms'
HTML
	}
	print <<HTML;
	}
};
// --></script>
</head>
<body>
</body>
</html>
HTML
}
#close(LOG);
