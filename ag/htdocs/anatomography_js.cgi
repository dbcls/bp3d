#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my $disEnv = &getDispEnv();
my $additionalModelsImpossible = $disEnv->{additionalModelsImpossible};
my $agInterfaceType = $disEnv->{agInterfaceType};
my $bgcolorTransparentHidden = $disEnv->{bgcolorTransparentHidden};
my $copyHidden = $disEnv->{copyHidden};
my $defColorHidden = $disEnv->{defColorHidden};
my $groupHidden = $disEnv->{groupHidden};
my $legendPanelHidden = $disEnv->{legendPanelHidden};
my $pinPanelHidden = $disEnv->{pinPanelHidden};
my $sectionalViewHidden = $disEnv->{sectionalViewHidden};
my $palletSelectAllHidden = $disEnv->{palletSelectAllHidden};
my $sampleLatestVersionHidden = $disEnv->{sampleLatestVersionHidden};
my $coordinateSystemHidden = $disEnv->{coordinateSystemHidden};
my $savePanelHidden = $disEnv->{savePanelHidden};
my $useUniversalID = $disEnv->{useUniversalID};
my $controlPanelCollapsible = $disEnv->{controlPanelCollapsible};
my $autoRotationHidden = $disEnv->{autoRotationHidden};
my $addPointElementHidden = $disEnv->{addPointElementHidden};
my $useImagePost = $disEnv->{useImagePost};
my $usePickPalletSelect = $disEnv->{usePickPalletSelect};
my $useColorPicker = $disEnv->{useColorPicker};
my $usePalletValueContextmenu = $disEnv->{usePalletValueContextmenu};
my $hiddenGridColNameJ = $disEnv->{hiddenGridColNameJ};
my $shortURLHidden = $disEnv->{shortURLHidden};
my $linkEmbedHidden = $disEnv->{linkEmbedHidden};

my $moveLeftPalletPanel = $disEnv->{moveLeftPalletPanel};
my $moveLicensesPanel = $disEnv->{moveLicensesPanel};
my $removeGridColValume = $disEnv->{removeGridColValume};
my $removeGridColOrganSystem = $disEnv->{removeGridColOrganSystem};
my $useTabTip = $disEnv->{useTabTip};
my $useClickPickTabSelect = $disEnv->{useClickPickTabSelect};
my $moveGridOrder = $disEnv->{moveGridOrder};
my $modifyAxisOfRotation = $disEnv->{modifyAxisOfRotation};

my $makeExtraToolbar = $disEnv->{makeExtraToolbar};

$additionalModelsImpossible = 'false' unless(defined $additionalModelsImpossible);
$agInterfaceType = '5' unless(defined $agInterfaceType);
$bgcolorTransparentHidden = 'false' unless(defined $bgcolorTransparentHidden);
$copyHidden = 'false' unless(defined $copyHidden);
$defColorHidden = 'false' unless(defined $defColorHidden);
$groupHidden = 'false' unless(defined $groupHidden);
$legendPanelHidden = 'false' unless(defined $legendPanelHidden);
$pinPanelHidden = 'false' unless(defined $pinPanelHidden);
$sectionalViewHidden = 'false' unless(defined $sectionalViewHidden);
$palletSelectAllHidden = 'false' unless(defined $palletSelectAllHidden);
$sampleLatestVersionHidden = 'false' unless(defined $sampleLatestVersionHidden);
$coordinateSystemHidden = 'false' unless(defined $coordinateSystemHidden);
$savePanelHidden = 'false' unless(defined $savePanelHidden);
$useUniversalID = 'true' unless(defined $useUniversalID);
$controlPanelCollapsible = 'true' unless(defined $controlPanelCollapsible);
$autoRotationHidden = 'false' unless(defined $autoRotationHidden);
$addPointElementHidden = 'false' unless(defined $addPointElementHidden);
$useImagePost = 'true' unless(defined $useImagePost);
$usePickPalletSelect = 'true' unless(defined $usePickPalletSelect);
$useColorPicker = 'true' unless(defined $useColorPicker);
$usePalletValueContextmenu = 'true' unless(defined $usePalletValueContextmenu);
$hiddenGridColNameJ = 'true' unless(defined $hiddenGridColNameJ);
$moveLeftPalletPanel = 'true' unless(defined $moveLeftPalletPanel);
$moveLicensesPanel = 'true' unless(defined $moveLicensesPanel);
$removeGridColValume = 'true' unless(defined $removeGridColValume);
$removeGridColOrganSystem = 'true' unless(defined $removeGridColOrganSystem);
$useTabTip = 'true' unless(defined $useTabTip);
$useClickPickTabSelect = 'true' unless(defined $useClickPickTabSelect);
$moveGridOrder = 'true' unless(defined $moveGridOrder);
$modifyAxisOfRotation = 'true' unless(defined $modifyAxisOfRotation);
$shortURLHidden = 'false' unless(defined $shortURLHidden);
$linkEmbedHidden = 'false' unless(defined $linkEmbedHidden);

$makeExtraToolbar = 'true' unless(defined $makeExtraToolbar);

my $linkWindowItemAnchor;
if($shortURLHidden ne 'true'){
	$linkWindowItemAnchor = $linkEmbedHidden ne 'true' ? '100% -216' : '100% -160';
}else{
	$linkWindowItemAnchor = $linkEmbedHidden ne 'true' ? '100% -233' : '100% -176';
}

my $sampleLatestVersionChecked = $sampleLatestVersionHidden eq 'false' ? 'true' : 'false';

my $gridColHiddenUniversalID = $useUniversalID eq 'true' ? 'false' : 'true';
my $gridColFixedUniversalID = $useUniversalID eq 'true' ? 'false' : 'true';
my $gridColHiddenID = $useUniversalID eq 'true' ? 'true' : 'false';


$useColorPicker = 'false';

#my $urlTwitterTweetAG = qq|twitter/tweet-ag.html?hashtags=anagra|;
my $urlTwitterTweetAG = qq|twitter/tweet-ag.html?hashtags=anagra&text=Anatomography|;

my $dbh = &get_dbh();

#my $CGI = (
#	"animation" => $IntermediateServerPath."animation.cgi",
#	"clip"      => $IntermediateServerPath."clip.cgi",
#	"focus"     => $IntermediateServerPath."focus.cgi",
#	"focusClip" => $IntermediateServerPath."focusClip.cgi",
#	"image"     => $IntermediateServerPath."image.cgi",
#	"pick"      => $IntermediateServerPath."pick.cgi",
#	"point"     => $IntermediateServerPath."point.cgi",
#	"print"     => $IntermediateServerPath."print.cgi"
#);


#require "anatomography_locale.pl";
my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));
my %COOKIE = ();
&getCookie(\%COOKIE);

#my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
#my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
#open(LOG,">> log.txt");
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "\$ENV{$key}=[",$ENV{$key},"]\n";
#}

if(!exists($FORM{tp_ap}) && exists($COOKIE{'ag_annotation.session'})){
	my $session = &AG::login::getSession($COOKIE{'ag_annotation.session'});
	$FORM{tp_ap} = join("&",@$session) if(defined $session);
}

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(exists($FORM{lng}) && $FORM{lng} !~ /^(ja|en:?)$/);
$FORM{lng} = "en" unless(exists($FORM{lng}));

$agInterfaceType = '5' if(exists($FORM{tp_md}) && defined $agInterfaceType && $agInterfaceType ne '5');

my $gridColHiddenNameJ = 'false';
my $gridColHiddenNameK = 'true';
if($hiddenGridColNameJ eq 'true'){
	if($FORM{lng} eq 'ja'){
		$gridColHiddenNameK = 'false';
		$gridColHiddenUniversalID = 'true';
		$gridColFixedUniversalID = 'true';
		$gridColHiddenID = 'true';
	}else{
		$gridColHiddenNameJ = 'true';
		$gridColHiddenID = 'true';
	}
}

#print LOG __LINE__,":",join("\n",@INC),"\n";

my %LOCALE = ();

#use File::Basename;
#my @extlist = qw|.cgi|;
#my($name,$dir,$ext) = fileparse($0,@extlist);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
open(LOG,">> logs/".(exists $COOKIE{'ag_annotation.session'} ? $COOKIE{'ag_annotation.session'} : '')."$cgi_name\_$FORM{lng}.txt");
print LOG "\n[$logtime]:$0\n";
print LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':%FORM='.&Data::Dumper::Dumper(\%FORM);
print LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':%COOKIE='.&Data::Dumper::Dumper(\%COOKIE);
print LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':%ENV='.&Data::Dumper::Dumper(\%ENV);

#close(LOG);

#my $pwd = `pwd`;
#$pwd =~ s/\s*$//g;
#$pwd =~ s/^\s*//g;
#print LOG __LINE__,":$pwd\n";
require "common_locale.pl";
my %LOCALE_BP3D = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_BP3D)){
	$LOCALE{$key} = $LOCALE_BP3D{$key}
}
undef %LOCALE_BP3D;

#my $pwd = `pwd`;
#$pwd =~ s/\s*$//g;
#$pwd =~ s/^\s*//g;
#print LOG __LINE__,":$pwd\n";
require "anatomography_locale.pl";
my %LOCALE_ANA = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_ANA)){
	$LOCALE{$key} = $LOCALE_ANA{$key}
}
undef %LOCALE_ANA;

foreach my $key (sort keys(%LOCALE)){
	print LOG __LINE__,":\$LOCALE{$key}=[",$LOCALE{$key},"]\n";
}

close(LOG);

if(scalar @ARGV == 1 && $ARGV[0] eq "--version"){
	my($prog_cat, $prog_dir, $prog_file) = File::Spec->splitpath($0);
	print "\nProgram: $prog_file\n\n";
	foreach my $module (sort keys %INC) {
		my $full_path = $INC{$module};
		my $package = $module;
		$package =~ s/\.p[lm]$//;
		$package =~ s!/!::!g;
		my $version = "";
		eval "\$version = \$${package}::VERSION;";
		$version = "undef" if (!$version);
		printf("%7s %-20s\n", $version, $package);
	}
	exit;
}

#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
my $is_success;
my $parentURL = $FORM{parent} if(exists($FORM{parent}));
#delete $FORM{parent} if(exists($FORM{parent}));

if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);



#my %LOCALE = &getLocale($FORM{lng});

my $MAX_YRANGE = 1800;
#my $MAX_YRANGE = 900;
#my $TIME_FORMAT = "Y/m/d H:i:s";
#my $DATE_FORMAT = "Y/m/d";

#my $DEF_COLOR = &getDefaultColor();

my @MODEL_VERSION = ();
{
	my $sql;
	$sql = qq|select mv.md_id,mv.mv_id,mv.mv_version|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(mv.mv_name_j,mv.mv_name_e)|;
	}else{
		$sql .= qq|,mv.mv_name_e|;
	}
	$sql .= qq| from model_version as mv left join(select * from model) as md on (md.md_id=mv.md_id) where mv.mv_delcause is null order by md.md_order,mv.mv_order|;

	my $md_id;
	my $mv_id;
	my $mv_version;
	my $mv_name;
	my $sth_model_version = $dbh->prepare($sql);
	$sth_model_version->execute();
	my $column_number = 0;
	$sth_model_version->bind_col(++$column_number, \$md_id, undef);
	$sth_model_version->bind_col(++$column_number, \$mv_id, undef);
	$sth_model_version->bind_col(++$column_number, \$mv_version, undef);
	$sth_model_version->bind_col(++$column_number, \$mv_name, undef);
	while($sth_model_version->fetch){
	#	my @TEMP = ($md_id,$mv_id,$tgi_version,$tgi_name);
	#	my @TEMP = ($md_id,$mv_id,$tgi_name,$tgi_name);
		my @TEMP = ($mv_name,$md_id,$mv_id,$mv_version);
		push(@MODEL_VERSION,\@TEMP);
	}
	$sth_model_version->finish;
	undef $sth_model_version;
}


my $tg_id;
my $tgi_version;
=pod
{
	my $sql;
	$sql = qq|select tg_id|;
	if($FORM{lng} eq "ja"){
		$sql .= qq|,COALESCE(tgi_name_j,tgi_name_e)|;
	}else{
		$sql .= qq|,tgi_name_e|;
	}
	$sql .= qq| from tree_group_item where tgi_port is not null and tgi_delcause is null order by tg_id,tgi_id,tgi_order|;
	my $sth_tree_group_item = $dbh->prepare($sql);
	$sth_tree_group_item->execute();
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
	$sth_tree_group_item->fetch;
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}
=cut
$tg_id = $MODEL_VERSION[0][1] unless(defined $tg_id);
$tgi_version = $MODEL_VERSION[0][0] unless(defined $tgi_version);

my $bul_id=3;


if(exists $ENV{REQUEST_METHOD}){
	print qq|Content-type: text/javascript; charset=UTF-8\n|;
	print qq|\n|;
}

#print qq|/*\n|;
#foreach my $key (sort keys(%LOCALE)){
#	print qq|$key=$LOCALE{$key}\n|;
#}
#print qq|*/\n|;

print <<HTML;
var controlPanelCollapsible = $controlPanelCollapsible;
if(controlPanelCollapsible && window.screen.width>1024){
	controlPanelCollapsible = false;
}
//2011-09-07
controlPanelCollapsible = true;


function callback_print_image(form){
	while(form.lastChild){
		form.removeChild(form.lastChild);
	}
	var doc = form.ownerDocument;
	var param = Ext.urlDecode(makeAnatomoPrm());
	for(var key in param){
		var node = doc.createElement('input');
		node.name = key;
		node.type = 'hidden';
		node.value = param[key];
		form.appendChild(node);
	}
	form.submit();
};

var ag_parts_gridpanel_checkColumn = new Ext.grid.CheckColumn({
	header    : "Select",
	dataIndex : 'zoom'
});

var ag_parts_gridpanel_excludeColumn = new Ext.grid.CheckColumn({
	header    : "Remove",
	dataIndex : 'exclude',
	id        : 'exclude',
	width     : 50,
	resizable : false,
	sortable  : true,
	renderer  : bp3s_parts_gridpanel_checkbox_renderer
});

var ag_parts_gridpanel_pointColumn = new Ext.grid.CheckColumn({
	header    : 'Point',
	dataIndex : 'point',
	id        : 'point',
	width     : 40,
	resizable : false,
	sortable  : true,
	renderer  : bp3s_parts_gridpanel_point_checkbox_renderer
});

var ag_parts_gridpanel_cols_value_contextmenu = null;

var ag_parts_gridpanel_col_version = {
	dataIndex : 'version',
	header    : 'Version',
	id        : 'version',
	sortable  : true,
	hidden    : true,
	renderer  : bp3s_parts_gridpanel_renderer
};
var ag_parts_gridpanel_col_rep_id = {
	dataIndex : 'b_id',
	header    : get_ag_lang('REP_ID'),
	id        : 'b_id',
	sortable  : true,
	hidden    : $gridColHiddenID,
	renderer  : bp3s_parts_gridpanel_renderer
};
var ag_parts_gridpanel_col_cdi_name = {
	dataIndex : 'f_id',
	header    : get_ag_lang('CDI_NAME'),
	id        : 'f_id',
	sortable  : true,
	hidden    : $gridColHiddenID,
	renderer  : bp3s_parts_gridpanel_renderer
};
var ag_parts_gridpanel_col_color = {
	dataIndex : 'color',
	header    : 'Color',
	id        : 'color',
	width     : 40,
	resizable : false,
	sortable  : true,
	renderer  : bp3s_parts_gridpanel_color_renderer,
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
	editor    : new Ext.ux.ColorPickerField({
		menuListeners : {
			select: function(e, c){
				this.setValue(c);
				try{var record = Ext.getCmp('ag-parts-gridpanel')._edit.record;}catch(e){_dump("color:"+e);}
				if(record){
					record.beginEdit();
					record.set('color',"#"+c);
					record.commit();
					record.endEdit();
				}
			},
			show : function(){ // retain focus styling
				this.onFocus();
			},
			hide : function(){
				this.focus.defer(10, this);
			},
			beforeshow : function(menu) {
				try {
					if (this.value != "") {
						menu.palette.select(this.value);
					}else{
						this.setValue("");
						var el = menu.palette.el;
						if(menu.palette.value){
							try{el.child("a.color-"+menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
							menu.palette.value = null;
						}
					}
				}catch(ex){}
			}
		}
HTML
}else{
	print <<HTML;
	editor    : new Ext.ux.ColorField({
		listeners: {
			select: function(e, c){
				try{var record = Ext.getCmp('ag-parts-gridpanel')._edit.record;}catch(e){_dump("color:"+e);}
				if(record){
					record.beginEdit();
					record.set('color',"#"+c);
					record.commit();
					record.endEdit();
				}
			}
		}
HTML
}
print <<HTML;
	})
};
var ag_parts_gridpanel_col_opacity = {
	dataIndex :'opacity',
	header    :'Opacity',
	id        :'opacity',
	width     : 50,
	resizable : false,
	sortable  : true,
	align     : 'right',
	renderer  : bp3s_parts_gridpanel_combobox_renderer,
	editor    : new Ext.form.ComboBox({
		typeAhead: true,
		triggerAction: 'all',
		store : ag_parts_gridpanel_col_opacity_arr,
		lazyRender:true,
		listClass: 'x-combo-list-small',
		listeners     : {
			'select' : function(combo,record,index){
				try{var record = Ext.getCmp('ag-parts-gridpanel')._edit.record;}catch(e){_dump("opacity:"+e);}
				if(record){
					record.beginEdit();
					record.set('opacity',combo.getValue());
					record.commit();
					record.endEdit();
				}
			},scope : this
		}
	})
};
var ag_parts_gridpanel_col_representation = {
	dataIndex : 'representation',
	header    : get_ag_lang('ANATOMO_REP_LABEL'),
	id        : 'representation',
	hidden    : true,
	sortable  : true,
	width     : 84,
	resizable : false,
	renderer  : bp3s_parts_gridpanel_combobox_renderer,
	editor    : new Ext.form.ComboBox({
		typeAhead: true,
		triggerAction: 'all',
		store : ag_parts_gridpanel_col_representation_arr,
		lazyRender:true,
		listClass: 'x-combo-list-small',
		listeners     : {
			'select' : function(combo,record,index){
				try{var record = Ext.getCmp('ag-parts-gridpanel')._edit.record;}catch(e){_dump("representation:"+e);}
				if(record){
					record.beginEdit();
					record.set('representation',combo.getValue());
					record.commit();
					record.endEdit();
				}
			},scope : this
		}
	})
};
var ag_parts_gridpanel_col_value = {
	dataIndex : 'value',
	header    : 'Value',
	id        : 'value',
	hidden    : true,
	sortable  : true,
	renderer  : bp3s_parts_gridpanel_renderer,
	editor    : new Ext.form.TextField({
		allowBlank: true
	})
};
var ag_parts_gridpanel_col_organsys = {
	dataIndex : 'organsys',
	header    : get_ag_lang('GRID_TITLE_ORGANSYS'),
	id        : 'organsys',
	sortable  : true,
	hidden    : true,
	renderer  : bp3s_parts_gridpanel_renderer
};
var ag_parts_gridpanel_col_entry = {
	dataIndex : 'entry',
	header    : get_ag_lang('GRID_TITLE_MODIFIED'),
	id        : 'entry',
	sortable  : true,
	hidden    : true,
	renderer  : bp3s_parts_gridpanel_date_renderer
};

var ag_parts_gridpanel_cols = [
	{dataIndex:'tg_id',     header:'Model',                           id:'tg_id',     sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_group_renderer, fixed:$groupHidden},
HTML
say qq|	ag_parts_gridpanel_col_version,| if($moveGridOrder ne 'true');
print <<HTML;
	{dataIndex:'conv_id',   header:'ConversionID',                    id:'conv_id',   sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer, fixed:$groupHidden},
	{dataIndex:'common_id', header:'UniversalID',                     id:'common_id', sortable: true,  hidden:$gridColHiddenUniversalID, fixed:$gridColFixedUniversalID, renderer:bp3s_parts_gridpanel_commonid_renderer},
HTML
say qq|	ag_parts_gridpanel_col_rep_id,| if($moveGridOrder ne 'true');
say qq|	ag_parts_gridpanel_col_cdi_name,| if($moveGridOrder ne 'true');
print <<HTML;
//	{dataIndex:'name_j',    header:get_ag_lang('GRID_TITLE_NAME_J'),      id:'name_j',    sortable: true,  hidden:$gridColHiddenNameJ, renderer:bp3s_parts_gridpanel_renderer},
//	{dataIndex:'name_k',    header:get_ag_lang('GRID_TITLE_NAME_K'),      id:'name_k',    sortable: true,  hidden:$gridColHiddenNameK,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'name_e',    header:get_ag_lang('DETAIL_TITLE_NAME_E'),                         id:'name_e',    sortable: true,  hidden:false, renderer:bp3s_parts_gridpanel_renderer},
//	{dataIndex:'name_l',    header:'Latina',                          id:'name_l',    sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
HTML
if($moveGridOrder ne 'true'){
	print <<HTML;
//	{dataIndex:'phase',     header:get_ag_lang('GRID_TITLE_PHASE'),       id:'phase',     sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	ag_parts_gridpanel_col_entry,
HTML
}else{
	print <<HTML;
	ag_parts_gridpanel_col_color,
	ag_parts_gridpanel_col_opacity,
	ag_parts_gridpanel_excludeColumn,
	ag_parts_gridpanel_col_value,
//	ag_parts_gridpanel_col_organsys,
	ag_parts_gridpanel_col_representation,
	ag_parts_gridpanel_col_rep_id,
	ag_parts_gridpanel_col_cdi_name,
HTML
}
print <<HTML;
	{dataIndex:'xmin',      header:'Xmin(mm)',                        id:'xmin',      sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'xmax',      header:'Xmax(mm)',                        id:'xmax',      sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'ymin',      header:'Ymin(mm)',                        id:'ymin',      sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'ymax',      header:'Ymax(mm)',                        id:'ymax',      sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'zmin',      header:'Zmin(mm)',                        id:'zmin',      sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'zmax',      header:'Zmax(mm)',                        id:'zmax',      sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
	{dataIndex:'volume',    header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',    sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
HTML
if($moveGridOrder ne 'true'){
#	print qq|	{dataIndex:'volume',    header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',    sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},\n| if($removeGridColValume ne 'true');
#	print qq|	ag_parts_gridpanel_col_organsys,\n| if($removeGridColOrganSystem ne 'true');
	print <<HTML;
	ag_parts_gridpanel_excludeColumn,
	ag_parts_gridpanel_col_color,
	ag_parts_gridpanel_col_opacity,
	ag_parts_gridpanel_col_representation,
	ag_parts_gridpanel_col_value
HTML
}else{
	print <<HTML;
	ag_parts_gridpanel_col_version,
	ag_parts_gridpanel_col_entry
HTML
}
if($addPointElementHidden ne 'true'){
	print <<HTML;
	,ag_parts_gridpanel_pointColumn
HTML
}
print <<HTML;
];

var ag_parts_gridpanel = new Ext.grid.EditorGridPanel({
	id             : 'ag-parts-gridpanel',
	stateful       : true,
	stateId        : 'ag-parts-gridpanel',
	title          : 'Pallet',
//	columns        : ag_parts_gridpanel_cols,
	cm             : new Ext.grid.ColumnModel(ag_parts_gridpanel_cols),
	enableDragDrop : true,
	stripeRows     : true,
	columnLines    : true,
//	region         : 'center',
	width          : 300,
	minWidth       : 150,
	loadMask       : true,
	maskDisabled   : true,
	split          : false,
	border         : false,
	style          : 'border-right-width:1px',
HTML
if($addPointElementHidden ne 'true'){
	print <<HTML;
	plugins        : [ag_parts_gridpanel_checkColumn,ag_parts_gridpanel_excludeColumn,ag_parts_gridpanel_pointColumn],
HTML
}else{
	print <<HTML;
	plugins        : [ag_parts_gridpanel_checkColumn,ag_parts_gridpanel_excludeColumn],
HTML
}
print <<HTML;
	clicksToEdit   : 1,
	trackMouseOver : true,
	selModel : new Ext.grid.RowSelectionModel({
		listeners: {
			'rowdeselect' : function(selModel,rowIndex,record){
				record.beginEdit();
				record.set('zoom',false);
				record.commit(true);
				record.endEdit();
			},
			'rowselect' : function(selModel,rowIndex,record){
				record.beginEdit();
				record.set('zoom',true);
				record.commit(true);
				record.endEdit();
			},
			'selectionchange' : function(selModel){
				try{
					try{Ext.getCmp('ag-pallet-def-color-button').disable();}catch(e){}
					try{Ext.getCmp('ag-pallet-none-color-button').disable();}catch(e){}
					Ext.getCmp('ag-pallet-home-button').disable();
					try{Ext.getCmp('ag-pallet-copy-button').disable();}catch(e){}
					Ext.getCmp('ag-pallet-delete-button').disable();

					Ext.getCmp('ag-pallet-color-pallet-button').disable();
					Ext.getCmp('ag-pallet-opacity-pallet-button').disable();
					Ext.getCmp('ag-pallet-remove-pallet-button').disable();

					\$('td.ag-extra-pallet-default-color>a').addClass('x-item-disabled');
					\$('td.ag-extra-pallet-distinct-color>a').addClass('x-item-disabled');

					if(selModel.getCount()>0){
						try{Ext.getCmp('ag-pallet-def-color-button').enable();}catch(e){}
						try{Ext.getCmp('ag-pallet-none-color-button').enable();}catch(e){}
						try{Ext.getCmp('ag-pallet-copy-button').enable();}catch(e){}
						Ext.getCmp('ag-pallet-delete-button').enable();

						Ext.getCmp('ag-pallet-color-pallet-button').enable();
						Ext.getCmp('ag-pallet-opacity-pallet-button').enable();
						Ext.getCmp('ag-pallet-remove-pallet-button').enable();

						\$('td.ag-extra-pallet-default-color>a').removeClass('x-item-disabled');
						\$('td.ag-extra-pallet-distinct-color>a').removeClass('x-item-disabled');
					}
					if(selModel.getCount()==1){
						var combo;
						var contents_tabs = Ext.getCmp('contents-tab-panel');
						if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
							combo = Ext.getCmp('bp3d-tree-group-combo');
						}else{
							combo = Ext.getCmp('anatomo-tree-group-combo');
						}
						if(combo.getValue()!=selModel.getSelected().get("tg_id")) Ext.getCmp('ag-pallet-home-button').enable();
					}
				}catch(e){
					_dump("441:"+e);
				}
			},
			scope:this
		}
	}),
	bbar : [
HTML
if($palletSelectAllHidden ne 'true'){
	print <<HTML;
		{
			id : 'ag-pallet-select-button',
			tooltip : 'Select All',
			iconCls  : 'pallet_select',
			listeners : {
				'click' : {
					fn : function (button, e) {
						var grid = Ext.getCmp('ag-parts-gridpanel');
						if(grid && grid.rendered) grid.getSelectionModel().selectAll();
					},
					scope: this
				}
			}
		},
		{
			id : 'ag-pallet-unselect-button',
			tooltip : 'Unselect All',
			iconCls  : 'pallet_unselect',
			listeners : {
				'click' : {
					fn : function (button, e) {
						var grid = Ext.getCmp('ag-parts-gridpanel');
						if(grid && grid.rendered) grid.getSelectionModel().clearSelections();
					},
					scope: this
				}
			}
		},
		'-',
HTML
}
print <<HTML;
		{
			hidden : true,
			id        : 'pallet-focus-center-button',
			tooltip   : get_ag_lang('TOOLTIP_FOCUS_CENTER'),
			iconCls   : 'pallet_focus_center',
			listeners : {
				'click' : {
					fn : function (button, e) {
						ag_focus(false,true);
					},
					scope: this
				}
			}
		},
		{
			hidden : true,
			id        : 'pallet-focus-button',
			tooltip   : get_ag_lang('TOOLTIP_FOCUS'),
			iconCls   : 'pallet_focus',
			listeners : {
				'click' : {
					fn : function (button, e) {
						ag_focus();
					},
					scope: this
				}
			}
		},
//		'-',
HTML
if($defColorHidden ne 'true'){
	print <<HTML;
		{
			hidden : true,
			id : 'ag-pallet-def-color-button',
			tooltip   : 'Set distinct color to selected parts',
			iconCls  : 'pallet_def_color',
			disabled : true,
			listeners : {
				'click' : {
					fn : function (button, e) {
						var grid = Ext.getCmp('ag-parts-gridpanel');
						if(!grid || !grid.rendered) return;
						grid.stopEditing();
						var records = grid.getSelectionModel().getSelections();
						if(records.length==0) return;
						var post_data = {f_ids:[]};
						var post_id_hash = {};
						for(var i=0;i<records.length;i++){
							var f_id = records[i].get('f_id');
							post_data.f_ids.push(f_id);
							post_id_hash[f_id] = "";
//_dump("f_id=["+f_id+"]");
						}
						post_data.f_ids = Ext.util.JSON.encode(post_data.f_ids);
						try{post_data.version = Ext.getCmp('anatomo-version-combo').getValue();}catch(e){delete post_data.version;}
						Ext.Ajax.request({
							url     : 'get-contents.cgi',
							method  : 'POST',
							params  : Ext.urlEncode(post_data),
							success : function(conn,response,options){
//_dump("success()");
								try{
									try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
									var store = Ext.getCmp('ag-parts-gridpanel').getStore();

										getRandomColor2 = function(bc,y){
											var c;
											do{
												c = Math.ceil(Math.random() * parseInt("FF", 16));
											}while(Math.abs(c-bc)<=10);
											c = c.toString(16);
											while(c.length<2){ c = '0' + c; }
											return c;
										};
										getRandomColor = function(){
											var prm_record = ag_param_store.getAt(0);
											var bg_rgb = prm_record.get('bg_rgb');
											var bg_r = parseInt(bg_rgb.substr(0,2),16);
											var bg_g = parseInt(bg_rgb.substr(2,2),16);
											var bg_b = parseInt(bg_rgb.substr(4,2),16);
											var bg_y = bg_r*0.299 + bg_g*0.587 + bg_b*0.114;

											var r = getRandomColor2(bg_r,bg_y);
											var g = getRandomColor2(bg_g,bg_y);
											var b = getRandomColor2(bg_b,bg_y);
											return ('#'+r+g+b).toUpperCase();
										};


									if(results && results.images && results.images.length>0){
										var prm_record = ag_param_store.getAt(0);

										for(var i=0;i<results.images.length;i++){
											var index = store.find('f_id',new RegExp("^"+results.images[i].f_id+"\$"));
											if(index<0) continue;
											delete post_id_hash[results.images[i].f_id];
//											var def_color = results.images[i].def_color;
//											if(Ext.isEmpty(def_color)){
//												def_color = '#'+prm_record.data.color_rgb;
//												def_color = getRandomColor();
//											}
											var def_color = getRandomColor();

//_dump("["+results.images[i].f_id+"]=["+def_color+"]");

											var record = store.getAt(index);
											if(record.get('color') == def_color) continue;
											record.set('color', def_color);
											record.commit();
										}
									}
									for(var f_id in post_id_hash){
										var index = store.find('f_id',new RegExp("^"+f_id+"\$"));
//_dump("f_id=["+f_id+"]["+index+"]");
										if(index<0) continue;
										def_color = getRandomColor();
										var record = store.getAt(index);
										record.set('color', def_color);
										record.commit();
									}
								}catch(e){
									_dump("success():"+e);
								}
							},
							failure : function(conn,response,options){
//_dump("failure()");
							}
						});
					},
					scope: this
				}
			}
		},
		{
			hidden: true,
			id : 'ag-pallet-none-color-button',
			tooltip   : 'Set default color to selected parts',
			iconCls  : 'pallet_none_color',
			disabled : true,
			listeners : {
				'click' : {
					fn : function (button, e) {
						var grid = Ext.getCmp('ag-parts-gridpanel');
						if(!grid || !grid.rendered) return;
						grid.stopEditing();
						var records = grid.getSelectionModel().getSelections();
						if(records.length==0) return;
						var prm_record = ag_param_store.getAt(0);
						for(var i=0;i<records.length;i++){
//							if(records[i].get('color') == '') continue;
							records[i].beginEdit();
							records[i].set('color', '#'+prm_record.data.color_rgb);
							records[i].endEdit();
							records[i].commit();
						}
					},
					scope: this
				}
			}
		},
//		'-',
		//2011-09-07 ADD
		new Ext.Toolbar.Button({
//		new Ext.Toolbar.MenuButton({
			id            : 'ag-pallet-heatmap-bar-button',
//			tooltip       : 'Heat Map Bar',
//			iconCls       : 'pallet_heatmap_bar',
			tooltip       : 'choropleth',
			iconCls       : 'pallet_heatmap',
			enableToggle  : true,
			pressed       : (ag_param_store.getAt(0).data.colorbar_f=='1')?true:false,
			toggleHandler : function (button, state) {
				var check = Ext.getCmp('show-colorbar-check');
				if(check && check.rendered) check.setValue(state);
/*
			},
			menu : {
				items: [
					new Ext.ux.TextFieldItem({
						fieldLabel :'MAX'
					}),
					new Ext.ux.TextFieldItem({
						fieldLabel :'MIN'
					})
				]
*/
			}

		}),
		'-',

		//2015-09-10 ADD START
		{
			id: 'ag-pallet-color-pallet-button',
			tooltip: 'Set select color to selected parts',
//			iconCls: 'color_pallet',
			text: 'Color',
			disabled: true,
			menu: new Ext.ux.ColorMenu({
				listeners : {
					beforerender: function(menu){
						if(menu.palette && menu.palette.colors) menu.palette.colors = window.palette_color;
					},
					select: {
						fn: function(colorPalette, color){
							if(color.substr(0,1) !== '#') color = '#'+color;
							var gridpanel = Ext.getCmp('ag-parts-gridpanel');
							var selModel = gridpanel.getSelectionModel();
							var store = gridpanel.getStore();
							var records = selModel.getSelections();
							Ext.each(records,function(record){
								record.beginEdit();
								record.set('color',color);
								record.endEdit();
								record.commit();
							});
						},
						buffer: 100
					}
				}
			},{
				text:'Option...',
				iconCls:'color_pallet',
				menuOptionListeners: {
					select: function(colorDialog, color){
						if(color.substr(0,1) !== '#') color = '#'+color;
						var gridpanel = Ext.getCmp('ag-parts-gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var store = gridpanel.getStore();
						var records = selModel.getSelections();
						Ext.each(records,function(record){
							record.beginEdit();
							record.set('color',color);
							record.endEdit();
							record.commit();
						});
					}
				},
				listeners: {
					click: {
						fn: function(){
							if(this.disabled){
								return;
							}
							if(Ext.isEmpty(this.menuOption)){
								var config = {
									closeAction:'hide',
									modal : true,
									buttons : [{
										text : 'OK',
										handler : function(b,e){
											try{
												this.menuOption.fireEvent('select',b,this.menuOption.getColor(1));
												this.menuOption.hide();
											}catch(e){
												_dump(e);
											}
										},
										scope : this
									},{
										text : 'Cancel',
										handler : function(b,e){
											try{
												this.menuOption.hide();
											}catch(e){
												_dump(e);
											}
										},
										scope : this
									}]
								};
								try{
									var color = this.getValue();
									if(color.substr(0,1) == '#') color = color.substr(1);
									config.color = color;
								}catch(e){}
								this.menuOption = new Ext.ux.ColorDialog(config);
								this.menuOption.on(Ext.apply({}, this.menuOptionListeners, {
									scope:this
								}));
							}
							var body_box = Ext.getBody().getBox();
							body_box.width -= 30;
							var menu_box = this.menuOption.getBox();
							var x = this.el.getX();
							var y = this.el.getY()+this.el.getHeight();
							if(x+menu_box.width>body_box.width) x = (x+this.el.getWidth()+17) - menu_box.width;
							if(y+menu_box.height>body_box.height) y = y - this.el.getHeight() - menu_box.height;

							if(x<0) x = 0;
							if(y<0) y = 0;

							this.menuOption.setPosition(x,y);

							try{
								var color = this.getValue();
								if(color.substr(0,1) == '#') color = color.substr(1);
								this.menuOption.setColor(color);
							}catch(e){}

							this.menuOption.show(this.el);
						},
						buffer:100
					}
				}
			})
		},{
			id: 'ag-pallet-opacity-pallet-button',
			text: 'Opacity',
			disabled: true,
			menu: {
				items:[{
					text: '1.0'
				},{
					text: '0.8'
				},{
					text: '0.6'
				},{
					text: '0.4'
				},{
					text: '0.3'
				},{
					text: '0.2'
				},{
					text: '0.1'
				},{
					text: '0.05'
				},{
					text: '0.0'
				}],
				listeners: {
					click: function( menu, item, e, eOpts ){
						if(isNaN(parseFloat(item.text))) return;
						var opacity = item.text;
						var gridpanel = Ext.getCmp('ag-parts-gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var store = gridpanel.getStore();
						var records = selModel.getSelections();
						Ext.each(records,function(record){
							record.beginEdit();
							record.set('opacity',opacity);
							record.endEdit();
							record.commit();
						});
					}
				}
			}
		},{
			id: 'ag-pallet-remove-pallet-button',
			text: 'Remove',
			disabled: true,
			menu: {
				items:[{
					text: 'Show'
				},{
					text: 'Remove'
				}],
				listeners: {
					click: function( menu, item, e, eOpts ){
						var exclude = item.text.toUpperCase()==='REMOVE';
						var gridpanel = Ext.getCmp('ag-parts-gridpanel');
						var selModel = gridpanel.getSelectionModel();
						var store = gridpanel.getStore();
						var records = selModel.getSelections();
						Ext.each(records,function(record){
							record.beginEdit();
							record.set('exclude',exclude);
							record.endEdit();
							record.commit();
						});
					}
				}
			}
		},
		//2015-09-10 ADD END

HTML
}
print <<HTML;
		'->',
HTML
if($groupHidden ne 'true'){
	print qq|		'-',\n|;
}
print <<HTML;
		{
			id : 'ag-pallet-home-button',
			tooltip   : 'Home',
			iconCls  : 'home',
			disabled : true,
			hidden   : $groupHidden,
			listeners : {
				'click' : {
					fn : function (button, e) {
						var selModel = ag_parts_gridpanel.getSelectionModel();
						var record = selModel.getSelected();
						if(record){
							var tg_id = record.get("tg_id");
							if(!Ext.isEmpty(tg_id)){
								try{
									var combo;
									var contents_tabs = Ext.getCmp('contents-tab-panel');
									if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
										combo = Ext.getCmp('bp3d-tree-group-combo');
									}else{
										combo = Ext.getCmp('anatomo-tree-group-combo');
									}
									if(combo.getValue()==tg_id) return;
									var store = combo.getStore();
									var index = store.find('tg_id', new RegExp('^'+tg_id+'\$'));
									combo.setValue(tg_id);
									combo.fireEvent('select',combo,store.getAt(index),index);
								}catch(e){
									_dump("683:"+e);
								}
							}
						}
						try{selModel.clearSelections();}catch(e){}
					},
					scope: this
				}
			}
		},
HTML
if($copyHidden ne 'true'){
	print <<HTML;
		'-',
		{
			xtype : 'tbbutton',
			id : 'ag-pallet-copy-button',
			tooltip   : get_ag_lang('COPY_TITLE')+' Selected',
			iconCls  : 'pallet_copy',
			disabled : true,
			listeners : {
				'click' : {
					fn : function (button, e) {
						var grid = Ext.getCmp('ag-parts-gridpanel');
						if(grid && grid.rendered){
							copyList(grid);
						}
					},
					scope: this
				}
			}
		},
		'-',
		{
			xtype     : 'tbbutton',
			id        : 'ag-pallet-paste-button',
			tooltip   : 'Paste',
			iconCls   : 'pallet_paste',
			listeners : {
				'click' : {
					fn : function (button, e) {
						var grid = Ext.getCmp('ag-parts-gridpanel');
						if(grid && grid.rendered){
							pasteList(grid);
						}
					},
					scope: this
				}
			}
		},
HTML
}
print <<HTML;
		'-',
		{
			id : 'ag-pallet-delete-button',
			tooltip   : 'Delete Selected',
			iconCls  : 'pallet_delete',
			disabled : true,
			listeners : {
				'click' : {
					fn : function (button, e) {
						var store = ag_parts_gridpanel.getStore();
						var records = store.getRange();
						for(var i=records.length-1;i>=0;i--){
							if(records[i].data.zoom) store.remove(records[i]);
						}
						var count = store.getCount();
						if(count == 0) store.removeAll();
						try{ag_parts_gridpanel.getSelectionModel().clearSelections();}catch(e){}
					},
					scope: this
				}
			}
		}
	],
	store : bp3d_parts_store,
	listeners : {
		"keydown" : function(e){
			if(e.getKey()!=e.DELETE) return;

			var button = Ext.getCmp('ag-pallet-delete-button');
			if(button) button.fireEvent('click',button,e);
		},
		"celldblclick" : function(grid,rowIndex,cellIndex,e){
			var id = grid.getColumnModel().getColumnId(cellIndex);
			if(id != "tg_id") return;
			var store = grid.getStore();
			var record = store.getAt(rowIndex);
			var tg_id = record.get(id);
			if(Ext.isEmpty(tg_id)) return;
			try{
				var combo;
				var contents_tabs = Ext.getCmp('contents-tab-panel');
				if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
					combo = Ext.getCmp('bp3d-tree-group-combo');
				}else{
					combo = Ext.getCmp('anatomo-tree-group-combo');
				}
				if(combo.getValue()==tg_id) return;
				var store = combo.getStore();
				var index = store.find('tg_id', new RegExp('^'+tg_id+'\$'));
				combo.setValue(tg_id);
				combo.fireEvent('select',combo,store.getAt(index),index);
			}catch(e){
				_dump("788:"+e);
			}
		},
		"rowclick" : function(grid,rowIndex,e){
			var store = grid.getStore();
			var records = store.getRange();
			if(!e.ctrlKey && !e.shiftKey){
				if(rowIndex>0) grid.getSelectionModel().deselectRange(0,rowIndex-1);
				if(rowIndex<records.length-1) grid.getSelectionModel().deselectRange(rowIndex+1,records.length-1);
			}
		},
		"resize" : function(e){
			resizeGridPanelColumns(ag_parts_gridpanel);
		},
		"beforeedit": function(e){
			e.grid._edit = e;
			_dump("ag_parts_gridpanel():beforeedit()");
		},
		"afteredit": function(e){
			e.record.commit();
//			e.grid._edit = undefined;
			_dump("ag_parts_gridpanel():afteredit()");
		},
		"complete": function(comp,row,col){
			comp.view.focusRow(row);
		},
		"beforerender": function(comp){
			var id = comp.getStateId();
//_dump("ag-parts-gridpanel.beforerender():id=["+id+"]");
			if(id){
				var state = Ext.state.Manager.get(id);
//_dump("ag-parts-gridpanel.beforerender():state=["+state+"]");
				if(state) comp.applyState(state);
			}
		},
		"render": function(comp){
//_dump("ag-parts-gridpanel.render()");
			restoreHiddenGridPanelColumns(comp);


			// This will make sure we only drop to the view container
			try{var ag_parts_gridpanelDropTargetEl = ag_parts_gridpanel.getView().el.dom.childNodes[0].childNodes[1]}catch(e){}
			if(ag_parts_gridpanelDropTargetEl){
				var destGridDropTarget = new Ext.dd.DropTarget(ag_parts_gridpanelDropTargetEl, {
					ddGroup    : 'partlistDD',
					copy       : false,
					notifyOver : function(ddSource, e, data){
						var rtn = "x-dd-drop-nodrop";
						function checkRow(record, index, allItems) {
							if(isNoneDataRecord(record)) return;
							var store = ag_parts_gridpanel.getStore();
							// Search for duplicates
							var foundItem = store.find('f_id', record.data.f_id);
							// if not found
							if (foundItem == -1) {
								rtn = "x-dd-drop-ok";
							}
						}
						// Loop through the selections
						Ext.each(ddSource.dragData.selections,checkRow);
						return rtn;
					},
					notifyDrop : function(ddSource, e, data){
						var rtn = true;
						// Generic function to add records.
						function addRow(record, index, allItems) {
							if(isNoneDataRecord(record)){
								rtn = false;
								return;
							}
							var store = ag_parts_gridpanel.getStore();
							// Search for duplicates
							var foundItem = store.find('f_id', record.data.f_id);
							// if not found
							if (foundItem  == -1) {
								ag_parts_gridpanel.stopEditing();

								var prm_record = ag_param_store.getAt(0);
								record.beginEdit();
								record.set('color','#'+prm_record.data.color_rgb);
								record.set('value','');
								record.set('zoom',false);
								record.set('exclude',false);
								record.set('opacity','1.0');
								record.set('representation','surface');
								record.dirty = false;
								record.endEdit();
								store.add(record);

								// Call a sort dynamically
								store.sort('name', 'ASC');
							}else{
								rtn = false;
							}
						}
						// Loop through the selections
						Ext.each(ddSource.dragData.selections,addRow);
						delete ddSource.dragData.selections;
						return rtn;
					}
				}); 
			}
		},
		'afterlayout' : function(panel,layout){
			afterLayout(panel);
		},
		'show' : function(panel){
			try{
				var size = panel.getSize();
				if(size.width && size.height) resizeGridPanelColumns(panel);
			}catch(e){
//				_dump("ag-parts-gridpanel.show():"+e);
			}
		},
		'render' : function(panel){
			if(!panel.loadMask) panel.loadMask = new Ext.LoadMask(panel.body,{removeMask:false});
		},
HTML
if($usePalletValueContextmenu eq 'true'){
	print <<HTML;
		'cellcontextmenu' : function(grid,rowIndex,cellIndex,e){
			e.stopEvent();

			var dataIndex = grid.getColumnModel().getDataIndex(cellIndex);
			_dump("ag-parts-gridpanel.cellcontextmenu("+rowIndex+","+cellIndex+","+dataIndex+")");
			if(dataIndex != 'value') return;

			var record = grid.getStore().getAt(rowIndex);
			if(!record || Ext.isEmpty(record.get(dataIndex))) return;
			var value = record.get(dataIndex);

			if(!ag_parts_gridpanel_cols_value_contextmenu){
				ag_parts_gridpanel_cols_value_contextmenu = new Ext.menu.Menu({
					id : 'ag-parts-gridpanel-cols-value-contextmenu',
					items : [{
						xtype   : 'menuitem',
						id      : 'max',
						text    : get_ag_lang('HEATMAP_SET_MAX_VALUE'),
						iconCls : 'bmax'
					},'-',{
						xtype   : 'menuitem',
						id      : 'min',
						text    : get_ag_lang('HEATMAP_SET_MIN_VALUE'),
						iconCls : 'bmin'
					}],
					listeners : {
						'click' : function(menu,menuitem,e){
							var comp = null;
							if(menuitem.id == 'max'){
								comp = Ext.getCmp('scalar-max-textfield');
							}else if(menuitem.id == 'min'){
								comp = Ext.getCmp('scalar-min-textfield');
							}
							if(comp){
								comp.setValue(menuitem.value);
								comp.fireEvent('change',comp,menuitem.value,'');
							}
						},
						scope:this
					}
				});
			}
			var maxItem;
			var minItem;
			var maxIndex = ag_parts_gridpanel_cols_value_contextmenu.items.findIndex('id','max');
			var minIndex = ag_parts_gridpanel_cols_value_contextmenu.items.findIndex('id','min');
			if(maxIndex>=0) maxItem = ag_parts_gridpanel_cols_value_contextmenu.items.itemAt(maxIndex);
			if(minIndex>=0) minItem = ag_parts_gridpanel_cols_value_contextmenu.items.itemAt(minIndex);
			if(maxItem) maxItem.value = value;
			if(minItem) minItem.value = value;
			if(e.getXY){
				var xy = e.getXY();
				xy[0] += 2;
				xy[1] += 2;
				ag_parts_gridpanel_cols_value_contextmenu.showAt(xy);
			}
		},
HTML
}
print <<HTML;
		scope:this
	},
	keys : {
		key: 'a',
		ctrl: true,
		stopEvent: true,
		handler: function() {
			ag_parts_gridpanel.getSelectionModel().selectAll();
		}
	}
});
ag_parts_gridpanel.getColumnModel().on({
	'hiddenchange' : function(column,columnIndex,hidden){
		resizeGridPanelColumns(ag_parts_gridpanel);
		saveHiddenGridPanelColumns(ag_parts_gridpanel);
	},
	scope: this,
	delay: 100
});
ag_parts_gridpanel.on({
	'afterlayout' : function(panel,layout){
		afterLayout(ag_parts_gridpanel);
	},
	scope:this
});

function setClipLine(){
	var textCmp = Ext.getCmp('anatomo-clip-value-text');
	var value = textCmp.getValue();
	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
	var clipImg = document.getElementById("clipImg");
	var clipImgDiv = document.getElementById("clipImgDiv");
	var clipImgLine = document.getElementById("clipImgLine");

//_dump("setClipLine()");

	if(clip && clipImgDiv && clipImgLine && !Ext.isEmpty(YRangeFromServer)){
		var zoom = $MAX_YRANGE/YRangeFromServer;
		var width = (clipImgDiv.offsetWidth?clipImgDiv.offsetWidth:138);
		var height = (clipImgDiv.offsetHeight?clipImgDiv.offsetHeight:303);
		if(clip == 'FB'){
			value -= glb_clip_center;
		}else if(clip == 'RL'){
			value -= glb_clip_center;
		}else if(clip == "TB"){
			value -= glb_clip_center;
		}
		if(clip == "FB" || clip == "RL"){
			clipImgLine.style.width = '0px';
			clipImgLine.style.height = height + 'px';
			var x = Math.ceil((width/2) + (height * (value / YRangeFromServer))) - 2;
//			_dump("setClipLine():x=["+x+"]");
			if(isNaN(x)) x = 0;
			clipImgLine.style.left = x + 'px';
			clipImgLine.style.top = '0px';
			clipImgLine.style.display = '';
		}else if(clip == "TB"){
			clipImgLine.style.width = width + 'px';
			clipImgLine.style.height = '0px';
			var y = Math.ceil((height/2) - (height * (value / YRangeFromServer))) - 2;
//			_dump("setClipLine():y=["+y+"]");
			if(isNaN(y)) y = 0;
			clipImgLine.style.left = '0px';
			clipImgLine.style.top = y + 'px';
			clipImgLine.style.display = '';
		}else{
			clipImgLine.style.display = 'none';
		}
	}
}



var anatomography_image = null;

function ag_pin_grid_renderer(value,metadata,record,rowIndex,colIndex,store){
	if(window.ag_extensions && ag_extensions.global_pin && ag_extensions.global_pin.grid_renderer){
		return ag_extensions.global_pin.grid_renderer(arguments);
	}

	var dataIndex = ag_pin_grid_panel_cols[colIndex].dataIndex;
	var item;
	for(var i=0;i<record.fields.length;i++){
		if(record.fields.keys[i] != dataIndex) continue;
		item = record.fields.items[i];
		break;
	}

	if(item){
		if(item.type == 'date'){
			if(dataIndex == 'entry' && value) value = new Date(value).format(bp3d.defaults.DATE_FORMAT);
			if(dataIndex == 'lastmod' && value) value = new Date(value).format(bp3d.defaults.TIME_FORMAT);
		}
	}

	return value;
}

function anatomo_comment_color_cell_style(value,metadata,record,rowIndex,colIndex,store){
	try{
		if(value){
			return '<span style="background-color:#' + value + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>';
		}
	}catch(e){_dump("1680:"+e);}
	return value;
};
HTML
if($lsdb_Auth && $addPointElementHidden ne 'true'){
	print <<HTML;
function clickAddPointElementButton(button, e){
	var records = ag_pin_grid_panel.getSelectionModel().getSelections();
	if(records.length != 1) return;
	var window_title = 'Add Point element';
	var record = records[0];
	var post = {
		f_pid   : record.get('oid'),
		p_coord : record.get('coord'),
		p_x3d   : record.get('x3d'),
		p_y3d   : record.get('y3d'),
		p_z3d   : record.get('z3d'),
		p_avx3d : record.get('avx3d'),
		p_avy3d : record.get('avy3d'),
		p_avz3d : record.get('avz3d'),
		p_uvx3d : record.get('uvx3d'),
		p_uvy3d : record.get('uvy3d'),
		p_uvz3d : record.get('uvz3d'),
	};
	try{post.b_version = Ext.getCmp('anatomo-version-combo').getValue();}catch(e){delete post.b_version;}

	var tg_name = '';
	var combo = Ext.getCmp('anatomo-tree-group-combo');
	var value = combo.getValue();
	post.tg_id = value;
	var store = combo.getStore();
	var index = store.find('tg_id',new RegExp('^'+value+'\$'));
	if(index>=0) tg_name = store.getAt(index).get('tg_name');

	var point_add_form = new Ext.form.FormPanel({
		baseCls     : 'x-plain',
		labelWidth  : 145,
		labelAlign  : 'right',
		url         : 'put-bp3d-point.cgi',
		fileUpload  : false,
		bodyStyle   : 'padding:5px',
		width       : 600,
		items       : [{
			id         : 'anatomo_point_element_add_overwrite_checkbox',
			xtype      : 'hidden',
			name       : 'p_overwrite'
		},{
			xtype      : 'hidden',
			name       : 'tg_id',
			value      : post.tg_id
//		},{
//			xtype      : 'hidden',
//			name       : 'p_coord',
//			value      : post.p_coord
//		},{
//			xtype      : 'hidden',
//			name       : 'p_x3d',
//			value      : post.p_x3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_y3d',
//			value      : post.p_y3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_z3d',
//			value      : post.p_z3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_avx3d',
//			value      : post.p_avx3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_avy3d',
//			value      : post.p_avy3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_avz3d',
//			value      : post.p_avz3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_uvx3d',
//			value      : post.p_uvx3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_uvy3d',
//			value      : post.p_uvy3d
//		},{
//			xtype      : 'hidden',
//			name       : 'p_uvz3d',
//			value      : post.p_uvz3d
		},{
			xtype         : 'fieldset',
			title         : 'Model',
			style         : 'padding:0px 10px;margin-bottom:4px;',
			autoHeight    : true,
			anchor        : '100%',
			layout        : 'column',
			items         : [{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .5,
				layout      : 'form',
				hideLabel   : true,
				items       : [{
					xtype     : 'textfield',
					hideLabel : true,
					readOnly  : true,
					value     : tg_name,
					anchor    : '90%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .5,
				layout      : 'form',
				labelWidth  : 50,
				labelAlign  : 'right',
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Version',
					name          : 'b_version',
					value         : post.b_version,
					anchor        : '100%'
				}]
			}]
		},{
			xtype         : 'textfield',
			readOnly      : true,
			fieldLabel    : get_ag_lang('COORDINATE_SYSTEM'),
			name          : 'p_coord',
			value         : post.p_coord,
			anchor        : '70%'
		},{
			xtype         : 'fieldset',
			title         : 'worldPos',
			style         : 'padding:0px;margin:0px;',
			autoHeight    : true,
			anchor        : '100%',
			layout        : 'column',
			items         : [{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'X',
					name          : 'p_x3d',
					value         : post.p_x3d,
					anchor        : '100%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Y',
					name          : 'p_y3d',
					value         : post.p_y3d,
					anchor        : '100%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Z',
					name          : 'p_z3d',
					value         : post.p_z3d,
					anchor        : '100%'
				}]
			}]
		},{
			xtype         : 'fieldset',
			title         : 'arrVec',
			style         : 'padding:0px;margin:0px;',
			autoHeight    : true,
			anchor        : '100%',
			layout        : 'column',
			items         : [{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'X',
					name          : 'p_avx3d',
					value         : post.p_avx3d,
					anchor        : '100%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Y',
					name          : 'p_avy3d',
					value         : post.p_avy3d,
					anchor        : '100%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Z',
					name          : 'p_avz3d',
					value         : post.p_avz3d,
					anchor        : '100%'
				}]
			}]
		},{
			xtype         : 'fieldset',
			title         : 'upVec',
			style         : 'padding:0px;margin-bottom:4px;',
			autoHeight    : true,
			anchor        : '100%',
			layout        : 'column',
			items         : [{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'X',
					name          : 'p_uvx3d',
					value         : post.p_uvx3d,
					anchor        : '100%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Y',
					name          : 'p_uvy3d',
					value         : post.p_uvy3d,
					anchor        : '100%'
				}]
			},{
				xtype       : 'panel',
				baseCls     : 'x-plain',
				columnWidth : .33,
				layout      : 'form',
				labelWidth  : 20,
				items       : [{
					xtype         : 'textfield',
					readOnly      : true,
					fieldLabel    : 'Z',
					name          : 'p_uvz3d',
					value         : post.p_uvz3d,
					anchor        : '100%'
				}]
			}]
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			readOnly      : true,
			fieldLabel    : 'FMAID(Parent)',
			name          : 'f_pid',
			value         : post.f_pid,
			allowBlank    : false,
			anchor        : '70%'
		},{
			id            : 'anatomo_point_element_add_fmaid_textfield',
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : 'FMAID',
			name          : 'f_id',
			allowBlank    : false,
			anchor        : '70%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : 'English',
			name          : 'p_name_e',
			allowBlank    : false,
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('GRID_TITLE_NAME_J'),
			name          : 'p_name_j',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('GRID_TITLE_NAME_K'),
			name          : 'p_name_j',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : 'Latina',
			name          : 'p_name_l',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('ADMIN_FORM_ORGAN_SYSTEM_E_TITLE'),
			name          : 'p_organsys_e',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('ADMIN_FORM_ORGAN_SYSTEM_J_TITLE'),
			name          : 'p_organsys_j',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('ADMIN_FORM_SYNONYM_E_TITLE'),
			name          : 'p_syn_e',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('ADMIN_FORM_SYNONYM_J_TITLE'),
			name          : 'p_syn_j',
			anchor        : '100%'
		},{
			xtype         : 'textfield',
			selectOnFocus : true,
			fieldLabel    : get_ag_lang('ADMIN_FORM_CLASSLABEL_TITLE'),
			name          : 'p_label',
			anchor        : '100%'
		}]
	});

	var point_add_window = new Ext.Window({
		title       : window_title,
		width       : 442,
		height      : 570,
		minWidth    : 400,
		minHeight   : 570,
		maxHeight   : 570,
		layout      : 'fit',
		plain       : true,
		bodyStyle   :'padding:5px;',
		buttonAlign :'right',
		items       : point_add_form,
		modal       : true,
		buttons : [{
			id      : 'anatomo_point_element_add_window_ok_button',
			text    : get_ag_lang('COMMENT_WIN_TITLE_SEND'),
			listeners : {
				'click' : function(){
					if(point_add_form.getForm().isValid()){
						point_add_form.getForm().submit({
							url     : 'put-bp3d-point.cgi',
							waitMsg : get_ag_lang('ADMIN_FORM_REG_WAITMSG')+'...',
							success : function(fp, o){
								try{
									if(o.result.success == true){
										Ext.MessageBox.show({
											title   : window_title,
											msg     : get_ag_lang('ADMIN_FORM_REG_OKMSG'),
											buttons : Ext.MessageBox.OK,
											icon    : Ext.MessageBox.INFO,
											fn      : function(){
												point_add_window.close();
												if(o.result.record){
													var prm_record = ag_param_store.getAt(0);
													var addrecs = [];
													var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
													var addrec = new newRecord({
														'exclude'       : false,
														'color'         : '#'+prm_record.data.point_color_rgb,
														'value'         : '',
														'zoom'          : false,
														'exclude'       : false,
														'opacity'       : '1.0',
														'representation': 'surface',
														'point'         : false
													});
													addrec.beginEdit();
													for(var fname in o.result.record){
														if(Ext.isEmpty(o.result.record[fname])) continue;
														addrec.set(fname,o.result.record[fname]);
													}
//													for(var fname in addrec.data){
//														_dump("["+fname+"]=["+addrec.data[fname]+"]");
//													}

													addrec.commit(true);
													addrec.endEdit();
													addrecs.push(addrec);

													var partslist = Ext.getCmp('control-tab-partslist-panel');
													var store = partslist.getStore();

													var regexp = new RegExp("^"+addrec.get('f_id')+"\$");
													var index = store.find('f_id',regexp);
													if(index<0) index = store.find('conv_id',regexp);
													if(index>=0) store.remove(store.getAt(index));

													store.add(addrecs);

													addrecs = store.getRange();
													clearConvertIdList(addrecs);
													getConvertIdList(addrecs,store);

													var button = Ext.getCmp('anatomo_comment_pick_delete');
													button.fireEvent('click',button);

													var combo = Ext.getCmp('anatomo-point-label-combo');
													combo.getStore().reload();

												}
											}
										});
										return;
									}
								}catch(e){ _dump("success():"+ e + ""); }
								Ext.MessageBox.show({
									title   : window_title,
									msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+o.result.msg+' ]',
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							},
							failure : function(fp, o){
								if(o.result){
									if(Ext.isEmpty(o.result.code) || o.result.code!=100){
										Ext.MessageBox.show({
											title   : window_title,
											msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+o.result.msg+' ]',
											buttons : Ext.MessageBox.OK,
											icon    : Ext.MessageBox.ERROR
										});
									}else{
										Ext.MessageBox.show({
											title   : window_title,
											msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+o.result.msg+' ]',
											buttons : Ext.MessageBox.OKCANCEL,
											icon    : Ext.MessageBox.QUESTION,
											fn      : function(buttonId,text,opt){
												if(buttonId!='ok') return;
												Ext.getCmp('anatomo_point_element_add_overwrite_checkbox').setValue(true);
												var button = Ext.getCmp('anatomo_point_element_add_window_ok_button');
												button.fireEvent('click',button);
											}
										});
									}
								}else if(o.response){
									Ext.MessageBox.show({
										title   : window_title,
										msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+o.response.statusText+' ][ '+o.response.status+' ]',
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
								}else{
									Ext.MessageBox.show({
										title   : window_title,
										msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG'),
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
								}
							}
						});
					}
				},
				scope: this
			}
		},{
			text: get_ag_lang('COMMENT_WIN_TITLE_CANCEL'),
			handler : function(){
				point_add_window.close();
			}
		}],
		listeners: {
			'show': {fn:function(self){},scope:this},
			'hide': {fn:function(self){},scope:this},
			'render': {
				fn: function(win){
					if(Ext.isEmpty(win.loadMask) || typeof win.loadMask == 'boolean') win.loadMask = new Ext.LoadMask(win.body,{removeMask:false});
					var textfield = Ext.getCmp('anatomo_point_element_add_fmaid_textfield');
					textfield.on({
						'specialkey' : function(textfield,e){
//											_dump(e.getKey());
							if(e.getKey() == e.ENTER){
								point_add_window.loadMask.show();
								var post = {};
								post.node = textfield.getValue();
								try{post.version = Ext.getCmp('anatomo-version-combo').getValue();}catch(e){delete post.version;}

								for(var key in init_bp3d_params){
									if(key.match(/_id\$/)) post[key] = init_bp3d_params[key];
								}

								try{
									var store = Ext.getCmp('anatomo-version-combo').getStore();
									var idx = store.findBy(function(record,id){
										if(record.data.tgi_version==post.version) return true;
									});
									if(idx>=0){
										var record = store.getAt(idx);
										if(record){
											post.md_id = record.data.md_id;
											post.mv_id = record.data.mv_id;
											post.mr_id = record.data.mr_id;
											post.ci_id = record.data.ci_id;
											post.cb_id = record.data.cb_id;
										}
									}
								}catch(e){}

								Ext.Ajax.request({
									url     : 'get-fma.cgi',
									method  : 'POST',
									params  : Ext.urlEncode(post),
									success : function(conn,response,options){
										try{
											try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
											if(results && results.records && results.records.length>0){
												var items = point_add_form.getForm().items;
												var data = results.records[0];
												var len = items.getCount();
												for(var i=0;i<len;i++){
													var item = items.itemAt(i);
													if(item.initialConfig.readOnly) continue;
													if(item.getXType()=='hidden') continue;
													if(!Ext.isEmpty(item.getValue())) continue;
													var name = item.getName();
													name = name.replace(/^p_/g,'');
													if(Ext.isEmpty(data[name])){
														if(name=='label'){
															var val = Ext.getCmp('anatomo_point_element_add_fmaid_textfield').getValue();
															if(!Ext.isEmpty(val)){
																val = val.replace(/^([A-Za-z]+).*\$/g,'\$1');
																item.setValue(val.trim());
															}else{
																item.setValue('');
															}
														}else{
															item.setValue('');
														}
													}else{
														item.setValue(data[name]);
													}
												}
											}else{
												var items = point_add_form.getForm().items;
												var len = items.getCount();
												for(var i=0;i<len;i++){
													var item = items.itemAt(i);
													if(item.initialConfig.readOnly) continue;
													if(item.getXType()=='hidden') continue;
													var name = item.getName();
													if(name=='f_id' || name=='p_label') continue;
													item.setValue('');
												}
											}
										}catch(e){
										}
										point_add_window.loadMask.hide();
									},
									failure : function(conn,response,options){
//														_dump("failure()");
										point_add_window.loadMask.hide();
									}
								});
							}
						},
						scope: this
					});
				}
			}
		}
	});
	point_add_window.show();
}
HTML
}
print <<HTML;
var ag_pin_grid_panel_cols_fixed = true;
if(window.ag_extensions && ag_extensions.single_pin && ag_extensions.single_pin.gridColumn){
	ag_pin_grid_panel_cols_fixed = false;
}
var ag_pin_grid_panel_cols = [
	{dataIndex:'coord',   header:'Coord',                      id:'coord', width:40, resizable:false, hidden:true, fixed:$coordinateSystemHidden, renderer:ag_pin_grid_renderer},
	{dataIndex:'no',      header:'No',                         id:'no',  width:30, align:'right', fixed:ag_pin_grid_panel_cols_fixed, renderer:ag_pin_grid_renderer, sortable:true},
	{dataIndex:'oid',     header:get_ag_lang('CDI_NAME'),          id:'oid', width:70, resizable:true, renderer:ag_pin_grid_renderer, sortable:true},
	{dataIndex:'organ',   header:'Organ',                      id:'organ', renderer:ag_pin_grid_renderer, sortable:true},
//	{dataIndex:'name_j',  header:get_ag_lang('GRID_TITLE_NAME_J'), id:'name_j', hidden:true, renderer:ag_pin_grid_renderer},
//	{dataIndex:'name_k',  header:get_ag_lang('GRID_TITLE_NAME_K'), id:'name_k', hidden:true, renderer:ag_pin_grid_renderer},
//	{dataIndex:'name_l',  header:'Latina',                     id:'name_l', hidden:true, renderer:ag_pin_grid_renderer},
	{dataIndex:'color',   header:'Color',                      id:'color', width:40, resizable:false, renderer: anatomo_comment_color_cell_style, sortable:true},
	{dataIndex:'comment', header:'Description',                id:'comment', renderer:ag_pin_grid_renderer, sortable:true}
	
];

if(window.ag_extensions && ag_extensions.single_pin && ag_extensions.single_pin.gridColumn){
	ag_pin_grid_panel_cols.push(ag_extensions.single_pin.gridColumn());
}

var ag_pin_grid_panel = new Ext.grid.GridPanel({
	id             : 'anatomography-pin-grid-panel',
	title          : 'Pin',
	columns        : ag_pin_grid_panel_cols,
	stripeRows     : true,
	columnLines    : true,
	region         : 'center',
	border         : false,
//	style          : 'border-right-width:1px',
	selModel : new Ext.grid.RowSelectionModel({
		listeners : {
			'selectionchange' : function(selModel){
				var add_btn = Ext.getCmp('anatomo_point_element_add_button');
				if(selModel.getCount()==1){
					Ext.getCmp('anatomo_comment_pick_edit').enable();
					if(!Ext.isEmpty(add_btn)) add_btn.enable();
				}else{
					Ext.getCmp('anatomo_comment_pick_edit').disable();
					if(!Ext.isEmpty(add_btn)) add_btn.disable();
				}
				if(selModel.getCount()>0){
					Ext.getCmp('anatomo_comment_pick_delete').enable();
//					Ext.getCmp('anatomo_comment_pick_sp_url_copy').enable();
				}else{
					Ext.getCmp('anatomo_comment_pick_delete').disable();
//					Ext.getCmp('anatomo_comment_pick_sp_url_copy').disable();
				}
				var store = ag_pin_grid_panel.getStore();
				if(store.getCount()>1 && selModel.getCount()==1){
					Ext.getCmp('anatomo_comment_pick_up').enable();
					Ext.getCmp('anatomo_comment_pick_down').enable();
				}else{
					Ext.getCmp('anatomo_comment_pick_up').disable();
					Ext.getCmp('anatomo_comment_pick_down').disable();
				}
			},
			scope : this
		}
	}),
	store : ag_comment_store,
	loadMask : true,
	maskDisabled : true,
	viewConfig: {
		deferEmptyText: false,
		emptyText: '<div class="bp3d-pallet-empty-message">'+get_ag_lang('CLICK_IMAGE_GRID_EMPTY_MESSAGE')+'</div>'
	},
	tbar:[
	{
		id : 'anatomo_comment_pick_button',
		enableToggle : true,
		text : 'Pin',
		hidden : true,
		listeners : {
			'toggle' : {
				fn : function(button, pressed) {
					anatomoPickMode = pressed;
					if(pressed) Ext.getCmp('anatomo_comment_point_button').toggle(false);
				},
				scope : this
			}
		}
	},{
		id: 'anatomo_comment_pick_depth_text',
		xtype:'tbtext',
		text:'Depth : '
	},{
		id : 'anatomo_comment_pick_depth',
		xtype : 'combo',
		triggerAction: 'all',
		editable: false,
		mode : 'local',
		displayField : 'value',
		valueFeild : 'value',
		value : 1,
		width: 40,
		store: new Ext.data.SimpleStore({
			fields:['value'],
			data:[
				[1],
				[2],
				[3],
				[4],
				[5],
				[6],
				[7],
				[8],
				[9],
				[10],
				[11],
				[12],
				[13],
				[14],
				[15],
				[16]
			]
		})
	},'-',{
		id : 'anatomo_comment_pick_edit',
//		text:'Edit',
		tooltip : 'Edit',
		iconCls: 'pin_edit',
		disabled:true,
		listeners: {
			'click' : function(button, e) {
				ag_pin_grid_panel.fireEvent('rowdblclick',ag_pin_grid_panel);
			},
			scope:this
		}
	},'-',{
		id : 'anatomo_comment_pick_up',
//		text:'Up',
		tooltip : 'Up',
		iconCls: 'pin_up',
		disabled:true,
		listeners: {
			'click' : {
				fn:function(button, e) {
					var records = ag_pin_grid_panel.getSelectionModel().getSelections();
					var store = ag_pin_grid_panel.getStore();
					if (records.length != 1) {
						return;
					}
					if (records[0].get('no') <= 1) {
						return;
					}
					store.remove(records[0]);
					store.insert(records[0].get('no') - 2, records[0]);
					ag_pin_grid_panel.getSelectionModel().selectRecords(records);
					for (var i = 0; i < store.getCount(); i++) {
						var rec = store.getAt(i);
						rec.set('no', i + 1);
						rec.commit();
					}
					updateAnatomo();
				},
				scope:this
			}
		}
	}, {
		id : 'anatomo_comment_pick_down',
//		text:'Down',
		tooltip : 'Down',
		iconCls: 'pin_down',
		disabled:true,
		listeners: {
			'click' : {
				fn:function(button, e) {
					var records = ag_pin_grid_panel.getSelectionModel().getSelections();
					var store = ag_pin_grid_panel.getStore();
					if (records.length != 1) {
						return;
					}
					if (records[0].get('no') >= store.getCount()) {
						return;
					}
					store.remove(records[0]);
					store.insert(records[0].get('no'), records[0]);
					ag_pin_grid_panel.getSelectionModel().selectRecords(records);
					for (var i = 0; i < store.getCount(); i++) {
						var rec = store.getAt(i);
						rec.set('no', i + 1);
						rec.commit();
					}
					updateAnatomo();
				},
				scope:this
			}
		}
	},'-',{
		id : 'anatomo_comment_pick_delete',
//		text:'Delete',
		tooltip : 'Delete',
		iconCls : 'pallet_delete',
		disabled:true,
		listeners: {
			'click' : {
				fn:function(button, e) {
					var records = ag_pin_grid_panel.getSelectionModel().getSelections();
					if (records.length == 0) {
						return;
					}
					var store = ag_pin_grid_panel.getStore();
					for (var i = records.length - 1; i >= 0; i--) {
						store.remove(records[i]);
					}
					var count = store.getCount();
					if (count == 0) {
						store.removeAll();
					}
					try{ag_pin_grid_panel.getSelectionModel().clearSelections();}catch(e){}

					store.suspendEvents();
					var no=0;
					Ext.each(store.getRange().sort(function(a,b){return (a.data.no-0)-(b.data.no-0);}),function(r,i,a){
						r.beginEdit();
						r.set('no',++no);
						r.commit();
						r.endEdit();
					});
					store.resumeEvents();
					ag_pin_grid_panel.getView().refresh();

					updateAnatomo();
				},
				scope:this
			}
		}
	},'-',{
		id : 'anatomo_comment_pick_delete_all',
		text:'ALL',
		tooltip : 'Delete ALL',
		iconCls : 'pallet_delete',
		listeners: {
			'click' : {
				fn: function(button, e){
					if(ag_pin_grid_panel.getStore().getCount()==0) return;
					Ext.MessageBox.show({
						title   : button.tooltip,
						msg     : 'Do you really want to delete all pins?',
						buttons : Ext.MessageBox.YESNO,
						icon    : Ext.MessageBox.QUESTION,
						fn:function(btn){
							if(btn != 'yes') return;
							ag_pin_grid_panel.getStore().removeAll();
							try{ag_pin_grid_panel.getSelectionModel().clearSelections();}catch(e){}
							updateAnatomo();
						}
					});
				},
				scope:this
			}
		}
	},
//	'-',
	{
		hidden: true,
		id : 'anatomo_comment_pick_addurl',
		text:'Import pins',
		listeners: {
			'click' : {
				fn:function(button, e) {

					Ext.Msg.show({
						title:'Import pins from other map URL',
						msg: 'URL',
						buttons: Ext.Msg.OKCANCEL,
						multiline : true,
						width : 400,
						fn:function(btn,text){
							if(btn != 'ok') return;
							if(!ag_comment_store) return;

							var url_arr = text.replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").split("\\n");
							for(var i=0;i<url_arr.length;i++){
								var search = "";
								if(url_arr[i].indexOf("?")>=0){
									search = url_arr[i].replace(/^.+\\?(.*)\$/g,"\$1");
								}else if(url_arr[i].search(/[&]*pno[0-9]{3}=/)>=0){
									search = url_arr[i];
								}else{
									continue;
								}

								var params = Ext.urlDecode(search);
								if(params.shorten){
									var window_title = 'Import pins from other map URL';

									Ext.Ajax.request({
										url     : 'get-convert-url.cgi',
										method  : 'POST',
										params  : Ext.urlEncode({url:url_arr[i]}),
										success : function(conn,response,options){
											try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
											if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
												var msg = get_ag_lang('CONVERT_URL_ERRMSG');
												if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
												for(var key in results){
													_dump("1:["+key+"]=["+results[key]+"]");
												}
												Ext.MessageBox.show({
													title   : window_title,
													msg     : msg,
													buttons : Ext.MessageBox.OK,
													icon    : Ext.MessageBox.ERROR
												});
												return;
											}
											if(Ext.isEmpty(results.data)){
												var msg = get_ag_lang('CONVERT_URL_ERRMSG');
												if(results && results.status_code) msg += ' [ no data ]';
												Ext.MessageBox.show({
													title   : window_title,
													msg     : msg,
													buttons : Ext.MessageBox.OK,
													icon    : Ext.MessageBox.ERROR
												});
												return;
											}
											if(!Ext.isEmpty(results.data.url)){//shortURLに変換
												return;
											}
											if(!Ext.isEmpty(results.data.expand)){//longURLに変換
												var search;
												if(Ext.isArray(results.data.expand)){
													search = results.data.expand[0].long_url;
												}else{
													search = results.data.expand.long_url;
												}
												if(search){
													if(search.indexOf("?")>=0){
														search = search.replace(/^.+\\?(.*)\$/g,"\$1");
													}else if(search.search(/[&]*pno[0-9]{3}=/)>=0){
													}else{
														search = undefined;
													}
												}
												if(search){
													var params = Ext.urlDecode(search);
													if(!params.tp_ap) params.tp_ap = search;
													add_comment_store_pins_from_TPAP(params.tp_ap);
												}
												return;
											}
										},
										failure : function(conn,response,options){
											anatomo_link_window.loadMask.hide();
											Ext.MessageBox.show({
												title   : window_title,
												msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
												buttons : Ext.MessageBox.OK,
												icon    : Ext.MessageBox.ERROR
											});
										}
									});

								}else{
									if(!params.tp_ap) params.tp_ap = search;
									add_comment_store_pins_from_TPAP(params.tp_ap);
								}
							}
						}
					});
				},
				scope:this
			}
		}
	},'->'
//	,{
//		hidden: (Ext.isEmpty(window.ag_extensions) || Ext.isEmpty(ag_extensions.single_pin) || Ext.isEmpty(ag_extensions.single_pin.openCopyWindow)),
//		xtype: 'tbseparator'
//	},{
//		hidden: (Ext.isEmpty(window.ag_extensions) || Ext.isEmpty(ag_extensions.single_pin) || Ext.isEmpty(ag_extensions.single_pin.openCopyWindow)),
//		id: 'anatomo_comment_pick_sp_url_copy',
//		tooltip: 'Copy SINGLE-PIN URL',
//		iconCls: 'pin_copy',
//		listeners: {
//			'click' : {
//				fn:function(button, e) {
//					ag_extensions.single_pin.openCopyWindow({
//						animEl: button.el,
//						iconCls: button.iconCls,
//						title: button.tooltip
//					});
//				},
//				scope:this
//			}
//		}
//	}
	],

	bbar : [
		{
			id : 'anatomo_pin_number_draw_check',
			xtype : 'checkbox',
			boxLabel : 'Number',
			value : init_anatomo_pin_number_draw,
			listeners: {
				'check' : function (checkbox, fChecked) {
					updateAnatomo();
				},
				'render': function(comp){
					comp.setValue(init_anatomo_pin_number_draw);
				},
				scope:this
			}
		},
		'-',
		{
			id : 'anatomo_pin_description_draw_check',
			xtype : 'checkbox',
			boxLabel : 'Description',
			value : init_anatomo_pin_description_draw,
			listeners: {
				'check' : function (checkbox, fChecked) {
					var combo = Ext.getCmp('anatomo_pin_description_draw_pin_indication_line_combo');
					if(combo){
						if(combo.rendered){
							if(fChecked){
								combo.enable();
							}else{
								combo.disable();
							}
							updateAnatomo();
						}else{
							combo.on({
								render: {
									fn: function(combo){
										if(fChecked){
											combo.enable();
										}else{
											combo.disable();
										}
										updateAnatomo();
									},single: true
								}
							});
						}
					}
				},
				'render': function(comp){
					comp.setValue(init_anatomo_pin_description_draw);
				},
				scope:this
			}
		},
		'-',
		{
			xtype : 'tbtext',
			text : 'Line'
		},
		{
			id:'anatomo_pin_description_draw_pin_indication_line_combo',
			xtype : 'combo',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			width: 55,
			value:init_anatomo_pin_description_line,
			triggerAction: 'all',
			store: new Ext.data.SimpleStore({
				fields: ['disp', 'value'],
				data : [
					['None', 0],
					['Tip', 1],
					['End', 2]
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
					var prm_record = ag_param_store.getAt(0);
					prm_record.beginEdit();
					prm_record.set('point_pin_line', record.data.value);
					prm_record.endEdit();
					prm_record.commit();
					if(record.data.value!=0){
						var cmp = Ext.getCmp('anatomo_pin_shape_combo');
						if(cmp && cmp.rendered){
							var val = cmp.getValue();
							if(val=='SC') cmp.setValue('PL');
						}
					}
					updateAnatomo();
				},
				scope:this
			}
		},
		'-',
		{
			id : 'anatomo_pin_shape_label',
			xtype : 'tbtext',
//			text : 'Pin Shape'
			text : 'Shape'
		},
		{
			id : 'anatomo_pin_shape_combo',
			xtype : 'combo',
			triggerAction: 'all',
			editable: false,
			mode : 'local',
			displayField : 'display',
			valueField : 'value',
			value : init_anatomo_pin_shape,
			width : 60,
			store: new Ext.data.SimpleStore({
				fields:['display', 'value'],
				data:[
					['Circle', 'SC'],
					['Corn', 'CC'],
					['Pin L', 'PL'],
					['Pin M', 'PM'],
					['Pin S', 'PS'],
					['Pin SS','PSS']
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
					updateAnatomo();
				},
				'render': function(comp){
					comp.setValue(init_anatomo_pin_shape);
				},
				scope:this
			}
		}
HTML
if($lsdb_Auth && $addPointElementHidden ne 'true'){
	print <<HTML;
		,'->',
		'-',
		{
			id : 'anatomo_point_element_add_button',
			text:'Add Point',
			disabled:true,
			listeners: {
				'click' : clickAddPointElementButton,
				scope:this
			}
		}
HTML
}
print <<HTML;
	],
	listeners : {
		"keydown" : function (e) {
			if (e.getKey() == e.DELETE) {
				var button = Ext.getCmp('anatomo_comment_pick_delete');
				button.fireEvent('click',button);
			}
		},
		"rowdblclick" : function (e) {
			var records = ag_pin_grid_panel.getSelectionModel().getSelections();
			if (records.length != 1) {
				return;
			}
			if(window.ag_extensions && ag_extensions.global_pin && ag_extensions.global_pin.isGlobalPin){
				if(ag_extensions.global_pin.isGlobalPin(records[0])) return;
			}

			var retColor = records[0].data.color;
			var win = new Ext.Window({
				title:'Edit Description Dialog',
				modal:true,
				width:450,
				height:500,
				closeAction:'close',
				plain:true,
				resizable: false,
				items: [{
					layout: 'anchor',
					items: [{
						height: 152,
						border: false,
						anchor: '100%',
						layout:'column',
						items: [{
							xtype: 'fieldset',
							title: 'Description',
							columnWidth: 1,
							height: 162,
							bodyStyle: 'padding:0px;',
							style: 'margin:0 0 4px 4px;',
							layout: 'anchor',
							items: [{
								hidden: true,
								xtype: 'combo',
								id:'anatomo-edit-comment-combo',
								hideLabel: true,
								style: 'margin:0 0 0 4px;',
								ctCls : 'x-small-editor',
								editable: false,
								mode: 'local',
								lazyInit: false,
								displayField: 'disp',
								valueField: 'value',
								width: 100,
								value:'',
								triggerAction: 'all',
								store: new Ext.data.SimpleStore({
									fields: ['disp', 'value'],
									data : [
										['Description', ''],
										['Point object', 'Point object[]'],
										['Object tag', 'Object tag[]']
									]
								}),
								listeners: {
									'select' : function(combo, record, index) {
										var text = Ext.getCmp('anatomo-edit-comment-text');
										if(text){
											var dom = text.el.dom;
											if(dom.selectionStart != undefined){
												var st = dom.selectionStart>0?dom.value.slice(0,dom.selectionStart):"";
												var et = dom.value.slice(dom.selectionEnd);
												text.setValue(st+record.data.value+et);
											}else{
												text.focus();
												var selection = dom.ownerDocument.selection.createRange();
												selection.text = record.data.value + selection.text;
											}
										}
									},
									scope:this
								}
							},{
								xtype: 'textarea',
								hideLabel: true,
								style: 'margin:4px 0 0 4px;',
//								anchor: '-8 -32',
								anchor: '-8 -8',
								id:'anatomo-edit-comment-text',
								value: records[0].data.comment
							}]
						},{
							xtype: 'fieldset',
							title: 'Color',
							width: 130,
							height: 60,
							style: 'margin:0 4px 4px 4px;',
							items: [
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
								new Ext.ux.ColorPickerField({
									ctCls : 'x-small-editor',
									id:'anatomo-edit-color-palette',
									width: 80,
									style: 'margin:0 0 0 4px;',
									hideLabel: true,
									value: records[0].data.color,
									menuListeners : {
										select: function(e, c){
											this.setValue(c);
										},
										show : function(){
											this.onFocus();
										},
										hide : function(){
											this.focus.defer(10, this);
										},
										beforeshow : function(menu) {
											try {
												if (this.value != "") {
													menu.palette.select(this.value);
												}else{
													this.setValue("");
													var el = menu.palette.el;
													if(menu.palette.value){
														try{el.child("a.color-"+menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
														menu.palette.value = null;
													}
												}
											}catch(ex){}
										}
									}
								})
HTML
}else{
	print <<HTML;
								new Ext.ux.ColorField({
									ctCls : 'x-small-editor',
									id:'anatomo-edit-color-palette',
									width: 80,
									style: 'margin:0 0 0 4px;',
									hideLabel: true,
									value: records[0].data.color
								})
HTML
}
print <<HTML;
							]
						}]
					},{
						xtype: 'fieldset',
						title: 'FMAID',
						style: 'margin:0 0 4px 4px;',
						anchor: '-8 -38',
						items: [{
							xtype: 'grid',
							id:'anatomo-edit-fmasearch-grid',
							columns: [
								{dataIndex:'f_id',   header:get_ag_lang('CDI_NAME'),            id:'f_id', width:70, resizable:true, fixed:true},
//								{dataIndex:'name_j', header:get_ag_lang('GRID_TITLE_NAME_J'), id:'name_j', hidden:true},
//								{dataIndex:'name_k', header:get_ag_lang('GRID_TITLE_NAME_K'), id:'name_k', hidden:true},
//								{dataIndex:'name_l', header:'Latina',                     id:'name_l', hidden:true},
								{dataIndex:'name_e', header:get_ag_lang('DETAIL_TITLE_NAME_E'),                    id:'name_e'}
							],
							selModel : new Ext.grid.CellSelectionModel(),
							store : fma_search_store,
							loadMask : true,
							maskDisabled : true,
							height: 234,
							stripeRows: true,
							columnLines    : true,
							tbar: [
								new Ext.app.SearchFMAStore({
									hideLabel: true,
									pageSize : 20,
									store    : fma_search_store
								}),'->',{
									id: 'anatomo-edit-fmasearch-grid-cell-copy',
									text: 'Paste',
									iuconCls: '',
									disabled: true,
									handler: function(e){
										var grid = Ext.getCmp('anatomo-edit-fmasearch-grid');
										var sel = grid.getSelectionModel();
										if(!sel || !sel.hasSelection()) return;
										var cellArr = sel.getSelectedCell();
										grid.fireEvent('celldblclick',grid,cellArr[0],cellArr[1],e);
									},
									scope: this
								}
							],
							bbar: new Ext.PagingToolbar({
								pageSize    : 20,
								store       : fma_search_store,
								displayInfo : false,
								displayMsg  : '',
								emptyMsg    : '',
								hideMode    : 'offsets',
								hideParent  : true
							}),
							listeners: {
								'render': function(grid){
									grid.getColumnModel().on({
										'hiddenchange' : function(column,columnIndex,hidden){
											resizeGridPanelColumns(Ext.getCmp('anatomo-edit-fmasearch-grid'));
										},
										scope: this,
										delay: 100
									});
								},
								'resize': function(grid){
									resizeGridPanelColumns(grid);
								},
								'cellclick': function(grid,rowIndex,columnIndex,e){
									if(rowIndex>=0 && rowIndex>=0) Ext.getCmp('anatomo-edit-fmasearch-grid-cell-copy').enable();
								},
								'celldblclick': function(grid,rowIndex,columnIndex,e){
//_dump('celldblclick');
									try{
										var record = grid.getStore().getAt(rowIndex);
										var fieldName = grid.getColumnModel().getDataIndex(columnIndex);
										var text = Ext.getCmp('anatomo-edit-comment-text');
										if(text){
											var dom = text.el.dom;
											if(dom.selectionStart != undefined){
												var st = dom.selectionStart>0?dom.value.slice(0,dom.selectionStart):"";
												var et = dom.value.slice(dom.selectionEnd);
												text.setValue(st+record.get(fieldName)+et);
											}else{
												text.focus();
												var selection = dom.ownerDocument.selection.createRange();
												selection.text = record.get(fieldName) + selection.text;
											}
										}
									}catch(e){
										for(var key in e){
											_dump(e[key]);
										}
									}
								},
								scope:this
							}
						}]
					}]



				}],
				buttons: [{
					text:'OK',
					handler : function() {
						var color = Ext.getCmp('anatomo-edit-color-palette').getValue();
						if(color.substr(0,1)=="#") color = color.substr(1);
//						records[0].set('comment', Ext.getCmp('anatomo-edit-comment-text').getValue().replace("\@","", "g").replace("\|","", "g"));
						records[0].set('comment', Ext.getCmp('anatomo-edit-comment-text').getValue());
						records[0].set('color', color);
						records[0].commit();
						win.close();
						updateAnatomo();
					}
				},{
					text:'Cancel',
					handler : function() {
						win.close();
					}
				}],
				listeners: {
					'render': function(win){
					},
					scope:this
				}

			});
			win.show();
		},
		"resize" : function(grid){
			resizeGridPanelColumns(grid);
		},
		"render" : function(grid){
			restoreHiddenGridPanelColumns(grid);
//			if(window.ag_extensions && ag_extensions.single_pin && ag_extensions.single_pin.bind) ag_extensions.single_pin.bind(grid);
		}
	},
	keys : {
		key : 'a',
		ctrl : true,
		stopEvent : true,
		handler: function () {
			ag_pin_grid_panel.getSelectionModel().selectAll();
		}
	}
});
ag_pin_grid_panel.getColumnModel().on({
	'hiddenchange' : function(column,columnIndex,hidden){
		resizeGridPanelColumns(ag_pin_grid_panel);
		saveHiddenGridPanelColumns(ag_pin_grid_panel);
	},
	scope: this,
	delay: 100
});
ag_pin_grid_panel.getStore().on({
	'add' : function(store,records,index){
		var selModel = ag_pin_grid_panel.getSelectionModel();
		selModel.fireEvent('selectionchange',selModel);
	},
	'remove' : function(store,records,index){
		var selModel = ag_pin_grid_panel.getSelectionModel();
		selModel.fireEvent('selectionchange',selModel);
	},
	scope: this
});

var ag_image_comment_panel = new Ext.Panel({
	title : 'Legend',
	id : 'ag_image_comment_panel',
	layout : 'form',
	labelWidth: 42,
	defaultType : 'textfield',
	bodyStyle: 'border: 0px; padding: 8px; overflow-x: hidden;overflow-y: auto;',
	items : [
		{
			fieldLabel : 'Title',
			name   : 'anatomography_image_comment_title',
			id     : 'anatomography_image_comment_title',
			anchor : '96%',
			listeners: {
				'render': function(comp){
					comp.setValue(init_anatomography_image_comment_title);
				},
				'change' : function(comp,newValue,oldValue){
					var check = Ext.getCmp('anatomography_image_comment_draw_check');
					if(check && check.rendered && check.getValue()) updateAnatomo();
				},
				scope:this
			}
		},{
			xtype : 'textarea',
			fieldLabel : 'Legend',
			name   : 'anatomography_image_comment_legend',
			id     : 'anatomography_image_comment_legend',
			height : 80,
			anchor : '96%',
			listeners: {
				'render': function(comp){
					comp.setValue(init_anatomography_image_comment_legend);
				},
				'change' : function(comp,newValue,oldValue){
					var check = Ext.getCmp('anatomography_image_comment_draw_check');
					if(check && check.rendered && check.getValue()) updateAnatomo();
				},
				scope:this
			}
		},{
			fieldLabel : 'Author',
			name   : 'anatomography_image_comment_author',
			id     : 'anatomography_image_comment_author',
			anchor : '96%',
			listeners: {
				'render': function(comp){
					comp.setValue(init_anatomography_image_comment_author);
				},
				'change' : function(comp,newValue,oldValue){
					var check = Ext.getCmp('anatomography_image_comment_draw_check');
					if(check && check.rendered && check.getValue()) updateAnatomo();
				},
				scope:this
			}
		}
	],
	bbar : [
		{
			id : 'anatomography_image_comment_draw_check',
			xtype : 'checkbox',
			boxLabel : 'Draw legend',
			value : init_anatomography_image_comment_draw,
			listeners: {
				'check' : function (checkbox, fChecked) {
					updateAnatomo();
				},
				'render': function(comp){
					comp.setValue(init_anatomography_image_comment_draw);
				},
				scope:this
			}
		}
	],
	listeners : {
		'afterlayout' : function(panel,layout){
			afterLayout(panel);
		},
		scope:this
	}
});

	var tree_expandnode = {};
	var formatTimestamp = function(val){
		return new Date(val).format(bp3d.defaults.TIME_FORMAT);
	}
	var anatomography_point_treepanel = new Ext.tree.TreePanel({
		id              : 'anatomography-point-treepanel',
		autoHeight      : true,
		autoScroll      : true,
		animate         : true,
		lines           : true,
		rootVisible     : false,
		monitorResize   : true,
		enableDD        : true,
		ddScroll        : true,
		containerScroll : true,
		useArrows       : false,
		border          : false,
		root : new Ext.tree.AsyncTreeNode({
			text      : get_ag_lang('TREE_ROOT_TITLE'),
			draggable : false,
			id        : 'root',
			expanded  : true,
			iconCls   : "ttopfolder"
		}),
		loader : new Ext.tree.TreeLoader({
			dataUrl : 'get-partof.cgi',
			baseParams : {
//				parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
//				lng    : gParams.lng,
				trash  : true
			},
			listeners : {
				'beforeload' : {
					fn : function(loader,node){
						loader.baseParams = loader.baseParams || {};
						var bp3d_version = Ext.getCmp('anatomo-version-combo');
						if(bp3d_version && bp3d_version.rendered){
							loader.baseParams.version = bp3d_version.getValue();
						}else{
							loader.baseParams.version = init_bp3d_version;
						}
					},scope : this
				},
				'load' : {
					fn : function(loader,node,response){
					},scope : this
				}
			}
		}),
		listeners : {
			"click" : {
				fn : function(node, event){
					if(gParams.id != undefined) delete gParams.id;
//					if(node.id == "root"){
//						Cookies.set('ag_annotation.images.id',"0");
//					}else{
//						Cookies.set('ag_annotation.images.id',"");
//					}
					selectPathCB(true,node);
				},scope : this},
			"dblclick" : {
				fn : function(node, event){
					event.stopEvent();
					event.stopPropagation();
				},scope : this},
			"append" : {
				fn:function(tree,parent,node,index){
					if(node.id == 'trash'){
						node.reload();
						return;
					}
					node.attributes.attr = node.attributes.attr || {};
					if(node.attributes.attr.lastmod && typeof node.attributes.attr.lastmod == "string"){
						node.attributes.attr.lastmod = new Date(parseInt(node.attributes.attr.lastmod)*1000);
						node.attributes.attr.dateString = formatTimestamp(node.attributes.attr.lastmod);
					}
					if(node.isLeaf()) return;
					if(tree_expandnode[node.id] == undefined){
						tree_expandnode[node.id] = node.isExpanded();
					}else if(tree_expandnode[node.id]){
						if(!node.isExpanded()) node.expand(false,false);
					}else{
						if(node.isExpanded()) node.collapse(false,false);
					}
				},scope:this},
			"remove" : {
				fn:function(tree,parent,node){
				},scope:this},
			"contextmenu" : {
				fn:function(node, event){
				},scope:this},
			"collapsenode" : {
				fn:function(node){
					tree_expandnode[node.id] = false;
				},scope:this},
			"expandnode" : {
				fn:function(node){
					tree_expandnode[node.id] = true;
				},scope:this},

			"nodedragover" : {
				fn : function(dragOverEvent){
					if(dragOverEvent.target.id == 'trash' && dragOverEvent.point == 'below'){
						dragOverEvent.cancel = true;
						return;
					}
					if(dragOverEvent.target.id == 'root' && dragOverEvent.point == 'append'){
						dragOverEvent.cancel = true;
						return;
					}
				},scope : this},
			"nodedrop" : {
				fn : function(dragOverEvent){
					var node = dragOverEvent.dropNode;
					var parentNode = node.parentNode;

					var trashNode = dragOverEvent.tree.getNodeById('trash');
					if(trashNode && trashNode.contains(dragOverEvent.dropNode)){
						node.attributes.attr.delcause = (new Date).toString();
					}else{
						node.attributes.attr.t_pid = parentNode.attributes.attr.t_id;
						node.attributes.attr.delcause = '';
					}
					var childNode = parentNode.firstChild;
					var t_order = 0;
					var attrs = [];
					while(childNode){
						childNode.attributes.attr = childNode.attributes.attr || {};
						childNode.attributes.attr.t_order = ++t_order;
						if(childNode.attributes.attr.t_id){
							attrs.push({
								t_id     : childNode.attributes.attr.t_id,
								t_pid    : childNode.attributes.attr.t_pid,
								t_order  : childNode.attributes.attr.t_order,
								delcause : childNode.attributes.attr.delcause
							});
						}
						childNode = childNode.nextSibling;
					}
					if(attrs.length>0){
						putTree(
							attrs,
							get_ag_lang('ADMIN_PROMPT_CHANGE_TITLE'),
							undefined,
							function(){
								var treeCmp = Ext.getCmp('navigate-tree-panel');
								if(!treeCmp || !treeCmp.root) return;
								treeCmp.root.reload(
									function(node){
										node.getOwnerTree().selectPath("/root" + Cookies.get('ag_annotation.images.path'));
									}
								);
							}
						);
					}
				},scope : this}
		}
	});


	var anatomography_point_jsonstore_fields = [
		{name:'f_id'},
		{name:'b_id'},
		{name:'common_id'},
		{name:'name_j'},
		{name:'name_e'},
		{name:'name_k'},
		{name:'name_l'},
		{name:'phase'},
		'version',
//		'tg_id',
//		'tgi_id',
		{name:'tg_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.md_id;
			}else{
				return v;
			}
		}},
		{name:'tgi_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.mv_id;
			}else{
				return v;
			}
		}},

		'segment',
		'seg_color',
		'seg_thum_bgcolor',
		'seg_thum_bocolor',

		{name:'entry', type:'date', dateFormat: 'timestamp'},
		{name:'xmin',    type:'float'},
		{name:'xmax',    type:'float'},
		{name:'ymin',    type:'float'},
		{name:'ymax',    type:'float'},
		{name:'zmin',    type:'float'},
		{name:'zmax',    type:'float'},
		{name:'volume',  type:'float'},
		{name:'organsys'},
		{name:'elem_type'},
		{name:'def_color'},
		{name:'bul_id',type:'int'},
		{name:'cb_id',type:'int'},
		{name:'ci_id',type:'int'},
		{name:'md_id',type:'int'},
		{name:'mv_id',type:'int'},
		{name:'mr_id',type:'int'}
	];

	var change_partof_route = function(store,route_number){
		var records = store.getRange();
		var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
		loader.removeAll();
		var w_records = [];
		var route_pos = route_number;
		for(var i=0;i<records.length;i++){
			if(route_pos>0){
				if(Ext.isEmpty(records[i].get('f_id'))) route_pos--;
				continue;
			}
			if(Ext.isEmpty(records[i].get('f_id'))) break;
			w_records.push(records[i]);
		}
		var route_num = 0;
		var route_arr = [];
		for(var i=0;i<records.length;i++){
			if(Ext.isEmpty(records[i].get('f_id'))){
				route_num++;
				if(route_num==route_number){
					route_arr.push(route_num);
				}else if(route_num>10){
					route_arr.push('...');
					break;
				}else{
					route_arr.push('<a href="#" onclick="change_partof_route(anatomography_point_partof_store,'+route_num+');return false;">&nbsp;'+route_num+'&nbsp;</a>');
				}
			}
		}
		var elem = Ext.getDom('ag-point-grid-content-route');
		if(elem){
			elem.innerHTML = route_arr.join(",&nbsp;&nbsp;");
		}
		loader.add(w_records);
	};

	var change_isa_route = function(store,route_number){
		var records = store.getRange();
		var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
		loader.removeAll();
		var w_records = [];
		var route_pos = route_number;
		for(var i=0;i<records.length;i++){
			if(route_pos>0){
				if(Ext.isEmpty(records[i].get('f_id'))) route_pos--;
				continue;
			}
			if(Ext.isEmpty(records[i].get('f_id'))) break;
			w_records.push(records[i]);
		}
		var route_num = 0;
		var route_arr = [];
		for(var i=0;i<records.length;i++){
			if(Ext.isEmpty(records[i].get('f_id'))){
				route_num++;
				if(route_num==route_number){
					route_arr.push(route_num);
				}else if(route_num>10){
					route_arr.push('...');
					break;
				}else{
					route_arr.push('<a href="#" onclick="change_isa_route(anatomography_point_isa_store,'+route_num+');return false;">&nbsp;'+route_num+'&nbsp;</a>');
				}
			}
		}
		var elem = Ext.getDom('ag-point-grid-content-route');
		if(elem){
			elem.innerHTML = route_arr.join(",&nbsp;&nbsp;");
		}
		loader.add(w_records);
	};

	var change_conventional_route = function(store,route_number){
		var records = store.getRange();
		var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
		loader.removeAll();
		var w_records = [];
		var route_pos = route_number;
		for(var i=0;i<records.length;i++){
			if(route_pos>0){
				if(Ext.isEmpty(records[i].get('f_id'))) route_pos--;
				continue;
			}
			if(Ext.isEmpty(records[i].get('f_id'))) break;
			w_records.push(records[i]);
		}
		var route_num = 0;
		var route_arr = [];
		for(var i=0;i<records.length;i++){
			if(Ext.isEmpty(records[i].get('f_id'))){
				route_num++;
				if(route_num==route_number){
					route_arr.push(route_num);
				}else if(route_num>10){
					route_arr.push('...');
					break;
				}else{
					route_arr.push('<a href="#" onclick="change_conventional_route(anatomography_point_conventional_root_store,'+route_num+');return false;">&nbsp;'+route_num+'&nbsp;</a>');
				}
			}
		}
		var elem = Ext.getDom('ag-point-grid-content-route');
		if(elem){
			elem.innerHTML = route_arr.join(",&nbsp;&nbsp;");
		}
		loader.add(w_records);
	};

	var anatomography_point_store_beforeload = function(store,options){
		var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
		loader.removeAll();
		loader.baseParams = {};
		var elem = Ext.getDom('ag-point-grid-content-route');
		if(elem) elem.innerHTML = '&nbsp;';

		store.baseParams = store.baseParams || {};
		var bp3d_version = Ext.getCmp('anatomo-version-combo');
		if(bp3d_version && bp3d_version.rendered){
			store.baseParams.version = bp3d_version.getValue();
		}else{
			store.baseParams.version = init_bp3d_version;
		}
		for(var key in init_bp3d_params){
			if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
		}

		try{
			var store = Ext.getCmp('anatomo-version-combo').getStore();
			var idx = store.findBy(function(record,id){
				if(record.data.tgi_version==store.baseParams.version) return true;
			});
			if(idx>=0){
				var record = store.getAt(idx);
				if(record){
					store.baseParams.md_id = record.data.md_id;
					store.baseParams.mv_id = record.data.mv_id;
					store.baseParams.mr_id = record.data.mr_id;
					store.baseParams.ci_id = record.data.ci_id;
					store.baseParams.cb_id = record.data.cb_id;
				}
			}
		}catch(e){}
	};

	var anatomography_point_store_load = function(store,records,options){
		if(records.length>0){
			var elem = Ext.getDom('ag-point-grid-content-route');
			if(elem) elem.innerHTML = '-';
		}
		Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
		Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
		var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
		loader.removeAll();
		loader.baseParams = store.baseParams;
		return loader;
	};

	var anatomography_point_partof_store = new Ext.data.JsonStore({
		url           : 'get-partof.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true,
		listeners     : {
			"beforeload" : function(store,options){
/*
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = {};
				var elem = Ext.getDom('ag-point-grid-content-route');
				if(elem) elem.innerHTML = '&nbsp;';

				store.baseParams = store.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					store.baseParams.version = bp3d_version.getValue();
				}else{
					store.baseParams.version = init_bp3d_version;
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('anatomo-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==store.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							store.baseParams.md_id = record.data.md_id;
							store.baseParams.mv_id = record.data.mv_id;
							store.baseParams.mr_id = record.data.mr_id;
							store.baseParams.ci_id = record.data.ci_id;
							store.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
*/
				anatomography_point_store_beforeload(store);
			},
			"load" : function(store,records,options){
/*
				if(records.length>0){
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '-';
				}
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = store.baseParams;
*/
				var loader = anatomography_point_store_load(store,records);
				if(Ext.isEmpty(records[0].get('f_id'))){
					change_partof_route(store,1);
				}else{
					loader.add(records);
				}
			},
			"loadexception" : function(){
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
			},
			scope : this
		}
	});

	var anatomography_point_haspart_store = new Ext.data.JsonStore({
		url           : 'get-haspart.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true,
		listeners     : {
			"beforeload" : function(store,options){
/*
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = {};
				var elem = Ext.getDom('ag-point-grid-content-route');
				if(elem) elem.innerHTML = '&nbsp;';

				store.baseParams = store.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					store.baseParams.version = bp3d_version.getValue();
				}else{
					store.baseParams.version = init_bp3d_version;
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('anatomo-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==store.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							store.baseParams.md_id = record.data.md_id;
							store.baseParams.mv_id = record.data.mv_id;
							store.baseParams.mr_id = record.data.mr_id;
							store.baseParams.ci_id = record.data.ci_id;
							store.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
*/
				anatomography_point_store_beforeload(store);
			},
			"load" : function(store,records,options){
/*
				if(records.length>0){
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '-';
				}
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = store.baseParams;
*/
				var loader = anatomography_point_store_load(store,records);
				loader.add(records);
			},
			"loadexception" : function(){
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
			},
			scope : this
		}
	});

	var anatomography_point_isa_store = new Ext.data.JsonStore({
		url           : 'get-isa.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true,
		listeners     : {
			"beforeload" : function(store,options){
/*
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = {};
				var elem = Ext.getDom('ag-point-grid-content-route');
				if(elem) elem.innerHTML = '&nbsp;';

				store.baseParams = store.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					store.baseParams.version = bp3d_version.getValue();
				}else{
					store.baseParams.version = init_bp3d_version;
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('anatomo-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==store.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							store.baseParams.md_id = record.data.md_id;
							store.baseParams.mv_id = record.data.mv_id;
							store.baseParams.mr_id = record.data.mr_id;
							store.baseParams.ci_id = record.data.ci_id;
							store.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
*/
				anatomography_point_store_beforeload(store);
			},
			"load" : function(store,records,options){
/*
				if(records.length>0){
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '-';
				}
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = store.baseParams;
*/
				var loader = anatomography_point_store_load(store,records);
				if(Ext.isEmpty(records[0].get('f_id'))){
					change_isa_route(store,1);
				}else{
					loader.add(records);
				}
			},
			"loadexception" : function(){
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
			},
			scope : this
		}
	});

	var anatomography_point_hasmember_store = new Ext.data.JsonStore({
		url           : 'get-hasmember.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true,
		listeners     : {
			"beforeload" : function(store,options){
/*
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = {};
				var elem = Ext.getDom('ag-point-grid-content-route');
				if(elem) elem.innerHTML = '&nbsp;';

				store.baseParams = store.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					store.baseParams.version = bp3d_version.getValue();
				}else{
					store.baseParams.version = init_bp3d_version;
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('anatomo-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==store.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							store.baseParams.md_id = record.data.md_id;
							store.baseParams.mv_id = record.data.mv_id;
							store.baseParams.mr_id = record.data.mr_id;
							store.baseParams.ci_id = record.data.ci_id;
							store.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
*/
				anatomography_point_store_beforeload(store);

			},
			"load" : function(store,records,options){
/*
				if(records.length>0){
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '-';
				}
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = store.baseParams;
*/
				var loader = anatomography_point_store_load(store,records);
				loader.add(records);
			},
			"loadexception" : function(){
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
			},
			scope : this
		}
	});

	var anatomography_point_conventional_root_store = new Ext.data.JsonStore({
		url           : 'get-conventional_root.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true,
		listeners     : {
			"beforeload" : function(store,options){
/*
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = {};
				var elem = Ext.getDom('ag-point-grid-content-route');
				if(elem) elem.innerHTML = '&nbsp;';

				store.baseParams = store.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					store.baseParams.version = bp3d_version.getValue();
				}else{
					store.baseParams.version = init_bp3d_version;
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('anatomo-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==store.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							store.baseParams.md_id = record.data.md_id;
							store.baseParams.mv_id = record.data.mv_id;
							store.baseParams.mr_id = record.data.mr_id;
							store.baseParams.ci_id = record.data.ci_id;
							store.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
*/
				anatomography_point_store_beforeload(store);
			},
			"load" : function(store,records,options){
/*
				if(records.length>0){
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '-';
				}
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = store.baseParams;
*/
				var loader = anatomography_point_store_load(store,records);
				if(Ext.isEmpty(records[0].get('f_id'))){
					change_conventional_route(store,1);
				}else{
					loader.add(records);
				}
			},
			"loadexception" : function(){
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
			},
			scope : this
		}
	});

	var anatomography_point_conventional_child_store = new Ext.data.JsonStore({
		url           : 'get-conventional_child.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true,
		listeners     : {
			"beforeload" : function(store,options){
/*
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = {};
				var elem = Ext.getDom('ag-point-grid-content-route');
				if(elem) elem.innerHTML = '&nbsp;';

				store.baseParams = store.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					store.baseParams.version = bp3d_version.getValue();
				}else{
					store.baseParams.version = init_bp3d_version;
				}
				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('anatomo-version-combo').getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.tgi_version==store.baseParams.version) return true;
					});
					if(idx>=0){
						var record = store.getAt(idx);
						if(record){
							store.baseParams.md_id = record.data.md_id;
							store.baseParams.mv_id = record.data.mv_id;
							store.baseParams.mr_id = record.data.mr_id;
							store.baseParams.ci_id = record.data.ci_id;
							store.baseParams.cb_id = record.data.cb_id;
						}
					}
				}catch(e){}
*/
				anatomography_point_store_beforeload(store);
			},
			"load" : function(store,records,options){
/*
				if(records.length>0){
					var elem = Ext.getDom('ag-point-grid-content-route');
					if(elem) elem.innerHTML = '-';
				}
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
				var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
				loader.removeAll();
				loader.baseParams = store.baseParams;
*/
				var loader = anatomography_point_store_load(store,records);
				loader.add(records);
			},
			"loadexception" : function(){
				Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
				Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
			},
			scope : this
		}
	});

HTML
if($usePickPalletSelect ne 'false'){
	print <<HTML;
	var anatomography_pallet_point_partof_store = new Ext.data.JsonStore({
		url           : 'get-partof.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true
	});

	var anatomography_pallet_point_isa_store = new Ext.data.JsonStore({
		url           : 'get-isa.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true
	});

	var anatomography_pallet_point_conventional_root_store = new Ext.data.JsonStore({
		url           : 'get-conventional_root.cgi',
		totalProperty : 'total',
		root          : 'data',
		fields        : anatomography_point_jsonstore_fields,
		remoteSort    : true
	});

	var anatomography_pallet_point_beforeload = function(store,options){
		store.baseParams = store.baseParams || {};
		var bp3d_version = Ext.getCmp('anatomo-version-combo');
		if(bp3d_version && bp3d_version.rendered){
			store.baseParams.version = bp3d_version.getValue();
		}else{
			store.baseParams.version = init_bp3d_version;
		}
		for(var key in init_bp3d_params){
			if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
		}
		try{
			var store = Ext.getCmp('anatomo-version-combo').getStore();
			var idx = store.findBy(function(record,id){
				if(record.data.tgi_version==store.baseParams.version) return true;
			});
			if(idx>=0){
				var record = store.getAt(idx);
				if(record){
					store.baseParams.md_id = record.data.md_id;
					store.baseParams.mv_id = record.data.mv_id;
					store.baseParams.mr_id = record.data.mr_id;
					store.baseParams.ci_id = record.data.ci_id;
					store.baseParams.cb_id = record.data.cb_id;
				}
			}
		}catch(e){}
	};

	var anatomography_pallet_point_load = function(store,records,options){
		Ext.getCmp('ag-parts-gridpanel').loadMask.hide();

//		var activeTab = ag_comment_tabpanel.getActiveTab();
		var activeTab = Ext.getCmp('ag-parts-gridpanel')

		if(Ext.isEmpty(activeTab)) return;
		var selModel = activeTab.getSelectionModel();
		selModel.clearSelections();

		var group_records = [];
		var group_count = -1;
		for(var i=0;i<records.length;i++){
			var f_id = records[i].get('f_id');
			if(Ext.isEmpty(f_id)){
				group_count++;
				continue;
			}
			if(group_count<0) group_count = 0;
			if(Ext.isEmpty(group_records[group_count])) group_records[group_count] = [];
			group_records[group_count].push(records[i]);
		}
		group_records.sort(function(a,b){return b.length-a.length});

		var max_pos = 1;
		for(var i=0;i<group_records.length;i++){
			var index = -1;
			for(var j=0;j<group_records[i].length;j++){
				var f_id = group_records[i][j].get('f_id');
				if(Ext.isEmpty(f_id)) continue;
				if(max_pos<(j+1)/group_records[i].length) continue;//そのグループ内の位置を割合で比較
				var regexp = new RegExp("^"+f_id+"\$");
				index = bp3d_parts_store.find('f_id',regexp);
				if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
				if(index<0) continue;
				max_pos=(j+1)/group_records[i].length;
				selModel.selectRow(index);
HTML
if($useClickPickTabSelect eq 'true'){
	print <<HTML;
				if(ag_comment_tabpanel.getActiveTab().id == 'ag-parts-gridpanel'){
					activeTab.getView().focusRow(index);
				}else{
					glb_point_pallet_index = index;
				}
HTML
}else{
	print <<HTML;
				activeTab.getView().focusRow(index);
HTML
}
print <<HTML;
				break;
			}
		}
	};
	var anatomography_pallet_point_loadexception = function(){
		Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
	};

	anatomography_pallet_point_partof_store.on('beforeload',anatomography_pallet_point_beforeload,this);
	anatomography_pallet_point_partof_store.on('load',anatomography_pallet_point_load,this);
	anatomography_pallet_point_partof_store.on('loadexception',anatomography_pallet_point_loadexception,this);

	anatomography_pallet_point_isa_store.on('beforeload',anatomography_pallet_point_beforeload,this);
	anatomography_pallet_point_isa_store.on('load',anatomography_pallet_point_load,this);
	anatomography_pallet_point_isa_store.on('loadexception',anatomography_pallet_point_loadexception,this);

	anatomography_pallet_point_conventional_root_store.on('beforeload',anatomography_pallet_point_beforeload,this);
	anatomography_pallet_point_conventional_root_store.on('load',anatomography_pallet_point_load,this);
	anatomography_pallet_point_conventional_root_store.on('loadexception',anatomography_pallet_point_loadexception,this);
HTML
}
print <<HTML;

	function anatomography_point_grid_group_renderer(value,metadata,record,rowIndex,colIndex,store){
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return gID2TreeGroup[value];
	}

	function anatomography_point_grid_renderer(value,metadata,record,rowIndex,colIndex,store){

		var dataIndex = anatomography_point_grid_cols()[colIndex].dataIndex;
		var item;
		for(var i=0;i<record.fields.length;i++){
			if(record.fields.keys[i] != dataIndex) continue;
			item = record.fields.items[i];
			break;
		}

		if(item){
			if(item.type == 'date'){
				if(dataIndex == 'entry' && value) value = new Date(value).format(bp3d.defaults.DATE_FORMAT);
				if(dataIndex == 'lastmod' && value) value = new Date(value).format(bp3d.defaults.TIME_FORMAT);
			}
		}

		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return value;
	}

	function anatomography_point_grid_combobox_renderer(value,metadata,record,rowIndex,colIndex,store){
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
			value = "";
		}else{
			if(record.data.partslist){
			}else{
				value = "";
			}
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return value;
	}

	function anatomography_point_grid_partslist_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
		var id = Ext.getCmp('anatomography-point-editorgrid-panel').getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td'; 
		if(isNoneDataRecord(record)) metadata.css += ' ag_point_none_data'; 
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data';
		if(record.data.seg_color) metadata.attr = 'style="background:'+record.data.seg_color+';"'
		if(isAdditionPartsList()){
			return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
		}else{
			return '<div class="ag_grid_checkbox'+(value?'-on':'')+'-dis x-grid3-cc-'+id+'">&#160;</div>';
		}
	}

	function anatomography_point_grid_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
		var id = Ext.getCmp('anatomography-point-editorgrid-panel').getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td'; 
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}else{
			if(record.data.partslist){
			}else{
				metadata.css += ' ag_point_none_pallet_data'; 
			}
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
	}

	function anatomography_point_grid_point_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
		var id = Ext.getCmp('anatomography-point-editorgrid-panel').getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td'; 
		if(isNoneDataRecord(record) || isPointDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}else{
			if(record.data.partslist){
			}else{
				metadata.css += ' ag_point_none_pallet_data'; 
			}
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
	}

	var anatomography_point_grid_color_cell_style = function (value,metadata,record,rowIndex,colIndex,store) {
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data';
			return '';
		}else{
			if(record.data.partslist && value){
				return '<span style="background-color:' + value + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>';
			}else{
				return '';
			}
		}
		return value;
	};

	var anatomography_point_grid_col_opacity_arr = [
		['1.0', '1.0'],
		['0.8', '0.8'],
		['0.6', '0.6'],
		['0.4', '0.4'],
		['0.3', '0.3'],
		['0.2', '0.2'],
		['0.1', '0.1'],
		['0.05', '0.05'],
		['0.0', '0.0']
	];

	var anatomography_point_grid_col_representation_arr = [
		['surface', 'surface'],
		['wireframe', 'wireframe'],
		['points', 'points']
	];

	var anatomography_point_grid_fields = function(){
		return [
			{name:'partslist'},
			{name:'common_id'},
			{name:'b_id'},
			{name:'f_id'},
			{name:'name_j'},
			{name:'name_e'},
			{name:'name_k'},
			{name:'name_l'},
			{name:'phase'},
			'version',
//		'tg_id',
//		'tgi_id',
			{name:'tg_id',type:'int',convert:function(v,r){
				if(Ext.isEmpty(v)){
					return r.md_id;
				}else{
					return v;
				}
			}},
			{name:'tgi_id',type:'int',convert:function(v,r){
				if(Ext.isEmpty(v)){
					return r.mv_id;
				}else{
					return v;
				}
			}},

			'segment',
			'seg_color',
			'seg_thum_bgcolor',
			'seg_thum_bocolor',

			{name:'entry',   type:'date', dateFormat: 'timestamp'},
			{name:'xmin',    type:'float'},
			{name:'xmax',    type:'float'},
			{name:'ymin',    type:'float'},
			{name:'ymax',    type:'float'},
			{name:'zmin',    type:'float'},
			{name:'zmax',    type:'float'},
			{name:'volume',  type:'float'},
			{name:'organsys'},
			{name:'color'},
			{name:'value'},
			{name:'zoom',type:'boolean'},
			{name:'exclude',type:'boolean'},
			{name:'opacity',type:'float'},
			{name:'representation'},
			{name:'point',type:'boolean'},
			{name:'elem_type'},
			{name:'def_color'},
			{name:'bul_id',type:'int'},
			{name:'cb_id',type:'int'},
			{name:'ci_id',type:'int'},
			{name:'md_id',type:'int'},
			{name:'mv_id',type:'int'},
			{name:'mr_id',type:'int'}
		];
	};

	var anatomography_point_grid_partslist_checkColumn = new Ext.grid.CheckColumn({
		header    : 'Pallet',
		dataIndex : 'partslist',
		width     : 40,
		fixed     : true,
		renderer  : anatomography_point_grid_partslist_checkbox_renderer
	});
	var anatomography_point_grid_zoom_checkColumn = new Ext.grid.CheckColumn({
		header    : "Zoom",
		dataIndex : 'zoom',
		hidden    : true,
		width     : 40,
		resizable : false,
		renderer  : anatomography_point_grid_checkbox_renderer
	});

	var anatomography_point_grid_exclude_checkColumn = new Ext.grid.CheckColumn({
		header    : "Remove",
		dataIndex : 'exclude',
		width     : 50,
		resizable : false,
		renderer  : anatomography_point_grid_checkbox_renderer
	});

	var anatomography_point_grid_point_checkColumn = new Ext.grid.CheckColumn({
		header    : 'Point',
		dataIndex : 'point',
		width     : 40,
		resizable : false,
		renderer  : anatomography_point_grid_point_checkbox_renderer
	});

var anatomography_point_grid_col_version = {
	dataIndex:'version',
	header:'Version',
	id:'version',
	sortable: false,
	renderer: anatomography_point_grid_renderer,
	hidden:true
};
var anatomography_point_grid_col_rep_id = {
	dataIndex:'b_id',
	header:get_ag_lang('REP_ID'),
	renderer: anatomography_point_grid_renderer,
	id:'b_id'
};
var anatomography_point_grid_col_cdi_name = {
	dataIndex:'f_id',
	header:get_ag_lang('CDI_NAME'),
	renderer: anatomography_point_grid_renderer,
	id:'f_id'
};
var anatomography_point_grid_col_color = {
	dataIndex : 'color',
	header    : 'Color',
	id        : 'color',
	width     : 40,
	resizable : false,
	renderer  : anatomography_point_grid_color_cell_style,
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
	editor    : new Ext.ux.ColorPickerField({
		menuListeners : {
			select: function(e, c){
				this.setValue(c);
				try{var record = Ext.getCmp('anatomography-point-editorgrid-panel')._edit.record;}catch(e){_dump("color:"+e);}
				if(record){
					record.beginEdit();
					record.set('color',"#"+c);
					record.commit();
					record.endEdit();

					var grid = Ext.getCmp('ag-parts-gridpanel');
					var store = grid.getStore();
					var f_id = record.get('f_id');
					var record = null;
					var regexp = new RegExp("^"+f_id+"\$");
					var index = store.find('f_id',regexp);
					if(index<0) index = store.find('conv_id',regexp);
					if(index>=0) record = store.getAt(index);
					if(record){
						record.set('color',"#"+c);
						record.commit();
					}
				}
			},
			show : function(){ // retain focus styling
				this.onFocus();
			},
			hide : function(){
				this.focus.defer(10, this);
			},
			beforeshow : function(menu) {
				try {
					if (this.value != "") {
						menu.palette.select(this.value);
					} else {
						this.setValue("");
						var el = menu.palette.el;
						if(menu.palette.value){
							try{el.child("a.color-"+menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
							menu.palette.value = null;
						}
					}
				}catch(ex){}
			}
		}
	})
HTML
}else{
	print <<HTML;
	editor    : new Ext.ux.ColorField({
		listeners : {
			select: function(e, c){
				this.setValue(c);
				try{var record = Ext.getCmp('anatomography-point-editorgrid-panel')._edit.record;}catch(e){_dump("color:"+e);}
				if(record){
					record.beginEdit();
					record.set('color',"#"+c);
					record.commit();
					record.endEdit();

					var grid = Ext.getCmp('ag-parts-gridpanel');
					var store = grid.getStore();
					var f_id = record.get('f_id');
					var record = null;
					var regexp = new RegExp("^"+f_id+"\$");
					var index = store.find('f_id',regexp);
					if(index<0) index = store.find('conv_id',regexp);
					if(index>=0) record = store.getAt(index);
					if(record){
						record.set('color',"#"+c);
						record.commit();
					}
				}
			}
		}
	})
HTML
}
print <<HTML;
};
var anatomography_point_grid_col_opacity = {
	dataIndex : 'opacity',
	header    : 'Opacity',
	id        : 'opacity',
	width     : 50,
	resizable : false,
	align     : 'right',
	renderer: anatomography_point_grid_combobox_renderer,
	editor    : new Ext.form.ComboBox({
		typeAhead     : true,
		triggerAction : 'all',
		store         : anatomography_point_grid_col_opacity_arr,
		lazyRender    : true,
		listClass     : 'x-combo-list-small',
		listeners     : {
			'select' : function(combo,record,index){
				try{var record = Ext.getCmp('anatomography-point-editorgrid-panel')._edit.record;}catch(e){_dump("opacity:"+e);}
				if(record){
					record.beginEdit();
					record.set('opacity',combo.getValue());
					record.commit();
					record.endEdit();

					var store = Ext.getCmp('ag-parts-gridpanel').getStore();
					var f_id = record.get('f_id');
					var record = null;
					var regexp = new RegExp("^"+f_id+"\$");
					var index = store.find('f_id',regexp);
					if(index<0) index = store.find('conv_id',regexp);
					if(index>=0) record = store.getAt(index);
					if(record){
						record.set('opacity',combo.getValue());
						record.commit();
					}
				}
			},
			scope : this
		}
	})
};
var anatomography_point_grid_col_representation = {
	dataIndex : 'representation',
	header    : get_ag_lang('ANATOMO_REP_LABEL'),
	id        : 'representation',
	width     : 40,
	resizable : false,
	renderer  : anatomography_point_grid_combobox_renderer,
	hidden    : true,
	hideable  : true,
	editor    : new Ext.form.ComboBox({
		typeAhead     : true,
		triggerAction : 'all',
		store         : anatomography_point_grid_col_representation_arr,
		lazyRender    : true,
		listClass     : 'x-combo-list-small',
		listeners     : {
			'select' : function(combo,record,index){
				try{var record = Ext.getCmp('anatomography-point-editorgrid-panel')._edit.record;}catch(e){_dump("representation:"+e);}
				if(record){
					record.beginEdit();
					record.set('representation',combo.getValue());
					record.commit();
					record.endEdit();

					var store = Ext.getCmp('ag-parts-gridpanel').getStore();
					var f_id = record.get('f_id');
					var record = null;
					var regexp = new RegExp("^"+f_id+"\$");
					var index = store.find('f_id',regexp);
					if(index<0) index = store.find('conv_id',regexp);
					if(index>=0) record = store.getAt(index);
					if(record){
						record.set('representation',combo.getValue());
						record.commit();
					}
				}
			},scope : this
		}
	})
};
var anatomography_point_grid_col_value = {
	dataIndex : 'value',
	header    : 'Value',
	id        : 'value',
	width     : 40,
	resizable : false,
	renderer  : anatomography_point_grid_renderer,
	hidden    : true,
	editor    : new Ext.form.TextField({
		allowBlank : true
	})
};
var anatomography_point_grid_col_organsys = {
	dataIndex:'organsys',
	header:get_ag_lang('GRID_TITLE_ORGANSYS'),
	renderer: anatomography_point_grid_renderer,
	id:'organsys',
	hidden:true
};
var anatomography_point_grid_col_entry = {
	dataIndex:'entry',
	header:get_ag_lang('GRID_TITLE_MODIFIED'),
	renderer: anatomography_point_grid_renderer,
	id:'entry',
	hidden:true
};


var anatomography_point_grid_cols = function(){ return [
	anatomography_point_grid_partslist_checkColumn,
	{dataIndex:'tg_id', header:'Model', id:'tg_id', sortable: false, renderer:anatomography_point_grid_group_renderer, hidden:true, fixed:$groupHidden},
HTML
print qq|	anatomography_point_grid_col_version,\n| if($moveGridOrder ne 'true');
print <<HTML;
	{dataIndex:'common_id',header:'UniversalID', renderer: anatomography_point_grid_renderer, id:'common_id',hidden:true, fixed:$gridColFixedUniversalID},
HTML
print qq|	anatomography_point_grid_col_rep_id,\n| if($moveGridOrder ne 'true');
print qq|	anatomography_point_grid_col_cdi_name,\n| if($moveGridOrder ne 'true');
print <<HTML;
//	{dataIndex:'name_j', header:get_ag_lang('GRID_TITLE_NAME_J'), renderer: anatomography_point_grid_renderer, id:'name_j', hidden:$gridColHiddenNameJ},
//	{dataIndex:'name_k', header:get_ag_lang('GRID_TITLE_NAME_K')', renderer: anatomography_point_grid_renderer, id:'name_k', hidden:$gridColHiddenNameK},
	{dataIndex:'name_e', header:get_ag_lang('DETAIL_TITLE_NAME_E'),                    renderer: anatomography_point_grid_renderer, id:'name_e'},
//	{dataIndex:'name_l', header:'Latina',                     renderer: anatomography_point_grid_renderer, id:'name_l', hidden:true},
HTML
if($moveGridOrder ne 'true'){
	print <<HTML;
	{dataIndex:'phase',    header:get_ag_lang('GRID_TITLE_PHASE'),    renderer: anatomography_point_grid_renderer, id:'phase', hidden:true},
	anatomography_point_grid_col_entry, 
HTML
}else{
	print <<HTML;
	anatomography_point_grid_col_color,
	anatomography_point_grid_col_opacity,
	anatomography_point_grid_exclude_checkColumn,
	anatomography_point_grid_col_value,
//	anatomography_point_grid_col_organsys,
	anatomography_point_grid_col_representation,
	anatomography_point_grid_col_rep_id,
	anatomography_point_grid_col_cdi_name,
HTML
}
print <<HTML;
	{dataIndex:'xmin',  header:'Xmin(mm)',                        renderer: anatomography_point_grid_renderer, id:'xmin',     hidden:true},
	{dataIndex:'xmax',  header:'Xmax(mm)',                        renderer: anatomography_point_grid_renderer, id:'xmax',     hidden:true},
	{dataIndex:'ymin',  header:'Ymin(mm)',                        renderer: anatomography_point_grid_renderer, id:'ymin',     hidden:true},
	{dataIndex:'ymax',  header:'Ymax(mm)',                        renderer: anatomography_point_grid_renderer, id:'ymax',     hidden:true},
	{dataIndex:'zmin',  header:'Zmin(mm)',                        renderer: anatomography_point_grid_renderer, id:'zmin',     hidden:true},
	{dataIndex:'zmax',  header:'Zmax(mm)',                        renderer: anatomography_point_grid_renderer, id:'zmax',     hidden:true},
	{dataIndex:'volume',header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', renderer: anatomography_point_grid_renderer, id:'volume',   hidden:true},
HTML
if($moveGridOrder ne 'true'){
#	print qq|	{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', renderer: anatomography_point_grid_renderer, id:'volume',   hidden:true},\n| if($removeGridColValume ne 'true');
#	print qq|	anatomography_point_grid_col_organsys,\n| if($removeGridColOrganSystem ne 'true');
	print <<HTML;
	anatomography_point_grid_exclude_checkColumn,
	anatomography_point_grid_col_color,
	anatomography_point_grid_col_opacity,
	anatomography_point_grid_col_representation,
	anatomography_point_grid_col_value
HTML
}else{
	print <<HTML;
	anatomography_point_grid_col_version,
	anatomography_point_grid_col_entry
HTML
}
if($addPointElementHidden ne 'true'){
	print <<HTML;
	,anatomography_point_grid_point_checkColumn
HTML
}
print <<HTML;
];
};

update_anatomography_point_grid = function(aParam){
	var store = anatomography_point_grid.ds;
	var bp3d_parts_store = ag_parts_gridpanel.getStore();


	function update_anatomography_point_record(aRecord){
		var index = store.find('f_id',new RegExp("^"+aRecord.get('f_id')+"\$"));
		if(index<0) return;
		var record = store.getAt(index);
		if(!record) return;

		var aIndex = bp3d_parts_store.indexOf(aRecord);
		if(aIndex>=0){
			record.beginEdit();
			record.set('partslist',true);
			for(var reckey in aRecord.data){
				record.set(reckey,aRecord.data[reckey]);
			}
			record.commit();
			record.endEdit();
		}else{
			record.beginEdit();
			record.set('partslist',false);
			record.commit();
			record.endEdit();
		}
	}
	if(aParam.constructor===Array){
		for(var i=0;i<aParam.length;i++){
			update_anatomography_point_record(aParam[i]);
		}
	}else{
		update_anatomography_point_record(aParam);
	}
};

var anatomography_point_grid = {
	ds : new Ext.data.SimpleStore({
		root   : 'records',
		fields : anatomography_point_grid_fields(),
		listeners : {
			"add" : function(store,records,index){
				var prm_record = ag_param_store.getAt(0);
				var bp3d_parts_store = ag_parts_gridpanel.getStore();
				for(var i=0;i<records.length;i++){
					var partslist = false;
					var zoom = false;
					var exclude = false;
					var color = null;
					var opacity = "1.0";
					var representation = "surface";
					var value = "";
					var point = false;
					var elem_type = records[i].get('elem_type');
					var regexp = new RegExp("^"+records[i].get('f_id')+"\$");
					var index = bp3d_parts_store.find('f_id',regexp);
					if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
					if(index>=0){
						partslist = true;
						var record = bp3d_parts_store.getAt(index);
						exclude = record.get('exclude');
						color = record.get('color');
						opacity = record.get('opacity');
						representation = record.get('representation');
						value = record.get('value');
						point = record.get('point');
					}else{
						if(!Ext.isEmpty(records[i].get('def_color'))) color = records[i].get('def_color');
					}
					records[i].beginEdit();
					records[i].set('partslist',partslist);
					records[i].set('zoom',zoom);
					records[i].set('exclude',exclude);
					records[i].set('color',color?color:'#'+ (elem_type=='bp3d_point'? prm_record.data.point_color_rgb:prm_record.data.color_rgb));
					records[i].set('opacity',opacity);
					records[i].set('representation',representation);
					records[i].set('value',value);
					records[i].set('conv_id',records[i].get('f_id'));
					records[i].set('point',point);
					records[i].commit(true);
					records[i].endEdit();
				}

				if(store.baseParams && store.baseParams.f_id){
					var index = store.find('f_id',new RegExp("^"+ store.baseParams.f_id +"\$"));
					if(index>=0) Ext.getCmp('anatomography-point-editorgrid-panel').getSelectionModel().selectRow(index);
				}
			},
			"beforeload" : function(store,options){
			},
			"clear" : function(store){
			},
			"datachanged" : function(store){
			},
			"load" : function(store,records,options){
			},
			"loadexception" : function(){
			},
			"metachange" : function(store,meta){
			},
			"remove" : function(store,record,index){
			},
			"update" : function(store,record,operation){
			},
			scope : this
		}

	}),
	cm : new Ext.grid.ColumnModel(anatomography_point_grid_cols())
};

var ag_comment_tabpanel = new Ext.TabPanel({
	id                : 'ag-comment-tabpanel',
	region            : 'center',
	deferredRender    : false,
	layoutOnTabChange : true,
	border            : false,
	listeners : {
		'tabchange' : function(tabpanel, panel) {
			var button = Ext.getCmp('anatomo_comment_pick_button');
			if(button){
				if(panel.id == 'anatomography-pin-grid-panel'){
					button.toggle(true);
				}else{
					button.toggle(false);
				}
			}
HTML
if($useClickPickTabSelect eq 'true'){
	print <<HTML;
			if(glb_point_pallet_index && panel.id == 'ag-parts-gridpanel'){
				if(panel.getStore().getCount()>glb_point_pallet_index){
					panel.getView().focusRow(glb_point_pallet_index);
				}
				glb_point_pallet_index = null;
			}
HTML
}
print <<HTML;
		},
		scope : this
	}
});

var ag_comment_panel = new Ext.Panel({
	id : 'anatomography_comment',
	region : 'east',
	split : true,
	autoScroll : false,
	width: 355,
	minWidth: 355,
	maxWidth : 500,
	layout : 'border',
	header        : controlPanelCollapsible,
	titleCollapse : controlPanelCollapsible,
	collapsible   : controlPanelCollapsible,
	items : [{
			region : 'north',
			id: 'ag-comment-panel-header',
			contentEl: 'ag-comment-panel-header-contentEl',
			border: false,
			height:46,
			bodyStyle: 'background:#dfe8f6;',
			listeners: {
				render: function(comp){
					Ext.getCmp('contents-tab-panel').on({
						tabchange: {
							fn: function(tabpanel,tab){
								if(tab.id != 'contents-tab-anatomography-panel') return;
								comp.setHeight(comp.initialConfig.height);
								comp.findParentByType('panel').doLayout();
							},
							buffer: 250
						}
					});
				}
			}
		},ag_comment_tabpanel
HTML
if($moveLicensesPanel ne 'true'){
	print <<HTML;
		,{
			hidden      : $moveLicensesPanel,
			id          : 'ag-licenses-panel',
			region      : 'south',
			height      : get_ag_lang('LICENSES_HEIGHT'),
			minHeight   : get_ag_lang('LICENSES_HEIGHT'),
			maxHeight   : get_ag_lang('LICENSES_HEIGHT'),
			html        : get_ag_lang('LICENSES'),
			border      : true,
			width       : get_ag_lang('LICENSES_WIDTH'),
			style       : 'font-size:11px;padding:4px 4px;',
			split       : false,
			collapsible : true,
			header      : true,
			title       : 'LICENSES',
			listeners : {
				'show' : function(panel){
					panel.doLayout();
				},
				'afterlayout' : function(panel,layout){
					afterLayout(panel);
				},
				scope:this
			}
		}
HTML
}elsif($makeExtraToolbar eq 'true'){
	print <<HTML;
		,{
			id          : 'ag-control-panel',
			region      : 'south',
//			height      : 118,
			height      : 52,
			border      : false,
			split       : false,
			collapsible : false,
			frame       : false,
			bodyStyle: 'background:#dfe8f6;',
//			html        : '<div class="ag-extra-pallet" style=""><table class="ag-extra-pallet"><tbody><tr><td class="ag-extra-pallet ag-extra-pallet-focus-centering"><a href="#"><img src="css/focusCentering100px.png" ext:qtip="'+get_ag_lang('TOOLTIP_FOCUS_CENTER')+'"></a></td><td class="ag-extra-pallet ag-extra-pallet-focus-zoom"><a href="#"><img src="css/focusZoom100px.png" ext:qtip="'+get_ag_lang('TOOLTIP_FOCUS')+'"></a></td><td class="ag-extra-pallet ag-extra-pallet-distinct-color"><a href="#" class="x-item-disabled"><img src="css/setDistinct64px.png" ext:qtip="Set distinct color to selected parts"></a></td><td class="ag-extra-pallet ag-extra-pallet-default-color"><a href="#" class="x-item-disabled"><img src="css/setDefault64px.png" ext:qtip="Set default color to selected parts"></a></td></tr></tbody></table></div><div class="ag-control-panel-table" style=""><table class="ag-control-panel-table"><tbody><tr><td class="ag-control-panel-td-print"><a href="#"><img width=48 height=48 src="css/ico_print_48.png?1" alt="Print" /></a></td><td class="ag-control-panel-td-link"><a href="#" id="ag-control-panel-a-link"><img width=48 height=48 src="css/ico_link_48.png?2" alt="Link"></a></td><td class="ag-control-panel-td-embed"><a href="#" id="ag-control-panel-a-embed"><img width=48 height=48 src="css/ico_embed_48.png?1" alt="Embed"></a></td><td class="ag-control-panel-td-license"><!--<a href="#" id="ag-control-panel-a-license"><img width=48 height=48 src="css/ico_license_48_c.png" alt="License" style=""></a>-->'+get_ag_lang('LICENSE_AG')+'</td><td class="ag-control-panel-td-tweet" style="display:none;"><a href="#"><img width=48 height=48 src="css/ico_twitter_48.png" alt="Tweet"></a></td></tr></tbody></table></div>',
			html        : '<div class="ag-extra-pallet" style=""><table class="ag-extra-pallet"><tbody><tr><td class="ag-extra-pallet ag-extra-pallet-focus-centering"><a href="#"><img src="css/focusCentering100px.png" ext:qtip="'+get_ag_lang('TOOLTIP_FOCUS_CENTER')+'"></a></td><td class="ag-extra-pallet ag-extra-pallet-focus-zoom"><a href="#"><img src="css/focusZoom100px.png" ext:qtip="'+get_ag_lang('TOOLTIP_FOCUS')+'"></a></td><td class="ag-extra-pallet ag-extra-pallet-distinct-color"><a href="#" class="x-item-disabled"><img src="css/setDistinct64px.png" ext:qtip="Set distinct color to selected parts"></a></td><td class="ag-extra-pallet ag-extra-pallet-default-color"><a href="#" class="x-item-disabled"><img src="css/setDefault64px.png" ext:qtip="Set default color to selected parts"></a></td></tr></tbody></table></div>',
			listeners : {
				'show' : function(panel){
					panel.doLayout();
				},
				'afterlayout' : function(panel,layout){
					afterLayout(panel);
				},
				render: function(comp){
					\$('td.ag-extra-pallet-focus-centering>a').live('click',function(){
						if(\$(this).hasClass('x-item-disabled')) return false;
						_dump("focus-centering");
						var btn = Ext.getCmp('pallet-focus-center-button');
						btn.fireEvent('click',btn);
						return false;
					});
					\$('td.ag-extra-pallet-focus-zoom>a').live('click',function(){
						if(\$(this).hasClass('x-item-disabled')) return false;
						_dump("focus-zoom");
						var btn = Ext.getCmp('pallet-focus-button');
						btn.fireEvent('click',btn);
						return false;
					});
					\$('td.ag-extra-pallet-distinct-color>a').live('click',function(){
						if(\$(this).hasClass('x-item-disabled')) return false;
						_dump("distinct-color");
						var btn = Ext.getCmp('ag-pallet-def-color-button');
						btn.fireEvent('click',btn);
						return false;
					});
					\$('td.ag-extra-pallet-default-color>a').live('click',function(){
						if(\$(this).hasClass('x-item-disabled')) return false;
						_dump("default-color");
						var btn = Ext.getCmp('ag-pallet-none-color-button');
						btn.fireEvent('click',btn);
						return false;
					});

					\$('td.ag-control-panel-td-print>a').live('click',function(){
						var form = Ext.getDom('ag-print-form');
						if(!form) return false;
						var target = Ext.id().replace(/\-/g,"_");

						var width = \$('img#ag_img').width();
						var height = \$('img#ag_img').height();
//						var print_win = window.open("", target, "titlebar=no,toolbar=yes,status=no,menubar=yes,dependent=yes,width="+width+",height="+height);


						var print_win = window.open("", target, "titlebar=no,toolbar=yes,status=no,menubar=yes,dependent=yes,width="+width+",height="+height);

						var jsonStr = glb_anatomo_image_still;
						try{
							jsonStr = ag_extensions.toJSON.URI2JSON(glb_anatomo_image_still,{
								toString:true,
								mapPin:false,
								callback:undefined
							});
							jsonStr = encodeURIComponent(jsonStr);
						}catch(e){jsonStr = glb_anatomo_image_still;}

						var printURL = getEditUrl() + "print.html?" + jsonStr;

						var transaction_id = Ext.Ajax.request({
							url     : 'get-convert-url.cgi',
							method  : 'POST',
							params  : Ext.urlEncode({url:printURL}),
							success : function(conn,response,options){
								try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
								if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}
								if(Ext.isEmpty(results.data)){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ no data ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}

								if(!Ext.isEmpty(results.data.url)){//shortURLに変換
									print_win.location.href = results.data.url;
								}else if(!Ext.isEmpty(results.data.expand)){//longURLに変換
									print_win.location.href = printURL;
								}
							},
							failure : function(conn,response,options){
								Ext.MessageBox.show({
									title   : window_title,
									msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
						return false;
					});
					\$('td.ag-control-panel-td-link>a').live('click',function(){
						anatomography_open_link_window();
						return false;
					});
					\$('td.ag-control-panel-td-embed>a').live('click',function(){
						anatomography_open_embed_window();
						return false;
					});
					\$('td.ag-control-panel-td-license>a').live('click',function(){
						var src = get_ag_lang('LICENSE_URL');
						window.open(src,"_blank","menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600");
						return false;
					});
					\$('td.ag-control-panel-td-tweet>a').live('click',function(){
						window.open('$urlTwitterTweetAG','_blank_ag','dependent=yes,width=800,height=600');
						return false;
					});

					Ext.getCmp('contents-tab-panel').on({
						tabchange: {
							fn: function(tabpanel,tab){
								if(tab.id != 'contents-tab-anatomography-panel') return;
								comp.setHeight(comp.initialConfig.height);
								comp.findParentByType('panel').doLayout();
							},
							buffer: 250
						}
					});

				},
				scope:this
			}
		}
HTML
}
print <<HTML;
	],
	listeners : {
		'show' : function(panel){
			panel.doLayout();
		},
		'render' : function(panel){
//			_dump("ag_comment_panel:render():controlPanelCollapsible=["+controlPanelCollapsible+"]["+window.screen.width+"]");
		},
		'afterlayout' : function(panel,layout){
			afterLayout(Ext.getCmp('ag-licenses-panel'));
			afterLayout(panel);
		},
		scope:this
	}
});
HTML
if($makeExtraToolbar eq 'true'){
	print <<HTML;

var anatomography_open_rotate_image_window = function(url_param){
	var urlStr = cgipath.animation + '?' + Ext.urlEncode(url_param);
	window.open(urlStr, "_blank", "titlebar=no,toolbar=yes,status=no,menubar=yes");
};


var anatomography_open_link_window = function(){
//	alert('link');

	var win = Ext.getCmp('ag-link-window');
	if(!Ext.isEmpty(win)){
		win.show(Ext.get('ag-control-panel-a-link'));
		return;
	}

	var anatomo_link_window = new Ext.Window({
		id          : 'ag-link-window',
		title       : 'Link',
		width       : 450,
		height      : 510,
		layout      : 'form',
		plain       : true,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'center',
		modal       : true,
		resizable   : false,
		contentEl   : 'ag-link-window-contentEl',
		closeAction : 'hide',
		buttons : [{
			text    : 'OK',
			handler : function(){
				Ext.getCmp('ag-link-window').hide(Ext.get('ag-control-panel-a-link'));
			}
		}],
		listeners : {
			beforeshow: function(comp){
				_dump("beforeshow():["+comp.id+"]");

				if(Ext.isEmpty(comp.loadMask) || typeof comp.loadMask == 'boolean') comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});

				Ext.getCmp('ag-link-window-page-reproduction-textfield').setValue('');

				var button = Ext.getCmp('ag-link-window-image-re-use-size-m-button');
				button.suspendEvents(false);
				button.setValue(true);
				button.resumeEvents();

				var button = Ext.getCmp('ag-link-window-image-re-use-size-s-button');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();

				var button = Ext.getCmp('ag-link-window-image-re-use-size-l-button');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();


				Ext.getCmp('ag-link-window-image-re-use-still-textfield').setValue('');
				Ext.getCmp('ag-link-window-image-re-use-rotate-textfield').setValue('');

//				Ext.getCmp('ag-link-window-embed-textarea').setValue('');

				var button = Ext.getCmp('ag-link-window-url-checkbox');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();

				var editURL = getEditUrl();

				comp.ag_link_url = comp.ag_link_url || {};
				comp.ag_link_url['ag-link-window-page-reproduction-textfield'] = comp.ag_link_url['ag-link-window-page-reproduction-textfield'] || {};

				if(comp.ag_link_url['ag-link-window-page-reproduction-textfield']['long'] != glb_anatomo_editor_url){
					comp.loadMask.show();

					//Page reproduction
					comp.ag_link_url['ag-link-window-page-reproduction-textfield']['long'] = glb_anatomo_editor_url;
					delete comp.ag_link_url['ag-link-window-page-reproduction-textfield']['short'];


					//Image re-use(Still)
					var ag_image_still_url = editURL + cgipath.image;
					var param = Ext.urlDecode(glb_anatomo_image_still,true);
					if(!Ext.isEmpty(param.orax)) delete param.orax;
					if(!Ext.isEmpty(param.oray)) delete param.oray;
					if(!Ext.isEmpty(param.oraz)) delete param.oraz;
					if(!Ext.isEmpty(param.orcx)) delete param.orcx;
					if(!Ext.isEmpty(param.orcy)) delete param.orcy;
					if(!Ext.isEmpty(param.orcz)) delete param.orcz;
					if(!Ext.isEmpty(param.ordg)) delete param.ordg;
					if(!Ext.isEmpty(param.autorotate)) delete param.autorotate;

					comp.ag_link_url['ag-link-window-image-re-use-still-textfield-s'] = comp.ag_link_url['ag-link-window-image-re-use-still-textfield-s'] || {};
					delete comp.ag_link_url['ag-link-window-image-re-use-still-textfield-s']['short'];

					comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m'] = comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m'] || {};
					delete comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m']['short'];

					comp.ag_link_url['ag-link-window-image-re-use-still-textfield-l'] = comp.ag_link_url['ag-link-window-image-re-use-still-textfield-l'] || {};
					delete comp.ag_link_url['ag-link-window-image-re-use-still-textfield-l']['short'];

					try{
						var jsonObj = ag_extensions.toJSON.URI2JSON(Ext.urlEncode(param),{
							toString:false,
							mapPin:false,
							callback:undefined
						});
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 120;
						comp.ag_link_url['ag-link-window-image-re-use-still-textfield-s']['long'] = ag_image_still_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 320;
						comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m']['long'] = ag_image_still_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 640;
						comp.ag_link_url['ag-link-window-image-re-use-still-textfield-l']['long'] = ag_image_still_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
					}catch(e){
						param.iw = param.ih = 120;
						comp.ag_link_url['ag-link-window-image-re-use-still-textfield-s']['long'] = ag_image_still_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 320;
						comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m']['long'] = ag_image_still_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 640;
						comp.ag_link_url['ag-link-window-image-re-use-still-textfield-l']['long'] = ag_image_still_url + '?' + Ext.urlEncode(param);
					}





					//Image re-use(Rotate)
					var ag_image_rotate_url = editURL + cgipath.animation;
					var param = Ext.urlDecode(glb_anatomo_image_rotate,true);
					if(!Ext.isEmpty(param.ordg)) param.ordg = 0;

					comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-s'] = comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-s'] || {};
					delete comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-s']['short'];

					comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m'] = comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m'] || {};
					delete comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m']['short'];

					comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-l'] = comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-l'] || {};
					delete comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-l']['short'];

					try{
						var jsonObj = ag_extensions.toJSON.URI2JSON(Ext.urlEncode(param),{
							toString:false,
							mapPin:false,
							callback:undefined
						});
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 120;
						comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-s']['long'] = ag_image_rotate_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 320;
						comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m']['long'] = ag_image_rotate_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 640;
						comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-l']['long'] = ag_image_rotate_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
					}catch(e){
						param.iw = param.ih = 120;
						comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-s']['long'] = ag_image_rotate_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 320;
						comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m']['long'] = ag_image_rotate_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 640;
						comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-l']['long'] = ag_image_rotate_url + '?' + Ext.urlEncode(param);
					}


					var window_title = comp.title;

					var urls = {};
					var hash_key = 'ag-link-window-page-reproduction-textfield';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};

					hash_key = 'ag-link-window-image-re-use-still-textfield-s';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};
					hash_key = 'ag-link-window-image-re-use-still-textfield-m';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};
					hash_key = 'ag-link-window-image-re-use-still-textfield-l';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};

					hash_key = 'ag-link-window-image-re-use-rotate-textfield-s';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};
					hash_key = 'ag-link-window-image-re-use-rotate-textfield-m';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};
					hash_key = 'ag-link-window-image-re-use-rotate-textfield-l';
					urls[hash_key] = {url:comp.ag_link_url[hash_key]['long']};


					Ext.Ajax.request({
						url     : 'get-convert-url.cgi',
						method  : 'POST',
						params  : Ext.urlEncode({urls:Ext.encode(urls)}),
						success : function(conn,response,options){
							try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
							if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
								var msg = get_ag_lang('CONVERT_URL_ERRMSG');
								if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
								for(var key in results){
									_dump("1:["+key+"]=["+results[key]+"]");
								}
								Ext.MessageBox.show({
									title   : window_title,
									msg     : msg,
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
								return;
							}
							for(var hash_key in results){
								if(hash_key == 'status_code') continue;
								var data = results[hash_key] && results[hash_key].result && results[hash_key].result.status_code==200 && results[hash_key].result.data ? results[hash_key].result.data : null;
								if(data && data.url) comp.ag_link_url[hash_key]['short'] = data.url;
							}
							Ext.getCmp('ag-link-window-page-reproduction-textfield').setValue(comp.ag_link_url['ag-link-window-page-reproduction-textfield']['short']);
							Ext.getCmp('ag-link-window-image-re-use-still-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m']['short']);
							Ext.getCmp('ag-link-window-image-re-use-rotate-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m']['short']);
							Ext.getCmp('ag-link-window').loadMask.hide();
						},
						failure : function(conn,response,options){
							Ext.getCmp('ag-link-window').loadMask.hide();
							Ext.MessageBox.show({
								title   : window_title,
								msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
						}
					});


				}else{
					comp.loadMask.hide();

					Ext.getCmp('ag-link-window-page-reproduction-textfield').setValue(comp.ag_link_url['ag-link-window-page-reproduction-textfield']['short']);
//					Ext.getCmp('ag-link-window-embed-textarea').setValue(comp.ag_link_url['ag-link-window-embed-textarea']['short']);

					Ext.getCmp('ag-link-window-image-re-use-still-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-still-textfield-m']['short']);
					Ext.getCmp('ag-link-window-image-re-use-rotate-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-m']['short']);

				}
			},
			show: function(comp){
				_dump("show():["+comp.id+"]");
			},
			render: function(win){
				_dump("render():["+win.id+"]");
				if(Ext.isEmpty(win.loadMask) || typeof win.loadMask == 'boolean') win.loadMask = new Ext.LoadMask(win.body,{removeMask:false});

					var change_link_value = function(){
						var size = 'm';
						if(Ext.getCmp('ag-link-window-image-re-use-size-s-button').getValue()){
							size = 's';
						}else if(Ext.getCmp('ag-link-window-image-re-use-size-l-button').getValue()){
							size = 'l';
						}
						var comp = Ext.getCmp('ag-link-window');
						if(Ext.getCmp('ag-link-window-url-checkbox').getValue()){
							Ext.getCmp('ag-link-window-page-reproduction-textfield').setValue(comp.ag_link_url['ag-link-window-page-reproduction-textfield']['long']);
//							Ext.getCmp('ag-link-window-embed-textarea').setValue(comp.ag_link_url['ag-link-window-embed-textarea']['long']);
							Ext.getCmp('ag-link-window-image-re-use-still-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-still-textfield-'+size]['long']);
							Ext.getCmp('ag-link-window-image-re-use-rotate-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-'+size]['long']);
						}else{
							Ext.getCmp('ag-link-window-page-reproduction-textfield').setValue(comp.ag_link_url['ag-link-window-page-reproduction-textfield']['short']);
//							Ext.getCmp('ag-link-window-embed-textarea').setValue(comp.ag_link_url['ag-link-window-embed-textarea']['short']);
							Ext.getCmp('ag-link-window-image-re-use-still-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-still-textfield-'+size]['short']);
							Ext.getCmp('ag-link-window-image-re-use-rotate-textfield').setValue(comp.ag_link_url['ag-link-window-image-re-use-rotate-textfield-'+size]['short']);
						}
					};
					var show_link_image = function(url){
						var size = 'width=320,height=320';
						if(Ext.getCmp('ag-link-window-image-re-use-size-s-button').getValue()){
							size = 'width=120,height=120';
						}else if(Ext.getCmp('ag-link-window-image-re-use-size-l-button').getValue()){
							size = 'width=640,height=640';
						}
						var win = window.open("", "_blank", "titlebar=no,toolbar=yes,status=no,menubar=yes,"+size);
						Ext.Ajax.request({
							url     : 'get-convert-url.cgi',
							method  : 'POST',
							params  : Ext.urlEncode({url:url}),
							success : function(conn,response,options){
								try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
								if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}
								if(Ext.isEmpty(results.data)){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ no data ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}
								if(!Ext.isEmpty(results.data.url)){//shortURLに変換
									win.location.href = results.data.url;
								}
								if(!Ext.isEmpty(results.data.expand)){//longURLに変換
									win.location.href = url;
								}
							},
							failure : function(conn,response,options){
								Ext.MessageBox.show({
									title   : window_title,
									msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
					};

					new Ext.form.Label({
						renderTo : 'ag-link-window-page-reproduction-label-renderTo',
						id       : 'ag-link-window-page-reproduction-label',
						html     : get_ag_lang('ANATOMO_EDITOR_LABEL')
					});

					new Ext.form.TextArea({
						renderTo : 'ag-link-window-page-reproduction-textfield-renderTo',
						id       : 'ag-link-window-page-reproduction-textfield',
						style    : 'width:100%;',
						height   : 22,
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							beforeshow: function(comp){
								_dump("beforeshow():["+comp.id+"]");
							},
							show: function(comp){
								_dump("show():["+comp.id+"]");
							},
							render: function(comp){
								_dump("render():["+comp.id+"]");
								comp.setValue(glb_anatomo_editor_url);
							}
						}
					});


					new Ext.form.Label({
						renderTo : 'ag-link-window-image-re-use-label-renderTo',
						id       : 'ag-link-window-image-re-use-label',
						html     : get_ag_lang('ANATOMO_IMAGE_LABEL')
					});

					new Ext.form.Label({
						renderTo : 'ag-link-window-image-re-use-size-label-renderTo',
						id       : 'ag-link-window-image-re-use-size-label',
						html     : 'Size&nbsp;'
					});
					new Ext.form.Radio({
						renderTo : 'ag-link-window-image-re-use-size-s-button-renderTo',
						id       : 'ag-link-window-image-re-use-size-s-button',
						name     : 'ag-link-window-image-re-use-size-radio',
						boxLabel : 'S',
						value    : 's',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								if(!checked) return;
								change_link_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'ag-link-window-image-re-use-size-m-button-renderTo',
						id       : 'ag-link-window-image-re-use-size-m-button',
						name     : 'ag-link-window-image-re-use-size-radio',
						checked  : true,
						boxLabel : 'M',
						value    : 'm',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								if(!checked) return;
								change_link_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'ag-link-window-image-re-use-size-l-button-renderTo',
						id       : 'ag-link-window-image-re-use-size-l-button',
						name     : 'ag-link-window-image-re-use-size-radio',
						boxLabel : 'L',
						value    : 'l',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								if(!checked) return;
								change_link_value();
							}
						}
					});

					new Ext.form.Label({
						renderTo : 'ag-link-window-image-re-use-still-label-renderTo',
						id       : 'ag-link-window-image-re-use-still-label',
						html     : 'Still'
					});
					new Ext.form.TextArea({
						renderTo : 'ag-link-window-image-re-use-still-textfield-renderTo',
						id       : 'ag-link-window-image-re-use-still-textfield',
						style    : 'width:100%;',
						height   : 22,
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							render: function(comp){
								_dump("render():["+comp.id+"]");
							}
						}
					});
					new Ext.Button({
						renderTo : 'ag-link-window-image-re-use-still-button-renderTo',
						id       : 'ag-link-window-image-re-use-still-button',
						text    : 'show image',
						listeners : {
							click: function(comp){
								_dump("click():["+comp.id+"]");
								show_link_image(Ext.getCmp('ag-link-window-image-re-use-still-textfield').getValue());
							}
						}
					});

					new Ext.form.Label({
						renderTo : 'ag-link-window-image-re-use-rotate-label-renderTo',
						id       : 'ag-link-window-image-re-use-rotate-label',
						html     : 'Rotate'
					});
					new Ext.form.TextArea({
						renderTo : 'ag-link-window-image-re-use-rotate-textfield-renderTo',
						id       : 'ag-link-window-image-re-use-rotate-textfield',
						style    : 'width:100%;',
						height   : 22,
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							render: function(comp){
								_dump("render():["+comp.id+"]");
							}
						}
					});
					new Ext.Button({
						renderTo : 'ag-link-window-image-re-use-rotate-button-renderTo',
						id       : 'ag-link-window-image-re-use-rotate-button',
						text    : 'show image',
						listeners : {
							click: function(comp){
								_dump("click():["+comp.id+"]");
								show_link_image(Ext.getCmp('ag-link-window-image-re-use-rotate-textfield').getValue());
							}
						}
					});

//					new Ext.form.Label({
//						renderTo : 'ag-link-window-embed-label-renderTo',
//						id       : 'ag-link-window-embed-label',
//						html     : get_ag_lang('ANATOMO_EMBEDDED_LABEL')
//					});
//					new Ext.form.TextArea({
//						renderTo : 'ag-link-window-embed-textarea-renderTo',
//						id       : 'ag-link-window-embed-textarea',
//						style    : 'width:100%;',
//						selectOnFocus : true,
//						readOnly      : true,
//						listeners : {
//							render: function(comp){
//								_dump("render():["+comp.id+"]");
//							}
//						}
//					});

					new Ext.form.Checkbox({
						renderTo : 'ag-link-window-url-checkbox-renderTo',
						id       : 'ag-link-window-url-checkbox',
						style    : 'width:100%;',
						boxLabel : 'Elongate URL to original configuration for parsing.',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								change_link_value();
							}
						}
					});

					var text_value = URI2Text(glb_anatomo_editor_url);

					new Ext.form.FieldSet({
						renderTo: 'ag-link-window-url-table-fieldset-renderTo',
						id      : 'ag-link-window-url-table-fieldset',
						title: 'Table',
						autoHeight: true,
						readOnly: true,
						layout: 'fit',
						items: [{
							xtype: 'textarea',
							id: 'ag-link-window-url-table-textarea',
							style: 'font-family:Courier;monospace;',
							readOnly: true,
							selectOnFocus: true,
							width: 402,
							height: 220,
							value: text_value
						}]
					});
			}
		}
	});
	anatomo_link_window.show(Ext.get('ag-control-panel-a-link'));
};

var anatomography_open_embed_window = function(){
//	alert('embed');

	var win = Ext.getCmp('ag-embed-window');
	if(!Ext.isEmpty(win)){
		win.show(Ext.get('ag-control-panel-a-embed'));
		return;
	}

	var anatomo_embed_window = new Ext.Window({
		id          : 'ag-embed-window',
		title       : 'Embed',
		width       : 450,
		height      : 344,
		layout      : 'form',
		plain       : true,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'center',
		modal       : true,
		resizable   : false,
		contentEl   : 'ag-embed-window-contentEl',
		closeAction : 'hide',
		buttons : [{
			text    : 'OK',
			handler : function(){
				Ext.getCmp('ag-embed-window').hide(Ext.get('ag-control-panel-a-embed'));
			}
		}],
		listeners : {
			beforeshow: function(comp){
				_dump("beforeshow():["+comp.id+"]");

				if(Ext.isEmpty(comp.loadMask) || typeof comp.loadMask == 'boolean') comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});

				Ext.getCmp('ag-embed-window-page-reproduction-textfield').setValue('');

				var button = Ext.getCmp('ag-embed-window-image-re-use-size-m-button');
				button.suspendEvents(false);
				button.setValue(true);
				button.resumeEvents();

				var button = Ext.getCmp('ag-embed-window-image-re-use-size-s-button');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();

				var button = Ext.getCmp('ag-embed-window-image-re-use-size-l-button');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();


				Ext.getCmp('ag-embed-window-image-re-use-still-textfield').setValue('');
				Ext.getCmp('ag-embed-window-image-re-use-rotate-textfield').setValue('');

				Ext.getCmp('ag-embed-window-embed-textarea').setValue('');

				var button = Ext.getCmp('ag-embed-window-url-checkbox');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();

				var editURL = getEditUrl();

				comp.ag_embed_url = comp.ag_embed_url || {};
				comp.ag_embed_url['ag-embed-window-page-reproduction-textfield'] = comp.ag_embed_url['ag-embed-window-page-reproduction-textfield'] || {};

				if(comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['long'] != glb_anatomo_editor_url){
					comp.loadMask.show();

					//Page reproduction
					comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['long'] = glb_anatomo_editor_url;
					delete comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['short'];

					//Embed Manipulabel Image
					comp.ag_embed_url['ag-embed-window-embed-textarea'] = comp.ag_embed_url['ag-embed-window-embed-textarea'] || {};
//					comp.ag_embed_url['ag-embed-window-embed-textarea']['long'] = getEmbedIFrameUrl(glb_anatomo_editor_url);
					comp.ag_embed_url['ag-embed-window-embed-textarea']['long'] = glb_anatomo_editor_url;
					delete comp.ag_embed_url['ag-embed-window-embed-textarea']['short'];


					//Image re-use(Still)
					var ag_image_still_url = editURL + cgipath.image;
					var param = Ext.urlDecode(glb_anatomo_image_still,true);
					if(!Ext.isEmpty(param.orax)) delete param.orax;
					if(!Ext.isEmpty(param.oray)) delete param.oray;
					if(!Ext.isEmpty(param.oraz)) delete param.oraz;
					if(!Ext.isEmpty(param.orcx)) delete param.orcx;
					if(!Ext.isEmpty(param.orcy)) delete param.orcy;
					if(!Ext.isEmpty(param.orcz)) delete param.orcz;
					if(!Ext.isEmpty(param.ordg)) delete param.ordg;
					if(!Ext.isEmpty(param.autorotate)) delete param.autorotate;

					comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-s'] = comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-s'] || {};
					delete comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-s']['short'];

					comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m'] = comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m'] || {};
					delete comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m']['short'];

					comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-l'] = comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-l'] || {};
					delete comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-l']['short'];

					try{
						var jsonObj = ag_extensions.toJSON.URI2JSON(Ext.urlEncode(param),{
							toString:false,
							mapPin:false,
							callback:undefined
						});
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 120;
						comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-s']['long'] = ag_image_still_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 320;
						comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m']['long'] = ag_image_still_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 640;
						comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-l']['long'] = ag_image_still_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
					}catch(e){
						param.iw = param.ih = 120;
						comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-s']['long'] = ag_image_still_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 320;
						comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m']['long'] = ag_image_still_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 640;
						comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-l']['long'] = ag_image_still_url + '?' + Ext.urlEncode(param);
					}




					//Image re-use(Rotate)
					var ag_image_rotate_url = editURL + cgipath.animation;
					var param = Ext.urlDecode(glb_anatomo_image_rotate,true);
					if(!Ext.isEmpty(param.ordg)) param.ordg = 0;

					comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-s'] = comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-s'] || {};
					delete comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-s']['short'];

					comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m'] = comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m'] || {};
					delete comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m']['short'];

					comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-l'] = comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-l'] || {};
					delete comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-l']['short'];

					try{
						var jsonObj = ag_extensions.toJSON.URI2JSON(Ext.urlEncode(param),{
							toString:false,
							mapPin:false,
							callback:undefined
						});
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 120;
						comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-s']['long'] = ag_image_rotate_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 320;
						comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m']['long'] = ag_image_rotate_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
						jsonObj.Window.ImageWidth = jsonObj.Window.ImageHeight = 640;
						comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-l']['long'] = ag_image_rotate_url + '?' + encodeURIComponent(Ext.util.JSON.encode(jsonObj));
					}catch(e){
						param.iw = param.ih = 120;
						comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-s']['long'] = ag_image_rotate_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 320;
						comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m']['long'] = ag_image_rotate_url + '?' + Ext.urlEncode(param);
						param.iw = param.ih = 640;
						comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-l']['long'] = ag_image_rotate_url + '?' + Ext.urlEncode(param);
					}


					var window_title = comp.title;

					var urls = {};
					var hash_key = 'ag-embed-window-page-reproduction-textfield';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};

					hash_key = 'ag-embed-window-embed-textarea';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};

					hash_key = 'ag-embed-window-image-re-use-still-textfield-s';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};
					hash_key = 'ag-embed-window-image-re-use-still-textfield-m';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};
					hash_key = 'ag-embed-window-image-re-use-still-textfield-l';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};

					hash_key = 'ag-embed-window-image-re-use-rotate-textfield-s';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};
					hash_key = 'ag-embed-window-image-re-use-rotate-textfield-m';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};
					hash_key = 'ag-embed-window-image-re-use-rotate-textfield-l';
					urls[hash_key] = {url:comp.ag_embed_url[hash_key]['long']};

					Ext.Ajax.request({
						url     : 'get-convert-url.cgi',
						method  : 'POST',
						params  : Ext.urlEncode({urls:Ext.encode(urls)}),
						success : function(conn,response,options){
							try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
							if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
								var msg = get_ag_lang('CONVERT_URL_ERRMSG');
								if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
								for(var key in results){
									_dump("1:["+key+"]=["+results[key]+"]");
								}
								Ext.MessageBox.show({
									title   : window_title,
									msg     : msg,
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
								return;
							}
							for(var hash_key in results){
								if(hash_key == 'status_code') continue;
								var data = results[hash_key] && results[hash_key].result && results[hash_key].result.status_code==200 && results[hash_key].result.data ? results[hash_key].result.data : null;
								if(data && data.url) comp.ag_embed_url[hash_key]['short'] = data.url;
							}
							Ext.getCmp('ag-embed-window-page-reproduction-textfield').setValue(getEmbedAUrl(comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['short']));
							Ext.getCmp('ag-embed-window-embed-textarea').setValue(getEmbedIFrameUrl(comp.ag_embed_url['ag-embed-window-embed-textarea']['short']));
							Ext.getCmp('ag-embed-window-image-re-use-still-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m']['short']));
							Ext.getCmp('ag-embed-window-image-re-use-rotate-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m']['short']));

							comp.loadMask.hide();
						},
						failure : function(conn,response,options){
							comp.loadMask.hide();
							Ext.MessageBox.show({
								title   : window_title,
								msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
						}
					});

				}else{
					comp.loadMask.hide();

					Ext.getCmp('ag-embed-window-page-reproduction-textfield').setValue(getEmbedAUrl(comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['short']));
					Ext.getCmp('ag-embed-window-embed-textarea').setValue(getEmbedIFrameUrl(comp.ag_embed_url['ag-embed-window-embed-textarea']['short']));

					Ext.getCmp('ag-embed-window-image-re-use-still-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-m']['short']));
					Ext.getCmp('ag-embed-window-image-re-use-rotate-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-m']['short']));

				}
			},
			show: function(comp){
				_dump("show():["+comp.id+"]");
			},
			render: function(win){
				_dump("render():["+win.id+"]");
				if(Ext.isEmpty(win.loadMask) || typeof win.loadMask == 'boolean') win.loadMask = new Ext.LoadMask(win.body,{removeMask:false});

					var change_embed_value = function(){
						var size = 'm';
						if(Ext.getCmp('ag-embed-window-image-re-use-size-s-button').getValue()){
							size = 's';
						}else if(Ext.getCmp('ag-embed-window-image-re-use-size-l-button').getValue()){
							size = 'l';
						}
						var comp = Ext.getCmp('ag-embed-window');
						if(Ext.getCmp('ag-embed-window-url-checkbox').getValue()){
							Ext.getCmp('ag-embed-window-page-reproduction-textfield').setValue(getEmbedAUrl(comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['long']));
							Ext.getCmp('ag-embed-window-embed-textarea').setValue(getEmbedIFrameUrl(comp.ag_embed_url['ag-embed-window-embed-textarea']['long']));
							Ext.getCmp('ag-embed-window-image-re-use-still-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-'+size]['long']));
							Ext.getCmp('ag-embed-window-image-re-use-rotate-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-'+size]['long']));
						}else{
							Ext.getCmp('ag-embed-window-page-reproduction-textfield').setValue(getEmbedAUrl(comp.ag_embed_url['ag-embed-window-page-reproduction-textfield']['short']));
							Ext.getCmp('ag-embed-window-embed-textarea').setValue(getEmbedIFrameUrl(comp.ag_embed_url['ag-embed-window-embed-textarea']['short']));
							Ext.getCmp('ag-embed-window-image-re-use-still-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-'+size]['short']));
							Ext.getCmp('ag-embed-window-image-re-use-rotate-textfield').setValue(getEmbedImgUrl(comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-'+size]['short']));
						}
					};
					var show_embed_image = function(url){
						var size = 'width=320,height=320';
						if(Ext.getCmp('ag-embed-window-image-re-use-size-s-button').getValue()){
							size = 'width=120,height=120';
						}else if(Ext.getCmp('ag-embed-window-image-re-use-size-l-button').getValue()){
							size = 'width=640,height=640';
						}
						var win = window.open("", "_blank", "titlebar=no,toolbar=yes,status=no,menubar=yes,"+size);
						Ext.Ajax.request({
							url     : 'get-convert-url.cgi',
							method  : 'POST',
							params  : Ext.urlEncode({url:url}),
							success : function(conn,response,options){
								try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
								if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}
								if(Ext.isEmpty(results.data)){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ no data ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}
								if(!Ext.isEmpty(results.data.url)){//shortURLに変換
									win.location.href = results.data.url;
								}
								if(!Ext.isEmpty(results.data.expand)){//longURLに変換
									win.location.href = url;
								}
							},
							failure : function(conn,response,options){
								Ext.MessageBox.show({
									title   : window_title,
									msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
					};

					new Ext.form.Label({
						renderTo : 'ag-embed-window-page-reproduction-label-renderTo',
						id       : 'ag-embed-window-page-reproduction-label',
						html     : get_ag_lang('ANATOMO_EDITOR_LABEL_A')
					});

					new Ext.form.TextArea({
						renderTo : 'ag-embed-window-page-reproduction-textfield-renderTo',
						id       : 'ag-embed-window-page-reproduction-textfield',
						style    : 'width:100%;',
						height   : 22,
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							beforeshow: function(comp){
								_dump("beforeshow():["+comp.id+"]");
							},
							show: function(comp){
								_dump("show():["+comp.id+"]");
							},
							render: function(comp){
								_dump("render():["+comp.id+"]");
								comp.setValue(glb_anatomo_editor_url);
							}
						}
					});


					new Ext.form.Label({
						renderTo : 'ag-embed-window-image-re-use-label-renderTo',
						id       : 'ag-embed-window-image-re-use-label',
						html     : get_ag_lang('ANATOMO_IMAGE_LABEL_IMG')
					});

					new Ext.form.Label({
						renderTo : 'ag-embed-window-image-re-use-size-label-renderTo',
						id       : 'ag-embed-window-image-re-use-size-label',
						html     : 'Size&nbsp;'
					});
					new Ext.form.Radio({
						renderTo : 'ag-embed-window-image-re-use-size-s-button-renderTo',
						id       : 'ag-embed-window-image-re-use-size-s-button',
						name     : 'ag-embed-window-image-re-use-size-radio',
						boxLabel : 'S',
						value    : 's',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								if(!checked) return;
								change_embed_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'ag-embed-window-image-re-use-size-m-button-renderTo',
						id       : 'ag-embed-window-image-re-use-size-m-button',
						name     : 'ag-embed-window-image-re-use-size-radio',
						checked  : true,
						boxLabel : 'M',
						value    : 'm',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								if(!checked) return;
								change_embed_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'ag-embed-window-image-re-use-size-l-button-renderTo',
						id       : 'ag-embed-window-image-re-use-size-l-button',
						name     : 'ag-embed-window-image-re-use-size-radio',
						boxLabel : 'L',
						value    : 'l',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								if(!checked) return;
								change_embed_value();
							}
						}
					});

					new Ext.form.Label({
						renderTo : 'ag-embed-window-image-re-use-still-label-renderTo',
						id       : 'ag-embed-window-image-re-use-still-label',
						html     : 'Still'
					});
					new Ext.form.TextArea({
						renderTo : 'ag-embed-window-image-re-use-still-textfield-renderTo',
						id       : 'ag-embed-window-image-re-use-still-textfield',
						style    : 'width:100%;',
						height   : 22,
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							render: function(comp){
								_dump("render():["+comp.id+"]");
							}
						}
					});
					new Ext.Button({
						renderTo : 'ag-embed-window-image-re-use-still-button-renderTo',
						id       : 'ag-embed-window-image-re-use-still-button',
						text    : 'show image',
						listeners : {
							click: function(comp){
								_dump("click():["+comp.id+"]");

								var size = 'm';
								if(Ext.getCmp('ag-embed-window-image-re-use-size-s-button').getValue()){
									size = 's';
								}else if(Ext.getCmp('ag-embed-window-image-re-use-size-l-button').getValue()){
									size = 'l';
								}
								var url;
								var comp = Ext.getCmp('ag-embed-window');
								if(Ext.getCmp('ag-embed-window-url-checkbox').getValue()){
									url = comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-'+size]['long'];
								}else{
									url = comp.ag_embed_url['ag-embed-window-image-re-use-still-textfield-'+size]['short'];
								}
								show_embed_image(url);

							}
						}
					});

					new Ext.form.Label({
						renderTo : 'ag-embed-window-image-re-use-rotate-label-renderTo',
						id       : 'ag-embed-window-image-re-use-rotate-label',
						html     : 'Rotate'
					});
					new Ext.form.TextArea({
						renderTo : 'ag-embed-window-image-re-use-rotate-textfield-renderTo',
						id       : 'ag-embed-window-image-re-use-rotate-textfield',
						style    : 'width:100%;',
						height   : 22,
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							render: function(comp){
								_dump("render():["+comp.id+"]");
							}
						}
					});
					new Ext.Button({
						renderTo : 'ag-embed-window-image-re-use-rotate-button-renderTo',
						id       : 'ag-embed-window-image-re-use-rotate-button',
						text    : 'show image',
						listeners : {
							click: function(comp){

								var size = 'm';
								if(Ext.getCmp('ag-embed-window-image-re-use-size-s-button').getValue()){
									size = 's';
								}else if(Ext.getCmp('ag-embed-window-image-re-use-size-l-button').getValue()){
									size = 'l';
								}
								var url;
								var comp = Ext.getCmp('ag-embed-window');
								if(Ext.getCmp('ag-embed-window-url-checkbox').getValue()){
									url = comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-'+size]['long'];
								}else{
									url = comp.ag_embed_url['ag-embed-window-image-re-use-rotate-textfield-'+size]['short'];
								}
								show_embed_image(url);

							}
						}
					});

					new Ext.form.Label({
						renderTo : 'ag-embed-window-embed-label-renderTo',
						id       : 'ag-embed-window-embed-label',
						html     : get_ag_lang('ANATOMO_EMBEDDED_LABEL')
					});
					new Ext.form.TextArea({
						renderTo : 'ag-embed-window-embed-textarea-renderTo',
						id       : 'ag-embed-window-embed-textarea',
						style    : 'width:100%;',
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							render: function(comp){
								_dump("render():["+comp.id+"]");
							}
						}
					});

					new Ext.form.Checkbox({
						renderTo : 'ag-embed-window-url-checkbox-renderTo',
						id       : 'ag-embed-window-url-checkbox',
						style    : 'width:100%;',
						boxLabel : 'Elongate URL to original configuration for parsing.',
						listeners : {
							check: function(checkbox,checked){
								_dump("check():["+checkbox.id+"]["+checked+"]");
								change_embed_value();
							}
						}
					});

			}
		}
	});
	anatomo_embed_window.show(Ext.get('ag-control-panel-a-embed'));
};

HTML
}
print <<HTML;
var anatomography_panel_toolbar = new Ext.Toolbar([
	{
		id    : 'anatomo_anatomogram_label',
		xtype : 'tbtext',
		text  : get_ag_lang('ANATOMO_ANATOMOGRAM_LABEL')
	},
	' ',
	'-',
	{
		id    : 'anatomo_editor_label',
		xtype : 'tbtext',
		text  : get_ag_lang('ANATOMO_EDITOR_LABEL')+' : '
	},
	{
		xtype: 'textfield',
		id: 'anatomo_editor_url',
		readOnly:true,
		width: 100
	},
	' ',
	'-',
	{
		id    : 'anatomo_image_label',
		xtype : 'tbtext',
		text  : get_ag_lang('ANATOMO_IMAGE_LABEL')
	},
	{
		xtype: 'textfield',
		id: 'anatomo_image_url',
		readOnly:true,
		width: 100
	}
//	,'->',
//	{
//		id : 'prm2_check',
//		xtype: 'checkbox'
//	}
//	{
//		xtype: 'hidden',
//		id: 'cameraX',
//		width: 10,
//		value : 2.7979888916016167
//	},
//	{
//		xtype: 'hidden',
//		id: 'cameraY',
//		width: 10,
//		value : -998.4280435445771
//	},
//	{
//		xtype: 'hidden',
//		id: 'cameraZ',
//		width: 10,
//		value : 809.7306805551052
//	},
//	{
//		xtype: 'hidden',
//		id: 'targetX',
//		width: 10,
//		value : 2.7979888916016167
//	},
//	{
//		xtype: 'hidden',
//		id: 'targetY',
//		width: 10,
//		value : -110.37168800830841
//	},
//	{
//		xtype: 'hidden',
//		id: 'targetZ',
//		width: 10,
//		value : 809.7306805551052
//	}
]);




var prm_record = ag_param_store.getAt(0);

function onload_ag_img(){
	var elem = Ext.get("ag_img");
	elem.un("load", onload_ag_img);

	var checked = false;
	try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
	if(!checked) return;

	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}

	var fix = Ext.getCmp('anatomo-clip-fix-check');
	var reverse = Ext.getCmp('anatomo-clip-reverse-check');
	var clipImgDiv = Ext.get('clipImgDiv');

	var prm_record = ag_param_store.getAt(0);
	prm_record.beginEdit();
	prm_record.set('clip_type', 'D');
	prm_record.set('clip_depth', 0);
	prm_record.endEdit();
	prm_record.commit();

	var param = Ext.urlDecode(makeAnatomoPrm(),true);
	var urlStr;

	if(clip == 'FREE'){
		if(clipImgDiv) clipImgDiv.hide();
		if(fix) fix.show();
//		urlStr = cgipath.clip+'?' + Ext.urlEncode(param);
		urlStr = cgipath.clip;
	}else{
		if(clipImgDiv) clipImgDiv.show();
		if(fix) fix.hide();
		if(reverse) reverse.enable();
		if(glb_rotateV == 90){
			param.cameraMode = "top";
		}else if(glb_rotateV == 270){
			param.cameraMode = "bottom";
		}else if(glb_rotateH == 90){
			param.cameraMode = "right";
		}else if(glb_rotateH == 180){
			param.cameraMode = "back";
		}else if(glb_rotateH == 270){
			param.cameraMode = "left";
		}else{
			param.cameraMode = "front";
		}
//		urlStr = cgipath.focusClip+'?' + Ext.urlEncode(param);
		urlStr = cgipath.focusClip;
	}

	var jsonStr = null;
	try{
		jsonStr = ag_extensions.toJSON.URI2JSON(param,{
			toString:true,
			mapPin:false,
			callback:undefined
		});
	}catch(e){jsonStr = null;}
	if(Ext.isEmpty(jsonStr)) jsonStr = Ext.urlEncode(param);

	Ext.Ajax.request({
		url     : urlStr,
		method  : 'POST',
//		params  : Ext.urlEncode(param),
		params  : jsonStr,
		success : function (response, options) {
			var targetXYZYRange = Ext.util.JSON.decode(response.responseText);
			updateRotateImg();

			var prm_record = ag_param_store.getAt(0);
			prm_record.beginEdit();

			prm_record.set('clip_paramA', parseFloat(targetXYZYRange.Clip.ClipPlaneA));
			prm_record.set('clip_paramB', parseFloat(targetXYZYRange.Clip.ClipPlaneB));
			prm_record.set('clip_paramC', parseFloat(targetXYZYRange.Clip.ClipPlaneC));
			prm_record.set('clip_paramD', parseFloat(targetXYZYRange.Clip.ClipPlaneD));
			if(clip == "FB" || clip == "TB" || clip == 'RL'){
				prm_record.set('clip_depth', parseFloat(targetXYZYRange.Clip.ClipPlaneD));
				prm_record.set('clip_type', 'P');
			}else if(clip == "FREE"){
				if(fix.getValue()){
					prm_record.set('clip_type', 'P');
					prm_record.set('clip_depth', Ext.getCmp('anatomo-clip-slider').getValue());
				}
			}

//切断面切り替え時にズームが変化しないようにする為
//			prm_record.set('zoom', sliderValue / 5);

			prm_record.endEdit();
			prm_record.commit();

			var clip_depth = prm_record.data.clip_depth;
			if(clip == 'FB'){
				clip_depth *= prm_record.data.clip_paramB;
			}else if(clip == 'RL'){
				clip_depth *= prm_record.data.clip_paramA;
			}else if(clip == 'TB'){
				clip_depth *= prm_record.data.clip_paramC;
			}

			var minValue;
			var maxValue;
			var clip_slider = Ext.getCmp('anatomo-clip-slider');
			var clip_text = Ext.getCmp('anatomo-clip-value-text');
			if(clip_slider && clip_text){
				if(clip == "FREE"){
//					minValue = Math.abs(Math.floor(prm_record.get('clip_paramD')))*-1;
//					maxValue = Math.abs(Math.ceil(prm_record.get('clip_paramD')));
					minValue = -1000;
					maxValue = 1000;
				}else if(clip == "FB"){
					minValue = Math.floor(parseFloat(targetXYZYRange.BoundingBox.YMin));
					maxValue = Math.ceil(parseFloat(targetXYZYRange.BoundingBox.YMax));
				}else if(clip == "RL"){
					minValue = Math.floor(parseFloat(targetXYZYRange.BoundingBox.XMin));
					maxValue = Math.ceil(parseFloat(targetXYZYRange.BoundingBox.XMax));
				}else if(clip == "TB"){
					minValue = Math.floor(parseFloat(targetXYZYRange.BoundingBox.ZMin));
					maxValue = Math.ceil(parseFloat(targetXYZYRange.BoundingBox.ZMax));
				}else{
					minValue = -350;
					maxValue = 1800;
				}
				clip_slider.minValue = minValue;
				clip_slider.maxValue = maxValue;
				clip_text.minValue = minValue;
				clip_text.maxValue = maxValue;
			}

//_dump("minValue=["+minValue+"],maxValue=["+maxValue+"]");
//_dump("clip_slider.minValue=["+clip_slider.minValue+"],clip_slider.maxValue=["+clip_slider.maxValue+"]");
//_dump("clip_depth=["+clip+"]["+clip_depth+"]");
//_dump("YRangeFromServer=["+YRangeFromServer+"]");

			if(clip_slider){
				var clip_slider_value;
				if(clip == "FB" || clip == "TB"){
					clip_slider.setValue(clip_depth*-1);
				}else if(clip == 'RL'){
					clip_slider.setValue(clip_depth);
				}else if(clip == 'FREE'){
					clip_slider.setValue(prm_record.get('clip_depth'));
				}
				clip_slider.syncThumb();
			}

			stopUpdateAnatomo();
			_updateAnatomo();
		}
	});
}

anatomography_control_panel = new Ext.Panel({
	title  : 'Controls',
	header : false,
	id     : 'control-tab-anatomography-panel',
	border : false
});

function updateClipPlane() {

	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
	if(!clip) return;

//	if(clip == 'TB'){
		updateAnatomo();
		return;
//	}

	// Store Camera, Target, UpVector
	var cameraPosX = m_ag.cameraPos.x;
	var cameraPosY = m_ag.cameraPos.y;
	var cameraPosZ = m_ag.cameraPos.z;
	var targetPosX = m_ag.targetPos.x;
	var targetPosY = m_ag.targetPos.y;
	var targetPosZ = m_ag.targetPos.z;
	var upVecX = m_ag.upVec.x;
	var upVecY = m_ag.upVec.y;
	var upVecZ = m_ag.upVec.z;

	var prm_record =ag_param_store.getAt(0);
	m_ag.cameraPos.x = prm_record.data.clipped_cameraX;
	m_ag.cameraPos.y = prm_record.data.clipped_cameraY;
	m_ag.cameraPos.z = prm_record.data.clipped_cameraZ;
	m_ag.targetPos.x = prm_record.data.clipped_targetX;
	m_ag.targetPos.y = prm_record.data.clipped_targetY;
	m_ag.targetPos.z = prm_record.data.clipped_targetZ;
	m_ag.upVec.x = prm_record.data.clipped_upVecX;
	m_ag.upVec.y = prm_record.data.clipped_upVecY;
	m_ag.upVec.z = prm_record.data.clipped_upVecZ;
	prm_record.set('clip_type', 'D');

//	var urlStr = cgipath.clip+'?' + makeAnatomoPrm();
	var urlStr = cgipath.clip;
	var params = makeAnatomoPrm();
	m_ag.cameraPos.x = cameraPosX;
	m_ag.cameraPos.y = cameraPosY;
	m_ag.cameraPos.z = cameraPosZ;
	m_ag.targetPos.x = targetPosX;
	m_ag.targetPos.y = targetPosY;
	m_ag.targetPos.z = targetPosZ;
	m_ag.upVec.x = upVecX;
	m_ag.upVec.y = upVecY;
	m_ag.upVec.z = upVecZ;
	Ext.Ajax.request({
		url: urlStr,
		method  : 'POST',
		params  : params,
		success: function (response, options) {
//			var clipAry = response.responseText.split("\\t");
//			prm_record.set('clip_paramA', parseFloat(clipAry[0]));
//			prm_record.set('clip_paramB', parseFloat(clipAry[1]));
//			prm_record.set('clip_paramC', parseFloat(clipAry[2]));
//			prm_record.set('clip_paramD', parseFloat(clipAry[3]));
//			prm_record.set('clip_type', 'P');

			var clipAry = Ext.util.JSON.decode(response.responseText);
			prm_record.set('clip_paramA', parseFloat(clipAry.clip0A));
			prm_record.set('clip_paramB', parseFloat(clipAry.clip0B));
			prm_record.set('clip_paramC', parseFloat(clipAry.clip0C));
			prm_record.set('clip_paramD', parseFloat(clipAry.clip0D));
			prm_record.set('clip_type', 'P');

			updateAnatomo();
		},
		failure : function (response, options) {
		}
	});
}

function updateRotateImg() {
	var img = document.getElementById("rotateImg");
	if(!img) return;

	var rotateH = getRotateHorizontalValue();
	rotateH = Math.round(rotateH/15) * 15;
	if(rotateH>=360) rotateH -= 360;
	rotateH = new String(rotateH);
	while (rotateH.length < 3) {
		rotateH = "0" + rotateH;
	}

	var rotateV = getRotateVerticalValue();
	rotateV = Math.round(rotateV/15) * 15;
	if(rotateV>=360) rotateV -= 360;
	rotateV = new String(rotateV);
	while (rotateV.length < 3) {
		rotateV = "0" + rotateV;
	}

	img.setAttribute("src", "img_angle/" + rotateH + "_" + rotateV + ".png");
}

function getPageOffset(aElem){
	try {
		if(!aElem) return null;
		var elem = aElem;
		var top = elem.offsetTop;
		var left = elem.offsetLeft;
		while(elem.offsetParent != null){
			if(!elem || !elem.offsetParent) break;
			elem = elem.offsetParent;
			top += elem.offsetTop;
			left += elem.offsetLeft;
		}
		return {left:left,top:top};
	} catch( e ){
		_dump("getPageOffset():["+e+"]");
	}
}

function getClipImgOffset(e){
	var val = undefined;
	try{
		var clip;
		try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
		if(!clip) return undefined;

		var target = e.getTarget('div.clipImgDiv');
		if(!target) return undefined;

		var offset = getPageOffset(target);

		var point = {
			x : e.getPageX(),
			y : e.getPageY()
		};

		//画面構成が変わった場合、修正する必要あり
		var cmp = Ext.getCmp('ag-command-sectional-view');
		if(cmp && cmp.body){
			var body = cmp.body.dom;
			point.x += body.scrollLeft;
			point.y += body.scrollTop;
		}

		var zoom = $MAX_YRANGE/YRangeFromServer;
		if(clip == "FB" || clip == "RL"){
			val = point.x - offset.left;
			if(Ext.isIE) val -= 1;
			val -= (target.offsetWidth/2);
			val = (YRangeFromServer*(val/target.offsetHeight));
			val += glb_clip_center;
		}else if(clip == "TB"){
			val = point.y - offset.top;
			if(Ext.isIE) val -= 2;
			val -= (target.offsetHeight/2);
			val = (YRangeFromServer*(val/target.offsetHeight));
			val -= glb_clip_center;
			val *= -1;
		}

	}catch(e){
		_dump("getClipImgOffset():e=["+e+"]");
	}
	return val;
}

function mousedownClipImg(e){

//_dump("mousedownClipImg()");
	var checked = false;
	try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
	if(!checked) return;

	var val = getClipImgOffset(e);
	if(Ext.isEmpty(val)) return;

	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
	if(!clip) return;
	if(clip == "TB"){
	}

	var textCmp = Ext.getCmp('anatomo-clip-value-text');
	textCmp.setValue(val);
	textCmp.fireEvent('change',textCmp,val);

}

var rotateImgHorizontal;
var rotateImgVertical;
var rotateImgTip;
function mouseoverClipImg(e){
	if(!rotateImgTip){
		rotateImgTip = new Ext.Tip({
		});
	}
}

function mouseoutClipImg(e){
	if(!rotateImgTip) return;
	setTimeout(function(){
		if(rotateImgTip) rotateImgTip.hide();
	},100);
}

function mousemoveClipImg(e){
	try{
		var checked = false;
		try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
		if(!checked) return;

		var val = getClipImgOffset(e);
		if(Ext.isEmpty(val)) return;

		var clip;
		try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
		if(!clip) return;
		val = Math.round(val) + ' mm';

		var pageOffsets = e.getXY();
		pageOffsets[0] += 10;
		pageOffsets[1] -= 30;

		if(rotateImgTip) rotateImgTip.showAt(pageOffsets);
		if(rotateImgTip) rotateImgTip.body.update(val);
		if(rotateImgTip) rotateImgTip.doAutoWidth();

	}catch(e){
		_dump("mousemoveClipImg():e=["+e+"]");
	}
}

function setClipImage(clipH,clipV,aCB){
	_setClipImage(clipH,clipV,[],aCB);
	return;

	var tree_param = {};
	tree_param.node = 'root';
	try{var treeType = Ext.getCmp('bp3d-tree-type-combo-ag').getValue();}catch(e){treeType=undefined;}
	if(!Ext.isEmpty(treeType)) tree_param.t_type = treeType;
	try{var bp3d_version = Ext.getCmp('anatomo-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
	tree_param.version = bp3d_version;
//	var urlStr = 'get-tree.cgi?' + Ext.urlEncode(tree_param);
	var urlStr = 'get-tree.cgi';
	Ext.Ajax.request({
		url     : urlStr,
		method  : 'POST',
		params  : Ext.urlEncode(tree_param),
		success : function (response, options) {
			var tree_nodes = Ext.util.JSON.decode(response.responseText);
			var f_ids = [];
			for(var i=0;i<tree_nodes.length;i++){
				f_ids.push(tree_nodes[i].f_id);
			}
			_setClipImage(clipH,clipV,f_ids,aCB);
		}
	});
}


function _setClipImage(clipH,clipV,f_ids,aCB){

	glb_clip_param = Ext.urlDecode(makeAnatomoPrm(),true);
	glb_clip_param.cm = 'N';
	glb_clip_param.cd = 'NaN';
//	glb_clip_param.iw = '301';
	glb_clip_param.iw = '136';
	glb_clip_param.ih = '301';
	glb_clip_param.bcl = 'FFFFFF';
	glb_clip_param.zm = '0';

	glb_clip_param.sx = '0';
	glb_clip_param.sn = '0';
	glb_clip_param.cf = '0';

	delete glb_clip_param.tn;

	delete glb_clip_param.cpa;
	delete glb_clip_param.cpb;
	delete glb_clip_param.cpc;
	delete glb_clip_param.cpd;
	delete glb_clip_param.cd;
	delete glb_clip_param.ct;
	glb_clip_param.cm = 'N';

	delete glb_clip_param.lp;
	delete glb_clip_param.lc;

	delete glb_clip_param.lt;
	delete glb_clip_param.le;
	delete glb_clip_param.la;

	delete glb_clip_param.gdr;
	delete glb_clip_param.gcl;
	delete glb_clip_param.gtc;

	for(var key in glb_clip_param){
		if(key.match(/[0-9]{3}\$/)) delete glb_clip_param[key];
	}

//_dump("_setClipImage():f_ids.length=["+f_ids.length+"]");

	if(f_ids.length>0){
		for(var i=0;i<f_ids.length;i++){
			var num = makeAnatomoOrganNumber(i+1);
			glb_clip_param["oid" + num] = f_ids[i];
			glb_clip_param["osz" + num] = 'Z';
			glb_clip_param["oop" + num] = '1.0';
			glb_clip_param["orp" + num] = 'S';
		}
	}else{
		var num = '001';
		var tg_id = Ext.getCmp('anatomo-tree-group-combo').getValue();
//_dump("_setClipImage():tg_id=["+tg_id+"]");
		if(tg_id=='1' || tg_id=='5'){
			glb_clip_param["oid" + num] = 'FMA20394';
		}else if(tg_id=='2'){
			glb_clip_param["onm" + num] = 'talairach';
		}else{
			glb_clip_param["onm" + num] = 'brain';
		}
		glb_clip_param["osz" + num] = 'Z';
		glb_clip_param["oop" + num] = '1.0';
		glb_clip_param["orp" + num] = 'S';
	}

	if(clipH == 90){
		glb_clip_param.cameraMode = "right";
	}else{
		glb_clip_param.cameraMode = "front";
	}

	glb_clip_param.cx = m_ag.initCameraPos.x;
	glb_clip_param.cy = m_ag.initCameraPos.y;
	glb_clip_param.cz = m_ag.initCameraPos.z;

	glb_clip_param.tx = m_ag.initTargetPos.x;
	glb_clip_param.ty = m_ag.initTargetPos.y;
	glb_clip_param.tz = m_ag.initTargetPos.z;

	glb_clip_param.ux = m_ag.initUpVec.x;
	glb_clip_param.uy = m_ag.initUpVec.y;
	glb_clip_param.uz = m_ag.initUpVec.z;

//	var urlStr = cgipath.focusClip+'?' + Ext.urlEncode(glb_clip_param);
	var urlStr = cgipath.focusClip;

	var jsonStr = null;
	try{
		jsonStr = ag_extensions.toJSON.URI2JSON(glb_clip_param,{
			toString:true,
			mapPin:false,
			callback:undefined
		});
	}catch(e){jsonStr = null;}
	if(Ext.isEmpty(jsonStr)) jsonStr = Ext.urlEncode(glb_clip_param);

	Ext.Ajax.request({
		url     : urlStr,
		method  : 'POST',
//		params  : Ext.urlEncode(glb_clip_param),
		params  : jsonStr,
		success : function (response, options) {
			var targetXYZYRange = Ext.util.JSON.decode(response.responseText);
			if(targetXYZYRange.Camera && targetXYZYRange.BoundingBox){
				glb_clip_param.cx = parseFloat(targetXYZYRange.Camera.CameraX);
				glb_clip_param.cy = parseFloat(targetXYZYRange.Camera.CameraY);
				glb_clip_param.cz = parseFloat(targetXYZYRange.Camera.CameraZ);

				glb_clip_param.tx = parseFloat(targetXYZYRange.Camera.TargetX);
				glb_clip_param.ty = parseFloat(targetXYZYRange.Camera.TargetY);
				glb_clip_param.tz = parseFloat(targetXYZYRange.Camera.TargetZ);

				glb_clip_param.ux = parseFloat(targetXYZYRange.Camera.CameraUpVectorX);
				glb_clip_param.uy = parseFloat(targetXYZYRange.Camera.CameraUpVectorY);
				glb_clip_param.uz = parseFloat(targetXYZYRange.Camera.CameraUpVectorZ);

				YRangeFromServer = parseFloat(targetXYZYRange.BoundingBox.ZMax) - parseFloat(targetXYZYRange.BoundingBox.ZMin);

				glb_clip_param.zm = ((parseFloat(Math.log(1800) / Math.LN2) - parseFloat(Math.log(YRangeFromServer) / Math.LN2)) * 5) / 5;

			}else if(targetXYZYRange.AgCamera){
				glb_clip_param.cx = parseFloat(targetXYZYRange.AgCamera.cameraPosX);
				glb_clip_param.cy = parseFloat(targetXYZYRange.AgCamera.cameraPosY);
				glb_clip_param.cz = parseFloat(targetXYZYRange.AgCamera.cameraPosZ);

				glb_clip_param.tx = parseFloat(targetXYZYRange.AgCamera.targetPosX);
				glb_clip_param.ty = parseFloat(targetXYZYRange.AgCamera.targetPosY);
				glb_clip_param.tz = parseFloat(targetXYZYRange.AgCamera.targetPosZ);

				glb_clip_param.ux = parseFloat(targetXYZYRange.AgCamera.upVecX);
				glb_clip_param.uy = parseFloat(targetXYZYRange.AgCamera.upVecY);
				glb_clip_param.uz = parseFloat(targetXYZYRange.AgCamera.upVecZ);

				YRangeFromServer = parseFloat(targetXYZYRange.AgCamera.yrange);

				glb_clip_param.zm = ((parseFloat(Math.log(1800) / Math.LN2) - parseFloat(Math.log(YRangeFromServer) / Math.LN2)) * 5) / 5;
			}


			delete glb_clip_param.cameraMode;
			for(var key in glb_clip_param){
				if(typeof glb_clip_param[key] == "number" && isNaN(glb_clip_param[key])){
					delete glb_clip_param[key];
					continue;
				}
				if(Ext.isEmpty(glb_clip_param[key])){
					delete glb_clip_param[key];
					continue;
				}
			}

			glb_clip_center = 0;
			var clip;
			try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
			if(clip){
				if(clip == 'FB'){
					glb_clip_center = glb_clip_param.ty;
				}else if(clip == 'RL'){
					glb_clip_center = glb_clip_param.tx;
				}else if(clip == 'TB'){
					glb_clip_center = glb_clip_param.tz;
				}
			}

			var jsonStr = null;
			try{
				jsonStr = ag_extensions.toJSON.URI2JSON(glb_clip_param,{
					toString:true,
					mapPin:false,
					callback:undefined
				});
			}catch(e){jsonStr = null;}
			if(Ext.isEmpty(jsonStr)) jsonStr = Ext.urlEncode(glb_clip_param);

//			var src = Ext.urlEncode(glb_clip_param);
			var src = jsonStr;
			var img = document.getElementById("clipImg");
//			img.setAttribute("src", cgipath.image+'?'+src);
HTML
if(1 || $useImagePost ne 'true'){
	print <<HTML;
			img.setAttribute("src", cgipath.image+'?'+src);
HTML
}else{
	print <<HTML;
			Ext.Ajax.request({
				url     : cgipath.image,
				method  : 'POST',
				params  : src,
				success : function(conn,response,options){
					try{
						img.src = conn.responseText;
					}catch(e){
						alert(e);
					}
				},
				failure : function(conn,response,options){
					try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
					var msg = '[';
					if(results && results.msg){
						msg += results.msg+' ]';
					}else{
						msg += conn.status+" "+conn.statusText+' ]';
					}
					Ext.MessageBox.show({
						title   : 'clipImg',
						msg     : msg,
						buttons : Ext.MessageBox.OK,
						icon    : Ext.MessageBox.ERROR
					});
				}
			});
HTML
}
print <<HTML;
			if(aCB) (aCB)(glb_clip_param,YRangeFromServer);
		}
	});
}

function setClipImageHV (clipH,clipV,rotateH,rotateV,aCB) {
	var clip;
	try{clip = Ext.getCmp('anatomo-clip-predifined-plane').getValue();}catch(e){clip = undefined;}
	if(!clip) return;

	stopUpdateAnatomo();

	glb_rotateH = rotateH;
	glb_rotateV = rotateV;

//_dump("CALL setClipImage(1)");
	setClipImage(clipH,clipV,function(aParam,aYRange){ onloadClipImage(); });
}

function onloadClipImage(){
	var checked = false;
	try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
	if(!checked) return;
	onload_ag_img();
}

function updateClipImage(){
	var checked = false;
	try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
	if(!checked) return false;
	return false;
}

function setRotate(horizontal,vertical) {

//m_ag.cameraPos = new AGVec3d(2.7979888916016167, -998.4280435445771, 809.7306805551052);
//m_ag.targetPos = new AGVec3d(2.7979888916015625, -110.37168800830841, 809.7306805551052);
//m_ag.upVec = new AGVec3d(0, 0, 1);

	setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
	var deg = calcRotateDeg();
//_dump("setRotate():H=["+deg.H+"],V=["+deg.V+"]");

	var h = (deg.H - horizontal) * -1;
	var v = (deg.V - vertical) * -1;

//_dump("setRotate():h=["+h+"],v=["+v+"]");

	if(h!=0) addLongitude(h);

	if(v!=0) addLatitude(v);

	var deg = calcRotateDeg();
//_dump("setRotate():H=["+deg.H+"],V=["+deg.V+"]\\n");
	setRotateHorizontalValue(horizontal);
	setRotateVerticalValue(vertical);

	updateRotateImg();
	stopUpdateAnatomo();
	_updateAnatomo();
}

function setRotateHorizontal (angle,degree) {
	var deg = getRotateHorizontalValue();
	angle = Math.round(angle/15)*15;
	while(deg != angle){
		deg += (15*degree);
		if(deg >= 360) deg = deg - 360;
		if(deg < 0) deg = deg + 360;
		setRotateHorizontalValue(deg);
		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
		addLongitude(15*degree);
	}
}

function setRotateVertical (angle,degree) {
	var deg = getRotateVerticalValue();
	angle = Math.round(angle/15)*15;
	while(deg != angle){
		deg += (15*degree);
		if(deg >= 360) deg = deg - 360;
		if(deg < 0) deg = deg + 360;
		setRotateVerticalValue(deg);
		setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
		addLatitude(15*degree);
	}
}

function rotateHorizontal (degree) {
	var deg = getRotateHorizontalValue();
	deg = deg + degree;
	if (deg >= 360) {
		deg = deg - 360;
	}
	if (deg < 0) {
		deg = deg + 360;
	}
	setRotateHorizontalValue(deg);
	updateRotateImg();
	setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
	addLongitude(degree);
	updateAnatomo();
}

function rotateVertical (degree) {
	var deg = getRotateVerticalValue();
	deg = deg + degree;
	if (deg < 0) {
		deg = deg + 360;
	}
	if (deg >= 360) {
		deg = deg - 360;
	}
	setRotateVerticalValue(deg);
	updateRotateImg();
	setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
	addLatitude(degree);
	updateAnatomo();
}

function anatomoZoomUpButton () {
	var slider = Ext.getCmp('zoom-slider');
	slider.setValue(slider.getValue() + 1);
}

function anatomoZoomDownButton () {
	var slider = Ext.getCmp('zoom-slider');
	slider.setValue(slider.getValue() - 1);
}

function anatomoUpdateZoomValueText (value) {
	anatomoUpdateZoomValue = true;
	var textField = Ext.getCmp('zoom-value-text');
	if(textField) textField.setValue(value);
	anatomoUpdateZoomValue = false;
}

function anatomoClipUpButton () {
	var textField = Ext.getCmp('anatomo-clip-value-text');
	var slider = Ext.getCmp('anatomo-clip-slider');
	slider.setValue(textField.getValue() + 1);
}

function anatomoClipDownButton () {
	var textField = Ext.getCmp('anatomo-clip-value-text');
	var slider = Ext.getCmp('anatomo-clip-slider');
	slider.setValue(textField.getValue() - 1);
}

function anatomoUpdateClipValueText (value) {
	anatomoUpdateClipValue = true;
	var textField = Ext.getCmp('anatomo-clip-value-text');
	if(textField) textField.setValue(value);
	anatomoUpdateClipValue = false;
}

var selectCommand = function () {
};


function anatomography_init() {
	makeRotImgDiv();
	ag_command_init();
}

function anatomography_render(){

	var ag_image_control_center_panel = new Ext.Panel({
		region    : 'center',
		border    : false,
		bodyStyle : 'border-top-width:1px;border-right-width:1px;',
		layout    : 'accordion',
		items : [

		{
			title      : 'Image controls',
			border     : false,
			autoScroll : false,
			bodyStyle  : 'overflow-y:auto;',
			contentEl  : 'ag-command-image-controls-content',
			collapsed  : true,
			listeners: {
				'beforerender': function(panel){
				},
				'render': function(panel){
					Ext.get('ag-command-image-controls-content').removeClass('x-hide-display');
					var prm_record = ag_param_store.getAt(0);

					ag_command_rotation_horizontal_numberField_task = new Ext.util.DelayedTask(function(){
						var field = Ext.getCmp('rotateH');
						if(!field || !field.rendered) return;
						if(!field.validate()) return;
						setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
						field.selectText();
					});

					new Ext.form.NumberField({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-rotation-horizontal-render',
						id: 'rotateH',
						width: 30,
						value : prm_record.data.rotate_h,
						allowBlank : false,
						allowDecimals : true,
						allowNegative : true,
						selectOnFocus : true,
						enableKeyEvents : true,
						maxValue : 359,
						minValue : 0,
						listeners: {
							'keydown' : function(field,e){
								if(e.getKey()!=e.ENTER){
									ag_command_rotation_horizontal_numberField_task.delay(500);
									return;
								}
								if(!field.validate()) return;
								setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
								field.selectText();
							},
							'change' : function(field){
								if(!field.validate()) return;
								setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
							}
						}
					})

					ag_command_rotation_vertical_numberField_task = new Ext.util.DelayedTask(function(){
						var field = Ext.getCmp('rotateV');
						if(!field || !field.rendered) return;
						if(!field.validate()) return;
						setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
						field.selectText();
					});

					new Ext.form.NumberField({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-rotation-vertical-render',
						id: 'rotateV',
						width: 30,
						value : prm_record.data.rotate_v,
						allowBlank : false,
						allowDecimals : true,
						allowNegative : true,
						selectOnFocus : true,
						enableKeyEvents : true,
						maxValue : 359,
						minValue : 0,
						listeners: {
							'keydown' : function(field,e){
								if(e.getKey()!=e.ENTER){
									ag_command_rotation_vertical_numberField_task.delay(500);
									return;
								}
								if(!field.validate()) return;
								setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
								field.selectText();
							},
							'change' : function(field){
								if(!field.validate()) return;
								setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
							}
						}
					});
HTML
if($autoRotationHidden ne 'true'){
	print <<HTML;
					new Ext.form.Checkbox({
						ctCls : 'x-small-editor',
						renderTo : 'ag-command-image-controls-rotateAuto-render',
						id       : 'ag-command-image-controls-rotateAuto',
						boxLabel : '&nbsp;On/Off',
						checked  : false,
						listeners: {
							'check': function(checkbox,checked){
								Ext.getCmp('ag-command-autorotate-chechbox').setValue(checked);
if(checked){
//	_dump("");
//	_dump("m_ag.cameraPos");
	calcRotateAxisDeg(m_ag.cameraPos);
//	_dump("m_ag.targetPos");
	calcRotateAxisDeg(m_ag.targetPos);
//	_dump("m_ag.upVec");
	calcRotateAxisDeg(m_ag.upVec);
//	_dump("");
}


								agRotateAuto.init();
								agRotateAuto.rotate(checked);
								stopUpdateAnatomo();
								_updateAnatomo(false);
							},
							scope:this
						}
					});

					new Ext.form.ComboBox({
						ctCls         : 'x-small-editor',
						renderTo      : 'ag-command-image-controls-rotateAuto-angles-render',
						id            : 'ag-command-image-controls-rotateAuto-angles',
						editable      : false,
						mode          : 'local',
						lazyInit      : false,
						displayField  : 'disp',
						valueField    : 'value',
						width         : 45,
						triggerAction : 'all',
						value         : 15,
						regex         : new RegExp("^[\-0-9]+\$"),
						allowBlank    : false,
						selectOnFocus : true,
						validator     : function(value){
							value = Number(value);
							if(isNaN(value)) return '';
							if(Math.abs(value)<=0 || Math.abs(value)>180) return '';
							return true;
						},
						store : new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
//								[-90, -90],
//								[-45, -45],
//								[-30, -30],
//								[-15, -15],
//								[-10, -10],
//								[-5, -5],
								[90, 90],
								[45, 45],
								[30, 30],
								[15, 15],
								[10, 10],
								[5, 5]
							]
						}),
						listeners : {
							'render' : function(combo){
							},
							'valid' : function(combo) {
								var value = Number(combo.getValue());
								var chg_value = 360/Math.round(360/value);
//								_dump("value=["+value+"]:chg_value=["+chg_value+"]");
								if(value!=chg_value) combo.setValue(chg_value);
							},
							'select' : function(combo, record, index) {
								agRotateAuto.init();
							},
							scope:this
						}
					});

					new Ext.form.NumberField({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-image-controls-rotateAuto-interval-render',
						id       : 'ag-command-image-controls-rotateAuto-interval',
						width: 25,
						value : 1,
						allowBlank : false,
						allowDecimals : true,
						allowNegative : true,
						selectOnFocus : true,
						enableKeyEvents : true,
						maxValue : 30,
						minValue : 1,
						listeners: {
							'keydown' : function(field,e){
								if(e.getKey()!=e.ENTER){
									ag_command_rotation_vertical_numberField_task.delay(500);
									return;
								}
								if(!field.validate()) return;
//								setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
//								field.selectText();
							},
							'change' : function(field){
//								if(!field.validate()) return;
//								setRotate(getRotateHorizontalValue(),getRotateVerticalValue());
							}
						}
					});
					agRotateAuto.init();
HTML
}
print <<HTML;
				}
			}
		},
		{
			title      : 'Sectional View',
			id         : 'ag-command-sectional-view',
			border     : false,
			autoScroll : false,
			bodyStyle  : 'overflow-y:auto;',
			contentEl  : 'ag-command-sectional-view-content',
			hidden     : $sectionalViewHidden,
			listeners: {
				'beforerender': function(panel){
				},
				'render': function(panel){
					Ext.get('ag-command-sectional-view-content').removeClass('x-hide-display');
					var prm_record = ag_param_store.getAt(0);

					new Ext.form.Checkbox ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-clip-checkbox-render',
						id : 'anatomo-clip-check',
						checked: isNaN(prm_record.data.clip_depth)?false:true,
						listeners: {
							'render': function(checkbox){
								checkbox.on('check',oncheck_anatomo_clip_check);
							},
							scope:this
						}
					});

					new Ext.form.ComboBox ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-clip-method-render',
						id : 'anatomo-clip-method-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 68,
						triggerAction: 'all',
						value: 'NS',
						hidden : false,
						store: new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
								['Amptation', 'NS'],
								['Section', 'S']
							]
						}),
						listeners: {
							'render': function(combobox){
								combobox.on('select',onselect_anatomo_clip_method_combo);
							},
							scope:this
						}
					});

					new Ext.form.ComboBox ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-clip-predifined-render',
						id : 'anatomo-clip-predifined-plane',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 88,
						listWidth : 100,
						triggerAction: 'all',
						value: 'TB',
						hidden : false,
						store: new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
								['FRONTAL', 'FB'],
								['SAGITTAL', 'RL'],
								['TRANSVERSE', 'TB'],
								['FREE PLANE', 'FREE']
							]
						}),
						listeners: {
							'render': function(combobox){
								combobox.on('select',onselect_anatomo_clip_predifined_plane);
								setClipImage(0,0,setClipLine);
							},
							scope:this
						}
					});

					new Ext.form.Checkbox ({
						hidden : false,
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-clip-fix-checkbox-render',
						id : 'anatomo-clip-fix-check',
						boxLabel : 'Fix',
						checked: false,
						listeners: {
							'render': function(checkbox){
								checkbox.on('check',oncheck_anatomo_clip_fix_check);
							},
							scope:this
						}
					});

					new Ext.form.Checkbox ({
						hidden : false,
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-clip-reverse-checkbox-render',
						id : 'anatomo-clip-reverse-check',
						boxLabel : 'Reverse',
						checked: false,
						listeners: {
							'render': function(checkbox){
								checkbox.on('check',oncheck_anatomo_clip_reverse_check);
							},
							scope:this
						}
					});

					new Ext.Slider({
						renderTo : 'ag-command-clip-slider-render',
						id: 'anatomo-clip-slider',
						vertical: false,
						value : isNaN(prm_record.data.clip_depth)?0:prm_record.data.clip_depth,
						width : 121,
						minValue: -350,
						maxValue: 1800,
						increment: 1,
						plugins: tip_depth,
						hidden : false,
						listeners: {
							'render': function(slider){
								slider.on('change',onchange_anatomo_clip_slider);
							},
							scope:this
						}
					});

					new Ext.form.NumberField ({
						ctCls : 'x-small-editor',
						renderTo : 'ag-command-clip-text-render',
						id: 'anatomo-clip-value-text',
						width: 40,
						value : isNaN(prm_record.data.clip_depth)?0:prm_record.data.clip_depth,
//						maxValue : 1000,
//						minValue : -1000,
						maxValue : 1800,
						minValue : -350,
						hidden : false,
						listeners: {
							'render': function(numberfield){
								numberfield.on('change',onchange_anatomo_clip_value_text);
							},
							scope:this
						}
					});

					Ext.EventManager.on("clipImgDiv", 'mousedown', mousedownClipImg);
					Ext.EventManager.on("clipImgDiv", 'mouseover', mouseoverClipImg);
					Ext.EventManager.on("clipImgDiv", 'mouseout',  mouseoutClipImg);
					Ext.EventManager.on("clipImgDiv", 'mousemove', mousemoveClipImg);
//					Ext.EventManager.on("clipImg",    'load',      onloadClipImage);

					var fix = Ext.getCmp('anatomo-clip-fix-check');
					if(fix) fix.hide();
					var reverse = Ext.getCmp('anatomo-clip-reverse-check');
					if(reverse) reverse.hide();
					var method = Ext.getCmp('anatomo-clip-method-combo');
					if(method) method.hide();
					var plane = Ext.getCmp('anatomo-clip-predifined-plane');
					if(plane) plane.hide();
					var slider = Ext.getCmp('anatomo-clip-slider');
					if(slider) slider.hide();
					var textField = Ext.getCmp('anatomo-clip-value-text');
					if(textField) textField.hide();

					var buttonSliderUp = Ext.get('anatomo-clip-slider-up-button');
					if(buttonSliderUp) buttonSliderUp.hide();
					var buttonSliderDown = Ext.get('anatomo-clip-slider-down-button');
					if(buttonSliderDown) buttonSliderDown.hide();
					var buttonTextUp = Ext.get('anatomo-clip-text-up-button');
					if(buttonTextUp) buttonTextUp.hide();
					var buttonTextDown = Ext.get('anatomo-clip-text-down-button');
					if(buttonTextDown) buttonTextDown.hide();
					var labelClipUnit = Ext.get('anatomo-clip-unit-label');
					if(labelClipUnit) labelClipUnit.hide();

					var clipImgDiv = Ext.get('clipImgDiv');
					if(clipImgDiv) clipImgDiv.hide();

				}
			}
		},
		{
			title      : 'Window controls',
			id         : 'ag-command-window-controls',
			border     : false,
			autoScroll : false,
			bodyStyle  : 'overflow-y:auto;',
			contentEl  : 'ag-command-window-controls-content',
			listeners: {
				'beforerender': function(panel){
				},
				'render': function(panel){
					Ext.get('ag-command-window-controls-content').removeClass('x-hide-display');
					var prm_record = ag_param_store.getAt(0);

					new Ext.form.ComboBox({
						ctCls : 'x-small-editor',
						renderTo:'ag-command-windowsize-width-render',
						id:'anatomo-width-combo',
						editable: true,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 55,
						triggerAction: 'all',
						value: prm_record.data.image_w,
						store: new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
								[100, 100],
								[200, 200],
								[300, 300],
								[400, 400],
								[500, 500],
								[600, 600],
								[700, 700],
								[800, 800],
								[900, 900]
							]
						}),
						listeners: {
							'render': function(combo){
								var checkbox = Ext.getCmp('anatomo-windowsize-autosize-check');
								if(checkbox && checkbox.rendered) oncheck_anatomo_windowsize_autosize_check(checkbox,checkbox.getValue());
							},
							'select' : function(combo, record, index) {
								var prm_record =ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('image_w', record.data.value);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							},
							scope:this
						}
					});

					new Ext.form.ComboBox({
						ctCls : 'x-small-editor',
						renderTo:'ag-command-windowsize-height-render',
						id:'anatomo-height-combo',
						editable: true,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 55,
						value:prm_record.data.image_h,
						triggerAction: 'all',
						store: new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
								[100, 100],
								[200, 200],
								[300, 300],
								[400, 400],
								[500, 500],
								[600, 600],
								[700, 700],
								[800, 800],
								[900, 900]
							]
						}),
						listeners: {
							'render': function(combo){
								var checkbox = Ext.getCmp('anatomo-windowsize-autosize-check');
								if(checkbox && checkbox.rendered) oncheck_anatomo_windowsize_autosize_check(checkbox,checkbox.getValue());
							},
							'select' : function(combo, record, index) {
								var prm_record =ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('image_h', record.data.value);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							},
							scope:this
						}
					});

					new Ext.form.Checkbox ({
						hidden : false,
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-windowsize-autosize-checkbox-render',
						id : 'anatomo-windowsize-autosize-check',
						boxLabel : 'Auto Window Size',
						checked: true,
						listeners: {
							'render': function(checkbox){
								checkbox.on('check',oncheck_anatomo_windowsize_autosize_check);
								oncheck_anatomo_windowsize_autosize_check(checkbox,checkbox.getValue());
							},
							scope:this
						}
					});

HTML
if($useColorPicker eq 'true'){
	print <<HTML;
					new Ext.ux.ColorPickerField({
HTML
}else{
	print <<HTML;
					new Ext.ux.ColorField({
HTML
}
print <<HTML;
						ctCls : 'x-small-editor',
						width: 80,
						renderTo:'ag-command-bgcolor-render',
						value:prm_record.data.bg_rgb,
						id:'anatomo-bgcp',
						listeners: {
							select : function (e, color) {
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('bg_rgb', color);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							}
						}
					});

					new Ext.form.Checkbox ({
						hidden : false,
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-bgcolor-transparent-checkbox-render',
						id : 'anatomo-bgcolor-transparent-check',
						hidden : $bgcolorTransparentHidden,
						boxLabel : 'Transparent',
						checked: false,
						listeners: {
							'render': function(checkbox){
								checkbox.on('check',oncheck_anatomo_bgcolor_transparent_check);
								oncheck_anatomo_bgcolor_transparent_check(checkbox,checkbox.getValue());
							},
							scope:this
						}
					});

					new Ext.form.TextField ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-colormap-max-render',
						id: 'scalar-max-textfield',
						width: 45,
						value: (isNaN(prm_record.data.scalar_max))?'':prm_record.data.scalar_max,
						listeners: {
							'change': {
								fn:function (textField, newValue, oldValue) {
									var prm_record =ag_param_store.getAt(0);
									prm_record.beginEdit();
									prm_record.set('scalar_max', parseFloat(newValue));
									prm_record.endEdit();
									prm_record.commit();
									updateAnatomo();
								}, scope:this
							}
						}
					});

					new Ext.form.TextField ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-colormap-min-render',
						id: 'scalar-min-textfield',
						width: 45,
						value: (isNaN(prm_record.data.scalar_min))?'':prm_record.data.scalar_min,
						listeners: {
							'change': {
								fn:function (textField, newValue, oldValue) {
									var prm_record =ag_param_store.getAt(0);
									prm_record.beginEdit();
									prm_record.set('scalar_min', parseFloat(newValue));
									prm_record.endEdit();
									prm_record.commit();
									updateAnatomo();
								}, scope:this
							}
						}
					});

					new Ext.form.Checkbox ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-colormap-bar-render',
						id: 'show-colorbar-check',
						width: 45,
						checked: (prm_record.data.colorbar_f=='1')?true:false,
						listeners: {
							'check': {
								fn:function (checkbox, fChecked) {
									var button = Ext.getCmp('ag-pallet-heatmap-bar-button');		//2011-09-30 ADD
									if(button && button.rendered) button.toggle(fChecked,true);	//2011-09-30 ADD

									var prm_record = ag_param_store.getAt(0);
									prm_record.beginEdit();
									if (fChecked) {
										prm_record.set('colorbar_f', '1');
										prm_record.set('heatmap_f', '1');
									} else {
										prm_record.set('colorbar_f', '0');
										prm_record.set('heatmap_f', '0');
									}
									prm_record.endEdit();
									prm_record.commit();
									updateAnatomo();

									//2011-09-30 ADD
									if(fChecked){
										var grid = Ext.getCmp('ag-parts-gridpanel');
										if(grid && grid.rendered){
											var colModel = grid.getColumnModel();
											var colid = colModel.getIndexById('value');
											if(colModel.isHidden(colid)) colModel.setHidden(colid,false);
										}
									}

								}, scope:this
							}
						}
					});

//					_dump("prm_record.data.color_rgb=["+prm_record.data.color_rgb+"]");
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
					new Ext.ux.ColorPickerField({
HTML
}else{
	print <<HTML;
					new Ext.ux.ColorField({
HTML
}
print <<HTML;
						ctCls : 'x-small-editor',
						width: 80,
						renderTo:'ag-command-default-parts-color-render',
						value:prm_record.data.color_rgb.toUpperCase(),
						id:'anatomo-default-parts-color',
						listeners: {
							select: function (e, color) {
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('color_rgb', color);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							}
						}
					});

HTML
if($useColorPicker eq 'true'){
	print <<HTML;
					new Ext.ux.ColorPickerField({
HTML
}else{
	print <<HTML;
					new Ext.ux.ColorField({
HTML
}
print <<HTML;
						ctCls : 'x-small-editor',
						width: 80,
						renderTo:'ag-command-default-pick-color-render',
						value: get_point_color().toUpperCase(),
						id:'anatomo-default-pick-color',
						listeners: {
							select: function(field, color){
								set_point_color(color);
								if(!Ext.isEmpty(get_point_f_id())) updateAnatomo();
							}
						}
					});

HTML
if($addPointElementHidden ne 'true'){
	print <<HTML;
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
					new Ext.ux.ColorPickerField({
HTML
}else{
	print <<HTML;
					new Ext.ux.ColorField({
HTML
}
print <<HTML;
						ctCls : 'x-small-editor',
						width: 80,
						renderTo:'ag-command-default-point-parts-color-render',
						value:prm_record.data.point_color_rgb,
						id:'anatomo-default-point-parts-color',
						listeners: {
							select: function (palette, color) {
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('point_color_rgb', color);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							}
						}
					});

					new Ext.form.ComboBox({
						ctCls : 'x-small-editor',
						renderTo:'ag-command-point-sphere-render',
						id:'ag-command-point-sphere-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 55,
						value:prm_record.data.point_sphere,
						triggerAction: 'all',
						store: new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
								['Small', 'SS'],
								['Medium','SM'],
								['Large', 'SL']
							]
						}),
						listeners: {
							'select' : function(combo, record, index) {
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('point_sphere', record.data.value);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							},
							scope:this
						}
					});

					new Ext.form.ComboBox({
						ctCls : 'x-small-editor',
						renderTo:'ag-command-point-label-render',
						id:'anatomo-point-label-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 120,
						value:prm_record.data.point_label,
						triggerAction: 'all',
						store: new Ext.data.JsonStore({
							autoLoad : true,
							url    : 'get-point-class-label.cgi',
							root   : 'records',
							fields : ['disp', 'value'],
							listeners     : {
								'beforeload' : {
									fn : function(self,options){
										self.baseParams = self.baseParams || {};
										var bp3d_version = Ext.getCmp('anatomo-version-combo');
										if(bp3d_version && bp3d_version.rendered){
											self.baseParams.version = bp3d_version.getValue();
										}else{
											self.baseParams.version = init_bp3d_version;
										}
									},
									scope:this
								},
								'load' : {
									fn : function(self,records,options){
										if(!records || records.lenth==0) return;
										var record = records[0];
										var combo = Ext.getCmp('anatomo-point-label-combo');
										combo.setValue(record.data.value);
										combo.fireEvent('select',combo,record,0);
									},
									scope:this,
									single:true
								}
							}
						}),
						listeners: {
							'render': function(combo){
								var checkbox = Ext.getCmp('anatomo-windowsize-autosize-check');
								if(checkbox && checkbox.rendered) oncheck_anatomo_windowsize_autosize_check(checkbox,checkbox.getValue());
							},
							'select' : function(combo, record, index) {
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('point_label', record.data.value);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							},
							scope:this
						}
					});

					new Ext.form.Checkbox ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-point-description-render',
						id: 'ag-command-point-description-check',
						width: 45,
						checked: (prm_record.data.point_desc===1),
						listeners: {
							'check': {
								fn:function (checkbox, fChecked) {
									var prm_record = ag_param_store.getAt(0);
									prm_record.beginEdit();
									if (fChecked) {
										prm_record.set('point_desc', 1);
										Ext.get('ag-command-point-description-command-div').show();
									} else {
										prm_record.set('point_desc', 0);
										Ext.get('ag-command-point-description-command-div').hide();
									}
									prm_record.endEdit();
									prm_record.commit();
									updateAnatomo();
								}, scope:this
							}
						}
					});
					if(prm_record.data.point_desc===1){
						Ext.get('ag-command-point-description-command-div').show();
					}else{
						Ext.get('ag-command-point-description-command-div').hide();
					}

					new Ext.form.ComboBox({
						ctCls : 'x-small-editor',
						renderTo:'ag-command-point-description-draw-point-indication-line-render',
						id:'ag-command-point-description-draw-point-indication-line-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'disp',
						valueField: 'value',
						width: 55,
						value:prm_record.data.point_point_line,
						triggerAction: 'all',
						store: new Ext.data.SimpleStore({
							fields: ['disp', 'value'],
							data : [
								['None', 0],
								['Tip', 1],
								['End', 2]
							]
						}),
						listeners: {
							'select' : function(combo, record, index) {
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('point_point_line', record.data.value);
								prm_record.endEdit();
								prm_record.commit();
								updateAnatomo();
							},
							scope:this
						}
					});
HTML
}
print <<HTML;
				}
			}
		},

//2011-09-07
		{
			hidden:true,// 2013/11/12時点で常に空なので、必要になれば表示させる
			title      : 'Sample',
			id         : 'ag-command-sample-panel',
			border     : false,
			autoScroll : false,
			bodyStyle  : 'overflow-y:auto;',
HTML
if($lsdb_Auth || $sampleLatestVersionHidden ne 'true'){
	print <<HTML;
			tbar : [
HTML
	if($sampleLatestVersionHidden ne 'true'){
		print <<HTML;
				new Ext.form.Checkbox({
					ctCls : 'x-small-editor',
					id : 'ag-command-sample-latest-version-check',
					boxLabel : 'Latest version',
					hidden   : $sampleLatestVersionHidden,
					checked  : $sampleLatestVersionChecked,
					listeners: {
						'render': function(checkbox){
						},
						scope:this
					}
				})
HTML
		print qq|				,\n| if($lsdb_Auth);
	}
	if($lsdb_Auth && 0){
		print <<HTML;
				'->',
				'-',
				{
					id   : 'ag-command-sample-panel-save-button',
					tooltip : 'Save',
					iconCls : 'sample_save',
					listeners : {
						'click' : {
							fn : function (button, e) {
								var records = ag_parts_gridpanel.getStore().getRange();
								if(records.length == 0) return;

								var tg_id = undefined;
								var tg_model = undefined;
								try{
									tg_id = Ext.getCmp('anatomo-tree-group-combo').getValue();
									if(tg_id && tg2model[tg_id] && tg2model[tg_id].tg_model) tg_model = tg2model[tg_id].tg_model;
								}catch(e){_dump(e);}

								var objs = {
									baseparam  : ag_param_store.getAt(0).data,
									partslist  : [],
									anatomoprm : Ext.urlDecode(makeAnatomoPrm(),true),
									cameraprm  : {
										m_ag.cameraPos : m_ag.cameraPos,
										m_ag.targetPos : m_ag.targetPos,
										m_ag.upVec     : m_ag.upVec,
										m_ag.longitude : m_ag.longitude,
										m_ag.latitude  : m_ag.latitude,
										m_ag.distance  : m_ag.distance
									},
									environment : {
										rotate : {
											H : getRotateHorizontalValue(),
											V : getRotateVerticalValue()
										},
										zoom : Ext.getCmp("zoom-value-text").getValue(),
										tg_id : tg_id,
										model : tg_model,
										bp3dversion : Ext.getCmp("anatomo-version-combo").getValue(),
										treename : Ext.getCmp("bp3d-tree-type-combo").getValue(),
										size : {
											width  : Ext.getCmp("anatomo-width-combo").getValue(),
											height : Ext.getCmp("anatomo-height-combo").getValue()
										},
										bgcolor : Ext.getCmp("anatomo-bgcp").getValue(),
										bgtransparent : Ext.getCmp("anatomo-bgcolor-transparent-check").getValue(),
										colormap : {
											max  : Ext.getCmp("scalar-max-textfield").getValue(),
											min  : Ext.getCmp("scalar-min-textfield").getValue(),
											bar  : Ext.getCmp("show-colorbar-check").getValue()
										}
									}
								};
								if(Ext.getCmp("anatomo-clip-check").getValue()){
									var src = Ext.getDom("clipImg").getAttribute("src");
									var clipprm = Ext.urlDecode(src.substr(src.indexOf("?")+1),true);
									objs.environment.clip = {
										method : Ext.getCmp("anatomo-clip-method-combo").getValue(),
										predifined : Ext.getCmp("anatomo-clip-predifined-plane").getValue(),
										fix : Ext.getCmp("anatomo-clip-fix-check").getValue(),
										reverse : Ext.getCmp("anatomo-clip-reverse-check").getValue(),
										value : Ext.getCmp("anatomo-clip-value-text").getValue(),
										clipprm : clipprm
									};
								}

								for(var i=0;i<records.length;i++){
									if(records[i].data.constructor===Array) continue;
									objs.partslist.push(records[i].data);
								}

								var save_form = new Ext.form.FormPanel({
									baseCls     : 'x-plain',
									defaultType : 'textfield',
									defaults    : {
										selectOnFocus : true
									},
									labelWidth  : 50,
									layoutConfig: {
										// layout-specific configs go here
										labelSeparator: ''
									},
									items       : [{
										xtype      : 'hidden',
										name       : 'type',
										value      : 'sample'
									},{
										xtype      : 'hidden',
										name       : 'param',
										value      : Ext.util.JSON.encode(objs)
									},{
										fieldLabel : 'Title',
										name       : 'title',
										allowBlank : false,
										anchor     : '100%'
									},{
										fieldLabel : 'Options',
										boxLabel   : 'Qualified',
										name       : 'qualified',
										xtype      : 'checkbox',
										checked    : true
									},{
										boxLabel   : 'Description',
										name       : 'description',
										xtype      : 'checkbox',
										checked    : true
									},{
										boxLabel   : 'Display environment',
										name       : 'environment',
										xtype      : 'checkbox',
										checked    : true
									}]
								});

								var save_window = new Ext.Window({
									title       : 'Save',
									width       : 250,
									height      : 200,
									plain       : true,
									bodyStyle   : 'padding:5px;',
									buttonAlign : 'center',
									defaultButton : 0,
									modal         : true,
									resizable     : false,
									items         : save_form,
									buttons : [{
										text    : 'Save',
										handler : function(){
											if(save_form.getForm().isValid()){
												save_form.getForm().submit({
													url     : 'put-savecontents.cgi',
													waitMsg : 'Wait...',
													success : function(fp, o){
														try{
															if(o.result.success == true){
																Ext.MessageBox.show({
																	title   : 'Save',
																	msg     : 'OK',
																	buttons : Ext.MessageBox.OK,
																	icon    : Ext.MessageBox.INFO,
																	fn      : function(){
																		save_window.close();
																		var cmp = Ext.getCmp('ag-sample-dataview');
																		if(cmp) cmp.initialConfig.store.reload();
																	}
																});
																return;
															}
														}catch(e){ _dump("success():"+ e + ""); }

														Ext.MessageBox.show({
															title   : 'Save',
															msg     : 'ERROR:'+o.result.msg,
															buttons : Ext.MessageBox.OK,
															icon    : Ext.MessageBox.ERROR
														});

													},
													failure : function(fp, o){
														Ext.MessageBox.show({
															title   : 'Save',
															msg     : 'ERROR',
															buttons : Ext.MessageBox.OK,
															icon    : Ext.MessageBox.ERROR
														});
													}
												});
											}
										}
									},{
										text    : 'Cancel',
										handler : function(){
											save_window.close();
										}
									}]
								});
								save_window.show();
							},
							scope: this
						}
					}
				},
				'-',
				{
					id : 'pallet-delete-button',
					tooltip : 'Delete',
					iconCls : 'sample_delete',
					listeners : {
						'click' : {
							fn : function (button, e) {
								var view = Ext.getCmp('ag-sample-dataview');
								var records = view.getSelectedRecords();
								if(!records || records.length == 0) return;
								Ext.MessageBox.show({
									title   : 'Delete',
									msg     : 'Delete ['+records[0].data.name+']?',
									buttons : Ext.MessageBox.YESNO,
									icon    : Ext.MessageBox.QUESTION,
									fn:function(btn){
										if(btn != 'yes') return;
										var delobjs = {
											id     : records[0].data.id,
											parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
											lng    : gParams.lng,
											type   : 'sample'
										};
										Ext.Ajax.request({
											url     : 'del-savecontents.cgi',
											method  : 'POST',
											params  : Ext.urlEncode(delobjs),
											success : function(conn,response,options){
												try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
												if(!results || results.success == false){
													Ext.MessageBox.show({
														title   : 'Delete',
														msg     : 'ERROR'+(results && results.msg ? " ["+results.msg+"]" : ""),
														buttons : Ext.MessageBox.OK,
														icon    : Ext.MessageBox.ERROR
													});
												}
												var cmp = Ext.getCmp('ag-sample-dataview');
												if(cmp) cmp.initialConfig.store.reload();
											},
											failure : function(conn,response,options){
												Ext.MessageBox.show({
													title   : 'Delete',
													msg     : 'ERROR',
													buttons : Ext.MessageBox.OK,
													icon    : Ext.MessageBox.ERROR
												});
												var cmp = Ext.getCmp('ag-sample-dataview');
												if(cmp) cmp.initialConfig.store.reload();
											}
										});
									}
								});
							},
							scope: this
						}
					}
				}
HTML
	}
	print <<HTML;
			],
HTML
}
print <<HTML;
			listeners: {
				'beforerender': function(panel){
				},
				'render': function(panel){
//					setTimeout(function(){Ext.getCmp('ag-command-sample-panel').expand(false);},500);
					setTimeout(function(){Ext.getCmp('ag-command-window-controls').expand(false);},500);

					var ag_sample_template = new Ext.XTemplate(
						'<tpl for=".">',
							'<div class="thumb-wrap" style="{style}" id="contents_{id}" ext:qtip="{shortName}">',
								'<table cellpadding=0 cellspacing=0><tr><td ext:qtip="{shortName}">',
									'<div class="thumb" style="background:{bgColor};float:left;" ext:qtip="{shortName}">',
										'<img src="{src}" alt="{name}" width="60" height="60" ext:qtip="{shortName}">',
									'</div>',
								'</td><td valign="top" align="left" ext:qtip="{shortName}">',
									'<span ext:qtip="{shortName}">{shortName}</span>',
								'</td></tr></table>',
							'</div>',
						'</tpl>',
						{
							isEmpty : function(val){
								return Ext.isEmpty(val);
							},
							isUPPath : function(val){
								return (!Ext.isEmpty(val) && val != 'ctg_' ? true : false);
							}
						}
					);
					ag_sample_template.compile();

					var ag_sample_images_store = new Ext.data.JsonStore({
						url: 'get-savecontents.cgi',
						baseParams    : {
							parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
							lng    : gParams.lng,
							type   : 'sample'
						},
						pruneModifiedRecords : true,
						root: 'images',
						fields: [
							'id',
							'name',
							'src',
							'partslist',
							'baseparam',
							'anatomoprm',
							'cameraprm',
							'environment'
						],
						listeners: {
							'beforeload' : {
								fn:function(self,options){
									self.baseParams = self.baseParams || {};
//									for(var key in self.baseParams){
//										_dump("ag_sample_images_store:"+key+"=["+self.baseParams[key]+"]");
//									}
								},
								scope:this
							},
							'load': {
								fn:function(self,records,options){
								},
								scope:this,
								single:true
							},
							'datachanged':{
								fn:function(self){
								},scope:this},
							'loadexception': {
								fn:function(){
								},scope:this
							}
						}
					});
					ag_sample_images_store.load();

					var ag_sample_formatData = function(data){
						data.shortName = null;
						if(data.name) data.shortName = data.name.ellipse(get_ag_lang('SORTNAME_LENGTH'));
						data.bgColor = "#dddddd";
						return data;
					};

					var ag_sample_formatTimestamp = function(val){
						return new Date(val).format(bp3d.defaults.TIME_FORMAT);
					}

					var ag_sample_onLoadException = function(v,o){
						var element = view_images.getEl();
						if(element) element.update('<div style="padding:10px;">Error loading images.</div>'); 
					};

					var ag_sample_dataview = new Ext.DataView({
						id           : 'ag-sample-dataview',
						tpl          : ag_sample_template,
						singleSelect : true,
						overClass    : 'x-view-over',
						autoShow     : false,
						itemSelector : 'div.thumb-wrap',
						multiSelect  : false,
						emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_ICON')+'</div>',
						store        : ag_sample_images_store,
						listeners: {
							'selectionchange': {
								fn:function(view,selections){
									if(!selections || selections.length == 0) return;
									var checked = false;
									try{checked = Ext.getCmp('ag-command-sample-latest-version-check').getValue()}catch(e){}
									loadSaveData(view.getRecord(selections[0]).copy(),checked);
								},
								scope:this
							},
							'loadexception'  : {fn:ag_sample_onLoadException, scope:this},
							'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}},
							'click'          : {fn:function(view,index,node,e){},scope:this, buffer:0},
							'beforeclick'    : {fn:function(view,index,node,e){},scope:this, buffer:0},
							'dblclick'       : {fn:function(view,index,node,e){},scope:this, buffer:0}
						},
						prepareData: ag_sample_formatData.createDelegate(this)
					});

					panel.add(ag_sample_dataview);
				}
			}
		}


HTML
if($lsdb_OpenID && 0){
	print <<HTML
		,{
			hidden     : $savePanelHidden,
			title      : 'Save',
			id         : 'ag-command-usersave-panel',
			border     : false,
			autoScroll : false,
			bodyStyle  : 'overflow-y:auto;',
			tbar : [
				new Ext.form.Checkbox({
					ctCls : 'x-small-editor',
					id : 'ag-command-usersave-latest-version-check',
					boxLabel : 'Latest version',
					checked: true,
					listeners: {
						'render': function(checkbox){
						},
						scope:this
					}
				})
				,'->',
				'-',
				{
					id   : 'ag-command-usersave-panel-save-button',
					tooltip : 'Save',
					iconCls : 'sample_save',
					listeners : {
						'click' : {
							fn : function (button, e) {
								var records = ag_parts_gridpanel.getStore().getRange();
								if(records.length == 0) return;

								var tg_id = undefined;
								var tg_model = undefined;
								try{
									tg_id = Ext.getCmp('anatomo-tree-group-combo').getValue();
									if(tg_id && tg2model[tg_id] && tg2model[tg_id].tg_model) tg_model = tg2model[tg_id].tg_model;
								}catch(e){_dump(e);}

								var objs = {
									baseparam  : ag_param_store.getAt(0).data,
									partslist  : [],
									anatomoprm : Ext.urlDecode(makeAnatomoPrm(),true),
									cameraprm  : {
										m_ag.cameraPos : m_ag.cameraPos,
										m_ag.targetPos : m_ag.targetPos,
										m_ag.upVec     : m_ag.upVec,
										m_ag.longitude : m_ag.longitude,
										m_ag.latitude  : m_ag.latitude,
										m_ag.distance  : m_ag.distance
									},
									environment : {
										rotate : {
											H : getRotateHorizontalValue(),
											V : getRotateVerticalValue()
										},
										zoom : Ext.getCmp("zoom-value-text").getValue(),
										tg_id : tg_id,
										model : tg_model,
										bp3dversion : Ext.getCmp("anatomo-version-combo").getValue(),
										treename : Ext.getCmp("bp3d-tree-type-combo").getValue(),
										size : {
											width  : Ext.getCmp("anatomo-width-combo").getValue(),
											height : Ext.getCmp("anatomo-height-combo").getValue()
										},
										bgcolor : Ext.getCmp("anatomo-bgcp").getValue(),
										bgtransparent : Ext.getCmp("anatomo-bgcolor-transparent-check").getValue(),
										colormap : {
											max  : Ext.getCmp("scalar-max-textfield").getValue(),
											min  : Ext.getCmp("scalar-min-textfield").getValue(),
											bar  : Ext.getCmp("show-colorbar-check").getValue()
										}
									}
								};
								if(Ext.getCmp("anatomo-clip-check").getValue()){
									var src = Ext.getDom("clipImg").getAttribute("src");
									var clipprm = Ext.urlDecode(src.substr(src.indexOf("?")+1),true);
									objs.environment.clip = {
										method : Ext.getCmp("anatomo-clip-method-combo").getValue(),
										predifined : Ext.getCmp("anatomo-clip-predifined-plane").getValue(),
										fix : Ext.getCmp("anatomo-clip-fix-check").getValue(),
										reverse : Ext.getCmp("anatomo-clip-reverse-check").getValue(),
										value : Ext.getCmp("anatomo-clip-value-text").getValue(),
										clipprm : clipprm
									};
								}

								for(var i=0;i<records.length;i++){
									if(records[i].data.constructor===Array) continue;
									objs.partslist.push(records[i].data);
								}

								var save_form = new Ext.form.FormPanel({
									baseCls     : 'x-plain',
									defaultType : 'textfield',
									defaults    : {
										selectOnFocus : true
									},
									labelWidth  : 50,
									layoutConfig: {
										// layout-specific configs go here
										labelSeparator: ''
									},
									items       : [{
										xtype      : 'hidden',
										name       : 'type',
										value      : 'user'
									},{
										xtype      : 'hidden',
										name       : 'param',
										value      : Ext.util.JSON.encode(objs)
									},{
										fieldLabel : 'Title',
										name       : 'title',
										allowBlank : false,
										anchor     : '100%'
									},{
										fieldLabel : 'Options',
										boxLabel   : 'Qualified',
										name       : 'qualified',
										xtype      : 'checkbox',
										checked    : true
									},{
										boxLabel   : 'Description',
										name       : 'description',
										xtype      : 'checkbox',
										checked    : true
									},{
										boxLabel   : 'Display environment',
										name       : 'environment',
										xtype      : 'checkbox',
										checked    : true
									}]
								});

								var save_window = new Ext.Window({
									title       : 'Save',
									width       : 250,
									height      : 200,
									plain       : true,
									bodyStyle   : 'padding:5px;',
									buttonAlign : 'center',
									defaultButton : 0,
									modal         : true,
									resizable     : false,
									items         : save_form,
									buttons : [{
										text    : 'Save',
										handler : function(){
											if(save_form.getForm().isValid()){
												save_form.getForm().submit({
													url     : 'put-savecontents.cgi',
													waitMsg : 'Wait...',
													success : function(fp, o){
														try{
															if(o.result.success == true){
																Ext.MessageBox.show({
																	title   : 'Save',
																	msg     : 'OK',
																	buttons : Ext.MessageBox.OK,
																	icon    : Ext.MessageBox.INFO,
																	fn      : function(){
																		save_window.close();
																		var cmp = Ext.getCmp('ag-usersave-dataview');
																		if(cmp) cmp.initialConfig.store.reload();
																	}
																});
																return;
															}
														}catch(e){ _dump("success():"+ e + ""); }

														Ext.MessageBox.show({
															title   : 'Save',
															msg     : 'ERROR:'+o.result.msg,
															buttons : Ext.MessageBox.OK,
															icon    : Ext.MessageBox.ERROR
														});

													},
													failure : function(fp, o){
														Ext.MessageBox.show({
															title   : 'Save',
															msg     : 'ERROR',
															buttons : Ext.MessageBox.OK,
															icon    : Ext.MessageBox.ERROR
														});
													}
												});
											}
										}
									},{
										text    : 'Cancel',
										handler : function(){
											save_window.close();
										}
									}]
								});
								save_window.show();
							},
							scope: this
						}
					}
				},
				'-',
				{
					id : 'ag-command-usersave-panel-delete-button',
					tooltip : 'Delete',
					iconCls : 'sample_delete',
					listeners : {
						'click' : {
							fn : function (button, e) {
								var view = Ext.getCmp('ag-usersave-dataview');
								var records = view.getSelectedRecords();
								if(!records || records.length == 0) return;
								Ext.MessageBox.show({
									title   : 'Delete',
									msg     : 'Delete ['+records[0].data.name+']?',
									buttons : Ext.MessageBox.YESNO,
									icon    : Ext.MessageBox.QUESTION,
									fn:function(btn){
										if(btn != 'yes') return;
										var delobjs = {
											id     : records[0].data.id,
											parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
											lng    : gParams.lng,
											type   : 'user'
										};
										Ext.Ajax.request({
											url     : 'del-savecontents.cgi',
											method  : 'POST',
											params  : Ext.urlEncode(delobjs),
											success : function(conn,response,options){
												try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
												if(!results || results.success == false){
													Ext.MessageBox.show({
														title   : 'Delete',
														msg     : 'ERROR'+(results && results.msg ? " ["+results.msg+"]" : ""),
														buttons : Ext.MessageBox.OK,
														icon    : Ext.MessageBox.ERROR
													});
												}
												var cmp = Ext.getCmp('ag-usersave-dataview');
												if(cmp) cmp.initialConfig.store.reload();
											},
											failure : function(conn,response,options){
												Ext.MessageBox.show({
													title   : 'Delete',
													msg     : 'ERROR',
													buttons : Ext.MessageBox.OK,
													icon    : Ext.MessageBox.ERROR
												});
												var cmp = Ext.getCmp('ag-usersave-dataview');
												if(cmp) cmp.initialConfig.store.reload();
											}
										});
									}
								});
							},
							scope: this
						}
					}
				}
			],
			listeners: {
				'beforerender': function(panel){
				},
				'render': function(panel){
					var ag_usersave_template = new Ext.XTemplate(
						'<tpl for=".">',
							'<div class="thumb-wrap" style="{style}" id="contents_{id}" ext:qtip="{shortName}">',
								'<table cellpadding=0 cellspacing=0><tr><td ext:qtip="{shortName}">',
								'<div class="thumb" style="background:{bgColor};float:left;" ext:qtip="{shortName}">',
									'<img src="{src}" alt="{name}" width="60" height="60" ext:qtip="{shortName}">',
								'</div>',
								'</td><td valign="top" ext:qtip="{shortName}">',
								'<span ext:qtip="{shortName}">{shortName}</span>',
								'</td></tr></table>',
							'</div>',
						'</tpl>',
						{
							isEmpty : function(val){
								return Ext.isEmpty(val);
							},
							isUPPath : function(val){
								return (!Ext.isEmpty(val) && val != 'ctg_' ? true : false);
							}
						}
					);
					ag_usersave_template.compile();

					var ag_usersave_images_store = new Ext.data.JsonStore({
						url: 'get-savecontents.cgi',
						baseParams    : {
							parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
							type   : 'user',
							lng    : gParams.lng
						},
						pruneModifiedRecords : true,
						root: 'images',
						fields: [
							'id',
							'name',
							'src',
							'partslist',
							'baseparam',
							'anatomoprm',
							'cameraprm',
							'environment'
						],
						listeners: {
							'beforeload' : {
								fn:function(self,options){
									self.baseParams = self.baseParams || {};
//									for(var key in self.baseParams){
//										_dump("ag_usersave_images_store:"+key+"=["+self.baseParams[key]+"]");
//									}
								},
								scope:this
							},
							'load': {
								fn:function(self,records,options){
								},
								scope:this,
								single:true
							},
							'datachanged':{
								fn:function(self){
								},scope:this},
							'loadexception': {
								fn:function(){
								},scope:this
							}
						}
					});
					ag_usersave_images_store.load();

					var ag_usersave_formatData = function(data){
						if(data.is_a == undefined) data.is_a = null;
						data.shortName = null;
						if(data.name) data.shortName = data.name.ellipse(get_ag_lang('SORTNAME_LENGTH'));
						data.dateString = ag_usersave_formatTimestamp(data.entry);

						data.bgColor = "#dddddd";
						if(data.phy_id){
							if(data.phy_id == 1){
								data.bgColor = "#ffcccc";
							}else if(data.phy_id == 2){
								data.bgColor = "#ccffff";
							}
						}

						return data;
					};

					var ag_usersave_formatTimestamp = function(val){
						return new Date(val).format(bp3d.defaults.TIME_FORMAT);
					}

					var ag_usersave_onLoadException = function(v,o){
						var element = view_images.getEl();
						if(element) element.update('<div style="padding:10px;">Error loading images.</div>'); 
					};

					var ag_usersave_dataview = new Ext.DataView({
						id           : 'ag-usersave-dataview',
						tpl          : ag_usersave_template,
						singleSelect : true,
						overClass    : 'x-view-over',
						autoShow     : false,
						itemSelector : 'div.thumb-wrap',
						style        : 'overflow:auto',
						multiSelect  : false,
						emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_ICON')+'</div>',
						store        : ag_usersave_images_store,
						listeners: {
							'selectionchange': {
								fn:function(view,selections){
									if(!selections || selections.length == 0) return;
									loadSaveData(view.getRecord(selections[0]).copy(),Ext.getCmp('ag-command-usersave-latest-version-check').getValue());
								},
								scope:this
							},
							'loadexception'  : {fn:ag_usersave_onLoadException, scope:this},
							'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}},
							'click'          : {fn:function(view,index,node,e){},scope:this, buffer:0},
							'beforeclick'    : {fn:function(view,index,node,e){},scope:this, buffer:0},
							'dblclick'       : {fn:function(view,index,node,e){},scope:this, buffer:0}
						},
						prepareData: ag_usersave_formatData.createDelegate(this)
					});

					panel.add(ag_usersave_dataview);
				}
			}
		}
HTML
}
print <<HTML;
		]
	});

	var ag_image_control_panel = new Ext.Panel({
		id         : 'ag-image-control-panel',
		autoScroll : false,
		bodyBorder : false,
		boder      : false,
		region     : 'west',
		width      : 162,
		minWidth   : 162,
		maxWidth   : 162,
		layout     : 'border',
//		split      : true,
		header        : controlPanelCollapsible,
		titleCollapse : controlPanelCollapsible,
		collapsible   : controlPanelCollapsible,
		items      : [{
			id: 'ag-image-control-north-panel',
			region: 'north',
			height: 110,
			border: false,
			frame: false,
			bodyStyle: 'border-width:0 1px 0 0;background:transparent;',
			html:'<table cellpadding=0 cellspacing=0 align="center"><tr><td><a class="goto-bp3d-btn" href="#"><img src="css/goto_bp3d.png"></a></td></tr></table>',
			listeners  : {
				render: function(comp){
					\$('a.goto-bp3d-btn').live('click',function(){
						Ext.getCmp('contents-tab-panel').activate(Ext.getCmp('contents-tab-bodyparts-panel'));
						return false;
					});
					Ext.getCmp('contents-tab-panel').on({
						tabchange: {
							fn: function(tabpanel,tab){
								if(tab.id != 'contents-tab-anatomography-panel') return;
								comp.setHeight(comp.initialConfig.height);
								comp.findParentByType('panel').doLayout();
							},
							buffer: 250
						}
					});
				},
				scope:this
			}
		},ag_image_control_center_panel],
		listeners  : {
			'show' : function(panel){
				panel.doLayout();
			},
			'afterlayout' : function(panel,layout){
				afterLayout(panel);
			},
			render: function(comp){
			},
			scope:this
		}
	});


	var anatomography_point_editorgrid_panel = new Ext.grid.EditorGridPanel({
		id             : 'anatomography-point-editorgrid-panel',
		header         : false,
		region         : 'center',
		ddGroup        : 'partlistDD',
		enableDragDrop : true,
		border         : false,
		stripeRows     : true,
		columnLines    : true,
		maskDisabled   : true,
		plugins        : [
			anatomography_point_grid_partslist_checkColumn,
			anatomography_point_grid_zoom_checkColumn,
			anatomography_point_grid_exclude_checkColumn
HTML
if($lsdb_Auth && $addPointElementHidden ne 'true'){
	print <<HTML;
			,anatomography_point_grid_point_checkColumn
HTML
}
print <<HTML;
		],
		clicksToEdit   : 1,
		trackMouseOver : true,
		selModel       : new Ext.grid.RowSelectionModel({singleSelect:true}),
		ds: anatomography_point_grid.ds,
		cm: anatomography_point_grid.cm,
		enableColLock: false,
		loadMask: true,
		viewConfig: {
			deferEmptyText: false,
			emptyText: '<div class="bp3d-pallet-empty-message">'+get_ag_lang('CLICK_IMAGE_GRID_EMPTY_MESSAGE')+'</div>'
		},
		listeners : {
			"beforeedit" : function(e){
				if(e.field == 'partslist'){
//					e.cancel = (Ext.isEmpty(e.record.get('zmax'))||(!isAdditionPartsList())?true:false);
					e.cancel = (isNoneDataRecord(e.record)||(!isAdditionPartsList())?true:false);
				}else{
					e.cancel = !e.record.get('partslist');
				}
				if(!e.cancel) e.grid._edit = e;
			},
			"afteredit" : function(e){
				e.record.commit();
//				e.grid._edit = undefined;
				if(e.field == 'partslist'){
					if(e.value){
						bp3d_parts_store.add(e.record.copy());
					}else{
						var record = null;
						var index = bp3d_parts_store.find('f_id',new RegExp("^"+e.record.get('f_id')+"\$"));
						if(index>=0) record = bp3d_parts_store.getAt(index);
						if(record) bp3d_parts_store.remove(record);
					}
				}else{
					var record = null;
					var regexp = new RegExp("^"+e.record.get('f_id')+"\$");
					var index = bp3d_parts_store.find('f_id',regexp);
					if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
					if(index>=0) record = bp3d_parts_store.getAt(index);
					if(record){
						record.set(e.field,e.record.get(e.field));
						record.commit();
					}
				}
			},
			"complete": function(comp,row,col){
				comp.view.focusRow(row);
			},
			"resize" : function(grid){
				resizeGridPanelColumns(grid);
			},
			"render" : function(grid){
				restoreHiddenGridPanelColumns(grid);
			},
			scope : this
		}
	});
	anatomography_point_editorgrid_panel.getColumnModel().on({
		'hiddenchange' : function(column,columnIndex,hidden){
			var editorgrid = Ext.getCmp('anatomography-point-editorgrid-panel');
			resizeGridPanelColumns(editorgrid);
			saveHiddenGridPanelColumns(editorgrid);
		},
		scope: this,
		delay: 100
	});

	var anatomography_point_grid_header_panel = new Ext.Panel({
		contentEl : 'ag-point-grid-content',
		region    : 'north',
		height    : 41,
		minHeight : 41,
		maxHeight : 41,
		border    : false,
		listeners : {
			"bodyresize": function(panel,adjWidth,adjHeight,rawWidth,rawHeight){
				if(adjWidth == undefined || !adjWidth) return;

				var table = Ext.get('ag-point-grid-content-table');
				if(table) table.setWidth(adjWidth);

//既に生成済みの場合、テーブル幅のみを更新
				if(Ext.get('anatomo_comment_point_toggle_partof')) return;

//通常は、render時に生成するがIEでテーブル幅が確定前に生成すると幅が不正確になる為、ここで生成する
				new Ext.form.ComboBox ({
					renderTo : 'ag-comment-point-type-render',
					id: 'anatomo-tree-type-combo',
					xtype: 'combo',
					typeAhead: true,
					triggerAction: 'all',
					width: 140,
					editable: false,
					mode: 'local',
					lazyInit: false,
					disabled : true,
					displayField: 't_name',
					valueField: 't_type',
					store : new Ext.data.JsonStore({
						url:'get-tree_type.cgi',
						totalProperty : 'total',
						root: 'records',
						fields: [
							't_type',
							't_name'
						],
						baseParams : {
							parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
							lng    : gParams.lng
						},
						listeners: {
							'beforeload' : function(self,options){
								self.baseParams = self.baseParams || {};
								delete self.baseParams.version;
								try{self.baseParams.version = Ext.getCmp('anatomo-version-combo').getValue();}catch(e){}

								var cmp = Ext.getCmp('anatomo-tree-type-combo');
								if(cmp && cmp.rendered) cmp.disable();

								for(var key in init_bp3d_params){
									if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
								}

								try{
									var store = Ext.getCmp('anatomo-version-combo').getStore();
									var idx = store.findBy(function(record,id){
										if(record.data.tgi_version==self.baseParams.version) return true;
									});
									if(idx>=0){
										var record = store.getAt(idx);
										if(record){
											self.baseParams.md_id = record.data.md_id;
											self.baseParams.mv_id = record.data.mv_id;
											self.baseParams.mr_id = record.data.mr_id;
											self.baseParams.ci_id = record.data.ci_id;
											self.baseParams.cb_id = record.data.cb_id;
										}
									}
								}catch(e){}
							},
							'load' : function(self,records,options){
								var cmp = Ext.getCmp('anatomo-tree-type-combo');
								if(cmp && cmp.rendered){
									if(records.length>0){
										cmp.enable();
										cmp.setValue(records[0].get('t_type'));
										cmp.fireEvent('select',cmp,records[0],0);
									}
								}
							},
							scope:this
						}
					}),
					listeners: {
						'select': function(combo,record,index){

							var record = Ext.getCmp('anatomography-point-editorgrid-panel').getSelectionModel().getSelected();
							if(record){

								Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.show();
								var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
								loader.removeAll();
								loader.baseParams = {};
								var elem = Ext.getDom('ag-point-grid-content-route');
								if(elem) elem.innerHTML = '&nbsp;';

								var cmp = Ext.getCmp('anatomo-tree-type-combo');
								if(cmp && cmp.rendered){
									var type = cmp.getValue();
									if(Ext.getCmp('anatomo_comment_point_toggle_partof').pressed){
										if(type == '4'){
											loader = anatomography_point_partof_store;
										}else if(type == '3'){
											loader = anatomography_point_isa_store;
										}else if(type == '1'){
											loader = anatomography_point_conventional_root_store;
										}
									}else if(Ext.getCmp('anatomo_comment_point_toggle_haspart').pressed){
										if(type == '4'){
											loader = anatomography_point_haspart_store;
										}else if(type == '3'){
											loader = anatomography_point_hasmember_store;
										}else if(type == '1'){
											loader = anatomography_point_conventional_child_store;
										}
									}
								}
								if(loader){
									loader.baseParams = loader.baseParams || {};
									loader.baseParams.f_id = record.data.f_id;
									loader.load();
								}else{
									var loader = Ext.getCmp('anatomography-point-editorgrid-panel').getStore();
									loader.removeAll();
									loader.baseParams = {};
									var elem = Ext.getDom('ag-point-grid-content-route');
									if(elem) elem.innerHTML = '&nbsp;';
									Ext.getCmp('anatomography-point-editorgrid-panel').loadMask.hide();
									Ext.getCmp('ag-parts-gridpanel').loadMask.hide();
								}
							}

						},
						'render': function(combo){
							combo.getStore().load();
						},
						scope:this
					}
				});

				new Ext.Toolbar.Button({
					renderTo     : 'ag-comment-point-toggle-partof-render',
					id : 'anatomo_comment_point_toggle_partof',
					enableToggle : true,
					toggleGroup  : 'anatomo_comment_point_toggle',
					pressed      : true,
					text         : 'Path to Root',
					listeners : {
						'click' : {
							fn : function(button) {
								if(!button.pressed) button.toggle(true);
								var record = Ext.getCmp('anatomography-point-editorgrid-panel').getSelectionModel().getSelected();
								if(record){
									var loader = null;
									var cmp = Ext.getCmp('anatomo-tree-type-combo');
									if(cmp && cmp.rendered){
										var type = cmp.getValue();
										if(type == '4'){
											loader = anatomography_point_partof_store;
										}else if(type == '3'){
											loader = anatomography_point_isa_store;
										}else if(type == '1'){
											loader = anatomography_point_conventional_root_store;
										}
									}

									if(loader){
										loader.baseParams = loader.baseParams || {};
										loader.baseParams.f_id = record.data.f_id;
										loader.load();
									}
								}
							},
							scope : this
						},
						'toggle' : {
							fn : function(button, pressed) {
							},
							scope : this
						}
					}
				});

				new Ext.Toolbar.Button({
					renderTo     : 'ag-comment-point-toggle-haspart-render',
					id : 'anatomo_comment_point_toggle_haspart',
					enableToggle : true,
					toggleGroup  : 'anatomo_comment_point_toggle',
					text : 'Children',
					listeners : {
						'click' : {
							fn : function(button) {
								if(!button.pressed) button.toggle(true);
								var record = Ext.getCmp('anatomography-point-editorgrid-panel').getSelectionModel().getSelected();
								if(record){
									var loader = null;
									var cmp = Ext.getCmp('anatomo-tree-type-combo');
									if(cmp && cmp.rendered){
										var type = cmp.getValue();
										if(type == '4'){
											loader = anatomography_point_hasmember_store;
										}else if(type == '3'){
											loader = anatomography_point_haspart_store;
										}else if(type == '1'){
											loader = anatomography_point_conventional_child_store;
										}
									}
									if(loader){
										loader.baseParams = loader.baseParams || {};
										loader.baseParams.f_id = record.data.f_id;
										loader.load();
									}
								}
							},
							scope : this
						},
						'toggle' : {
							fn : function(button, pressed) {
							},
							scope : this
						}
					}
				});
/*
				new Ext.Toolbar.Button({
					renderTo     : 'ag-comment-point-toggle-isa-render',
					id : 'anatomo_comment_point_toggle_isa',
					enableToggle : true,
					toggleGroup  : 'anatomo_comment_point_toggle',
					text : 'Path to Root',
					listeners : {
						'click' : {
							fn : function(button) {
								if(!button.pressed) button.toggle(true);
								var record = Ext.getCmp('anatomography-point-editorgrid-panel').getSelectionModel().getSelected();
								if(record){
									var loader = anatomography_point_isa_store;
									if(loader){
										loader.baseParams = loader.baseParams || {};
										loader.baseParams.f_id = record.data.f_id;
										loader.load();
									}
								}
							},
							scope : this
						},
						'toggle' : {
							fn : function(button, pressed) {
							},
							scope : this
						}
					}
				});

				new Ext.Toolbar.Button({
					renderTo     : 'ag-comment-point-toggle-hasmember-render',
					id : 'anatomo_comment_point_toggle_hasmember',
					enableToggle : true,
					toggleGroup  : 'anatomo_comment_point_toggle',
					text : 'Children',
					listeners : {
						'click' : {
							fn : function(button) {
								if(!button.pressed) button.toggle(true);
								var record = Ext.getCmp('anatomography-point-editorgrid-panel').getSelectionModel().getSelected();
								if(record){
									var loader = anatomography_point_hasmember_store;
									if(loader){
										loader.baseParams = loader.baseParams || {};
										loader.baseParams.f_id = record.data.f_id;
										loader.load();
									}
								}
							},
							scope : this
						},
						'toggle' : {
							fn : function(button, pressed) {
							},
							scope : this
						}
					}
				});
*/
			},
			"render": function(panel){

				new Ext.Toolbar.Button({
					id : 'anatomo_comment_point_button',
					enableToggle : true,
					text : 'Pick',
					hidden : true,
					listeners : {
						'toggle' : {
							fn : function(button, pressed) {
								anatomoPointMode = pressed;
								if(pressed) Ext.getCmp('anatomo_comment_pick_button').toggle(false);
							},
							scope : this
						}
					}
				});
			},
			scope : this
		}
	});

	var ag_point_grid_footer_panel = new Ext.Panel({
		contentEl : 'ag-point-grid-footer-content',
		region    : 'south',
		height    : 52,
		minHeight : 52,
		maxHeight : 52,
		border    : false,
		bodyStyle : 'border-top-width:1px;',
		listeners : {
			"bodyresize": function(panel,adjWidth,adjHeight,rawWidth,rawHeight){
				if(adjWidth == undefined || !adjWidth) return;

				var table = Ext.get('ag-point-grid-footer-content-table');
				if(table) table.setWidth(adjWidth);

//既に生成済みの場合、テーブル幅のみを更新
				if(Ext.get('anatomography-point-grid-bbar-tx-text')) return;

				new Ext.form.NumberField({
					id       : 'anatomography-point-grid-bbar-tx-text',
					renderTo : 'ag-point-grid-footer-content-coordinate-x-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'anatomography-point-grid-bbar-ty-text',
					renderTo : 'ag-point-grid-footer-content-coordinate-y-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'anatomography-point-grid-bbar-tz-text',
					renderTo : 'ag-point-grid-footer-content-coordinate-z-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});

				new Ext.form.NumberField({
					id       : 'ag-point-grid-footer-content-distance-x-text',
					renderTo : 'ag-point-grid-footer-content-distance-x-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'ag-point-grid-footer-content-distance-y-text',
					renderTo : 'ag-point-grid-footer-content-distance-y-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'ag-point-grid-footer-content-distance-z-text',
					renderTo : 'ag-point-grid-footer-content-distance-z-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'anatomography-point-grid-bbar-distance-text',
					renderTo : 'ag-point-grid-footer-content-distance-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
			}
		}
	});

	var ag_point_grid_panel = new Ext.Panel({
		id     : 'anatomography-point-grid-panel',
		header : false,
		title  : 'Pick',
		layout : 'border',
		border : false,
		items  : [
			Ext.getCmp('anatomography-point-editorgrid-panel'),
			anatomography_point_grid_header_panel,
			ag_point_grid_footer_panel
		],
		listeners  : {
			'show' : function(panel){
				panel.doLayout();
			},
			'afterlayout' : function(panel,layout){
				afterLayout(anatomography_point_grid_header_panel);
				afterLayout(panel);
			},
			scope:this
		}
	});

	function ag_point_search_renderer(value,metadata,record,rowIndex,colIndex,store){

		var dataIndex = ag_point_search_cols[colIndex].dataIndex;
		var item;
		for(var i=0;i<record.fields.length;i++){
			if(record.fields.keys[i] != dataIndex) continue;
			item = record.fields.items[i];
			break;
		}

		if(item){
			if(item.type == 'date'){
				if(dataIndex == 'entry' && value) value = new Date(value).format(bp3d.defaults.DATE_FORMAT);
				if(dataIndex == 'lastmod' && value) value = new Date(value).format(bp3d.defaults.TIME_FORMAT);
			}else if(item.type == 'float'){
				if(!Ext.isEmpty(value)) value = Math.round(parseFloat(value)*1000)/1000;
			}
		}

		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return value;
	}

	function ag_point_search_partslist_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
		var id = Ext.getCmp('ag-point-search-editorgrid-panel').getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td'; 
		if(isNoneDataRecord(record)) metadata.css += ' ag_point_none_data'; 
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data';
		if(record.data.seg_color) metadata.attr = 'style="background:'+record.data.seg_color+';"'
		if(isAdditionPartsList()){
			return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
		}else{
			return '<div class="ag_grid_checkbox'+(value?'-on':'')+'-dis x-grid3-cc-'+id+'">&#160;</div>';
		}
	}

	function ag_point_search_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
		var id = Ext.getCmp('ag-point-search-editorgrid-panel').getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td'; 
		if(isNoneDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}else{
			if(record.data.partslist){
			}else{
				metadata.css += ' ag_point_none_pallet_data'; 
			}
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
	}

	function ag_point_search_point_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
		var id = Ext.getCmp('ag-point-search-editorgrid-panel').getColumnModel().getColumnId(colIndex);
		metadata.css += ' x-grid3-check-col-td'; 
		if(isNoneDataRecord(record) || isPointDataRecord(record)){
			metadata.css += ' ag_point_none_data'; 
		}else{
			if(record.data.partslist){
			}else{
				metadata.css += ' ag_point_none_pallet_data'; 
			}
		}
		if(store.baseParams && store.baseParams.f_id && store.baseParams.f_id == record.data.f_id) metadata.css += ' ag_point_data'; 
		return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
	}

	var ag_point_search_col_version = {
		dataIndex:'version',
		header:'Version',
		id:'version',
		sortable: false,
		renderer: ag_point_search_renderer,
		hidden:true
	};
	var ag_point_search_col_rep_id = {
		dataIndex:'b_id',
		header:get_ag_lang('REP_ID'),
		renderer: ag_point_search_renderer,
		id:'b_id'
	};
	var ag_point_search_col_cdi_name = {
		dataIndex:'f_id',
		header:get_ag_lang('CDI_NAME'),
		renderer: ag_point_search_renderer,
		id:'f_id'
	};

	var ag_point_search_col_value = {
		dataIndex : 'value',
		header    : 'Value',
		id        : 'value',
		width     : 40,
		resizable : false,
		renderer  : ag_point_search_renderer,
		hidden    : true,
		editor    : new Ext.form.TextField({
			allowBlank : true
		})
	};
	var ag_point_search_col_organsys = {
		dataIndex:'organsys',
		header:get_ag_lang('GRID_TITLE_ORGANSYS'),
		renderer: ag_point_search_renderer,
		id:'organsys',
		hidden:true
	};
	var ag_point_search_col_entry = {
		dataIndex:'entry',
		header:get_ag_lang('GRID_TITLE_MODIFIED'),
		renderer: ag_point_search_renderer,
		id:'entry',
		hidden:true
	};

	var ag_point_search_col_color = {
		dataIndex : 'color',
		header    : 'Color',
		id        : 'color',
		width     : 40,
		resizable : false,
		renderer  : anatomography_point_grid_color_cell_style,
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
		editor    : new Ext.ux.ColorPickerField({
			menuListeners : {
				select: function(e, c){
					this.setValue(c);
					try{var record = Ext.getCmp('ag-point-search-editorgrid-panel')._edit.record;}catch(e){_dump("color:"+e);}
					if(record){
						record.beginEdit();
						record.set('color',"#"+c);
						record.commit();
						record.endEdit();

						var grid = Ext.getCmp('ag-parts-gridpanel');
						var store = grid.getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"\$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('color',"#"+c);
							record.commit();
						}
					}
				},
				show : function(){ // retain focus styling
					this.onFocus();
				},
				hide : function(){
					this.focus.defer(10, this);
				},
				beforeshow : function(menu) {
					try {
						if (this.value != "") {
							menu.palette.select(this.value);
						} else {
							this.setValue("");
							var el = menu.palette.el;
							if(menu.palette.value){
								try{el.child("a.color-"+menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
								menu.palette.value = null;
							}
						}
					}catch(ex){}
				}
			}
		})
HTML
}else{
	print <<HTML;
		editor    : new Ext.ux.ColorField({
			listeners : {
				select: function(e, c){
					this.setValue(c);
					try{var record = Ext.getCmp('ag-point-search-editorgrid-panel')._edit.record;}catch(e){_dump("color:"+e);}
					if(record){
						record.beginEdit();
						record.set('color',"#"+c);
						record.commit();
						record.endEdit();

						var grid = Ext.getCmp('ag-parts-gridpanel');
						var store = grid.getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"\$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('color',"#"+c);
							record.commit();
						}
					}
				}
			}
		})
HTML
}
print <<HTML;
	};

	var ag_point_search_col_opacity = {
		dataIndex : 'opacity',
		header    : 'Opacity',
		id        : 'opacity',
		width     : 50,
		resizable : false,
		align     : 'right',
		renderer: anatomography_point_grid_combobox_renderer,
		editor    : new Ext.form.ComboBox({
			typeAhead     : true,
			triggerAction : 'all',
			store         : anatomography_point_grid_col_opacity_arr,
			lazyRender    : true,
			listClass     : 'x-combo-list-small',
			listeners     : {
				'select' : function(combo,record,index){
					try{var record = Ext.getCmp('ag-point-search-editorgrid-panel')._edit.record;}catch(e){_dump("opacity:"+e);}
					if(record){
						record.beginEdit();
						record.set('opacity',combo.getValue());
						record.commit();
						record.endEdit();

						var store = Ext.getCmp('ag-parts-gridpanel').getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"\$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('opacity',combo.getValue());
							record.commit();
						}
					}
				},
				scope : this
			}
		})
	};
	var ag_point_search_col_representation = {
		dataIndex : 'representation',
		header    : get_ag_lang('ANATOMO_REP_LABEL'),
		id        : 'representation',
		width     : 40,
		resizable : false,
		renderer  : anatomography_point_grid_combobox_renderer,
		hidden    : true,
		hideable  : true,
		editor    : new Ext.form.ComboBox({
			typeAhead     : true,
			triggerAction : 'all',
			store         : anatomography_point_grid_col_representation_arr,
			lazyRender    : true,
			listClass     : 'x-combo-list-small',
			listeners     : {
				'select' : function(combo,record,index){
					try{var record = Ext.getCmp('ag-point-search-editorgrid-panel')._edit.record;}catch(e){_dump("representation:"+e);}
					if(record){
						record.beginEdit();
						record.set('representation',combo.getValue());
						record.commit();
						record.endEdit();

						var store = Ext.getCmp('ag-parts-gridpanel').getStore();
						var f_id = record.get('f_id');
						var record = null;
						var regexp = new RegExp("^"+f_id+"\$");
						var index = store.find('f_id',regexp);
						if(index<0) index = store.find('conv_id',regexp);
						if(index>=0) record = store.getAt(index);
						if(record){
							record.set('representation',combo.getValue());
							record.commit();
						}
					}
				},scope : this
			}
		})
	};

	var ag_point_search_partslist_checkColumn = new Ext.grid.CheckColumn({
		header    : 'Pallet',
		dataIndex : 'partslist',
		width     : 40,
		fixed     : true,
		renderer  : ag_point_search_partslist_checkbox_renderer
	});
	var ag_point_search_zoom_checkColumn = new Ext.grid.CheckColumn({
		header    : "Zoom",
		dataIndex : 'zoom',
		hidden    : true,
		width     : 40,
		resizable : false,
		renderer  : ag_point_search_checkbox_renderer
	});

	var ag_point_search_exclude_checkColumn = new Ext.grid.CheckColumn({
		header    : "Remove",
		dataIndex : 'exclude',
		width     : 50,
		resizable : false,
		renderer  : ag_point_search_checkbox_renderer
	});

	var ag_point_search_point_checkColumn = new Ext.grid.CheckColumn({
		header    : 'Point',
		dataIndex : 'point',
		width     : 40,
		resizable : false,
		renderer  : ag_point_search_point_checkbox_renderer
	});

	var ag_point_search_cols = [
		ag_point_search_partslist_checkColumn,
		{dataIndex:'tg_id', header:'Model', id:'tg_id', sortable: false, renderer:anatomography_point_grid_group_renderer, hidden:true, fixed:$groupHidden},
		{dataIndex:'common_id',header:'UniversalID',               renderer: ag_point_search_renderer, id:'common_id',hidden:true, fixed:$gridColFixedUniversalID},
		{dataIndex:'name_j', header:get_ag_lang('GRID_TITLE_NAME_J'),  renderer: ag_point_search_renderer, id:'name_j', hidden:true},
		{dataIndex:'name_k', header:get_ag_lang('GRID_TITLE_NAME_K'),  renderer: ag_point_search_renderer, id:'name_k', hidden:true},
		{dataIndex:'name_e', header:get_ag_lang('GRID_TITLE_NAME_E'),renderer: ag_point_search_renderer, id:'name_e'},
		{dataIndex:'name_l', header:'Latina',                      renderer: ag_point_search_renderer, id:'name_l', hidden:true},

		ag_point_search_col_color,
		ag_point_search_col_opacity,
		ag_point_search_exclude_checkColumn,
		ag_point_search_col_value,
//		ag_point_search_col_organsys,
		ag_point_search_col_representation,
		ag_point_search_col_rep_id,
		ag_point_search_col_cdi_name,

		{dataIndex:'xmin',  header:'Xmin(mm)',                        renderer: ag_point_search_renderer, id:'xmin',     hidden:true},
		{dataIndex:'xmax',  header:'Xmax(mm)',                        renderer: ag_point_search_renderer, id:'xmax',     hidden:true},
		{dataIndex:'ymin',  header:'Ymin(mm)',                        renderer: ag_point_search_renderer, id:'ymin',     hidden:true},
		{dataIndex:'ymax',  header:'Ymax(mm)',                        renderer: ag_point_search_renderer, id:'ymax',     hidden:true},
		{dataIndex:'zmin',  header:'Zmin(mm)',                        renderer: ag_point_search_renderer, id:'zmin',     hidden:true},
		{dataIndex:'zmax',  header:'Zmax(mm)',                        renderer: ag_point_search_renderer, id:'zmax',     hidden:true},
		{dataIndex:'volume',header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', renderer: ag_point_search_renderer, id:'volume',   hidden:true},

		ag_point_search_col_version,
		ag_point_search_col_entry,
		{dataIndex:'distance',  header:'Distance(mm)',                renderer: ag_point_search_renderer, id:'distance', hidden:false}
	];

	ag_point_search_fields = [
		{name:'partslist'},
		{name:'common_id'},
		{name:'b_id'},
		{name:'f_id'},
		{name:'name_j'},
		{name:'name_e'},
		{name:'name_k'},
		{name:'name_l'},
		{name:'phase'},
		'version',
//		'tg_id',
//		'tgi_id',
		{name:'tg_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.md_id;
			}else{
				return v;
			}
		}},
		{name:'tgi_id',type:'int',convert:function(v,r){
			if(Ext.isEmpty(v)){
				return r.mv_id;
			}else{
				return v;
			}
		}},

		'segment',
		'seg_color',
		'seg_thum_bgcolor',
		'seg_thum_bocolor',

		{name:'entry',   type:'date', dateFormat: 'timestamp'},
		{name:'xmin',    type:'float'},
		{name:'xmax',    type:'float'},
		{name:'ymin',    type:'float'},
		{name:'ymax',    type:'float'},
		{name:'zmin',    type:'float'},
		{name:'zmax',    type:'float'},
		{name:'volume',  type:'float'},
		{name:'organsys'},
		{name:'color'},
		{name:'value'},
		{name:'zoom',type:'boolean'},
		{name:'exclude',type:'boolean'},
		{name:'opacity',type:'float'},
		{name:'representation'},
		{name:'point',type:'boolean'},
		{name:'elem_type'},
		{name:'def_color'},
		{name:'distance',type:'float'},
	];

	var ag_point_search = {
		ds : new Ext.data.SimpleStore({
			root   : 'records',
			fields : ag_point_search_fields,
			listeners : {
				"add" : function(store,records,index){
					var prm_record = ag_param_store.getAt(0);
					var bp3d_parts_store = ag_parts_gridpanel.getStore();

					//検索結果を全てパレットに追加する
//					var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
//					var newRecords = [];

					for(var i=0;i<records.length;i++){
						var partslist = false;
//						var partslist = true;//検索結果を全てパレットに追加する為、常にtrueにする
						var zoom = false;
						var exclude = false;
						var color = null;
						var opacity = "1.0";
						var representation = "surface";
						var value = "";
						var point = false;
						var elem_type = records[i].get('elem_type');
						var regexp = new RegExp("^"+records[i].get('f_id')+"\$");
						var index = bp3d_parts_store.find('f_id',regexp);
						if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
//						if(index<0){
//							newRecords.push(new newRecord(records[i].data));
//						}
						if(index>=0){
							partslist = true;
							var record = bp3d_parts_store.getAt(index);
							exclude = record.get('exclude');
							color = record.get('color');
							opacity = record.get('opacity');
							representation = record.get('representation');
							value = record.get('value');
							point = record.get('point');
						}else{
							if(!Ext.isEmpty(records[i].get('def_color'))) color = records[i].get('def_color');
						}
						records[i].beginEdit();
						records[i].set('partslist',partslist);
						records[i].set('zoom',zoom);
						records[i].set('exclude',exclude);
						records[i].set('color',color?color:'#'+ (elem_type=='bp3d_point'? prm_record.data.point_color_rgb:prm_record.data.color_rgb));
						records[i].set('opacity',opacity);
						records[i].set('representation',representation);
						records[i].set('value',value);
						records[i].set('conv_id',records[i].get('f_id'));
						records[i].set('point',point);
						records[i].commit(true);
						records[i].endEdit();
					}
//					if(newRecords.length>0) bp3d_parts_store.add(newRecords);

					if(store.baseParams && store.baseParams.f_id){
						var index = store.find('f_id',new RegExp("^"+ store.baseParams.f_id +"\$"));
						if(index>=0) Ext.getCmp('ag-point-search-editorgrid-panel').getSelectionModel().selectRow(index);
					}
				},
				"beforeload" : function(store,options){
				},
				"clear" : function(store){
				},
				"datachanged" : function(store){
				},
				"load" : function(store,records,options){
				},
				"loadexception" : function(){
				},
				"metachange" : function(store,meta){
				},
				"remove" : function(store,record,index){
				},
				"update" : function(store,record,operation){
				},
				scope : this
			}

		}),
		cm : new Ext.grid.ColumnModel(ag_point_search_cols)
	};


	var ag_point_search_editorgrid_panel = new Ext.grid.EditorGridPanel({
		id             : 'ag-point-search-editorgrid-panel',
		header         : false,
		region         : 'center',
		ddGroup        : 'partlistDD',
		enableDragDrop : true,
		border         : false,
		stripeRows     : true,
		columnLines    : true,
		maskDisabled   : true,
		plugins        : [
			ag_point_search_partslist_checkColumn,
			ag_point_search_zoom_checkColumn,
			ag_point_search_exclude_checkColumn
HTML
if($lsdb_Auth && $addPointElementHidden ne 'true'){
	print <<HTML;
			,ag_point_search_point_checkColumn
HTML
}
print <<HTML;
		],
		clicksToEdit   : 1,
		trackMouseOver : true,
		selModel       : new Ext.grid.RowSelectionModel({singleSelect:true}),
		ds: ag_point_search.ds,
		cm: ag_point_search.cm,
		enableColLock: false,
		loadMask: true,
		style : 'border-bottom-width:1px;',
		viewConfig: {
			deferEmptyText: true,
			emptyText: '<div class="bp3d-pallet-empty-message">'+get_ag_lang('NEIGHBOR_PARTS_GRID_EMPTY_MESSAGE')+'</div>'
		},
		bbar: [{
			xtype: 'tbfill'
		},{
			id: 'ag-point-search-editorgrid-bbar-text',
			xtype: 'tbtext',
			text: '- / -'
		}],
		listeners : {
			"beforeedit" : function(e){
				if(e.field == 'partslist'){
//					e.cancel = (Ext.isEmpty(e.record.get('zmax'))||(!isAdditionPartsList())?true:false);
					e.cancel = (isNoneDataRecord(e.record)||(!isAdditionPartsList())?true:false);
				}else{
					e.cancel = !e.record.get('partslist');
				}
				if(!e.cancel) e.grid._edit = e;
			},
			"afteredit" : function(e){
				e.record.commit();
//				e.grid._edit = undefined;
				if(e.field == 'partslist'){
					if(e.value){
						bp3d_parts_store.add(e.record.copy());
					}else{
						var record = null;
						var index = bp3d_parts_store.find('f_id',new RegExp("^"+e.record.get('f_id')+"\$"));
						if(index>=0) record = bp3d_parts_store.getAt(index);
						if(record) bp3d_parts_store.remove(record);
					}
				}else{
					var record = null;
					var regexp = new RegExp("^"+e.record.get('f_id')+"\$");
					var index = bp3d_parts_store.find('f_id',regexp);
					if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
					if(index>=0) record = bp3d_parts_store.getAt(index);
					if(record){
						record.set(e.field,e.record.get(e.field));
						record.commit();
					}
				}
			},
			"complete": function(comp,row,col){
				comp.view.focusRow(row);
			},
			"resize" : function(grid){
				resizeGridPanelColumns(grid);
			},
			"render" : function(grid){
				restoreHiddenGridPanelColumns(grid);
				setTimeout(function(){
					grid.getStore().loadData([]);
				},250);

				ag_parts_gridpanel.getStore().on('remove',function(store,record,index){
					var regexp = new RegExp("^"+record.get('f_id')+"\$");
					var index = this.getStore().find('f_id',regexp);
					if(index>=0){
						var r = this.getStore().getAt(index);
						r.beginEdit();
						r.set('partslist',false);
						r.commit();
						r.endEdit();
					}
				},grid);
			},
			scope : this
		}
	});
	ag_point_search_editorgrid_panel.getColumnModel().on({
		'hiddenchange' : function(column,columnIndex,hidden){
			var editorgrid = Ext.getCmp('anatomography-point-editorgrid-panel');
			resizeGridPanelColumns(editorgrid);
			saveHiddenGridPanelColumns(editorgrid);
		},
		scope: this,
		delay: 100
	});

	var ag_point_search_header_panel = new Ext.Panel({
		contentEl : 'ag-point-search-header-content',
		region    : 'north',
		height    : 52,
		minHeight : 52,
		maxHeight : 52,
		border    : false,
		bodyStyle : 'border-top-width:1px;',

		items: [
		{
			hidden: true,
			xtype: 'numberfield',
			id: 'ag-point-search-header-content-screen-x-text',
			readOnly: true
		},{
			hidden: true,
			xtype: 'numberfield',
			id: 'ag-point-search-header-content-screen-y-text',
			readOnly: true
		}
/*
		,{
			hidden: true,
			xtype: 'numberfield',
			id: 'ag-point-search-header-content-coordinate-x-text',
			readOnly: true,
			listeners: {
				change: function(field,newValue,oldValue){
					\$('div#ag-point-search-header-content-coordinate-x-render').text(newValue);
				}
			}
		},{
			hidden: true,
			xtype: 'numberfield',
			id: 'ag-point-search-header-content-coordinate-y-text',
			readOnly: true,
			listeners: {
				change: function(field,newValue,oldValue){
					\$('div#ag-point-search-header-content-coordinate-y-render').text(newValue);
				}
			}
		},{
			hidden: true,
			xtype: 'numberfield',
			id: 'ag-point-search-header-content-coordinate-z-text',
			readOnly: true,
			listeners: {
				change: function(field,newValue,oldValue){
					\$('div#ag-point-search-header-content-coordinate-z-render').text(newValue);
				}
			}
		},{
			hidden: true,
			xtype: 'numberfield',
			id: 'ag-point-search-header-content-voxel-range-text',
			readOnly: true,
			listeners: {
				change: function(field,newValue,oldValue){
					\$('div#ag-point-search-header-content-distance-z-render').text(newValue);
				}
			}
		}
*/
		],
		listeners : {
			"bodyresize": function(panel,adjWidth,adjHeight,rawWidth,rawHeight){
				if(adjWidth == undefined || !adjWidth) return;

				var table = Ext.get('ag-point-search-header-content-table');
				if(table) table.setWidth(adjWidth);

//既に生成済みの場合、テーブル幅のみを更新
				if(Ext.get('ag-point-search-header-content-more-button')) return;

				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-coordinate-x-text',
					renderTo : 'ag-point-search-header-content-coordinate-x-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-coordinate-y-text',
					renderTo : 'ag-point-search-header-content-coordinate-y-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-coordinate-z-text',
					renderTo : 'ag-point-search-header-content-coordinate-z-render',
					width    : 54,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});

/*
				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-screen-x-text',
					renderTo : 'ag-point-search-header-content-distance-x-render',
					width    : 33,
					readOnly : true,
					selectOnFocus : true
				});
				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-screen-y-text',
					renderTo : 'ag-point-search-header-content-distance-y-render',
					width    : 33,
					readOnly : true,
					selectOnFocus : true
				});
*/

				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-voxel-range-text',
					renderTo : 'ag-point-search-header-content-distance-z-render',
					width    : 23,
					style    : 'color:gray;',
					readOnly : true,
					selectOnFocus : true
				});

/*
				new Ext.form.NumberField({
					id       : 'ag-point-search-header-content-distance-text',
					renderTo : 'ag-point-search-header-content-distance-render',
					width    : 54,
					readOnly : true,
					selectOnFocus : true
				});
*/
				new Ext.Button({
					id       : 'ag-point-search-header-content-more-button',
					renderTo : 'ag-point-search-header-content-distance-render',
					width    : 54,
					disabled : true,
					text     : 'more',
					listeners: {
						click: function(b){
							var voxelRadiusCmp = Ext.getCmp('ag-point-search-header-content-voxel-range-text');
							var voxelRadius = voxelRadiusCmp.getValue();
							if(Ext.isEmpty(voxelRadius)) return;

							var screenXCmp = Ext.getCmp('ag-point-search-header-content-screen-x-text');
							var screenYCmp = Ext.getCmp('ag-point-search-header-content-screen-y-text');

							var screenX = screenXCmp.getValue();
							var screenY = screenYCmp.getValue();
							point_search(screenX,screenY,voxelRadius+5);


						}
					}
				});
			}
		}
	});

	var ag_point_search_panel = new Ext.Panel({
		id     : 'anatomography-point-search-panel',
		header : false,
		title  : 'Neighbor Parts',
		loadMask: true,
		border : false,
		layout : 'border',
		items  : [
			ag_point_search_header_panel,
			ag_point_search_editorgrid_panel
		],
		listeners  : {
			render: function(comp){
				if(Ext.isEmpty(comp.loadMask) || typeof comp.loadMask == 'boolean') comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});
			},
			'show' : function(panel){
				panel.doLayout();
			},
			'afterlayout' : function(panel,layout){
//				afterLayout(anatomography_point_grid_header_panel);
				afterLayout(panel);
			},
			scope:this
		}
	});

	var ag_bp3d_grid_store_fields = [
		{name:'f_id'},
		{name:'b_id'},
		{name:'name_j'},
		{name:'name_e'},
		{name:'name_k'},
		{name:'name_l'},
		{name:'phase'},
		{name:'entry',   type:'date', dateFormat: 'timestamp'},
		{name:'zmin',    type:'float'},
		{name:'zmax',    type:'float'},
		{name:'volume',  type:'float'},
		{name:'organsys'}
	];

	var ag_bp3d_grid_store = new Ext.data.JsonStore({
		url           : 'get-contents-tree-list.cgi',
		totalProperty : 'total',
		root          : 'records',
		fields        : ag_bp3d_grid_store_fields,
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},
		listeners     : {
			'beforeload' : function(self,options){
				self.removeAll();
				self.baseParams = self.baseParams || {};
				var bp3d_version = Ext.getCmp('anatomo-version-combo');
				if(bp3d_version && bp3d_version.rendered){
					self.baseParams.version = bp3d_version.getValue();
				}else{
					self.baseParams.version = init_bp3d_version;
				}
				if(self.baseParams.b_ids) self.baseParams.b_ids = undefined;
				try{
					if(ag_comment_tabpanel.getActiveTab().id != 'anatomography-bp3d-grid-panel') return false;
					var store = Ext.getCmp('ag-parts-gridpanel').getStore();
					var b_ids = [];
					var records = store.getRange();
					for(var i=0,len=records.length;i<len;i++){
						if(records[i].data.exclude) continue;
						if(Ext.isEmpty(records[i].data.b_id)){
							b_ids.push(records[i].data.f_id);
						}else{
							b_ids.push(records[i].data.b_id);
						}
					}
					if(b_ids.length>0){
						self.baseParams.b_ids = Ext.util.JSON.encode(b_ids);
					}else{
						return false;
					}
				}catch(e){
					_dump("ag_bp3d_grid_store.beforeload():"+e);
					return false;
				}
			},
			'load' : function(self,records,options){
			},
			'datachanged' : function(self){
			},
			'loadexception' : function(){
			},
			'exception' : function(){
			},
			scope:this
		}
	});
	try{
		var store = Ext.getCmp('ag-parts-gridpanel').getStore();
		store.on('add',function(){
			var store = Ext.getCmp('anatomography-bp3d-grid-panel').getStore();
			store.reload();
		},this);
		store.on('remove',function(){
			var store = Ext.getCmp('anatomography-bp3d-grid-panel').getStore();
			store.reload();
		},this);
		store.on('update',function(){
			var store = Ext.getCmp('anatomography-bp3d-grid-panel').getStore();
			store.reload();
		},this);
	}catch(e){
		_dump("store:"+e);
	}
	var ag_bp3d_grid_cols = [
		{dataIndex:'f_id',     header:get_ag_lang('CDI_NAME'),                           id:'f_id',     hidden:true},
		{dataIndex:'b_id',     header:get_ag_lang('REP_ID'),                              id:'b_id',     hidden:false},
//		{dataIndex:'name_j',   header:get_ag_lang('GRID_TITLE_NAME_J'),      id:'name_j',   hidden:$gridColHiddenNameJ},
//		{dataIndex:'name_k',   header:get_ag_lang('GRID_TITLE_NAME_K'),      id:'name_k',   hidden:$gridColHiddenNameK},
		{dataIndex:'name_e',   header:get_ag_lang('DETAIL_TITLE_NAME_E'),                         id:'name_e',   hidden:false},
//		{dataIndex:'name_l',   header:'Latina',                          id:'name_l',   hidden:true},
//		{dataIndex:'phase',    header:get_ag_lang('GRID_TITLE_PHASE'),       id:'phase',    hidden:false},
		{dataIndex:'entry',    header:get_ag_lang('GRID_TITLE_MODIFIED'),    id:'entry',    hidden:true, renderer:Ext.util.Format.dateRenderer('Y/m/d')}, 
		{dataIndex:'xmin',     header:'Xmin(mm)',                        id:'xmin',     hidden:true},
		{dataIndex:'xmax',     header:'Xmax(mm)',                        id:'xmax',     hidden:true},
		{dataIndex:'ymin',     header:'Ymin(mm)',                        id:'ymin',     hidden:true},
		{dataIndex:'ymax',     header:'Ymax(mm)',                        id:'ymax',     hidden:true},
		{dataIndex:'zmin',     header:'Zmin(mm)',                        id:'zmin',     hidden:false},
		{dataIndex:'zmax',     header:'Zmax(mm)',                        id:'zmax',     hidden:false},
		{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',   hidden:true}
HTML
#print qq|		,{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',   hidden:true}\n| if($removeGridColValume ne 'true');
#print qq|		,{dataIndex:'organsys', header:get_ag_lang('GRID_TITLE_ORGANSYS'),    id:'organsys', hidden:true}\n| if($removeGridColOrganSystem ne 'true');
print <<HTML;
	];

	var ag_bp3d_grid_panel = new Ext.grid.GridPanel({
		id         : 'anatomography-bp3d-grid-panel',
		header     : false,
		title      : 'BP3D',
		border     : false,
		loadMask   : true,
		columns    : ag_bp3d_grid_cols,
		stripeRows : true,
		columnLines    : true,
		selModel   : new Ext.grid.RowSelectionModel(),
		store      : ag_bp3d_grid_store,
		listeners : {
			'activate' : function(panel){
				panel.getStore().reload();
			},
			'deactivate' : function(panel){
			},
			'render' : function(panel){
			},
			'resize' : function(grid){
				resizeGridPanelColumns(grid);
			},
			scope : this
		}
	});
	ag_bp3d_grid_panel.getColumnModel().on({
		'hiddenchange' : function(column,columnIndex,hidden){
			resizeGridPanelColumns(Ext.getCmp('anatomography-bp3d-grid-panel'));
		},
		scope: this,
		delay: 100
	});

	ag_fma_search_grid_cols_hidden = {
		'common_id':true,
		'name_j':true,
		'name_k':true,
		'name_e':false,
		'name_l':true,
		'phase':true,
		'entry':true,
		'xmin':true,
		'xmax':true,
		'ymin':true,
		'ymax':true,
		'zmin':true,
		'zmax':true,
		'volume':false,
		'organsys':true,
		'exclude':true,
		'color':true,
		'opacity':true,
		'representation':true,
		'value':true,
		'point':true
	};

	createAGSearchGridPanel = function(aQuery){
		try{
		function ag_fma_search_store_fields(){
			return [
				'f_id',
				'b_id',
				'common_id',
				'name_j',
				'name_e',
				'name_k',
				'name_l',
				'syn_j',
				'syn_e',
				'organsys_j',
				'organsys_e',
				'text',
				'name',
				'organsys',
				'phase',
				{name:'xmin',   type:'float'},
				{name:'xmax',   type:'float'},
				{name:'ymin',   type:'float'},
				{name:'ymax',   type:'float'},
				{name:'zmin',   type:'float'},
				{name:'zmax',   type:'float'},
				{name:'volume', type:'float'},
				'taid',
				'physical',
				'phy_id',
				'version',
//				'tg_id',
//				'tgi_id',
				{name:'tg_id',type:'int',convert:function(v,r){
					if(Ext.isEmpty(v)){
						return r.md_id;
					}else{
						return v;
					}
				}},
				{name:'tgi_id',type:'int',convert:function(v,r){
					if(Ext.isEmpty(v)){
						return r.mv_id;
					}else{
						return v;
					}
				}},

				'state',
				'elem_type',
				{name:'entry', type:'date', dateFormat:'timestamp'},
				{name:'lastmod', type:'date', dateFormat:'timestamp'},
				{name:'partslist'},
				{name:'color'},
				{name:'value'},
				{name:'zoom',type:'boolean'},
				{name:'exclude',type:'boolean'},
				{name:'opacity',type:'float'},
				{name:'representation'}
			];
		}

		var ag_fma_search_store = new Ext.data.JsonStore({
			url: 'get-fma.cgi',
			pruneModifiedRecords : true,
			totalProperty : 'total',
			root: 'records',
			fields: ag_fma_search_store_fields(),
//			remoteSort: true,
//			sortInfo: {field: 'volume', direction: 'DESC'},
			listeners: {
				'beforeload' : {
					fn:function(self,options){
						try{
							ag_fma_search_editorgrid_panel.getStore().removeAll();
							self.baseParams = self.baseParams || {};
							delete gParams.parent;
							if(!Ext.isEmpty(gParams.parent)) self.baseParams.parent = gParams.parent;
							self.baseParams.lng = gParams.lng;
							try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){_dump("bp3d_contents_store.beforeload():e=["+e+"]");bp3d_version='$tgi_version';}
							if(!Ext.isEmpty(bp3d_version)) self.baseParams.version = bp3d_version;
						}catch(e){
							_dump("ag_fma_search_store.beforeload():"+e);
						}

						for(var key in init_bp3d_params){
							if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
						}

						try{
							var store = Ext.getCmp('anatomo-version-combo').getStore();
							var idx = store.findBy(function(record,id){
								if(record.data.tgi_version==self.baseParams.version) return true;
							});
							if(idx>=0){
								var record = store.getAt(idx);
								if(record){
									self.baseParams.md_id = record.data.md_id;
									self.baseParams.mv_id = record.data.mv_id;
									self.baseParams.mr_id = record.data.mr_id;
									self.baseParams.ci_id = record.data.ci_id;
									self.baseParams.cb_id = record.data.cb_id;
								}
							}
						}catch(e){}
					},
					scope:this
				},
				'load': {
					fn:function(self,records,options){
						ag_fma_search_editorgrid_panel.getStore().add(records);
						try{ag_fma_search_editorgrid_panel.el.child('div.x-grid3-scroller').scrollTo('top',0,false);}catch(e){_dump("ag_fma_search_store.load():"+e);}

						try{
							var tb = ag_fma_search_editorgrid_panel.getBottomToolbar();
							var count = tb.items.getCount();
							var item = tb.items.get(13);
							item.el.innerHTML='<label>'+self.getTotalCount()+'&nbsp;Objects</label>';
						}catch(e){
							_dump("load():"+e);
						}

					},
					scope:this
				}
			}
		});

		function ag_fma_search_grid_renderer(value,metadata,record,rowIndex,colIndex,store){
			var dataIndex = ag_fma_search_grid_cols[colIndex].dataIndex;
			var item;
			for(var i=0;i<record.fields.length;i++){
				if(record.fields.keys[i] != dataIndex) continue;
				item = record.fields.items[i];
				break;
			}
			if(item){
				if(item.type == 'date'){
					if(dataIndex == 'entry' && value) value = new Date(value).format(bp3d.defaults.DATE_FORMAT);
					if(dataIndex == 'lastmod' && value) value = new Date(value).format(bp3d.defaults.TIME_FORMAT);
				}
			}
			if(isNoneDataRecord(record)){
				metadata.css += ' ag_point_none_data'; 
			}
			return value;
		}
		function ag_fma_search_grid_combobox_renderer(value,metadata,record,rowIndex,colIndex,store){
			if(isNoneDataRecord(record)){
				metadata.css += ' ag_point_none_data'; 
				value = "";
			}else{
				if(record.data.partslist){
				}else{
					value = "";
				}
			}
			return value;
		}
		function ag_fma_search_grid_partslist_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
			var id = ag_fma_search_editorgrid_panel.getColumnModel().getColumnId(colIndex);
			metadata.css += ' x-grid3-check-col-td'; 
			if(isNoneDataRecord(record)) metadata.css += ' ag_point_none_data'; 
			if(isAdditionPartsList()){
				return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
			}else{
				return '<div class="ag_grid_checkbox'+(value?'-on':'')+'-dis x-grid3-cc-'+id+'">&#160;</div>';
			}
		}
		function ag_fma_search_grid_color_cell_renderer(value,metadata,record,rowIndex,colIndex,store) {
			if(isNoneDataRecord(record)){
				metadata.css += ' ag_point_none_data'; 
				return '';
			}else{
				if(record.data.partslist && value){
					return '<span style="background-color:' + value + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>';
				}else{
					return '';
				}
			}
			return value;
		};

		function ag_fma_search_grid_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
			var id = ag_fma_search_editorgrid_panel.getColumnModel().getColumnId(colIndex);
			metadata.css += ' x-grid3-check-col-td'; 
			if(isNoneDataRecord(record)){
				metadata.css += ' ag_point_none_data'; 
			}else{
				if(record.data.partslist){
				}else{
					metadata.css += ' ag_point_none_pallet_data'; 
				}
			}
			return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
		}
		function ag_fma_search_grid_point_checkbox_renderer(value,metadata,record,rowIndex,colIndex,store){
			var id = ag_fma_search_editorgrid_panel.getColumnModel().getColumnId(colIndex);
			metadata.css += ' x-grid3-check-col-td'; 
			if(isNoneDataRecord(record) || isPointDataRecord(record)){
				metadata.css += ' ag_point_none_data'; 
			}else{
				if(record.data.partslist){
				}else{
					metadata.css += ' ag_point_none_pallet_data'; 
				}
			}
			return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
		}

		var ag_fma_search_grid_partslist_checkColumn = new Ext.grid.CheckColumn({
			header    : 'Pallet',
			dataIndex : 'partslist',
			id        : 'partslist',
			width     : 40,
			fixed     : true,
			hidden    : false,
			hideable  : true,
			renderer  : ag_fma_search_grid_partslist_checkbox_renderer
		});
		var ag_fma_search_grid_exclude_checkColumn = new Ext.grid.CheckColumn({
			header    : "Remove",
			dataIndex : 'exclude',
			id        : 'exclude',
			width     : 50,
			resizable : false,
			hidden    : ag_fma_search_grid_cols_hidden['exclude'],
			renderer  : ag_fma_search_grid_checkbox_renderer
		});
		var ag_fma_search_grid_point_checkColumn = new Ext.grid.CheckColumn({
			header    : 'Point',
			dataIndex : 'point',
			id        : 'point',
			width     : 40,
			resizable : false,
			hidden    : ag_fma_search_grid_cols_hidden['point'],
			renderer  : ag_fma_search_grid_point_checkbox_renderer
		});

		var ag_fma_search_grid_col_rep_id = {
			dataIndex:'b_id',
			header:get_ag_lang('REP_ID'),
			renderer: ag_fma_search_grid_renderer,
			id:'b_id',
			width:70,
			resizable:true,
			fixed:!$moveGridOrder,
			hideable:true
		};
		var ag_fma_search_grid_col_cdi_name = {
			dataIndex:'f_id',
			header:get_ag_lang('CDI_NAME'),
			renderer: ag_fma_search_grid_renderer,
			id:'f_id',
			width:70,
			resizable:true,
			fixed:!$moveGridOrder,
			hideable:true
		};
		var ag_fma_search_grid_col_color = {
			dataIndex : 'color',
			header    : 'Color',
			id        : 'color',
			width     : 40,
			resizable : false,
			hidden    : ag_fma_search_grid_cols_hidden['color'],
			hideable  : true,
			renderer  : ag_fma_search_grid_color_cell_renderer,
HTML
if($useColorPicker eq 'true'){
	print <<HTML;
			editor    : new Ext.ux.ColorPickerField({
				menuListeners : {
					select: function(e, c){
						this.setValue(c);
						try{var record = ag_fma_search_editorgrid_panel._edit.record;}catch(e){_dump("color:"+e);}
						if(record){
							record.beginEdit();
							record.set('color',"#"+c);
							record.commit();
							record.endEdit();

							var grid = Ext.getCmp('ag-parts-gridpanel');
							var store = grid.getStore();
							var f_id = record.get('f_id');
							var record = null;
							var regexp = new RegExp("^"+f_id+"\$");
							var index = store.find('f_id',regexp);
							if(index<0) index = store.find('conv_id',regexp);
							if(index>=0) record = store.getAt(index);
							if(record){
								record.set('color',"#"+c);
								record.commit();
							}
						}
					},
					show : function(){
						this.onFocus();
					},
					hide : function(){
						this.focus.defer(10, this);
					},
					beforeshow : function(menu) {
						try {
							if (this.value != "") {
								menu.palette.select(this.value);
							} else {
								this.setValue("");
								var el = menu.palette.el;
								if(menu.palette.value){
									try{el.child("a.color-"+menu.palette.value).removeClass("x-color-palette-sel");}catch(e){}
									menu.palette.value = null;
								}
							}
						}catch(ex){}
					}
				}
			})
HTML
}else{
	print <<HTML;
			editor    : new Ext.ux.ColorField({
				listeners : {
					select: function(e, c){
						try{var record = ag_fma_search_editorgrid_panel._edit.record;}catch(e){_dump("color:"+e);}
						if(record){
							record.beginEdit();
							record.set('color',"#"+c);
							record.commit();
							record.endEdit();

							var grid = Ext.getCmp('ag-parts-gridpanel');
							var store = grid.getStore();
							var f_id = record.get('f_id');
							var record = null;
							var regexp = new RegExp("^"+f_id+"\$");
							var index = store.find('f_id',regexp);
							if(index<0) index = store.find('conv_id',regexp);
							if(index>=0) record = store.getAt(index);
							if(record){
								record.set('color',"#"+c);
								record.commit();
							}
						}
					}
				}
			})
HTML
}
print <<HTML;
		};
		var ag_fma_search_grid_col_opacity = {
			dataIndex : 'opacity',
			header    : 'Opacity',
			id        : 'opacity',
			width     : 50,
			resizable : false,
			hidden    : ag_fma_search_grid_cols_hidden['opacity'],
			hideable  : true,
			align     : 'right',
			renderer: ag_fma_search_grid_combobox_renderer,
			editor    : new Ext.form.ComboBox({
				typeAhead     : true,
				triggerAction : 'all',
				store         : anatomography_point_grid_col_opacity_arr,
				lazyRender    : true,
				listClass     : 'x-combo-list-small',
				listeners     : {
					'select' : function(combo,record,index){
						try{var record = ag_fma_search_editorgrid_panel._edit.record;}catch(e){_dump("color:"+e);}
						if(record){
							record.beginEdit();
							record.set('opacity',combo.getValue());
							record.commit();
							record.endEdit();

							var store = Ext.getCmp('ag-parts-gridpanel').getStore();
							var f_id = record.get('f_id');
							var record = null;
							var regexp = new RegExp("^"+f_id+"\$");
							var index = store.find('f_id',regexp);
							if(index<0) index = store.find('conv_id',regexp);
							if(index>=0) record = store.getAt(index);
							if(record){
								record.set('opacity',combo.getValue());
								record.commit();
							}

						}
					},scope : this
				}
			})
		};
		var ag_fma_search_grid_col_representation = {
			dataIndex : 'representation',
			header    : get_ag_lang('ANATOMO_REP_LABEL'),
			id        : 'representation',
			width     : 40,
			resizable : false,
			renderer  : ag_fma_search_grid_combobox_renderer,
			hidden    : ag_fma_search_grid_cols_hidden['representation'],
			hideable  : true,
			editor    : new Ext.form.ComboBox({
				typeAhead     : true,
				triggerAction : 'all',
				store         : anatomography_point_grid_col_representation_arr,
				lazyRender    : true,
				listClass     : 'x-combo-list-small',
				listeners     : {
					'select' : function(combo,record,index){
						try{var record = ag_fma_search_editorgrid_panel._edit.record;}catch(e){_dump("color:"+e);}
						if(record){
							record.beginEdit();
							record.set('representation',combo.getValue());
							record.commit();
							record.endEdit();

							var store = Ext.getCmp('ag-parts-gridpanel').getStore();
							var f_id = record.get('f_id');
							var record = null;
							var regexp = new RegExp("^"+f_id+"\$");
							var index = store.find('f_id',regexp);
							if(index<0) index = store.find('conv_id',regexp);
							if(index>=0) record = store.getAt(index);
							if(record){
								record.set('representation',combo.getValue());
								record.commit();
							}

						}
					},scope : this
				}
			})
		};
		var ag_fma_search_grid_col_value = {
			dataIndex : 'value',
			header    : 'Value',
			id        : 'value',
			width     : 40,
			resizable : false,
			renderer  : ag_fma_search_grid_renderer,
			hidden    : ag_fma_search_grid_cols_hidden['value'],
			editor    : new Ext.form.TextField({
				allowBlank : true
			})
		};
		var ag_fma_search_grid_col_organsys = {
			dataIndex:'organsys',
			header:get_ag_lang('GRID_TITLE_ORGANSYS'),
			renderer: ag_fma_search_grid_renderer,
			id:'organsys',
			hidden:ag_fma_search_grid_cols_hidden['organsys']
		};
		var ag_fma_search_grid_col_entry = {
			dataIndex:'entry',
			header:get_ag_lang('GRID_TITLE_MODIFIED'),
			renderer: ag_fma_search_grid_renderer,
			id:'entry',
			hidden:ag_fma_search_grid_cols_hidden['entry']
		};

		var ag_fma_search_grid_cols = [
			ag_fma_search_grid_partslist_checkColumn,
			{dataIndex:'common_id',header:'UniversalID',                     renderer: ag_fma_search_grid_renderer, id:'common_id',hidden:ag_fma_search_grid_cols_hidden['common_id'], fixed:$gridColFixedUniversalID},
HTML
print qq|			ag_fma_search_grid_col_rep_id,\n| if($moveGridOrder ne 'true');
print qq|			ag_fma_search_grid_col_cdi_name,\n| if($moveGridOrder ne 'true');
print <<HTML;
			{dataIndex:'name_j',   header:get_ag_lang('DETAIL_TITLE_NAME_J'),    renderer: ag_fma_search_grid_renderer, id:'name_j',   hidden:ag_fma_search_grid_cols_hidden['name_j']},
			{dataIndex:'name_k',   header:get_ag_lang('DETAIL_TITLE_NAME_K'),    renderer: ag_fma_search_grid_renderer, id:'name_k',   hidden:ag_fma_search_grid_cols_hidden['name_k']},
			{dataIndex:'name_e',   header:get_ag_lang('DETAIL_TITLE_NAME_E'),    renderer: ag_fma_search_grid_renderer, id:'name_e',   hidden:ag_fma_search_grid_cols_hidden['name_e']},
			{dataIndex:'name_l',   header:get_ag_lang('DETAIL_TITLE_NAME_L'),    renderer: ag_fma_search_grid_renderer, id:'name_l',   hidden:ag_fma_search_grid_cols_hidden['name_l']},
HTML
if($moveGridOrder ne 'true'){
	print <<HTML;
			{dataIndex:'phase',    header:get_ag_lang('GRID_TITLE_PHASE'),       renderer: ag_fma_search_grid_renderer, id:'phase',    hidden:ag_fma_search_grid_cols_hidden['phase']},
			ag_fma_search_grid_col_entry, 
HTML
}else{
	print <<HTML;
			ag_fma_search_grid_col_color,
			ag_fma_search_grid_col_opacity,
			ag_fma_search_grid_exclude_checkColumn,
			ag_fma_search_grid_col_value,
//			ag_fma_search_grid_col_organsys,
			ag_fma_search_grid_col_representation,
			ag_fma_search_grid_col_rep_id,
			ag_fma_search_grid_col_cdi_name,
HTML
}
print <<HTML;
			{dataIndex:'xmin',     header:'Xmin(mm)',                        renderer: ag_fma_search_grid_renderer, id:'xmin',     hidden:ag_fma_search_grid_cols_hidden['xmin']},
			{dataIndex:'xmax',     header:'Xmax(mm)',                        renderer: ag_fma_search_grid_renderer, id:'xmax',     hidden:ag_fma_search_grid_cols_hidden['xmax']},
			{dataIndex:'ymin',     header:'Ymin(mm)',                        renderer: ag_fma_search_grid_renderer, id:'ymin',     hidden:ag_fma_search_grid_cols_hidden['ymin']},
			{dataIndex:'ymax',     header:'Ymax(mm)',                        renderer: ag_fma_search_grid_renderer, id:'ymax',     hidden:ag_fma_search_grid_cols_hidden['ymax']},
			{dataIndex:'zmin',     header:'Zmin(mm)',                        renderer: ag_fma_search_grid_renderer, id:'zmin',     hidden:ag_fma_search_grid_cols_hidden['zmin']},
			{dataIndex:'zmax',     header:'Zmax(mm)',                        renderer: ag_fma_search_grid_renderer, id:'zmax',     hidden:ag_fma_search_grid_cols_hidden['zmax']},
			{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', renderer: ag_fma_search_grid_renderer, id:'volume',   hidden:ag_fma_search_grid_cols_hidden['volume']},
HTML
if($moveGridOrder ne 'true'){
#	print qq|			{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', renderer: ag_fma_search_grid_renderer, id:'volume',   hidden:ag_fma_search_grid_cols_hidden['volume']},\n| if($removeGridColValume ne 'true');
#	print qq|			ag_fma_search_grid_col_organsys,\n| if($removeGridColOrganSystem ne 'true');
	print <<HTML;
			ag_fma_search_grid_exclude_checkColumn,
			ag_fma_search_grid_col_color,
			ag_fma_search_grid_col_opacity,
			ag_fma_search_grid_col_representation,
			ag_fma_search_grid_col_value
HTML
}else{
	print <<HTML;
			ag_fma_search_grid_col_entry
HTML
}
if($addPointElementHidden ne 'true'){
	print <<HTML;
			,ag_fma_search_grid_point_checkColumn
HTML
}
print <<HTML;
		];

		var ag_fma_search_dummy_store = new Ext.data.SimpleStore({
			pruneModifiedRecords : true,
			root: 'records',
			fields: ag_fma_search_store_fields(),
			listeners: {
				'add' : function(store,records,index){
//_dump("ag_fma_search_dummy_store.add():"+records.length);
					var prm_record = ag_param_store.getAt(0);
					var bp3d_parts_store = ag_parts_gridpanel.getStore();
					for(var i=0;i<records.length;i++){
						var partslist = false;
						var zoom = false;
						var exclude = false;
						var color = null;
						var opacity = "1.0";
						var representation = "surface";
						var value = "";
						var point = false;
						var elem_type = records[i].get('elem_type');
						var regexp = new RegExp("^"+records[i].get('f_id')+"\$");
						var index = bp3d_parts_store.find('f_id',regexp);
						if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
						if(index>=0){
							partslist = true;
							var record = bp3d_parts_store.getAt(index);
							exclude = record.get('exclude');
							color = record.get('color');
							opacity = record.get('opacity');
							representation = record.get('representation');
							value = record.get('value');
							point = record.get('point');
						}
						records[i].beginEdit();
						records[i].set('partslist',partslist);
						records[i].set('zoom',zoom);
						records[i].set('exclude',exclude);
						records[i].set('color',color?color:'#'+ (elem_type=='bp3d_point'? prm_record.data.point_color_rgb:prm_record.data.color_rgb));
						records[i].set('opacity',opacity);
						records[i].set('representation',representation);
						records[i].set('value',value);
						records[i].set('conv_id',records[i].get('b_id'));
						records[i].set('point',point);
						records[i].commit(true);
						records[i].endEdit();
					}
				}
			}
		});
		ag_fma_search_dummy_store.loadData([]);

		var ag_fma_search_editorgrid_panel = new Ext.grid.EditorGridPanel({
			title          : aQuery,
			border         : false,
			stripeRows     : true,
			columnLines    : true,
			maskDisabled   : true,
			plugins        : [
				ag_fma_search_grid_partslist_checkColumn,
				ag_fma_search_grid_exclude_checkColumn
HTML
if($addPointElementHidden ne 'true'){
	print <<HTML;
				,ag_fma_search_grid_point_checkColumn
HTML
}
print <<HTML;
			],
			clicksToEdit   : 1,
			trackMouseOver : true,
			selModel       : new Ext.grid.RowSelectionModel({singleSelect:true}),
			ds: ag_fma_search_dummy_store,
			columns: ag_fma_search_grid_cols,
			enableColLock: false,
			loadMask: true,
			closable: true,
			bbar: new Ext.PagingToolbar({
				pageSize    : 50,
				store       : ag_fma_search_store,
				displayInfo : false,
				displayMsg  : '',
				emptyMsg    : '',
				hideMode    : 'offsets',
				hideParent  : true,
				items :[
					'->',
					'-',
					{xtype: 'tbtext', text: '&nbsp;'}
HTML
if($copyHidden ne 'true'){
	print <<HTML;
					,'-',
					{
						tooltip   : get_ag_lang('COPY_TITLE'),
						iconCls  : 'pallet_copy',
						listeners : {
							'click': {
								fn:function(button,e){
									try{
										copyList(ag_fma_search_editorgrid_panel,ag_fma_search_store);
									}catch(e){
										_dump("7389:"+e);
									}
								},
								scope:this
							}
						}
					}
HTML
}
print <<HTML;
				],
				listeners : {
					"render" : function(toolbar){
//_dump("PagingToolbar.render()");
					},
					scope : this
				}
			}),
			listeners : {
				"beforeedit" : function(e){
					if(e.field == 'partslist'){
//						e.cancel = (Ext.isEmpty(e.record.get('zmax'))||(!isAdditionPartsList())?true:false);
						e.cancel = (isNoneDataRecord(e.record)||(!isAdditionPartsList())?true:false);
					}else{
						e.cancel = !e.record.get('partslist');
					}
					if(!e.cancel) e.grid._edit = e;
				},
				"afteredit" : function(e){
					e.record.commit();
//					e.grid._edit = undefined;
					if(e.field == 'partslist'){
						if(e.value){
							bp3d_parts_store.add(e.record.copy());
						}else{
							var record = null;
							var regexp = new RegExp("^"+e.record.get('f_id')+"\$");
							var index = bp3d_parts_store.find('f_id',regexp);
							if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
							if(index>=0) record = bp3d_parts_store.getAt(index);
							if(record) bp3d_parts_store.remove(record);
						}
					}else{
						var record = null;
						var regexp = new RegExp("^"+e.record.get('f_id')+"\$");
						var index = bp3d_parts_store.find('f_id',regexp);
						if(index<0) index = bp3d_parts_store.find('conv_id',regexp);
						if(index>=0) record = bp3d_parts_store.getAt(index);
						if(record){
							record.set(e.field,e.record.get(e.field));
							record.commit();
						}
					}
				},
				"complete": function(comp,row,col){
					comp.view.focusRow(row);
				},
				"resize" : function(grid){
					resizeGridPanelColumns(grid);
				},
				"render" : function(grid){
					if(Ext.isEmpty(grid.loadMask) || typeof grid.loadMask == 'boolean') grid.loadMask = new Ext.LoadMask(grid.body,{removeMask:false,store:ag_fma_search_store});
					restoreHiddenGridPanelColumns(grid,'ag-fma-search-editorgrid-panel');

					var o = {start:0,limit:50};
					ag_fma_search_store.baseParams = ag_fma_search_store.baseParams || {};
					ag_fma_search_store.baseParams.query = aQuery;
					ag_fma_search_store.baseParams.node = 'search';
					ag_fma_search_store.load({params:o});
				},
				scope : this
			}
		});
		ag_fma_search_editorgrid_panel.getColumnModel().on({
			'hiddenchange' : function(column,columnIndex,hidden){
				resizeGridPanelColumns(ag_fma_search_editorgrid_panel);
				saveHiddenGridPanelColumns(ag_fma_search_editorgrid_panel,'ag-fma-search-editorgrid-panel');
				for(var i=0,len=column.getColumnCount();i<len;i++){
					ag_fma_search_grid_cols_hidden[column.getColumnId(i)] = column.isHidden(i);
				}
			},
			scope: this,
			delay: 100
		});
		return ag_fma_search_editorgrid_panel;
		}catch(e){
			_dump("createAGSearchGridPanel():"+e);
		}
	};

	update_ag_fma_search_grid = function(aParam){
		try{
			function update_ag_fma_search_record(aRecord){
				var index = store.find('f_id',new RegExp("^"+aRecord.get('f_id')+"\$"));
				if(index<0) return;
				var record = store.getAt(index);
				if(!record) return;

				var aIndex = bp3d_parts_store.indexOf(aRecord);
				if(aIndex>=0){
					record.beginEdit();
					record.set('partslist',true);
					for(var reckey in aRecord.data){
						record.set(reckey,aRecord.data[reckey]);
					}
					record.commit();
					record.endEdit();
				}else{
					record.beginEdit();
					record.set('partslist',false);
					record.commit();
					record.endEdit();
				}
			}
			var bp3d_parts_store = ag_parts_gridpanel.getStore();
			var tabpanel = Ext.getCmp('ag-fma-search-tabpanel');
			for(var index=0,len=tabpanel.items.getCount();index<len;index++){
				var store = tabpanel.items.itemAt(index).getStore();
				if(aParam.constructor===Array){
					for(var i=0;i<aParam.length;i++){
						update_ag_fma_search_record(aParam[i]);
					}
				}else{
					update_ag_fma_search_record(aParam);
				}
			}
		}catch(e){
			_dump("update_ag_fma_search_grid():"+e);
		}
	};


	var ag_fma_search_tabpanel = new Ext.TabPanel({
		id : 'ag-fma-search-tabpanel',
		border: false,
		tabPosition:'top',
		enableTabScroll: true,
		anchor:'100% 100%'
	});
	var ag_fma_search_panel = new Ext.Panel({
		id    : 'ag-fma-search-panel',
		title : 'Search',
		border: true,
		layout: 'anchor',
		tbar: [
			new Ext.app.SearchFieldListeners({
				hideLabel: true,
				pageSize : 50,
				listeners : {
					'clear' : function(field){
//_dump("SearchFieldListeners.clear()");
					},
					'search' : function(field,query){
//_dump("SearchFieldListeners.search():"+query);
						var tabCmp = Ext.getCmp('ag-fma-search-tabpanel');
						var tab = null;
						for(var index=0,len=tabCmp.items.getCount();index<len;index++){
							var title = tabCmp.items.itemAt(index).initialConfig.title;
							if(title != query) continue;
							tab = tabCmp.items.itemAt(index);
							break;
						}
						if(!tab){
							tab = createAGSearchGridPanel(query);
							if(tab) tabCmp.setActiveTab(tabCmp.add(tab));
						}else{
							tabCmp.setActiveTab(tab);
						}
					},
					scope: this
				}
			})
		],
		items: ag_fma_search_tabpanel,
		listeners: {
			'add': function(tabpanel,tab,index){
//_dump("ag_fma_search_tabpanel.add():"+tab.id);
			},
			scope: this
		}
	});

HTML
if($moveLeftPalletPanel eq 'true'){
	print <<HTML;
	ag_comment_tabpanel.add(ag_parts_gridpanel);
HTML
}
print <<HTML;
	ag_comment_tabpanel.add(ag_point_grid_panel);
HTML

#DEBUG
#print qq|	ag_comment_tabpanel.add(ag_pin_grid_panel);\n|;
print qq|	ag_comment_tabpanel.add(ag_pin_grid_panel);\n| if($pinPanelHidden ne 'true');#if($lsdb_Auth && $pinPanelHidden ne 'true');
print qq|	ag_comment_tabpanel.add(ag_image_comment_panel);\n| if($legendPanelHidden ne 'true');#if($lsdb_Auth && $legendPanelHidden ne 'true');

print <<HTML;
//	ag_comment_tabpanel.add(ag_bp3d_grid_panel);
//	ag_comment_tabpanel.add(ag_fma_search_editorgrid_panel);
//	ag_comment_tabpanel.add(ag_fma_search_panel);
	ag_comment_tabpanel.add(ag_point_search_panel);
HTML
if($moveLeftPalletPanel ne 'true'){
	print <<HTML;
	ag_comment_tabpanel.add(ag_parts_gridpanel);
	ag_comment_tabpanel.activate(ag_point_grid_panel);
HTML
}else{
	print <<HTML;
	ag_comment_tabpanel.activate(ag_parts_gridpanel);
HTML
}
print <<HTML;

	anatomography_image = new Ext.Panel({
		contentEl  : 'anatomography-image-contentEl',
		id         : 'anatomography-image',
		region     : 'center',
//		autoScroll : true,
		autoScroll : false,
		border     : false,
//		bodyStyle  : 'border-right-width:1px;background-color:#f8f8f8;',
		bodyStyle  : 'background-color:#f8f8f8;',
		listeners : {
			"render": function(comp){
				anatomography_image_render(comp);
			},
			scope:this
		}
	});

	ag_image_shortcut_panel = new Ext.Panel({
		hidden     : false,
		autoShow   : true,
		id         : 'ag-image-shortcut-panel',
		region     : 'north',
//		height     : 52,
//		minHeight  : 52,
//		maxHeight  : 52,
//		autoScroll : false,
//		height     : 106,
		minHeight  : 52,
//		maxHeight  : 106,
		autoHeight     : true,
		autoScroll : true,
		border     : false,
//		bodyStyle  : 'border-right-width:1px;background-color:#f8f8f8;',
		contentEl  : 'ag-image-rotate-box',
		listeners  : {
			'show' : function(panel){
				panel.doLayout();
			},
			'afterlayout' : function(panel,layout){
				afterLayout(panel);
			},
			'resize' : function(panel){
				afterLayout(panel);
			},
			'render': function(panel){
if(0){
					Ext.get('ag-image-rotate-box').removeClass('x-hide-display');
					var prm_record = ag_param_store.getAt(0);
					new Ext.Slider({
						renderTo: 'ag-command-zoom-slider-render',
						id: 'zoom-slider',
						value : prm_record.data.zoom,
						width: 90,
						minValue: 0,
						maxValue: DEF_ZOOM_MAX-1,
						increment: 1,
						plugins: new Ext.ux.SliderTip(),
						listeners: {
							'change' : {
								fn : function (slider, value) {
									if(glb_zoom_xy){
										var elemImg = Ext.get("ag_img");
										var xyImg = elemImg.getXY();
										var mouseX = glb_zoom_xy[0] - xyImg[0];
										var mouseY = glb_zoom_xy[1] - xyImg[1];
										var centerX = parseInt((ag_param_store.getAt(0).data.image_w /2) -  mouseX);
										var centerY = parseInt((ag_param_store.getAt(0).data.image_h /2) -  mouseY);
										setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
										moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, centerX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), centerY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
									}
									var prm_record =ag_param_store.getAt(0);
									prm_record.beginEdit();
									prm_record.set('zoom', value / 5);
									prm_record.endEdit();
									prm_record.commit();
									anatomoUpdateZoomValueText(value + 1);
									if(glb_zoom_xy){
										var elemImg = Ext.get("ag_img");
										var xyImg = elemImg.getXY();
										var mouseX = glb_zoom_xy[0] - xyImg[0];
										var mouseY = glb_zoom_xy[1] - xyImg[1];
										var moveX = parseInt(mouseX - (ag_param_store.getAt(0).data.image_w /2));
										var moveY = parseInt(mouseY - (ag_param_store.getAt(0).data.image_h /2));
										setCameraAndTarget(m_ag.cameraPos, m_ag.targetPos, m_ag.upVec, true);
										moveTargetByMouseForOrtho(ag_param_store.getAt(0).data.image_h, moveX / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)), moveY / parseFloat(Math.pow(2, ag_param_store.getAt(0).data.zoom)));
									}
									updateAnatomo();
									updateClipImage();
									if(glb_zoom_xy) glb_zoom_xy = null;
								},
								scope  : this
							},
							'render' : {
								fn : function(slider){
									if(glb_zoom_slider){
										var textField = Ext.getCmp('zoom-value-text');
										var slider = Ext.getCmp('zoom-slider');
										if(slider && slider.rendered && textField && textField.rendered){
											slider.setValue(glb_zoom_slider-1);
											slider.syncThumb();
											glb_zoom_slider = null;
										}
									}
								},
								scope:this
							}
						}
					});

					new Ext.form.NumberField ({
						ctCls : 'x-small-editor',
						renderTo: 'ag-command-zoom-text-render',
						id: 'zoom-value-text',
						width: 30,
						value : prm_record.data.zoom+1,
						allowBlank : false,
						allowDecimals : false,
						allowNegative : false,
						selectOnFocus : true,
						maxValue : DEF_ZOOM_MAX,
						minValue : 1,
						listeners: {
							'change': {
								fn : function(textField,newValue,oldValue){
									if (anatomoUpdateZoomValue) {
										return;
									}
									var value = isNaN(parseInt(newValue, 10))?oldValue:parseInt(newValue, 10);
									if (value < 1) {
										value = 1;
									}
									if (value > DEF_ZOOM_MAX) {
										value = DEF_ZOOM_MAX
									}
									textField.setValue(value);
									var slider = Ext.getCmp('zoom-slider');
									slider.setValue(value - 1);
								},
								scope:this
							},
							'valid': {
								fn : function(textField){
									var value = textField.getValue();
									var slider = Ext.getCmp('zoom-slider');
									slider.setValue(value - 1);
								},
								scope:this
							},
							'render': {
								fn : function(){
									if(glb_zoom_slider){
										var textField = Ext.getCmp('zoom-value-text');
										var slider = Ext.getCmp('zoom-slider');
										if(slider && slider.rendered && textField && textField.rendered){
											slider.setValue(glb_zoom_slider-1);
											glb_zoom_slider = null;
										}
									}
								},
								scope:this
							}
						}
					});
}

			},
			scope:this
		}
	});

	ag_contents_panel = new Ext.Panel({
		id         : 'ag-contents-panel',
		region     : 'center',
		autoScroll : false,
		bodyBorder : false,
		boder : false,
		layout : 'border',
		items : [
HTML
if(defined $agInterfaceType && $agInterfaceType eq '4'){
	print qq|			ag_image_shortcut_panel,\n|;
}
print <<HTML;
			anatomography_image
			,{


			region      : 'south',
//			height      : 118,
			height      : 64,
//			height      : 90,
//			height      : 94,
//			height      : 108,
			border      : false,
			split       : false,
			collapsible : false,
			frame       : false,
			bodyStyle: 'background:#dfe8f6;',
			html        : '<div class="ag-control-panel-table" style=""><table class="ag-control-panel-table"><tbody><tr><td style="vertical-align: top;"><table class="ag-control-panel-table-button"><tbody><tr><td class="ag-control-panel-td ag-control-panel-td-print"><a href="#"><img width=48 height=48 src="css/ico_print_48.png?1" alt="Print" /></a></td><td class="ag-control-panel-td ag-control-panel-td-link"><a href="#" id="ag-control-panel-a-link"><img width=48 height=48 src="css/ico_link_48.png?2" alt="Link"></a></td><td class="ag-control-panel-td ag-control-panel-td-embed"><a href="#" id="ag-control-panel-a-embed"><img width=48 height=48 src="css/ico_embed_48.png?1" alt="Embed"></a></td><td class="ag-control-panel-td ag-control-panel-td-download">'+

			'<div class="ag-control-panel-download-div-button">'+
			'<a href="#" id="ag-control-panel-a-download"><img width=33 height=48 src="css/icon_download.png?2" alt="Download" style="width:33px;"></a>'+
			'</div>'+

			'</td></tr></tbody></table></td>' +
//			'</tr><tr>' +
			'<td class="ag-control-panel-td-license"><div class="ag-control-panel-div-license">'+get_ag_lang('LICENSE_AG')+'</div></td>' +
//			'<td class="ag-control-panel-td-tweet" style="display:none;"><a href="#"><img width=48 height=48 src="css/ico_twitter_48.png" alt="Tweet"></a></td>'+
			'</tr></tbody></table></div>',
			listeners : {
				'show' : function(panel){
					panel.doLayout();
				},
				'afterlayout' : function(panel,layout){
					afterLayout(panel);
				},
				render: function(comp){

					\$('td.ag-control-panel-td-download>div>a').live('click',function(e){
//						console.log(e);
						var maskElem = Ext.get(e.currentTarget).findParent('div.ag-control-panel-download-div-button',2,true);
						if(maskElem && maskElem.isMasked()) return;
						if(maskElem) maskElem.mask();

						var store = Ext.getCmp('ag-parts-gridpanel').getStore();
						var target_rep_ids = [];
						store.each(function(record){
							target_rep_ids.push({
								rep_id: record.get('b_id'),
								opacity: record.get('opacity'),
								exclude: record.get('exclude')
							});
						});
						if(target_rep_ids.length){
							var _download = function(params){
								params = params || {};
								var form_name = 'form_download';
								var form;
								if(!document.forms[form_name]){
									form = \$('<form>').attr({
										action: "download.cgi",
										method: "POST",
										name:   form_name,
										id:     form_name,
										style:  "display:none;"
									}).appendTo(\$(document.body));
								}else{
									form = \$(document.forms[form_name]).empty();
								}
								if(Ext.isArray(params.rep_id) && params.rep_id.length){
									var input = \$('<input type="hidden" name="rep_id">').appendTo(form);
									input.val(Ext.encode(params.rep_id));
								}
								if(Ext.isArray(params.exclusion_ids) && params.exclusion_ids.length){
									var input = \$('<input type="hidden" name="exclusion_ids">').appendTo(form);
									input.val(Ext.encode(params.exclusion_ids));
								}
								if(Ext.isArray(params.ids) && params.ids.length){
									var input = \$('<input type="hidden" name="ids">').appendTo(form);
									input.val(Ext.encode(params.ids));
								}
								if(params.filename){
									var input = \$('<input type="hidden" name="filename">').appendTo(form);
									input.val(params.filename);
								}
								var input = \$('<input type="hidden" name="type" value="art_file">').appendTo(form);
								var input = \$('<input type="hidden" name="all_downloads" value="1">').appendTo(form);

								document.forms[form_name].submit();
							};

							var transaction_id = Ext.Ajax.request({
								url     : 'download-pallet-art_file.cgi',
								method  : 'POST',
								params  : Ext.urlEncode({rep_ids:Ext.encode(target_rep_ids)}),
								success : function(conn,response,options){
									try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
									results = results || {};
									if(Ext.isArray(results.rep_ids) && results.rep_ids.length){
//										var filename = Ext.util.Format.date(new Date(),'YmdHis_u');

										var filename = Ext.util.Format.date(new Date(),'YmdHis');
										_download({rep_id:results.rep_ids,ids:results.art_ids,filename:filename});
										if(maskElem) maskElem.unmask();
										return;

										var win = window.open(
											"about:blank",
//											filename,
											null,
											"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600"
										);
										console.log(win.name);
										setTimeout(function(){
											var form_name = 'form_download_art_file_list';
											var form;
											if(!document.forms[form_name]){
												form = \$('<form>').attr({
													action: "download-art_file-list.cgi?type=html&lng=$FORM{lng}",
													method: "POST",
													name:   form_name,
													id:     form_name,
													style:  "display:none;",
													target: filename
												}).appendTo(\$(document.body));
											}else{
												form = \$(document.forms[form_name]).empty();
											}
											var input = \$('<input type="hidden" name="rep_ids">').appendTo(form);
											input.val(Ext.encode(results.rep_ids));

											form.bind('submit',function(){
												form.remove();
											});
											document.forms[form_name].submit();
										},250);

									}
									if(maskElem) maskElem.unmask();
								},
								failure : function(conn,response,options){
									Ext.MessageBox.show({
										title   : 'Donwload OBJ',
										msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									if(maskElem) maskElem.unmask();
								}
							});


						}else{
							if(maskElem) maskElem.unmask();
						}
						return false;
					});

					\$('td.ag-control-panel-td-print>a').live('click',function(){
						var form = Ext.getDom('ag-print-form');
						if(!form) return false;
						var target = Ext.id().replace(/\-/g,"_");

						var width = \$('img#ag_img').width();
						var height = \$('img#ag_img').height();
//						var print_win = window.open("", target, "titlebar=no,toolbar=yes,status=no,menubar=yes,dependent=yes,width="+width+",height="+height);


						var print_win = window.open("", target, "titlebar=no,toolbar=yes,status=no,menubar=yes,dependent=yes,width="+width+",height="+height);

						var jsonStr = glb_anatomo_image_still;
						try{
							jsonStr = ag_extensions.toJSON.URI2JSON(glb_anatomo_image_still,{
								toString:true,
								mapPin:false,
								callback:undefined
							});
							jsonStr = encodeURIComponent(jsonStr);
						}catch(e){jsonStr = glb_anatomo_image_still;}

						var printURL = getEditUrl() + "print.html?" + jsonStr;

						var transaction_id = Ext.Ajax.request({
							url     : 'get-convert-url.cgi',
							method  : 'POST',
							params  : Ext.urlEncode({url:printURL}),
							success : function(conn,response,options){
								try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
								if(Ext.isEmpty(results) || Ext.isEmpty(results.status_code) || results.status_code!=200){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ '+ results.status_code +' ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}
								if(Ext.isEmpty(results.data)){
									var msg = get_ag_lang('CONVERT_URL_ERRMSG');
									if(results && results.status_code) msg += ' [ no data ]';
									Ext.MessageBox.show({
										title   : window_title,
										msg     : msg,
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
									return;
								}

								if(!Ext.isEmpty(results.data.url)){//shortURLに変換
									print_win.location.href = results.data.url;
								}else if(!Ext.isEmpty(results.data.expand)){//longURLに変換
									print_win.location.href = printURL;
								}
							},
							failure : function(conn,response,options){
								Ext.MessageBox.show({
									title   : window_title,
									msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
						return false;
					});
					\$('td.ag-control-panel-td-link>a').live('click',function(){
						anatomography_open_link_window();
						return false;
					});
					\$('td.ag-control-panel-td-embed>a').live('click',function(){
						anatomography_open_embed_window();
						return false;
					});
					\$('td.ag-control-panel-td-license>a').live('click',function(){
						var src = get_ag_lang('LICENSE_URL');
						window.open(src,"_blank","menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600");
						return false;
					});
					\$('td.ag-control-panel-td-tweet>a').live('click',function(){
						window.open('$urlTwitterTweetAG','_blank_ag','dependent=yes,width=800,height=600');
						return false;
					});

					Ext.getCmp('contents-tab-panel').on({
						tabchange: {
							fn: function(tabpanel,tab){
								if(tab.id != 'contents-tab-anatomography-panel') return;
								comp.setHeight(comp.initialConfig.height);
								comp.findParentByType('panel').doLayout();
							},
							buffer: 250
						}
					});

				},
				scope:this
			}












			}
		]
	});

	oncheck_anatomo_windowsize_autosize_check = function(checkbox, fChecked){
		var wc = Ext.getCmp('anatomo-width-combo');
		var hc = Ext.getCmp('anatomo-height-combo');
		if(wc && wc.rendered && hc && hc.rendered){
			if(fChecked){
				wc.disable();
				hc.disable();
			}else{
				wc.enable();
				hc.enable();
			}
		}
		if(fChecked) setImageWindowSize();
	};

	oncheck_anatomo_bgcolor_transparent_check = function(checkbox, fChecked){
		var prm_record = ag_param_store.getAt(0);
		prm_record.beginEdit();
		prm_record.set('bg_transparent', fChecked ? 0 : NaN);
		prm_record.endEdit();
		prm_record.commit();
		updateAnatomo();
	};

	anatomography_panel = new Ext.Panel({
		title  : get_ag_lang('TITLE_AG'),
HTML
print qq|		tabTip   : get_ag_lang('TABTIP_AG'),| if($useTabTip eq 'true');
print <<HTML;
		id    : 'contents-tab-anatomography-panel',
		autoScroll : false,
		bodyBorder : false,
		boder : false,
		layout : 'border',
		items : [
			ag_contents_panel,
			ag_comment_panel,
			ag_image_control_panel
		],
//		tbar  : anatomography_panel_toolbar,
		listeners : {
			'show' : function(panel){
				panel.doLayout();
				var cmp = Ext.getCmp('zoom-slider');
				if(cmp) cmp.syncThumb();
			},
			scope:this
		}
	});
}

function ag_command_init(e){
	var ag_command_btn_move = Ext.get('ag-command-btn-move');
	var ag_command_btn_rotate = Ext.get('ag-command-btn-rotate');
	if(!ag_command_btn_move || !ag_command_btn_rotate) return;
	ag_command_btn_move.addListener("click",ag_command_toggle);
	ag_command_btn_rotate.addListener("click",ag_command_toggle);
	if(anatomoDragModeMove){
		ag_command_btn_move.addClass("ag_command_btn_on");
	}else{
		ag_command_btn_rotate.addClass("ag_command_btn_on");
	}
}
function ag_command_toggle(e){
	e.preventDefault();
	var target = e.getTarget(undefined,undefined,true);
	ag_command_toggle_exec(target);
	return false;
}
function ag_command_toggle_exec(target){
	target.blur();
	if(target.hasClass("ag_command_btn_on")) return;
	var elem = Ext.select('a[class*=ag_command_btn_on]',true);
	if(elem){
		for(var i=elem.getCount()-1;i>=0;i--){
			elem.item(i).removeClass("ag_command_btn_on");
		}
	}
//	if(target.id == "ag-command-btn-move"){
//		target = Ext.get('ag-command-btn-rotate');
//	}else{
//		target = Ext.get('ag-command-btn-move');
//	}
	target.addClass("ag_command_btn_on");

	var checkbox = Ext.getCmp('anatomo-dragmode-check');
	anatomoDragModeMove = (target.id == "ag-command-btn-move" ? true : false);
	if(checkbox && checkbox.rendered && checkbox.getValue() != anatomoDragModeMove) checkbox.setValue(anatomoDragModeMove);
}

var agRotateAuto = {
//var ag_image_auto_rotate_interval = -1;
//var ag_image_auto_rotate_start_time = -1;
//var ag_image_auto_rotate_angle = 0;
//var ag_image_auto_rotate_rotAxis = {
//	rotAxisX : 0,
//	rotAxisZ : 0,
//	rotAxisY : 0
//};
//var ag_image_auto_rotate_imgX = 0;
//var ag_image_auto_rotate_imgY = 0;

	load_time : -1,
	dt_time : -1,
	angle : 0,
	rotAxis : null,
	imgX : 0,
	imgY : 0,

	init : function(){
		agRotateAuto.removeRotateImages();
		agRotateAuto.load_time = (new Date()).getTime();
		agRotateAuto.dt_time = getDateString();
		agRotateAuto.angle = 0;
		agRotateAuto.imgX = 0;
		agRotateAuto.imgY = 0;
HTML
if($modifyAxisOfRotation eq 'true'){
	print <<HTML;
		if(agRotateAuto.checkCoordinate(new AGVec3d(m_ag.upVec.x,m_ag.upVec.y,m_ag.upVec.z))){
HTML
}else{
	print <<HTML;
		if(agRotateAuto.checkCoordinate(new AGVec3d((90 * Math.PI / 180),m_ag.upVec.y,m_ag.upVec.z),'init')){
HTML
}
print <<HTML;
			agRotateAuto.dispAxisOfRotationAngle();
			agRotateAuto.dispNowAngle();
		}
	},

	checkCoordinate : function(pAGVec3d,fname){
		if(isNaN(pAGVec3d.x) || isNaN(pAGVec3d.y) || isNaN(pAGVec3d.z)){
			Ext.MessageBox.show({
				title   : 'Auto rotation',
				msg     : 'The result of the calculation is incorrect coordinates. ['+fname+']',
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
			return false;
		}else{
			agRotateAuto.rotAxis = pAGVec3d;
			return true;
		}
	},

	dispAxisOfRotationAngle : function(){
		var dom = Ext.getDom('ag-command-image-controls-rotateAuto-axis-label');
		if(dom && agRotateAuto.rotAxis){
			var deg = calcRotateAxisDeg(agRotateAuto.rotAxis);
			dom.innerHTML = Math.round(deg.V);
//			dom.innerHTML = Math.round(deg.H)+","+Math.round(deg.V);
		}
	},

	dispNowAngle : function(){
		var dom = Ext.getDom('ag-command-image-controls-rotateAuto-now-angle-label');
		if(dom){
			dom.innerHTML = Math.round(agRotateAuto.angle);
		}
	},

	removeRotateImages : function(){
		var delobjs = {
			dt : agRotateAuto.dt_time
		};
		Ext.Ajax.request({
			url     : 'del-rotate_images.cgi',
			method  : 'POST',
			params  : Ext.urlEncode(delobjs),
			success : function(conn,response,options){
			},
			failure : function(conn,response,options){
			}
		});
	},

	setRotAxis : function(rotAxis){
		agRotateAuto.removeRotateImages();
		agRotateAuto.dt_time = getDateString();
		if(agRotateAuto.checkCoordinate(new AGVec3d(rotAxis.rotAxisX,rotAxis.rotAxisY,rotAxis.rotAxisZ),'setRotAxis')){
			agRotateAuto.dispAxisOfRotationAngle();
		}
	},

	getAngles : function (){
		var angles;
		try{
			angles = Ext.getCmp('ag-command-image-controls-rotateAuto-angles').getValue();
		}catch(e){
			angles = 15;
		}
		return angles;
	},

	getInterval : function(){
		var interval;
		try{
			interval = Ext.getCmp('ag-command-image-controls-rotateAuto-interval').getValue();
		}catch(e){
			interval = 1;
		}
		return interval;
	},

	rotate : function(state){
		var ag_img = Ext.get('ag_img');
		if(!state){
			ag_img.un('load',agRotateAuto._rotate);
			ag_img.un('abort',agRotateAuto._abort);
			ag_img.un('error',agRotateAuto._error);
			return;
		}
		ag_img.on('load',agRotateAuto._rotate);
		ag_img.on('abort',agRotateAuto._abort);
		ag_img.on('error',agRotateAuto._error);

		agRotateAuto.load_time = (new Date()).getTime();
		agRotateAuto._rotate();
	},

	_rotate : function(){
//		_dump("agRotateAuto._rotate()");
		var interval = agRotateAuto.getInterval() * 1000;
		var curTime = (new Date()).getTime();

		agRotateAuto.angle += agRotateAuto.getAngles();
		if(agRotateAuto.angle>=360){
			agRotateAuto.angle -= 360;
		}else if(agRotateAuto.angle<=-360){
			agRotateAuto.angle += 360;
		}
		agRotateAuto.dispNowAngle();

		if(curTime-agRotateAuto.load_time<interval){
			interval -= (curTime-agRotateAuto.load_time);
			setTimeout(function(){
				agRotateAuto.load_time = (new Date()).getTime();
				stopUpdateAnatomo();
				_updateAnatomo(false);
			},interval);
		}else{
			agRotateAuto.load_time = curTime;
			stopUpdateAnatomo();
			_updateAnatomo(false);
		}
	},

	_abort : function(){
		_dump("agRotateAuto._abort()");
	},
	_error : function(){
		_dump("agRotateAuto._error()");
	}
};

function addAgMenuItem(parentMenu){
	return;
}


agCommandMenuImageMove = {
	xtype : 'menu',
	id    : 'ag-command-menu-image-move',
	text  : 'Move',
	icon    : 'css/menu_move.png',
	menu  : {
		items : [{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-move-up',
			text    : 'up',
			icon    : 'css/arrow_up.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-move-right',
			text    : 'right',
			icon    : 'css/arrow_right.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-move-down',
			text    : 'down',
			icon    : 'css/arrow_down.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-move-left',
			text    : 'left',
			icon    : 'css/arrow_left.png',
			handler : agCommandMenuClick
		},'-',{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-move-focus-center',
			text    : 'Centering',
			icon    : 'css/focus_center.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-move-focus-zoom',
			text    : 'Centering & Zoom',
			icon    : 'css/focus_zoom.png',
			handler : agCommandMenuClick
		}]
	}
};

agCommandMenuImageRotation = {
	xtype : 'menu',
	id    : 'ag-command-menu-image-rotation',
	text  : 'Rotation',
	icon    : 'css/menu_rotate.png',
	menu  : {
		items : [{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-up',
			text    : 'up',
			icon    : 'img/rotate_u.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-right',
			text    : 'right',
			icon    : 'img/rotate_r.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-down',
			text    : 'down',
			icon    : 'img/rotate_d.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-left',
			text    : 'left',
			icon    : 'img/rotate_l.png',
			handler : agCommandMenuClick
		},'-',{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-0-0',
			text    : 'H:<tt>&nbsp;&nbsp;</tt>0,V:<tt>&nbsp;&nbsp;</tt>0',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-90-0',
			text    : 'H:<tt>&nbsp;</tt>90,V:<tt>&nbsp;&nbsp;</tt>0',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-180-0',
			text    : 'H:180,V:<tt>&nbsp;&nbsp;</tt>0',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-270-0',
			text    : 'H:270,V:<tt>&nbsp;&nbsp;</tt>0',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-180-90',
			text    : 'H:180,V:<tt>&nbsp;</tt>90',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-rotation-0-270',
			text    : 'H:<tt>&nbsp;&nbsp;</tt>0,V:270',
			handler : agCommandMenuClick
		}]
	}
};
agCommandMenuImageZoom = {
	xtype : 'menu',
	id    : 'ag-command-menu-image-zoom',
	text  : 'Zoom',
	icon    : 'css/magnifier.png',
	menu  : {
		items : [{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-zoom-up',
			text    : 'In',
			icon    : 'css/magnifier_zoom.png',
			handler : agCommandMenuClick
		},{
			xtype   : 'menuitem',
			id      : 'ag-command-menu-image-zoom-down',
			text    : 'Out',
			icon    : 'css/magnifier_zoom_out.png',
			handler : agCommandMenuClick
		}]
	}
};
agCommandMenuImageGridCheckbox = {
	xtype   : 'checkbox',
	id      : 'ag-command-menu-image-grid-checkbox',
	text    : 'Grid(On/Off)',
	checked : false,
	checkHandler : agCommandMenuClick
};
agCommandMenuImageGridColor = {
	id   : 'ag-command-menu-image-grid-color',
	text : 'Choose a Color',
	menu : new Ext.menu.ColorMenu({
		id      : 'ag-command-menu-image-grid-color-palette',
		handler : agCommandMenuClick,
		listeners : {
			'beforerender' : function(menu){
				if(menu.palette && menu.palette.colors) menu.palette.colors = window.palette_color;
			},
			'beforeshow' : function(menu){
				var color = Ext.getCmp('ag-command-grid-color-field').getValue();
				if(!color) return;
				color = color.replace(/^#/g,"").toUpperCase();
				if(menu.palette){
					menu.palette.suspendEvents();
					menu.palette.select(color);
					menu.palette.resumeEvents();
				}
			}
		}
	})
};
agCommandMenuImageGridLen = {
	id   : 'ag-command-menu-image-grid-len',
	text : 'Rect Length',
	menu : {
		items : ['<b class="menu-title">Choose a Rect Length</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-image-grid-len-';
				var combo = Ext.getCmp('ag-command-grid-len-combobox');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var items = {};
				for(var i=0;i<records.length;i++){
					items[records[i].data.value] = menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp,
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				var value = combo.getValue();
				if(items[value]) items[value].setChecked(true);
			}
		}
	}
};
agCommandMenuImageGrid = {
	xtype : 'menu',
	id    : 'ag-command-menu-image-grid',
	text  : 'Grid',
	menu  : {
		items : [
			agCommandMenuImageGridCheckbox,
			'-',
			agCommandMenuImageGridColor,
			agCommandMenuImageGridLen
		],
		listeners : {
			'beforeshow' : function(menu){
				var show = Ext.getCmp('ag-command-grid-show-check').getValue();
				Ext.getCmp('ag-command-menu-image-grid-checkbox').setChecked(show);
				if(show){
					Ext.getCmp('ag-command-menu-image-grid-color').enable();
					Ext.getCmp('ag-command-menu-image-grid-len').enable();
				}else{
					Ext.getCmp('ag-command-menu-image-grid-color').disable();
					Ext.getCmp('ag-command-menu-image-grid-len').disable();
				}
			}
		}
	}
};
agCommandMenuImageControls = {
	xtype : 'menu',
	id    : 'ag-command-menu-image-controls',
	text  : 'Image controls',
	menu  : {
		items : [
			agCommandMenuImageMove,
			agCommandMenuImageRotation,
			agCommandMenuImageZoom,
			agCommandMenuImageGrid
		]
	}
};

agCommandMenuClipCheckbox = {
	xtype   : 'checkbox',
	id      : 'ag-command-menu-clip-checkbox',
	text    : 'Clip(On/Off)',
	checked : false,
	checkHandler : agCommandMenuClick
};
agCommandMenuClipMethod = {
	id   : 'ag-command-menu-clip-method',
	text : 'Method',
	menu : {
		items : ['<b class="menu-title">Choose a Method</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-clip-method-';
				var combo = Ext.getCmp('anatomo-clip-method-combo');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				for(var i=0;i<records.length;i++){
					menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp,
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				Ext.getCmp(key+combo.getValue()).setChecked(true);
			}
		}
	}
};
agCommandMenuClipPredefinedPlane = {
	id   : 'ag-command-menu-clip-predefined-plane',
	text : 'Predefined plane',
	menu : {
		items : ['<b class="menu-title">Choose a Predefined plane</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-clip-predefined-plane-';
				var combo = Ext.getCmp('anatomo-clip-predifined-plane');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var items = {};
				for(var i=0;i<records.length;i++){
					items[records[i].data.value] = menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp,
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				menu.addSeparator();
				var fix_menu = menu.addMenuItem({
					xtype   : 'checkbox',
					id      : key+'freeplane-fix',
					text    : 'Fix',
					checked : false,
					checkHandler : agCommandMenuClick
				});
				var reverse_menu = menu.addMenuItem({
					xtype   : 'checkbox',
					id      : key+'reverse',
					text    : 'Reverse',
					checked : false,
					checkHandler : agCommandMenuClick
				});

				var plane = combo.getValue();
				var fix = Ext.getCmp('anatomo-clip-fix-check').getValue();
				var reverse = Ext.getCmp('anatomo-clip-reverse-check').getValue();

				if(plane=='FREE'){
					fix_menu.enable();
					fix_menu.setChecked(fix);
					if(fix){
						reverse_menu.enable();
						reverse_menu.setChecked(reverse);
					}else{
						reverse_menu.disable();
						reverse_menu.setChecked(false);
					}
				}else{
					fix_menu.disable();
					fix_menu.setChecked(false);
					reverse_menu.enable();
					reverse_menu.setChecked(reverse);
				}
				if(items[plane]) items[plane].setChecked(true);
			}
		}
	}
};

agCommandMenuSectionalView = {
	text  : 'Sectional View',
	hidden: $sectionalViewHidden,
	menu  : {
		id    : 'ag-command-menu-sectional-view',
		items : [
			agCommandMenuClipCheckbox,
			'-',
			agCommandMenuClipMethod,
			agCommandMenuClipPredefinedPlane,
			'-',{
				xtype   : 'menuitem',
				id      : 'ag-command-menu-clip-up',
				text    : 'up',
				icon    : 'css/arrow_up.png',
				handler : agCommandMenuClick
			},{
				xtype   : 'menuitem',
				id      : 'ag-command-menu-clip-down',
				text    : 'down',
				icon    : 'css/arrow_down.png',
				handler : agCommandMenuClick
			}
		],
		listeners : {
			'beforeshow' : function(menu){
//				_dump("agCommandMenuSectionalView:beforeshow(1):"+menu.id);
				var checked = Ext.getCmp('anatomo-clip-check').getValue();
				Ext.getCmp('ag-command-menu-clip-checkbox').setChecked(checked);
				if(checked){
					Ext.getCmp('ag-command-menu-clip-method').enable();
					Ext.getCmp('ag-command-menu-clip-predefined-plane').enable();
					Ext.getCmp('ag-command-menu-clip-up').enable();
					Ext.getCmp('ag-command-menu-clip-down').enable();
				}else{
					Ext.getCmp('ag-command-menu-clip-method').disable();
					Ext.getCmp('ag-command-menu-clip-predefined-plane').disable();
					Ext.getCmp('ag-command-menu-clip-up').disable();
					Ext.getCmp('ag-command-menu-clip-down').disable();
				}
			},
			'show' : function(menu){
//				_dump("agCommandMenuSectionalView:show(1):"+menu.id);
			}
		}
	}
};

agCommandMenuWindowSizeWidth = {
	text : 'Width',
	icon : 'css/arrow_width.png',
	menu : {
		id    : 'ag-command-menu-window-size-width',
		items : ['<b class="menu-title">Choose a Window width</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-window-size-width-';
				var combo = Ext.getCmp('anatomo-width-combo');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var items = {};
				for(var i=0;i<records.length;i++){
					items[records[i].data.value] = menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp+' px',
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				if(Ext.getCmp('anatomo-windowsize-autosize-check').getValue()) return;
				var value = combo.getValue();
				if(items[value]) items[value].setChecked(true);
			}
		}
	}
};
agCommandMenuWindowSizeHeight = {
	text : 'Height',
	icon : 'css/arrow_height.png',
	menu : {
		id    : 'ag-command-menu-window-size-height',
		items : ['<b class="menu-title">Choose a Window height</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-window-size-height-';
				var combo = Ext.getCmp('anatomo-height-combo');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var items = {};
				for(var i=0;i<records.length;i++){
					items[records[i].data.value] = menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp+' px',
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				if(Ext.getCmp('anatomo-windowsize-autosize-check').getValue()) return;
				var value = combo.getValue();
				if(items[value]) items[value].setChecked(true);
			}
		}
	}
};
agCommandMenuWindowSizeAutoCheckbox = {
	xtype   : 'checkbox',
	id      : 'ag-command-menu-window-size-autosize',
	text    : 'Auto Window Size',
	checked : false,
	checkHandler : agCommandMenuClick
};
agCommandMenuWindowSize = {
	text : 'Window size',
	menu : {
		id    : 'ag-command-menu-window-size',
		items : [
			agCommandMenuWindowSizeWidth,
			agCommandMenuWindowSizeHeight,
			agCommandMenuWindowSizeAutoCheckbox
		],
		listeners : {
			'beforeshow' : function(menu){
//				_dump("agCommandMenuWindowSize:beforeshow(1):"+menu.id);
				var autosize = Ext.getCmp('anatomo-windowsize-autosize-check').getValue();
				Ext.getCmp('ag-command-menu-window-size-autosize').setChecked(autosize);
			}
		}
	}
};


agCommandMenuWindowBackgroundColorMenu = {
	text : 'Choose a Color',
	menu : new Ext.menu.ColorMenu({
		id      : 'ag-command-menu-window-background-color-palette',
		handler : agCommandMenuClick,
		listeners : {
			'beforerender' : function(menu){
				if(menu.palette && menu.palette.colors) menu.palette.colors = window.palette_color;
			},
			'beforeshow' : function(menu){
				var bgcp = Ext.getCmp('anatomo-bgcp').getValue();
				if(!bgcp) return;
				bgcp = bgcp.replace(/^#/g,"").toUpperCase();
				if(menu.palette){
					menu.palette.suspendEvents();
					menu.palette.select(bgcp);
					menu.palette.resumeEvents();
				}
			}
		}
	})
};
agCommandMenuWindowBackgroundColorTransparent = {
	xtype   : 'checkbox',
	id      : 'ag-command-menu-window-background-color-transparent',
	text    : 'Transparent',
	checked : false,
	checkHandler : agCommandMenuClick
};
agCommandMenuWindowBackgroundColor = {
	text  : 'Background color',
	menu  : {
		id    : 'ag-command-menu-window-background-color',
		items : [
			agCommandMenuWindowBackgroundColorMenu,
			agCommandMenuWindowBackgroundColorTransparent
		],
		listeners : {
			'beforeshow' : function(menu){
//				_dump("agCommandMenuWindowBackgroundColor:beforeshow(1):"+menu.id);
				var transparent = Ext.getCmp('anatomo-bgcolor-transparent-check').getValue();
				Ext.getCmp('ag-command-menu-window-background-color-transparent').setChecked(transparent);
			}
		}
	}
};


agCommandMenuDefaultPartsColor = {
	text : 'Default parts color',
	menu : new Ext.menu.ColorMenu({
		id      : 'ag-command-menu-default-parts-color',
		handler : agCommandMenuClick,
		listeners : {
			'beforerender' : function(menu){
				if(menu.palette && menu.palette.colors) menu.palette.colors = window.palette_color;
			},
			'beforeshow' : function(menu){
				var color = Ext.getCmp('anatomo-default-parts-color').getValue();
				if(!color) return;
				color = color.replace(/^#/g,"").toUpperCase();
				if(menu.palette){
					menu.palette.suspendEvents();
					menu.palette.select(color);
					menu.palette.resumeEvents();
				}
			}
		}
	})
};

agCommandMenuPointColorMenu = {
	text : 'Choose a Color',
	menu : new Ext.menu.ColorMenu({
		id      : 'ag-command-menu-point-color',
		handler : agCommandMenuClick,
		listeners : {
			'beforerender' : function(menu){
				if(menu.palette && menu.palette.colors) menu.palette.colors = window.palette_color;
			},
			'beforeshow' : function(menu){
				var color = Ext.getCmp('anatomo-default-point-parts-color').getValue();
				if(!color) return;
				color = color.replace(/^#/g,"").toUpperCase();
				if(menu.palette){
					menu.palette.suspendEvents();
					menu.palette.select(color);
					menu.palette.resumeEvents();
				}
			}
		}
	})
};
agCommandMenuPointSphere = {
	text : 'Sphere',
	menu : {
		id    : 'ag-command-menu-point-sphere',
		items : ['<b class="menu-title">Choose a Sphere</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-point-sphere-';
				var combo = Ext.getCmp('ag-command-point-sphere-combo');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var items = {};
				for(var i=0;i<records.length;i++){
					items[records[i].data.value] = menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp,
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				var value = combo.getValue();
				if(items[value]) items[value].setChecked(true);
			}
		}
	}
};
agCommandMenuPointClassificationLabel = {
	text : 'Classification label',
	menu : {
		id    : 'ag-command-menu-point-classification-label',
		items : [
			'<b class="menu-title">Choose a Classification label</b>'
		],
		listeners : {
			'beforeshow' : function(menu){
				var combo = Ext.getCmp('anatomo-point-label-combo');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var key = 'ag-command-menu-point-classification-label-';
				for(var i=0;i<records.length;i++){
					menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp,
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				var label = combo.getValue();
				Ext.getCmp(key+label).setChecked(true);
			}
		}
	}
};
agCommandMenuPointDescription = {
	xtype   : 'checkbox',
	id      : 'ag-command-menu-point-description',
	text    : 'Description',
	checked : false,
	checkHandler : agCommandMenuClick
};
agCommandMenuPointDrawPointIndicationLine = {
	id    : 'ag-command-menu-point-draw-point-indication-line',
	text : 'Draw Point Indication Line',
	menu : {
		items : ['<b class="menu-title">Choose a Draw Point Indication Line</b>'],
		listeners : {
			'beforeshow' : function(menu){
				var key = 'ag-command-menu-point-draw-point-indication-line-';
				var combo = Ext.getCmp('ag-command-point-description-draw-point-indication-line-combo');
				var count = menu.items.getCount();
				while(count>1){
					count--;
					var item = menu.items.get(count);
					if(item) menu.remove(item);
				}
				var records = combo.getStore().getRange();
				if(records.length==0) return;
				var items = {};
				for(var i=0;i<records.length;i++){
					items[records[i].data.value] = menu.addMenuItem({
						id      : key+records[i].data.value,
						text    : records[i].data.disp,
						value   : records[i].data.value,
						checked : false,
						group   : key+'group',
						handler : agCommandMenuClick
					});
				}
				var value = combo.getValue();
				if(items[value]) items[value].setChecked(true);
			}
		}
	}
};
agCommandMenuPoint = {
	id    : 'ag-command-menu-point',
	text  : 'Point',
	hidden : $addPointElementHidden,
	menu  : {
		items : [
			agCommandMenuPointColorMenu,
			agCommandMenuPointSphere,
			agCommandMenuPointClassificationLabel,
			agCommandMenuPointDescription,
			agCommandMenuPointDrawPointIndicationLine
		],
		listeners : {
			'beforeshow' : function(menu){
//				_dump("agCommandMenuPoint:beforeshow(1):"+menu.id);
				var description = Ext.getCmp('ag-command-point-description-check').getValue();
				Ext.getCmp('ag-command-menu-point-description').setChecked(description);
				var cmp_line = Ext.getCmp('ag-command-menu-point-draw-point-indication-line');
				if(description){
					cmp_line.enable();
				}else{
					cmp_line.disable();
				}
			}
		}
	}
};

agCommandMenuWindowControls = {
	id    : 'ag-command-menu-window-controls',
	text  : 'Window controls',
	menu  : {
		items : [
			agCommandMenuWindowSize,
			agCommandMenuWindowBackgroundColor,
			agCommandMenuDefaultPartsColor,
			agCommandMenuPoint
		]
	}
};

agMenuItemShortcutKeys = {
	id    : 'ag-menu-options-shortcut',
	text  : 'Shortcut Keys',
	handler : openOptionsShortcutKeys
};

agCommandMenuItems = [
	agCommandMenuImageControls,
	agCommandMenuSectionalView,
	agCommandMenuWindowControls,
	'-',
	agMenuItemShortcutKeys
];

function agCommandMenuClick(b,e){
//	_dump("agCommandMenuClick():["+b.xtype+"]:["+b.id+"]:["+(typeof e)+"]["+e+"]["+b.checked+"]["+b.value+"]");
	try{
		e.stopEvent();
	}catch(ex){}
	if(b.id.match(/^ag-command-menu-image-move-(.+)\$/)){
		var cmd = RegExp.\$1;
		var x = ag_param_store.getAt(0).data.image_w /2;
		var y = ag_param_store.getAt(0).data.image_h /2;
		var move_value = 15;
		if(cmd=='up' || cmd=='down' || cmd=='left' || cmd=='right'){
			if(cmd=='up'){
				y += move_value;
			}else if(cmd=='down'){
				y -= move_value;
			}else if(cmd=='left'){
				x += move_value;
			}else if(cmd=='right'){
				x -= move_value;
			}
			anatomoImgMoveCenter(x,y);
		}else if(cmd=='focus-center'){
			ag_focus(false,true);
		}else if(cmd=='focus-zoom'){
			ag_focus(false);
		}
	}else if(b.id.match(/^ag-command-menu-image-rotation-(.+)\$/)){
		var cmd = RegExp.\$1;
//		var rotation_value = 15;
		var rotation_value = 1;
		if(cmd=='up'){
			rotateVertical(-rotation_value);
		}else if(cmd=='down'){
			rotateVertical(rotation_value);
		}else if(cmd=='left'){
			rotateHorizontal(rotation_value);
		}else if(cmd=='right'){
			rotateHorizontal(-rotation_value);
		}else if(cmd.match(/(\\d+)-(\\d+)/)){
			var h = Number(RegExp.\$1);
			var v = Number(RegExp.\$2);
			if(isNaN(h) || isNaN(v)) return;
			setRotate(h,v);
		}
	}else if(b.id.match(/^ag-command-menu-image-zoom-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='up'){
			anatomoZoomUpButton();
		}else if(cmd=='down'){
			anatomoZoomDownButton();
		}
	}else if(b.id.match(/^ag-command-menu-image-grid-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='checkbox'){
			Ext.getCmp('ag-command-grid-show-check').setValue(b.checked);
		}else if(cmd.match(/^color-(.+)\$/)){
			if(Ext.isEmpty(b.value)) return;
			try{
				var cmp = Ext.getCmp('ag-command-grid-color-field');
				cmp.setValue(b.value);
				if(!cmp.menu) cmp.onTriggerClick();
				cmp.menu.palette.select(b.value);
				cmp.menu.hide();
			}catch(e){
				_dump(e);
			}
		}else if(cmd.match(/^len-(.+)\$/)){
			var cmp = Ext.getCmp('ag-command-grid-len-combobox');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}
	}else if(b.id.match(/^ag-command-menu-clip-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='checkbox'){
			Ext.getCmp('anatomo-clip-check').setValue(b.checked);
		}else if(cmd=='up'){
			anatomoClipUpButton();
		}else if(cmd=='down'){
			anatomoClipDownButton();
		}else if(cmd.match(/^method-(.+)\$/)){
			cmd = RegExp.\$1;
			var cmp = Ext.getCmp('anatomo-clip-method-combo');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}else if(cmd.match(/^predefined-plane-(.+)\$/)){
			cmd = RegExp.\$1;
			if(cmd=='FB' || cmd=='RL' || cmd=='TB' || cmd=='FREE'){
				var cmp = Ext.getCmp('anatomo-clip-predifined-plane');
				var store = cmp.getStore();
				var record = null;
				var index = store.find('value',new RegExp("^"+b.value+"\$"));
				if(index<0) return;
				var record = store.getAt(index);
				cmp.setValue(b.value);
				cmp.fireEvent('select',cmp,record,index);
			}else if(cmd=='freeplane-fix'){
				Ext.getCmp('anatomo-clip-fix-check').setValue(b.checked);
			}else if(cmd=='reverse'){
				Ext.getCmp('anatomo-clip-reverse-check').setValue(b.checked);
			}
		}
	}else if(b.id.match(/^ag-command-menu-window-size-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='autosize'){
			Ext.getCmp('anatomo-windowsize-autosize-check').setValue(b.checked);
		}else if(cmd.match(/^width-(.+)\$/)){
			Ext.getCmp('anatomo-windowsize-autosize-check').setValue(false);
			var cmp = Ext.getCmp('anatomo-width-combo');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}else if(cmd.match(/^height-(.+)\$/)){
			Ext.getCmp('anatomo-windowsize-autosize-check').setValue(false);
			var cmp = Ext.getCmp('anatomo-height-combo');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}
	}else if(b.id.match(/^ag-command-menu-window-background-color-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='transparent'){
			Ext.getCmp('anatomo-bgcolor-transparent-check').setValue(b.checked);
		}else if(cmd=='palette'){
			if(Ext.isEmpty(b.value)) return;
			try{
				var cmp = Ext.getCmp('anatomo-bgcp');
				cmp.setValue(b.value);
				if(!cmp.menu) cmp.onTriggerClick();
				cmp.menu.palette.select(b.value);
				cmp.menu.hide();
			}catch(e){
				_dump(e);
			}
		}
	}else if(b.id.match(/^ag-command-menu-default-parts-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='color'){
			if(Ext.isEmpty(b.value)) return;
			try{
				var cmp = Ext.getCmp('anatomo-default-parts-color');
				cmp.setValue(b.value);
				if(!cmp.menu) cmp.onTriggerClick();
				cmp.menu.palette.select(b.value);
				cmp.menu.hide();
			}catch(e){
				_dump(e);
			}
		}
	}else if(b.id.match(/^ag-command-menu-point-(.+)\$/)){
		var cmd = RegExp.\$1;
		if(cmd=='description'){
			Ext.getCmp('ag-command-point-description-check').setValue(b.checked);
		}else if(cmd=='color'){
			if(Ext.isEmpty(b.value)) return;
			try{
				var cmp = Ext.getCmp('anatomo-default-point-parts-color');
				cmp.setValue(b.value);
				if(!cmp.menu) cmp.onTriggerClick();
				cmp.menu.palette.select(b.value);
				cmp.menu.hide();
			}catch(e){
				_dump(e);
			}
		}else if(cmd.match(/^sphere-(.+)\$/)){
			cmd = RegExp.\$1;
			var cmp = Ext.getCmp('ag-command-point-sphere-combo');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}else if(cmd.match(/^classification-label-(.*)\$/)){
			cmd = RegExp.\$1;
			var cmp = Ext.getCmp('anatomo-point-label-combo');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}else if(cmd.match(/^draw-point-indication-line-(.+)\$/)){
			cmd = RegExp.\$1;
			var cmp = Ext.getCmp('ag-command-point-description-draw-point-indication-line-combo');
			var store = cmp.getStore();
			var record = null;
			var index = store.find('value',new RegExp("^"+b.value+"\$"));
			if(index<0) return;
			var record = store.getAt(index);
			cmp.setValue(b.value);
			cmp.fireEvent('select',cmp,record,index);
		}
	}
}

var agShortcutMenuCommands = [
	agCommandMenuImageMove,
	agCommandMenuImageRotation,
	agCommandMenuImageZoom
HTML
if($sectionalViewHidden ne 'true'){
	print <<HTML;
	,agCommandMenuClipCheckbox
HTML
}
print <<HTML;
];
function getMenuTextFromMenuId(id,pMenu){
	if(Ext.isEmpty(pMenu)){
		var commands = agShortcutMenuCommands;
		for(var i=0;i<commands.length;i++){
			if(typeof commands[i] != 'object') continue;
			var text = getMenuTextFromMenuId(id,commands[i]);
			if(!Ext.isEmpty(text)) return text;
		}
	}else{
		if(id==pMenu.id) return pMenu.text;
		if(!pMenu.menu || !pMenu.menu.items || pMenu.menu.items.length==0) return undefined;
		for(var i=0;i<pMenu.menu.items.length;i++){
			var text = getMenuTextFromMenuId(id,pMenu.menu.items[i]);
			if(!Ext.isEmpty(text)) return pMenu.text? pMenu.text + ":" + text : text;
		}
	}
}
function getAllMenuText(pMenu,menuText,menuList){
	if(Ext.isEmpty(pMenu)){
		var commands = agShortcutMenuCommands;
		var list = [];
		for(var i=0;i<commands.length;i++){
			if(typeof commands[i] != 'object') continue;
			getAllMenuText(commands[i],"",list);
		}
		return list;
	}else{
		if(pMenu.text){
			if(menuText.length>0) menuText += ":";
			menuText += pMenu.text;
		}
		if(!pMenu.menu || !pMenu.menu.items || pMenu.menu.items.length==0){
			if(pMenu.id && pMenu.text) menuList.push({id:pMenu.id,text:menuText});
		}else{
			for(var i=0;i<pMenu.menu.items.length;i++){
				getAllMenuText(pMenu.menu.items[i],menuText,menuList);
			}
		}
	}
}
var agCommandArr = [];
var agKeyArr = [];
var list = getAllMenuText();
var span = document.createElement('span');
for(var i=0;i<list.length;i++){
	span.innerHTML = list[i].text;
	agCommandArr.push([list[i].id,span.textContent]);
}
span = undefined;
agKeyMapNames.sort();
for(var i=0;i<agKeyMapNames.length;i++){
	agKeyArr.push([agKeyMapNames[i],agKeyMapNames[i]]);
}

function openOptionsShortcutKeys(b,e){
	try{
		e.stopEvent();
	}catch(ex){}

	var ag_shortcut_keys_grid_shift_checkColumn = new Ext.grid.CheckColumn({
		id:'shift',
		dataIndex:'shift',
		header:'Shift',
		width:40,
		sortable: true,
		align:'center'
	});
	var ag_shortcut_keys_grid_ctrl_checkColumn = new Ext.grid.CheckColumn({
		id:'ctrl',
		dataIndex:'ctrl',
		header:'Ctrl',
		width:40,
		sortable: true,
		align:'center'
	});
	var ag_shortcut_keys_grid_alt_checkColumn = new Ext.grid.CheckColumn({
		id:'alt',
		dataIndex:'alt',
		header:'Alt',
		width:40,
		sortable: true,
		align:'center'
	});
	var ag_shortcut_keys_grid_stop_checkColumn = new Ext.grid.CheckColumn({
		id:'stop',
		dataIndex:'stop',
		header:'Stop',
		width:40,
		align:'center',
		sortable: true,
		hidden:true
	});

	function ag_shortcut_keys_grid_command_renderer(value,metadata,record,rowIndex,colIndex,store){
		var text = getMenuTextFromMenuId(value);
		return text?text:value;
	}

	var ag_shortcut_keys_window = new Ext.Window({
		title       : 'Shortcut Keys',
		width       : 600,
		height      : 500,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'right',
		modal       : true,
		resizable   : true,
		border      : false,
		layout      : 'border',
		items: [{
			id : 'ag-shortcut-keys-window-grid',
			region : 'center',
			xtype : 'grid',
			store : ag_keymap_store,
			colModel: new Ext.grid.ColumnModel({
				columns : [
					{id:'order', dataIndex:'order', header:'#',     width:30, sortable:true, align:'right'},
					{id:'key',   dataIndex:'key',   header:'Key',   width:80, sortable:true, align:'left'},
					{id:'code',  dataIndex:'code',  header:'Code',  width:30, sortable:true, align:'right', hidden:true},
					ag_shortcut_keys_grid_shift_checkColumn,
					ag_shortcut_keys_grid_ctrl_checkColumn,
					ag_shortcut_keys_grid_alt_checkColumn,
					ag_shortcut_keys_grid_stop_checkColumn,
					{id:'cmd',   dataIndex:'cmd',   header:'Command',sortable:true,align:'left',renderer:ag_shortcut_keys_grid_command_renderer}
				]
			}),
			plugins        : [
				ag_shortcut_keys_grid_shift_checkColumn,
				ag_shortcut_keys_grid_ctrl_checkColumn,
				ag_shortcut_keys_grid_alt_checkColumn,
				ag_shortcut_keys_grid_stop_checkColumn
			],
			listeners : {
				'beforeedit' : function(e){
						e.cancel = true;
				},
				'rowclick' : function(grid,rowIndex,e){
				}
			},
			autoExpandColumn : 'cmd',
			autoExpandMin : 80,
			stripeRows : true,
			columnLines    : true,
			sm: new Ext.grid.RowSelectionModel({
				singleSelect:true,
				listeners : {
					'rowselect' : function(sm,rowIndex,record){
						var key_combo = Ext.getCmp('ag-shortcut-keys-window-key-combo');
						var shift_checkbox = Ext.getCmp('ag-shortcut-keys-window-shift-checkbox');
						var ctrl_checkbox = Ext.getCmp('ag-shortcut-keys-window-ctrl-checkbox');
						var alt_checkbox = Ext.getCmp('ag-shortcut-keys-window-alt-checkbox');
						var command_combo = Ext.getCmp('ag-shortcut-keys-window-command-combo');

						key_combo.enable();
						shift_checkbox.enable();
						ctrl_checkbox.enable();
						alt_checkbox.enable();
						command_combo.enable();

						key_combo.setValue(record.get('key'));
						shift_checkbox.setValue(record.get('shift'));
						ctrl_checkbox.setValue(record.get('ctrl'));
						alt_checkbox.setValue(record.get('alt'));
						command_combo.setValue(record.get('cmd'));

						var down_button = Ext.getCmp('ag-shortcut-keys-window-grid-down-button');
						var up_button = Ext.getCmp('ag-shortcut-keys-window-grid-up-button');
						var delete_button = Ext.getCmp('ag-shortcut-keys-window-grid-delete-button');
						if(rowIndex==record.store.getCount()-1){
							down_button.disable();
						}else{
							down_button.enable();
						}
						if(rowIndex==0){
							up_button.disable();
						}else{
							up_button.enable();
						}
						delete_button.enable();
					},
					'selectionchange' : function(sm){
						if(sm.getCount()>0) return;
						var key_combo = Ext.getCmp('ag-shortcut-keys-window-key-combo');
						var shift_checkbox = Ext.getCmp('ag-shortcut-keys-window-shift-checkbox');
						var ctrl_checkbox = Ext.getCmp('ag-shortcut-keys-window-ctrl-checkbox');
						var alt_checkbox = Ext.getCmp('ag-shortcut-keys-window-alt-checkbox');
						var command_combo = Ext.getCmp('ag-shortcut-keys-window-command-combo');
						key_combo.disable();
						shift_checkbox.disable();
						ctrl_checkbox.disable();
						alt_checkbox.disable();
						command_combo.disable();

						key_combo.clearValue();
						shift_checkbox.setValue(false);
						ctrl_checkbox.setValue(false);
						alt_checkbox.setValue(false);
						command_combo.clearValue();

						var down_button = Ext.getCmp('ag-shortcut-keys-window-grid-down-button');
						var up_button = Ext.getCmp('ag-shortcut-keys-window-grid-up-button');
						var delete_button = Ext.getCmp('ag-shortcut-keys-window-grid-delete-button');
						down_button.disable();
						up_button.disable();
						delete_button.disable();
					}
				}
			}),
			tbar : ['->','-',{
				id : 'ag-shortcut-keys-window-grid-add-button',
				iconCls  : 'pallet_add',
				handler  : function(button, e){
					var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
					var sel = grid.getSelectionModel();
					var store = grid.getStore();
					var count = store.getCount();
					var ag_keymap_record = Ext.data.Record.create(ag_keymap_fields);
					var new_record = new ag_keymap_record({
						order : count+1,
						shift : false,
						ctrl  : false,
						alt   : false,
						stop  : true
					});
					store.add(new_record);
					sel.selectLastRow();
				}
			},'-',{
				id : 'ag-shortcut-keys-window-grid-down-button',
				iconCls  : 'pallet_down',
				disabled : true,
				handler  : function(button, e){
					var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
					var sel = grid.getSelectionModel();
					var record  = sel.getSelected();
					if(Ext.isEmpty(record)) return;
					var store = record.store;
					var index = store.indexOf(record);
					var n_record = store.getAt(index+1);

					var order = record.get('order');
					var n_order = n_record.get('order');

					record.beginEdit();
					record.set('order',n_order);
					record.commit();
					record.endEdit();

					n_record.beginEdit();
					n_record.set('order',order);
					n_record.commit();
					n_record.endEdit();

					var sort_state = store.getSortState();
					store.sort(sort_state.field,sort_state.direction);
				}
			},{
				id : 'ag-shortcut-keys-window-grid-up-button',
				iconCls  : 'pallet_up',
				disabled : true,
				handler  : function(button, e){
					var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
					var sel = grid.getSelectionModel();
					var record  = sel.getSelected();
					if(Ext.isEmpty(record)) return;
					var store = record.store;
					var index = store.indexOf(record);
					var p_record = store.getAt(index-1);

					var order = record.get('order');
					var p_order = p_record.get('order');

					record.beginEdit();
					record.set('order',p_order);
					record.commit();
					record.endEdit();

					p_record.beginEdit();
					p_record.set('order',order);
					p_record.commit();
					p_record.endEdit();

					var sort_state = store.getSortState();
					store.sort(sort_state.field,sort_state.direction);
				}
			},'-',{
				id : 'ag-shortcut-keys-window-grid-delete-button',
				tooltip  : 'Delete Selected',
				iconCls  : 'pallet_delete',
				disabled : true,
				handler  : function(button, e){
					var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
					var sel = grid.getSelectionModel();
					var record  = sel.getSelected();
					if(Ext.isEmpty(record)) return;
					var store = record.store;
					store.remove(record);
					var count = store.getCount();
					if(count == 0){
						store.removeAll();
					}else{
						for(var i=0;i<count;i++){
							record = store.getAt(i);
							var order = (i+1);
							if(record.get('order') == order) continue;
							record.beginEdit();
							record.set('order',order);
							record.commit();
							record.endEdit();
						}
					}
					sel.clearSelections();

					var key_combo = Ext.getCmp('ag-shortcut-keys-window-key-combo');
					var shift_checkbox = Ext.getCmp('ag-shortcut-keys-window-shift-checkbox');
					var ctrl_checkbox = Ext.getCmp('ag-shortcut-keys-window-ctrl-checkbox');
					var alt_checkbox = Ext.getCmp('ag-shortcut-keys-window-alt-checkbox');
					var command_combo = Ext.getCmp('ag-shortcut-keys-window-command-combo');
					key_combo.clearValue();
					shift_checkbox.setValue(false);
					ctrl_checkbox.setValue(false);
					alt_checkbox.setValue(false);
					command_combo.clearValue();

				}
			}]
		},{
			region : 'east',
			width  : 250,
			layout : 'form',
			labelWidth : 60,
			labelAlign : 'right',
			bodyStyle   : 'padding:5px;',
			items  : [{
				disabled : true,
				id:'ag-shortcut-keys-window-key-combo',
				fieldLabel:'Key',
				xtype : 'combo',
				typeAhead: true,
				triggerAction: 'all',
				lazyRender:true,
				mode: 'local',
				width:160,
				store: new Ext.data.SimpleStore({
					id: 0,
					fields: [
						'value',
						'disp'
					],
					data: agKeyArr
				}),
				valueField: 'value',
				displayField: 'disp',
				listeners     : {
					'select' : function(combo,record,index){
						var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
						var sel = grid.getSelectionModel();
						var record  = sel.getSelected();
						if(Ext.isEmpty(record)) return;
						record.beginEdit();
						record.set('key',combo.getValue());
						record.commit();
						record.endEdit();
					},scope : this
				}
			},{
				border : false,
				bodyStyle   : 'padding:5px;text-align:center;',
				layout      : 'column',
				items : [{
					columnWidth: .33,
					id:'ag-shortcut-keys-window-shift-checkbox',
					disabled : true,
					hideLabel : true,
					boxLabel : 'Shift',
					xtype    : 'checkbox',
					handler  : function(checkbox, e){
						var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
						var sel = grid.getSelectionModel();
						var record  = sel.getSelected();
						if(Ext.isEmpty(record)) return;
						record.beginEdit();
						record.set('shift',checkbox.getValue());
						record.commit();
						record.endEdit();
					}
				},{
					columnWidth: .33,
					id:'ag-shortcut-keys-window-ctrl-checkbox',
					disabled : true,
					hideLabel : true,
					boxLabel : 'Ctrl',
					xtype    : 'checkbox',
					handler  : function(checkbox, e){
						var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
						var sel = grid.getSelectionModel();
						var record  = sel.getSelected();
						if(Ext.isEmpty(record)) return;
						record.beginEdit();
						record.set('ctrl',checkbox.getValue());
						record.commit();
						record.endEdit();
					}
				},{
					columnWidth: .33,
					id:'ag-shortcut-keys-window-alt-checkbox',
					disabled : true,
					hideLabel : true,
					boxLabel : 'Alt',
					xtype    : 'checkbox',
					handler  : function(checkbox, e){
						var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
						var sel = grid.getSelectionModel();
						var record  = sel.getSelected();
						if(Ext.isEmpty(record)) return;
						record.beginEdit();
						record.set('alt',checkbox.getValue());
						record.commit();
						record.endEdit();
					}
				}]
			},{
				disabled : true,
				id:'ag-shortcut-keys-window-command-combo',
				fieldLabel:'Command',
				xtype : 'combo',
				typeAhead: true,
				triggerAction: 'all',
				lazyRender:true,
				mode: 'local',
				width:160,
				store: new Ext.data.SimpleStore({
					id: 0,
					fields: [
						'value',
						'disp'
					],
					data: agCommandArr
				}),
				valueField: 'value',
				displayField: 'disp',
				listeners     : {
					'select' : function(combo,record,index){
						var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
						var sel = grid.getSelectionModel();
						var record  = sel.getSelected();
						if(Ext.isEmpty(record)) return;
						record.beginEdit();
						record.set('cmd',combo.getValue());
						record.commit();
						record.endEdit();
					},scope : this
				}
			}]
		}],
		buttons : [{
			text    : 'OK',
			handler : function(){
				var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
				var sel = grid.getSelectionModel();
				var store = grid.getStore();
				var records = store.getRange();
				glb_us_keymap.length=0;
				var order = 0;
				for(var i=0;i<records.length;i++){
					var key = records[i].get('key');
					var cmd = records[i].get('cmd');
					if(Ext.isEmpty(key) || Ext.isEmpty(cmd)) continue;
					var code = Ext.EventObject[key];
					order++;
					glb_us_keymap.push({
						order : order,
						key   : key,
						code  : code,
						shift : records[i].get('key'),
						ctrl  : records[i].get('ctrl'),
						alt   : records[i].get('alt'),
						stop  : records[i].get('stop'),
						cmd   : cmd
					});
				}
				ag_put_usersession_task.delay(1000);
				ag_shortcut_keys_window.close();
				agKeyMapExec();
			}
		},{
			text    : 'Cencel',
			handler : function(){
				var grid = Ext.getCmp('ag-shortcut-keys-window-grid');
				var sel = grid.getSelectionModel();
				var store = grid.getStore();
				ag_shortcut_keys_window.close();
				store.loadData({keymaps:glb_us_keymap});
			}
		}]
	});
	ag_shortcut_keys_window.show();
}

agOptionsMenuItems = [
	agMenuItemShortcutKeys
];

HTML
