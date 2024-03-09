#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use File::Basename;
use URI::Split;
use LWP::UserAgent;
use HTTP::Headers;
use HTTP::Request;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

#my $wiki_url = qq|http://221.186.138.155/project/anatomo_wiki/en/index.php|;
#my $wiki_url = qq|http://lifesciencedb.jp:32888/bp3d-38321/wiki/index.php|;
#http://192.168.1.237/bp3d-38321/wiki/index.php?title=Special:OpenIDLogin&openid_url=
#http://192.168.1.237/bp3d-38321/wiki/index.php?title=Special:UserLogout&returnto=Special:OpenIDFinish
#api.php ? action=logout
my $wiki_url = qq|wiki/index.php|;
my $wiki_target = qq|_blank|;
my $wiki_style = qq|width=800,height=600,dependent=yes,scrollbars=yes,resizable=yes|;

my $wiki_key = qq|ag_wiki|;
my $wiki_api_url = qq|wiki/api.php|;
my $wiki_api_logout_params = qq|{action:'logout'}|;
my $wiki_login_query = qq|?title=Special:OpenIDLogin&openid_url=|;

if(defined $ENV{HTTP_REFERER}){
	my($scheme, $auth, $path, $query, $frag) = &URI::Split::uri_split($ENV{HTTP_REFERER});
	$path = &File::Basename::dirname($path) unless($path =~ /\/$/);
	$path .= '/' unless($path =~ /\/$/);
	$wiki_url = &URI::Split::uri_join($scheme, $auth, qq|$path$wiki_url|);
	$wiki_api_url = &URI::Split::uri_join($scheme, $auth, qq|$path$wiki_api_url|);
}


my $disEnv = &getDispEnv();
my $additionalModelsImpossible = $disEnv->{additionalModelsImpossible};
my $copyHidden = $disEnv->{copyHidden};
my $editLSDBTermHidden = $disEnv->{editLSDBTermHidden};
my $groupHidden = $disEnv->{groupHidden};
my $informationHidden = $disEnv->{informationHidden};
my $linkEmbedHidden = $disEnv->{linkEmbedHidden};
my $reviewHidden = $disEnv->{reviewHidden};
my $rootVisible = $disEnv->{rootVisible};
my $urlAnalysisHidden = $disEnv->{urlAnalysisHidden};
my $palletSelectAllHidden = $disEnv->{palletSelectAllHidden};
my $coordinateSystemHidden = $disEnv->{coordinateSystemHidden};
my $useUniversalID = $disEnv->{useUniversalID};
my $shortURLHidden = $disEnv->{shortURLHidden};
my $treeGroupHidden = $disEnv->{treeGroupHidden};
my $copyThumbnailHidden = $disEnv->{copyThumbnailHidden};
my $localeMenuHidden = $disEnv->{localeMenuHidden};
my $addPointElementHidden = $disEnv->{addPointElementHidden};
my $wikiLinkHidden = $disEnv->{wikiLinkHidden};
my $useColorPicker = $disEnv->{useColorPicker};
my $hiddenGridColNameJ = $disEnv->{hiddenGridColNameJ};

my $showGridColPartsExists = $disEnv->{showGridColPartsExists};
my $localeMenuIcon = $disEnv->{localeMenuIcon};
my $hiddenGridColZmin = $disEnv->{hiddenGridColZmin};
my $hiddenGridColZmax = $disEnv->{hiddenGridColZmax};
my $removeGridColValume = $disEnv->{removeGridColValume};
my $removeGridColOrganSystem = $disEnv->{removeGridColOrganSystem};
my $moveLicensesPanel = $disEnv->{moveLicensesPanel};

my $useTabTip = $disEnv->{useTabTip};
my $defaultLocaleJa = $disEnv->{defaultLocaleJa};
my $moveGridOrder = $disEnv->{moveGridOrder};
my $useContentsTree = $disEnv->{useContentsTree};
my $useNavigateRange = $disEnv->{useNavigateRange};

my $useTwitter = $disEnv->{useTwitter};
my $makeGotoAGButton = $disEnv->{makeGotoAGButton};
my $makeExtraToolbar = $disEnv->{makeExtraToolbar};

my $useWikiUserAuth = $disEnv->{useWikiUserAuth};

$additionalModelsImpossible = 'false' unless(defined $additionalModelsImpossible);
$copyHidden = 'false' unless(defined $copyHidden);
$editLSDBTermHidden = 'false' unless(defined $editLSDBTermHidden);
$groupHidden = 'false' unless(defined $groupHidden);
$informationHidden = 'true' unless(defined $informationHidden);
$linkEmbedHidden = 'false' unless(defined $linkEmbedHidden);
$reviewHidden = 'false' unless(defined $reviewHidden);
$rootVisible = 'true' unless(defined $rootVisible);
$urlAnalysisHidden = 'false' unless(defined $urlAnalysisHidden);
$palletSelectAllHidden = 'false' unless(defined $palletSelectAllHidden);
$coordinateSystemHidden = 'false' unless(defined $coordinateSystemHidden);
$useUniversalID = 'true' unless(defined $useUniversalID);
$shortURLHidden = 'false' unless(defined $shortURLHidden);
$copyThumbnailHidden = 'false' unless(defined $copyThumbnailHidden);
$localeMenuHidden = 'false' unless(defined $localeMenuHidden);
$addPointElementHidden = 'false' unless(defined $addPointElementHidden);
$wikiLinkHidden = 'false' unless(defined $wikiLinkHidden);
$useColorPicker = 'true' unless(defined $useColorPicker);
$hiddenGridColNameJ = 'true' unless(defined $hiddenGridColNameJ);
$showGridColPartsExists = 'true' unless(defined $showGridColPartsExists);
$localeMenuIcon = 'true' unless(defined $localeMenuIcon);
$hiddenGridColZmin = 'true' unless(defined $hiddenGridColZmin);
$hiddenGridColZmax = 'true' unless(defined $hiddenGridColZmax);
$removeGridColValume = 'true' unless(defined $removeGridColValume);
$removeGridColOrganSystem = 'true' unless(defined $removeGridColOrganSystem);
$moveLicensesPanel = 'true' unless(defined $moveLicensesPanel);

$useTabTip = 'true' unless(defined $useTabTip);
$defaultLocaleJa = 'true' unless(defined $defaultLocaleJa);
$moveGridOrder = 'true' unless(defined $moveGridOrder);
$useContentsTree = 'true' unless(defined $useContentsTree);
$useNavigateRange = 'true' unless(defined $useNavigateRange);

$useTwitter = 'true' unless(defined $useTwitter);
#$useTwitter = 'false' unless(defined $useTwitter);
$makeGotoAGButton = 'true' unless(defined $makeGotoAGButton);
$makeExtraToolbar = 'true' unless(defined $makeExtraToolbar);

#$useWikiUserAuth = 'true' unless(defined $useWikiUserAuth);
$useWikiUserAuth = 'false' unless(defined $useWikiUserAuth);

#$rootVisible = 'true';
my $toppageHidden = $rootVisible eq 'true' ? 'false' : 'true';

my $linkWindowItemAnchor;
if($shortURLHidden ne 'true'){
	$linkWindowItemAnchor = $linkEmbedHidden ne 'true' ? '100% -216' : '100% -160';
}else{
	$linkWindowItemAnchor = $linkEmbedHidden ne 'true' ? '100% -233' : '100% -176';
}

my $gridColHiddenUniversalID = $useUniversalID eq 'true' ? 'false' : 'true';
my $gridColFixedUniversalID = $useUniversalID eq 'true' ? 'false' : 'true';
my $gridColHiddenID = $useUniversalID eq 'true' ? 'true' : 'false';

#DEBUG
#$wikiLinkHidden = 'false';
$wikiLinkHidden = 'true';
$editLSDBTermHidden = 'true';

my $urlTwitterTweetBP3D = qq|twitter/tweet-bp3d.html?hashtags=bp3d&text=|;
my $urlTwitterTweetAG = qq|twitter/tweet-ag.html?hashtags=anagra&text=Anatomography|;
my $urlTwitterTimeline = qq|twitter/timeline.html|;
my $urlTwitterTimeline_bp3d = qq|twitter/timeline-bp3d.html|;
my $urlTwitterTimeline_ag = qq|twitter/timeline-ag.html|;

#2013年度下期納品用
$rootVisible = 'true';
$useContentsTree='false';

my %LOCALE = ();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my $load_session;
#if(!exists($FORM{tp_ap}) && exists($COOKIE{'ag_annotation.session'})){
#	my $session = &getSession($COOKIE{'ag_annotation.session'});
#	if(defined $session){
#		$FORM{tp_ap} = join("&",@$session);
#		$load_session = 1;
#	}
#}
undef $load_session;#フラグをundefすることにより、最初の仕様に戻す。フラグの値を有効にすることにより、パラメータ指定時にのみ、anatomographyタブを開く
my $open_tab_bodyparts_panel = 1;#常にbodypartsタブを開く場合
undef $open_tab_bodyparts_panel;

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" unless(exists($FORM{lng}));

my $gridColHiddenNameJ = 'false';
if($hiddenGridColNameJ eq 'true' && $FORM{lng} ne 'ja'){
	$gridColHiddenNameJ = 'true';
}

require "anatomography_locale.pl";
my %LOCALE_ANA = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_ANA)){
	$LOCALE{$key} = $LOCALE_ANA{$key}
}
undef %LOCALE_ANA;

require "common_locale.pl";
my %LOCALE_BP3D = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_BP3D)){
	$LOCALE{$key} = $LOCALE_BP3D{$key}
}
undef %LOCALE_BP3D;

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

my $dbh = &get_dbh();

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
my $log_file = &catfile($FindBin::Bin,'logs',(exists $COOKIE{'ag_annotation.session'} && defined $COOKIE{'ag_annotation.session'} && length $COOKIE{'ag_annotation.session'} ? $COOKIE{'ag_annotation.session'} : '') . qq|.$cgi_name.txt|);
my $LOG;
open($LOG,"> $log_file");
print $LOG "\n[$logtime]:$0\n";
&cgi_lib::common::dumper(\%FORM,$LOG) if(defined $LOG);
&cgi_lib::common::dumper(\%COOKIE,$LOG) if(defined $LOG);
&cgi_lib::common::dumper(\%ENV,$LOG) if(defined $LOG);
close($LOG);

#DEBUG 常に削除
#delete $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
my $is_success;
my $parentURL = $FORM{parent} if(exists $FORM{parent} && defined $FORM{parent});
#delete $FORM{parent} if(exists($FORM{parent}));
$FORM{parent} = '' unless(exists $FORM{parent} && defined $FORM{parent});

if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
#	print LOG __LINE__,":\$lsdb_OpenID=[$lsdb_OpenID]\n";
#	print LOG __LINE__,":\$lsdb_Auth=[$lsdb_Auth]\n";
#	print LOG __LINE__,":\$lsdb_Config=[$lsdb_Config]\n";
#	print LOG __LINE__,":\$lsdb_Identity=[$lsdb_Identity]\n";
}
if($useWikiUserAuth eq 'true'){
	unless(defined $lsdb_OpenID && defined $lsdb_Auth && defined $lsdb_Config){
		if(exists($COOKIE{$wiki_key.qq|UserID|}) && exists($COOKIE{$wiki_key.qq|OpenID|})){
			my $ua = LWP::UserAgent->new;
			my $req = HTTP::Request->new(GET => qq|$wiki_api_url?action=query&meta=userinfo&uiprop=rights&format=json|);
			$req->header("Cookie"=>"cookiename=$ENV{HTTP_COOKIE}");
			my $res= $ua->request($req);
			if($res->is_success){
				my $json;
				eval{$json = JSON::XS::decode_json($res->content);};
				if(defined $json && defined $json->{'query'} && defined $json->{'query'}->{'userinfo'}){
					$lsdb_OpenID = $COOKIE{$wiki_key.qq|OpenID|};
					if(defined $json->{'query'}->{'userinfo'}->{'name'}){
						$lsdb_Identity = {} unless(defined $lsdb_Identity);
						$lsdb_Identity->{'display'} = $json->{'query'}->{'userinfo'}->{'name'};
					}
					if(defined $json->{'query'}->{'userinfo'}->{'rights'} && ref $json->{'query'}->{'userinfo'}->{'rights'} eq 'ARRAY'){
						my %rights = map {$_ => undef } @{$json->{'query'}->{'userinfo'}->{'rights'}};
						$lsdb_Auth = '1' if(exists($rights{'edit'}));
					}
				}
			}
		}
	}
}


$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);
#close(LOG);

my $user_name = '';
my $login_label = 'Login';
my $login_func = 'tbarBodypartsLogin';
if(defined $lsdb_OpenID){
	$login_label = qq|Logout|;
	if(defined $lsdb_Identity && defined $lsdb_Identity->{display}){
		$login_label .= qq| - | . $lsdb_Identity->{display};
		$user_name = $lsdb_Identity->{display};
	}else{
		$login_label .= qq| [ $lsdb_OpenID ]|;
	}
	$login_func = 'tbarBodypartsLogout';
}

#my $localeMenuHidden = 'true';

my $locale_label = "Eng";
my $locale_icon = "";
my $locale_cls = "";
if($localeMenuIcon eq 'true'){
	$locale_label = "English";
#	$locale_icon = "css/us.png";
#	$locale_icon = "css/gb.png";
	$locale_icon = "";
	$locale_cls = "";
	if($FORM{lng} eq "en"){
		$locale_label = "";
		$locale_icon = "css/jp.png";
#		$locale_cls = "x-btn-text-icon";
		$locale_cls = "x-btn-icon";
	}
}else{
	$locale_label = "Jpn" if($FORM{lng} eq "en");
}

my $enableDD = 'false';
$enableDD = 'true' if($lsdb_Auth);

#my $rootVisible = 'true';
#my $reviewHidden = 'false';
#my $informationHidden = 'true';
$informationHidden = 'true';
$reviewHidden = 'true';

my %CONFIG = ();
if(defined $lsdb_Config && $lsdb_Config ne ""){
	&getConfig(\%CONFIG,$lsdb_Config);
	if(!exists($FORM{height})){
		$FORM{height} = $CONFIG{height} if(exists($CONFIG{height}) && !exists($FORM{height}));
		$FORM{page}   = $CONFIG{page}   if(exists($CONFIG{page})   && !exists($FORM{page}));
		$FORM{show}   = $CONFIG{show}   if(exists($CONFIG{show})   && !exists($FORM{show}));
		$FORM{la}     = $CONFIG{la}     if(exists($CONFIG{la})     && !exists($FORM{la}));
		$FORM{query}  = $CONFIG{query}  if(exists($CONFIG{query})  && !exists($FORM{query}));
		$FORM{au}     = $CONFIG{au}     if(exists($CONFIG{au})     && !exists($FORM{au}));
		$FORM{ad}     = $CONFIG{ad}     if(exists($CONFIG{ad})     && !exists($FORM{ad}));
		$FORM{jid}    = $CONFIG{jid}    if(exists($CONFIG{jid})    && !exists($FORM{jid}));
		$FORM{iss}    = $CONFIG{iss}    if(exists($CONFIG{iss})    && !exists($FORM{iss}));
		$FORM{la}     = $CONFIG{la}     if(exists($CONFIG{la})     && !exists($FORM{la}));
		if(exists($CONFIG{dtype}) && !exists($FORM{dtype})){
			$FORM{dtype} = $CONFIG{dtype};
			$FORM{fixed} = $CONFIG{fixed} if(exists($CONFIG{fixed}) && !exists($FORM{fixed}));
		}
	}
}
my %PARENT = ();
&getParent(\%PARENT,$parentURL) if(defined $parentURL);

my $LOADING_IMG = qq|ext-2.2.1/resources/images/default/tree/loading.gif|;
my $LOADING_MSG = qq|<div style="padding:10px;font-size:11px;"><img src="$LOADING_IMG">'+get_ag_lang('MSG_LOADING_DATA')+'</div>|;

my $TIME_FORMAT = "Y/m/d H:i:s";
my $DATE_FORMAT = "Y/m/d";

my $DEF_COLOR = &getDefaultColor();

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


my $info_html = 'info.html';
$info_html = 'info_en.html' if(exists($FORM{lng}) && $FORM{lng} eq "en" && -e 'info_en.html');

my $app_path = &getGlobalPath();
if(defined $app_path){
#	$app_path .= qq|ag_annotation.cgi?|;
}else{
	my $host = (split(/,\s*/,(exists($ENV{HTTP_X_FORWARDED_HOST})?$ENV{HTTP_X_FORWARDED_HOST}:$ENV{HTTP_HOST})))[0];
	my @TEMP = split("/",$ENV{REQUEST_URI});
	my $sc_name = (split(/\?/,pop @TEMP))[0];
	undef @TEMP;
	$app_path = (split(/\?/,$ENV{REQUEST_URI}))[0];
#	$app_path =~ s/$sc_name/ag_annotation.cgi/;
	$app_path =~ s/$sc_name//;
	$app_path = qq|http://$host$app_path|;
}
$app_path .= qq|?|;

my @COMMENT_STATUS = ();
my $column_number;
my $cs_id;
my $cs_name;
my $sql  = qq|select|;
$sql .= qq| comment_status.cs_id|;
$sql .= qq|,comment_status.cs_name|;
$sql .= qq| from comment_status|;
$sql .= qq| where comment_status.cs_delcause is null|;
$sql .= qq| order by comment_status.cs_id|;
my $sth = $dbh->prepare($sql);
$sth->execute();
if($sth->rows>0){
	$column_number = 0;
	$sth->bind_col(++$column_number, \$cs_id, undef);
	$sth->bind_col(++$column_number, \$cs_name, undef);
	while($sth->fetch){
		push(@COMMENT_STATUS,{
			cs_id   => $cs_id,
			cs_name => $cs_name
		});
	}
}
$sth->finish();
undef $sth;

my $tree_class_conventional_id = 1;
my $tree_class_isa_id = 3;
my $tree_class_partof_id = 4;
my $tree_class;
if($lsdb_Auth){
	$tree_class = qq|[|;
	$tree_class .= qq|['$tree_class_conventional_id', '$LOCALE{TREE_TYPE_1}']|;
	$tree_class .= qq|,['2', '$LOCALE{TREE_TYPE_2}']|;
	$tree_class .= qq|,['$tree_class_isa_id', '$LOCALE{TREE_TYPE_3}']|;
	$tree_class .= qq|,['$tree_class_partof_id', '$LOCALE{TREE_TYPE_4}']|;
	$tree_class .= qq|,['5', '123(is-a)']|;
	$tree_class .= qq|,['6', '123(combined)']|;
	$tree_class .= qq|,['7', '1w2(is-a)']|;
	$tree_class .= qq|,['8', '1w2(combined)']|;
#	$tree_class .= qq|,['9', '113(is-a)']|;
#	$tree_class .= qq|,['10', '113(combined)']|;
	$tree_class .= qq|]|;
}else{
#	$tree_class = qq|[['$tree_class_conventional_id', '$LOCALE{TREE_TYPE_1}'],['2', '$LOCALE{TREE_TYPE_2}'],['$tree_class_isa_id', '$LOCALE{TREE_TYPE_3}'],['$tree_class_partof_id', '$LOCALE{TREE_TYPE_4}']]|;
	$tree_class = qq|[|;
	$tree_class .= qq| ['$tree_class_conventional_id', '$LOCALE{TREE_TYPE_1}']|;
#	$tree_class .= qq|,['101', '$LOCALE{TREE_TYPE_1} (TA or BP3D)']|;
#	$tree_class .= qq|,['102', '$LOCALE{TREE_TYPE_1} (BP3D)']|;
#	$tree_class .= qq|,['103', '$LOCALE{TREE_TYPE_1} (TA)']|;
#	$tree_class .= qq|,['104', '$LOCALE{TREE_TYPE_1} (TA and BP3D)']|;
#	$tree_class .= qq|,['2', '$LOCALE{TREE_TYPE_2}']|;
	$tree_class .= qq|,['$tree_class_isa_id', '$LOCALE{TREE_TYPE_3}']|;
	$tree_class .= qq|,['$tree_class_partof_id', '$LOCALE{TREE_TYPE_4}']|;
	$tree_class .= qq|,['301', '$LOCALE{TREE_TYPE_3} (TA or BP3D)']|;
	$tree_class .= qq|,['302', '$LOCALE{TREE_TYPE_3} (BP3D)']|;
	$tree_class .= qq|,['303', '$LOCALE{TREE_TYPE_3} (TA)']|;
#	$tree_class .= qq|,['304', '$LOCALE{TREE_TYPE_3} (TA and BP3D)']|;
	$tree_class .= qq|,['401', '$LOCALE{TREE_TYPE_4} (TA or BP3D)']|;
	$tree_class .= qq|,['402', '$LOCALE{TREE_TYPE_4} (BP3D)']|;
	$tree_class .= qq|,['403', '$LOCALE{TREE_TYPE_4} (TA)']|;
#	$tree_class .= qq|,['404', '$LOCALE{TREE_TYPE_4} (TA and BP3D)']|;
#	$tree_class .= qq|,['101', 'Talairach']|;
	$tree_class .= qq|]|;
}

$sql = qq|select tg_id|;
if($FORM{lng} eq "ja"){
	$sql .= qq|,COALESCE(tg_name_j,tg_name_e)|;
}else{
	$sql .= qq|,tg_name_e|;
}
$sql .= qq| as tg_name from tree_group where tg_delcause is null order by tg_order|;

my @TREE_GROUP = ();
my %ID2TREE_GROUP = ();
my %TREE_GROUP2ID = ();
my $tg_id;
my $tg_name;
my $sth_tree_group = $dbh->prepare($sql);
$sth_tree_group->execute();
$column_number = 0;
$sth_tree_group->bind_col(++$column_number, \$tg_id, undef);
$sth_tree_group->bind_col(++$column_number, \$tg_name, undef);
while($sth_tree_group->fetch){
	my @TEMP = ($tg_id,$tg_name);
	next if(defined $treeGroupHidden && defined $treeGroupHidden->{$tg_id} && exists($treeGroupHidden->{$tg_id}));
	push(@TREE_GROUP,\@TEMP);
	$ID2TREE_GROUP{$tg_id} = $tg_name;
	$TREE_GROUP2ID{$tg_name} = $tg_id;
}
$sth_tree_group->finish;
undef $sth_tree_group;
#my $tree_group = to_json(\@TREE_GROUP);
my $tree_group = encode_json(\@TREE_GROUP);
#my $id2tree_group = to_json(\%ID2TREE_GROUP);
my $id2tree_group = encode_json(\%ID2TREE_GROUP);
#my $tree_group2id = to_json(\%TREE_GROUP2ID);
my $tree_group2id = encode_json(\%TREE_GROUP2ID);

if(exists $ENV{REQUEST_METHOD}){
	print qq|Content-type: text/javascript; charset=UTF-8\n|;
	print qq|\n|;
}
if(scalar @COMMENT_STATUS > 0){
	print qq|var comment_status = [];\n|;
	foreach my $cs (@COMMENT_STATUS){
		print qq|comment_status[$cs->{cs_id}]="$cs->{cs_name}";\n|;
	}
}

#if(exists($FORM{tp_ap})){
#	my $value = $FORM{tp_ap};
#	$value =~ s/[^\\]"/\\"/g;
#	$value =~ s/[\r\n]+//g;
#	print qq|var gBP3D_TPAP = Ext.urlDecode("$value");\n|;
#}else{
	print qq|var gBP3D_TPAP;\n|;
#}

print <<HTML;
var gSelNode = null;
var gDispAnatomographyPanel = false;
var gID2TreeGroup = $id2tree_group;
var gTreeGroup2ID = $tree_group2id;

//isEditablePartsList = function(){
//	var disabled = true;
//	try{disabled = Ext.getCmp('bp3d-home-group-btn').disabled;}catch(e){}
//	return disabled;
//};

makeCopyListText = function(grid,records){
	try{
		var radio = Ext.getCmp('bp3d-pallet-copy-radio-tab');
		try{var copy_type = radio.getGroupValue();}catch(e){copy_type='tab';}
		var copy_type_obj;
//_dump("makeCopyListText():copy_type=["+copy_type+"]");
		if(copy_type=='csv'){
			copy_type_obj = CSVData;
		}else{
			copy_type_obj = TabData;
		}

		var copyText = "";
		var column = [];

		if(grid instanceof Ext.grid.GridPanel){
			var dataIndex;
			var data;
			var columnModel = grid.getColumnModel();
			var columnCount = columnModel.getColumnCount(false);
			for(var colIndex=0;colIndex<columnCount;colIndex++){
				if(columnModel.isHidden(colIndex)) continue;
				dataIndex = columnModel.getDataIndex(colIndex);
				if(dataIndex=='partslist'||dataIndex=='icon') continue;
				column.push(copy_type_obj.escape(columnModel.getColumnHeader(colIndex)));
			}
			copyText = column.join(copy_type_obj.colDelimiter)+"\\n";

			for(var i=0;i<records.length;i++){
				column = [];
				for(var colIndex=0;colIndex<columnCount;colIndex++){
					if(columnModel.isHidden(colIndex)) continue;
					dataIndex = columnModel.getDataIndex(colIndex);
					if(dataIndex=='partslist'||dataIndex=='icon') continue;
					if(records[i].data){
						data = records[i].data[dataIndex];
					}else{
						data = records[i][dataIndex];
					}
					if(dataIndex=='tg_id') data = gID2TreeGroup[data];
					column.push(copy_type_obj.escape(data));
				}
				copyText += column.join(copy_type_obj.colDelimiter)+"\\n";
			}
		}else if(grid instanceof Ext.DataView && records.length>0){
			var columnModel = Ext.getCmp('navigate-grid-panel').getColumnModel();
			var columnCount = columnModel.getColumnCount(false);
			for(var colIndex=0;colIndex<columnCount;colIndex++){
				dataIndex = columnModel.getDataIndex(colIndex);
				if(dataIndex=='partslist'||dataIndex=='icon') continue;
				column.push(copy_type_obj.escape(columnModel.getColumnHeader(colIndex)));
			}
			copyText = column.join(copy_type_obj.colDelimiter)+"\\n";

			for(var i=0;i<records.length;i++){
				column = [];
				for(var colIndex=0;colIndex<columnCount;colIndex++){
					dataIndex = columnModel.getDataIndex(colIndex);
					if(dataIndex=='partslist'||dataIndex=='icon') continue;
					if(records[i].data){
						data = records[i].data[dataIndex];
					}else{
						data = records[i][dataIndex];
					}
					if(dataIndex=='tg_id') data = gID2TreeGroup[data];
					column.push(copy_type_obj.escape(data));
				}
				copyText += column.join(copy_type_obj.colDelimiter)+"\\n";
			}
		}
		var textarea = Ext.getCmp('bp3d-pallet-copy-textarea');
		textarea.setValue(copyText);
		textarea.enable();
	}catch(e){
		_dump("makeCopyListText():"+e);
	}
};

copyListCB = function(grid,records,title){

	var bp3d_pallet_copy_window = new Ext.Window({
		id          : 'bp3d-pallet-copy-window',
		title       : title,
		width       : 600,
		height      : 300,
		layout      : 'form',
		plain       : true,
		bodyStyle   : 'padding:5px;text-align:right;',
		buttonAlign : 'center',
		modal       : true,
		resizable   : true,
		labelWidth  : 68,
		items       : [
		{
			xtype      : 'radiogroup',
			id         : 'bp3d-pallet-copy-radiogroup',
			fieldLabel : 'Copy Type',
//			columns    : [144,184],
			columns    : 2,
			height     : 22,
//			width      : 328,
			width      : 450,
			items      : [
				{boxLabel:'Tab-Separated Values',   id:'bp3d-pallet-copy-radio-tab', name:'copy-list-type', hideLabel:true, inputValue:'tab', checked: true},
				{boxLabel:'Comma-Separated Values', id:'bp3d-pallet-copy-radio-csv', name:'copy-list-type', hideLabel:true, inputValue:'csv', listeners:{'check':function(radio,checked){makeCopyListText(grid,records);},scope : this}}
			]
		},
		{
			xtype         : 'textarea',
			id            : 'bp3d-pallet-copy-textarea',
			hideLabel     : true,
			anchor        : '100% -30',
			selectOnFocus : true,
			disabled      : true,
			value         : "",
			listeners : {
				'render' : function(radiogroup){
					makeCopyListText(grid,records);
				}
			}
		}
		],
		buttons : [{
			text    : 'OK',
			handler : function(){
				bp3d_pallet_copy_window.close();
				bp3d_pallet_copy_window = undefined;
			}
		}]
	});
	bp3d_pallet_copy_window.show();
};

copyList = function(grid,store){
	if(store == undefined) store = grid.getStore();
//_dump("copyList():grid=["+(typeof grid)+"]["+((grid instanceof Ext.grid.GridPanel)?true:false)+"]");
	var window_title = get_ag_lang('COPY_TITLE');
	var records = [];
	if(grid instanceof Ext.grid.GridPanel){
		records = grid.getSelectionModel().getSelections();
	}else if(grid instanceof Ext.DataView){
		records = grid.getSelectedRecords();
		if(records.length==0) records = store.getRange();
	}
	if(records.length>0){
		copyListCB(grid,records,window_title);
	}else if(store.getCount() == store.getTotalCount()){
		copyListCB(grid,store.getRange(),window_title);
	}else{
		var baseParams = store.baseParams;
		var lastOptions = store.lastOptions;
		var params = {};
		for(var key in baseParams){
			params[key] = baseParams[key];
		}
		for(var key in lastOptions){
			params[key] = lastOptions[key];
		}
		delete params.start;
		delete params.limit;

		Ext.Ajax.request({
			url     : store.url,
			method  : 'POST',
			params  : params,
			success : function(conn,response,options){
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				if(!results || results.success == false){
					var msg = '';
					if(results && results.msg) msg += ' ['+results.msg+' ]';
					Ext.MessageBox.show({
						title   : window_title,
						msg     : msg,
						buttons : Ext.MessageBox.OK,
						icon    : Ext.MessageBox.ERROR
					});
					return;
				}
				try{
					if(results.records) copyListCB(grid,results.records,window_title);
				}catch(e){
					_dump("501:"+e);
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
					title   : window_title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
			}
		});
	}
};

TabData = {
	colDelimiter : '\\t',
	parse : function(data){
		data = data.trim();
		var rows = data.split("\\n");
		if(rows.length>=1) rows[0] = rows[0].replace(/^#+/g,"").split(TabData.colDelimiter);
		var i;
		for(i=1;i<rows.length;i++){
			rows[i] = rows[i].split("\\t");
			rows[i][rows[i].length-1] = rows[i][rows[i].length-1].replace(/\\s\$/g,"")
		}
		return rows;
	},
	escape : function(value){
		return value;
	}
};

CSVData = {
	colDelimiter : ',',
	parse : function(data){
		var rows = new Array();
		var cols = new Array();
		var quated = false;
		var colStartIndex = 0;
		var quateCount = 0;
		var i;
		for(i=0;i<data.length;i++){
			var c = data.charAt(i);
			if(c == '"'){
				quateCount++;
				if(!quated){
					quated = true;
				}else{
					if(quateCount % 2 == 0 ){
						if(i == data.length - 1 || data.charAt(i + 1) != '"'){
							quated = false;
						}
					}
				}
			}
			if(quated) continue;
			if(c == CSVData.colDelimiter){
				var value = data.substring(colStartIndex, i);
				value = CSVData.unescape(value);
				cols.push(value);
				colStartIndex = i + 1;
			}else if(c == "\\r"){
				var value = data.substring(colStartIndex, i);
				value = CSVData.unescape(value);
				cols.push(value);
				i += 1;
				colStartIndex = i + 1;
				rows.push(cols);
				cols = new Array();
			}else if(c == "\\n"){
				var value = data.substring(colStartIndex, i);
				value = CSVData.unescape(value);
				cols.push(value);
				colStartIndex = i + 1;
				rows.push(cols);
				cols = new Array();
			}
		}
		if(cols.length>0 && colStartIndex<i-1){
			var value = data.substring(colStartIndex).replace(/\\s+\$/g,"");
			value = CSVData.unescape(value);
			cols.push(value);
			rows.push(cols);
		}
		return rows;
	},
	escape : function(value){
		if(Ext.isEmpty(value)) return value;
		if(typeof value == "string"){
			value = value.replace(/"/g, '""');
			value = '"' + value + '"';
		}
		return value;
	},
	unescape : function(value){
		if(typeof value == "string"){
			if(value.charAt(0) == '"' && value.charAt(value.length-1) == '"') value = value.substring(1, value.length-1);
			value = value.replace(/""/g, '"');
		}
		return value;
	}
};

pasteTextareaSpecialkeyCB = function(textarea, e){
	if(e.getKey() == e.TAB){
		e.stopEvent();
		var elem = textarea.el.dom;
		var value = (new String(elem.value)).replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n");
		var selectionStart = -1;
		var selectionEnd = -1;
		if(elem.selectionStart != undefined && elem.selectionEnd != undefined){
			selectionStart = elem.selectionStart;
			selectionEnd = elem.selectionEnd;
		}else if(Ext.isIE){
			elem.focus();
			var r = document.selection.createRange();
			var len = r.text.replace(/\\r/g, "").length;
			var br = document.body.createTextRange();
			br.moveToElementText(elem);
			var all_len = br.text.replace(/\\r/g, "").length;
			br.setEndPoint("StartToStart",r);
			selectionStart = all_len - br.text.replace(/\\r/g, "").length;
			selectionEnd = selectionStart + len;
		}
		if(selectionStart<0 || selectionEnd<0) return;
		var l = value.substr(0,selectionStart)+"\\t";
		var c = value.substr(selectionStart,selectionEnd-selectionStart);
		var r = value.substr(selectionEnd);
		textarea.setRawValue(l+r);
		if(elem.selectionStart != undefined && elem.selectionEnd != undefined){
			elem.selectionStart = elem.selectionEnd = l.length;
		}else if(Ext.isIE){
			var range = elem.createTextRange();
			range.move("character",l.length);
			range.select();
		}
	}
};

pasteList = function(pasteText){
	if(pasteText==undefined || typeof pasteText != 'string') pasteText = '';
	var title = get_ag_lang('PASTE_TITLE');
	if(pasteText!='') title += ' <label style="color:red;">Error!!</label>';
	var bp3d_pallet_paste_window = new Ext.Window({
		id          : 'bp3d-pallet-paste-window',
		title       : title,
		width       : 600,
		height      : 450,
		layout      : 'form',
		plain       : true,
		bodyStyle   : 'padding:5px;text-align:right;',
		buttonAlign : 'center',
		modal       : true,
		resizable   : true,
		labelWidth  : 68,
		items       : [
		{
			xtype           : 'textarea',
			id              : 'bp3d-pallet-paste-textarea',
			hideLabel       : true,
			anchor          : '100% -185',
			selectOnFocus   : true,
			allowBlank      : false,
			value           : pasteText,
			enableKeyEvents : Ext.isChrome,
			listeners       : {
				'keydown' : pasteTextareaSpecialkeyCB,
				'specialkey' : pasteTextareaSpecialkeyCB,
				'valid' : function (textarea){
					var button = Ext.getCmp('bp3d-pallet-paste-ok-button');
					if(button && button.rendered) button.enable();
				},
				scope: this
			}
		}
		,
		{
			xtype      : 'radiogroup',
			id         : 'bp3d-pallet-paste-radiogroup',
			fieldLabel : 'Paste Type',
			columns    : 2,
			height     : 22,
			width      : 450,
			items      : [{
				boxLabel:'Tab-Separated Values',
				id:'bp3d-pallet-paste-radio-tab',
				name:'paste-list-type',
				hideLabel:true,
				inputValue:'tab',
				checked: true,
				handler:function(checkbox,checked){
					if(!checked) return;
					try{
						Ext.getCmp('bp3d-pallet-paste-description').layout.setActiveItem('bp3d-pallet-paste-description-'+checkbox.getGroupValue());
					}catch(e){
						_dump(e);
					}
				}
			},{
				boxLabel:'Comma-Separated Values',
				id:'bp3d-pallet-paste-radio-csv',
				name:'paste-list-type',
				hideLabel:true,
				inputValue:'csv',
				handler:function(checkbox,checked){
					if(!checked) return;
					try{
						Ext.getCmp('bp3d-pallet-paste-description').layout.setActiveItem('bp3d-pallet-paste-description-'+checkbox.getGroupValue());
					}catch(e){
						_dump(e);
					}
				}
			}]
		}
		,
		{
			id         : 'bp3d-pallet-paste-description',
			hideLabel  : true,
			layout     :'card',
			frame      : true,
			anchor     : '100%',
			height     : 155,
			activeItem : 0,
			bodyStyle  : 'padding:2px;text-align:left;',
			autoScroll : true,
			defaults: {
				border:false
			},
			items: [{
				id  : 'bp3d-pallet-paste-description-tab',
				html: '<div style="margin-bottom:4px;">'+get_ag_lang('PASTE_DESC_TAB')+'</div><label>Sample:</label><br/><textarea wrap=off readonly style="font-size:12px;width:90%;height:60px;margin-left:1em;">'+get_ag_lang('CDI_NAME')+'	Value\\nFMA7148	10000\\nFMA7198	42000\\nFMA7202	481\\nFMA7204	-1589\\nFMA7205	-20000</textarea>'
			},{
				id  : 'bp3d-pallet-paste-description-csv',
				html: '<div style="margin-bottom:4px;">'+get_ag_lang('PASTE_DESC_CSV')+'</div><label>Sample:</label><br/><textarea wrap=off readonly style="font-size:12px;width:90%;height:60px;margin-left:1em;">'+get_ag_lang('CDI_NAME')+',Value\\nFMA7148,10000\\nFMA7198,42000\\nFMA7202,481\\nFMA7204,-1589\\nFMA7205,-20000</textarea>'
			}]
		}

		],
		buttons : [{
			text     : 'OK',
			id       : 'bp3d-pallet-paste-ok-button',
			handler  : function(b,e){
				var textarea = Ext.getCmp('bp3d-pallet-paste-textarea');
				if(!textarea.validate()) return;

				bp3d_pallet_paste_window.loadMask.show();
				b.disable();
				Ext.getCmp('bp3d-pallet-paste-cancel-button').disable();
				var pasteText = textarea.getValue();
				textarea.disable();
				setTimeout(function(){
					try{
						if(pasteText){
							try{var paste_type = Ext.getCmp('bp3d-pallet-paste-radio-tab').getGroupValue();}catch(e){paste_type='tab';}

							var cvs_arr = CSVData.parse(pasteText);
							var cvs_title_arr = cvs_arr.shift();
							var tab_arr = TabData.parse(pasteText);
							var tab_title_arr = tab_arr.shift();
							if(paste_type=='csv' && cvs_title_arr.length<tab_title_arr.length){
								Ext.Msg.show({
									title:'Paste Type?',
									msg: 'Is this a Comma-Separated Values ?',
									buttons: Ext.Msg.YESNO,
									fn: function(buttonId){
										if(buttonId=='no'){
											pasteCancel();
										}else{
											pasteCB(pasteText);
										}
									},
									icon: Ext.MessageBox.QUESTION
								});
							}else if(paste_type=='tab' && cvs_title_arr.length>tab_title_arr.length){
								Ext.Msg.show({
									title:'Paste Type?',
									msg: 'Is this a Tab-Separated Values ?',
									buttons: Ext.Msg.YESNO,
									fn: function(buttonId){
										if(buttonId=='no'){
											pasteCancel();
										}else{
											pasteCB(pasteText);
										}
									},
									icon: Ext.MessageBox.QUESTION
								});
							}else{
								pasteCB(pasteText);
							}
						}else{
							pasteCancel();
						}
					}catch(e){
						_dump(e);
						pasteCancel();
					}
				},0);
			}
		},{
			text    : 'Cancel',
			id      : 'bp3d-pallet-paste-cancel-button',
			handler : function(){
				bp3d_pallet_paste_window.close();
				bp3d_pallet_paste_window = undefined;
			}
		}],
		listeners : {
			'render': function(comp){
				comp.loadMask = new Ext.LoadMask(comp.body,{msg:'Please wait...'});
			},
			'close': function(comp){
				//keymapの有効・無効
				if(window.agKeyMap) window.agKeyMap.enable();
			},
			'hide': function(comp){
				//keymapの有効・無効
				if(window.agKeyMap) window.agKeyMap.enable();
			},
			'show': function(comp){
				//keymapの有効・無効
				if(window.agKeyMap) window.agKeyMap.disable();
			},
			scope: this
		}
	});
	bp3d_pallet_paste_window.show();


	var pasteCancel = function(){
		try{
			bp3d_pallet_paste_window.loadMask.hide();
			Ext.getCmp('bp3d-pallet-paste-textarea').enable();
			Ext.getCmp('bp3d-pallet-paste-ok-button').enable();
			Ext.getCmp('bp3d-pallet-paste-cancel-button').enable();
		}catch(e){
			_dump(e);
		}
	};

	var pasteCB = function(pasteText){
		try{
			var arr = [];
			if(pasteText){
				try{var paste_type = Ext.getCmp('bp3d-pallet-paste-radio-tab').getGroupValue();}catch(e){paste_type='tab';}
				if(paste_type=='csv'){
					arr = CSVData.parse(pasteText);
				}else{
					arr = TabData.parse(pasteText);
				}
			}
			if(pasteText && arr.length>1){
				var tg_id = init_tree_group;
				var version = init_bp3d_version;
				var t_type;

				var tgi_id;
				var md_id;
				var mv_id;
				var mr_id;
				var bul_id;
				var cb_id;
				var ci_id;
				if(!Ext.isEmpty(init_bp3d_params.md_id)){
					tg_id = md_id = init_bp3d_params.md_id;
				}
				if(!Ext.isEmpty(init_bp3d_params.mv_id)){
					tgi_id = mv_id = init_bp3d_params.mv_id;
				}
				if(!Ext.isEmpty(init_bp3d_params.bul_id)){
					t_type = bul_id = init_bp3d_params.bul_id;
				}
				if(!Ext.isEmpty(init_bp3d_params.mr_id)){
					mr_id = init_bp3d_params.mr_id;
				}
				if(!Ext.isEmpty(init_bp3d_params.cb_id)){
					cb_id = init_bp3d_params.cb_id;
				}
				if(!Ext.isEmpty(init_bp3d_params.ci_id)){
					ci_id = init_bp3d_params.ci_id;
				}
				if(!Ext.isEmpty(init_bp3d_params.version)){
					version = init_bp3d_params.version;
				}

				var combo_group;
				var combo_version;
				var combo_t_type;
				var partslist = null;
				var contents_tabs = Ext.getCmp('contents-tab-panel');
				if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
					combo_group = Ext.getCmp('bp3d-tree-group-combo');
					combo_version = Ext.getCmp('bp3d-version-combo');
					combo_t_type = Ext.getCmp('bp3d-tree-type-combo');
					partslist = Ext.getCmp('control-tab-partslist-panel');
				}else if(contents_tabs.getActiveTab().id == 'contents-tab-anatomography-panel'){
					combo_group = Ext.getCmp('anatomo-tree-group-combo');
					combo_version = Ext.getCmp('anatomo-version-combo');
					combo_t_type = Ext.getCmp('bp3d-tree-type-combo-ag');
					partslist = Ext.getCmp('ag-parts-gridpanel');
				}
				if(!partslist) return;
//				if(combo_group) tg_id = combo_group.getValue();
//				if(combo_version) version = combo_version.getValue();
//				if(combo_t_type) t_type = combo_t_type.getValue();

				var title_arr = arr.shift();
				var columnTitle = [];

				var columnModel = partslist.getColumnModel();
				var columnCount = columnModel.getColumnCount(false);
				var columnTitleHash = [];
				for(var colIndex=0;colIndex<columnCount;colIndex++){
					dataIndex = columnModel.getDataIndex(colIndex);
					if(dataIndex=='partslist'||dataIndex=='icon') continue;
					columnTitleHash[columnModel.getColumnHeader(colIndex).trim().toLowerCase()] = dataIndex;
				}
				for(var i=0;i<title_arr.length;i++){
					var title = title_arr[i].trim().toLowerCase();
					title_arr[i] = columnTitleHash[title] ? columnTitleHash[title] : undefined;
				}

				var prm_record = ag_param_store.getAt(0);
				var store = partslist.getStore();
				var conv_flag = false;
				var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
				var addrecs = [];
				for(var i=0;i<arr.length;i++){
					var data_arr = arr[i];
					var addrec = new newRecord({
						'tg_id'         : tg_id,
						'version'       : version,
						'exclude'       : false,
						'color'         : '#'+prm_record.data.color_rgb,
						'value'         : '',
						'zoom'          : true,
						'opacity'       : '1.0',
						'representation': 'surface',
						'point'         : false
					});
					addrec.beginEdit();
					for(var j=0;j<data_arr.length;j++){
						if(!title_arr[j]) continue;
						var title = title_arr[j].trim();
						var value = data_arr[j].trim();
						if(title=='tg_id' && gTreeGroup2ID[value]){
							if(gTreeGroup2ID[value] != tg_id) conv_flag=true;
							addrec.set(title,gTreeGroup2ID[value]);
						}else if(title=='exclude'){
							addrec.set(title,value.toLowerCase()=='true'?true:false);
						}else if(value.length>0){
							addrec.set(title,value);
						}
					}
					addrec.commit(true);
					addrec.endEdit();
					addrecs.push(addrec);

				}
				store.suspendEvents();
				try{
					store.add(addrecs);
					clearConvertIdList(addrecs);

					if(conv_flag){
						var btn = Ext.getCmp('bp3d-home-group-btn');
						if(btn && btn.rendered){
							if(store.getCount()>0 && store.find('tg_id', new RegExp('^'+tg_id+'\$')) == -1){
								btn.enable();
								btn.el.dom.setAttribute('tg_id',addrecs[0].data.tg_id);
							}else{
								btn.disable();
							}
						}
					}

					var objs = [];
					for(var i=0;i<addrecs.length;i++){
						var obj = {
							id      : addrecs[i].id,
							version : addrecs[i].get('version')
						};
						if(!Ext.isEmpty(addrecs[i].get('f_id'))){
							obj.f_id = addrecs[i].get('f_id');
						}else{
							if(!Ext.isEmpty(addrecs[i].get('name_e'))) obj.name_e = addrecs[i].get('name_e');
							if(!Ext.isEmpty(addrecs[i].get('name_j'))) obj.name_j = addrecs[i].get('name_j');
							if(!Ext.isEmpty(addrecs[i].get('name_l'))) obj.name_l = addrecs[i].get('name_l');
							if(!Ext.isEmpty(addrecs[i].get('name_k'))) obj.name_k = addrecs[i].get('name_k');
						}
						if(obj.f_id || obj.name_e || obj.name_j || obj.name_l || obj.name_k) objs.push(obj);
					}
					if(objs.length>0){
						var params = {
							objs : Ext.util.JSON.encode(objs)
						};
						params.version = version;
						params.t_type = t_type;
						params.tgi_id = tgi_id;
						params.md_id = md_id;
						params.mv_id = mv_id;
						params.mr_id = mr_id;
						params.bul_id = bul_id;
						params.cb_id = cb_id;
						params.ci_id = ci_id;
						params.bul_all = true;
						bp3d_pallet_paste_store.load({
							params:params,
							callback:function(records,options,success){
								if(!success){
									store.resumeEvents();
									return;
								}

								var partslist = getActivePartsList();
								if(partslist) partslist.loadMask.show();
								getConvertIdList(records,store,function(){
									if(partslist) partslist.loadMask.hide();
								});
								store.resumeEvents();

							}
						});
					}else{
						setTimeout(function(){pasteList(pasteText);},0);
						for(var i=0;i<addrecs.length;i++){
							store.remove(addrecs[i]);
						}
						store.resumeEvents();
					}
				}catch(e){
					store.resumeEvents();
				}
			}else if(pasteText && arr.length==1){


			}
			bp3d_pallet_paste_window.close();
			bp3d_pallet_paste_window = undefined;
		}catch(e){
			_dump("802:"+e);
			pasteCancel();
		}
	};
};

var bp3d_pallet_paste_store_fields = [];
for(var i=0;i<bp3d_parts_store_fields.length;i++){
	var field = {};
	for(var key in bp3d_parts_store_fields[i]){
		field[key] = bp3d_parts_store_fields[i][key];
	}
	bp3d_pallet_paste_store_fields.push(field);
}
bp3d_pallet_paste_store_fields.push({name:'id'});
var bp3d_pallet_paste_store = new Ext.data.JsonStore({
	url: 'get-contents.cgi',
	pruneModifiedRecords : true,
	root: 'images',
	fields: bp3d_pallet_paste_store_fields,
	listeners: {
		'beforeload' : function(store,options){
			var partslist = getActivePartsList();
			if(!partslist) return;
			if(!partslist.loadMask) partslist.loadMask = new Ext.LoadMask(partslist.body,{msg:'Please wait...'});
			partslist.loadMask.show();
		},
		'load' : function(store,records,options){
			var partslist = getActivePartsList();
			if(!partslist) return;
			if(records.length==0){
				partslist.loadMask.hide();
				return;
			}
			try{
				var edit_store = partslist.getStore();
				var edit_records = [];
				var error_records = [];
				for(var i=0;i<records.length;i++){
					var id = records[i].get('id');
					var edit_record = edit_store.getById(id);
					if(Ext.isEmpty(edit_record)) continue;
					var b_id = records[i].get('b_id');
					if(!Ext.isEmpty(b_id)){
						edit_record = edit_record.copy();
						edit_record.beginEdit();
						for(var j=0;j<bp3d_parts_store_fields.length;j++){
							var name = bp3d_parts_store_fields[j].name;
							if(name == 'exclude' || name == 'color' || name == 'value' || name == 'zoom' || name == 'opacity' || name == 'representation' || name == 'point') continue;
							var value = records[i].get(name);
							if(!Ext.isEmpty(value)) edit_record.set(name,value);
						}
						edit_record.commit(true);
						edit_record.endEdit();
						edit_records.push(edit_record);
					}else{
						error_records.push(edit_record.copy());
					}
				}
				edit_store.removeAll();
				if(edit_records.length>0){
					edit_store.add(edit_records);
				}
				if(error_records.length>0){
					copyListCB(partslist,error_records,get_ag_lang('PASTE_TITLE')+' Error!!');
				}
			}catch(e){
				_dump("bp3d_pallet_paste_store.load:"+e);
			}
			partslist.loadMask.hide();
		},
		'loadexception' : function(){
			_dump("bp3d_pallet_paste_store.loadexception()");

			var partslist = getActivePartsList();
			if(partslist) partslist.loadMask.hide();

		},scope:this
	}
});

isEditablePartsList = function(tg_id){
	var editable = true;
	var group = Ext.getCmp('bp3d-tree-group-combo');
	if(group && group.rendered && group.getValue() != tg_id) editable = false; 
	return editable;
};

isAdditionPartsList = function(){
	var add = true;
HTML
if($additionalModelsImpossible eq 'true'){
	print <<HTML;
	var group = Ext.getCmp('bp3d-tree-group-combo');
	if(group && group.rendered){
		var tg_id = group.getValue();
		var records = bp3d_parts_store.getRange();
		for(var i=0;i<records.length;i++){
			if(records[i].data.tg_id == tg_id) continue;
			add = false;
			break;
		}
	}
HTML
}
print <<HTML;
	return add;
};

HTML
if($showGridColPartsExists eq 'true'){
	print <<HTML;
bp3s_parts_search_gridpanel_exists_parts_renderer = function(value,metadata,record,rowIndex,colIndex,store){
//	metadata.css += ' x-grid3-check-col-td'; 
////	return '<div class="x-grid3-cc-b_id"><img src="css/bullet_'+(Ext.isEmpty(value)? 'delete' : 'picture')+'.png" width="16" height="16"/></div>';
//	return '<div class="x-grid3-cc-b_id"><img src="css/bullet_'+(Ext.isEmpty(record.data.zmin)? 'delete' : 'picture')+'.png" width="16" height="16"/></div>';

		if(record.data.seg_color) metadata.attr = 'style="background:'+record.data.seg_color+';"'
		value = '<img src="css/bullet_'+(Ext.isEmpty(record.data.zmin)? 'delete' : 'picture')+'.png" width="16" height="16"/>';
		if(!Ext.isEmpty(record.data.icon)) value = '<img width=16 height=16 src='+record.data.icon+'>';
		return value;

};
HTML
}
print <<HTML;

bp3s_parts_gridpanel_group_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return gID2TreeGroup[value];
};
bp3s_parts_gridpanel_date_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return new Date(value).format("$DATE_FORMAT");
};
bp3s_parts_gridpanel_checkbox_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	var id = Ext.getCmp('ag-parts-gridpanel').getColumnModel().getColumnId(colIndex);
	metadata.css += ' x-grid3-check-col-td'; 
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
};
bp3s_parts_gridpanel_point_checkbox_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	var id = Ext.getCmp('ag-parts-gridpanel').getColumnModel().getColumnId(colIndex);
	metadata.css += ' x-grid3-check-col-td'; 
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
HTML
if($addPointElementHidden ne 'true'){
	print <<HTML;
	if(!isPointDataRecord(record)){
		return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
	}else{
		return '<div class="ag_grid_checkbox'+(value?'-on':'')+'-dis x-grid3-cc-'+id+'">&#160;</div>';
	}
HTML
}else{
	print <<HTML;
	return '<div class="x-grid3-check-col'+(value?'-on':'')+' x-grid3-cc-'+id+'">&#160;</div>';
HTML
}
print <<HTML;
};

bp3s_parts_gridpanel_color_renderer = function (value,metadata,record,rowIndex,colIndex,store) {
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return '<span style="background-color:' + value + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>';
};

bp3s_parts_gridpanel_combobox_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return value;
};


bp3s_parts_gridpanel_commonid_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	if(!isEditablePartsList(record.data.tg_id)){
		if(Ext.isEmpty(record.data.conv_id)){
			metadata.css += ' bp3d_parts_none_common_data';
		}else{
			metadata.css += ' bp3d_parts_none_data';
		}
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return value;
}

bp3s_parts_gridpanel_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}
	return value;
}

bp3s_parts_gridpanel_icon_renderer = function(value,metadata,record,rowIndex,colIndex,store){
	if(!isEditablePartsList(record.data.tg_id)){
		metadata.css += ' bp3d_parts_none_data';
	}else{
		if(Ext.isEmpty(record.data.conv_id)) metadata.css += ' bp3d_parts_none_version_data';
	}

	if(record.data.seg_color) metadata.attr = 'style="background:'+record.data.seg_color+';"'

	if(!Ext.isEmpty(value)) value = '<img width=16 height=16 src='+value+'>';
	return value;
}

hideConvIDColumn = function(){
	return;
	try{
		var bp3d_grid = Ext.getCmp('control-tab-partslist-panel');
		if(bp3d_grid){
			var cmodel = bp3d_grid.getColumnModel();
//			var index = cmodel.getIndexById('conv_id');
			var index = cmodel.getIndexById('common_id');
			if(index>=0 && !cmodel.isHidden(index)){
//				cmodel.setHidden(index,true);
				var size = bp3d_grid.getSize();
				if(size.width && size.height) resizeGridPanelColumns(bp3d_grid);
			}
		}else{
			bp3d_grid = undefined;
		}
	}catch(e){}

	try{
		var ag_grid = Ext.getCmp('ag-parts-gridpanel');
		if(ag_grid){
			var cmodel = ag_grid.getColumnModel();
//			var index = cmodel.getIndexById('conv_id');
			var index = cmodel.getIndexById('common_id');
			if(index>=0 && !cmodel.isHidden(index)){
//				cmodel.setHidden(index,true);
				var size = ag_grid.getSize();
				if(size.width && size.height) resizeGridPanelColumns(ag_grid);
			}
		}else{
			ag_grid = undefined;
		}
	}catch(e){}
};

showConvIDColumn = function(){
	return;
	try{
		var bp3d_grid = Ext.getCmp('control-tab-partslist-panel');
		if(bp3d_grid){
			var cmodel = bp3d_grid.getColumnModel();
//			var index = cmodel.getIndexById('conv_id');
			var index = cmodel.getIndexById('common_id');
			if(index>=0 && cmodel.isHidden(index)){
				cmodel.setHidden(index,false);
				var size = bp3d_grid.getSize();
				if(size.width && size.height) resizeGridPanelColumns(bp3d_grid);
			}
		}else{
			bp3d_grid = undefined;
		}
	}catch(e){}

	try{
		var ag_grid = Ext.getCmp('ag-parts-gridpanel');
		if(ag_grid){
			var cmodel = ag_grid.getColumnModel();
//			var index = cmodel.getIndexById('conv_id');
			var index = cmodel.getIndexById('common_id');
			if(index>=0 && cmodel.isHidden(index)){
				cmodel.setHidden(index,false);
				var size = ag_grid.getSize();
				if(size.width && size.height) resizeGridPanelColumns(ag_grid);
			}
		}else{
			ag_grid = undefined;
		}
	}catch(e){}
};

clearConvertIdList = function(records){
	for(var i=0;i<records.length;i++){
		records[i].beginEdit();
		records[i].set('conv_id',null);
//		records[i].set('common_id',null);
		records[i].commit(true);
		records[i].endEdit();
	}
	hideConvIDColumn();
};

tbarBodypartsLogout = function(b,e){};
chkOpenid = function(openid_url,aCB){};
tbarBodypartsLogin = function(b,e){};

function ag_ann_init(){
//try{
	var tree_expandnode = {};
	var thumbTemplate;
	var listTemplate;
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
	var contentsDetailsTemplate;
	var detailsTemplate;
	var detailsTemplate;
	var detailsConceptTemplate;
	var detailsTweetTemplate;
	var commentContentsDetailsTemplate;
	var commentDetailsTemplate;
	var commentContentsDetailsChildTemplate;
	var commentDetailsChildTemplate;
	var feedbackTemplate;
	var feedbackChildTemplate;
	var contents_tab_prev = null;
	var image_detailed_store_timer = null;

	var image_position = Cookies.get('ag_annotation.images.position');
	if(Ext.isEmpty(image_position)) image_position = 'front';
//	if(Ext.isEmpty(image_position)) image_position = 'rotate';
	var image_disptype = Cookies.get('ag_annotation.images.disptype');
HTML
if($useContentsTree eq 'true'){
}else{
	print <<HTML;
	if(Ext.isEmpty(image_disptype)) image_disptype = 'thump';
HTML
}
print <<HTML;

	getViewImages = function(){
		var cmp = Ext.getCmp('img-chooser-view');
		if(!cmp || !cmp.rendered || !cmp.layout || !cmp.layout.activeItem) return undefined;
//		return bp3d_contents_thumbnail_dataview;
		return cmp.layout.activeItem.items.first();
	};

	click_point_children = function(fmaid,label){
		var tabCmp = Ext.getCmp('navigate-tab-panel');
		var tabpanel = createSearchGridPanel(label,{
			title : 'Label['+label+']',
			baseParams : {
				query : label,
				node  : 'label',
				f_pid  : fmaid
			}
		});
		if(tabpanel) tabCmp.setActiveTab(tabCmp.add(tabpanel));
	};

	click_conventional = function(fmaid,path){
		var tabCmp = Ext.getCmp('navigate-tab-panel');
		if(tabCmp && tabCmp.getActiveTab().id != 'navigate-tree-panel') tabCmp.setActiveTab('navigate-tree-panel')
		var navigate_tree_combobox = Ext.getCmp('bp3d-tree-type-combo');
		var regexp = new RegExp("^$tree_class_conventional_id\$");
		var index = navigate_tree_combobox.store.find('t_type',regexp);
		if(index<0) return;
		tree_expandnode = {};
		Cookies.set('ag_annotation.images.fmaid',fmaid);
		Cookies.set('ag_annotation.images.path','/'+path);
		if(navigate_tree_combobox.getValue() != $tree_class_conventional_id){
			navigate_tree_combobox.setValue($tree_class_conventional_id);
			navigate_tree_combobox.fireEvent('select',navigate_tree_combobox,navigate_tree_combobox.store.getAt(index),index);
		}else{
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			treeCmp.selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
		}
	};


	var click_isa_partof_cb = function(fmaid,path,bul_id){
		_dump("click_isa_partof_cb():["+fmaid+"]["+path+"]["+bul_id+"]");
		var navigate_tree_combobox = Ext.getCmp('bp3d-tree-type-combo');
		var regexp = new RegExp("^"+bul_id+"\$");
		var index = navigate_tree_combobox.store.find('t_type',regexp);
		if(index<0) return;
		tree_expandnode = {};

		var path_arr = path.split("/");
		if(path_arr[path_arr.length-1]==fmaid) path_arr.pop();
		path = path_arr.join("/");

		var treeCmp = Ext.getCmp('navigate-tree-panel');
		var baseParams = treeCmp.getLoader().baseParams;

		Cookies.set('ag_annotation.images.fmaid',fmaid);
		Cookies.set('ag_annotation.images.path','/'+path);
		if(navigate_tree_combobox.getValue() != bul_id){
			navigate_tree_combobox.setValue(bul_id);
			navigate_tree_combobox.fireEvent('select',navigate_tree_combobox,navigate_tree_combobox.store.getAt(index),index);
		}else if(baseParams.t_type!=bul_id){
			treeCmp.getRootNode().reload(function(){
				treeCmp.selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
			});
		}
		treeCmp.selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
	};

	click_isa = function(fmaid,path){
//		clickDensityEnds(fmaid);
//		return;

		var bul_id = $tree_class_isa_id;
		var tabCmp = Ext.getCmp('navigate-tab-panel');
		if(tabCmp && tabCmp.getActiveTab().id == 'navigate-tree-panel'){
			click_isa_partof_cb.defer(0, this, [fmaid,path,bul_id]);
		}else{
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			treeCmp.on('show',function(){
				click_isa_partof_cb(fmaid,path,bul_id);
//				click_isa_partof_cb.defer(0, this, [fmaid,path,bul_id]);
			},this,{single:true,buffer:250});
			tabCmp.suspendEvents(false);
			tabCmp.setActiveTab('navigate-tree-panel');
			tabCmp.resumeEvents();
			bp3d_change_location(undefined,true);
			try{
				Ext.each(Ext.getCmp('bp3d-tree-type-combo').getStore().getRange(),function(r,i,a){
					\$('label#navigate-north-panel-content-label-'+r.data.t_type).text('');
				});
			}catch(e){}
/*
			if(fmaid){
				var load_params = {};
				for(var key in bp3d_contents_store.baseParams){
					load_params[key] = bp3d_contents_store.baseParams[key];
				}
				load_params.t_type = bul_id;
				load_params.bul_id = bul_id;
				delete load_params.node;
				load_params.f_ids = Ext.util.JSON.encode([fmaid]);
				bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(load_params)}));
			}
*/
		}
	};

	click_partof = function(fmaid,path){
//		clickDensityEnds(fmaid);
//		return;

		var bul_id = $tree_class_partof_id;
		var tabCmp = Ext.getCmp('navigate-tab-panel');
		if(tabCmp && tabCmp.getActiveTab().id == 'navigate-tree-panel'){
			click_isa_partof_cb.defer(0, this, [fmaid,path,bul_id]);
		}else{
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			treeCmp.on('show',function(){
				click_isa_partof_cb(fmaid,path,bul_id);
//				click_isa_partof_cb.defer(0, this, [fmaid,path,bul_id]);
			},this,{single:true,buffer:250});
			tabCmp.suspendEvents(false);
			tabCmp.setActiveTab('navigate-tree-panel');
			tabCmp.resumeEvents();
			bp3d_change_location(undefined,true);
			try{
				Ext.each(Ext.getCmp('bp3d-tree-type-combo').getStore().getRange(),function(r,i,a){
					\$('label#navigate-north-panel-content-label-'+r.data.t_type).text('');
				});
			}catch(e){}
/*
//			if(fmaid){
//				var load_params = {};
//				for(var key in bp3d_contents_store.baseParams){
//					load_params[key] = bp3d_contents_store.baseParams[key];
//				}
//				load_params.t_type = bul_id;
//				load_params.bul_id = bul_id;
//				delete load_params.node;
//				load_params.f_ids = Ext.util.JSON.encode([fmaid]);
//				bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(load_params)}));
//			}
*/
		}
	};

	click_used_parts_list_all = function(rep_id){
//		alert(bu_id);

		w = window.open(
//			"get-table.cgi?type=html&table=art_file&rep_id="+encodeURIComponent(rep_id),
//			"get-table.cgi?type=html&table=representation_art&rep_id="+encodeURIComponent(rep_id)+"&lng=$FORM{lng}",
			"download-art_file-list.cgi?type=html&rep_id="+encodeURIComponent(rep_id)+"&lng=$FORM{lng}",
			"_blank",
			"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600");

	};

	var prev_filter;
	filter_func = function(){
		var filterCmp = Ext.getCmp('filter');
		if(!filterCmp || filterCmp.disabled) return;
		var value = filterCmp.getValue();
		var store = getViewImages().store;
		if(prev_filter==value) return;
		store.clearFilter(false);
		store.filter('name', value,true);
		prev_filter=value;
	};
	bp3d_contents_store.on({
		beforeload: function(store){
//			_dump("bp3d_contents_store.beforeload(1)");
			prev_filter = undefined;
		}
	});

	var sortImages = function(){
		var v = Ext.getCmp('sortSelect').getValue();
		getViewImages().store.sort(v, v == 'name' ? 'asc' : 'desc');
		Cookies.set('ag_annotation.images.sort',v);
	};

	var getTreeFolderExpanded = function(node){
		var ids = [];
		if(!node) return ids;
		if(node.isExpanded()) ids.push(node.id);
		if(node.firstChild){
			node = node.firstChild;
			while(node){
				ids = ids.concat(getTreeFolderExpanded(node));
				node = node.nextSibling;
			}
		}
		return ids;
	};

	var selectPathCB = function(bSuccess, oSelNode){
_dump("selectPathCB()");
		var contentCmp = Ext.getCmp('content-card-panel');
		try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){}
		try{var sorttype = Ext.getCmp('sortSelect').getValue();}catch(e){}
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;

		//リストがアクティブの場合
		var tab_panel = navigate_tabs.getActiveTab();
		if(tab_panel.id == 'navigate-grid-panel'){
			var gridCmp = Ext.getCmp('navigate-grid-panel');
			var f_ids = [];
			var sels = gridCmp.getSelectionModel().getSelections();
			for(var i=0,len=sels.length;i<len;i++){
				f_ids.push(sels[i].data.b_id);
			}
			if(f_ids.length>0){
				var params = {
					f_ids : Ext.util.JSON.encode(f_ids)
				};
				if(!Ext.isEmpty(position)) params.position = position;
				var store = gridCmp.getStore();
				for(var key in store.lastOptions.params){
					params[key] = store.lastOptions.params[key];
				}
//				bp3d_contents_store.load({params:params});
//				_dump("CALL bp3d_change_location():1766");
				bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(params)}));
//_dump("selectPathCB(609):tab_panel.id=["+tab_panel.id+"]");
			}
			return;
		}
		if(tab_panel.id != 'navigate-tree-panel'){
			try{
				var f_ids = [];
				var sels = tab_panel.getSelectionModel().getSelections();
				if(sels.length == 0) sels = tab_panel.getStore().getRange();
				for(var i=0,len=sels.length;i<len;i++){
					f_ids.push(sels[i].data.f_id);
				}
				if(f_ids.length>0){
					var params = {
						fma_ids : Ext.util.JSON.encode(f_ids)
					};
					if(!Ext.isEmpty(position)) params.position = position;
					var store = tab_panel.getStore();
					for(var key in store.lastOptions.params){
						params[key] = store.lastOptions.params[key];
					}
//					bp3d_contents_store.load({params:params});
//					_dump("CALL bp3d_change_location():1790");
					bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(params)}));


//_dump("selectPathCB(630):tab_panel.id=["+tab_panel.id+"]");
				}
				return;
			}catch(e){
				_dump("selectPathCB():"+e);
			}
		}
//_dump("selectPathCB():gBP3D_TPAP=["+Ext.isEmpty(gBP3D_TPAP)+"]");

HTML
if($useContentsTree eq 'true'){
	print <<HTML;
HTML
}
print <<HTML;

		if(!Ext.isEmpty(gBP3D_TPAP)){
			gBP3D_TPAP = undefined;
			return;
		}

//_dump("selectPathCB():gParams.fmaid=["+(!Ext.isEmpty(gParams.fmaid))+"]["+gParams.fmaid+"]");
//_dump("selectPathCB():gParams.txpath=["+(!Ext.isEmpty(gParams.txpath))+"]["+gParams.txpath+"]");
//_dump("selectPathCB():gParams.t_type=["+(!Ext.isEmpty(gParams.t_type))+"]["+gParams.t_type+"]");
//_dump("selectPathCB():gParams.version=["+(!Ext.isEmpty(gParams.version))+"]");
//_dump("selectPathCB():gParams.query=["+(!Ext.isEmpty(gParams.query))+"]");

		if(!Ext.isEmpty(gParams.fmaid) && !Ext.isEmpty(gParams.txpath) && !Ext.isEmpty(gParams.t_type)){
			gParams.node = gParams.fmaid;
			Cookies.set('ag_annotation.images.node',gParams.fmaid);
			Cookies.set('ag_annotation.images.path',gParams.txpath);
			delete gParams.fmaid;
			if(!Ext.isEmpty(gParams.tp_ap)) delete gParams.tp_ap;
//			_location.location.href = "location.html?" + Ext.urlEncode(gParams);
//			_dump("CALL bp3d_change_location():1829");
			bp3d_change_location(Ext.urlEncode(gParams));
			return;
		}
		if(!Ext.isEmpty(gParams.fmaid) && !Ext.isEmpty(gParams.query) && !Ext.isEmpty(gParams.t_type)){
			gParams.node = 'search';
			Cookies.set('ag_annotation.images.node',gParams.fmaid);
			delete gParams.fmaid;
			if(!Ext.isEmpty(gParams.tp_ap)) delete gParams.tp_ap;
//			_location.location.href = "location.html?" + Ext.urlEncode(gParams);
//			_dump("CALL bp3d_change_location():1839");
			bp3d_change_location(Ext.urlEncode(gParams));
			return;
		}

//_dump("selectPathCB():bSuccess=["+bSuccess+"]");

		if(Ext.isEmpty(bSuccess)) bSuccess = false;

//_dump("selectPathCB():gSelNode=["+Ext.isEmpty(gSelNode)+"]");
//_dump("selectPathCB():oSelNode=["+Ext.isEmpty(oSelNode)+"]");

		if(!bSuccess && Ext.isEmpty(gSelNode) && Ext.isEmpty(oSelNode)){
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			if(treeCmp){
				oSelNode = treeCmp.getRootNode();
				if(oSelNode){
					treeCmp.getSelectionModel().select(oSelNode);
				}
			}
		}
		if(bSuccess){
			if(Ext.isEmpty(oSelNode)){
				try{
					var treeCmp = Ext.getCmp('navigate-tree-panel');
					if(treeCmp) oSelNode = treeCmp.getSelectionModel().getSelectedNode();
				}catch(e){
					_dump("selectPathCB():"+ e + "");
				}
			}
			gSelNode = oSelNode;
		}

//_dump("selectPathCB():gSelNode=["+(gSelNode?gSelNode.id:"")+"]");
//_dump("selectPathCB():oSelNode=["+(oSelNode?oSelNode.id:"")+"]");

//		if(gSelNode && gSelNode.id != "root"){
		if(gSelNode){
			var path;
			try{
				path = gSelNode.getPath('f_id');
			}catch(e){
				path = null;
			}
			if(path){
				_dump("selectPathCB():path=["+path+"]");
				path = path.replace(/^\\/root/,"");
				_dump("selectPathCB():path=["+path+"]");

				if(gSelNode.id != "trash"){
					Cookies.set('ag_annotation.images.node',gSelNode.id);
					Cookies.set('ag_annotation.images.path',path);
				}

				gParams.node = gSelNode.attributes.f_id;
				gParams.txpath = path;
				if(!Ext.isEmpty(position)) gParams.position = position;

				var cookies_sort = Cookies.get('ag_annotation.images.sort');
				if(Ext.isEmpty(cookies_sort)) cookies_sort = '';

				if(cookies_sort != sorttype){
					gParams.sorttype = sorttype;
					Cookies.set('ag_annotation.images.sort',sorttype);
				}else{
					delete gParams.sorttype;
				}

				if(!Ext.isEmpty(gParams.query)) delete gParams.query;
				if(!Ext.isEmpty(gParams.tp_ap)) delete gParams.tp_ap;

				if(gSelNode.id != 'search'){
					bp3d_change_location(Ext.urlEncode(gParams));
				}else{
					gParams.query = gSelNode.text.replace(/^search:\\[(.+)?\\]/i,"\$1");
					bp3d_change_location(Ext.urlEncode(gParams));
				}
			}
		}else if(oSelNode && oSelNode.id == "root"){
			gParams.node = oSelNode.id;
			gParams.txpath = '';
			if(!Ext.isEmpty(gParams.query)) delete gParams.query;
//			_location.location.href = "location.html?" + Ext.urlEncode(gParams);
//			_dump("CALL bp3d_change_location():1925");
			bp3d_change_location(Ext.urlEncode(gParams));


//			if(contentCmp) contentCmp.layout.setActiveItem(0);
//_dump("selectPathCB(3):Ext.urlEncode(gParams)=["+Ext.urlEncode(gParams)+"]");
		}
	};

	var WhatnewPanel = Ext.extend(Ext.DataView, {
		autoHeight   : true,
		frame        : true,
		cls          : 'demos',
		itemSelector : 'dd',
		overClass    : 'over',
		tpl : new Ext.XTemplate(
			'<div id="sample-ct">',
				'<tpl for=".">',
					'<div><h2><div>{title}</div></h2><dl>',
					'<tpl for="fma">',
						'<dd ext:txpath="/root/{txpath}" ext:id="{id}" ext:tg_id="{tg_id}" ext:version="{version}"><img style="width:90px;height:90px;margin:5px 0 0 5px;float:left;" src="{image}"/>',
							'<div><img style="width:16px;height:16px;margin:0 2px 0 0;float:left;" src="css/{icon}"/><h4>{name}</h4><p style="">{entry}<br/>{tg_name}<br/>{version}<br/>{detail}</p></div>',
						'</dd>',
					'</tpl>',
					'<div style="clear:left"></div></dl></div>',
				'</tpl>',
			'</div>'
		),
		onClick : function(e){
			var group = e.getTarget('h2', 3, true);
			if(group){
				group.up('div').toggleClass('collapsed');
			}else {
				var t = e.getTarget('dd', 5, true);
				if(t && !e.getTarget('a', 2)){
					var txpath = t.getAttributeNS('ext', 'txpath');
					var id = t.getAttributeNS('ext', 'id');
					var tg_id = t.getAttributeNS('ext', 'tg_id');
					var version = t.getAttributeNS('ext', 'version');

					var treeCmp = Ext.getCmp('navigate-tree-panel');
					var groupCmp = Ext.getCmp('bp3d-tree-group-combo');
					var versionCmp = Ext.getCmp('bp3d-version-combo');

					Cookies.set('ag_annotation.images.fmaid',id);

					if(treeCmp && groupCmp && versionCmp && groupCmp.getValue()==tg_id){
						if(txpath=='/root/') txpath += id;
						if(versionCmp.getValue()==version){
							treeCmp.selectPath(txpath,'f_id',selectPathCB);
						}else{
							txpath = txpath.replace(/^\\/root/g,"")
							Cookies.set('ag_annotation.images.path',txpath);
							var store = versionCmp.getStore();
							var index = store.find('tgi_version', new RegExp('^'+version+'\$'));
							versionCmp.setValue(version);
							versionCmp.fireEvent('select',versionCmp,store.getAt(index),index);
						}
					}else if(treeCmp && groupCmp && versionCmp && groupCmp.getValue()!=tg_id){
						var c_version_str = Cookies.get('ag_annotation.images.version');
						var c_version;
						if(c_version_str) c_version = Ext.util.JSON.decode(c_version_str);
						c_version = c_version || {};
						c_version[tg_id] = version;
						c_version_str = Ext.util.JSON.encode(c_version);
						Cookies.set('ag_annotation.images.version',c_version_str);

						var store = groupCmp.getStore();
						var index = store.find('tg_id', new RegExp('^'+tg_id+'\$'));
						groupCmp.setValue(tg_id);
						groupCmp.fireEvent('select',groupCmp,store.getAt(index),index);
					}
				}
			}
			return WhatnewPanel.superclass.onClick.apply(this, arguments);
		}
	});

	var whatnew_store = new Ext.data.JsonStore({
		url: 'get-whatnew.cgi',
		root: 'whatnew',
		fields: ['title', 'fma'],
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		}
	});

	var whatnew_panel = new Ext.Panel({
		title : get_ag_lang('TOP_WHATSNEW_TITLE'),
		hidden : $toppageHidden,
		id    : 'whatnew-panel',
		collapsible   : true,
		region: 'center',
		autoScroll : true,
		frame : true,
		items : new WhatnewPanel({ store : whatnew_store })
	});

	if(!$toppageHidden) whatnew_store.load();

	clickThumbTwisty = function(e,index,cPath){
		if(e.stopEvent) e.stopEvent();
		if(e.stopPropagation) e.stopPropagation();
		if(e.preventDefault) e.preventDefault();

		var dataview = getViewImages();
		if(!dataview) return;

HTML
if($useContentsTree eq 'true'){
}else{
	print <<HTML;
		var record = dataview.store.getAt(index);
HTML
}
print <<HTML;

//console.log(record);

//		if(!record || !record.data || !record.data.f_id || !(record.data.c_path || record.data.u_path || record.data.search_c_path)) return;
		if(!record || !record.data || !record.data.f_id) return;

		var activeTab = Ext.getCmp('navigate-tab-panel').getActiveTab();
		if(activeTab.id == 'navigate-tree-panel'){

			if(!(record.data.c_path || record.data.u_path || record.data.search_c_path)) return;

			var treeCmp = Ext.getCmp('navigate-tree-panel');
			if(!treeCmp || !treeCmp.root) return;
			var txpath = "/root";
			if(record.data.c_path){
HTML
if($useContentsTree eq 'true'){
}else{
	print <<HTML;
				txpath += Cookies.get('ag_annotation.images.path','') + '/' + record.data.f_id;
HTML
}
print <<HTML;
			}else if(record.data.u_path){
HTML
if($useContentsTree eq 'true'){
}else{
	print <<HTML;
				var arr = Cookies.get('ag_annotation.images.path','').split('/');
				arr.pop()
				txpath += arr.join('/');
HTML
}
print <<HTML;
			}else if(record.data.search_c_path){
				txpath += '/' + record.data.search_c_path;
			}
			treeCmp.selectPath(txpath,'f_id',selectPathCB);
		}else{
			var fma_id;
			if(record.data.c_path){
				fma_id = record.data.c_path.split("/").pop();
			}else if(record.data.u_path){
				fma_id = record.data.u_path.split("/").pop();
			}else if(record.data.but_cnum){
				fma_id = record.data.f_id;
			}
			if(fma_id){
				var load_params = {};
				for(var key in bp3d_contents_store.baseParams){
					load_params[key] = bp3d_contents_store.baseParams[key];
				}
				load_params.node = fma_id;
//				bp3d_contents_store.load({params:load_params});

//				if(!Ext.isEmpty(gBP3D_TPAP)){
//					gBP3D_TPAP = undefined;
//					return;
//				}
//				_location.location.href = "location.html?" + Ext.urlEncode({params:Ext.urlEncode(load_params)});
//				_dump("CALL bp3d_change_location():2124");
				bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(load_params)}));

			}
		}
	};

	clickDensityEnds = function(f_id){
		if(f_id){
			var load_params = {};
			for(var key in bp3d_contents_store.baseParams){
				load_params[key] = bp3d_contents_store.baseParams[key];
			}
//			load_params.node = f_id;
			delete load_params.node;
			load_params.f_ids = Ext.util.JSON.encode([f_id]);
//			bp3d_contents_store.load({params:load_params});
//			_dump("CALL bp3d_change_location():2141");
			bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(load_params)}));
		}
	};

	clickFeedbackThumb = function(e,c_id,xindex){
		if(e.stopEvent) e.stopEvent();
		if(e.stopPropagation) e.stopPropagation();
		if(e.preventDefault) e.preventDefault();
		try{
			var index = contents_tab_feedback_store.find('c_id',c_id);
			if(index<0) return;
			var record = contents_tab_feedback_store.getAt(index);
			if(!record || !record.data || !record.data.c_fmas  || !record.data.c_fmas[xindex].fma_path || !record.data.c_fmas[xindex].fma_tree) return;
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			if(!treeCmp || !treeCmp.root) return;

			var tree_combobox = Ext.getCmp('bp3d-tree-type-combo');
			try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}

			if(treeType != record.data.c_fmas[xindex].fma_tree[0].t_type){
				var index = tree_combobox.store.find('name',treeType);
				if(index<0) return;
				tree_combobox.setValue(record.data.c_fmas[xindex].fma_tree[0].t_type);
				Cookies.set('ag_annotation.images.path','/'+record.data.c_fmas[xindex].fma_path[0]);
				tree_combobox.fireEvent('select',tree_combobox,tree_combobox.store.getAt(index),index);
			}else{

				Cookies.set('ag_annotation.images.fmaid',record.data.c_fmas[xindex].fma_id);

				var txpath = "/root/";
				txpath += record.data.c_fmas[xindex].fma_path[0];
//_dump("624:CALL selectPathCB()");
				treeCmp.selectPath(txpath,'f_id',selectPathCB);
			}
			contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
		}catch(e){_dump("clickFeedbackThumb():"+e);}
	};

	openWiki = function(node){
		window.open(node.href, "$wiki_target", "$wiki_style");
		return false;
	};

	var getDetailsTemplateArray = function(aID){
		var id = aID;
		return [
			'<div class="details">',
				'<tpl for=".">',

					'<tpl if="this.isEmpty(b_id) == false">',
						'<table cellpadding="0" cellspacing="0" boder="0"><tbody>',
						'<tr><td align="right"><b style="">'+get_ag_lang('REP_ID')+':</b></td>',
						'<td><span style="margin-left:0.5em;">{b_id}</span></td></tr>',
						'</tbody></table>',
					'</tpl>',

					'<div class="details-info" style="text-align:center;vertical-align:bottom;">',
						'<img src="{src}" width="120" height="120">',
//						'<br>',
						'&nbsp;<label style="font-size:1.2em;">[<a id="bp3d-link-a-link" href="#" onclick="return bp3d_open_link_window(\\'{b_id}\\');">Icon URL</a>]</label>',
					'</div>',
					'<div class="details-info">',
						'<tpl if="this.isEmpty(f_id) == false">',
							'<b style="display:inline;white-space:nowrap;">'+get_ag_lang('CDI_NAME')+':</b>',
							'<span style="display:inline;">{f_id}</span><br/>',
						'</tpl>',

						'<tpl if="this.isEmpty(used_parts) == false">',
							'<b style="display:inline;white-space:nowrap;">'+get_ag_lang('ART_NAME')+':</b>',
							'<span style="display:inline;white-space:nowrap;">{used_parts:ellipsis(21,false)}</span><br/>',
//							'<span style="white-space:nowrap;text-align:right;font-size:1.5em;">[<a href="#" style="white-space:nowrap;" onclick="click_used_parts_list_all(',"'{b_id}'",');return false;" style="font-weight:bold;white-space:nowrap;">download obj files</a>]</span>',
							'<span style="white-space:nowrap;text-align:right;margin-top:5px;"><a href="#" style="white-space:nowrap;" onclick="click_used_parts_list_all(',"'{b_id}'",');return false;" style="font-weight:bold;white-space:nowrap;"><img src="css/btn_dlobjfiles02.png"></a></span>',
						'</tpl>',

						'<tpl if="this.isEmpty(density_ends) == false">',
							'<b style="display:inline;white-space:nowrap;">'+get_ag_lang('REP_PRIMITIVE')+':</b>',
							'<span style="display:inline;white-space:nowrap;">',
							'<tpl if="primitive == true">',
								'{[Ext.util.Format.ellipsis("'+get_ag_lang('ELEMENT_PRIMARY')+'",12)]}',
							'</tpl>',
							'<tpl if="primitive == false">',
								'{[Ext.util.Format.ellipsis("'+get_ag_lang('COMPOUND_SECONDARY')+'",10)]}',
							'</tpl>',
							'</span><br/>',
						'</tpl>',
					'</div>',

					'<tpl if="this.isEmpty(b_id) == false">',
						'<div class="details-info">',
							'<b style="display:inline;white-space:nowrap;">Share comments on {b_id}</b>',
							'<span style="display:inline;white-space:nowrap;">({tweet_num}) <a href="#" onclick="clickThumbTweet(event);return false;"><img src="css/twitter_16x14.png" ext:qtip="Error report"></a></span><br/>',
							'<tpl if="this.isArray(tweets) == true">',
								'<tpl for="tweets">',
									'<tpl if="xindex &lt; 6">',
										'<span style="border-top:1px solid #ddd;"></span>',
										'<table style="">',
										'<tr><td rowspan="2" valign="top"><img src={user_piuhs}></td><td>{user_name} \@{user_scname}</td>',
										'<td align="right" valign="top" nowrap>{[Ext.util.Format.date(this.toDate(values.created*1000),"d M")]}</td></tr>',
										'<tr><td colspan="2">{text}</td></tr>',
										'</table>',
									'</tpl>',
								'</tpl>',
								'<span style="border-top:1px solid #ddd;"><a href="#" onclick="showTweets(event);return false;">show all</a></span>',
							'</tpl>',
						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(density_ends) == false">',
						'<div class="details-info">',
							'<b style="display:inline;white-space:nowrap;">'+get_ag_lang('REP_DENSITY')+':</b>',
							'<span style="display:inline;white-space:nowrap;">{density}%</span><br/>',

							'<tpl if="this.isArray(density_ends) == true">',

								'<b style="">Represented / missing component</b>',
								'<div style="max-height:440px;overflow:auto;">',

								'<table><tbody>',
								'<tpl for="density_ends">',
									'<tr><td valign="top">',
									'<tpl if="this.isEmpty(b_id) == false">',
										'{b_id}',
									'</tpl>',
									'<tpl if="this.isEmpty(b_id) == true">',
										'NONE',
									'</tpl>',
									':</td><td valign="top">',
									'<tpl if="primitive == true">',
										'<a href="#" style="',
										'color:#006400;white-space:nowrap;',
										'" onclick="clickDensityEnds(',"'",'{f_id}',"'",');return false;">{f_id}</a>',
									'</tpl>',
									'<tpl if="primitive == false">',
										'<label style="',
										'color:#dc143c;',
										'">{f_id}</label>',
									'</tpl>',

									'</td><td valign="top">:</td><td valign="top"',

									'<tpl if="primitive == true &amp;&amp; this.isEmpty(path) == false">',
										'>{name}</td><td valign="top"><img src="{path}" width=40 height=40>',
									'</tpl>',
									'<tpl if="primitive != true || this.isEmpty(path) == true">',
										' colspan=2>{name}',
									'</tpl>',
									'</td></tr>',
								'</tpl>',
								'</tbody></table>',
								'</div>',
							'</tpl>',
							'<tpl if="this.isArray(density_ends) == false">',
								'<span>{density_ends}</span>',
							'</tpl>',


						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(f_id) == false">',
						'<div class="details-info">',
							'<b style="white-space: nowrap;">Concept labels for {f_id} (<label style="font-size:0.85em;">in {concept_info}{concept_build}</label>)</b>',
							'<tpl if="this.isEmpty(name_e) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_E')+':</b></td>',
								'<td><span>{name_e}</span></td></tr>',
								'</table>',
							'</tpl>',
HTML
if($FORM{lng} eq 'ja'){
	print <<HTML;
							'<tpl if="this.isEmpty(name_j) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_J')+':</b></td>',
								'<td><span>{name_j}</span></td></tr>',
								'</table>',
							'</tpl>',
							'<tpl if="this.isEmpty(name_k) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_K')+':</b></td>',
								'<td><span>{name_k}</span></td></tr>',
								'</table>',
							'</tpl>',
HTML
}
print <<HTML;
							'<tpl if="this.isEmpty(name_l) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_L')+':</b></td>',
								'<td><span>{name_l}</span></td></tr>',
								'</table>',
							'</tpl>',
							'<tpl if="this.isEmpty(syn_e) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_SYNONYM_E')+':</b></td>',
								'<td><span>{syn_e}</span></td></tr>',
								'</table>',
							'</tpl>',
HTML
if($FORM{lng} eq 'ja'){
	print <<HTML;
							'<tpl if="this.isEmpty(syn_j) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_SYNONYM_J')+':</b></td>',
								'<td><span>{syn_j}</span></td></tr>',
								'</table>',
							'</tpl>',
HTML
}
print <<HTML;
							'<tpl if="this.isEmpty(def_e) == false">',
								'<table cellpadding=0 cellspacing=0>',
								'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_DEFINITION_E')+':</b></td>',
								'<td><span>{def_e}</span></td></tr>',
								'</table>',
							'</tpl>',
						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(b_id) == false">',
						'<div class="bp3d-info">',
							'<b>Model cluster coordinates</b>',
							'<div style="padding-left:5px;">',
								'<table>',
									'<tpl if="this.isEmpty(phase) == false">',
										'<tr>',
											'<th><b>Phase&nbsp;:</b></th>',
											'<td><span>{phase}</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(xmin) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_XMIN')+'&nbsp;:</b></th>',
											'<td><span>{xmin} mm</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(xmax) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_XMAX')+'&nbsp;:</b></th>',
											'<td><span>{xmax} mm</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(ymin) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_YMIN')+'&nbsp;:</b></th>',
											'<td><span>{ymin} mm</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(ymax) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_YMAX')+'&nbsp;:</b></th>',
											'<td><span>{ymax} mm</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(zmin) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_ZMIN')+'&nbsp;:</b></th>',
											'<td><span>{zmin} mm</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(zmax) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_ZMAX')+'&nbsp;:</b></th>',
											'<td><span>{zmax} mm</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(volume) == false">',
										'<tr>',
											'<th><b>'+get_ag_lang('DETAIL_TITLE_VOLUME')+'&nbsp;:</b></th>',
											'<td><span>{volume} cm<sup>3</sup></span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(entryString) == false">',
										'<tr>',
											'<th><b>LastUpdate&nbsp;:</b></th>',
											'<td><span>{entryString}</span></td>',
										'</tr>',
									'</tpl>',
									'<tpl if="this.isEmpty(physical) == false">',
										'<tr>',
											'<th><b>Physical&nbsp;:</b></th>',
											'<td><span>{physical}</sup></span></td>',
										'</tr>',
									'</tpl>',
								'</table>',
							'</div>',
						'</div>',
					'</tpl>',

//					'<tpl if="this.isEmpty(srcstr) == false">',
//						'<div class="details-info">',
//							'<b>'+get_ag_lang('DETAIL_TITLE_ICON_URL')+':</b>',
//							'<span>Small&nbsp;:&nbsp;<a href="{srcstr}&amp;s=S" target="_blank">{srcstr}&amp;s=S</a></span>',
//							'<span>Large&nbsp;:&nbsp;<a href="{srcstr}&amp;s=L" target="_blank">{srcstr}&amp;s=L</a></span>',
//						'</div>',
//					'</tpl>',

//					'<div class="details-info">',
//						'<b>'+get_ag_lang('DETAIL_TITLE_LAST')+':</b>',
//						'<span>{dateString}</span>',
//					'</div>',
				'</tpl>',
			'</div>'
		];
	};

	var createDetailsTemplate = function(aID){
		var arr = getDetailsTemplateArray(aID);
		var template = new Ext.XTemplate(arr.join(''),{
			isEmpty:function(val){return Ext.isEmpty(val);},
			isArray:function(val){return Ext.isArray(val);},
			isNotEmptys:function(){for(var i=0;i<arguments.length;i++){if(!Ext.isEmpty(arguments[i])) return true;};return false;},
			isNotEmptyLSDBTermArray:function(lsdb_term_arr){
				for(var i=0;i<lsdb_term_arr.length;i++){
					if(!Ext.isEmpty(lsdb_term_arr[i].lsdb_term_e)) return true;
					if(!Ext.isEmpty(lsdb_term_arr[i].lsdb_term_l)) return true;
					if(!Ext.isEmpty(lsdb_term_arr[i].lsdb_term_j)) return true;
					if(!Ext.isEmpty(lsdb_term_arr[i].lsdb_term_k)) return true;
				};
				return false;
			},
			toDate:function(val){
				var dd = new Date();
				dd.setTime(val);
				return dd;
			}
		});
		template.compile();
		return template;
	};


	var createDetailsConceptTemplate = function(aID){
		var id = aID;
		var arr = [
			'<tpl if="this.isEmpty(f_id) == false">',
				get_ag_lang('FMA_DESCRIPTION_HTML'),
				'<div class="details-info" style="margin:0 5px;">',
					'<b style="white-space: nowrap;">Concept labels for <label>{f_id}</label> (<label style="font-size:0.85em;">in {concept_info}{concept_build}</label>)</b>',
					'<tpl if="this.isEmpty(name_e) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_E')+':</b></td>',
						'<td><span>{name_e}</span></td></tr>',
						'</table>',
					'</tpl>',
HTML
if($FORM{lng} eq 'ja'){
	print <<HTML;
					'<tpl if="this.isEmpty(name_j) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_J')+':</b></td>',
						'<td><span>{name_j}</span></td></tr>',
						'</table>',
					'</tpl>',
					'<tpl if="this.isEmpty(name_k) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_K')+':</b></td>',
						'<td><span>{name_k}</span></td></tr>',
						'</table>',
					'</tpl>',
HTML
}
print <<HTML;
					'<tpl if="this.isEmpty(name_l) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_NAME_L')+':</b></td>',
						'<td><span>{name_l}</span></td></tr>',
						'</table>',
					'</tpl>',
					'<tpl if="this.isEmpty(syn_e) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_SYNONYM_E')+':</b></td>',
						'<td><span>{syn_e}</span></td></tr>',
						'</table>',
					'</tpl>',
HTML
if($FORM{lng} eq 'ja'){
	print <<HTML;
					'<tpl if="this.isEmpty(syn_j) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_SYNONYM_J')+':</b></td>',
						'<td><span>{syn_j}</span></td></tr>',
						'</table>',
					'</tpl>',
HTML
}
print <<HTML;
					'<tpl if="this.isEmpty(def_e) == false">',
						'<table cellpadding=0 cellspacing=0>',
						'<tr><td valign="top" nowrap><b>'+get_ag_lang('DETAIL_TITLE_DEFINITION_E')+':</b></td>',
						'<td><span>{def_e}</span></td></tr>',
						'</table>',
					'</tpl>',
				'</div>',
				'<tpl if="this.isNotEmptys(is_a_path2root,is_a_brother,is_a_children,partof_path2root,partof_brother,partof_children)==false">',
					'<div class="details-info fmastratum-anchor">',
						'<div style="margin:0 5px;">',
							'<div id="',id,'"><span style="vertical-align:middle;"><img src="resources/images/default/tree/loading.gif"/>&nbsp;'+get_ag_lang('MSG_LOADING_DATA')+'</span><div>',
						'</div>',
					'</div>',
				'</tpl>',
			'</tpl>'
		];
		var template = new Ext.XTemplate(arr.join(''),{
			isEmpty:function(val){return Ext.isEmpty(val);},
			isArray:function(val){return Ext.isArray(val);},
			isNotEmptys:function(){for(var i=0;i<arguments.length;i++){if(!Ext.isEmpty(arguments[i])) return true;};return false;},
			toDate:function(val){
				var dd = new Date();
				dd.setTime(val);
				return dd;
			}
		});
		template.compile();
		return template;
	};

	var createDetailsTweetTemplate = function(aID){
		var id = aID;
		var arr = [
			'<tpl if="this.isEmpty(b_id) == false">',
				'<div class="details-info" style="border-width:0;margin:0 4px;">',
					'<b style="display:inline;white-space:nowrap;">Share comments on {b_id}</b>',
					'<span style="display:inline;white-space:nowrap;">({tweet_num}) <a href="#" onclick="clickThumbTweet(event);return false;"><img src="css/twitter_16x14.png" ext:qtip="Error report"></a></span><br/>',
					'<tpl if="this.isArray(tweets) == true && this.isEmpty(tweets) == false">',
						'<tpl for="tweets">',
							'<tpl if="xindex &lt; 6">',
								'<span style="border-top:1px solid #ddd;"></span>',
								'<table style="">',
								'<tr><td rowspan="2" valign="top"><img src={user_piuhs}></td><td>{user_name} \@{user_scname}</td>',
								'<td align="right">{[Ext.util.Format.date(this.toDate(values.created*1000),"d M")]}</td></tr>',
								'<tr><td colspan="2">{text}</td></tr>',
								'</table>',
							'</tpl>',
						'</tpl>',
					'</tpl>',
					'<tpl if="this.isEmpty(tweets) == true">',
						'<span style="border-top:1px solid #ddd;margin-top:4px;"></span>',
						'<span style="color:#666;font-family: arial,tahoma,helvetica,sans-serif;">Please Share the problems you find on this representation.</span>',
					'</tpl>',
				'</div>',
			'</tpl>'
		];
		var template = new Ext.XTemplate(arr.join(''),{
			isEmpty:function(val){return Ext.isEmpty(val);},
			isArray:function(val){return Ext.isArray(val);},
			isNotEmptys:function(){for(var i=0;i<arguments.length;i++){if(!Ext.isEmpty(arguments[i])) return true;};return false;},
			toDate:function(val){
				var dd = new Date();
				dd.setTime(val);
				return dd;
			}
		});
		template.compile();
		return template;
	};

	var getCommentDetailsTemplateArray = function(aID){
		var id = aID;
		return [
			'<div class="details">',
				'<tpl for=".">',
					'<div class="comment-details-info" style="padding-bottom:0px;">',
						'<div class="comment-details-info-title">',
							'<div style="margin:0px;margin-bottom:2px;padding-bottom:2px;0px;border-bottom:1px dotted #ccc;">',
								'<span style="display:inline;margin:0px;float:right;font-weight:bold;color:#333;">{tgi_version}</span>',
								'<span style="display:inline;margin:0px;font-weight:bold;color:#333;">{t_name}</span>',
							'</div>',
							'<span class="status">{cs_name}</span><br style="clear:both;"/>',

							'<span style="float:right;">',
							'[<a class="comment-details-info-comment-reply"        c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_REPLY')+'</a>]',
							'&nbsp;[<a class="comment-details-info-comment-edit"   c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_EDIT')+'</a>]',
							'&nbsp;[<a class="comment-details-info-comment-delete" c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_DELETE')+'</a>]',
							'</span>',
							'<tpl if="this.isEmpty(c_title) == false">',
								'<b>[{c_id}]:{c_title}</b>',
							'</tpl>',
						'</div>',
						'<tpl if="this.isEmpty(c_image) == false">',
							'<a class="comment-details-info-comment-thumb" href="{c_image}" target="_blank"><img src="{c_image_thumb}" align="right" border="0"></a>',
						'</tpl>',
						'<div class="comment-details-info-comment" c_id="{c_id}">{commentString}</div>',
						'<tpl if="this.isEmpty(nameString) == false">',
							'<div style="text-align:right;clear:both;"><b>Name:</b><span>{nameString}</span></div>',
						'</tpl>',
						'<div style="text-align:right;clear:both;"><span>{dateString}</span></div>',
						'<div class="comment-child" id="',id,'_comment_child_{c_id}"></div>',
					'</div>',
				'</tpl>',
			'</div>',
		];
	};
	var createCommentDetailsTemplate = function(aID){
		var arr = getCommentDetailsTemplateArray(aID);
		var template = new Ext.XTemplate(
			arr.join(''),
			{isEmpty:function(val){return Ext.isEmpty(val);}}
		);
		template.compile();
		return template;
	};

	var getCommentDetailsChildTemplateArray = function(aID){
		var id = aID;
		return [
			'<tpl for=".">',
				'<div class="comment-details-info-child">',
					'<div class="comment-details-info-title">',
						'<span style="float:right;">',
						'[<a class="comment-details-info-comment-reply"        c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_REPLY')+'</a>]',
						'&nbsp;[<a class="comment-details-info-comment-edit"   c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_EDIT')+'</a>]',
						'&nbsp;[<a class="comment-details-info-comment-delete" c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_DELETE')+'</a>]',
						'</span>',
						'<tpl if="this.isEmpty(c_title) == false">',
							'<b>[{c_id}]:{c_title}</b>',
						'</tpl>',
					'</div>',
					'<tpl if="this.isEmpty(c_image) == false">',
						'<a class="comment-details-info-comment-thumb" href="{c_image}" target="_blank"><img src="{c_image_thumb}" align="right" border="0"></a>',
					'</tpl>',
					'<div class="comment-details-info-comment" c_id="{c_id}">{commentString}</div>',
					'<tpl if="this.isEmpty(nameString) == false">',
						'<div style="text-align:right;clear:both;"><b>Name:</b><span>{nameString}</span></div>',
					'</tpl>',
					'<div style="text-align:right;clear:both;"><span>{dateString}</span></div>',
					'<div class="comment-child" id=""',id,'_comment_child_{c_id}"></div>',
				'</div>',
			'</tpl>',
		];
	};
	var createCommentDetailsChildTemplate = function(aID){
		var arr = getCommentDetailsChildTemplateArray(aID);
		var template = new Ext.XTemplate(
			arr.join(''),
			{isEmpty:function(val){return Ext.isEmpty(val);}}
		);
		template.compile();
		return template;
	};

	jumpFmastratum = function(node,selector){
		try{
			var body = Ext.get(node).findParentNode('div.x-panel-body',undefined,true);
			var child = body.child(selector);
			var scroll = body.getScroll();
			var offset = child.getOffsetsTo(body);
			body.scrollTo('top',offset[1]+scroll.top,true);
		}catch(e){
			_dump("jumpFmastratum():"+e);
		}
	};

	clickThumbTweet = function(){
		var selRec;
		var oSelNode = null;
		var dataview = getViewImages();
		if(!dataview) return;
		var selRecs = dataview.getSelectedRecords();
		if(selRecs && selRecs.length>0){
			selRec = selRecs[0].data;
		}else if(oSelNode){
			selRec = oSelNode.attributes.attr;
		}
		if(selRec){
			var b_id = selRec.mca_id ? selRec.mca_id : selRec.b_id;
			var url = '$urlTwitterTweetBP3D' + encodeURIComponent(b_id+' '+selRec.name);
			window.open(url,'_blank','dependent=yes,width=800,height=600');
		}else{
			Ext.Msg.show({
				title:'Tweet',
				buttons: Ext.Msg.OK,
				icon: Ext.Msg.ERROR,
				modal : true,
				msg : "パーツが選択されていません"
			});
		}
	};

	showTweets = function(){
		Ext.getCmp('bp3d-contents-detail-panel').activate(Ext.getCmp('bp3d-contents-detail-tweet-panel'));
	};

	var initTemplates = function(){
		thumbTemplate = new Ext.XTemplate(
			'<tpl for=".">',
				'<div class="thumb-wrap" style="{style}" ext:qtip="{name}">',
					'<div class="thumb" style="background:{bgColor};border-color:{borderColor};" ext:qtip="{name}">',
						(Ext.isIE ? '<img src="{src}" alt="{name}" width="120" height="120" ext:qtip="{name}">' : '<img src="resources/images/default/s.gif" lsrc="{src}" alt="{name}" width="120" height="120" ext:qtip="{name}">'),
						'<tpl if="this.isEmpty(c_path) == false">',
							'<a class="thumb-twisty" href="#" onclick="clickThumbTwisty(event,{[xindex-1]});this.blur();return false;"></a>',
						'</tpl>',
						'<tpl if="this.isEmpty(search_c_path) == false">',
							'<a class="thumb-twisty" href="#" onclick="clickThumbTwisty(event,{[xindex-1]});this.blur();return false;"></a>',
						'</tpl>',
						'<tpl if="this.isEmpty(u_path) == false">',
							'<tpl if="this.isUPPath(u_path) == true">',
								'<a class="thumb-up" href="#" onclick="clickThumbTwisty(event,{[xindex-1]});this.blur();return false;"></a>',
							'</tpl>',
							'<tpl if="this.isUPPath(u_path) == false">',
								'<span class="thumb-up-dis"></span>',
							'</tpl>',
						'</tpl>',
//						'<tpl if="this.isEmpty(common_id) == false">',
//							'<a class="thumb-link" href="#" f_id="{common_id}" onclick="this.blur();"></a>',
//						'</tpl>',
						'<tpl if="this.isEmpty(density_icon) == false">',
							'<div class="thumb-density thumb-density-{density_icon}" ext:qtip="{density}%"><img src="css/{density_icon}.png" ext:qtip="{density}%"></div>',
						'</tpl>',
						'<tpl if="tweet_num &gt; 0">',
							'<div class="thumb-tweet" ext:qtip="Tweet"><a href="#" onclick="showTweets(event);return false;"><img src="css/twitter_16x14.png" ext:qtip="Tweet"></a></div>',
						'</tpl>',
					'</div>',
					'<tpl if="this.isEmpty(state) == true">',
						'<div class="thumb-shortname" ext:qtip="{name}"><span ext:qtip="{name}"><label ext:qtip="{name}">{shortName}</label></span></div>',
					'</tpl>',
					'<tpl if="this.isEmpty(state) == false">',
						'<div class="thumb-shortname thumb-shortname-{state}" ext:qtip="{name}"><span ext:qtip="{name}"><label ext:qtip="{name}">{shortName}</label></span></div>',
					'</tpl>',
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
		thumbTemplate.compile();

		listTemplate = new Ext.XTemplate(
			'<tpl for=".">',
				'<div class="thumb-list-wrap" style="{style}">',
					'<table class="thumb-information"><tbody><tr>',
						'<td class="thumb-information-item">',
							'<div class="thumb" style="background:{bgColor};border-color:{borderColor};">',
								(Ext.isIE ? '<img src="{src}" alt="{name}" width="60" height="60">' : '<img src="resources/images/default/s.gif" lsrc="{src}" alt="{name}" width="60" height="60">'),
								'<tpl if="this.isEmpty(c_path) == false">',
									'<a class="thumb-twisty" href="#" onclick="clickThumbTwisty(event,{[xindex-1]});this.blur();return false;"></a>',
								'</tpl>',
								'<tpl if="this.isEmpty(search_c_path) == false">',
									'<a class="thumb-twisty" href="#" onclick="clickThumbTwisty(event,{[xindex-1]});this.blur();return false;"></a>',
								'</tpl>',
								'<tpl if="this.isEmpty(u_path) == false">',
									'<tpl if="this.isUPPath(u_path) == true">',
										'<a class="thumb-up" href="#" onclick="clickThumbTwisty(event,{[xindex-1]});this.blur();return false;"></a>',
									'</tpl>',
									'<tpl if="this.isUPPath(u_path) == false">',
										'<span class="thumb-up-dis"></span>',
									'</tpl>',
								'</tpl>',
								'<tpl if="this.isEmpty(density_icon) == false">',
									'<div class="thumb-density thumb-density-{density_icon}" ext:qtip="{density}%"><img src="css/{density_icon}.png" ext:qtip="{density}%"></div>',
								'</tpl>',

							'<tpl if="tweet_num &gt; 0">',
								'<div class="thumb-tweet" ext:qtip="Tweet"><a href="#" onclick="showTweets(event);return false;"><img src="css/twitter_16x14.png" ext:qtip="Tweet"></a></div>',
							'</tpl>',

							'</div>',
							'<tpl if="this.isEmpty(state) == false">',
								'<div class="thumb-shortname thumb-shortname-{state}"><span></span></div>',
							'</tpl>',
						'</td>',
						'<td class="thumb-information-item thumb-information-item-1">',
							'<table><tbody>',
							'<tpl if="this.isEmpty(b_id)==false">',
								'<tr><th>'+get_ag_lang('REP_ID')+':</th><td>{b_id}</td></tr>',
							'</tpl>',
							'<tr><th>'+get_ag_lang('CDI_NAME')+':</th><td>{f_id}</td></tr>',
							'<tr><th>TAID:</th><td><tpl if="this.isEmpty(taid) == false">{taid}</tpl></td></tr>',
							'</tbody></table>',
						'</td>',
						'<td class="thumb-information-item thumb-information-item-2">',
							'<table><tbody>',
							'<tr><th>'+get_ag_lang('DETAIL_TITLE_NAME_E')+':</th><td><tpl if="this.isEmpty(name_e) == false">{name_e}</tpl></td></tr>',
HTML
if($FORM{lng} eq 'ja'){
	print <<HTML;
							'<tr><th>'+get_ag_lang('DETAIL_TITLE_NAME_J')+':</th><td><tpl if="this.isEmpty(name_j) == false">{name_j}</tpl></td></tr>',
							'<tr><th>'+get_ag_lang('DETAIL_TITLE_NAME_K')+':</th><td><tpl if="this.isEmpty(name_k) == false">{name_k}</tpl></td></tr>',
HTML
}
print <<HTML;
							'<tr><th>'+get_ag_lang('DETAIL_TITLE_NAME_L')+':</th><td><tpl if="this.isEmpty(name_l) == false">{name_l}</tpl></td></tr>',
							'</tbody></table>',
						'</td>',
						'<td class="thumb-information-item thumb-information-item-3">',
							'<table><tbody>',
							'<tr><th>'+get_ag_lang('DETAIL_TITLE_SYNONYM_E')+':</th><td><tpl if="this.isEmpty(syn_e) == false">{syn_e}</tpl></td></tr>',
HTML
if($FORM{lng} eq 'ja'){
	print <<HTML;
							'<tr><th>'+get_ag_lang('DETAIL_TITLE_SYNONYM_J')+':</th><td><tpl if="this.isEmpty(syn_j) == false">{syn_j}</tpl></td></tr>',
HTML
}
print <<HTML;
							'</tbody></table>',
						'</td>',
					'</tr></tbody></table>',
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
		listTemplate.compile();

HTML
if($useContentsTree eq 'true'){
}
print <<HTML;

		fmastratumTemplate = new Ext.XTemplate(
			'<tpl for=".">',
				'<tpl if="this.isNotEmptys(partof_path2root,partof_brother,partof_children,is_a_path2root,is_a_brother,is_a_children)">',
					'<b style="padding-top:5px;">',
					'<tpl if="this.isNotEmptys(partof_path2root,partof_brother,partof_children)">',
						'<span style="white-space:nowrap;margin:0px 0.5em 0px 0px;float:left;">',
							'<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-partof'",');return false;">FMA part_of</a>',
							'<tpl if="this.isEmpty(partof_path2root) == false">',
								'(<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-partof-path2root'",');return false;">r</a>)',
							'</tpl>',
							'<tpl if="this.isEmpty(partof_brother) == false">',
								'(<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-partof-brother'",');return false;">b</a>)',
							'</tpl>',
							'<tpl if="this.isEmpty(partof_children) == false">',
								'(<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-partof-children'",');return false;">c</a>)',
							'</tpl>',
						'</span>',
					'</tpl>',
					'<tpl if="this.isNotEmptys(is_a_path2root,is_a_brother,is_a_children)">',
						'<span style="white-space:nowrap;margin:0px;float:left;">',
							'<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-is_a'",');return false;">FMA is_a</a>',
							'<tpl if="this.isEmpty(is_a_path2root) == false">',
								'(<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-is_a-path2root'",');return false;">r</a>)',
							'</tpl>',
							'<tpl if="this.isEmpty(is_a_brother) == false">',
								'(<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-is_a-brother'",');return false;">b</a>)',
							'</tpl>',
							'<tpl if="this.isEmpty(is_a_children) == false">',
								'(<a href="#" onclick="jumpFmastratum(this,',"'b.fmastratum-anchor-is_a-children'",');return false;">c</a>)',
							'</tpl>',
						'</span>',
					'</tpl>',

					'<br style="clear:left;"/>',
					'</b>',
				'</tpl>',


				'<tpl if="this.isNotEmptys(partof_path2root,partof_path2root_circular,partof_brother,partof_children)">',
					'<b style="padding-top:5px;" class="fmastratum-anchor-partof">FMA part_of</b>',
					'<tpl if="this.isEmpty(partof_path2root) == false">',
						'<div style="padding-left:5px;">',
							'<tpl for="partof_path2root">',
								'<tpl if="[xcount] == 1">',
									'<b style="padding-top:0px;text-decoration:underline;" class="fmastratum-anchor-partof-path2root">',
									'<a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Path to root</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',
											'<tpl for="fma">',
												'<tr><td valign="top">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td>',
												'<tpl if="this.isEmpty(potype) == false">',
													'<td valign="top">:</td><td valign="top">',
													'<tpl for="potype">',
														'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
													'</tpl>',
												'</tpl>',
												'<tpl if="this.isEmpty(potype) == true">',
													'<td valign="top"></td><td valign="top">',
												'</tpl>',
												'</td></tr>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
								'<tpl if="[xcount] &gt; 1">',
									'<tpl if="[xindex] &lt;= 10">',
										'<b style="padding-top:0px;text-decoration:underline;"',
										'<tpl if="[xindex] == 1">',
											' class="fmastratum-anchor-partof-path2root"',
										'</tpl>',
										'><a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
										'Path to root({[xindex]})</b>',
										'<div style="padding-left:5px;padding-bottom:5px;">',
											'<table style="margin:0px;padding:0px;">',
												'<tpl for="fma">',
													'<tr><td valign="top">',
													'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
														'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
													'</tpl>',
													'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
														'{f_id}',
													'</tpl>',
													'</td><td valign="top">:</td><td valign="top">{name}</td>',
													'<tpl if="this.isEmpty(potype) == false">',
														'<td valign="top">:</td><td valign="top">',
														'<tpl for="potype">',
															'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
														'</tpl>',
													'</tpl>',
													'<tpl if="this.isEmpty(potype) == true">',
														'<td valign="top"></td><td valign="top">',
													'</tpl>',
													'</td></tr>',
												'</tpl>',
											'</table>',
										'</div>',
									'</tpl>',
									'<tpl if="[xindex] &gt; 10">',
										'<b style="padding-top:0px;text-decoration:underline;">Path to root(...)</b>',
									'</tpl>',
								'</tpl>',
							'</tpl>',
						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(partof_path2root_circular) == false">',
						'<div style="padding-left:5px;">',
							'<tpl for="partof_path2root_circular">',
								'<tpl if="[xcount] == 1">',
									'<b style="padding-top:0px;text-decoration:underline;">Path to root [<font style="color:red;">Circular</font>]</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',
											'<tpl for="fma">',
												'<tr><td valign="top" class="{circular}">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top" class="{circular}">:</td><td valign="top" class="{circular}">{name}</td>',
												'<tpl if="this.isEmpty(potype) == false">',
													'<td valign="top" class="{circular}">:</td><td valign="top" class="{circular}">',
													'<tpl for="potype">',
														'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
													'</tpl>',
												'</tpl>',
												'<tpl if="this.isEmpty(potype) == true">',
													'<td valign="top" class="{circular}"></td><td valign="top" class="{circular}">',
												'</tpl>',
												'</td></tr>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
								'<tpl if="[xcount] &gt; 1">',
									'<tpl if="[xindex] &lt;= 10">',
										'<b style="padding-top:0px;text-decoration:underline;">Path to root [<font style="color:red;">Circular</font>] ({[xindex]})</b>',
										'<div style="padding-left:5px;padding-bottom:5px;">',
											'<table style="margin:0px;padding:0px;">',
												'<tpl for="fma">',
													'<tr><td valign="top" class="{circular}">',
													'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
														'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
													'</tpl>',
													'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
														'{f_id}',
													'</tpl>',
													'</td><td valign="top" class="{circular}">:</td><td valign="top" class="{circular}">{name}</td>',
													'<tpl if="this.isEmpty(potype) == false">',
														'<td valign="top" class="{circular}">:</td><td valign="top" class="{circular}">',
														'<tpl for="potype">',
															'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
														'</tpl>',
													'</tpl>',
													'<tpl if="this.isEmpty(potype) == true">',
														'<td valign="top" class="{circular}"></td><td valign="top" class="{circular}">',
													'</tpl>',
													'</td></tr>',
												'</tpl>',
											'</table>',
										'</div>',
									'</tpl>',
									'<tpl if="[xindex] &gt; 10">',
										'<b style="padding-top:0px;text-decoration:underline;">Path to root [<font style="color:red;">Circular</font>] (...)</b>',
									'</tpl>',
								'</tpl>',
							'</tpl>',
						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(partof_brother) == false">',
						'<div style="padding-left:5px;">',
							'<tpl for="partof_brother">',
								'<tpl if="[xcount] == 1">',
									'<b style="padding-top:0px;text-decoration:underline;" class="fmastratum-anchor-partof-brother">',
									'<a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Brother</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',

											'<tpl if="this.isEmpty(f_id) == false">',
												'<tr bgcolor="#dddddd"><td valign="top" style="font-weight:bold;">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td>',
												'<tpl if="this.isEmpty(potype) == false">',
													'<td valign="top">:</td><td valign="top">',
													'<tpl for="potype">',
														'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
													'</tpl>',
												'</tpl>',
												'<tpl if="this.isEmpty(potype) == true">',
													'<td valign="top"></td><td valign="top">',
												'</tpl>',
												'</td></tr>',
												'<tpl for="children">',
													'<tr><td valign="top" style="padding-left:5px;">',
													'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
														'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
													'</tpl>',
													'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
														'{f_id}',
													'</tpl>',
													'</td><td valign="top">:</td><td valign="top">{name}</td>',
													'<tpl if="this.isEmpty(potype) == false">',
														'<td valign="top">:</td><td valign="top">',
														'<tpl for="potype">',
															'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
														'</tpl>',
													'</tpl>',
													'<tpl if="this.isEmpty(potype) == true">',
														'<td valign="top"></td><td valign="top">',
													'</tpl>',
													'</td></tr>',
												'</tpl>',
											'</tpl>',

											'<tpl if="this.isEmpty(f_id) == true">',
												'<tpl for="children">',
													'<tr><td valign="top">',
													'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
														'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
													'</tpl>',
													'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
														'{f_id}',
													'</tpl>',
													'</td><td valign="top">:</td><td valign="top">{name}</td><td valign="top"></td><td valign="top"></td></tr>',
												'</tpl>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
								'<tpl if="[xcount] &gt; 1">',
									'<b style="padding-top:0px;text-decoration:underline;"',
									'<tpl if="[xindex] == 1">',
										' class="fmastratum-anchor-partof-brother"',
									'</tpl>',
									'><a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Brother({[xindex]})</b>',


									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',
											'<tr bgcolor="#dddddd"><td valign="top" style="font-weight:bold;">',
											'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
												'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
											'</tpl>',
											'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
												'{f_id}',
											'</tpl>',
											'</td><td valign="top">:</td><td valign="top" style="font-weight:bold;">{name}</td>',
											'<tpl if="this.isEmpty(potype) == false">',
												'<td valign="top">:</td><td valign="top">',
												'<tpl for="potype">',
													'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
												'</tpl>',
											'</tpl>',
											'<tpl if="this.isEmpty(potype) == true">',
												'<td valign="top"></td><td valign="top">',
											'</tpl>',
											'</td></tr>',
											'<tpl for="children">',
												'<tr><td valign="top" style="padding-left:5px;">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td>',
												'<tpl if="this.isEmpty(potype) == false">',
													'<td valign="top">:</td><td valign="top">',
													'<tpl for="potype">',
														'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
													'</tpl>',
												'</tpl>',
												'<tpl if="this.isEmpty(potype) == true">',
													'<td valign="top"></td><td valign="top">',
												'</tpl>',
												'</td></tr>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
							'</tpl>',
						'</div>',
					'</tpl>',
					'<tpl if="this.isEmpty(partof_children) == false">',
						'<div style="padding-left:5px;padding-bottom:5px;">',
							'<b style="padding-top:0px;text-decoration:underline;" class="fmastratum-anchor-partof-children">',
							'<a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
							'Children</b>',
							'<div style="padding-left:5px;">',
								'<table style="margin:0px;padding:0px;">',
									'<tpl for="partof_children">',
										'<tr><td valign="top">',
										'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
											'<a href="#" style="white-space:nowrap;" onclick="click_partof(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
										'</tpl>',
										'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
											'{f_id}',
										'</tpl>',
										'</td><td valign="top">:</td><td valign="top">{name}</td>',
										'<tpl if="this.isEmpty(potype) == false">',
											'<td valign="top">:</td><td valign="top">',
											'<tpl for="potype">',
												'<div class="potype {potabbr}" title="{potname}">{potabbr}</div>',
											'</tpl>',
										'</tpl>',
										'<tpl if="this.isEmpty(potype) == true">',
											'<td valign="top"></td><td valign="top">',
										'</tpl>',
										'</td></tr>',
									'</tpl>',
								'</table>',
							'</div>',
						'</div>',
					'</tpl>',
				'</tpl>',

				'<tpl if="this.isNotEmptys(is_a_path2root,is_a_brother,is_a_children)">',
					'<b style="padding-top:5px;" class="fmastratum-anchor-is_a">FMA is_a</b>',
					'<tpl if="this.isEmpty(is_a_path2root) == false">',
						'<div style="padding-left:5px;">',
							'<tpl for="is_a_path2root">',
								'<tpl if="[xcount] == 1">',
									'<b style="padding-top:0px;text-decoration:underline;" class="fmastratum-anchor-is_a-path2root">',
									'<a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Path to root</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',
											'<tpl for="fma">',
												'<tr><td valign="top">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td></tr>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
								'<tpl if="[xcount] &gt; 1">',
									'<b style="padding-top:0px;text-decoration:underline;"',
									'<tpl if="[xindex] == 1">',
										' class="fmastratum-anchor-is_a-path2root"',
									'</tpl>',
									'><a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Path to root({[xindex]})</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',
											'<tpl for="fma">',
												'<tr><td valign="top">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td></tr>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
							'</tpl>',
						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(is_a_brother) == false">',
						'<div style="padding-left:5px;">',
							'<tpl for="is_a_brother">',
								'<tpl if="[xcount] == 1">',
									'<b style="padding-top:0px;text-decoration:underline;" class="fmastratum-anchor-is_a-brother">',
									'<a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Brother</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',

											'<tpl if="this.isEmpty(f_id) == false">',
												'<tr bgcolor="#dddddd"><td valign="top" style="font-weight:bold;">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td></tr>',
												'<tpl for="children">',
													'<tr><td valign="top" style="padding-left:5px;">',
													'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
														'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
													'</tpl>',
													'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
														'{f_id}',
													'</tpl>',
													'</td><td valign="top">:</td><td valign="top">{name}</td></tr>',
												'</tpl>',
											'</tpl>',

											'<tpl if="this.isEmpty(f_id) == true">',
												'<tpl for="children">',
													'<tr><td valign="top">',
													'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
														'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
													'</tpl>',
													'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
														'{f_id}',
													'</tpl>',
													'</td><td valign="top">:</td><td valign="top">{name}</td><td valign="top"></td></tr>',
												'</tpl>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
								'<tpl if="[xcount] &gt; 1">',
									'<b style="padding-top:0px;text-decoration:underline;"',
									'<tpl if="[xindex] == 1">',
										' class="fmastratum-anchor-is_a-brother"',
									'</tpl>',
									'><a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
									'Brother({[xindex]})</b>',
									'<div style="padding-left:5px;padding-bottom:5px;">',
										'<table style="margin:0px;padding:0px;">',
											'<tr bgcolor="#dddddd"><td valign="top" style="font-weight:bold;">',
											'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
												'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
											'</tpl>',
											'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
												'{f_id}',
											'</tpl>',
											'</td><td valign="top">:</td><td valign="top" style="font-weight:bold;">{name}</td></tr>',
											'<tpl for="children">',
												'<tr><td valign="top" style="padding-left:5px;">',
												'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
													'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
												'</tpl>',
												'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
													'{f_id}',
												'</tpl>',
												'</td><td valign="top">:</td><td valign="top">{name}</td></tr>',
											'</tpl>',
										'</table>',
									'</div>',
								'</tpl>',
							'</tpl>',
						'</div>',
					'</tpl>',

					'<tpl if="this.isEmpty(is_a_children) == false">',
						'<div style="padding-left:5px;">',
							'<b style="padding-top:0px;text-decoration:underline;" class="fmastratum-anchor-is_a-children">',
							'<a href="#" onclick="jumpFmastratum(this,',"'div.fmastratum-anchor'",');return false;" style="float:right;">Top</a>',
							'Children</b>',
							'<div style="padding-left:5px;padding-bottom:5px;">',
								'<table style="margin:0px;padding:0px;">',
								'<tpl for="is_a_children">',
									'<tr><td valign="top">',
									'<tpl if="this.isEmpty(t_delcause) == true && this.isEmpty(c_path) == false">',
										'<a href="#" style="white-space:nowrap;" onclick="click_isa(', "'", '{f_id}', "'", ',', "'", '{c_path}', "'", ');return false;">{f_id}</a>',
									'</tpl>',
									'<tpl if="this.isEmpty(t_delcause) == false || this.isEmpty(c_path) == true">',
										'{f_id}',
									'</tpl>',
									'</td><td valign="top">:</td><td valign="top">{name}</td></tr>',
								'</tpl>',
								'</table>',
							'</div>',
						'</div>',
					'</tpl>',
				'</tpl>',
			'</tpl>',
			{
				isEmpty : function(val){
					return Ext.isEmpty(val);
				},
				isNotEmptys : function(){
					for(var i=0;i<arguments.length;i++){
						if(!Ext.isEmpty(arguments[i])) return true;
					}
					return false;
				}
			}
		);
		fmastratumTemplate.compile();
/*
		commentDetailsTemplate = new Ext.XTemplate(
			'<div class="details">',
				'<tpl for=".">',
					'<div class="comment-details-info" style="padding-bottom:0px;">',
						'<div class="comment-details-info-title">',
						'<span class="status">{cs_name}</span><br style="clear:both;"/>',
							'<span style="float:right;">',
							'[<a class="comment-details-info-comment-reply"        c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_REPLY')+'</a>]',
							'&nbsp;[<a class="comment-details-info-comment-edit"   c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_EDIT')+'</a>]',
							'&nbsp;[<a class="comment-details-info-comment-delete" c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_DELETE')+'</a>]',
							'</span>',
							'<tpl if="this.isEmpty(c_title) == false">',
								'<b>[{c_id}]:{c_title}</b>',
							'</tpl>',
						'</div>',
						'<tpl if="this.isEmpty(c_image) == false">',
							'<a class="comment-details-info-comment-thumb" href="{c_image}" target="_blank"><img src="{c_image_thumb}" align="right" border="0"></a>',
						'</tpl>',
						'<div class="comment-details-info-comment" c_id="{c_id}">{commentString}</div>',
						'<tpl if="this.isEmpty(nameString) == false">',
							'<div style="text-align:right;clear:both;"><b>Name:</b><span>{nameString}</span></div>',
						'</tpl>',
						'<div style="text-align:right;clear:both;"><span>{dateString}</span></div>',
						'<div class="comment-child" id="comment_child_{c_id}"></div>',
					'</div>',
				'</tpl>',
			'</div>',
			{
				isEmpty : function(val){
					return Ext.isEmpty(val);
				}
			}
		);
		commentDetailsTemplate.compile();

		commentDetailsChildTemplate = new Ext.XTemplate(
			'<tpl for=".">',
				'<div class="comment-details-info-child">',
					'<div class="comment-details-info-title">',
						'<span style="float:right;">',
						'[<a class="comment-details-info-comment-reply"        c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_REPLY')+'</a>]',
						'&nbsp;[<a class="comment-details-info-comment-edit"   c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_EDIT')+'</a>]',
						'&nbsp;[<a class="comment-details-info-comment-delete" c_id="{c_id}" href="#" style="text-decoration:none;" onclick="return false;">'+get_ag_lang('COMMENT_TITLE_DELETE')+'</a>]',
						'</span>',
						'<tpl if="this.isEmpty(c_title) == false">',
							'<b>[{c_id}]:{c_title}</b>',
						'</tpl>',
					'</div>',
					'<tpl if="this.isEmpty(c_image) == false">',
						'<a class="comment-details-info-comment-thumb" href="{c_image}" target="_blank"><img src="{c_image_thumb}" align="right" border="0"></a>',
					'</tpl>',
					'<div class="comment-details-info-comment" c_id="{c_id}">{commentString}</div>',
					'<tpl if="this.isEmpty(nameString) == false">',
						'<div style="text-align:right;clear:both;"><b>Name:</b><span>{nameString}</span></div>',
					'</tpl>',
					'<div style="text-align:right;clear:both;"><span>{dateString}</span></div>',
					'<div class="comment-child" id="comment_child_{c_id}"></div>',
				'</div>',
			'</tpl>',
			{
				isEmpty : function(val){
					return Ext.isEmpty(val);
				}
			}
		);
		commentDetailsChildTemplate.compile();
*/

		feedbackTemplate = new Ext.XTemplate(
			'<tpl for=".">',
				'<div id="feedback_{c_id}" class="feedback-head">',
					'<h2><div>',
						'<table style="margin:0px;padding:0px;border-spacing:0px;width:99%;" border="0"><tbody style="margin:0px;padding:0px;"><tr>',
							'<td style="margin:0px;padding:0px 4px;width:70px;vertical-align:top;">{ct_name}</td>',

//							'<td style="margin:0px;padding:0px 4px;width:70px;"><a href="#" border="0" onclick="clickFeedbackThumb(event,{c_id});this.blur();return false;">{f_id}</a></td>',
//							'<td style="margin:0px;padding:0px 4px;">{f_name}</td>',

							'<td style="margin:0px;padding:0px 4px;vertical-align:top;">',
							'<tpl for="c_fmas">',
								'<span style="float:left;white-space:pre;margin-left:1em;"><a href="#" border="0" onclick="clickFeedbackThumb(event,{parent.c_id},{[xindex-1]});this.blur();return false;">{fma_id}</a>&nbsp;{fma_name}</span>',
							'</tpl>',
							'<br style="clear: both;">',
							'</td>',


							'<td style="margin:0px;padding:0px 4px;width:18px;vertical-align:top;" align="right">{cs_name}</td>',
						'</tr></tbody></table>',
					'</div></h2>',
					'<dl>',
						'<dd>',
							'<table style="margin:0px;padding:0px;border-spacing:0px;width:99%;"><tbody style="margin:0px;padding:0px;"><tr>',
								'<td valign="top" style="margin:0px;padding:0px 4px;vertical-align:top;width:80px;">',
								'<tpl for="c_fmas">',
									'<tpl if="[xcount] == 1">',
										'<div class="thumbL">',
											'<a href="#" border="0" onclick="clickFeedbackThumb(event,{parent.c_id},{[xindex-1]});this.blur();return false;"><img src="{fma_image}"/></a>',
										'</div>',
									'</tpl>',
									'<tpl if="[xcount] &gt; 1 &amp;&amp; [xindex] &gt;= 1 &amp;&amp; [xindex] &lt;= 6">',
										'<div class="thumb">',
											'<a href="#" border="0" onclick="clickFeedbackThumb(event,{parent.c_id},{[xindex-1]});this.blur();return false;"><img src="{fma_image}"/></a>',
										'</div>',
									'</tpl>',
									'<tpl if="[xcount] &gt; 1 &amp;&amp; [xindex] &gt;= 7 &amp;&amp; [xindex] &lt;= 11">',
										'<div class="thumbS">',
											'<a href="#" border="0" onclick="clickFeedbackThumb(event,{parent.c_id},{[xindex-1]});this.blur();return false;"><img src="{fma_image}"/></a>',
										'</div>',
									'</tpl>',
									'<tpl if="[xcount] &gt; 1 &amp;&amp; [xindex] &gt; 11">',
										'<div class="thumbSS">',
											'<a href="#" border="0" onclick="clickFeedbackThumb(event,{parent.c_id},{[xindex-1]});this.blur();return false;"><img src="{fma_image}"/></a>',
										'</div>',
									'</tpl>',
								'</tpl>',
								'</td>',

								'<td valign="top" style="margin:0px;padding:0px 4px;">',
									'<div class="feedback-title">',
										'<table style="margin:0px;padding:0px;border-spacing:0px;width:99%;border:0px solid black;">',
											'<tbody style="margin:0px;padding:0px;"><tr>',
												'<td style="margin:0px;padding:0px 4px;width:50%;" align="left" nowrap>{c_title}</td>',
												'<td style="margin:0px;padding:0px 4px;width:50%;" align="right" nowrap>{nameString}&nbsp;&nbsp;{dateString}',
												'&nbsp;&nbsp;[<a href="#" style="text-decoration:none;" onclick="editFeedback({c_id});return false;">'+get_ag_lang('COMMENT_TITLE_EDIT')+'</a>]',
												'&nbsp;&nbsp;[<a href="#" style="text-decoration:none;" onclick="deleteFeedback({c_id});return false;">'+get_ag_lang('COMMENT_TITLE_DELETE')+'</a>]',
												'</td>',
											'</tr></tbody>',
										'</table>',
									'</div>',
									'<div class="feedback-comment" c_id="{c_id}">',
										'<tpl if="this.isEmpty(c_image) == false">',
											'<a href="{c_image}" target="_blank"><img align="right" border="0" src="{c_image_thumb}"/></a>',
										'</tpl>',
										'{commentString}',
									'</div>',
									'<div class="feedback-child" id="feedback_child_{c_id}"></div>',
								'</td>',
							'</tr></tbody></table>',
						'</dd>',
					'</dl>',
				'</div>',
			'</tpl>',
			{
				isEmpty : function(val){
					return Ext.isEmpty(val);
				}
HTML
if($lsdb_OpenID){
print <<HTML;
			},
			{
				isOpenID : function(val){
					return (val=='$lsdb_OpenID'?true:false);
				}
HTML
}
print <<HTML;
			}
		);
		feedbackTemplate.compile();


		feedbackChildTemplate = new Ext.XTemplate(
			'<dl class="feedback-child-dl">',
				'<tpl for=".">',
					'<dd id="feedback_{c_id}">',
						'<div class="feedback-child-head">',
							'<h2><div>',
								'<table style="margin:0px;padding:0px;border-spacing:0px;width:99%;border:0px solid black;">',
									'<tbody style="margin:0px;padding:0px;"><tr>',
										'<td style="margin:0px;padding:0px 4px;width:50%;" align="left" nowrap>{c_title}</td>',
										'<td style="margin:0px;padding:0px 4px;width:50%;" align="right" nowrap>{nameString}&nbsp;&nbsp;{dateString}',
										'&nbsp;&nbsp;[<a href="#" style="text-decoration:none;" onclick="editFeedback({c_id});return false;">'+get_ag_lang('COMMENT_TITLE_EDIT')+'</a>]',
										'&nbsp;&nbsp;[<a href="#" style="text-decoration:none;" onclick="deleteFeedback({c_id});return false;">'+get_ag_lang('COMMENT_TITLE_DELETE')+'</a>]',
										'</td>',
									'</tr></tbody>',
								'</table>',
							'</div></h2>',
							'<div class="feedback-comment" c_id="{c_id}">',
								'<tpl if="this.isEmpty(c_image) == false">',
									'<a href="{c_image}" target="_blank"><img align="right" border="0" src="{c_image_thumb}"/></a>',
								'</tpl>',
								'{commentString}',
							'</div>',
							'<div class="feedback-child" id="feedback_child_{c_id}"></div>',
						'</div>',
					'</dd>',
				'</tpl>',
			'</dl>',
			{
				isEmpty : function(val){
					return Ext.isEmpty(val);
				}
HTML
if($lsdb_OpenID){
print <<HTML;
			},
			{
				isOpenID : function(val){
					return (val=='$lsdb_OpenID'?true:false);
				}
HTML
}
print <<HTML;
			}
		);
		feedbackChildTemplate.compile();
	};

	replyComment=function(index){
		index = index-1;
		var records = bp3d_contents_detail_annotation_store.getRange(index,index);
		if(!records || records.length==0) return;
		openWindowComment(records[0].copy().data);
	};

HTML
if($lsdb_OpenID){
print <<HTML;
	deleteComment=function(index,c_pid){
		var data = null;
		index = index-1;
		if(c_pid){
			var p_index = bp3d_contents_detail_annotation_store.find('c_id',c_pid);
			var records = bp3d_contents_detail_annotation_store.getRange(p_index,p_index);
			if(!records || records.length==0) return;
			data = records[0].copy().data;
			data = data.c_reply[index];
		}else{
			var records = bp3d_contents_detail_annotation_store.getRange(index,index);
			if(!records || records.length==0) return;
			data = records[0].copy().data;
		}


		Ext.MessageBox.show({
			title   : get_ag_lang('COMMENT_TITLE_DELETE'),
			msg     : get_ag_lang('COMMENT_TITLE_DELETE_MSG'),
			buttons : Ext.MessageBox.YESNO,
			icon    : Ext.MessageBox.QUESTION,
			fn:function(btn){
				if(btn != 'yes') return;
				var delobjs = {
					f_id    : data.f_id,
					c_id    : data.c_id,
					c_image : data.c_image,
					parent  : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
					lng     : gParams.lng
				};
				Ext.Ajax.request({
					url     : 'del-comment.cgi',
					method  : 'POST',
					params  : Ext.urlEncode(delobjs),
					success : function(conn,response,options){
						try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
						if(!results || results.success == false){
							Ext.MessageBox.show({
								title   : get_ag_lang('COMMENT_TITLE_DELETE'),
								msg     : get_ag_lang('COMMENT_TITLE_DELETE_ERRMSG'),
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
						}
						bp3d_contents_detail_annotation_store.reload();
					},
					failure : function(conn,response,options){
						Ext.MessageBox.show({
							title   : get_ag_lang('COMMENT_TITLE_DELETE'),
							msg     : get_ag_lang('COMMENT_TITLE_DELETE_ERRMSG'),
							buttons : Ext.MessageBox.OK,
							icon    : Ext.MessageBox.ERROR
						});
						bp3d_contents_detail_annotation_store.reload();
					}
				});
			}
		});
	};
HTML
}
print <<HTML;

	authFeedback=function(config){
		if(Ext.isEmpty(config.store)) config.store = contents_tab_feedback_store;
		if(Ext.isEmpty(config.storeAll)) config.storeAll = contents_tab_feedback_all_store;
		var data = null;
		var index = config.store.find('c_id',config.c_id);
		var records = null;
		if(index>=0){
			records = config.store.getRange(index,index);
		}else{
			index = config.storeAll.find('c_id',config.c_id);
			if(index>=0) records = config.storeAll.getRange(index,index);
		}
		if(!records || records.length==0) return;
		data = records[0].copy().data;
		data.parent = (Ext.isEmpty(gParams.parent)?'':gParams.parent);
HTML
if($lsdb_OpenID){
	print <<HTML;
		Ext.Ajax.request({
			url     : 'auth-feedback.cgi',
			method  : 'POST',
			params  : Ext.urlEncode(data),
			success : function(conn,response,options){
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				if(!results || results.success == false){
					Ext.Msg.prompt('Name', 'Please enter your password:', function(btn, text){
						if (btn == 'ok'){
							data.c_passwd = text;
							Ext.Ajax.request({
								url     : 'auth-feedback.cgi',
								method  : 'POST',
								params  : Ext.urlEncode(data),
								success : function(conn,response,options){
									try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
									if(!results || results.success == false){
										if(config.failure) config.failure(results,data);
									}else{
										if(config.success) config.success(results,data);
									}
								},
								failure : function(conn,response,options){
									try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
									if(config.failure) config.failure(results,data);
								}
							});
						}
					});
				}else{
					if(config.success) config.success(results,data);
				}
			},
			failure : function(conn,response,options){
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				if(config.failure) config.failure(results,data);
			}
		});
HTML
}else{
	print <<HTML;
		Ext.Msg.prompt('Password', 'Please enter your password:', function(btn, text){
			if (btn == 'ok'){
				data.c_passwd = text;
				Ext.Ajax.request({
					url     : 'auth-feedback.cgi',
					method  : 'POST',
					params  : Ext.urlEncode(data),
					success : function(conn,response,options){
						try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
						if(!results || results.success == false){
							if(config.failure) config.failure(results,data);
						}else{
							if(config.success) config.success(results,data);
						}
					},
					failure : function(conn,response,options){
						try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
						if(config.failure) config.failure(results,data);
					}
				});
			}
		});
HTML
}
print <<HTML;
	};

	editFeedback=function(c_id,config){
		if(Ext.isEmpty(c_id)) return;
		config = config || {};
		config.c_id = c_id;
		config.success = function(results,data){openWindowComment(data,'edit');};
		config.failure = function(results,data){alert('failure');};
		authFeedback(config);
	};

	deleteFeedback=function(c_id,config){
		if(Ext.isEmpty(c_id)) return;
		config = config || {};
		config.c_id = c_id;
		config.success = function(results,data){
			var msg = get_ag_lang('COMMENT_TITLE_DELETE_MSG');
			if(data.c_title) msg = get_ag_lang('FEEDBACK_TITLE_DELETE_MSG').sprintf(data.c_title);

			Ext.MessageBox.show({
				title   : get_ag_lang('COMMENT_TITLE_DELETE'),
				msg     : msg,
				buttons : Ext.MessageBox.YESNO,
				icon    : Ext.MessageBox.QUESTION,
				fn:function(btn){
					if(btn != 'yes') return;
					Ext.Ajax.request({
						url     : 'del-comment.cgi',
						method  : 'POST',
						params  : Ext.urlEncode(data),
						success : function(conn,response,options){
							try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
							if(!results || results.success == false){
								Ext.MessageBox.show({
									title   : get_ag_lang('COMMENT_TITLE_DELETE'),
									msg     : get_ag_lang('COMMENT_TITLE_DELETE_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
							contents_tab_feedback_store.reload();
							bp3d_contents_detail_annotation_store.reload();
						},
						failure : function(conn,response,options){
							Ext.MessageBox.show({
								title   : get_ag_lang('COMMENT_TITLE_DELETE'),
								msg     : get_ag_lang('COMMENT_TITLE_DELETE_ERRMSG'),
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
							contents_tab_feedback_store.reload();
							bp3d_contents_detail_annotation_store.reload();
						}
					});
				}
			});
		};
		config.failure = function(results,data){alert('failure');};
		authFeedback(config);
	};


	var showDetails = function(dataview,selections){
//		_dump("showDetails()");

		try{var contentsDetailEl = Ext.getCmp('bp3d-contents-detail-information-panel').body;}catch(e){}
		try{var detailEl = Ext.getCmp('bp3d-detail-information-panel').body;}catch(e){}
		try{var commentDetailEl = Ext.getCmp('comment-detail-panel').body;}catch(e){}
		try{var conceptDetailEl = Ext.getCmp('bp3d-contents-detail-concept-panel').body;}catch(e){}
		try{var tweetDetailEl = Ext.getCmp('bp3d-contents-detail-tweet-panel').body;}catch(e){}

		if(Ext.isEmpty(contentsDetailEl) || Ext.isEmpty(detailEl)) return;
		var data = null;
		if(selections && selections.length > 0){
			data = dataview.getRecord(selections[0]).data;
		}else{
			var selNode = null;
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
			if(selNode){
				if(selNode.id != 'search'){
					var records = dataview.store.getRange();
					if(records.length>0){
						dataview.select(0);
					}else{
						data = selNode.attributes.attr;
					}
				}else{
					var records = dataview.store.getRange();
					if(records.length>0){
						dataview.select(0);
					}
				}
			}
		}
//		console.log(data);
		if(data){
			if(Ext.isEmpty(contentsDetailsTemplate)) contentsDetailsTemplate = createDetailsTemplate('bp3d-contents-detail-information-panel-fmastratum');
			if(Ext.isEmpty(detailsTemplate)) detailsTemplate = createDetailsTemplate('bp3d-detail-information-panel-fmastratum');
			if(Ext.isEmpty(detailsConceptTemplate)) detailsConceptTemplate = createDetailsConceptTemplate('bp3d-detail-information-panel-fmastratum');
			if(Ext.isEmpty(detailsTweetTemplate)) detailsTweetTemplate = createDetailsTweetTemplate('bp3d-detail-information-panel-fmastratum');

			try{
				contentsDetailEl.hide();
				contentsDetailsTemplate.overwrite(contentsDetailEl, data);
				contentsDetailEl.show();

				if(detailEl){
					detailEl.hide();
					detailsTemplate.overwrite(detailEl, data);
					detailEl.show();
				}

				if(conceptDetailEl){
					conceptDetailEl.hide();
					detailsConceptTemplate.overwrite(conceptDetailEl, data);
					conceptDetailEl.show();
				}

				if(tweetDetailEl){
					tweetDetailEl.hide();
					detailsTweetTemplate.overwrite(tweetDetailEl, data);
					tweetDetailEl.show();
				}

				if(bp3d_contents_detail_annotation_store){
					bp3d_contents_detail_annotation_store.load({
						params:{
							start : 0,
							limit : (bp3d_contents_detail_annotation_pagingBar?bp3d_contents_detail_annotation_pagingBar.initialConfig.pageSize:20)
						}
					});
					bp3d_contents_detail_annotation_panel.enable();
					bp3d_contents_detail_annotation_pagingBar.enable();
				}
				if(image_detailed_store_timer) clearTimeout(image_detailed_store_timer);
				image_detailed_store_timer = setTimeout(function(){
					image_detailed_store.load();
				},500);

				var fma_thumbnail = 'front';
				try{ fma_thumbnail = Ext.getCmp('positionSelect').getValue(); }catch(e){}

				var thumbnail_tree = 'conventional';
				try{
					thumbnail_tree = Ext.getCmp('bp3d-tree-type-combo').getValue();
					if(thumbnail_tree==1){
						thumbnail_tree = 'conventional';
					}else if(thumbnail_tree==3){
						thumbnail_tree = 'is_a';
					}else if(thumbnail_tree==4){
						thumbnail_tree = 'part_of';
					}
				}catch(e){}

				var thumbnail_version = '3.0';
				try{ thumbnail_version = Ext.getCmp('bp3d-version-combo').getValue(); }catch(e){}

HTML
if($wikiLinkHidden ne 'true'){
	print <<HTML;

				var iframe = document.getElementById('bp3d-contents-detail-wiki-panel-iframe');
//				console.log(iframe);
				if(iframe){
					Ext.get(iframe).setVisible(false);
					iframe.src = "about:blank";
					iframe.onload=function(){
						iframe.src = "$wiki_url/"+data.f_id+'#fma_thumbnail='+fma_thumbnail+'&thumbnail_tree='+thumbnail_tree+'&thumbnail_version='+thumbnail_version;
						iframe.onload=function(){ Ext.get(iframe).setVisible(true,true); }
					};
				}
HTML
}
print <<HTML;
			}catch(e){
				_dump("showDetails():"+e);
				_dump(e);
				contentsDetailEl.update('');
				if(commentDetailEl) commentDetailEl.update('');
				if(bp3d_contents_detail_annotation_panel) bp3d_contents_detail_annotation_panel.disable();
				if(bp3d_contents_detail_annotation_pagingBar) bp3d_contents_detail_annotation_pagingBar.disable();
			}
		}else{
			contentsDetailEl.update('');
			if(commentDetailEl) commentDetailEl.update('');
			if(bp3d_contents_detail_annotation_panel) bp3d_contents_detail_annotation_panel.disable();
			if(bp3d_contents_detail_annotation_pagingBar) bp3d_contents_detail_annotation_pagingBar.disable();
		}
	};

	var showCommentDetails = function(node){
	};

	reset_func = function(){
		if(viewport && viewport.rendered){
			var filter = Ext.getCmp('filter');
			if(filter) filter.reset();
			prev_filter = undefined;

			var element = bp3d_contents_thumbnail_dataview.getEl();
			if(element) element.dom.scrollTop = 0;
			var element = bp3d_contents_list_dataview.getEl();
			if(element) element.dom.scrollTop = 0;
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
		}
		bp3d_contents_thumbnail_dataview.store.clearFilter();
		bp3d_contents_list_dataview.store.clearFilter();
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
	};


	var onLoadException = function(v,o){
		var element = v.getEl();
		if(element) element.update('<div style="padding:10px;">Error loading images.</div>');
	};

	var formatData = function(data){
		if(data.is_a == undefined) data.is_a = null;
		if(data.search_c_path == undefined) data.search_c_path = null;
		if(data.c_path == undefined) data.c_path = null;
		if(data.u_path == undefined) data.u_path = null;
		data.shortName = null;
		if(data.name) data.shortName = data.name.ellipse(get_ag_lang('SORTNAME_LENGTH'));
		data.entryString = null;
		if(data.entry) data.entryString = formatDate(data.entry);
		data.dateString = formatTimestamp(data.lastmod);

//		data.bgColor = "#F0E5D2";
		data.bgColor = "#F0D2A0";
		data.borderColor = "#dddddd";
//		if(data.phy_id){
//			if(data.phy_id == 1){
//				data.bgColor = "#ffcccc";
//			}else if(data.phy_id == 2){
//				data.bgColor = "#ccffff";
//			}
//		}
		if(data.seg_thum_bgcolor){
			data.bgColor = data.seg_thum_bgcolor;
		}
		if(data.seg_thum_bocolor){
			data.borderColor = data.seg_thum_bocolor;
		}

		if(data.taid) data.taid = data.taid.replace(/\\|/g,"; ");

		if(data.name_j) data.name_j = data.name_j.replace(/；/g,"; ");
		if(data.name_k) data.name_k = data.name_k.replace(/；/g,"; ");
		if(data.syn_j) data.syn_j = data.syn_j.replace(/；/g,"; ");

		if(data.name_e) data.name_e = data.name_e.replace(/;(\\S)/g,"; \$1");
		if(data.name_l) data.name_l = data.name_l.replace(/;(\\S)/g,"; \$1");
		if(data.syn_e) data.syn_e = data.syn_e.replace(/;(\\S)/g,"; \$1");

		return data;
	};

	var formatTimestamp = function(val){
		return new Date(val).format("$TIME_FORMAT");
	}

	var formatDate = function(val){
		return new Date(val).format("$DATE_FORMAT");
	}

	initTemplates();

	var image_detailed_store = new Ext.data.JsonStore({
		url: 'get-fmastratum.cgi',
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},
		pruneModifiedRecords : true,
		root: 'images',
		fields: [
			'is_a_path2root',
			'is_a_brother',
			'is_a_children',
			'partof_path2root',
			'partof_path2root_circular',
			'partof_brother',
			'partof_children'
		],
		listeners: {
			'beforeload' : {
				fn:function(self,options){
					self.baseParams = self.baseParams || {};
					var dataview = getViewImages();
					if(!dataview) return;
					var records = dataview.getSelectedRecords();
					if(records.length == 0) return false;
					self.baseParams.f_id = records[0].data.f_id;
					try{var position = Ext.getCmp('positionSelect').getValue();}catch(e){position=undefined;}
					if(!Ext.isEmpty(position)) self.baseParams.position = position;
					try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
					self.baseParams.version = bp3d_version;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					try{var detailEl = Ext.get('bp3d-contents-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)) detailEl.update('');

					for(var key in init_bp3d_params){
						if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
					}

					try{
						var store = Ext.getCmp('bp3d-version-combo').getStore();
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

					try{var detailEl = Ext.get('bp3d-contents-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)){
						try{
							var data = records[0].data;
							detailEl.hide();
							fmastratumTemplate.overwrite(detailEl, data);
							detailEl.show();
						}catch(e){
							detailEl.update('');
						}
					}

					try{var detailEl = Ext.get('bp3d-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)){
						try{
							var data = records[0].data;
							detailEl.hide();
							fmastratumTemplate.overwrite(detailEl, data);
							detailEl.show();
						}catch(e){
							detailEl.update('');
						}
					}
				},
				scope:this,
				single:true
			},
			'datachanged':{
				fn:function(self){
					var records = self.getRange();

					try{var detailEl = Ext.get('bp3d-contents-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)){
						try{
							var data = records[0].data;
							detailEl.hide();
							fmastratumTemplate.overwrite(detailEl, data);
							detailEl.show();
						}catch(e){
							detailEl.update('');
						}
					}

					try{var detailEl = Ext.get('bp3d-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)){
						try{
							var data = records[0].data;
							detailEl.hide();
							fmastratumTemplate.overwrite(detailEl, data);
							detailEl.show();
						}catch(e){
							detailEl.update('');
						}
					}
				},scope:this},
			'loadexception': {
				fn:function(){
					try{var detailEl = Ext.get('bp3d-contents-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)) detailEl.update('<label style="color:red;font-weight:bolder;">Error!!</label>');

					try{var detailEl = Ext.get('bp3d-detail-information-panel-fmastratum');}catch(e){}
					if(!Ext.isEmpty(detailEl)) detailEl.update('<label style="color:red;font-weight:bolder;">Error!!</label>');

				},scope:this
			}
		}
	});

	var bp3d_contents_toolbar = new Ext.Toolbar([

		{
			id    : 'disptypeSelect_label',
			xtype : 'tbtext',
//			text  : get_ag_lang('DISPTYPE_TITLE')+':'
			text  : 'View:'
		},{
			id: 'disptypeSelect_old',
			xtype: 'combo',
			typeAhead: true,
			triggerAction: 'all',
			width: get_ag_lang('DISPTYPE_WIDTH'),
			listWidth: get_ag_lang('DISPTYPE_LIST_WIDTH'),
			editable: false,
			mode: 'local',
			displayField: 'label',
			valueField: 'value',
			lazyInit: false,
			disabled : true,
			store: new Ext.data.SimpleStore({
				fields : ['value', 'label'],
				data   : [
					['thump', get_ag_lang('DISPTYPE_THUMB')],
					['list',  get_ag_lang('DISPTYPE_LIST')]
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
				]
			}),
			listeners: {
				'select': {
					fn:function(combo,record,index){
						var value = record.get('value');
						Cookies.set('ag_annotation.images.disptype',value);
//						selectPathCB();
						var cmp = Ext.getCmp('img-chooser-view');
						if(cmp && cmp.rendered){
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
							setTimeout(function(){
								cmp.layout.setActiveItem(index);
							},250);
						}
					},scope:this
				}
			}
		},

/*
		'-',
		{
			id    : 'filter_label',
			xtype : 'tbtext',
			text: get_ag_lang('FILTER_TITLE')+':'
		},{
			xtype: 'textfield',
			id: 'filter',
			selectOnFocus: true,
			width: 100,
			disabled : true,
			listeners: {
				'render': {
						fn:function(){
							try{Ext.getCmp('filter').getEl().on('keyup', function(){ filter_func(); }, this, {buffer:500});}catch(e){}
						},
						scope:this
				}
			}
		},
*/
		' ',
		'-',
		{
			id    : 'sortSelect_label',
			xtype : 'tbtext',
			text  : get_ag_lang('SORT_TITLE')+':'
		},{
			id: 'sortSelect_old',
			xtype: 'combo',
			typeAhead: true,
			triggerAction: 'all',
			width: get_ag_lang('SORT_WIDTH'),
			listWidth: get_ag_lang('SORT_LIST_WIDTH'),
			editable: false,
			mode: 'local',
			displayField: 'desc',
			valueField: 'name',
			lazyInit: false,
			value: '',
			disabled : true,
			store: new Ext.data.SimpleStore({
				fields: ['name', 'desc'],
				data : [
					['',        get_ag_lang('SORT_TITLE_NONE')],
					['id',      get_ag_lang('CDI_NAME')],
//					['name_j',  get_ag_lang('SORT_TITLE_NAME_J')],
//					['name_k',  get_ag_lang('SORT_TITLE_NAME_K')],
					['name_e',  get_ag_lang('SORT_TITLE_NAME_E')],
//					['name_l',  get_ag_lang('SORT_TITLE_NAME_L')],
					['zmin',    'Zmin'],
					['zmax',    'Zmax'],
					['volume',  get_ag_lang('SORT_TITLE_VOLUME')],
					['lastmod', get_ag_lang('SORT_TITLE_LAST')],
					['tweet_num', 'Tweet']
				]
			}),
			listeners: {
				'select': {
					fn:function(combo,record,index){
//_dump("2109:CALL selectPathCB()");
//						selectPathCB();
						try{
							getViewImages().getStore().reload();
						}catch(e){
							_dump(e);
						}
					},scope:this}
			}
		},

		' ',
		'-',
		{
			id    : 'positionSelect_label',
			xtype : 'tbtext',
			text  : get_ag_lang('IMAGE_POSITION')+':'
		},{
			id: 'positionSelect_old',
			xtype: 'combo',
			typeAhead: true,
			triggerAction: 'all',
			width: get_ag_lang('IMAGE_POSITION_WIDTH'),
			listWidth: get_ag_lang('IMAGE_POSITION_LIST_WIDTH'),
			editable: false,
			mode: 'local',
			displayField: 'label',
			valueField: 'value',
			lazyInit: false,
			disabled : true,
			store: new Ext.data.SimpleStore({
				fields : ['value', 'label'],
				data   : [
					['rotate', get_ag_lang('IMAGE_POSITION_ROTATE')],
					['front',  get_ag_lang('IMAGE_POSITION_FRONT')],
					['back',   get_ag_lang('IMAGE_POSITION_BACK')],
					['left',   get_ag_lang('IMAGE_POSITION_LEFT')],
					['right',  get_ag_lang('IMAGE_POSITION_RIGHT')]
				]
			}),
			listeners: {
				'select': {
					fn:function(combo,record,index){
						Cookies.set('ag_annotation.images.position',record.get('value'));
//_dump("2140:CALL selectPathCB()");
//						selectPathCB();
						try{
							getViewImages().getStore().reload();
						}catch(e){
							_dump(e);
						}
					},scope:this
				}
			}
		}
HTML
if($useContentsTree eq 'true'){
}
if($lsdb_Auth && 0){
	print <<HTML;
		,
		'->',
		'-',
		{
			text: 'Delete Thumbnail',
			iconCls: 'thumbnail_delete',
			listeners: {
				'click': {
					fn : function(self,e){
					},scope : this
				}
			}
		}
HTML
}
if($copyThumbnailHidden ne 'true'){
	print <<HTML;
		,'->','-',{
			tooltip   : get_ag_lang('COPY_TITLE'),
			iconCls  : 'pallet_copy',
			handler : function(b,e){
				copyList(getViewImages());
			}
		}
HTML
}
print <<HTML;
	]);

	var bp3d_contents_thumbnail_dataview = new Ext.DataView({
		id           : 'bp3d-contents-dataview',
		tpl          : thumbTemplate,
		singleSelect : true,
		overClass    : 'x-view-over',
		autoShow     : false,
		itemSelector : 'div.thumb-wrap',
		style        : 'overflow:auto',
		multiSelect  : true,
		plugins      : new Ext.DataView.DragSelector({dragSafe:true}),
		loadingText  : '<div style="padding:10px;">'+get_ag_lang('MSG_LOADING_DATA')+'</div>',
		emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_ICON')+'</div>',
		store        : bp3d_contents_store,
		listeners: {
			'selectionchange': {fn:showDetails, scope:this, buffer:300},
			'loadexception'  : {fn:onLoadException, scope:this},
			'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}},
			'click'          : {fn:function(view,index,node,e){
				var record = view.getRecord(node);
				if(record) Cookies.set('ag_annotation.images.fmaid',record.data.f_id);
			},scope:this, buffer:0},

			'beforeclick'    : {fn:function(view,index,node,e){
				var target = e.getTarget('a',1,true);
				if(!target || !target.hasClass('thumb-link')) return;

				var href = "";
				if(target && target.dom && target.dom.href) href = target.dom.getAttribute("f_id");
				if(href) href = href.split("/").pop();
				if(href && href.match(/^(?:FMA|BP)/)){
					var form = Ext.getDom('ag-link-form');
					if(form){
						form.q.value = href;
						form.submit();
						form.q.value = "";
					}
					e.stopEvent();
					return false;
				}
			},scope:this, buffer:0},
			dblclick: {
				fn:function(view,index,node,e){clickThumbTwisty(e,index);},
				scope:this,
				buffer:0
			},
			render: function(comp){
				if(Ext.isIE) return;
				\$(comp.el.dom.parentElement).bind("scroll",function(e){
					var baseTop = \$(this).offset().top;
					var baseHeight = \$(this).height();
					var scrTop = this.scrollTop;
					var scrHeight = this.scrollHeight;
					\$(this).find("img[src='resources/images/default/s.gif']").each(function(){
						var top = \$(this).offset().top;
						var height = \$(this).height();
						if(((top-baseTop)>=0 && (top-baseTop)<=baseHeight) || ((top-baseTop+height)>=0 && (top-baseTop+height)<=baseHeight)){
							\$(this).one("load",function(e){
								\$(comp.el.dom.parentElement).trigger("scroll",[comp.el.dom.parentElement]);
							});
							\$(this).attr('src',\$(this).attr('lsrc'));
							return false;
						}
					});
				});
				bp3d_contents_store.on({
					load: {
						fn: function(store){
							\$(comp.el.dom.parentElement).trigger("scroll",[comp.el.dom.parentElement]);
						},
						buffer: 100
					}
				});
			}
		},
		prepareData: formatData.createDelegate(this)
	});

	var bp3d_contents_list_dataview = new Ext.DataView({
		id           : 'bp3d-contents-list-dataview',
		tpl          : listTemplate,
		singleSelect : true,
		overClass    : 'x-view-over',
		autoShow     : false,
		itemSelector : 'div.thumb-list-wrap',
		style        : 'overflow:auto',
		multiSelect  : true,
		plugins      : new Ext.DataView.DragSelector({dragSafe:true}),
		loadingText  : '<div style="padding:10px;">'+get_ag_lang('MSG_LOADING_DATA')+'</div>',
		emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_ICON')+'</div>',
		store        : bp3d_contents_store,
		listeners: {
			'selectionchange': {fn:showDetails, scope:this, buffer:300},
			'loadexception'  : {fn:onLoadException, scope:this},
			'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}},
			'click'          : {fn:function(view,index,node,e){
				var record = view.getRecord(node);
				if(record) Cookies.set('ag_annotation.images.fmaid',record.data.f_id);
			},scope:this, buffer:0},

			'beforeclick'    : {fn:function(view,index,node,e){
				var target = e.getTarget('a',1,true);
				if(!target || !target.hasClass('thumb-link')) return;

				var href = "";
				if(target && target.dom && target.dom.href) href = target.dom.getAttribute("f_id");
				if(href) href = href.split("/").pop();
				if(href && href.match(/^(?:FMA|BP)/)){
					var form = Ext.getDom('ag-link-form');
					if(form){
						form.q.value = href;
						form.submit();
						form.q.value = "";
					}
					e.stopEvent();
					return false;
				}
			},scope:this, buffer:0},
			'dblclick'       : {fn:function(view,index,node,e){clickThumbTwisty(e,index);},scope:this, buffer:0},
			'show'           : {fn:function(view){
				var nodes = Ext.query('div.thumb-list-wrap table.thumb-information td.thumb-information-item-2',view.body);
//				_dump("bp3d_contents_list_dataview.show():["+nodes.length+"]");
				var maxWidth = -1;
				Ext.each(nodes,function(node,i,a){
					var width = Ext.get(node).getWidth(false);
					if(maxWidth < width) maxWidth = width;
				});
				if(maxWidth >= 0){
					Ext.each(nodes,function(node,i,a){
						Ext.get(node).setWidth(maxWidth);
					});
				}
			},scope:this},
			render: function(comp){
				if(Ext.isIE) return;
				\$(comp.el.dom.parentElement).bind("scroll",function(e){
					var baseTop = \$(this).offset().top;
					var baseHeight = \$(this).height();
					var scrTop = this.scrollTop;
					var scrHeight = this.scrollHeight;
					\$(this).find("img[src='resources/images/default/s.gif']").each(function(){
						var top = \$(this).offset().top;
						var height = \$(this).height();
						if(((top-baseTop)>=0 && (top-baseTop)<=baseHeight) || ((top-baseTop+height)>=0 && (top-baseTop+height)<=baseHeight)){
							\$(this).one("load",function(e){
								\$(comp.el.dom.parentElement).trigger("scroll",[comp.el.dom.parentElement]);
							});
							\$(this).attr('src',\$(this).attr('lsrc'));
							return false;
						}
					});
				});
				bp3d_contents_store.on({
					load: function(store){
						\$(comp.el.dom.parentElement).trigger("scroll",[comp.el.dom.parentElement]);
					}
				});
			},
			resize: function(comp){
				if(Ext.isIE) return;
				\$(comp.el.dom.parentElement).trigger("scroll",[comp.el.dom.parentElement]);
			}
		},
		prepareData: formatData.createDelegate(this)
	});

HTML
if($useContentsTree eq 'true'){
}
print <<HTML;

	var bp3d_contents_thumbnail_panel = new Ext.Panel({
//		title      : get_ag_lang('CONTENT_TITLE'),
		id: 'bp3d-content-panel',
		region     : 'center',
		layout     : 'border',
		border     : false,
		monitorResize: true,
		items:[{
			border     : false,
			region     : 'center',
			id         : 'img-chooser-view',
			layout     : 'card',
	    activeItem : 0,
			autoScroll : false,
			bodyBorder : false,
			monitorResize: true,
			items      : [{
				border     : false,
				autoScroll : true,
				items      : bp3d_contents_thumbnail_dataview
			},{
				border     : false,
				autoScroll : true,
				items      : bp3d_contents_list_dataview
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
			}],
			listeners: {
				bodyresize: {
					fn: function(comp){
						if(Ext.isIE) return;
						Ext.each([bp3d_contents_thumbnail_dataview,bp3d_contents_list_dataview],function(dataview){
							try{\$(dataview.el.dom.parentElement).trigger("scroll",[dataview.el.dom.parentElement]);}catch(e){}
						});
					},
					buffer: 100
				}
			}
		},{
//			tbar       : bp3d_contents_toolbar,
			id: 'bp3d-content-panel-header',
			contentEl: 'bp3d-content-panel-header-contentEl',
			border: false,
			frame: false,
			bodyStyle:'border-bottom-width:1px;',
			region: 'north',
//			height: 57,
			height: 63,
			listeners: {
				render: {
					fn:function(comp){

						new Ext.Button({
							id: 'bp3d-content-panel-header-content-view-thump',
							renderTo      : 'bp3d-content-panel-header-content-view-thump-render',
							iconCls: 'view_tile',
							enableToggle: true,
							pressed: true,
							listeners: {
								toggle: function(button,pressed){
									_dump("toggle():["+button.id+"]["+pressed+"]");
									Ext.getCmp('bp3d-content-panel-header-content-view-list').toggle(!pressed,true);
									if(!pressed) return;
									var combobox = Ext.getCmp('disptypeSelect');
									var store = combobox.getStore();
									var idx = store.find('value','thump');
									var rec = store.getAt(idx);
									combobox.fireEvent('select',combobox,rec,idx);
								}
							}
						});
						new Ext.Button({
							id: 'bp3d-content-panel-header-content-view-list',
							renderTo      : 'bp3d-content-panel-header-content-view-list-render',
							iconCls: 'view_list',
							enableToggle: true,
							listeners: {
								toggle: function(button,pressed){
									_dump("toggle():["+button.id+"]["+pressed+"]");
									Ext.getCmp('bp3d-content-panel-header-content-view-thump').toggle(!pressed,true);
									var combobox = Ext.getCmp('disptypeSelect');
									var store = combobox.getStore();
									var idx = store.find('value','list');
									var rec = store.getAt(idx);
									combobox.fireEvent('select',combobox,rec,idx);
								}
							}
						});

						new Ext.form.ComboBox({
							id: 'disptypeSelect',
							renderTo      : 'bp3d-content-panel-header-content-view-combobox-render',
							typeAhead: true,
							triggerAction: 'all',
							width: get_ag_lang('DISPTYPE_WIDTH'),
							listWidth: get_ag_lang('DISPTYPE_LIST_WIDTH'),
							editable: false,
							mode: 'local',
							displayField: 'label',
							valueField: 'value',
							lazyInit: false,
							disabled : true,
							store: new Ext.data.SimpleStore({
								fields : ['value', 'label'],
								data   : [
									['thump', get_ag_lang('DISPTYPE_THUMB')],
									['list',  get_ag_lang('DISPTYPE_LIST')]
								]
							}),
							listeners: {
								'select': {
									fn:function(combo,record,index){
										var value = record.get('value');
										Cookies.set('ag_annotation.images.disptype',value);
										var cmp = Ext.getCmp('img-chooser-view');
										if(cmp && cmp.rendered){
											setTimeout(function(){
												cmp.layout.setActiveItem(index);
											},250);
										}
									},scope:this
								}
							}
						});

						new Ext.form.ComboBox({
							id: 'positionSelect',
							renderTo      : 'bp3d-content-panel-header-content-position-combobox-render',
							typeAhead: true,
							triggerAction: 'all',
							width: get_ag_lang('IMAGE_POSITION_WIDTH'),
							listWidth: get_ag_lang('IMAGE_POSITION_LIST_WIDTH'),
							editable: false,
							mode: 'local',
							displayField: 'label',
							valueField: 'value',
							lazyInit: false,
							disabled : true,
							store: new Ext.data.SimpleStore({
								fields : ['value', 'label'],
								data   : [
									['rotate', get_ag_lang('IMAGE_POSITION_ROTATE')],
									['front',  get_ag_lang('IMAGE_POSITION_FRONT')],
									['back',   get_ag_lang('IMAGE_POSITION_BACK')],
									['left',   get_ag_lang('IMAGE_POSITION_LEFT')],
									['right',  get_ag_lang('IMAGE_POSITION_RIGHT')]
								]
							}),
							listeners: {
								'select': {
									fn:function(combo,record,index){
										Cookies.set('ag_annotation.images.position',record.get('value'));
										try{
											getViewImages().getStore().reload();
										}catch(e){
											_dump(e);
										}
									},scope:this
								}
							}
						});

						new Ext.form.ComboBox({
							id: 'sortSelect',
							renderTo: 'bp3d-content-panel-header-content-sort-combobox-render',
							typeAhead: true,
							triggerAction: 'all',
							width: get_ag_lang('SORT_WIDTH'),
//							width: 110,
							width: 140,
//							listWidth: get_ag_lang('SORT_LIST_WIDTH'),
							listWidth: 140,
							editable: false,
							mode: 'local',
							displayField: 'desc',
							valueField: 'name',
							lazyInit: false,
//							value: '',
//							value: 'f_id',
							value: 'volume',
							disabled : true,
							store: new Ext.data.SimpleStore({
								fields: ['name', 'desc'],
								data : [
/*
									['',        get_ag_lang('SORT_TITLE_NONE')],
									['b_id',    get_ag_lang('REP_ID')],
									['f_id',    get_ag_lang('CDI_NAME')],
									['name_e',  get_ag_lang('DETAIL_TITLE_NAME_E')],
//									['name_j',  get_ag_lang('SORT_TITLE_NAME_J')],
//									['name_k',  get_ag_lang('SORT_TITLE_NAME_K')],
//									['name_l',  get_ag_lang('SORT_TITLE_NAME_L')],
									['zmin',    'Zmin'],
									['zmax',    'Zmax'],
									['volume',  get_ag_lang('SORT_TITLE_VOLUME')],
									['lastmod', get_ag_lang('SORT_TITLE_LAST')],
									['tweet_num', 'Tweet']
*/

									['f_id',    'Concept ID'],
									['name_e',  'Concept name'],
									['b_id',    'Representation ID'],
									['density', 'Representation density'],
									['volume',  'Volume'],
									['zmax',    'Z max'],
									['zmin',    'Z min'],
									['lastmod', 'Last modified'],
									['tweet_num', 'Tweet'],
									['taid',    'TAID']

								]
							}),
							listeners: {
								'select': {
									fn:function(combo,record,index){
										try{
											getViewImages().getStore().reload();
										}catch(e){
											_dump(e);
										}
									},scope:this}
							}
						});

						Ext.getCmp('contents-tab-panel').on({
							tabchange: {
								fn: function(tabpanel,tab){
									if(tab.id != 'contents-tab-bodyparts-panel') return;
									comp.setHeight(comp.initialConfig.height);
									comp.findParentByType('panel').doLayout();
								},
								buffer: 250
							}
						});

						\$('input#bp3d-content-panel-header-content-degenerate-same-shape-icons').change(function(){
							try{
								getViewImages().getStore().reload();
							}catch(e){
								_dump(e);
							}
						});

					}
				}

			}
		}]
	});


	var bp3d_contents_detail_information_toolbar = null;
HTML
if($lsdb_Auth && 0){
	print <<HTML;
	bp3d_contents_detail_information_toolbar = new Ext.Toolbar([
		'->',
		{
			hidden : true,
			text: get_ag_lang('ADMIN_MENU_ADD_TITLE'),
			iconCls: 'badd',
			listeners: {
				'click': {
					fn : function(self,e){
						setTimeout(function(){
							try{
								openWindowContent();
							}catch(e){alert(e);}
						},250);
					},scope : this}
			}
		},'-',{
			text: get_ag_lang('ADMIN_MENU_UPDATE_TITLE'),
			iconCls: 'bupdate',
			listeners: {
				'click': {
					fn : function(self,e){
						setTimeout(function(){
							var data = null;
							var dataview = getViewImages();
							if(!dataview) return;
							var selRecs = dataview.getSelectedRecords();
							if(selRecs && selRecs.length > 0){
								data = selRecs[0].data;
							}else{
								var selNode = null;
								var treeCmp = Ext.getCmp('navigate-tree-panel');
								if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
								if(selNode) data = selNode.attributes.attr;
							}
							if(!Ext.isEmpty(data)) openWindowContent(data);
						},250);
					},scope : this}
			}
		},'-',{
			text: get_ag_lang('ADMIN_MENU_DELETE_TITLE'),
			iconCls: 'bdelete',
			listeners: {
				'click': {
					fn : function(self,e){
						setTimeout(function(){
							try{
								var data = null;
								var dataview = getViewImages();
								if(!dataview) return;
								var selRecs = dataview.getSelectedRecords();
								if(selRecs && selRecs.length > 0){
									data = selRecs[0].data;
								}else{
									var selNode = null;
									var treeCmp = Ext.getCmp('navigate-tree-panel');
									if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
									if(selNode) data = selNode.attributes.attr;
								}
								if(!Ext.isEmpty(data)) openWindowContent(data,true);
							}catch(e){alert(e);}
						},250);
					},scope : this}
			}
		}
	]);
HTML
}
if($lsdb_Auth && $editLSDBTermHidden ne 'true'){
	print <<HTML;
	bp3d_contents_detail_information_toolbar = new Ext.Toolbar([
		'->','-',
		{
			text: get_ag_lang('ADMIN_MENU_UPDATE_TITLE'),
			iconCls: 'bupdate',
			listeners: {
				'click': {
					fn : function(self,e){
						setTimeout(function(){
							var data = null;
							var dataview = getViewImages();
							if(!dataview) return;
							var selRecs = dataview.getSelectedRecords();
							if(selRecs && selRecs.length > 0){
								data = selRecs[0].data;
							}else{
								var selNode = null;
								var treeCmp = Ext.getCmp('navigate-tree-panel');
								if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
								if(selNode) data = selNode.attributes.attr;
							}
							if(!Ext.isEmpty(data)) openContentEditWindow(data);
						},250);
					},scope : this}
			}
		}
	]);
HTML
}
print <<HTML;
	var bp3d_contents_detail_information_panel = new Ext.Panel({
		title       : get_ag_lang('DETAIL_TITLE_TAB_INFORMATION'),
		id          : 'bp3d-contents-detail-information-panel',
		split       : true,
		autoScroll  : true,
		collapsible : true,
		width       : 200,
		minWidth    : 150,
		maxWidth    : 230,
		tbar        : bp3d_contents_detail_information_toolbar
	});

	var bp3d_contents_detail_annotation_store_fields = [
		{name: 'f_id',     type:'string'},
		{name: 'c_id',     type:'int'},
		{name: 'c_pid',    type:'int'},
		{name: 'c_openid', type:'string'},
		{name: 'c_name',   type:'string'},
		{name: 'c_email',  type:'string'},
		{name: 'c_title',  type:'string'},
		{name: 'c_comment',type:'string'},
		{name: 'c_entry',  type:'date', dateFormat:'timestamp'},
		{name: 'c_image',  type:'string'},
		{name: 'c_image_thumb', type:'string'},
		{name: 'ct_id',    type:'int'},
		{name: 'cs_id',    type:'int'},
		{name: 'tgi_version', type:'string'},
		{name: 't_name',    type:'string'}
	];

	updateCommentChildTimeoutID = null;
	updateCommentChildStack = [];
	updateCommentChild = function(){
		if(updateCommentChildStack.length == 0) return;
		var data = updateCommentChildStack.shift();
		var elem = Ext.get('bp3d-contents-detail-annotation-panel'+'_comment_child_'+data.c_id);
		if(Ext.isEmpty(elem)) elem = Ext.get('bp3d-detail-annotation-panel'+'_comment_child_'+data.c_id);
		if(elem){
			bp3d_contents_detail_annotation_child_store.load({params : {c_pid : data.c_id}});
		}else{
			if(updateCommentChildTimeoutID) clearTimeout(updateCommentChildTimeoutID);
			updateCommentChildTimeoutID = setTimeout(updateCommentChild,0);
		}
	};

	var bp3d_contents_detail_annotation_child_store = new Ext.data.JsonStore({
		url           : 'get-comment.cgi',
		root          : 'topics',
		totalProperty : 'totalCount',
		remoteSort    : true,
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},
		fields : bp3d_contents_detail_annotation_store_fields,
		listeners: {
			'beforeload' : function(store,options){
				store.baseParams = store.baseParams || {};
			},
			'load' : function(store,records,options){
				if(records.length>0){
					var c_pid = records[0].data.c_pid;
					var data = [];
					for(var i=0,len=records.length;i<len;i++){
						bp3d_contents_detail_annotation_dataview_formatData(records[i].data);
						data.push(records[i].data);
						updateCommentChildStack.push(records[i].data);
					}
					if(!Ext.isEmpty(c_pid)){
						var panel_id = 'bp3d-contents-detail-annotation-panel';
						if(Ext.isEmpty(commentContentsDetailsChildTemplate)) commentContentsDetailsChildTemplate = createCommentDetailsChildTemplate(panel_id)
						var elem = Ext.get(panel_id+'_comment_child_'+c_pid);
						if(elem) commentContentsDetailsChildTemplate.overwrite(elem,data);

						var panel_id = 'bp3d-detail-annotation-panel';
						if(Ext.isEmpty(commentDetailsChildTemplate)) commentDetailsChildTemplate = createCommentDetailsChildTemplate(panel_id)
						var elem = Ext.get(panel_id+'_comment_child_'+c_pid);
						if(elem) commentDetailsChildTemplate.overwrite(elem,data);
					}
				}
				if(updateCommentChildTimeoutID) clearTimeout(updateCommentChildTimeoutID);
				updateCommentChildTimeoutID = setTimeout(updateCommentChild,0);
				bp3d_contents_detail_annotation_all_store.add(records);
			},
			'loadexception': function(){
			},
			'datachanged': function(){
			},
			scope:this
		}
	});

	var bp3d_contents_detail_annotation_all_store = new Ext.data.SimpleStore({
		root          : 'topics',
		totalProperty : 'totalCount',
		fields        : bp3d_contents_detail_annotation_store_fields
	});

	var bp3d_contents_detail_annotation_store = new Ext.data.JsonStore({
		url           : 'get-comment.cgi',
		root          : 'topics',
		totalProperty : 'totalCount',
		remoteSort    : true,
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},

		fields : bp3d_contents_detail_annotation_store_fields,

		listeners: {
			'beforeload' : function(store,options){
				store.baseParams = store.baseParams || {};
				delete store.baseParams.f_id;
				delete store.baseParams.version;
				bp3d_contents_detail_annotation_all_store.removeAll();

				if(contents_tabs.layout.activeItem.id == 'contents-tab-bodyparts-panel'){
					if(contents_panel.layout.activeItem.id == 'viewpage-panel'){
						var dataview = getViewImages();
						if(!dataview) return;
						var selections = dataview.getSelectedRecords();
						var data = null;
						if(selections && selections.length > 0){
							data = selections[0].data;
						}else{
							var selNode = null;
							var treeCmp = Ext.getCmp('navigate-tree-panel');
							if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
							if(selNode) data = selNode.attributes.attr;
						}
						if(data) store.baseParams.f_id = data.f_id;
						try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
						store.baseParams.version = bp3d_version;
					}else if(contents_panel.layout.activeItem.id == 'toppage-panel'){
						store.baseParams.f_id = "0";
					}
				}else if(contents_tabs.layout.activeItem.id == 'contents-tab-home-panel'){
					store.baseParams.f_id = "0";
				}

				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) store.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('bp3d-version-combo').getStore();
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
			'load' : function(store,records,options){

				try{Ext.getCmp('bp3d-contents-detail-annotation-panel').setTitle('Review ('+records.length+')');}catch(e){}
				try{Ext.getCmp('bp3d-detail-annotation-panel').setTitle('Review ('+records.length+')');}catch(e){}

				if(records.length>0){
					var c_pid = records[0].data.c_pid;
					for(var i=0,len=records.length;i<len;i++){
						updateCommentChildStack.push(records[i].data);
					}
					if(Ext.isEmpty(c_pid)){
						if(updateCommentChildTimeoutID) clearTimeout(updateCommentChildTimeoutID);
						updateCommentChildTimeoutID = setTimeout(updateCommentChild,500);
					}
				}
				bp3d_contents_detail_annotation_all_store.add(records);
			},
			'loadexception': function(){
				if(bp3d_contents_detail_annotation_pagingBar) bp3d_contents_detail_annotation_pagingBar.disable();
				if(bp3d_contents_detail_annotation_panel) bp3d_contents_detail_annotation_panel.disable();

				if(bp3d_detail_annotation_pagingBar) bp3d_detail_annotation_pagingBar.disable();
				if(bp3d_detail_annotation_panel) bp3d_detail_annotation_panel.disable();
			},
			scope:this
		}
	});
	bp3d_contents_detail_annotation_store.setDefaultSort('entry', 'desc');

	var bp3d_contents_detail_annotation_dataview_formatData = function(data){

		data.dateString = formatTimestamp(data.c_entry);

		data.nameString = null;
		if(data.c_name){
			if(data.c_email){
				data.nameString = '<a class="comment-details-info-comment-mail" href="mailto:'+data.c_email+'">'+data.c_name+'</a>';
			}else{
				data.nameString = data.c_name;
			}
		}else if(data.c_openid){
			if(data.c_email){
				data.nameString = '<a class="comment-details-info-comment-mail" href="mailto:'+data.c_email+'">'+data.c_openid+'</a>';
			}else{
				data.nameString = data.c_openid;
			}
		}

		data.commentString = null;
		if(data.c_comment){
			data.commentString = data.c_comment.replace(/\\n/g,"<br>");
		}

		data.cs_name = null;
		if(data.cs_id && comment_status[data.cs_id]){
			if(data.cs_id == 1){
				data.cs_name = '<span class="pending">'+comment_status[data.cs_id]+'</span>';
			}else if(data.cs_id == 2){
				data.cs_name = '<span class="ok">'+comment_status[data.cs_id]+'</span>';
			}else{
				data.cs_name = comment_status[data.cs_id];
			}
		}

		return data;
	};

	var bp3d_contents_detail_annotation_dataview_click = function(dataview,index,node,e){
		var target = e.getTarget('div.comment-details-info-comment',1,true);
		if(target){
			var c_id = target.dom.getAttribute('c_id');
			index = bp3d_contents_detail_annotation_all_store.find('c_id',c_id);
			if(index>=0) openWindowComment(bp3d_contents_detail_annotation_all_store.getAt(index).copy().data);
			return;
		}

		target = e.getTarget('a.comment-details-info-comment-reply',1,true);
		if(target){
			var c_id = target.dom.getAttribute('c_id');
			index = bp3d_contents_detail_annotation_all_store.find('c_id',c_id);
			if(index>=0) openWindowComment(bp3d_contents_detail_annotation_all_store.getAt(index).copy().data);
			return;
		}

		target = e.getTarget('a.comment-details-info-comment-edit',1,true);
		if(target){
			var c_id = target.dom.getAttribute('c_id');
			if(!Ext.isEmpty(c_id)) editFeedback(c_id,{store:bp3d_contents_detail_annotation_all_store});
			return;
		}

		target = e.getTarget('a.comment-details-info-comment-delete',1,true);
		if(target){
			var c_id = target.dom.getAttribute('c_id');
			if(!Ext.isEmpty(c_id)) deleteFeedback(c_id,{store:bp3d_contents_detail_annotation_all_store});
			return;
		}

		target = e.getTarget('a.comment-details-info-comment-thumb',2,true);
		if(target){
			var form = Ext.getDom('link-form');
			if(form){
				form.action = target.dom.href;
				form.submit();
				e.stopEvent();
			}
			return;
		}

		target = e.getTarget('a.comment-details-info-comment-mail',1,true);
		if(target){
			var form = Ext.getDom('link-form');
			if(form){
				form.action = target.dom.href;
				form.submit();
				e.stopEvent();
			}
			return;
		}

		target = e.getTarget('a',1,true);
		if(target){
			var form = Ext.getDom('comment-link-form');
			if(form){
				form.action = target.dom.href;

				while(form.lastChild){
					form.removeChild(form.lastChild);
				}
				var loc_path = target.dom.href;
				var loc_search = "";
				var loc_hash = "";
				var loc_search_index = loc_path.indexOf("?");
				if(loc_search_index>=0){
					loc_search = loc_path.substr(loc_search_index+1);
					loc_path = loc_path.substr(0,loc_search_index);
					form.action = loc_path;
				}
				var loc_hash_index = loc_search.indexOf("#");
				if(loc_hash_index>=0){
					loc_hash = loc_search.substr(loc_hash_index+1);
					loc_search = loc_search.substr(0,loc_hash_index);
				}

				if(loc_search){
					var loc_search = Ext.urlDecode(loc_search,true);
					for(var key in loc_search){
						var elem = form.ownerDocument.createElement("input");
						elem.setAttribute("type","hidden");
						elem.setAttribute("name",key);
						elem.setAttribute("value",loc_search[key]);
						form.appendChild(elem);
					}
				}
				if(loc_hash) form.setAttribute("action",loc_path + "#" + loc_hash);

				form.submit();
				e.stopEvent();
			}
			return;
		}
	};

	if(Ext.isEmpty(commentContentsDetailsTemplate)) commentContentsDetailsTemplate = createCommentDetailsTemplate('bp3d-contents-detail-annotation-panel');
	var bp3d_contents_detail_annotation_dataview = new Ext.DataView({
		tpl          : commentContentsDetailsTemplate,
		itemSelector : 'div.comment-details-info',
		overClass    : 'x-view-over',
		autoShow     : true,
		autoHeight   : true,
		singleSelect : true,
		multiSelect  : false,
		emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_REVIEW')+'</div>',
		loadingText  : get_ag_lang('MSG_LOADING_DATA'),
		store        : bp3d_contents_detail_annotation_store,
		renderTo     : 'view-images-detail-annotation-dataview-render',
		listeners: {
			'render': {fn:function(view){}, scope:this},
			'show': {fn:function(view){}, scope:this},
			'selectionchange': {fn:function(view,selections){}, scope:this, buffer:0},
			'loadexception'  : {fn:onLoadException, scope:this},
			'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}},
			'click'          : {fn:bp3d_contents_detail_annotation_dataview_click,scope:this}
		},
		prepareData: bp3d_contents_detail_annotation_dataview_formatData.createDelegate(this)
	});

	var bp3d_contents_detail_annotation_pagingBar = new Ext.PagingToolbar({
		pageSize    : 20,
		store       : bp3d_contents_detail_annotation_store,
		displayInfo : false,
		displayMsg  : '',
		emptyMsg    : '',
		hideMode    : 'offsets',
		hideParent  : true
	});
	if(bp3d_contents_detail_annotation_pagingBar){
		bp3d_contents_detail_annotation_pagingBar.firstText = get_ag_lang('PAGING_FIRST');
		bp3d_contents_detail_annotation_pagingBar.lastText = get_ag_lang('PAGING_LAST');
		bp3d_contents_detail_annotation_pagingBar.nextText = get_ag_lang('PAGING_NEXT');
		bp3d_contents_detail_annotation_pagingBar.prevText = get_ag_lang('PAGING_PREV');
		bp3d_contents_detail_annotation_pagingBar.refreshText = get_ag_lang('PAGING_REFRESH');
	}

	var bp3d_contents_detail_annotation_panel = new Ext.Panel({
		title      : 'Review',
		id         : 'bp3d-contents-detail-annotation-panel',
		bbar       : bp3d_contents_detail_annotation_pagingBar,
		autoScroll : true,
		items      : bp3d_contents_detail_annotation_dataview,
		listeners: {
			'render' : {
				fn : function(panel){
					bp3d_contents_detail_annotation_store.reload();
				},
				scope  : this,
				buffer : 0
			}
		}
	});

	var bp3d_contents_detail_wiki_panel = new Ext.Panel({
		title     : 'Information(Wiki)',
		id        : 'bp3d-contents-detail-wiki-panel',
		autoScroll: false,
		contentEl : 'bp3d-contents-detail-wiki-panel-render',
		listeners: {
			resize: function(panel,adjWidth,adjHeight,rawWidth,rawHeight){
				Ext.get('bp3d-contents-detail-wiki-panel-iframe').setSize(adjWidth,adjHeight);
			}
		}
	});

	var bp3d_contents_detail_tweet_panel = new Ext.Panel({
		title: get_ag_lang('DETAIL_TITLE_TAB_TWEET'),
		id   : 'bp3d-contents-detail-tweet-panel',
		autoScroll: true
	});

	var bp3d_contents_detail_concept_panel = new Ext.Panel({
		title     : get_ag_lang('DETAIL_TITLE_TAB_CONCEPT'),
		id        : 'bp3d-contents-detail-concept-panel',
		autoScroll: true
	});

	var bp3d_contents_detail_panel = new Ext.TabPanel({
		id          : 'bp3d-contents-detail-panel',
		title       : get_ag_lang('DETAIL_TITLE'),
		region      : 'east',
		split       : true,
		border      : true,
		width       : 230,
		minWidth    : 230,
		maxWidth    : 330,
		activeTab   : 0,
HTML
if($lsdb_Auth && $reviewHidden ne 'true'){
	if($wikiLinkHidden eq 'true'){
		print <<HTML;
		layoutOnTabChange: true,
		items       : [bp3d_contents_detail_information_panel,bp3d_contents_detail_annotation_panel],
HTML
	}else{
		print <<HTML;
		enableTabScroll : true,
		layoutOnTabChange: true,
		deferredRender: false,
		items       : [bp3d_contents_detail_wiki_panel,bp3d_contents_detail_information_panel,bp3d_contents_detail_annotation_panel],
HTML
	}
}elsif($wikiLinkHidden ne 'true'){
	print <<HTML;
		deferredRender: false,
		items       : [bp3d_contents_detail_wiki_panel,bp3d_contents_detail_information_panel],
HTML
}else{
	print <<HTML;
		deferredRender: false,
		enableTabScroll: true,
		items       : [
			bp3d_contents_detail_information_panel,
			bp3d_contents_detail_tweet_panel,
			bp3d_contents_detail_concept_panel
		],
HTML
}
print <<HTML;
		listeners : {
			'afterlayout' : function(panel,layout){
				afterLayout(panel);
			},
			scope : this
		}
	});


	var toppage_info_panel = new Ext.Panel({
		id : 'toppage-info-base-panel',
		hidden : $toppageHidden,
		title : get_ag_lang('TOP_TITLE'),
		frame : true,
		collapsible : true,
		region: 'north',
		minHeight : 100,
		height : 100,
		split:true,
		items: [{
			id : 'toppage-info-panel',
			autoLoad : {
				url     : '$info_html',
				nocache : true
			}
		}],
HTML
if($lsdb_Auth){
print <<HTML;
		tools : [{
			id:'gear',
			qtip:'Edit',
			hidden:false,
			handler: function(event, toolEl, panel){
				var edit_form = new Ext.form.FormPanel({
					border : false,
					width  : 600,
					items  : [{
						xtype     : 'htmleditor',
						id        : 'bio',
						value     : (Ext.getCmp('toppage-info-panel').body).dom.innerHTML,
						hideLabel : true,
						anchor    : '100% 100%'
					}]
				});

				var edit_window = new Ext.Window({
					title       : get_ag_lang('TOP_EDIT_TITLE'),
					width       : 600,
					height      : 400,
					minWidth    : 400,
					minHeight   : 250,
					plain       : true,
					bodyStyle   :'padding:5px;',
					buttonAlign :'right',
					modal       : true,
					layout      : 'fit',
					items       : edit_form,
					buttons: [{
						text    : get_ag_lang('COMMENT_WIN_TITLE_SEND'),
						handler : function(){
							var value = Ext.getCmp('bio').getValue();
							var params = {
								parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
								lng    : gParams.lng,
								html   : value
							};
							Ext.Ajax.request({
								url     : 'put-info.cgi',
								method  : 'POST',
								params  : Ext.urlEncode(params),
								success : function(conn,response,options){
									try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
									if(!results) results = {success:false,msg:""};
									if(!results.msg) results.msg = "";
									if(results.success){
										Ext.MessageBox.show({
											title   : get_ag_lang('TOP_EDIT_TITLE'),
											msg     : get_ag_lang('ADMIN_FORM_REG_OKMSG'),
											buttons : Ext.MessageBox.OK,
											icon    : Ext.MessageBox.INFO,
											fn      : function(){
												edit_window.close();
												(Ext.getCmp('toppage-info-panel').body).update(value);
											}
										});
										return;
									}
									Ext.MessageBox.show({
										title   : get_ag_lang('TOP_EDIT_TITLE'),
										msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+results.msg+' ]',
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
								},
								failure : function(conn,response,options){
									try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
									if(!results) results = {success:false,msg:""};
									if(!results.msg) results.msg = "";
									Ext.MessageBox.show({
										title   : get_ag_lang('TOP_EDIT_TITLE'),
										msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+results.msg+' ]',
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
								}
							});
						}
					},{
						text: get_ag_lang('COMMENT_WIN_TITLE_CANCEL'),
						handler : function(){
							edit_window.close();
						}
					}]
				});
				edit_window.show();
			}
		}],
HTML
}
print <<HTML;
		border : true,
		listeners: {
			'afterlayout' : function(panel,layout){
				afterLayout(panel);
			},
			scope : this
		}
	});

	afterLayout = function(panel){
		try{
			if(!Ext.isIE) return;
			if(!panel.rendered) return;
			if(panel.collapsed) panel.expand(false);
//			if(panel.collapsed) return;

			var box = panel.getBox();
			if(box.x==0 && box.y==0) return;
			var width  = Ext.isEmpty(panel.initialConfig.minWidth) ?box.width :panel.initialConfig.minWidth;
			var height = Ext.isEmpty(panel.initialConfig.minHeight)?box.height:panel.initialConfig.minHeight;
			if((box.width<width && height > 0) || (width > 0 && box.height<height)){
				panel.setSize(width,height);
				panel.ownerCt.doLayout();
			}
		}catch(e){
//			for(var key in e){
//				_dump("afterLayout():e["+key+"]="+e[key]);
//			}
			try{_dump("afterLayout():panel.layout=["+panel.layout+"]");}catch(e){}
		}
	};

	var toppage_annotation_toolbar = new Ext.Toolbar([
		'->','-',
		{
			id        : 'btn-add-comment',
			text      : get_ag_lang('COMMENT_TITLE_PLUS'),
			iconCls   : 'comment_add-icon',
			tooltip   : get_ag_lang('COMMENT_TITLE_PLUS'),
			listeners : {
				'click': {fn:function(self,e){openWindowComment();},scope:this}
			}
		}
	]);

	var toppage_annotation_pagingBar = new Ext.PagingToolbar({
		pageSize    : 20,
		store       : bp3d_contents_detail_annotation_store,
		displayInfo : false,
		displayMsg  : '',
		emptyMsg    : '',
		hideMode    : 'offsets',
		hideParent  : true
	});
	if(toppage_annotation_pagingBar){
		toppage_annotation_pagingBar.firstText = get_ag_lang('PAGING_FIRST');
		toppage_annotation_pagingBar.lastText = get_ag_lang('PAGING_LAST');
		toppage_annotation_pagingBar.nextText = get_ag_lang('PAGING_NEXT');
		toppage_annotation_pagingBar.prevText = get_ag_lang('PAGING_PREV');
		toppage_annotation_pagingBar.refreshText = get_ag_lang('PAGING_REFRESH');
	}

	var toppage_annotation_panel = new Ext.Panel({
		region: 'east',
		split: true,
		title      : 'Review',
		id         : 'toppage-annotation-panel',
		tbar       : toppage_annotation_toolbar,
		bbar       : toppage_annotation_pagingBar,
		autoScroll : true,
		width       : 220,
		minWidth    : 220,
		maxWidth    : 330,
		html       : '',
		listeners: {
			'render' : {
				fn : function(panel){
					bp3d_contents_detail_annotation_store.reload();
				},
				scope  : this,
				buffer : 0
			}
		}
	});
/*
	var toppage_panel = new Ext.Panel({
		id     : 'toppage-panel',
		region : 'center',
		hidden : $toppageHidden,
		layout : 'border',
		border : false,
		items : [{
			region : 'center',
			border : false,
			layout : 'border',
			items: [toppage_info_panel,whatnew_panel]
		}],
		listeners : {
			'show' : function(panel){
				panel.doLayout();
			},
			scope:this
		}
	});
*/
	var bp3d_contents_panel = new Ext.Panel({
//		title      : get_ag_lang('CONTENT_TITLE'),
//		collapsible : true,
		id         : 'bp3d-contents-panel',
		closable   : false,
		autoScroll : false,
		bodyBorder : false,
		border     : false,
		layout     : 'border',
		items : [bp3d_contents_thumbnail_panel,bp3d_contents_detail_panel],
		listeners : {
			'show' : function(panel){
				panel.doLayout();
			},
			scope:this
		}
	});

	var bp3d_detail_information_toolbar = null;
HTML
if($lsdb_Auth){
	print <<HTML;
	bp3d_detail_information_toolbar = new Ext.Toolbar([
		'->','-',
		{
			text: get_ag_lang('ADMIN_MENU_UPDATE_TITLE'),
			iconCls: 'bupdate',
			listeners: {
				'click': {
					fn : function(self,e){
						setTimeout(function(){
							var data = null;
							var dataview = getViewImages();
							if(!dataview) return;
							var selRecs = dataview.getSelectedRecords();
							if(selRecs && selRecs.length > 0){
								data = selRecs[0].data;
							}else{
								var selNode = null;
								var treeCmp = Ext.getCmp('navigate-tree-panel');
								if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
								if(selNode) data = selNode.attributes.attr;
							}
							if(!Ext.isEmpty(data)) openContentEditWindow(data);
						},250);
					},scope : this}
			}
		}
	]);
HTML
}
print <<HTML;

	var bp3d_detail_information_panel = new Ext.Panel({
		title       : 'Information',
		id          : 'bp3d-detail-information-panel',
		split       : true,
		autoScroll  : true,
		collapsible : true,
		width       : 200,
		minWidth    : 150,
		maxWidth    : 230,
		tbar        : bp3d_detail_information_toolbar
	});

	if(Ext.isEmpty(commentDetailsTemplate)) commentDetailsTemplate = createCommentDetailsTemplate('bp3d-detail-annotation-panel');
	var bp3d_detail_annotation_dataview = new Ext.DataView({
		tpl          : commentDetailsTemplate,
		itemSelector : 'div.comment-details-info',
		overClass    : 'x-view-over',
		autoShow     : true,
		autoHeight   : true,
		singleSelect : true,
		multiSelect  : false,
		emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_REVIEW')+'</div>',
		loadingText  : get_ag_lang('MSG_LOADING_DATA'),
		store        : bp3d_contents_detail_annotation_store,
		renderTo     : 'bp3d-detail-annotation-dataview-render',
		listeners: {
			'render': {fn:function(view){}, scope:this},
			'show': {fn:function(view){}, scope:this},
			'selectionchange': {fn:function(view,selections){}, scope:this, buffer:0},
			'loadexception'  : {fn:onLoadException, scope:this},
			'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}},
			'click'          : {fn:bp3d_contents_detail_annotation_dataview_click,scope:this}
		},
		prepareData: bp3d_contents_detail_annotation_dataview_formatData.createDelegate(this)
	});

	var bp3d_detail_annotation_pagingBar = new Ext.PagingToolbar({
		pageSize    : 20,
		store       : bp3d_contents_detail_annotation_store,
		displayInfo : false,
		displayMsg  : '',
		emptyMsg    : '',
		hideMode    : 'offsets',
		hideParent  : true
	});
	if(bp3d_detail_annotation_pagingBar){
		bp3d_detail_annotation_pagingBar.firstText = get_ag_lang('PAGING_FIRST');
		bp3d_detail_annotation_pagingBar.lastText = get_ag_lang('PAGING_LAST');
		bp3d_detail_annotation_pagingBar.nextText = get_ag_lang('PAGING_NEXT');
		bp3d_detail_annotation_pagingBar.prevText = get_ag_lang('PAGING_PREV');
		bp3d_detail_annotation_pagingBar.refreshText = get_ag_lang('PAGING_REFRESH');
	}

	var bp3d_detail_annotation_panel = new Ext.Panel({
		title      : 'Review',
		id         : 'bp3d-detail-annotation-panel',
		bbar       : bp3d_detail_annotation_pagingBar,
		autoScroll : true,
		items      : bp3d_detail_annotation_dataview,
		listeners: {
			'render' : {
				fn : function(panel){
//					bp3d_contents_detail_annotation_store.reload();
				},
				scope  : this,
				buffer : 0
			}
		}
	});

	var bp3d_detail_panel = new Ext.TabPanel({
		id         : 'bp3d-detail-panel',
		closable   : false,
		autoScroll : false,
		bodyBorder : false,
		border     : false,
		header     : true,
		activeTab   : 0,
		layoutOnTabChange : true,
HTML
if($lsdb_Auth && $reviewHidden ne 'true'){
	print <<HTML;
		items       : [bp3d_detail_information_panel,bp3d_detail_annotation_panel],
HTML
}else{
	print <<HTML;
		items       : bp3d_detail_information_panel,
HTML
}
print <<HTML;
		listeners : {
			'afterlayout' : function(panel,layout){
				afterLayout(panel);
			},
			'show' : function(panel){
				panel.doLayout();
			},
			scope:this
		}
	});

	var view_panel = new Ext.Panel({
		id         : 'viewpage-panel',
		closable   : false,
		autoScroll : false,
		bodyBorder : false,
		border     : false,
		layout     : 'card',
		activeItem : 0,
		items      : [bp3d_contents_panel,bp3d_detail_panel],
		listeners  : {
			'show' : function(panel){
				panel.doLayout();
			},
			scope:this
		}
	});

	var contents_panel = new Ext.Panel({
		id         : 'content-card-panel',
		region     : 'center',
		layout     : 'card',
		split      : true,
		autoScroll : false,
		border     : true,
		deferredRender : true,
//		activeItem : 1,
//		items      : [toppage_panel,view_panel]
		activeItem : 0,
		items      : [view_panel]
	});

	Ext.menu.RangeMenu.prototype.icons = {
		gt: 'css/greater_then.png',
		lt: 'css/less_then.png',
		eq: 'css/equals.png'
	};
	Ext.menu.RangeMenu.prototype.iconStyles = {
		gt: 'position:relative;margin: 0px 3px 2px 0px;', 
		lt: 'position:relative;margin: 0px 3px 2px 0px;',
		eq: 'position:relative;margin: 0px 3px 2px 0px;'
	};
	Ext.menu.RangeMenu.prototype.fieldCfg = {
		gt: {style:{paddingLeft:'17px',marginLeft:'-19px'}},
		lt: {style:{paddingLeft:'17px',marginLeft:'-19px'}},
		eq: {style:{paddingLeft:'17px'}}
	};
	Ext.grid.filter.StringFilter.prototype.icon = 'css/find.png';
	Ext.grid.filter.StringFilter.prototype.textfieldCfg = {style:{paddingLeft:'16px'}};

	Ext.grid.filter.BooleanFilter.prototype.yesText = get_ag_lang('SEARCH_GRID_FILTER_YES');
	Ext.grid.filter.BooleanFilter.prototype.noText = get_ag_lang('SEARCH_GRID_FILTER_NO');

	var navigate_grid_fields = [
		{name:'f_id'},
		{name:'b_id'},
		{name:'common_id'},
		{name:'name_j'},
		{name:'name_e'},
		{name:'name_k'},
		{name:'name_l'},
		{name:'syn_j'},
		{name:'syn_e'},
		{name:'organsys_j'},
		{name:'organsys_e'},
		{name:'organsys'},
		{name:'phase'},
		{name:'taid'},
		{name:'icon'},
		{name:'seg_color'},
		{name:'xmin',    type:'float'},
		{name:'xmax',    type:'float'},
//		{name:'xcenter', type:'float', convert:function(v,rec){if(Ext.isEmpty(rec.xmax)||Ext.isEmpty(rec.xmin)){return null;}else{return (Number(rec.xmax)+Number(rec.xmin))/2;}}},
		{name:'ymin',    type:'float'},
		{name:'ymax',    type:'float'},
//		{name:'ycenter', type:'float', convert:function(v,rec){if(Ext.isEmpty(rec.ymax)||Ext.isEmpty(rec.ymin)){return null;}else{return (Number(rec.ymax)+Number(rec.ymin))/2;}}},
		{name:'zmin',    type:'float'},
		{name:'zmax',    type:'float'},
//		{name:'zcenter', type:'float', convert:function(v,rec){if(Ext.isEmpty(rec.zmax)||Ext.isEmpty(rec.zmin)){return null;}else{return (Number(rec.zmax)+Number(rec.zmin))/2;}}},
		{name:'volume',  type:'float'},
		{name:'cube_volume',  type:'float'},
		{name:'density',  type:'float', convert:function(v,rec){if(Ext.isEmpty(v)){return null;}else{return Math.round(Number(v)*10000)/100;}}},
		{name:'primitive',  type:'boolean'},
		{name:'state'},
		{name:'entry',   type:'date', dateFormat: 'timestamp'},
		{name:'lastmod', type:'date', dateFormat: 'timestamp'},
		{name:'delcause'},
		{name:'m_openid'}
	];

	var navigate_grid_col_rep_id = {
		dataIndex:'b_id',
		header:get_ag_lang('REP_ID'),
		id:'b_id',
		width: 70,
		resizable: true,
		hidden:$gridColHiddenID
	};
	var navigate_grid_col_entry = {
		dataIndex:'entry',
		header:get_ag_lang('GRID_TITLE_MODIFIED'),
		id:'entry',
		renderer:Ext.util.Format.dateRenderer('Y/m/d'),
		hidden:true
	};
	var navigate_grid_col_organsys = {
		dataIndex:'organsys',
		header:get_ag_lang('GRID_TITLE_ORGANSYS'),
		id:'organsys',
		hidden:true
	};

	navigate_grid_primitive_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		if(Ext.isEmpty(value)) value = false;
		if(value){
			value = get_ag_lang('ELEMENT_PRIMARY');
		}else{
			value = get_ag_lang('COMPOUND_SECONDARY');
		}
		return value;
	}
	var navigate_grid_col_primitive = {
		dataIndex:'primitive',
		header:get_ag_lang('REP_PRIMITIVE'),
		id:'primitive',
		renderer:navigate_grid_primitive_renderer,
		hidden:true
	};

	var navigate_grid_col_density = {
		dataIndex:'density',
		header:get_ag_lang('REP_DENSITY'),
		id:'density',
		hidden:true
	};

	var navigate_grid_icon_renderer = function(value,metadata,record,rowIndex,colIndex,store){
		if(record.data.seg_color) metadata.attr = 'style="background:'+record.data.seg_color+';"'
		value = '';
		if(!Ext.isEmpty(record.data.icon)) value = '<img width=16 height=16 src='+record.data.icon+'>';
		return value;
	};


	var navigate_grid_col_icon = {
		dataIndex:'seg_color',
		header:'',
		id:'seg_color',
		sortable: true,
		hidden:$gridColHiddenID,
		renderer:navigate_grid_icon_renderer,
		width:28,
		maxWidth:28,
		resizable:false,
		fixed:true,
		menuDisabled:true,
		hideable: false,
		resizable: false
	};

	var navigate_grid_cols = [
		navigate_grid_col_icon,
		navigate_grid_col_rep_id,
		{dataIndex:'f_id',   header:get_ag_lang('CDI_NAME'),                 id:'f_id', resizable:true, width: 72},
		{dataIndex:'common_id',header:'UniversalID',                     id:'common_id', hidden:$gridColHiddenUniversalID, fixed:$gridColFixedUniversalID},
HTML
print qq|		navigate_grid_col_rep_id,\n| if($moveGridOrder ne 'true');
print <<HTML;
//		{dataIndex:'name_j',   header:get_ag_lang('DETAIL_TITLE_NAME_J'),      id:'name_j', hidden:$gridColHiddenNameJ},
		{dataIndex:'name_j',   header:get_ag_lang('DETAIL_TITLE_NAME_J'),    id:'name_j', hidden:true},
		{dataIndex:'name_k',   header:get_ag_lang('DETAIL_TITLE_NAME_K'),    id:'name_k', hidden:true},
		{dataIndex:'name_e',   header:get_ag_lang('DETAIL_TITLE_NAME_E'),    id:'name_e'},
		{dataIndex:'name_l',   header:get_ag_lang('DETAIL_TITLE_NAME_L'),    id:'name_l', hidden:true},
HTML
if($moveGridOrder ne 'true'){
	print <<HTML;
		{dataIndex:'phase',    header:get_ag_lang('GRID_TITLE_PHASE'),       id:'phase', hidden:true},
		navigate_grid_col_entry,
HTML
}else{
	print <<HTML;
//		navigate_grid_col_organsys,
HTML
}
print <<HTML;
		{dataIndex:'xmin',     header:'Xmin(mm)',                        id:'xmin',    hidden:true},
		{dataIndex:'xmax',     header:'Xmax(mm)',                        id:'xmax',    hidden:true},
//		{dataIndex:'xcenter',  header:'Xcenter(mm)',                     id:'xcenter', hidden:true},
		{dataIndex:'ymin',     header:'Ymin(mm)',                        id:'ymin',    hidden:true},
		{dataIndex:'ymax',     header:'Ymax(mm)',                        id:'ymax',    hidden:true},
//		{dataIndex:'ycenter',  header:'Ycenter(mm)',                     id:'ycenter', hidden:true},
		{dataIndex:'zmin',     header:'Zmin(mm)',                        id:'zmin',    hidden:true},
		{dataIndex:'zmax',     header:'Zmax(mm)',                        id:'zmax',    hidden:true},
//		{dataIndex:'zcenter',  header:'Zcenter(mm)',                     id:'zcenter', hidden:true},
		{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',  hidden:true},
HTML
if($moveGridOrder ne 'true'){
#	print qq|		{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume', hidden:true},\n| if($removeGridColValume ne 'true');
#	print qq|		navigate_grid_col_organsys,\n| if($removeGridColOrganSystem ne 'true');
}else{
	print <<HTML;
		navigate_grid_col_entry,
HTML
}
print <<HTML;
		navigate_grid_col_density,
		navigate_grid_col_primitive,
		{dataIndex:'state',    header:'State',                           id:'state', hidden:true},
		{dataIndex:'taid',     header:'TAID',                            id:'taid',  hidden:true}
	];

	var navigate_grid = {
		ds : new Ext.data.JsonStore({
			url:'get-contents-list.cgi',
			totalProperty: 'total',
			root: 'records',
			fields: navigate_grid_fields,
			sortInfo: {field: 'name_e', direction: 'ASC'},
			remoteSort: true,
			baseParams : {
				parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
				lng    : gParams.lng
			},
			listeners: {
				'beforeload' : function(self,options){
//						_dump("beforeload()");
					self.baseParams = self.baseParams || {};
					try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
					if(self.baseParams.version != bp3d_version){
						self.baseParams.version = bp3d_version;
						options.params.start = 0;
					}
					delete self.baseParams.t_type;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					for(var key in init_bp3d_params){
						if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
					}

					try{
						var store = Ext.getCmp('bp3d-version-combo').getStore();
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
					try{
						if(!navigate_grid_panel.rendered) return;
						var tb = navigate_grid_panel.getTopToolbar();
						var count = tb.items.getCount();
						if(count==0) return;
						var item = tb.items.get(count-3);
						item.el.innerHTML='<label>'+self.getTotalCount()+'&nbsp;Objects</label>';
						if(navigate_grid_panel.disabled) navigate_grid_panel.enable();

						if(navigate_tabs.getActiveTab().id=='navigate-grid-panel'){
							var store = self;
							if(store && store.reader && store.reader.jsonData && !Ext.isEmpty(store.reader.jsonData.rep_num)){
								var t_type;
								for(t_type in store.reader.jsonData.rep_num){
									\$('label#navigate-north-panel-content-label-'+t_type).html('(<span>'+store.reader.jsonData.rep_num[t_type]+'</span>)');
								}
							}
						}

					}catch(e){
						_dump("load():"+e);
					}
				},
				scope:this
			}
		}),
		filters : new Ext.grid.GridFilters({
			filters:[
				{type:'string',  dataIndex:'common_id'},
				{type:'string',  dataIndex:'b_id'},
				{type:'string',  dataIndex:'name_j'},
				{type:'string',  dataIndex:'name_e'},
				{type:'string',  dataIndex:'name_k'},
				{type:'string',  dataIndex:'name_l'},
				{type:'numeric', dataIndex:'phase'},
				{type:'date',    dataIndex:'entry'},
				{type:'numeric', dataIndex:'xmin'},
				{type:'numeric', dataIndex:'xmax'},
				{type:'numeric', dataIndex:'ymin'},
				{type:'numeric', dataIndex:'ymax'},
				{type:'numeric', dataIndex:'zmin'},
				{type:'numeric', dataIndex:'zmax'},
				{type:'numeric', dataIndex:'volume'},
				{type:'numeric', dataIndex:'density'},
				{type:'boolean', dataIndex:'primitive'},
				{type:'string',  dataIndex:'organsys'},
				{type:'string',  dataIndex:'state'},
				{type:'string',  dataIndex:'taid'}
		]}),
		cm : new Ext.grid.ColumnModel(navigate_grid_cols)
	};
	navigate_grid.cm.defaultSortable = true;
	navigate_grid.cm.defaultWidth = 40;
	navigate_grid.cm.on({
		'hiddenchange' : function(column,columnIndex,hidden){
			resizeNavigateGridPanel();
		},
		scope: this,
		delay: 100
	});

	var navigate_grid_pagingBar = new Ext.PagingToolbar({
		id          : 'navigate-grid-paging-toolbar',
		pageSize    : 30,
		store       : navigate_grid.ds,
		displayInfo : false,
		displayMsg  : '',
		emptyMsg    : '',
		hideMode    : 'offsets',
		hideParent  : true
	});

	navigate_grid.ds.load({
		params:{
			start : 0,
			limit : (navigate_grid_pagingBar?navigate_grid_pagingBar.initialConfig.pageSize:30)
		}
	});

	var navigate_grid_panel = new Ext.grid.GridPanel({
		title   : 'List',
		id      : 'navigate-grid-panel',
		ds: navigate_grid.ds,
		cm: navigate_grid.cm,
		bbar : navigate_grid_pagingBar,
		enableColLock: false,
		loadMask: true,
		plugins: navigate_grid.filters,
		autoScroll:true,
		tbar : new Ext.Toolbar([
			'->',
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
							copyList(navigate_grid_panel);
						},
						scope:this
					}
				}
			}
HTML
}
print <<HTML;
		]),
		listeners : {
			"rowclick" : function(grid, rowIndex, event){
				selectPathCB();
			},
			"resize" : function(grid){
				resizeGridPanelColumns(grid);
			},
			"render" : function(grid){
				try{
					var tb = grid.getTopToolbar();
					var count = tb.items.getCount();
					if(count==0) return;
					var item = tb.items.get(1);
					item.el.innerHTML='<label>'+grid.getStore().getTotalCount()+'&nbsp;Objects</label>';
				}catch(e){
					_dump("render():"+e);
				}
				restoreHiddenGridPanelColumns(grid);
			},
			show: {
				fn: function(grid){
					_dump("show():["+grid.id+"]");
					var store = grid.getStore();
					if(store && store.reader && store.reader.jsonData && !Ext.isEmpty(store.reader.jsonData.rep_num)){
						var t_type;
						for(t_type in store.reader.jsonData.rep_num){
							\$('label#navigate-north-panel-content-label-'+t_type).html('(<span>'+store.reader.jsonData.rep_num[t_type]+'</span>)');
						}
					}
				},
				buffer:250
			},
			scope : this
		}
	});
	navigate_grid_panel.getColumnModel().on({
		'hiddenchange' : function(column,columnIndex,hidden){
			resizeGridPanelColumns(navigate_grid_panel);
			saveHiddenGridPanelColumns(navigate_grid_panel);
		},
		scope: this,
		delay: 100
	});

	createSearchGridPanel = function(aQuery,aOptions){

		navigate_grid_primitive_renderer = function(value,metadata,record,rowIndex,colIndex,store){
			if(Ext.isEmpty(value)) value = false;
			if(value){
				value = get_ag_lang('ELEMENT_PRIMARY');
			}else{
				value = get_ag_lang('COMPOUND_SECONDARY');
			}
			return value;
		}
		var navigate_search_grid_col_primitive = {
			dataIndex:'primitive',
			header:get_ag_lang('REP_PRIMITIVE'),
			id:'primitive',
			renderer:navigate_grid_primitive_renderer,
			hidden:true
		};

		var navigate_search_grid_col_density = {
			dataIndex:'density',
			header:get_ag_lang('REP_DENSITY'),
			id:'density',
			hidden:true
		};

		var navigate_search_grid_fields = [
			{name:'f_id'},
			{name:'b_id'},
			{name:'common_id'},
			{name:'name_j'},
			{name:'name_e'},
			{name:'name_k'},
			{name:'name_l'},
			{name:'syn_j'},
			{name:'syn_e'},
			{name:'organsys_j'},
			{name:'organsys_e'},
			{name:'organsys'},
			{name:'phase'},
			{name:'taid'},
			{name:'icon'},
			{name:'seg_color'},
			{name:'xmin',    type:'float'},
			{name:'xmax',    type:'float'},
			{name:'ymin',    type:'float'},
			{name:'ymax',    type:'float'},
			{name:'zmin',    type:'float'},
			{name:'zmax',    type:'float'},
			{name:'volume',  type:'float'},
			{name:'primitive'},
			{name:'density'},
			{name:'state'},
			{name:'score',  type:'int'},
			{name:'entry',   type:'date', dateFormat: 'timestamp'},
			{name:'lastmod', type:'date', dateFormat: 'timestamp'},
			{name:'delcause'},
			{name:'m_openid'}
		];

		var navigate_search_grid_col_id = {
			dataIndex:'f_id',
			header:get_ag_lang('CDI_NAME'),
			id:'f_id',
			width:72,
			resizable:true,
			fixed:!$moveGridOrder,
			hideable:true
		};
		var navigate_search_grid_col_entry = {
			dataIndex:'entry',
			header:get_ag_lang('GRID_TITLE_MODIFIED'),
			id:'entry',
			renderer:Ext.util.Format.dateRenderer('Y/m/d'),
			hidden:true
		};
		var navigate_search_grid_col_organsys = {
			dataIndex:'organsys',
			header:get_ag_lang('GRID_TITLE_ORGANSYS'),
			id:'organsys',
			hidden:true
		};
		var navigate_search_grid_col_icon = {
			dataIndex:'seg_color',
			header:'',
			id:'seg_color',
			sortable: true,
			hidden:$gridColHiddenID,
			renderer:bp3s_parts_search_gridpanel_exists_parts_renderer,
			width:28,
			resizable:false,
			fixed:true,
			menuDisabled:true,
			hideable: false,
			resizable: false
		};
		var navigate_search_grid_cols = [
			navigate_search_grid_col_icon,
HTML
#print qq|			{dataIndex:'b_id',     header:'',                                id:'b_id',fixed:true,width:20,renderer:bp3s_parts_search_gridpanel_exists_parts_renderer},\n| if($showGridColPartsExists eq 'true');
print <<HTML;
			{dataIndex:'common_id',header:'UniversalID',                     id:'common_id', hidden:true, fixed:$gridColFixedUniversalID},
HTML
print qq|			navigate_search_grid_col_id,\n| if($moveGridOrder ne 'true');
print <<HTML;
			{dataIndex:'name_e',   header:get_ag_lang('DETAIL_TITLE_NAME_E'),    id:'name_e'},
//			{dataIndex:'name_j',   header:get_ag_lang('DETAIL_TITLE_NAME_J'),    id:'name_j', hidden:$gridColHiddenNameJ},
			{dataIndex:'name_j',   header:get_ag_lang('DETAIL_TITLE_NAME_J'),    id:'name_j', hidden:true},
			{dataIndex:'name_k',   header:get_ag_lang('DETAIL_TITLE_NAME_K'),    id:'name_k', hidden:true},
			{dataIndex:'name_l',   header:get_ag_lang('DETAIL_TITLE_NAME_L'),    id:'name_l', hidden:true},
			{dataIndex:'syn_e',    header:get_ag_lang('DETAIL_TITLE_SYNONYM_E'), id:'syn_e', hidden:true},
			{dataIndex:'syn_j',    header:get_ag_lang('DETAIL_TITLE_SYNONYM_J'), id:'syn_j', hidden:true},
HTML
if($moveGridOrder ne 'true'){
	print <<HTML;
			{dataIndex:'phase',    header:get_ag_lang('GRID_TITLE_PHASE'),       id:'phase', hidden:true},
			navigate_search_grid_col_entry,
HTML
}else{
	print <<HTML;
//			navigate_search_grid_col_organsys,
			navigate_search_grid_col_id,
HTML
}
print <<HTML;
			{dataIndex:'xmin',     header:'Xmin(mm)',                        id:'xmin',  hidden:true},
			{dataIndex:'xmax',     header:'Xmax(mm)',                        id:'xmax',  hidden:true},
			{dataIndex:'ymin',     header:'Ymin(mm)',                        id:'ymin',  hidden:true},
			{dataIndex:'ymax',     header:'Ymax(mm)',                        id:'ymax',  hidden:true},
			{dataIndex:'zmin',     header:'Zmin(mm)',                        id:'zmin',  hidden:true},
			{dataIndex:'zmax',     header:'Zmax(mm)',                        id:'zmax',  hidden:true},
			{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',hidden:false},
HTML
if($moveGridOrder ne 'true'){
#	print qq|			{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume', hidden:true},\n| if($removeGridColValume ne 'true');
#	print qq|			navigate_search_grid_col_organsys,\n| if($removeGridColOrganSystem ne 'true');
}else{
	print <<HTML;
			navigate_search_grid_col_entry,
HTML
}
print <<HTML;
			navigate_search_grid_col_density,
			navigate_search_grid_col_primitive,
			{dataIndex:'state',    header:'State',                           id:'state', hidden:true},
			{dataIndex:'taid',     header:'TAID',                            id:'taid', hidden:true},
			{dataIndex:'score',    header:'Score',                           id:'score', width:40, align:'right', resizable:true, hidden:true}
		];

		var tbar_items = [];
/*
		var combo = Ext.getCmp('bp3d-tree-type-combo');
		var value = combo.getValue()
		var type_records = combo.getStore().getRange();
		var radio_name = Ext.id();
		Ext.each(type_records,function(r,i,a){
			var id_isa = Ext.id();
			var div_isa = \$('<div class="bp3d-tree-type-div">').css({margin:'0 2px'});
			\$('<input type="radio" name="'+radio_name+'" id="'+id_isa+'" value="'+r.data.t_type+'" class="bp3d-tree-type-radio-count bp3d-tree-type-radio-count-'+r.data.t_type+'">').css({marginTop:'4px'}).appendTo(div_isa);
			var tbitem_isa = new Ext.Toolbar.Item(div_isa.get(0));
			var tbitem_isa_label = new Ext.Toolbar.Item(\$('<label for="'+id_isa+'">').html(r.data.t_name+'(<label class="bp3d-tree-type-label-count bp3d-tree-type-label-count-'+r.data.t_type+'">-</label>)').appendTo(\$('<span class="ytb-text">')).get(0));

			tbar_items.push(tbitem_isa);
			tbar_items.push(tbitem_isa_label);
		});
*/
		var total_count_pos = tbar_items.length+1;

		var store = new Ext.data.JsonStore({
			url:'get-fma.cgi',
			totalProperty : 'total',
			root: 'records',
			fields: navigate_search_grid_fields,
//			sortInfo: {field: 'name_e', direction: 'ASC'},
			sortInfo: {field: 'volume', direction: 'DESC'},
			remoteSort: true,
			baseParams : {
				parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
				lng    : gParams.lng
			},
			listeners: {
				'beforeload' : function(self,options){
//_dump("beforeload():"+grid_panel.id);
					self.baseParams = self.baseParams || {};
					try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
					self.baseParams.version = bp3d_version;
					delete self.baseParams.t_type;
					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) self.baseParams.t_type = treeType;

					try{
						var tb = grid_panel.getTopToolbar();
						var item = tb.items.get(total_count_pos);
						item.el.innerHTML='<label>-&nbsp;Objs</label>';

						\$(tb.el).find("input.bp3d-tree-type-radio-count[checked]").removeAttr("checked");
						\$(tb.el).find("label.bp3d-tree-type-label-count").text('-');
					}catch(e){
						_dump("load():"+e);
					}

					for(var key in init_bp3d_params){
						if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
					}

					try{
						var store = Ext.getCmp('bp3d-version-combo').getStore();
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
					selectPathCB();

					try{
						var tb = grid_panel.getTopToolbar();
						var item = tb.items.get(total_count_pos);
						item.el.innerHTML='<label>'+self.getTotalCount()+'&nbsp;Objs</label>';

						if(!Ext.isEmpty(self.reader.jsonData.rep_num)){
							try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
							var t_type;
							for(t_type in self.reader.jsonData.rep_num){
								for(var i=0;i<total_count_pos;i+=2){
									if(treeType==t_type){
										var item = tb.items.get(i);
										\$(item.el).find("input.bp3d-tree-type-radio-count-"+t_type).attr({checked:true});
									}
									var item = tb.items.get(i+1);
									\$(item.el).find("label.bp3d-tree-type-label-count-"+t_type).text(self.reader.jsonData.rep_num[t_type]);
								}
								\$('label#navigate-north-panel-content-label-'+t_type).html('(<span>'+self.reader.jsonData.rep_num[t_type]+'</span>)');
							}
						}

					}catch(e){
						_dump("load():"+e);
					}
				},
				scope:this
			}
		});

		var title = 'Search['+aQuery+']';
		if(!Ext.isEmpty(aOptions) && !Ext.isEmpty(aOptions.title)) title = aOptions.title;


		tbar_items.push('->');
		tbar_items.push({xtype: 'tbtext', text: '&nbsp;'});
HTML
if($copyHidden ne 'true'){
	print <<HTML;
		tbar_items.push('-');
		tbar_items.push({
			tooltip   : get_ag_lang('COPY_TITLE'),
			iconCls  : 'pallet_copy',
			listeners : {
				'click': {
					fn:function(button,e){
						copyList(grid_panel);
					},
					scope:this
				}
			}
		});
HTML
}
print <<HTML;


		var grid_panel = new Ext.grid.GridPanel({
			title: title,
			ds: store,
			cm: new Ext.grid.ColumnModel(navigate_search_grid_cols),

			tbar : new Ext.Toolbar(tbar_items),

			bbar : new Ext.PagingToolbar({
				pageSize    : 30,
				store       : store,
				displayInfo : false,
				displayMsg  : '',
				emptyMsg    : '',
				hideMode    : 'offsets',
				hideParent  : true
			}),
			enableColLock: false,
			loadMask: true,
			closable: true,
			plugins: new Ext.grid.GridFilters({
				filters:[
					{type:'boolean', dataIndex:'b_id'},
					{type:'string',  dataIndex:'f_id'},
					{type:'string',  dataIndex:'name_j'},
					{type:'string',  dataIndex:'name_e'},
					{type:'string',  dataIndex:'name_k'},
					{type:'string',  dataIndex:'name_l'},
					{type:'numeric', dataIndex:'phase'},
					{type:'date',    dataIndex:'entry'},
					{type:'numeric', dataIndex:'xmin'},
					{type:'numeric', dataIndex:'xmax'},
					{type:'numeric', dataIndex:'ymin'},
					{type:'numeric', dataIndex:'ymax'},
					{type:'numeric', dataIndex:'zmin'},
					{type:'numeric', dataIndex:'zmax'},
					{type:'numeric', dataIndex:'volume'},
					{type:'string',  dataIndex:'organsys'},
					{type:'string',  dataIndex:'state'},
					{type:'string',  dataIndex:'taid'}
			]}),
			autoScroll:true,
			listeners : {
				"rowclick" : function(grid, rowIndex, event){
//_dump("3261:CALL selectPathCB()");
					selectPathCB();
				},
				"resize" : function(grid){
					resizeGridPanelColumns(grid);
				},
				"render" : function(grid){
					var store = grid.getStore();
					if(Ext.isEmpty(grid.loadMask) || typeof grid.loadMask == 'boolean') grid.loadMask = new Ext.LoadMask(grid.body,{removeMask:false,store:store});
					restoreHiddenGridPanelColumns(grid,'bp3d-navigate-search-grid-panel');

					var cm = grid.getColumnModel();
					cm.defaultSortable = true;
					cm.defaultWidth = 40;
					cm.on({
						'hiddenchange' : function(column,columnIndex,hidden){
							resizeGridPanelColumns(grid);
							saveHiddenGridPanelColumns(grid,'bp3d-navigate-search-grid-panel');
						},
						scope: this,
						delay: 100
					});

					store.baseParams = store.baseParams || {};
					delete store.baseParams.f_pid;

					if(!Ext.isEmpty(aOptions) && !Ext.isEmpty(aOptions.baseParams)){
						for(var key in aOptions.baseParams){
							store.baseParams[key] = aOptions.baseParams[key];
						}
					}else{
						store.baseParams.query = aQuery;
						store.baseParams.node = 'search';
					}
					store.reload({params:{start:0,limit:30}});

					var tb = grid.getTopToolbar();
					try{
						for(var i=0;i<total_count_pos;i+=2){
							var item = tb.items.get(i);
							\$(item.el).find("input.bp3d-tree-type-radio-count").change(function(){
								var combo = Ext.getCmp('bp3d-tree-type-combo');
								var value = Number(\$(this).val());
								var store = combo.getStore();
								var idx = store.findBy(function(r,id){
									return r.get('t_type')===value;
								});
								if(idx<0) return;
								combo.setValue(value);
								var rec = store.getAt(idx);
								combo.fireEvent('select',combo,rec,idx);
							});
						}
					}catch(e){
					}
				},
				beforeshow: function(grid){
					_dump("beforeshow():["+grid.id+"]");
					var store = grid.getStore();
					if(store && store.reader && store.reader.jsonData && !Ext.isEmpty(store.reader.jsonData.rep_num)){
						var t_type;
						for(t_type in store.reader.jsonData.rep_num){
							\$('label#navigate-north-panel-content-label-'+t_type).html('(<span>'+store.reader.jsonData.rep_num[t_type]+'</span>)');
						}
					}
				},
				scope : this
			}
		});

		return grid_panel;
	};

	var navigate_tree_type_store = new Ext.data.JsonStore({
		url:'get-tree_type.cgi',
		totalProperty : 'total',
		root: 'records',
		fields: [
			{name:'bul_id',type:'int'},
			{name:'ci_id',type:'int'},
			'ci_name',
			'cb_name',
			'bul_name',
			'bul_abbr',
			{name:'cb_id',type:'int'},
			{name:'butc_num',type:'int'},

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
				try{self.baseParams.version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){}

				var cmp = Ext.getCmp('bp3d-tree-type-combo');
				if(cmp && cmp.rendered) cmp.disable();
				var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
				if(cmp && cmp.rendered) cmp.disable();

				for(var key in init_bp3d_params){
					if(key.match(/_id\$/)) self.baseParams[key] = init_bp3d_params[key];
				}

				try{
					var store = Ext.getCmp('bp3d-version-combo').getStore();
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
			'load' : function(store,records,options){
				if(records.length<=0) return;
				var index = 0;
				var record = records[index];
				var t_type = Cookies.get('ag_annotation.images.type');
				if(store.baseParams.version){
					var types_str = Cookies.get('ag_annotation.images.types');
//_dump("navigate_tree_type_store.load():types_str=["+types_str+"]");
					if(types_str){
						var types = Ext.util.JSON.decode(types_str);
						if(types[store.baseParams.version]) t_type = types[store.baseParams.version];
					}
				}

				if(t_type){
					var findIndex = store.find('t_type', new RegExp('^'+t_type+'\$'));
					if(findIndex>=0){
						index = findIndex;
						record = store.getAt(index);
					}
				}
				var cmp = Ext.getCmp('bp3d-tree-type-combo');
				if(cmp && cmp.rendered){
					cmp.enable();
					cmp.setValue(record.get('t_type'));
					cmp.fireEvent('select',cmp,record,index);
				}
				var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
				if(cmp && cmp.rendered){
					cmp.enable();
					cmp.setValue(record.get('t_type'));
				}
			},
			scope:this
		}
	});

	var navigate_tree_panel = new Ext.tree.TreePanel({
		title: 'Tree',
HTML
if($useNavigateRange ne 'true'){
	print <<HTML;
		tbar:[
		{
			id    : 'treeType_label',
			xtype : 'tbtext',
			text  : get_ag_lang('TREE_TYPE')+':'
		},
		{
			hidden: true,
			id: 'bp3d-tree-type-combo-old',
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
			store : navigate_tree_type_store,
			listeners: {
				'select': function(combo,record,index){
					var treeCmp = Ext.getCmp('navigate-tree-panel');
					if(!treeCmp || !treeCmp.root) return;

					try{var version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){version = null;}
					if(!version) return;

					Cookies.set('ag_annotation.images.type',combo.getValue());
					var types_str = Cookies.get('ag_annotation.images.types');
					var types;
					if(types_str){
						types = Ext.util.JSON.decode(types_str);
					}else{
						types = {};
					}
					types[version] = combo.getValue();
					Cookies.set('ag_annotation.images.types',Ext.util.JSON.encode(types));

					treeCmp.root.reload(
						function(node){
							if(!Ext.isEmpty(gBP3D_TPAP) && node.firstChild && node.firstChild.attributes.attr.f_id){
								gBP3D_TPAP = undefined;
								Cookies.set('ag_annotation.images.path','/'+node.firstChild.attributes.attr.f_id);
							}
							var path = Cookies.get('ag_annotation.images.path','');
							node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',function(bSuccess,oSelNode){
								if(bSuccess){
									selectPathCB(bSuccess,oSelNode);
								}else if(node.firstChild){
									Cookies.set('ag_annotation.images.path','/'+node.firstChild.attributes.attr.f_id);
									var path = Cookies.get('ag_annotation.images.path','');
									node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
								}
							});
						}
					);
					var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
					if(cmp && cmp.rendered){
						cmp.setValue(record.data.t_type);
					}
				},
				'render': function(combo){
				},
				scope:this
			}
		}],
HTML
}
print <<HTML;
		id              : 'navigate-tree-panel',
		autoScroll      : true,
		animate         : true,
		lines           : true,
		rootVisible     : $rootVisible,
		rootVisible     : true,
		monitorResize   : true,
//		enableDD        : $enableDD,
//		ddScroll        : true,

		ddGroup  : 'partlistDD',
		ddScroll : false,
		enableDD : false,
		enableDrag : true,
		enableDrop : false,


		containerScroll : true,
		useArrows       : false,
		root : new Ext.tree.AsyncTreeNode({
//			text      : get_ag_lang('TREE_ROOT_TITLE'),
			text      : '/',
			draggable : false,
			id        : 'root',
			f_id      : 'root',
			expanded  : true,
			iconCls   : "ttopfolder"
		}),
		loader : new Ext.tree.TreeLoader({
			dataUrl : 'get-tree.cgi',
			baseParams : {
				parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
				lng    : gParams.lng,
				trash  : true
			},
			listeners : {
				'beforeload' : function(loader,node){
					loader.baseParams = loader.baseParams || {};
					delete loader.baseParams.pid;
					delete loader.baseParams.f_id;
					delete loader.baseParams.f_pid;
					delete loader.baseParams.treeType;
					delete loader.baseParams.tg_id;
					delete loader.baseParams.tgi_id;
					delete loader.baseParams.bp3d_version;

					if(node.attributes.attr){
						if(!Ext.isEmpty(node.attributes.attr.f_id)) loader.baseParams.f_pid = node.attributes.attr.f_id;
						if(!Ext.isEmpty(node.attributes.attr.t_type)){
							loader.baseParams.t_type = node.attributes.attr.t_type;
						}else{
							try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
							if(!Ext.isEmpty(treeType)) loader.baseParams.t_type = treeType;
						}
					}else if(node.id == 'root'){
						try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
						if(!Ext.isEmpty(treeType)) loader.baseParams.t_type = treeType;
					}

					try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
					loader.baseParams.version = bp3d_version;

					if(node.id=='root'){
						var bul_name = Cookies.get('ag_annotation.images.bul_name');
						var butc_num = Cookies.get('ag_annotation.images.butc_num');
						if(bul_name && butc_num){
							bul_name += ' ('+butc_num+')';
						}else{
							bul_name = '/';
						}
						node.setText(bul_name);
					}

					for(var key in init_bp3d_params){
						if(key.match(/_id\$/)) loader.baseParams[key] = init_bp3d_params[key];
					}

					try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
					if(!Ext.isEmpty(treeType)) init_bp3d_params.bul_id = init_bp3d_params.t_type = loader.baseParams.bul_id = loader.baseParams.t_type = treeType;

					try{
						var store = Ext.getCmp('bp3d-version-combo').getStore();
						var idx = store.findBy(function(record,id){
							if(record.data.tgi_version==loader.baseParams.version) return true;
						});
						if(idx>=0){
							var record = store.getAt(idx);
							if(record){
								loader.baseParams.md_id = record.data.md_id;
								loader.baseParams.mv_id = record.data.mv_id;
								loader.baseParams.mr_id = record.data.mr_id;
								loader.baseParams.ci_id = record.data.ci_id;
								loader.baseParams.cb_id = record.data.cb_id;
							}
						}
					}catch(e){}

				},
				'load' : function(loader,node,response){
//					console.log(node);
//					if(node.id=='root'){
//						var combo = Ext.getCmp('bp3d-tree-type-combo');
//						node.setText();
//					}


//2011-09-28 追加
					var viewport = Ext.getCmp('viewport');
					if(node.getDepth()>0 && viewport && viewport.loadMask){
						try{
							viewport.loadMask.hide();
							delete viewport.loadMask;
HTML
if(defined $open_tab_bodyparts_panel || defined $load_session){
	print <<HTML;
							var contents_tabs = Ext.getCmp('contents-tab-panel');
							if(contents_tabs) contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
HTML
}
print <<HTML;
						}catch(e){}
					}
				},
				'loadexception': function(){
//2011-09-28 追加
					try{
						var viewport = Ext.getCmp('viewport');
						if(viewport && viewport.loadMask){
							viewport.loadMask.hide();
							delete viewport.loadMask;
HTML
if(defined $open_tab_bodyparts_panel || defined $load_session){
	print <<HTML;
							var contents_tabs = Ext.getCmp('contents-tab-panel');
							if(contents_tabs) contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
HTML
}
print <<HTML;
						}
					}catch(e){}
				},
				scope : this
			}
		}),
		listeners : {
			"click" : {
				fn : function(node, event){
					if(gParams.id != undefined) delete gParams.id;
//_dump("3421:CALL selectPathCB()");
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
			"render" : {
				fn:function(tree,parent,node){
//					_dump("render():["+tree.id+"]");
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
										var path = Cookies.get('ag_annotation.images.path','');
										node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id');
									}
								);
							}
						);
					}
				},scope : this}
		}
	});
HTML
if($useNavigateRange eq 'true'){
	print <<HTML;

	var get_ajax_zrange_object_transactionId;
	var get_ajax_zrange_object_lastParams;
	var get_ajax_zrange_object = new Ext.util.DelayedTask(function(params){

		params = params || {};
		params.t_type = Ext.getCmp('bp3d-tree-type-combo').getValue();
		params.version = Ext.getCmp('bp3d-version-combo').getValue();

		if(Ext.isEmpty(params.t_type) || Ext.isEmpty(params.version)) return;

		for(var key in init_bp3d_params){
			if(key.match(/_id\$/)) params[key] = init_bp3d_params[key];
		}

		try{
			var store = Ext.getCmp('bp3d-version-combo').getStore();
			var idx = store.findBy(function(record,id){
				if(record.data.tgi_version==params.version) return true;
			});
			if(idx>=0){
				var record = store.getAt(idx);
				if(record){
					params.md_id = record.data.md_id;
					params.mv_id = record.data.mv_id;
					params.mr_id = record.data.mr_id;
					params.ci_id = record.data.ci_id;
					params.cb_id = record.data.cb_id;
				}
			}
		}catch(e){}

		var encode_params = Ext.urlEncode(params);
		get_ajax_zrange_object_lastParams = encode_params;
		if(get_ajax_zrange_object_transactionId){
			if(Ext.Ajax.isLoading(get_ajax_zrange_object_transactionId)) Ext.Ajax.abort(get_ajax_zrange_object_transactionId);
		}
		Ext.Ajax.timeout = 60000*5;
		get_ajax_zrange_object_transactionId = Ext.Ajax.request({
			url     : 'get-zrange-object.cgi',
			method  : 'POST',
			params  : encode_params,
			success : function(conn,response,options){
				try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
				if(results && results.success){

					if(params && params.cb) (params.cb)(results);

					if(!Ext.isEmpty(gParams.fmaid)){
						results.records = [gParams.fmaid];
						results.total = 1;
						delete gParams.fmaid;
					}

					if(results.other){
						for(bul_id in results.other){
							\$('label#navigate-north-panel-content-label-'+bul_id).html('(<span>'+results.other[bul_id].total+'</span>)');
						}
						\$('label#navigate-north-panel-content-label-'+params.t_type).html('(<span>'+results.total+'</span>)');
					}

					if(results.total==0){
						bp3d_contents_store.removeAll();
						return;
					}

					var load_params = {};
					for(var key in bp3d_contents_store.baseParams){
						load_params[key] = bp3d_contents_store.baseParams[key];
					}
					for(var key in params){
						load_params[key] = params[key];
					}
					load_params.fma_ids = Ext.util.JSON.encode(results.records);
					bp3d_change_location(Ext.urlEncode({params:Ext.urlEncode(load_params)}),true);
				}
			},
			failure : function(conn,response,options){
				_dump("failure():["+conn.tId+"]");

				var viewImages = getViewImages();
				if(viewImages && viewImages.refresh){
					viewImages.getStore().removeAll();
					viewImages.refresh();
				}
			}
		});
		var viewImages = getViewImages();
		if(viewImages && viewImages.onBeforeLoad) viewImages.onBeforeLoad();
	});

	var get_ajax_zrange_object_position_task = new Ext.util.DelayedTask(function(){
//_dump("get_ajax_zrange_object_position_task()");
		zpositionCmp = Ext.getCmp('navigate-position-panel-zposition-numberfield');
		if(zpositionCmp.isValid(true)){
			var params = {};
			for(var key in bp3d_contents_store.baseParams){
				params[key] = bp3d_contents_store.baseParams[key];
			}
			delete params.zmin;
			delete params.zmax;
			delete params.only_ta;

			params.zrange = Ext.getCmp('navigate-position-panel-range-combobox').getValue();
			params.filter = Ext.getCmp('navigate-position-panel-filter-combobox').getValue();
			params.cvmin = Ext.getCmp('navigate-position-panel-cube-volume-zmin-numberfield').getValue();
			params.cvmax = Ext.getCmp('navigate-position-panel-cube-volume-zmax-numberfield').getValue();
			params.zposition = zpositionCmp.getValue();

			params.zrate = Ext.getCmp('navigate-position-panel-zrate-numberfield').getValue();

			params.density_min = Ext.getCmp('navigate-position-panel-density-min-numberfield').getValue();
			params.density_max = Ext.getCmp('navigate-position-panel-density-max-numberfield').getValue();
			params.primitive = Ext.getCmp('navigate-position-panel-density-primitive-checkbox').getValue();

			if(\$("input#navigate-position-panel-only-taid:checked").val()) params.only_ta = true;

//			get_ajax_zrange_object(params);
			get_ajax_zrange_object.cancel();
			get_ajax_zrange_object.delay(250,null,null,[params]);
		}
	});

	var get_ajax_zrange_object_range_params = function(){
		var params = Ext.apply({},bp3d_contents_store.baseParams);
		delete params.zposition;
		delete params.zrange;
		delete params.only_ta;

		params.filter = Ext.getCmp('navigate-range-panel-filter-combobox').getValue();
		params.cvmin = Ext.getCmp('navigate-range-panel-cube-volume-min-numberfield').getValue();
		params.cvmax = Ext.getCmp('navigate-range-panel-cube-volume-max-numberfield').getValue();
		params.zmin = Ext.getCmp('navigate-range-panel-zmin-numberfield').getValue();
		params.zmax = Ext.getCmp('navigate-range-panel-zmax-numberfield').getValue();

		params.density_min = Ext.getCmp('navigate-range-panel-density-min-numberfield').getValue();
		params.density_max = Ext.getCmp('navigate-range-panel-density-max-numberfield').getValue();
		params.primitive = Ext.getCmp('navigate-range-panel-density-primitive-checkbox').getValue();

		if(\$("input#navigate-range-panel-only-taid:checked").val()) params.only_ta = true;

		for(var key in params){
			if(Ext.isEmpty(params[key])) params[key] = null;
		}
		params.cb = function(results){
//			_dump("get_ajax_zrange_object_range_params:CB()");
			var sel_value;
			if(!Ext.isEmpty(results.segments)){

				var range_value=null;
				var cube_value=null;

				var combo = Ext.getCmp('navigate-range-panel-range-combobox');
				if(!Ext.isEmpty(combo)) range_value = combo.getValue();
//				_dump("get_ajax_zrange_object_range_params():range_value=["+range_value+"]");

				var combo = Ext.getCmp('navigate-range-panel-cube-volume-combobox');
				if(!Ext.isEmpty(combo)) cube_value = combo.getValue();
//				_dump("get_ajax_zrange_object_range_params():cube_value=["+cube_value+"]");

				Ext.each(results.segments,function(r,i,a){
					\$('#navigate-range-panel-event-'+r.value+'>.navigate-range-panel-value').text(r.total);

					if(!Ext.isEmpty(r.totals)){
						Ext.each(r.totals,function(r2,i,a){

//							_dump("get_ajax_zrange_object_range_params():CB():r2=["+r2.cuboid_value+"]["+r2.segment_value+"]");

							\$('td.range_segment_'+r2.cuboid_value+' div.range_segment_'+r2.segment_value).text(r2.total).attr({
								cuboid_value: r2.cuboid_value,
								segment_value: r2.segment_value
							});
//							if(r2.total>0 && navigate_range_panel_init_show){//結果が０でも良い場合は、コメントにする
//							if(r2.cuboid_value=='100-inf' && r2.segment_value=='H' && navigate_range_panel_init_show){//結果が０でも良い場合は、コメントにする
							if(r2.total>0 && r2.cuboid_value=='100-inf' && navigate_range_panel_init_show){//結果が０でも良い場合は、コメントにする
								if(Ext.isEmpty(sel_value)){
									sel_value = {cuboid_value: r2.cuboid_value, segment_value: r2.segment_value};
								}else if(r2.cuboid_value==cube_value && r2.segment_value==range_value){
									sel_value = {cuboid_value: r2.cuboid_value, segment_value: r2.segment_value};
								}
							}
						});
					}

				});
				navigate_range_panel_init_show = 0;
			}
			if(Ext.isEmpty(gParams.fmaid)){
				if(!Ext.isEmpty(sel_value)){
					var combo = Ext.getCmp('navigate-range-panel-cube-volume-combobox');
					var store = combo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==sel_value.cuboid_value) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						combo.setValue(rec.data.value);
						combo.fireEvent('select',combo,rec,idx);
//						_dump("CB():CALL get_ajax_zrange_object_range_task()");
						get_ajax_zrange_object_range_task.cancel();
					}
					var combo = Ext.getCmp('navigate-range-panel-range-combobox');
					var store = combo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==sel_value.segment_value) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						combo.setValue(rec.data.value);
						combo.fireEvent('select',combo,rec,idx);
						get_ajax_zrange_object_range_task.cancel();
					}
					get_ajax_zrange_object_range_task.delay(0);
				}else{
					var cuboid_value = Ext.getCmp('navigate-range-panel-cube-volume-combobox').getValue();
					var segment_value = Ext.getCmp('navigate-range-panel-range-combobox').getValue();
					if(\$('table.range_segment_'+cuboid_value+'.range_segment_area_'+segment_value).addClass('range_select').length==0){
						if(\$('td.range_segment_'+cuboid_value+' div.range_segment_area_'+segment_value).addClass('range_select').length==0){
							\$('td.range_segment_'+cuboid_value+' div.range_segment_'+segment_value).addClass('range_select');
						}
					}
				}
				Ext.getCmp('navigate-range-panel-num-numberfield').setValue(Ext.isEmpty(results.records)?0:results.records.length);
			}
		};
		return params;
	};

	var get_ajax_zrange_object_range_task = new Ext.util.DelayedTask(function(){
//_dump("get_ajax_zrange_object_range_task()");
		var params = get_ajax_zrange_object_range_params();
//		get_ajax_zrange_object(params);
		get_ajax_zrange_object.cancel();
		get_ajax_zrange_object.delay(250,null,null,[params]);
	});

	var get_ajax_zrange_object_range_task2 = get_ajax_zrange_object_range_task;
	var get_ajax_zrange_object_range_task3 = new Ext.util.DelayedTask(function(){
//_dump("get_ajax_zrange_object_range_task3()");
		var params = get_ajax_zrange_object_range_params();

		var disp = Ext.getCmp('navigate-range-panel-filter-combobox').getRawValue();
		\$('td.range_show_only_image').removeClass('range_select');
		\$('td.range_show_only_image_'+disp).addClass('range_select');




		var segments = [];
		var cuboid_volumes  = [];
		var combo = Ext.getCmp('navigate-range-panel-range-combobox');
		Ext.each(combo.getStore().getRange(),function(r,i,a){
			var o = Ext.apply({},r.data);
			segments.push(o);
		});
		params.segments = Ext.encode(segments);

		var combo = Ext.getCmp('navigate-range-panel-cube-volume-combobox');
		Ext.each(combo.getStore().getRange(),function(r,i,a){
//			if(Ext.isEmpty(r.data.min) && Ext.isEmpty(r.data.max)) return true;
			var o = Ext.apply({},r.data);
			cuboid_volumes.push(o);
		});
		params.cuboid_volumes = Ext.encode(cuboid_volumes);

//		get_ajax_zrange_object(params);
		get_ajax_zrange_object.cancel();
		get_ajax_zrange_object.delay(250,null,null,[params]);

//		\$('td.range_segment div.range_value').text('-').removeAttr('cuboid_value').removeAttr('segment_value');
		\$('td.range_segment div.range_value').html('<img src="resources/images/default/tree/loading.gif" style="width:12px;height:12px;border-width:0;margin-top:16px;">').removeAttr('cuboid_value').removeAttr('segment_value');
});

	var navigate_position_panel = new Ext.Panel({
		title: 'Intersection',
		id: 'navigate-position-panel',
		autoScroll: true,
		layout: 'form',
		labelWidth: 90,
		labelAlign: 'right',
		defaultType: 'numberfield',
		defaults : {
			hidden: true,
			hideLabel: true,
			allowBlank: false,
			readOnly: true,
			selectOnFocus: true
		},
		items : [{
			hidden: false,
			xtype: 'panel',
			border: false,
			contentEl: 'navigate-position-panel-content',
//			height: 743
//			height: 771
			height: 787
		},{
			hidden: true,
			hideLabel: true,
			id: 'navigate-position-panel-density-combobox',
			xtype: 'combo',
			ctCls : 'x-hide-display',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
			value: 'any',
			readOnly: false,
			width: 106,
			listWidth: 120,
			store: new Ext.data.SimpleStore({
				fields: ['disp','value','min','max'],
				data : [
					['Any'                     ,'any'      ,null,null],
					[get_ag_lang('ELEMENT_PRIMARY'),'primitive',null,null],
					['100%'                    ,'100-inf'  ,1.0 ,null],
					['80%-'                    ,'80-inf'   ,0.8 ,null],
					['-30%'                    ,'inf-30'   ,null,0.3]
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]["+combo.getValue()+"]");

					Ext.getCmp('navigate-position-panel-density-max-numberfield').setValue(record.data.max);
					Ext.getCmp('navigate-position-panel-density-min-numberfield').setValue(record.data.min);
					Ext.getCmp('navigate-position-panel-density-primitive-checkbox').setValue(record.data.value==='primitive');

					get_ajax_zrange_object_position_task.delay(0);
				},
				'render' : function(combo) {
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: 'Density Max(%)',
			id : 'navigate-position-panel-density-max-numberfield',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: 'Density Min(%)',
			id : 'navigate-position-panel-density-min-numberfield',
			readOnly: false,
			value: 0,
			listeners: {
				change: function(field, newValue, oldValue){
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			fieldLabel: '',
			id : 'navigate-position-panel-density-primitive-checkbox',
			xtype: 'checkbox',
			readOnly: false,
			checked: true,
			listeners: {
				change: function(field, newValue, oldValue){
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			xtype: 'combo',
			fieldLabel: 'Range',
			id : 'navigate-position-panel-range-combobox',
			renderTo:'navigate-position-panel-range-combobox-render',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
			value: 5,
			readOnly: false,
			store: new Ext.data.SimpleStore({
				fields: ['value','disp'],
				data : [
					[5,  '5mm'],
					[10, '10mm'],
					[15, '15mm']
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
					get_ajax_zrange_object_position_task.delay(0);
				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
					combo.hide();
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			fieldLabel: 'ZMax',
			id : 'navigate-position-panel-zmax-numberfield',
			renderTo:'navigate-position-panel-zmax-numberfield-render',
			value: 1670.79,
			listeners: {
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			fieldLabel: 'ZMin',
			id : 'navigate-position-panel-zmin-numberfield',
			renderTo:'navigate-position-panel-zmin-numberfield-render',
			value: -13.53,
			listeners: {
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			fieldLabel: 'Show only',
			id: 'navigate-position-panel-filter-combobox',
			renderTo:'navigate-position-panel-filter-combobox-render',
			xtype: 'combo',
//			ctCls : 'x-small-editor',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
			value: 'FMA5018',
			readOnly: false,
			width: 114,
			store: new Ext.data.SimpleStore({
				fields: ['value','disp'],
				data : [
					['other.obo','Internal'],
					['FMA5018',  'Bone'],
					['FMA5022',  'Muscle'],
					['FMA3710',  'Vessel'],
					['',         'All']
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
					get_ajax_zrange_object_position_task.delay(0);

//					\$('table.position_value').removeClass('position_select');
//					\$('td.position_segment div.position_segment_area').removeClass('position_select');
//					\$('td.position_segment div.position_value').removeClass('position_select');

					var disp = combo.getRawValue();
					\$('td.position_show_only_image').removeClass('position_select');
					\$('td.position_show_only_image_'+disp).addClass('position_select');

				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
//					combo.hide();

//					_dump("render():["+combo.id+"]["+disp+"]");
					var disp = 'Bone';
					\$('td.position_show_only_image_'+disp).addClass('position_select');
//					_dump("render():["+combo.id+"]["+disp+"]");

				},
				scope:this
			}
		},{
			hidden:true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			fieldLabel: 'Cuboid&nbsp;Vol(cc)',
			id: 'navigate-position-panel-cube-volume-combobox',
			renderTo:'navigate-position-panel-cube-volume-combobox-render',
			xtype: 'combo',
//			ctCls : 'x-small-editor',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
			value: 'any',
			readOnly: false,
			width: 114,
			store: new Ext.data.SimpleStore({
				fields: ['disp','value','min','max'],
				data : [
					['1未満'       ,'<1'   ,null,   1],
					['1以上100未満','<100' ,   1, 100],
					['100以上'     ,'>=100', 100,null],
					['Any'         ,'any'  ,null,null]
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
					Ext.getCmp('navigate-position-panel-cube-volume-zmax-numberfield').setValue(record.data.max);
					Ext.getCmp('navigate-position-panel-cube-volume-zmin-numberfield').setValue(record.data.min);

					get_ajax_zrange_object_position_task.delay(0);
				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: '<span style="font-size:8px;">VolMax(cc)</span>',
			id : 'navigate-position-panel-cube-volume-zmax-numberfield',
			renderTo:'navigate-position-panel-cube-volume-zmax-numberfield-render',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: '<span style="font-size:8px;">VolMin(cc)</span>',
			id : 'navigate-position-panel-cube-volume-zmin-numberfield',
			renderTo:'navigate-position-panel-cube-volume-zmin-numberfield-render',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden:true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			id : 'navigate-position-panel-zrate-numberfield',
			maxValue: 1,
			minValue: 0,
			value: 0.09,
			readOnly: false
		},{
			hidden:true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			fieldLabel: 'Z-center(mm)',
			id : 'navigate-position-panel-zposition-numberfield',
			renderTo:'navigate-position-panel-zposition-numberfield-render',
			maxValue: 1670.79,
			minValue: -13.53,
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
//					_dump("change():["+field.id+"]["+newValue+"]["+oldValue+"]");
//					_dump("change():["+Ext.getCmp('navigate-position-panel-range-combobox').getValue()+"]");

					get_ajax_zrange_object_position_task.delay(0);

					if(oldValue === undefined) return;

					var base = \$('#navigate-position-panel-base');
					var img = \$('#navigate-position-panel-img');
					var line = \$('#navigate-position-panel-line');
					var b_offset = base.offset();
					var i_offset = img.offset();
					var zmax = Ext.getCmp('navigate-position-panel-zmax-numberfield').getValue();
					var zmin = Ext.getCmp('navigate-position-panel-zmin-numberfield').getValue();
					var zrange = zmax-zmin;
					var zrate = (zmax - newValue) / zrange;
					var y = zrate * img.height();
					var top = (y+(i_offset.top-b_offset.top))+'px';
					if(line.css('top') != top){
						\$('#navigate-position-panel-line').css({
							display: 'block',
							top: top
						});
					}
				},
				valid: function(field){
//					_dump("valid():["+field.id+"]");
				},
				specialkey: function(field, e){
					if(e.getKey() != e.ENTER) return;
					Ext.getCmp('navigate-position-panel-range-combobox').focus(false);
					field.focus();
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden:true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			id:'navigate-position-panel-range-label',
			renderTo:'navigate-position-panel-range-label-render',
			xtype: 'label',
			width: '100%',
			style: 'font-size:0.8em;text-align:center;',
			html: '<table width=100%><tbody><tr><td align="center">(range=+2.5mm)</td></tr></tbody></table>'
		}],
		listeners: {
			render: function(comp){
//				_dump("render():["+comp.id+"]");

				Ext.get('navigate-position-panel-event').unselectable();
				Ext.get('navigate-position-panel-base-fx').unselectable();
				Ext.get('navigate-position-panel-base').unselectable();
				Ext.get('navigate-position-panel-img').unselectable();
				Ext.get('navigate-position-panel-img2').unselectable();
				Ext.get('navigate-position-panel-line').unselectable();

				Ext.get('navigate-position-panel-head-disable').unselectable();
				Ext.get('navigate-position-panel-tail-disable').unselectable();


				\$('table.navigate_position_panel_density label').each(function(){
					Ext.get(this).unselectable();
				});
				\$('table.navigate_position_panel_density_item input[type="radio"]').bind('change',function(event){

					\$('table.navigate_position_panel_density_item').removeClass('select_item');
					\$(this).closest('table.navigate_position_panel_density_item').addClass('select_item');

					var val = \$(this).val();
					var densityCombo = Ext.getCmp('navigate-position-panel-density-combobox');
					var store = densityCombo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==val) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						densityCombo.setValue(val);
						densityCombo.fireEvent('select',densityCombo,rec,idx);
					}
				});
				\$('table.navigate_position_panel_density_item input[type="checkbox"]').bind('change',function(event){

					if(get_ajax_zrange_object_transactionId){
						if(Ext.Ajax.isLoading(get_ajax_zrange_object_transactionId)){
							Ext.Ajax.abort(get_ajax_zrange_object_transactionId);
							get_ajax_zrange_object_transactionId = null;
						}
					}

					var minValue = null;
					var maxValue = null;
					var checkValue = false;

					var \$c1 = \$('table.navigate_position_panel_density_item input#navigate-position-panel-density-checkbox-name-element[type="checkbox"]:checked');
					var \$c2 = \$('table.navigate_position_panel_density_item input#navigate-position-panel-density-checkbox-name-complete-compound[type="checkbox"]:checked');
					var \$c3 = \$('table.navigate_position_panel_density_item input#navigate-position-panel-density-checkbox-name-incomplete-compound[type="checkbox"]:checked');

					if(\$c1.length) checkValue = true;
					if(\$c2.length && \$c3.length){
						minValue = 0;
						maxValue = null;
					}else if(\$c2.length){
						minValue = 1.0;
						maxValue = null;
					}else if(\$c3.length){
						minValue = 0;
						maxValue = 1.0;
					}
					if(!checkValue && minValue==null && maxValue==null){
						checkValue = true;
						minValue = 0;
					}

					Ext.getCmp('navigate-position-panel-density-max-numberfield').setValue(maxValue);
					Ext.getCmp('navigate-position-panel-density-min-numberfield').setValue(minValue);
					Ext.getCmp('navigate-position-panel-density-primitive-checkbox').setValue(checkValue);

					get_ajax_zrange_object_position_task.delay(0);

				});



				var combobox = Ext.getCmp('navigate-position-panel-filter-combobox');
//				_dump("render():["+comp.id+"]["+combobox.id+"]["+combobox.rendered+"]");

				var disp = combobox.getRawValue();
				\$('td.position_show_only_image_'+disp).addClass('position_select');

//				_dump("render():["+comp.id+"]["+disp+"]");

				\$('td.position_show_only_image').bind('click',function(event){
					\$('td.position_show_only_image').removeClass('position_select');
					var value;
					if(\$(this).hasClass('position_show_only_image_Bone')){
						value = 'Bone';
					}else if(\$(this).hasClass('position_show_only_image_Muscle')){
						value = 'Muscle';
					}else if(\$(this).hasClass('position_show_only_image_Vessel')){
						value = 'Vessel';
					}else if(\$(this).hasClass('position_show_only_image_Internal')){
						value = 'Internal';
					}else if(\$(this).hasClass('position_show_only_image_All')){
						value = 'All';
					}
					if(!Ext.isEmpty(value)){
						var combo = Ext.getCmp('navigate-position-panel-filter-combobox');
						var store = combo.getStore();
						var idx = store.findBy(function(record,id){
							if(record.data.disp==value) return true;
							return false;
						});
						var rec;
						if(idx>=0) rec = store.getAt(idx);
						if(rec){
							combo.setValue(rec.data.value);
							combo.fireEvent('select',combo,rec,idx);
						}
					}
					event.preventDefault();
					event.stopPropagation();
					return false;
				});


			},
			resize: function(comp, adjWidth, adjHeight, rawWidth, rawHeight){
//				_dump("resize():["+comp.id+"]["+adjWidth+"]["+adjHeight+"]["+rawWidth+"]["+rawHeight+"]");
				var img = \$('#navigate-position-panel-img');
				var node = img.get(0);

				var base = \$('#navigate-position-panel-base');
				\$('#navigate-position-panel-line').css({width : base.width()});
				\$('#navigate-position-panel-head-disable').css({width : base.width()});
				\$('#navigate-position-panel-tail-disable').css({width : base.width()});

				var b_position = base.position();

				\$('#navigate-position-panel-event').css({
					left   : b_position.left,
					top    : b_position.top,
					width  : base.outerWidth({margin:true}),
					height : base.innerHeight()
				});
			},
			show: {
				fn: function(comp){
					function move_zpos(event,p_zpos){
						if(event){
							event.preventDefault();
							event.stopPropagation();
						}
						var base = \$('#navigate-position-panel-base');
						var img = \$('#navigate-position-panel-img');
						var line = \$('#navigate-position-panel-line');

						var head_disable = \$('#navigate-position-panel-head-disable');
						var tail_disable = \$('#navigate-position-panel-tail-disable');

						var b_offset = base.offset();
						var b_position = base.position();
						var i_offset = img.offset();
	//					var x = event.pageX-i_offset.left;
						var y;
						if(Ext.isEmpty(p_zpos)){
							y = event.pageY-i_offset.top-1;
						}else{
							y = p_zpos;
						}
	//					_dump("move_zpos():y=["+y+"]");
						if(y<0) y = 0;
						if(y>img.height()) y = img.height();
	//					_dump("move_zpos():y=["+y+"]");
						var zrate = y/img.height();
	//					_dump("move_zpos():zrate=["+zrate+"]");
						var zmax = Ext.getCmp('navigate-position-panel-zmax-numberfield').getValue();
						var zmin = Ext.getCmp('navigate-position-panel-zmin-numberfield').getValue();
						var zrange = zmax-zmin;
						var zpos = Math.round((zmax-zrange*zrate)*100)/100;
						var field = Ext.getCmp('navigate-position-panel-zposition-numberfield');
						if(zpos != field.getValue()){
							field.setValue(zpos);
						}

						var field_zrate = Ext.getCmp('navigate-position-panel-zrate-numberfield');
						field_zrate.setValue(zrate);

						var top = (y+(i_offset.top-b_offset.top)+b_position.top+4)-(line.height()/2);//+'px';
	//					_dump("move_zpos():top=["+top+"]["+parseInt(line.css('top'))+"]");
						if(parseInt(line.css('top')) != top){
							line.css({
								display: 'block',
								top: top
							});
							head_disable.css({
								display: 'block',
								height: top
							});
							tail_disable.css({
								display: 'block',
								top: top+line.height()+1
							});
						}
					}
					\$('#navigate-position-panel-event').mousedown(function(event,p_zpos){
	//					_dump('mousedown');
						move_zpos(event,p_zpos);
						\$(this).mousemove(function(event,p_zpos){
	//						_dump('mousemove');
							move_zpos(event,p_zpos);
							return false;
						}).mouseup(function(event,p_zpos){
	//						_dump('mouseup');
							move_zpos(event,p_zpos);

							get_ajax_zrange_object_position_task.delay(0);

							\$(this).unbind('mousemove').unbind('mouseup');
							return false;
						});
						return false;
					}).css({
						'cursor':'pointer'
					});
					\$("input#navigate-position-panel-only-taid").change(function(){
						get_ajax_zrange_object_position_task.delay(0);
					});


					setTimeout(function(){
						\$('#navigate-position-panel-event')
							.trigger('mousedown',[48])
							.trigger('mousemove',[48])
							.trigger('mouseup',[48]);
					},250);

					if(_location.location.href == 'about:blank') _location.location.href = 'location.html';
				},
				single: true
			}
		}
	});

	var navigate_range_panel_items = [{
			xtype: 'panel',
			border: false,
			contentEl: 'navigate-range-panel-content',
			anchor: '100%',
//			height:458
//			height:376
//			height:Ext.isIE ? 450 : 448
//			height:Ext.isIE ? 472 : 474
			height: 486
		},{
			hidden: true,
			hideLabel: true,
//			fieldLabel: '表現密度(%)',
			fieldLabel: get_ag_lang('REP_DENSITY')+'(%)',
			labelStyle: 'white-space:nowrap;',
			id: 'navigate-range-panel-density-combobox',
			xtype: 'combo',
			ctCls : 'x-hide-display',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
			value: 'any',
			readOnly: false,
			width: 106,
			listWidth: 120,
			store: new Ext.data.SimpleStore({
				fields: ['disp','value','min','max'],
				data : [
/*
					['<10'   ,'inf-10' ,null, 0.1],
					['10-20' ,'10-20'  , 0.1, 0.2],
					['20-30' ,'20-30'  , 0.2, 0.3],
					['30-40' ,'30-40'  , 0.3, 0.4],
					['40-50' ,'40-50'  , 0.4, 0.5],
					['50-60' ,'50-60'  , 0.5, 0.6],
					['60-70' ,'60-70'  , 0.6, 0.7],
					['70-80' ,'70-80'  , 0.7, 0.8],
					['80-90' ,'80-90'  , 0.8, 0.9],
					['90-100','90-100' , 0.9, 1.0],
					['100'   ,'100-inf', 1.0,null],
					['Any'   ,'any'    ,null,null]
*/
/*
					['10%'+get_ag_lang('OR_MODE'),'10-inf' , 0.1,null],
					['20%'+get_ag_lang('OR_MODE'),'20-inf' , 0.2,null],
					['30%'+get_ag_lang('OR_MODE'),'30-inf' , 0.3,null],
					['40%'+get_ag_lang('OR_MODE'),'40-inf' , 0.4,null],
					['50%'+get_ag_lang('OR_MODE'),'50-inf' , 0.5,null],
					['60%'+get_ag_lang('OR_MODE'),'60-inf' , 0.6,null],
					['70%'+get_ag_lang('OR_MODE'),'70-inf' , 0.7,null],
					['80%'+get_ag_lang('OR_MODE'),'80-inf' , 0.8,null],
					['90%'+get_ag_lang('OR_MODE'),'90-inf' , 0.9,null],
					['100%'   ,'100-inf', 1.0,null],
					[get_ag_lang('ELEMENT_PRIMARY'),'primitive', null,null],
					['Any'    ,'any'    ,null,null]
*/
					['Any'                     ,'any'      ,null,null],
					[get_ag_lang('ELEMENT_PRIMARY'),'primitive',null,null],
					['100%'                    ,'100-inf'  ,1.0 ,null],
					['80%-'                    ,'80-inf'   ,0.8 ,null],
					['-30%'                    ,'inf-30'   ,null,0.3]
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
					Ext.getCmp('navigate-range-panel-density-max-numberfield').setValue(record.data.max);
					Ext.getCmp('navigate-range-panel-density-min-numberfield').setValue(record.data.min);
					Ext.getCmp('navigate-range-panel-density-primitive-checkbox').setValue(record.data.value==='primitive');

//					_dump("select():["+combo.id+"]:CALL get_ajax_zrange_object_range_task3()");
//					get_ajax_zrange_object_range_task3.delay(250);
					get_ajax_zrange_object_range_task3.delay(0);

					\$('table.range_value').removeClass('range_select');
					\$('td.range_segment div.range_segment_area').removeClass('range_select');
					\$('td.range_segment div.range_value').removeClass('range_select');
				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
					try{
						var treetypeCombo = Ext.getCmp('bp3d-tree-type-combo');
						treetypeCombo.on('select',function(combo,record,index){

							var activeTab = Ext.getCmp('navigate-tab-panel').getActiveTab();
							if(activeTab.id != 'navigate-range-panel') return;

							var densityCombo = Ext.getCmp('navigate-range-panel-density-combobox');
							densityCombo.setDisabled(combo.getValue()===1);
							if(densityCombo.disabled){
//								var val = 'any';
								var val = 'primitive';
								var store = densityCombo.getStore();
								var idx = store.findBy(function(record,id){
									if(record.data.value==val) return true;
									return false;
								});
								var rec;
								if(idx>=0) rec = store.getAt(idx);
								if(rec){
									densityCombo.setValue(val);
									densityCombo.fireEvent('select',densityCombo,rec,idx);
								}
							}
						});
					}catch(e){
						alert(e);
					}
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: 'Density Max(%)',
			id : 'navigate-range-panel-density-max-numberfield',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
					_dump("change():["+field.id+"]");
					_dump("change():["+field.id+"]:CALL get_ajax_zrange_object_range_task3()");
//					get_ajax_zrange_object_range_task3.delay(250);
					get_ajax_zrange_object_range_task3.delay(0);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: 'Density Min(%)',
			id : 'navigate-range-panel-density-min-numberfield',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
					_dump("change():["+field.id+"]");
					_dump("change():["+field.id+"]:CALL get_ajax_zrange_object_range_task3()");
//					get_ajax_zrange_object_range_task3.delay(250);
					get_ajax_zrange_object_range_task3.delay(0);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			fieldLabel: '',
			id : 'navigate-range-panel-density-primitive-checkbox',
			xtype: 'checkbox',
			readOnly: false,
			checked: false,
			listeners: {
				change: function(field, newValue, oldValue){
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}

		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			fieldLabel: 'Show only',
			id: 'navigate-range-panel-filter-combobox',
			xtype: 'combo',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
//			value: 'FMA5018',
//			value: Ext.isEmpty(gParams.fmaid) ? 'FMA5018':'',
//			value: Ext.isEmpty(gParams.fmaid) ? 'other.obo':'',
			value: '',
			readOnly: false,
			width: 130,
			store: new Ext.data.SimpleStore({
				fields: ['value','disp'],
				data : [
					['other.obo','Internal'],
					['FMA5018'  ,'Bone'],
					['FMA5022'  ,'Muscle'],
					['FMA3710'  ,'Vessel'],
					['',         'All']
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
//					_dump("select():["+combo.id+"]:CALL get_ajax_zrange_object_range_task3()");
//					get_ajax_zrange_object_range_task3.delay(100);
					get_ajax_zrange_object_range_task3.delay(0);
					\$('table.range_value').removeClass('range_select');
					\$('td.range_segment div.range_segment_area').removeClass('range_select');
					\$('td.range_segment div.range_value').removeClass('range_select');
				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			fieldLabel: 'Cuboid&nbsp;Vol(cc)',
			id: 'navigate-range-panel-cube-volume-combobox',
			xtype: 'combo',
			ctCls : 'x-hide-display',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
//			value: 'any',
			value: 'inf-10',
			readOnly: false,
			width: 130,
			store: new Ext.data.SimpleStore({
				fields: ['disp','value','min','max'],
				data : [
					['Less than 0.1'      ,'inf-01' ,null, 0.1],
					['0.1 or more and less than 0.35' ,'01-1'   , 0.1,0.35],
					['0.35 or more and less than 1'   ,'1-10'   ,0.35,   1],
					['1 or more and less than 10'     ,'10-100' ,   1,  10],
					['More than 10'                   ,'100-inf',  10,null],
					['Any'                            ,'any'    ,null,null]
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
					Ext.getCmp('navigate-range-panel-cube-volume-max-numberfield').setValue(record.data.max);
					Ext.getCmp('navigate-range-panel-cube-volume-min-numberfield').setValue(record.data.min);

					get_ajax_zrange_object_range_task2.delay(250);

					\$('table.range_value').removeClass('range_select');
					\$('td.range_segment div.range_segment_area').removeClass('range_select');
					\$('td.range_segment div.range_value').removeClass('range_select');
				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: '<span style="font-size:8px;">VolMax(cc)</span>',
			id : 'navigate-range-panel-cube-volume-max-numberfield',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			minValue: 0,
			fieldLabel: '<span style="font-size:8px;">VolMin(cc)</span>',
			id : 'navigate-range-panel-cube-volume-min-numberfield',
			readOnly: false,
			listeners: {
				change: function(field, newValue, oldValue){
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			xtype: 'combo',
			fieldLabel: 'Segment Range',
			ctCls : 'x-hide-display',
			id : 'navigate-range-panel-range-combobox',
			editable: false,
			mode: 'local',
			lazyInit: false,
			displayField: 'disp',
			valueField: 'value',
			triggerAction: 'all',
			value: 'H',
			width: 130,
			readOnly: false,
			store: new Ext.data.SimpleStore({
				fields:['disp'          ,'value','zmin'          ,'zmax'],
				data : [
					['Head'               ,'H'   ,1431.1           ,  null],
					['Upper body'         ,'U'   ,914.2            ,1431.1],
					['Leg'                ,'L'   ,null             , 914.2],

//					['Head+Upper body'    ,'HU'  ,'[1431.1,914.2]' ,'[null,1431.1]'],
//					['Upper body+Leg'     ,'UL'  ,'[914.2 , null]' ,'[1431.1,914.2]'],
//					['Head+Upper body+Leg','HUL' ,'[1431.1,null]'  ,'[null,914.2]'],

					['Head+Upper body+Leg','HUL' ,'[1431.1,914.2,null]'  ,'[null,1431.1,914.2]'],
					['Any'                ,'ANY' ,null             ,null]
				]
			}),
			listeners: {
				'select' : function(combo, record, index) {
//					_dump("select():["+combo.id+"]");
//					console.log(record);
					Ext.getCmp('navigate-range-panel-zmax-numberfield').setValue(record.data.zmax);
					Ext.getCmp('navigate-range-panel-zmin-numberfield').setValue(record.data.zmin);
//					_dump("select():["+combo.id+"]:CALL get_ajax_zrange_object_range_task()");
//					get_ajax_zrange_object_range_task.delay(250);
					get_ajax_zrange_object_range_task.delay(0);

					\$('table.range_value').removeClass('range_select');
					\$('td.range_segment div.range_segment_area').removeClass('range_select');
					\$('td.range_segment div.range_value').removeClass('range_select');

					\$('.navigate-range-panel-event').removeClass('navigate-range-panel-event-select');
					\$('#navigate-range-panel-event-'+record.data.value).addClass('navigate-range-panel-event-select');
				},
				'render' : function(combo) {
//					_dump("render():["+combo.id+"]");
					var val = combo.getValue();
					var store = combo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==val) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						combo.fireEvent('select',combo,rec,idx);
//						_dump("render():["+combo.id+"]:CALL get_ajax_zrange_object_range_task()");
						get_ajax_zrange_object_range_task.cancel();


						var tabpanel = Ext.getCmp('navigate-tab-panel');
						if(tabpanel && tabpanel.rendered){
							var activeTab = tabpanel.getActiveTab();
							if(activeTab && activeTab.id=='navigate-range-panel'){
//							_dump("render():["+combo.id+"]:CALL get_ajax_zrange_object_range_task3()");
//								get_ajax_zrange_object_range_task3.delay(250);
								get_ajax_zrange_object_range_task3.delay(0);
//								combo.fireEvent('select',combo,rec,idx);
							}else{
								Ext.getCmp('navigate-range-panel').on({
									beforeshow: function(panel){
										var combo = Ext.getCmp('bp3d-tree-type-combo');
										var value = combo.getValue();
										var store = combo.getStore();
										var idx = store.findBy(function(r,id){
											return r.get('t_type')===value;
										});
										if(idx<0) return;
										var rec = store.getAt(idx);
										combo.fireEvent('select',combo,rec,idx);
									},
									self: this,
									single:true,
									buffer: 250
								});
							}
						}
					}
				},
				scope:this
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			readOnly: false,
			xtype: 'textfield',
			width: 114,
			fieldLabel: '<span style="font-size:8px;">ZMax(mm)</span>',
			id : 'navigate-range-panel-zmax-numberfield',
			listeners: {
				change: function(field, newValue, oldValue){
//					_dump("change():["+field.id+"]");
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			readOnly: false,
			xtype: 'textfield',
			width: 114,
			fieldLabel: '<span style="font-size:8px;">ZMin(mm)</span>',
			id : 'navigate-range-panel-zmin-numberfield',
			listeners: {
				change: function(field, newValue, oldValue){
//					_dump("change():["+field.id+"]");
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			readOnly: false,
			xtype: 'textfield',
			width: 114,
			fieldLabel: '<span style="font-size:8px;">Add condition</span>',
			id : 'navigate-range-panel-condition-textfield',
			listeners: {
				change: function(field, newValue, oldValue){
//					_dump("change():["+field.id+"]");
					get_ajax_zrange_object_range_task2.delay(250);
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		},{
			hidden: true,
			hideLabel: true,
			ctCls : 'x-hide-display',
			allowBlank: true,
			readOnly: true,
			fieldLabel: '#',
			id : 'navigate-range-panel-num-numberfield',
			listeners: {
				change: function(field, newValue, oldValue){
//					_dump("change():["+field.id+"]");
				},
				render: function(field) {
//					_dump("render():["+field.id+"]");
				}
			}
		}];
	var navigate_range_panel = new Ext.Panel({
		title: 'Segment',
		id: 'navigate-range-panel',
		autoScroll: true,
		layout: 'form',
		labelWidth: 156,
		labelAlign: 'right',
		defaultType: 'numberfield',
		defaults : {
			allowBlank: false,
			ctCls : 'x-small-editor',
			readOnly: true,
			selectOnFocus: true,
			width: 60
		},
		items : navigate_range_panel_items,
		listeners: {
			render: function(comp){
//				_dump("render():["+comp.id+"]");


				Ext.get('navigate-range-panel-base').unselectable();
				Ext.get('navigate-range-panel-event-head').unselectable();
				Ext.get('navigate-range-panel-event-body').unselectable();
				Ext.get('navigate-range-panel-event-leg').unselectable();
				Ext.get('navigate-range-panel-event-head-body').unselectable();
				Ext.get('navigate-range-panel-event-body-leg').unselectable();
				Ext.get('navigate-range-panel-event-all').unselectable();

				\$('table.navigate_range_panel_density label').each(function(){
					Ext.get(this).unselectable();
				});
				\$('table.navigate_range_panel_density_item input[type="radio"]').bind('change',function(event){

					\$('table.navigate_range_panel_density_item').removeClass('select_item');
					\$(this).closest('table.navigate_range_panel_density_item').addClass('select_item');

					var val = \$(this).val();
					var densityCombo = Ext.getCmp('navigate-range-panel-density-combobox');
					var store = densityCombo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==val) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						densityCombo.setValue(val);
						densityCombo.fireEvent('select',densityCombo,rec,idx);
					}
				});
				\$('table.navigate_range_panel_density_item input[type="checkbox"]').bind('change',function(event){

					if(get_ajax_zrange_object_transactionId){
						if(Ext.Ajax.isLoading(get_ajax_zrange_object_transactionId)){
							Ext.Ajax.abort(get_ajax_zrange_object_transactionId);
							get_ajax_zrange_object_transactionId = null;
						}
					}

					var minValue = null;
					var maxValue = null;
					var checkValue = false;

					var \$c1 = \$('table.navigate_range_panel_density_item input#navigate-range-panel-density-checkbox-name-element[type="checkbox"]:checked');
					var \$c2 = \$('table.navigate_range_panel_density_item input#navigate-range-panel-density-checkbox-name-complete-compound[type="checkbox"]:checked');
					var \$c3 = \$('table.navigate_range_panel_density_item input#navigate-range-panel-density-checkbox-name-incomplete-compound[type="checkbox"]:checked');

					if(\$c1.length) checkValue = true;
					if(\$c2.length && \$c3.length){
						minValue = 0;
						maxValue = null;
					}else if(\$c2.length){
						minValue = 1.0;
						maxValue = null;
					}else if(\$c3.length){
						minValue = 0;
						maxValue = 1.0;
					}
					if(!checkValue && minValue==null && maxValue==null){
						checkValue = true;
						minValue = 0;
					}

					Ext.getCmp('navigate-range-panel-density-max-numberfield').setValue(maxValue);
					Ext.getCmp('navigate-range-panel-density-min-numberfield').setValue(minValue);
					Ext.getCmp('navigate-range-panel-density-primitive-checkbox').setValue(checkValue);

					get_ajax_zrange_object_range_task3.delay(0);
				});

				\$('.navigate-range-panel-event').bind('click',function(event){
					var id = \$(this).attr('id');
					var val = id.substr('navigate-range-panel-event'.length+1);

					var combo = Ext.getCmp('navigate-range-panel-range-combobox');
					var store = combo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==val) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						combo.setValue(val);
						combo.fireEvent('select',combo,rec,idx);
					}

					event.preventDefault();
					event.stopPropagation();
					return false;
				});


				\$('div#navigate-range-panel-base2').hide();
				\$('div#navigate-range-panel-base-fx').show();

				\$('td.range_show_only_image').bind('click',function(event){
					\$('td.range_show_only_image').removeClass('range_select');
					var value;
					if(\$(this).hasClass('range_show_only_image_Bone')){
						value = 'Bone';
					}else if(\$(this).hasClass('range_show_only_image_Muscle')){
						value = 'Muscle';
					}else if(\$(this).hasClass('range_show_only_image_Vessel')){
						value = 'Vessel';
					}else if(\$(this).hasClass('range_show_only_image_Internal')){
						value = 'Internal';
					}else if(\$(this).hasClass('range_show_only_image_All')){
						value = 'All';
					}
					if(!Ext.isEmpty(value)){
						var combo = Ext.getCmp('navigate-range-panel-filter-combobox');
						var store = combo.getStore();
						var idx = store.findBy(function(record,id){
							if(record.data.disp==value) return true;
							return false;
						});
						var rec;
						if(idx>=0) rec = store.getAt(idx);
						if(rec){
							combo.setValue(rec.data.value);
							combo.fireEvent('select',combo,rec,idx);
						}
					}
					event.preventDefault();
					event.stopPropagation();
					return false;
				});

				\$('td.range_segment div.range_value').bind('click',function(event){
					_dump("td.range_segment div.range_value : click()");
					var cuboid_value = \$(this).attr('cuboid_value');
					var segment_value = \$(this).attr('segment_value');

					\$('table.range_value').removeClass('range_select');
					\$('td.range_segment div.range_segment_area').removeClass('range_select');
					\$('td.range_segment div.range_value').removeClass('range_select');

					var combo = Ext.getCmp('navigate-range-panel-cube-volume-combobox');
					var store = combo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==cuboid_value) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						combo.setValue(rec.data.value);
						combo.fireEvent('select',combo,rec,idx);
						get_ajax_zrange_object_range_task.cancel();
					}
					var combo = Ext.getCmp('navigate-range-panel-range-combobox');
					var store = combo.getStore();
					var idx = store.findBy(function(record,id){
						if(record.data.value==segment_value) return true;
						return false;
					});
					var rec;
					if(idx>=0) rec = store.getAt(idx);
					if(rec){
						combo.setValue(rec.data.value);
						combo.fireEvent('select',combo,rec,idx);
						get_ajax_zrange_object_range_task.cancel();
					}
//					get_ajax_zrange_object_range_task.delay(100);
					get_ajax_zrange_object_range_task.delay(0);

//													<tr><td class="range_segment range_segment_inf-10 range_value">
//														<div class="range_segment_base">
//															<div class="range_segment range_segment_HU range_segment_area range_segment_area_HU">&nbsp</div>


					if(\$('table.range_segment_'+cuboid_value+'.range_segment_area_'+segment_value).addClass('range_select').length==0){
						if(\$('td.range_segment_'+cuboid_value+' div.range_segment_area_'+segment_value).addClass('range_select').length==0){
							\$('td.range_segment_'+cuboid_value+' div.range_segment_'+segment_value).addClass('range_select');
						}
					}

					event.preventDefault();
					event.stopPropagation();
					return false;
				});

				\$("input#navigate-range-panel-only-taid").change(function(){
					get_ajax_zrange_object_range_task3.delay(0);
				});

				\$('table.navigate_range_panel_density_item input[type="checkbox"]').trigger('change');


			},
			resize: function(comp, adjWidth, adjHeight, rawWidth, rawHeight){
//				_dump("resize():["+comp.id+"]["+adjWidth+"]["+adjHeight+"]["+rawWidth+"]["+rawHeight+"]");
			},
			show: {
				fn: function(comp){
					if(_location.location.href == 'about:blank') _location.location.href = 'location.html';

					navigate_range_panel_init_show=1;

				},
				single: true
			}
		}
	});

HTML
}
print <<HTML;
	var navigate_tabs = new Ext.TabPanel({
//		title   : get_ag_lang('TREE_TITLE'),
//		title   : " ",
//		header: true,
//		headerAsText: false,
		id      : 'navigate-tab-panel',
//		region  : 'west',
		region  : 'center',
//		split   : true,
//		width   : 192,
//		minWidth : 192,
		border  : false,
		anchor:'100% 100%',
//		bodyStyle: 'border-width:0 1px;',
//		frame:true,
		enableTabScroll: true,
HTML
if($useNavigateRange eq 'true'){
	print <<HTML;
//		activeTab: (!Ext.isEmpty(gParams.fmaid) && !Ext.isEmpty(gParams.txpath) && !Ext.isEmpty(gParams.t_type)) ? 2 : 0,
		activeTab: 0,
HTML
}else{
	print <<HTML;
		activeTab: 0,
HTML
}
print <<HTML;
		layoutOnTabChange : true,
		deferredRender : false,
		items:[
HTML
if($useNavigateRange eq 'true'){
	print <<HTML;
			navigate_range_panel,
			navigate_position_panel,
HTML
}
print <<HTML;
			navigate_tree_panel,
			navigate_grid_panel
HTML
if($useNavigateRange eq 'true'){
	print <<HTML;
//			,navigate_position_panel
HTML
}
print <<HTML;
		],
HTML
print <<HTML;
		listeners: {
			'tabchange' : function(tabpanel,tab){
//				_dump("tabchange():["+tabpanel.id+"]["+tab.id+"]");

				try{
					Ext.each(Ext.getCmp('bp3d-tree-type-combo').getStore().getRange(),function(r,i,a){
						\$('label#navigate-north-panel-content-label-'+r.data.t_type).text('');
					});
				}catch(e){}

bp3d_change_location(undefined,true);//ローカルな履歴をクリア

				if(tab.id == 'navigate-grid-panel'){
//					contents_panel.layout.setActiveItem(1);
HTML
if($useNavigateRange eq 'true'){
	print <<HTML;

					var t_type = Ext.getCmp('bp3d-tree-type-combo').getValue();
					var version = Ext.getCmp('bp3d-version-combo').getValue();
					var baseParams = tab.getStore().baseParams;
					if(baseParams.t_type != t_type || baseParams.version != version){
						Ext.getCmp('navigate-grid-paging-toolbar').changePage(1);
						_dump(Ext.getCmp('navigate-grid-paging-toolbar'));
					}
				}else if(tab.id == 'navigate-tree-panel'){
					var treeCmp = tab;
					if(!treeCmp || !treeCmp.root) return;

					var t_type = Ext.getCmp('bp3d-tree-type-combo').getValue();
					var version = Ext.getCmp('bp3d-version-combo').getValue();
					var baseParams = treeCmp.getLoader().baseParams;

					var cb = function(node){
						if(!Ext.isEmpty(gBP3D_TPAP) && node.firstChild && node.firstChild.attributes.attr.f_id){
							gBP3D_TPAP = undefined;
							Cookies.set('ag_annotation.images.path','/'+node.firstChild.attributes.attr.f_id);
						}
						var path = Cookies.get('ag_annotation.images.path','');
						node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',function(bSuccess,oSelNode){
							if(bSuccess){
								selectPathCB(bSuccess,oSelNode);
							}else if(node.firstChild){
								Cookies.set('ag_annotation.images.path','/'+node.firstChild.attributes.attr.f_id);
								var path = Cookies.get('ag_annotation.images.path','')
								node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
							}
						});
					};

					if(baseParams.t_type != t_type || baseParams.version != version){
						treeCmp.root.reload(cb);
					}else{
						cb(treeCmp.root);
					}

				}else if(
					tab.id == 'navigate-position-panel' ||
					tab.id == 'navigate-range-panel'
				){
					var value = 'thump';
					image_disptype = value;
					try{
						var disptypeSelect = Ext.getCmp('disptypeSelect');
						disptypeSelect.setValue(value);
						var idx = disptypeSelect.getStore().findBy(function(r,id){
							return(value===r.data.value)
						});
						var cmp = Ext.getCmp('img-chooser-view');
						if(cmp && cmp.rendered){
							cmp.layout.setActiveItem(idx);
						}

						if(tab.id == 'navigate-position-panel'){
							zpositionCmp = Ext.getCmp('navigate-position-panel-zposition-numberfield');
							if(zpositionCmp.isValid(true)){
								get_ajax_zrange_object_position_task.delay(250);
							}else{
								getViewImages().getStore().reload();
							}
						}else if(tab.id == 'navigate-range-panel'){
//							_dump("tabchange():["+tabpanel.id+"]:CALL get_ajax_zrange_object_range_task3()");
							get_ajax_zrange_object_range_task3.cancel();
//							get_ajax_zrange_object_range_task3.delay(100);
							get_ajax_zrange_object_range_task3.delay(0);
						}
					}catch(e){
						image_disptype = value;
					}

HTML
}
print <<HTML;
				}else{
					var store;
					try{if(tab.getStore) store = tab.getStore();}catch(e){}
					if(store) store.reload({params:{start:0,limit:store.lastOptions.params.limit}});
				}


			},
			'afterlayout' : function(tabpanel,layout){
				afterLayout(tabpanel);
			},
			'remove' : function(tabpanel,panel){
//_dump("navigate-tab-panel.remove():"+tabpanel.items.getCount());
				if(tabpanel.items.getCount()<=4) tabpanel.scrollToTab(Ext.getCmp('navigate-range-panel'),false);
			},
			scope:this
		}
	});

	var navigate_panel = new Ext.Panel({
		id      : 'navigate-panel',
//		title   : ' ',
		region  : 'west',
		split   : true,
//		width   : 192,
//		width   : 250,
//		width   : 300,

		width   : 300,
		minWidth : 300,

		border  : false,
		bodyStyle: 'border-width:0 1px 1px;',
//		layout: 'anchor',
		layout: 'border',
		items: [{
			id: 'navigate-north-panel',
			region: 'north',
			height: 70,
			border: false,
//			frame: false,
			bodyStyle: 'border-width:0 0 1px 0;background:transparent;',
//			html:get_ag_lang('TREE_TYPE_NORTH_HTML')
			contentEl: 'navigate-north-panel-content',
			listeners: {
				render: function(comp){
					\$('div#navigate-north-panel-content label').each(function(){
						Ext.get(this).unselectable();
					});
					\$('div#navigate-north-panel-content input[type=radio]').change(function(){
						var combo = Ext.getCmp('bp3d-tree-type-combo');
						var value = Number(\$(this).val());
						if(combo.getValue()==value) return;
						var store = combo.getStore();
						var idx = store.findBy(function(r,id){
							return r.get('t_type')===value;
						});
						if(idx<0) return;
						combo.setValue(value);
						var rec = store.getAt(idx);
						combo.fireEvent('select',combo,rec,idx);
					});

					var combo = Ext.getCmp('bp3d-tree-type-combo');
					var store = combo.getStore();
//					_dump("render():["+comp.id+"]["+store.getCount()+"]");
					if(store.getCount()>0){
						var t_type = combo.getValue();
						\$('div#navigate-north-panel-content input[type=radio][value='+t_type+']').attr({checked:true});
					}
					combo.on({
						select: {
							fn: function(combo,record,index){
								\$('div#navigate-north-panel-content input[type=radio][value='+record.data.t_type+']').attr({checked:true});
							}
						}
					});

					Ext.getCmp('contents-tab-panel').on({
						tabchange: {
							fn: function(tabpanel,tab){
								if(tab.id != 'contents-tab-bodyparts-panel') return;
								comp.setHeight(comp.initialConfig.height);
								comp.findParentByType('panel').doLayout();
							},
							buffer: 250
						}
					});
				}
			}
		},navigate_tabs],
/*
		tools:[{
			id:'right',
			handler: function(event, toolEl, panel){
				toolEl.addClass('x-hide-display');
				var left_tool = panel.getTool('left');
				if(left_tool) left_tool.removeClass('x-hide-display');

				var contents_tab_bodyparts_panel = Ext.getCmp('contents-tab-bodyparts-panel');
				var bp3d_contents_detail_panel = Ext.getCmp('bp3d-contents-detail-panel');
				if(contents_tab_bodyparts_panel && bp3d_contents_detail_panel){
					var size1 = contents_tab_bodyparts_panel.getSize();
					var size2 = bp3d_contents_detail_panel.getSize();
					panel.setWidth(size1.width-size2.width);
				}
				var cmp = Ext.getCmp('viewpage-panel');
				if(cmp) cmp.layout.setActiveItem('bp3d-detail-panel');
				var viewport = Ext.getCmp('viewport');
				if(viewport && viewport.rendered) viewport.doLayout();
			}
		},{
			id:'left',
			handler: function(event, toolEl, panel){
				toolEl.addClass('x-hide-display');
				var right_tool = panel.getTool('right');
				if(right_tool) right_tool.removeClass('x-hide-display');

				var box = panel.getBox();
				if(box.x==0 && box.y==0) return;
				var width  = Ext.isEmpty(panel.initialConfig.minWidth) ?box.width :panel.initialConfig.minWidth;

				panel.setWidth(width);

				var cmp = Ext.getCmp('viewpage-panel');
				if(cmp) cmp.layout.setActiveItem('bp3d-contents-panel');
				var viewport = Ext.getCmp('viewport');
				if(viewport && viewport.rendered) viewport.doLayout();
			}
		}],
*/
		listeners: {
			'render' : function(panel){
				var left_tool = panel.getTool('left');
				if(left_tool) left_tool.addClass('x-hide-display');
			},
			'afterlayout' : function(panel,layout){
				afterLayout(panel);
			},
			scope:this
		}
	});

	var resizeNavigateGridPanel = function(){
		var grid = Ext.getCmp('navigate-grid-panel');
		var column = grid.getColumnModel();
		var innerWidth = grid.getInnerWidth();
		var totalWidth = column.getTotalWidth(false);
		var columnCount = column.getColumnCount();
		var columnNum = 0;
		for(var i=0;i<columnCount;i++){
			if(column.isHidden(i)) continue;
			columnNum++;
		}
		if(columnNum==0) return;
		var columnWidth = parseInt((innerWidth-15)/columnNum);
		for(var i=0;i<columnCount;i++){
			if(column.isHidden(i)) continue;
			column.setColumnWidth(i,columnWidth);
		}
	};

	var formatFeedbackData = function(data){
		data.shortTitle = null;
		if(data.c_title) data.shortTitle = data.c_title.ellipse(get_ag_lang('SORTNAME_LENGTH'));

		data.name = null;
		if(data.c_name){
			data.name = data.c_name;
		}else if(data.c_openid){
			data.name = data.c_openid;
		}

		data.nameString = '';
		if(data.c_name){
			if(data.c_email){
				data.nameString = '<a href="mailto:'+data.c_email+'">'+data.c_name+'</a>';
			}else{
				data.nameString = data.c_name;
			}
		}else if(data.c_openid){
			if(data.c_email){
				data.nameString = '<a href="mailto:'+data.c_email+'">'+data.c_openid+'</a>';
			}else{
				data.nameString = data.c_openid;
			}
		}

		data.commentString = null;
		if(data.c_comment){
			data.commentString = data.c_comment.replace(/\\n/g,"<br>");
		}

		if(data.c_reply && data.c_reply.length>0){
			for(var j=0,len=data.c_reply.length;j<len;j++){
				var data2 = data.c_reply[j];

				data2.c_entry=new Date(parseInt(data2.c_entry)*1000);
				data2.dateString = formatTimestamp(data2.c_entry);

				data2.nameString = null;
				if(data2.c_name){
					if(data2.c_email){
						data2.nameString = '<a href="mailto:'+data.c_email+'">'+data2.c_name+'</a>';
					}else{
						data2.nameString = data2.c_name;
					}
				}else if(data2.c_openid){
					if(data2.c_email){
						data2.nameString = '<a href="mailto:'+data.c_email+'">'+data2.c_openid+'</a>';
					}else{
						data2.nameString = data2.c_openid;
					}
				}

				data2.commentString = null;
				if(data2.c_comment){
					data2.commentString = data2.c_comment.replace(/\\n/g,"<br>");
				}
			}
		}
		data.dateString = formatTimestamp(data.c_entry);

		if(data.c_path && data.c_names && data.c_tree){
		}

		if(data.c_path && data.c_path.length>0) data.c_path = data.c_path[0];
		if(data.c_tree && data.c_tree.length>0) data.c_tree = data.c_tree[0];


		data.cs_name = null;
		if(data.cs_id && comment_status[data.cs_id]){
			if(data.cs_id == 1){
				data.cs_name = '<span class="pending">'+comment_status[data.cs_id]+'</span>';
			}else{
				data.cs_name = comment_status[data.cs_id];
			}
		}

		return data;
	};

	var contents_tab_feedback_store_fields = [
		{name: 'f_id',        type:'string'},
		{name: 'c_id',        type:'int'},
		{name: 'c_pid',       type:'int'},
		{name: 'c_openid',    type:'string'},
		{name: 'c_name',      type:'string'},
		{name: 'c_email',     type:'string'},
		{name: 'c_title',     type:'string'},
		{name: 'c_comment',   type:'string'},
		{name: 'c_entry',     type:'date', dateFormat:'timestamp'},
		{name: 'c_image',     type:'string'},
		{name: 'c_image_thumb', type:'string'},
		{name: 'c_fma_image', type:'string'},
		{name: 'c_fma_name',  type:'string'},
		{name: 'ct_name',     type:'string'},
		{name: 'ct_id',       type:'int'},
		{name: 'cs_id',       type:'int'},
		{name: 'cs_name',     type:'string'},
		{name: 'f_name',      type:'string'},
		{name: 'c_reply'},
		{name: 'c_path'},
		{name: 'c_names'},
		{name: 'c_tree'},
		{name: 'c_fmas'},
	];

	var updateFeedbackChildStore = new Ext.data.JsonStore({
		url           : 'get-feedback.cgi',
		root          : 'feedback',
		totalProperty : 'totalCount',
		remoteSort    : true,
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},
		fields : contents_tab_feedback_store_fields,
		listeners: {
			'beforeload' : function(store,options){
				store.baseParams = store.baseParams || {};
			},
			'load' : function(store,records,options){
				if(records.length>0){
					var c_pid = records[0].data.c_pid;
					var data = [];
					for(var i=0,len=records.length;i<len;i++){
						formatFeedbackData(records[i].data);
						data.push(records[i].data);
						updateFeedbackChildStack.push(records[i].data);
					}
					if(!Ext.isEmpty(c_pid)){
						var elem = Ext.get('feedback_child_'+c_pid);
						if(elem) feedbackChildTemplate.overwrite(elem,data);
					}
				}
				if(updateFeedbackChildTimeoutID) clearTimeout(updateFeedbackChildTimeoutID);
				updateFeedbackChildTimeoutID = setTimeout(updateFeedbackChild,0);
				contents_tab_feedback_all_store.add(records);
			},
			'loadexception': function(){
			},
			'datachanged': function(){
			},
			scope:this
		}
	});

	updateFeedbackChildTimeoutID = null;
	updateFeedbackChildStack = [];
	updateFeedbackChild = function(){
		if(updateFeedbackChildStack.length == 0) return;
		var data = updateFeedbackChildStack.shift();
		var elem = Ext.get('feedback_child_'+data.c_id);
		if(elem){
			updateFeedbackChildStore.load({params : {c_pid : data.c_id}});
		}else{
			if(updateFeedbackChildTimeoutID) clearTimeout(updateFeedbackChildTimeoutID);
			updateFeedbackChildTimeoutID = setTimeout(updateFeedbackChild,0);
		}
	};


	var contents_tab_feedback_all_store = new Ext.data.SimpleStore({
		root          : 'feedback',
		totalProperty : 'totalCount',
		fields : contents_tab_feedback_store_fields
	})

	var contents_tab_feedback_store = new Ext.data.JsonStore({
		url           : 'get-feedback.cgi',
		root          : 'feedback',
		totalProperty : 'totalCount',
		remoteSort    : true,
		baseParams    : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},
		fields : contents_tab_feedback_store_fields,
		listeners: {
			'beforeload' : function(store,options){
				contents_tab_feedback_all_store.removeAll();
				store.baseParams = store.baseParams || {};
				store.baseParams.cs_id = Ext.getCmp('contents-tab-feedback-status-combo').getValue();
			},
			'load' : function(store,records,options){
				if(contents_tab_feedback_pagingBar) contents_tab_feedback_pagingBar.enable();
				if(records.length>0){
					var c_pid = records[0].data.c_pid;
					for(var i=0,len=records.length;i<len;i++){
						updateFeedbackChildStack.push(records[i].data);
					}
					if(Ext.isEmpty(c_pid)){
						if(updateFeedbackChildTimeoutID) clearTimeout(updateFeedbackChildTimeoutID);
						updateFeedbackChildTimeoutID = setTimeout(updateFeedbackChild,500);
					}
				}
				contents_tab_feedback_all_store.add(records);
			},
			'loadexception': function(){
				if(contents_tab_feedback_pagingBar) contents_tab_feedback_pagingBar.disable();
			},
			'datachanged': function(){
				var element = contents_tab_feedback_dataview.getEl();
				if(element){
					element.dom.scrollTop = 0;
					element.dom.parentNode.scrollTop = 0;
				}
			},
			scope:this
		}
	});
	contents_tab_feedback_store.setDefaultSort('c_entry', 'desc');

	var contents_tab_feedback_pagingBar = new Ext.PagingToolbar({
		pageSize    : 10,
		store       : contents_tab_feedback_store,
		displayInfo : true,
		displayMsg  : get_ag_lang('PAGING_DISP_MSG')+' {0} - {1} of {2}',
		emptyMsg    : get_ag_lang('PAGING_EMPTY_MSG'),
		hideMode    : 'offsets',
		hideParent  : true,
		items       : [
			'-',
			{
				id    : 'sortSelect_label1',
				xtype : 'tbtext',
				text  : get_ag_lang('SORT_TITLE')+':'
			},{
				hidden : false,
				id: 'sortFeedback',
				xtype: 'combo',
				typeAhead: true,
				triggerAction: 'all',
				width: get_ag_lang('SORT_WIDTH'),
				listWidth: get_ag_lang('SORT_LIST_WIDTH'),
				editable: false,
				mode: 'local',
				displayField: 'desc',
				valueField: 'name',
				lazyInit: false,
				value: 'c_entry',
				disabled : true,
				store: new Ext.data.SimpleStore({
					fields: ['name', 'desc'],
					data : [
						['c_entry',    'New Thread'],
						['c_modified', 'Modified'],
						['cs_id',      'Status'],
						['f_id',       'FMAID']
					]
				}),
				listeners: {
					'select': {
						fn:function(combo,record,index){
							var value = combo.getValue();
							var dir = 'asc';
							if(value == 'c_entry' || value == 'c_modified' || value == 'cs_id') dir = 'desc';
							contents_tab_feedback_store.setDefaultSort(value, dir);
							contents_tab_feedback_store.reload();
						},scope:this}
				}
			},
			'-'
		]
	});

	var FeedbackPanel = Ext.extend(Ext.DataView, {
		onClick : function(e){
			var group = e.getTarget('h2', 7, true);
			if(group){
				var targetDom = e.getTarget('a',0);
				if(Ext.isEmpty(targetDom)) group.up('div').toggleClass('collapsed');
			}else {
				var index = -1;
				var target = e.getTarget('div.feedback-comment',1,true);
				if(target){
					var c_id = target.dom.getAttribute('c_id');
					index = contents_tab_feedback_all_store.find('c_id',c_id);
					if(index>=0) openWindowComment(contents_tab_feedback_all_store.getAt(index).copy().data);
				}
				if(index<0){
					var t = e.getTarget('dd', 5, true);
					if(t && !e.getTarget('a', 2)){
						var txpath = t.getAttributeNS('ext', 'txpath');
						var id = t.getAttributeNS('ext', 'id');
						var treeCmp = Ext.getCmp('navigate-tree-panel');
						if(treeCmp){
							Cookies.set('ag_annotation.images.fmaid',id);
//_dump("3926:CALL selectPathCB()");
							treeCmp.selectPath(txpath,'f_id',selectPathCB);
						}
					}else{
						var targetDom = e.getTarget('a',0);
						if(targetDom && targetDom.href != location.protocol + "//" + location.host + location.pathname + location.search + "#"){
							var form = Ext.getDom('comment-link-form');
							if(form){
								form.action = targetDom.href;

								while(form.lastChild){
									form.removeChild(form.lastChild);
								}
								var loc_path = targetDom.href;
								var loc_search = "";
								var loc_hash = "";
								var loc_search_index = loc_path.indexOf("?");
								if(loc_search_index>=0){
									loc_search = loc_path.substr(loc_search_index+1);
									loc_path = loc_path.substr(0,loc_search_index);
									form.action = loc_path;
								}
								var loc_hash_index = loc_search.indexOf("#");
								if(loc_hash_index>=0){
									loc_hash = loc_search.substr(loc_hash_index+1);
									loc_search = loc_search.substr(0,loc_hash_index);
								}

								if(loc_search){
									var loc_search = Ext.urlDecode(loc_search,true);
									for(var key in loc_search){
										var elem = form.ownerDocument.createElement("input");
										elem.setAttribute("type","hidden");
										elem.setAttribute("name",key);
										elem.setAttribute("value",loc_search[key]);
										form.appendChild(elem);
									}
								}
								if(loc_hash) form.setAttribute("action",loc_path + "#" + loc_hash);
								form.submit();
								e.stopEvent();
							}
						}
					}
				}else{
				}
			}
			return FeedbackPanel.superclass.onClick.apply(this, arguments);
		}
	});

	var contents_tab_feedback_dataview = new FeedbackPanel({
		id           : 'contents-tab-feedback-dataview',
		tpl          : feedbackTemplate,
		itemSelector : 'dd',
		overClass    : 'over',
		autoShow     : true,
		autoHeight   : true,
		singleSelect : true,
		multiSelect  : false,
		emptyText    : '<div style="padding:10px;">'+get_ag_lang('MSG_NOT_DATA')+'</div>',
		loadingText  : get_ag_lang('MSG_LOADING_DATA'),
		store        : contents_tab_feedback_store,
		renderTo   : 'contents-tab-feedback-contents-panel-render',
		listeners: {
			'render': {
				fn:function(view){
				}, scope:this},
			'show': {
				fn:function(view){
				}, scope:this},
			'selectionchange': {
				fn:function(view,selections){
					var data = null;
					if(selections && selections.length > 0) data = view.getRecord(selections[0]).data;
					try{var commentDetailEl = contents_tab_feedback_detail_panel.body;}catch(e){}
					if(Ext.isEmpty(commentDetailEl)) return;

				}, scope:this, buffer:0},
			'loadexception'  : {fn:onLoadException, scope:this},
			'beforeselect'   : {fn:function(view){return view.store.getRange().length > 0;}}
		},
		prepareData: formatFeedbackData.createDelegate(this)
	});

	var contents_tab_feedback_detail_panel = new Ext.Panel({
		region      : 'east',
		split       : true,
		autoScroll  : true,
		width       : 220,
		minWidth    : 220,
		maxWidth    : 330
	});

	var contents_tab_feedback_contents_panel = new Ext.Panel({
		id         : 'contents-tab-feedback-contents-panel',
		border     : false,
		bbar       : contents_tab_feedback_pagingBar,
		autoShow   : true,
		autoScroll : true,
		region     : 'center',
		items      : contents_tab_feedback_dataview,
		listeners  : {
			'beforeshow' : function(panel){
			},
			'show' : function(){
				if(!contents_tab_feedback_dataview.rendered){
					setTimeout(function(){ contents_tab_feedback_dataview.render(); },500);
				}else{
					contents_tab_feedback_store.reload({params:{start:0,limit:10}});
				}
			},
			scope : this
		}
	});

	var contents_tab_feedback_panel = new Ext.Panel({
		title    : get_ag_lang('TITLE_REVIEWS'),
HTML
print qq|		tabTip   : get_ag_lang('TABTIP_REVIEWS'),\n| if($useTabTip eq 'true');
print <<HTML;
		header   : false,
		border   : false,
		autoShow : true,
		id       : 'contents-tab-feedback-panel',
		renderTo : 'contents-tab-feedback-panel-render',
		layout   : 'border',
		items    : contents_tab_feedback_contents_panel,
		listeners  : {
			'beforeshow' : function(panel){
			},
			'show' : function(){
				if(!contents_tab_feedback_dataview.rendered){
					setTimeout(function(){ contents_tab_feedback_dataview.render(); },500);
				}else{
					contents_tab_feedback_store.reload({params:{start:0,limit:10}});
				}
			},
			scope : this
		}
	});

	var contents_tab_home_panel = new Ext.Panel({
		title  : get_ag_lang('TITLE_HOME'),
HTML
print qq|		tabTip   : get_ag_lang('TABTIP_HOME'),| if($useTabTip eq 'true');
print <<HTML;
		id     : 'contents-tab-home-panel'
	});

	var bp3s_parts_gridpanel_col_version = {
		dataIndex:'version',
		header: ag_lang.DATA_VERSION,
		id:'version',
		sortable: true,
		hidden:true,
		renderer:bp3s_parts_gridpanel_renderer
	};

	var bp3s_parts_gridpanel_col_icon = {
		dataIndex:'icon',
		header:'',
		id:'icon',
		sortable: false,
		hidden:$gridColHiddenID,
		renderer:bp3s_parts_gridpanel_icon_renderer,
		width:28,
		resizable:false,
		fixed:true,
		menuDisabled:true,
		hideable: false,
		resizable: false
	};

	var bp3s_parts_gridpanel_col_b_id = {
		dataIndex:'b_id',
		header:get_ag_lang('REP_ID'),
		id:'b_id',
		sortable: true,
		hidden:$gridColHiddenID,
		renderer:bp3s_parts_gridpanel_renderer,
		width:70,
		resizable:true,
		fixed:!$moveGridOrder,
		hideable:$moveGridOrder
	};
	var bp3s_parts_gridpanel_col_f_id = {
		dataIndex:'f_id',
		header:get_ag_lang('CDI_NAME'),
		id:'f_id',
		sortable: true,
		hidden:$gridColHiddenID,
		renderer:bp3s_parts_gridpanel_renderer,
		width:80,
		resizable:true,
		fixed:!$moveGridOrder,
		hideable:$moveGridOrder
	};
	var bp3s_parts_gridpanel_col_entry = {
		dataIndex:'entry',
		header:get_ag_lang('GRID_TITLE_MODIFIED'),
		id:'entry',
		sortable: true,
		hidden:true,
		renderer:bp3s_parts_gridpanel_date_renderer
	};
	var bp3s_parts_gridpanel_col_organsys = {
		dataIndex:'organsys',
		header:get_ag_lang('GRID_TITLE_ORGANSYS'),
		id:'organsys',
		sortable: true,
		hidden:true,
		renderer:bp3s_parts_gridpanel_renderer
	};

	var bp3s_parts_gridpanel_cols = [
		bp3s_parts_gridpanel_col_icon,
		bp3s_parts_gridpanel_col_b_id,
		bp3s_parts_gridpanel_col_f_id,
		{dataIndex:'tg_id',    header:'Model',                           id:'tg_id',    sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_group_renderer, fixed:$groupHidden},
HTML
print qq|		bp3s_parts_gridpanel_col_version,\n| if($moveGridOrder ne 'true');
print <<HTML;
		{dataIndex:'conv_id',  header:'ConversionID',                    id:'conv_id',  sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer, fixed:$groupHidden},
		{dataIndex:'common_id',header:'UniversalID',                     id:'common_id',sortable: true,  hidden:$gridColHiddenUniversalID, fixed:$gridColFixedUniversalID, renderer:bp3s_parts_gridpanel_commonid_renderer},
HTML
print qq|		bp3s_parts_gridpanel_col_f_id,\n| if($moveGridOrder ne 'true');
print <<HTML;
		{dataIndex:'name_e',   header:get_ag_lang('DETAIL_TITLE_NAME_E'),    id:'name_e',   sortable: true,  hidden:false, renderer:bp3s_parts_gridpanel_renderer},
//		{dataIndex:'name_l',   header:'Latina',                          id:'name_l',   sortable: true,  hidden:true, renderer:bp3s_parts_gridpanel_renderer},
//		{dataIndex:'name_j',   header:get_ag_lang('GRID_TITLE_NAME_J'),      id:'name_j',   sortable: true,  hidden:$gridColHiddenNameJ, renderer:bp3s_parts_gridpanel_renderer},
//		{dataIndex:'name_k',   header:get_ag_lang('GRID_TITLE_NAME_K'),      id:'name_k',   sortable: true,  hidden:$gridColHiddenNameJ, renderer:bp3s_parts_gridpanel_renderer},
HTML
if($moveGridOrder ne 'true'){
	print <<HTML;
		{dataIndex:'phase',    header:get_ag_lang('GRID_TITLE_PHASE'),       id:'phase',    sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
		bp3s_parts_gridpanel_col_entry,
HTML
}else{
	print <<HTML;
//		bp3s_parts_gridpanel_col_organsys,
HTML
}
print <<HTML;
		{dataIndex:'xmin',     header:'Xmin(mm)',                        id:'xmin',     sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
		{dataIndex:'xmax',     header:'Xmax(mm)',                        id:'xmax',     sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
		{dataIndex:'ymin',     header:'Ymin(mm)',                        id:'ymin',     sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
		{dataIndex:'ymax',     header:'Ymax(mm)',                        id:'ymax',     sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer},
		{dataIndex:'zmin',     header:'Zmin(mm)',                        id:'zmin',     sortable: true,  hidden:$hiddenGridColZmin, renderer:bp3s_parts_gridpanel_renderer},
		{dataIndex:'zmax',     header:'Zmax(mm)',                        id:'zmax',     sortable: true,  hidden:$hiddenGridColZmax, renderer:bp3s_parts_gridpanel_renderer},
		{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',   sortable: true,  hidden:true,  renderer:bp3s_parts_gridpanel_renderer}
HTML
if($moveGridOrder ne 'true'){
#	print qq|		,{dataIndex:'volume',   header:get_ag_lang('GRID_TITLE_VOLUME')+'(cm3)', id:'volume',   sortable: true,  hidden:false, renderer:bp3s_parts_gridpanel_renderer}\n| if($removeGridColValume ne 'true');
#	print qq|		,bp3s_parts_gridpanel_col_organsys\n| if($removeGridColOrganSystem ne 'true');
}else{
	print <<HTML;
		,bp3s_parts_gridpanel_col_version
		,bp3s_parts_gridpanel_col_entry
HTML
}
print <<HTML;
		,{dataIndex:'color',          header:'Color',                      sortable:false,  hidden:true, hideable:false}
		,{dataIndex:'opacity',        header:'Opacity',                    sortable:false,  hidden:true, hideable:false}
		,{dataIndex:'representation', header:get_ag_lang('ANATOMO_REP_LABEL'), sortable:false,  hidden:true, hideable:false}
		,{dataIndex:'value',          header:'Value',                      sortable:false,  hidden:true, hideable:false}
		,{dataIndex:'exclude',        header:'Remove',                     sortable:false,  hidden:true, hideable:false}
	];

	var bp3s_parts_gridpanel = new Ext.grid.GridPanel({
		title  : 'Pallet',
		header : false,
		id     : 'control-tab-partslist-panel',
		stateful       : true,
		stateId        : 'control-tab-partslist-panel',
//		columns        : bp3s_parts_gridpanel_cols,
		cm             : new Ext.grid.ColumnModel(bp3s_parts_gridpanel_cols),
		enableDragDrop : true,
		stripeRows     : true,
		region         : 'center',
		border         : false,
		style          : 'border-right-width:1px',
		viewConfig: {
			deferEmptyText: true,
			emptyText: '<div class="bp3d-pallet-empty-message">'+get_ag_lang('GRID_EMPTY_MESSAGE')+'</div>'
		},
		clicksToEdit   : 1,
		selModel : new Ext.grid.RowSelectionModel({
			listeners: {
				'selectionchange' : function(selModel){
					try{
						try{Ext.getCmp('bp3d-pallet-home-button').disable();}catch(e){}
						try{Ext.getCmp('bp3d-pallet-copy-button').disable();}catch(e){}
						Ext.getCmp('bp3d-pallet-delete-button').disable();
						if(selModel.getCount()>0){
							try{Ext.getCmp('bp3d-pallet-copy-button').enable();}catch(e){}
							Ext.getCmp('bp3d-pallet-delete-button').enable();
						}
						if(selModel.getCount()==1){
							var combo;
							var contents_tabs = Ext.getCmp('contents-tab-panel');
							if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
								combo = Ext.getCmp('bp3d-tree-group-combo');
							}else{
								combo = Ext.getCmp('anatomo-tree-group-combo');
							}
							if(combo.getValue()!=selModel.getSelected().get("tg_id")){
								try{Ext.getCmp('bp3d-pallet-home-button').enable();}catch(e){}
							}
						}
					}catch(e){
						_dump("5602:"+e);
					}
				},
				scope:this
			}
		}),
		store : bp3d_parts_store,
		listeners : {
			"keydown" : function(e){
				if(e.getKey()!=e.DELETE) return;
				var records = bp3s_parts_gridpanel.getSelectionModel().getSelections();
				if(records.length == 0) return;
				var store = bp3s_parts_gridpanel.getStore();
				for(var i=records.length-1;i>=0;i--){
					store.remove(records[i]);
				}
				var count = store.getCount();
				if(count == 0) store.removeAll();
				try{bp3s_parts_gridpanel.getSelectionModel().clearSelections();}catch(e){}
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
					_dump("5643:"+e);
				}
			},
			"resize" : function(grid,adjWidth,adjHeight,rawWidth,rawHeight){
				try{
					var panel = Ext.getCmp('control-tab-panel');
					var size = panel.getSize();
					if(!size.width || !size.height) return;
					resizeGridPanelColumns(grid);
				}catch(e){}
			},
			"render": function(grid){
				setEmptyGridText();
				try{
					var panel = Ext.getCmp('control-tab-panel');
					var size = panel.getSize();
					if(!size.width || !size.height) return;
					resizeGridPanelColumns(bp3s_parts_gridpanel);
				}catch(e){
					_dump("5662:"+e);
				}
				restoreHiddenGridPanelColumns(grid);

				try{var bp3s_parts_gridpanelDropTargetEl = bp3s_parts_gridpanel.getView().el.dom.childNodes[0].childNodes[1]}catch(e){}
				if(bp3s_parts_gridpanelDropTargetEl){
					var destGridDropTarget = new Ext.dd.DropTarget(bp3s_parts_gridpanelDropTargetEl, {
						ddGroup    : 'partlistDD',
						copy       : false,
						notifyDrop : function(ddSource, e, data){
							var rtn = false;
							if(!isAdditionPartsList()) return rtn;
HTML
if($useContentsTree eq 'true'){
}else{
	print <<HTML;
							if(ddSource.id=="bp3d-contents-dataview" || ddSource.id=="bp3d-contents-list-dataview"){
HTML
}
print <<HTML;
								function addRow(record, index, allItems) {
									var store = bp3s_parts_gridpanel.getStore();
									var foundItem = -1;
									if(store.getCount()>0){
										foundItem = store.find('b_id', new RegExp('^'+record.data.b_id+'\$'));
										if(foundItem>=0){
											var rec = store.getAt(foundItem);
											if(!rec || rec.data.tg_id!=record.data.tg_id) foundItem = -1;
										}
									}
									if(foundItem == -1){
										if(isNoneDataRecord(record)) return; //BP3Dに情報が無いものは追加しない

										var prm_record = ag_param_store.getAt(0);
										bp3s_parts_gridpanel.stopEditing();
										record.beginEdit();
										record.set('conv_id',record.data.b_id);
										if(Ext.isEmpty(record.data.def_color)){
											record.set('color','#'+(isPointDataRecord(record)?prm_record.data.point_color_rgb:prm_record.data.color_rgb));
										}else{
											record.set('color',record.data.def_color);
										}
										record.set('value','');
										record.set('zoom',true);
										record.set('exclude',false);
										record.set('opacity','1.0');
										record.set('representation','surface');
										record.set('point',false);
										record.dirty = false;
										record.endEdit();
										store.add(record);
										store.sort('name', 'ASC');
										rtn = true;
									}
								}
								Ext.each(ddSource.dragData.selections,addRow);
								delete ddSource.dragData.selections;

							}else if(ddSource.dragData && ddSource.dragData.node && ddSource.dragData.node.attributes && ddSource.dragData.node.attributes.f_id){
								var store = bp3s_parts_gridpanel.getStore();
								var foundItem = -1;
								if(store.getCount()>0){
									foundItem = store.find('b_id', new RegExp('^'+ddSource.dragData.node.attributes.attr.f_id+'\$'));
									if(foundItem>=0){
										var rec = store.getAt(foundItem);
										if(!rec || rec.data.tg_id!=ddSource.dragData.node.attributes.attr.tg_id) foundItem = -1;
									}
								}
								if(foundItem == -1){
									rtn = true;
									try{
										bp3s_parts_gridpanel.stopEditing();
										var drop_data = {f_ids:[ddSource.dragData.node.attributes.f_id]};
										drop_data.f_ids = Ext.util.JSON.encode(drop_data.f_ids);
										try{drop_data.version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){delete drop_data.version;}

										if(init_bp3d_params.version) drop_data.version = init_bp3d_params.version;
										if(init_bp3d_params.t_type) drop_data.t_type = init_bp3d_params.t_type;
										if(init_bp3d_params.tgi_id) drop_data.tgi_id = init_bp3d_params.tgi_id;
										if(init_bp3d_params.md_id) drop_data.md_id = init_bp3d_params.md_id;
										if(init_bp3d_params.mv_id) drop_data.mv_id = init_bp3d_params.mv_id;
										if(init_bp3d_params.mr_id) drop_data.mr_id = init_bp3d_params.mr_id;
										if(init_bp3d_params.bul_id) drop_data.bul_id = init_bp3d_params.bul_id;
										if(init_bp3d_params.cb_id) drop_data.cb_id = init_bp3d_params.cb_id;
										if(init_bp3d_params.ci_id) drop_data.ci_id = init_bp3d_params.ci_id;

										Ext.Ajax.request({
											url     : 'get-contents.cgi',
											method  : 'POST',
											params  : Ext.urlEncode(drop_data),
											success : function(conn,response,options){
												try{
													try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
													if(results && results.images && results.images.length>0){
														var prm_record = ag_param_store.getAt(0);
														var newRecord = Ext.data.Record.create(bp3d_parts_store_fields);
														var addrecs = [];
														for(var i=0;i<results.images.length;i++){
															var addrec = new newRecord({});
															addrec.beginEdit();
															for(var fcnt=0;fcnt<addrec.fields.items.length;fcnt++){
																var fname = addrec.fields.items[fcnt].name;
																var ftype = addrec.fields.items[fcnt].type;
																var fdefaultValue = addrec.fields.items[fcnt].defaultValue;
																if(Ext.isEmpty(results.images[i][fname])){
																	addrec.set(fname,fdefaultValue);
																}else{
																	addrec.set(fname,results.images[i][fname]);
																}
															}
															if((!addrec.data.b_id || addrec.data.b_id == "") && record.data.partslist[i].f_id) addrec.data.b_id = record.data.partslist[i].f_id;
															if((!addrec.data.entry || addrec.data.entry == "") && record.data.partslist[i].lastmod) addrec.data.entry = record.data.partslist[i].lastmod;
															if(addrec.data.entry.match(/^[0-9]+\$/)){
																addrec.data.entry = Date.parseDate(parseInt(addrec.data.entry), "U");
															}else if(addrec.data.entry.match(/^[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}T/)){
																if(addrec.data.entry.match(/^[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\$/)) addrec.data.entry+='Z';
																addrec.data.entry = Date.parseDate(addrec.data.entry, "c");
															}
															addrec.set('conv_id',addrec.data.b_id);
															addrec.set('color','#'+prm_record.data.color_rgb);
															addrec.set('value','');
															addrec.set('zoom',true);
															addrec.set('exclude',false);
															addrec.set('opacity','1.0');
															addrec.set('representation','surface');
															addrec.set('point',false);
															addrec.dirty = false;
															addrec.endEdit();
															store.add(addrec);
														}
													}
												}catch(e){}
											},
											failure : function(conn,response,options){
											}
										});
									}catch(e){
									}
								}
							}
							return rtn;
						}
					});
				}
			},
			scope:this
		},
		keys : {
			key: 'a',
			ctrl: true,
			stopEvent: true,
			handler: function() {
				bp3s_parts_gridpanel.getSelectionModel().selectAll();
			}
		}
	});
	bp3s_parts_gridpanel.getColumnModel().on({
		'hiddenchange' : function(column,columnIndex,hidden){
			resizeGridPanelColumns(bp3s_parts_gridpanel);
			saveHiddenGridPanelColumns(bp3s_parts_gridpanel);
		},
		scope: this,
		delay: 100
	});

	var control_tabs = new Ext.Panel({
		id        : 'control-tab-panel',
		region    : 'center',
		border    : false,
		layout    : 'card',
		activeItem : 0,
		deferredRender : true,
		frame     : false,
		items:[bp3s_parts_gridpanel],
		listeners: {
			'render': function(panel){
			},
			scope:this
		}
	});

	var bp3d_toolbox_panel = new Ext.Panel({
		id        : 'bp3d-toolbox-panel',
		region    : 'east',
		border    : false,
		bodyStyle : 'border-right-width:1px;',
		style     : 'padding:0px;',
		baseCls   : 'x-plain x-toolbar x-small-editor',
		width     : 28,
		minWidth  : 28,
		maxWidth  : 28,
		split     : false,
		header : true,
		tools  : [{
			id : 'down',
			handler : function(event, toolEl, panel){
				var cmp = Ext.getCmp('south-panel');
				if(cmp) cmp.toggleCollapse(true);
			}
		}],
		items : [
			{
				xtype : 'tbbutton',
				id : 'bp3d-pallet-select-button',
				tooltip : 'Select All',
				iconCls  : 'pallet_select',
				listeners : {
					'click' : {
						fn : function (button, e) {
							var grid = Ext.getCmp('control-tab-partslist-panel');
							if(grid && grid.rendered) grid.getSelectionModel().selectAll();
						},
						scope: this
					}
				}
			},
			{
				xtype : 'tbbutton',
				id : 'bp3d-pallet-unselect-button',
				tooltip : 'Unselect All',
				iconCls  : 'pallet_unselect',
				listeners : {
					'click' : {
						fn : function (button, e) {
							var grid = Ext.getCmp('control-tab-partslist-panel');
							if(grid && grid.rendered) grid.getSelectionModel().clearSelections();
						},
						scope: this
					}
				}
			},
			{
				xtype : 'tbbutton',
				id : 'bp3d-pallet-copy-button',
				tooltip   : get_ag_lang('COPY_TITLE')+' Selected',
				iconCls  : 'pallet_copy',
				disabled : true,
				listeners : {
					'click' : {
						fn : function (button, e) {
							var grid = Ext.getCmp('control-tab-partslist-panel');
							if(grid && grid.rendered){
								copyList(grid);
							}
						},
						scope: this
					}
				}
			},
			{
				xtype : 'tbbutton',
				id : 'bp3d-pallet-paste-button',
				tooltip   : get_ag_lang('PASTE_TITLE'),
				iconCls  : 'pallet_paste',
				listeners : {
					'click' : {
						fn : function (button, e) {
							var grid = Ext.getCmp('control-tab-partslist-panel');
							if(grid && grid.rendered){
								pasteList(grid);
							}
						},
						scope: this
					}
				}
			},
			{
				xtype : 'tbbutton',
				id : 'bp3d-pallet-delete-button',
				tooltip   : 'Delete Selected',
				iconCls  : 'pallet_delete',
				disabled : true,
				listeners : {
					'click' : {
						fn : function (button, e) {
							var grid = Ext.getCmp('control-tab-partslist-panel');
							if(grid && grid.rendered){
								var store = grid.getStore();
								var records = grid.getSelectionModel().getSelections();
								for(var i=records.length-1;i>=0;i--){
									store.remove(records[i]);
								}
							}
						},
						scope: this
					}
				}
			}
		],
		listeners : {
			show : function(panel){
				panel.doLayout();
			},
			afterlayout : function(panel,layout){
				afterLayout(panel);
			},
			render: function(comp){
				Ext.getCmp('contents-tab-panel').on({
					tabchange: {
						fn: function(tabpanel,tab){
							if(tab.id != 'contents-tab-bodyparts-panel') return;
							comp.setHeight(comp.initialConfig.width);
							comp.findParentByType('panel').doLayout();
						},
						buffer: 250
					}
				});
			},
			scope:this
		}
	});

	var south_panel = new Ext.Panel({
		id          : 'south-panel',
		region      : 'south',
		split       : true,
		height      : 150,
		minHeight   : 150,
		collapsible : true,
		border      : true,
		layout : 'border',
		items : [
			{
				id          : 'south-panel-west',
				region    : 'west',
				layout : 'border',
				width     : 76,
				minWidth  : 76,
				maxWidth  : 76,
				border    : false,
				items : [{
					id: 'south-panel-west-center',
					region: 'center',
					border: false,
					bodyStyle: 'background:transparent;border-right-width:1px;',
					html: '<img src="css/3.png" width=44 height=44>'
				},bp3d_toolbox_panel],
				listeners: {
					render: function(comp){
						Ext.getCmp('contents-tab-panel').on({
							tabchange: {
								fn: function(tabpanel,tab){
									if(tab.id != 'contents-tab-bodyparts-panel') return;
									comp.setWidth(comp.initialConfig.width);
									comp.findParentByType('panel').doLayout();
								},
								buffer: 250
							}
						});
					}
				}
			},
			control_tabs,
			{
				id       : 'goto-ag-panel',
				region   : 'east',
				html     : get_ag_lang('GOTO_AG'),
				border   : false,
				width    : get_ag_lang('GOTO_AG_WIDTH'),
				minWidth : get_ag_lang('GOTO_AG_WIDTH'),
				maxWidth : get_ag_lang('GOTO_AG_WIDTH'),
				style    : 'font-size:11px;padding:0;',
				bodyStyle: 'background:transparent;',
				split    : false,
				collapsible : false,
				collapseFirst : false,
				listeners : {
					'show' : function(panel){
						panel.doLayout();
					},
					'afterlayout' : function(panel,layout){
						afterLayout(panel);
					},
					render: function(comp){
						\$('a.goto-ag-btn').live('click',function(){
							Ext.getCmp('contents-tab-panel').activate(Ext.getCmp('contents-tab-anatomography-panel'));
							return false;
						});

						Ext.getCmp('contents-tab-panel').on({
							tabchange: {
								fn: function(tabpanel,tab){
									if(tab.id != 'contents-tab-bodyparts-panel') return;
									comp.setWidth(comp.initialConfig.width);
									comp.findParentByType('panel').doLayout();
								},
								buffer: 250
							}
						});

					},
					scope:this
				}
			}
		],
		listeners : {
			'show' : function(panel){
				panel.doLayout();
			},
			'afterlayout' : function(panel,layout){
HTML
if($moveLicensesPanel ne 'true'){
print <<HTML;
				afterLayout(Ext.getCmp('licenses-panel'));
HTML
}elsif($makeGotoAGButton eq 'true'){
print <<HTML;
				afterLayout(Ext.getCmp('goto-ag-panel'));
HTML
}
print <<HTML;
				afterLayout(panel);
			},
			scope:this
		}
	});

	var contents_tab_bodyparts_panel = new Ext.Panel({
		title  : get_ag_lang('TITLE_BP3D'),
HTML
print qq|		tabTip   : get_ag_lang('TABTIP_BP3D'),| if($useTabTip eq 'true');
print <<HTML;
		id     : 'contents-tab-bodyparts-panel',
		layout : 'border',
		items  : [navigate_panel,contents_panel,south_panel],
		listeners: {
			'show' : function(panel){
				panel.doLayout();
			},
			scope : this
		}
	});
HTML

if($informationHidden ne 'true'){
	if($useTwitter eq 'true'){
		print <<HTML;
	var contents_tab_information_panel = new Ext.TabPanel({
HTML
	}else{
		print <<HTML;
	var contents_tab_information_panel = new Ext.Panel({
HTML
	}
	print <<HTML;
		title      : get_ag_lang('TITLE_INFORMATION'),
HTML
	print qq|		tabTip   : get_ag_lang('TABTIP_INFORMATION'),| if($useTabTip eq 'true');
	print <<HTML;
		id         : 'contents-tab-information-panel',
HTML
	if($useTwitter eq 'true'){
	print <<HTML;
		activeTab: 0,
		items: [{
			title: 'Welcome to BodyParts3D',
			frame: true,
			bodyStyle: 'background-color:#fff;',
			autoScroll: true,
			autoLoad: {
				url: '$info_html',
				nocache: true
			}
		},{
			title: 'Tweet(#bp3d)',
			iconCls: 'btweet',
			html: '<iframe frameborder="0" height="100%" width="100%" src="$urlTwitterTimeline_bp3d"></iframe>'
		},{
			title: 'Tweet(#anagra)',
			iconCls: 'btweet',
			html: '<iframe frameborder="0" height="100%" width="100%" src="$urlTwitterTimeline_ag"></iframe>'
		}]
HTML
	}else{
		print <<HTML;
		frame      : true,
		bodyStyle  : 'background-color:#fff;border:1px solid #99bbe8;padding:10px;',
		autoScroll : true,
		autoLoad   : {
			url     : '$info_html',
			nocache : true
		}
HTML
	}
	print <<HTML;
	});
HTML
}
print <<HTML;
	var contents_tabs = new Ext.TabPanel({
//	var contents_tabs = new Ext.Panel({
//		layout:'card',
		id        : 'contents-tab-panel',
		region    : 'center',
		border    : true,
		tabPosition : 'top',
		frame     : false,
		layoutOnTabChange : true,
		deferredRender : true,
HTML
#if($rootVisible eq 'true'){
#	print qq|		activeTab : 1,\n|;
#}else{
	print qq|		activeTab : 0,\n|;
#}
print qq|		items : [|;
#print qq|contents_tab_home_panel,| if(defined $rootVisible && $rootVisible eq 'true');
print qq|contents_tab_bodyparts_panel,anatomography_panel|;
print qq|,contents_tab_feedback_panel| if($lsdb_Auth && $reviewHidden ne 'true');
print qq|,contents_tab_information_panel| if($informationHidden ne 'true');
print qq|],\n|;
print <<HTML;
		listeners: {
			"render" : function(tabpanel){
				var tabHomeDom = Ext.get('contents-tab-panel__contents-tab-home-panel');
				var tabBodypartsDom = Ext.get('contents-tab-panel__contents-tab-bodyparts-panel');
				if(tabBodypartsDom){
					tabBodypartsDom.on({
						'click' : function(){
							var tabBodypartsDom = Ext.get('contents-tab-panel__contents-tab-bodyparts-panel');
							if(!tabBodypartsDom.hasClass('x-tab-strip-active')){
								var tabHomeDom = Ext.get('contents-tab-panel__contents-tab-home-panel');
								tabHomeDom.removeClass('x-tab-strip-active');
								tabBodypartsDom.addClass('x-tab-strip-active');
								Ext.getCmp('header-panel').layout.setActiveItem(1);
								control_tabs.layout.activeItem.syncSize();
								control_tabs.layout.activeItem.fireEvent('resize',control_tabs.layout.activeItem);
							}
							var tree_panel = Ext.getCmp("navigate-tree-panel");
							var rootNode = tree_panel.getRootNode();
							var selNode = tree_panel.getSelectionModel().getSelectedNode();
							if(rootNode == selNode){
								var path = Cookies.get('ag_annotation.images.path','');
								if(path){
//_dump("4115:CALL selectPathCB()");
									var path = Cookies.get('ag_annotation.images.path','');
									tree_panel.selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
								}else{
									rootNode.expand(false,false,function(node){
//_dump("4118:CALL selectPathCB()");
									tree_panel.selectPath(rootNode.firstChild.getPath('f_id'),'f_id',selectPathCB);
									});
								}
							}
						},
						scope : this
					});
				}

			},
			"beforetabchange" : function(tabpanel,newTab,currentTab){

				if(newTab.id == 'contents-tab-home-panel'){
					contents_tab_prev = newTab;
					setTimeout(function(){ contents_tabs.setActiveTab('contents-tab-bodyparts-panel'); },0);
					var tabHomeDom = Ext.get('contents-tab-panel__contents-tab-home-panel');
					var tabBodypartsDom = Ext.get('contents-tab-panel__contents-tab-bodyparts-panel');
					if(tabHomeDom && tabBodypartsDom){
						tabHomeDom.addClass('x-tab-strip-active');
						tabBodypartsDom.removeClass('x-tab-strip-active');
					}
					return false;
				}else{
					if(contents_tab_prev && contents_tab_prev.id == 'contents-tab-home-panel'){

						Ext.getCmp('header-panel').layout.setActiveItem(0);

						var tree_panel = Ext.getCmp("navigate-tree-panel");
						var selNode = tree_panel.getSelectionModel().getSelectedNode();
						var rootNode = tree_panel.getRootNode();
						if(selNode != rootNode){
							tree_panel.getSelectionModel().select(rootNode);
//_dump("4150:CALL selectPathCB()");
							selectPathCB(true,rootNode);
						}

						if(newTab.id == 'contents-tab-bodyparts-panel' && newTab == currentTab) contents_tab_prev = null;
						Ext.getCmp('south-panel').hide();
					}else{
						var tabHomeDom = Ext.get('contents-tab-panel__contents-tab-home-panel');
						if(tabHomeDom && tabHomeDom.hasClass('x-tab-strip-active')) tabHomeDom.removeClass('x-tab-strip-active');
						if(newTab.id == 'contents-tab-bodyparts-panel'){
							Ext.getCmp('south-panel').show();
						}else{
							Ext.getCmp('south-panel').hide();
						}
					}
					setTimeout(function(){
						var viewport = Ext.getCmp('viewport');
						if(viewport && viewport.rendered) viewport.doLayout();
					},0);
				}
				return true;

			},
			'tabchange' : function(tabpanel,tab){

				var tab_id = tab.id;
				if(contents_tab_prev){
					tab_id = contents_tab_prev.id;
					contents_tab_prev = null;
				}

//_dump("contents_tabs.tabchange():tab_id=["+tab_id+"]");

				if(tab_id == 'contents-tab-anatomography-panel'){
					gDispAnatomographyPanel = true;
				}else if(tab_id == 'contents-tab-bodyparts-panel'){

					if(bp3d_parts_store.getCount()==0){
						gDispAnatomographyPanel = false;
						Ext.getCmp('bp3d-home-group-btn').disable();
					}
					try{
						control_tabs.layout.setActiveItem('control-tab-partslist-panel');
						control_tabs.layout.activeItem.fireEvent('resize',control_tabs.layout.activeItem);
					}catch(e){}

					var tree_panel = Ext.getCmp("navigate-tree-panel");
					var selNode = tree_panel.getSelectionModel().getSelectedNode();
					var rootNode = tree_panel.getRootNode();
					if(selNode == rootNode){
						rootNode.expand(false,false,function(){
//_dump("4255:CALL selectPathCB()");
							try{tree_panel.selectPath(rootNode.firstChild.getPath('f_id'),'f_id',selectPathCB);}catch(e){}
						});
					}

				}else if(tab_id == 'contents-tab-home-panel'){

					var tree_panel = Ext.getCmp("navigate-tree-panel");
					var selNode = tree_panel.getSelectionModel().getSelectedNode();
					var rootNode = tree_panel.getRootNode();
					if(selNode != rootNode){
						tree_panel.getSelectionModel().select(rootNode);
//_dump("4266:CALL selectPathCB()");
						selectPathCB(true,rootNode);
					}
					var tabHomeDom = Ext.get('contents-tab-panel__contents-tab-home-panel');
					var tabBodypartsDom = Ext.get('contents-tab-panel__contents-tab-bodyparts-panel');
					if(tabHomeDom && tabBodypartsDom){
						var classname = 'x-tab-strip-active';
						if(!tabHomeDom.hasClass(classname)) tabHomeDom.addClass(classname);
						if(tabBodypartsDom.hasClass(classname)) tabBodypartsDom.removeClass(classname);
					}
				}else{
				}


				if(tab_id == 'contents-tab-bodyparts-panel'){
					Ext.getCmp('header-panel').layout.setActiveItem(1);
				}else if(tab_id == 'contents-tab-anatomography-panel'){
					Ext.getCmp('header-panel').layout.setActiveItem(2);
					tabChange(tabpanel,tab);
				}else if(tab_id == 'contents-tab-feedback-panel'){
					Ext.getCmp('header-panel').layout.setActiveItem(3);
				}else if(tab_id == 'contents-tab-information-panel'){
					Ext.getCmp('header-panel').layout.setActiveItem(4);
				}else{
					Ext.getCmp('header-panel').layout.setActiveItem(0);
				}

				//keymapの有効・無効
				if(window.agKeyMap){
					if(tab_id == 'contents-tab-anatomography-panel'){
						window.agKeyMap.enable();
					}else{
						window.agKeyMap.disable();
					}
				}

			},
			'resize' : function(tabpanel,adjWidth,adjHeight,rawWidth,rawHeight){
				tabpanel.doLayout();
			},
			scope:this
		}
	});

	tbarBodypartsPrint = function(){
		var selRec = null;
		var oSelNode = null;
		var treeCmp = Ext.getCmp('navigate-tree-panel');
		if(treeCmp) oSelNode = treeCmp.getSelectionModel().getSelectedNode();
		if(oSelNode && oSelNode.id == 'root'){
			selRec = oSelNode.attributes.attr;
		}else{
			var dataview = getViewImages();
			if(!dataview) return;
			var selRecs = dataview.getSelectedRecords();
			if(selRecs && selRecs.length>0){
				selRec = selRecs[0].data;
			}else if(oSelNode){
				selRec = oSelNode.attributes.attr;
			}
		}

		var params = {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		};
		for(var key in selRec){
			params[key] = selRec[key];
		}

		w = window.open(
			"print-bp3d.cgi?" + Ext.urlEncode(params),
			"_blank",
			"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=300,height=350");
	};

	tbarBodypartsSendMail = function(){
		location.href = 'mailto:?body=' + encodeURIComponent(getBP3DLinkURL());
	};

	tbarBodypartsSendReview = function(){
		openWindowComment();
	};

	getBP3DLinkURL = function(){
		var selRec;
		var oSelNode = null;
		var treeCmp = Ext.getCmp('navigate-tree-panel');
		if(treeCmp) oSelNode = treeCmp.getSelectionModel().getSelectedNode();
		if(oSelNode && oSelNode.id == 'root'){
			selRec = oSelNode.attributes.attr;
		}else{
			var dataview = getViewImages();
			if(!dataview) return;
			var selRecs = dataview.getSelectedRecords();
			if(selRecs && selRecs.length>0){
				selRec = selRecs[0].data;
			}else if(oSelNode){
				selRec = oSelNode.attributes.attr;
			}
		}

		var param = 'i=';
		if(selRec.b_id){
			param += selRec.b_id;
		}else{
			param += selRec.f_id;
			try{var treeType = Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){treeType=undefined;}
			if(!Ext.isEmpty(treeType)){
				if(treeType == 1){
					param += '&t=Conventional';
				}else if(treeType == 3){
					param += '&t=is_a';
				}else if(treeType == 4){
					param += '&t=PartOf';
				}
			}
			if(oSelNode){
				if(oSelNode.id == 'search'){
					param += '&q=' + encodeURIComponent(oSelNode.text.replace(/^search:\\[(.+)?\\]/i,"\$1"));
				}else{
					param += '&p=' + oSelNode.getPath('f_id').replace(/^\\/root/,"");
				}
			}
			try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
			param += '&v=' + bp3d_version;

			var bp3d_tree_group_value = init_tree_group;
			var bp3d_tree_group = Ext.getCmp('bp3d-tree-group-combo');
			if(bp3d_tree_group && bp3d_tree_group.rendered) bp3d_tree_group_value = bp3d_tree_group.getValue();
			param += "&m=" + encodeURIComponent(tg2model[bp3d_tree_group_value].tg_model);
		}
		return '$app_path' + param;
	};

	tbarBodypartsLink = function(){

		Ext.Msg.show({
			title:'Link',
			buttons: Ext.Msg.OK,
			width : 400,
			modal : true,
			multiline : true,
			prompt : true,
			closable : true,
			value : getBP3DLinkURL()
		});
	};

	tbarAnatomoPrintRotatingImage = function(w,h){
		setTimeout(function(){
			var param = Ext.urlDecode(makeAnatomoPrm(),true);
			param.iw = w;
			param.ih = h;
			if(!Ext.isEmpty(param.ordg)) param.ordg = 0;
			var urlStr = cgipath.animation + '?' + Ext.urlEncode(param);
			window.open(urlStr, "_blank", "titlebar=no,toolbar=yes,status=no,menubar=yes");
		},100);
	};

	tbarAnatomoSendReview = function(){
		var comment_form = new Ext.form.FormPanel({
			baseCls : 'x-plain',
			labelWidth : 55,
			url : 'put-anatomo_comment.cgi',
			defaultType : 'textfield',
			items : [{
				xtype      : 'hidden',
				name       : 'parent',
				value      : '$FORM{parent}'
			},{
				xtype      : 'hidden',
				name       : 'fma_id',
				value      : getFMAID_CSVstr()
			},{
				xtype      : 'hidden',
				name       : 'tp_ap',
				value      : encodeURIComponent(makeAnatomoPrm())
			},{
				fieldLabel : 'Name',
				id         : 'comment_form_author',
				name       : 'author',
				anchor     : '100%',
				value      : '$user_name',
HTML
if(!$lsdb_OpenID){
print <<HTML;
				allowBlank : false,
HTML
}
print <<HTML;
				selectOnFocus : true
			},{
				fieldLabel : 'e-mail',
				id         : 'comment_form_email',
				name       : 'email',
				anchor     : '100%',
				selectOnFocus : true
			},{
				fieldLabel : 'Title',
				id         : 'comment_form_title',
				name       : 'title',
				anchor     : '100%',
				selectOnFocus : true
HTML
if(!$lsdb_OpenID){
print <<HTML;
			},{
				fieldLabel : 'Password',
				id         : 'comment_form_passwd',
				name       : 'passwd',
				anchor     : '50%',
				allowBlank : false,
				selectOnFocus : true
HTML
}
print <<HTML;
			},{
				xtype     : 'textarea',
				hideLabel : true,
				id        : 'comment_form_comment',
				name      : 'comment',
HTML
if($lsdb_OpenID){
print <<HTML;
				anchor    : '100% -76',
HTML
}else{
print <<HTML;
				anchor    : '100% -102',
HTML
}
print <<HTML;
				allowBlank : false,
				selectOnFocus : true
			}]
		});
		var comment_window = new Ext.Window({
			title       : get_ag_lang('COMMENT_WIN_TITLE'),
			width       : 500,
			height      : 300,
			minWidth    : 300,
			minHeight   : 250,
			layout      : 'fit',
			plain       : true,
			bodyStyle   :'padding:5px;',
			buttonAlign :'right',
			items       : comment_form,
			modal       : true,
			buttons : [{
				text    : get_ag_lang('COMMENT_WIN_TITLE_SEND'),
				handler : function(){
//												if(comment_form.getForm().isValid()){
//													comment_form.getForm().submit({
//														url     : 'put-anatomo_comment.cgi',
//														waitMsg : get_ag_lang('COMMENT_WIN_WAITMSG')+'...',
//														success : function(fp, o) {
//															comment_window.close();
//														}
//													});
//												}

					if(comment_form.getForm().isValid()){
						var tgi_version = "";
						var t_type = "";
						try{tgi_version=Ext.getCmp('anatomo-version-combo').getValue();}catch(e){}
						try{t_type=Ext.getCmp('bp3d-tree-type-combo-ag').getValue();}catch(e){}

//						var urlStr = 'put-anatomo_comment.cgi?tp_ap=';
						var urlStr = 'tp_ap=';
						urlStr = urlStr + encodeURIComponent(makeAnatomoPrm());
						urlStr = urlStr.replace(/\\|/g, "\@_\@_\@_\@_\@");
						urlStr = urlStr + '&fma_id=' + getFMAID_CSVstr();
						urlStr = urlStr + '&email=' + encodeURIComponent(comment_form.getComponent("comment_form_email").getValue());
						urlStr = urlStr + '&title=' + encodeURIComponent(comment_form.getComponent("comment_form_title").getValue());
						urlStr = urlStr + '&comment=' + encodeURIComponent(comment_form.getComponent("comment_form_comment").getValue());
						urlStr = urlStr + '&author=' + encodeURIComponent(comment_form.getComponent("comment_form_author").getValue());
						urlStr = urlStr + '&version=' + encodeURIComponent(tgi_version);
						urlStr = urlStr + '&type=' + encodeURIComponent(t_type);
						if(comment_form.getComponent("comment_form_passwd")){
							urlStr = urlStr + '&passwd=' + encodeURIComponent(comment_form.getComponent("comment_form_passwd").getValue());
						}
						urlStr = urlStr + '&parent=' + encodeURIComponent('$FORM{parent}');

						Ext.Ajax.request({
							url     : 'put-anatomo_comment.cgi',
							method  : 'POST',
							params  : makeAnatomoPrm(),
							success : function (response, options) {
								try{var results = Ext.util.JSON.decode(response.responseText);}catch(e){}
								if(!results) results = {success:false,msg:""};
								if(!results.msg) results.msg = "";
								if(results.success){
									var contentsPanel = Ext.getCmp('contents-tab-panel');
									contentsPanel.setActiveTab('contents-tab-feedback-panel');
									comment_window.close();
								}else{
									Ext.MessageBox.show({
										title   : get_ag_lang('COMMENT_TITLE_PLUS'),
										msg     : get_ag_lang('COMMENT_WIN_ERRMSG')+' [ '+results.msg+' ]',
										buttons : Ext.MessageBox.OK,
										icon    : Ext.MessageBox.ERROR
									});
								}
							},
							failure: function (response, options) {
//_dump("failure!!");
								Ext.MessageBox.show({
									title   : get_ag_lang('COMMENT_TITLE_PLUS'),
									msg     : get_ag_lang('COMMENT_WIN_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
					}
				}
			},{
				text: get_ag_lang('COMMENT_WIN_TITLE_CANCEL'),
				handler : function(){
					comment_window.close();
				}
			}]
		});
		comment_window.show();
	};

	var version_store = new Ext.data.JsonStore({
		url:'get-version.cgi',
		totalProperty : 'total',
		root: 'records',
		fields: [
			'tg_id',
			'tgi_id',
			'tgi_version',
			'tgi_renderer_version',
			'tgi_name',
			'tgi_comment',
			'tgi_objects_set',
			'tgi_tree_version',
			'tgi_part_of_relation',
			{name:'tgi_part_of_relation_bp3d',convert:function(v,rec){if(rec.tgi_tree_version.match(/inference/)){return ag_lang.PART_OF_RELATION_BP3D_MESSAGE}else{return ''}}},
			{name:'md_id',type:'int'},
			{name:'mv_id',type:'int'},
			{name:'mr_id',type:'int', defaultValue:1},
			{name:'ci_id',type:'int'},
			{name:'cb_id',type:'int'}
		],
		baseParams : {
			parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
			lng    : gParams.lng
		},
		listeners: {
			'beforeload' : function(self,options){
				self.baseParams = self.baseParams || {};
				delete self.baseParams.tg_id;
				try{self.baseParams.tg_id = Ext.getCmp('bp3d-tree-group-combo').getValue();}catch(e){}
				var cmp = Ext.getCmp('bp3d-version-combo');
				if(cmp && cmp.rendered) cmp.disable();
			},
			'load' : function(self,records,options){
				var cmp = Ext.getCmp('bp3d-version-combo');
				if(cmp && cmp.rendered){
					if(records.length>0){
						cmp.enable();
					}
				}
			},
			scope:this
		}
	});

	click_error_report_button = function(params){
		var src = 'api-error-twitter-store.cgi';
		window.open(
			src,
			"_blank",
			"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600"
		);
	};

	click_objfiles_list_button = function(params){
		var version = Ext.getCmp('bp3d-version-combo').getValue();
		var treeCombo = Ext.getCmp('bp3d-tree-type-combo');
		var treeStore = treeCombo.getStore();
		var idx = treeStore.find('t_type',new RegExp('^'+treeCombo.getValue()+'\$'),0,false,true);
		var rec = treeStore.getAt(idx);
		var tree = (rec ? rec.get('bul_abbr') : null);
		params = Ext.apply({},params||{},{version:version,tree:tree,cmd:'upload-all-list'});
		var src = 'get-info.cgi?'+Ext.urlEncode(params);
		window.open(
			src,
			"_blank",
			"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600"
		);
	};

	click_concept2objfiles_list_button = function(params){
		var version = Ext.getCmp('bp3d-version-combo').getValue();
		params = Ext.apply({},params||{},{version:version,cmd:'concept-objfiles-list'});
		var src = 'get-info.cgi?'+Ext.urlEncode(params);
//		window.open(
//			src,
//			"_blank",
//			"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600"
//		);

		window.location.href=src;

	};

	click_information_button = function(params){
		_dump(params);
		var contentsPanel = Ext.getCmp("contents-tab-panel");
		if(contentsPanel && contentsPanel.rendered){
			var cmp = Ext.getCmp('contents-tab-information-panel');
			if(Ext.isEmpty(cmp)){
				var src = get_ag_lang('INFORMATION_URL');
				if(!Ext.isEmpty(params)){
					if(params.hash){
						src += params.hash;
					}else if(params.url){
						src = params.url;
					}
				}
				_dump("src=["+src+"]");
				window.open(
					src,
					"_blank",
					"menubar=yes,titlebar=no,toolbar=yes,status=no,resizable=yes,dependent=yes,alwaysRaised=yes,scrollbars=yes,width=800,height=600"
				);

			}else{
				if(!Ext.isEmpty(params)){
					cmp.on({
						show: {
							fn:function(panel){
								if(panel.getXType()=='tabpanel'){
									panel.setActiveTab(0);
									var at = panel.getActiveTab();
									at.load({
										url: '$info_html',
										nocache: true,
										callback: function(el,success,response,options){
											if(!success) return;
											var src = \$(el.dom).find('iframe').attr('src');
											if(src){
												if(params.hash){
													src+=params.hash;
												}else if(params.url){
													src = params.url;
												}
												\$(el.dom).find('iframe').attr({src:src});
											}
										}
									});
								}else if(panel.getXType()=='panel'){
									panel.getLayout().setActiveItem(0);
									var at = panel.activeItem;
									at.load({
										url: '$info_html',
										nocache: true,
										callback: function(el,success,response,options){
											if(!success) return;
											var src = \$(el.dom).find('iframe').attr('src');
											if(src){
												if(params.hash){
													src+=params.hash;
												}else if(params.url){
													src = params.url;
												}
												\$(el.dom).find('iframe').attr({src:src});
											}
										}
									});
								}
							},
							buffer:250,
							single:true
						}
					});
				}


				if(contentsPanel.getXType()=='tabpanel'){
					contentsPanel.setActiveTab('contents-tab-information-panel');
				}else if(contentsPanel.getXType()=='panel'){
					contentsPanel.getLayout().setActiveItem('contents-tab-information-panel');
				}

				var cb = function(){
					var cmp = Ext.getCmp('contents-tab-information-panel');
					var body = \$(cmp.body.dom);
					var iframe = body.find('iframe');
					_dump(iframe);
					var src = body.find('iframe').attr('src');
					_dump("src=["+src+"]");
					if(src){
						if(src.indexOf('#')>0) src = src.substring(0,src.indexOf('#'));
						body.find('iframe').attr({src:src});
						if(params.hash){
							src+=params.hash;
						}else if(params.url){
							src = params.url;
						}
						_dump("src=["+src+"]");
						body.find('iframe').attr({src:src});
					}
				};
			}
		}
		return false;
	};

	click_open_url = function(window_title){
		var url = glb_anatomo_editor_url;
		var open_url_form = new Ext.form.FormPanel({
			plain       : true,
			border : false,
			labelAlign  : 'top',
			baseCls     : 'x-plain',
			defaults    : {
				selectOnFocus : true
			},
			items  : [{
				xtype      : 'textfield',
				id         : 'ag-open-url-window-form-url',
				name       : 'url',
				fieldLabel : 'http request',
				value      : url,
				allowBlank : false,
				anchor     : '100%'
			}]
		});

		var open_url_window = new Ext.Window({
			title       : window_title,
			width       : 500,
			height      : 120,
			minWidth    : 500,
			minHeight   : 120,
			layout      : 'fit',
			plain       : true,
			bodyStyle   :'padding:5px;',
			buttonAlign :'right',
			items       : open_url_form,
			modal       : true,
			buttons : [{
				text    : 'Open',
				handler : function(){
					if(open_url_form.getForm().isValid()){
						var url = Ext.getCmp('ag-open-url-window-form-url').getValue();
						url = url.replace(/\\r|\\n/g,"").trim();
						Ext.getDom('ag-open-url-form-url').value = url;
						Ext.getDom('ag-open-url-form').submit();
						open_url_window.close();
					}
				}
			},{
				text    : 'Cancel',
				handler : function(){
					open_url_window.close();
				}
			}],
			listeners : {
				"render" : function(win){
					if(Ext.isEmpty(win.loadMask) || typeof win.loadMask == 'boolean') win.loadMask = new Ext.LoadMask(win.body,{removeMask:false});
				},
				"show" : function(win){
					win.loadMask.show();
					Ext.Ajax.request({
						url     : 'get-convert-url.cgi',
						method  : 'POST',
						params  : Ext.urlEncode({url:url}),
						success : function(conn,response,options){
							win.loadMask.hide();
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
							if(Ext.isEmpty(results.data.url)){//shortURLに変換
								return;
							}
							Ext.getCmp('ag-open-url-window-form-url').setValue(results.data.url);
						},
						failure : function(conn,response,options){
							win.loadMask.hide();
							Ext.MessageBox.show({
								title   : window_title,
								msg     : get_ag_lang('CONVERT_URL_ERRMSG'),
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
						}
					});
				}
			}
		});
		open_url_window.show();
	};

	update_open_url2text = function(long_url,aCB){
		var transaction_id = Ext.Ajax.request({
			url     : 'get-convert-url.cgi',
			method  : 'POST',
			params  : Ext.urlEncode({url:long_url}),
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
					if(aCB) (aCB)(results.data.url);
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
		})
	};

	update_open_ShortURL2LongURL = function(short_url,aCB){
		var transaction_id = Ext.Ajax.request({
			url     : 'get-convert-url.cgi',
			method  : 'POST',
			params  : Ext.urlEncode({url:short_url}),
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
					if(aCB) (aCB)(results.data.url);
					return;
				}
				if(!Ext.isEmpty(results.data.expand)){//longURLに変換
					var long_url;
					if(Ext.isArray(results.data.expand)){
						long_url = results.data.expand[0].long_url;
					}else{
						long_url = results.data.expand.long_url;
					}
					if(aCB) (aCB)(long_url);
					return;
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
		})
	};

	click_open_url2text = function(window_title){

		var cur_text = URI2Text(glb_anatomo_editor_url,{target:{pins:false}});
		var cur_url = Text2URI(cur_text,{target:{pins:false}});
		var convOpts = {
			pin: {
				url_prefix : cur_url+encodeURIComponent('&')
			}
		};

		var text_value = URI2Text(glb_anatomo_editor_url,convOpts);
		if(Ext.isEmpty(text_value)) return;

		var anatomo_url_window = new Ext.Window({
			title       : window_title,
			width       : 600,
			height      : 500,
			layout      : 'form',
			plain       : true,
			bodyStyle   : 'padding:5px;text-align:right;',
			buttonAlign : 'center',
			modal       : true,
			resizable   : true,
			labelAlign  : 'top',
			labelWidth  : 65,
			items       : [
			{
				xtype         : 'textarea',
				id            : 'ag_url_textarea',
				hideLabel     : true,
				anchor        : '100%',
				height        : 100,
				selectOnFocus : false,
				value         : glb_anatomo_editor_url
			},
			{
				layout:'table',
				border: false,
				width: '100%',
				bodyStyle: 'background-color: transparent;',
				layoutConfig: {
					columns: 2
				},
				items:[{
					xtype: 'button',
					text: 'URL to Table',
					handler: function(){
//						var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").replace(/\\n\$/g,"").split("\\n");
//						for(var i=0;i<url_arr.length;i++){
//							var rtnstr = URI2Text(url_arr[i],convOpts);
//							if(Ext.isEmpty(rtnstr)) continue;
//							Ext.getCmp('ag_url_editor').setValue(rtnstr);
//							break;
//						}

						var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").replace(/\\n\$/g,"").split("\\n");
						for(var i=0;i<url_arr.length;i++){
							url_arr[i] = url_arr[i].trim();
							if(Ext.isEmpty(url_arr[i])) continue;
							var idx = url_arr[i].indexOf("?");
							if(idx<0) continue;
							var search = url_arr[i].substr(idx+1);
							if(Ext.isEmpty(search)) continue;
							var params = Ext.urlDecode(search);
							if(params.shorten){
								update_open_ShortURL2LongURL(url_arr[i],function(long_url){
									var rtnstr = URI2Text(long_url,convOpts);
									if(Ext.isEmpty(rtnstr)) return;
									Ext.getCmp('ag_url_editor').setValue(rtnstr);
								});
								break;
							}else{
								var rtnstr = URI2Text(url_arr[i],convOpts);
								if(Ext.isEmpty(rtnstr)) continue;
								Ext.getCmp('ag_url_editor').setValue(rtnstr);
								break;
							}
						}

					}
				},{
					xtype: 'button',
					text: 'Open this URL',
					handler: function(){
						var url_arr = Ext.getCmp('ag_url_textarea').getValue().replace(/0x0d0x0a|0x0d|0x0a|\\r\\n/g,"\\n").replace(/\\n\$/g,"").split("\\n");
						for(var i=0;i<url_arr.length;i++){
							var rtnstr = url_arr[i];
							rtnstr = rtnstr.replace(/\\r|\\n/g,"").trim();
							if(Ext.isEmpty(rtnstr)) continue;
							Ext.getDom('ag-open-url-form-url').value = rtnstr;
							Ext.getDom('ag-open-url-form').submit();
							break;
						}
					}
				}],
				listeners: {
					render: {
						fn: function(comp){
							_dump("render():["+comp.id+"]");
							var table = \$(comp.body.dom).children('table.x-table-layout');
							_dump(table);
							table.css({width:'100%'}).find('td.x-table-layout-cell:eq(1)').attr({align:'right'});
						},
						buffer: 250
					}
				}
			},
			{
				xtype     : 'textarea',
				id        : 'ag_url_editor',
				style     : 'font-family:Courier;monospace;',
				hideLabel : true,
				value     : text_value,
				anchor    : '100% -170'
			},
			{
				xtype    : 'button',
				text     : 'Table to URL',
				disabled : false,
				handler : function(){
					var rtnstr = Text2URI(Ext.getCmp('ag_url_editor').getValue());
					Ext.getCmp('ag_url_textarea').setValue(rtnstr);
					update_open_url2text(rtnstr,function(url){
						Ext.getCmp('ag_url_textarea').setValue(url);
					});
				}
			}
			],
			buttons : [{
				text    : 'Close',
				handler : function(){
					anatomo_url_window.close();
				}
			}],
			listeners: {
				render: function(){
					var long_url = Ext.getCmp('ag_url_textarea').getValue();
					update_open_url2text(long_url,function(url){
						Ext.getCmp('ag_url_textarea').setValue(url);
					});
				}
			}
		});
		anatomo_url_window.show();
	};

	var viewport = new Ext.Viewport({
		renderTo : Ext.getBody(),
		id       : 'viewport',
		layout   : 'border',
		items    : [
		{
			id       : 'header-panel',
			region   : 'north',
			split    : false,
			border   : false,
			frame    : false,
//			height   : 25,
//			height   : 125,
//			height   : 50,
			height   : 52,
			layout   : 'card',
			activeItem : 3,
			items    : [
			{
			},
			{
				border: false,
				bodyStyle: 'height:25px;',
				html: '$LOCALE{BP3D_TITLE_HTML}',
				listeners: {
					afterlayout: function(comp){
						\$(comp.body.dom).css({height:25});
					},
					render : function(comp){
						\$(comp.body.dom).css({height:25});
					},
					resize : function(comp){
						\$(comp.body.dom).css({height:25});
					}
				},
				bbar:[
//					'<label style="color:#15428b;font-size:16px;font-weight:bold;">BodyParts3D</label>',
//					'-',

					new Ext.form.ComboBox ({
						ctCls : 'x-small-editor',
						id : 'bp3d-tree-group-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'tg_name',
						valueField: 'tg_id',
						width: 125,
						triggerAction: 'all',
						value: init_tree_group,
						hidden : $groupHidden,
						store: new Ext.data.SimpleStore({
							fields: ['tg_id','tg_name'],
							data : $tree_group
						}),
						listeners: {
							'select' : function(combo, record, index) {
//								_dump("select():["+combo.id+"]["+combo.getValue()+"]");
								var cmp = Ext.getCmp('anatomo-tree-group-combo');
								if(cmp && cmp.rendered){
									cmp.setValue(record.data.tg_id);
								}else{
//									init_tree_group = record.data.tg_id;
								}
								Cookies.set('ag_annotation.images.tg_id',record.data.tg_id);

								var cmp = Ext.getCmp('bp3d-version-combo');
								if(cmp && cmp.rendered){
									cmp.getStore().reload({
										callback:function(records,options,success){
//_dump("1callback!!!!!!!");
											try{
												_updateAnatomo();

												var index = -1;
												var c_version_str = Cookies.get('ag_annotation.images.version');
//_dump("1callback!!!!!!!:c_version_str=["+c_version_str+"]");
												if(c_version_str){
													var c_version = Ext.util.JSON.decode(c_version_str);
													var tg_id = null;
													var cmp = Ext.getCmp('bp3d-tree-group-combo');
													if(cmp && cmp.rendered) tg_id = cmp.getValue();

//_dump("1callback!!!!!!!:tg_id=["+tg_id+"]");
//_dump("1callback!!!!!!!:c_version=["+c_version+"]["+(c_version?c_version[tg_id]:null)+"]");

													if(tg_id && c_version && c_version[tg_id]){
														var cmp = Ext.getCmp('bp3d-version-combo');
														var store = cmp.getStore();
														index = store.find('tgi_version', new RegExp('^'+c_version[tg_id]+'\$'));
														if(index>=0){
															var record = store.getAt(index);
															cmp.setValue(record.data.tgi_version);
															cmp.fireEvent('select',cmp,record,index);
														}
													}
												}
//_dump("1callback!!!!!!!:index=["+index+"]");
												if(index<0){
													index = 0;
													var cmp = Ext.getCmp('bp3d-version-combo');
													var store = cmp.getStore();
													var record = store.getAt(index);
													cmp.setValue(record.data.tgi_version);
													cmp.fireEvent('select',cmp,record,index);
												}


//												var cmp = Ext.getCmp('control-tab-partslist-panel');
//												if(cmp && cmp.rendered){
//													try{
//														var store = cmp.getStore();
//														var records = store.getRange();
//														getConvertIdList(records,store);
//													}catch(e){
//														_dump("cmp.getStore().loadData([],true);"+e);
//													}
//												}

											}catch(e){
												_dump("6424:"+e);
												for(var i in e){
													_dump(i+"="+e[i]);
												}
											}
										}
									});
								}
								var cmp = Ext.getCmp('control-tab-partslist-panel');
								if(cmp && cmp.rendered){
									try{
										var store = cmp.getStore();
										var records = store.getRange();
										store.removeAll();
										try{clearConvertIdList(records);}catch(e){}
										store.add(records);
									}catch(e){
										_dump("cmp.getStore().loadData([],true);"+e);
									}
								}

								var btn = Ext.getCmp('bp3d-home-group-btn');
								var store = bp3s_parts_gridpanel.getStore();

//								var count = store.query('tg_id', new RegExp('^'+record.data.tg_id+'\$'));
//_dump("1callback!!!!!!!:store=["+store.getCount()+"]");
//_dump("1callback!!!!!!!:count=["+count.getCount()+"]");
//								if(store.getCount()>0 && store.getCount()>count.getCount()){

								if(store.getCount()>0 && store.find('tg_id', new RegExp('^'+record.data.tg_id+'\$')) == -1){
									btn.enable();
									btn.el.dom.setAttribute('tg_id',store.getAt(0).data.tg_id);
								}else{
									btn.disable();
								}

							},
							'render' : function(combo) {
//								_dump("render():["+combo.id+"]["+combo.getValue()+"]");
							},
							scope:this
						}
					}),

					{
						id        : 'bp3d-home-group-btn',
						iconCls   : 'home',
						disabled  : true,
						hidden    : $groupHidden,
						listeners : {
							'click' : function(button,e){
								try{
									var tg_id = button.el.dom.getAttribute('tg_id');
									var combo;
									if(contents_tabs.getActiveTab().id == 'contents-tab-bodyparts-panel'){
										combo = Ext.getCmp('bp3d-tree-group-combo');
									}else{
										combo = Ext.getCmp('anatomo-tree-group-combo');
									}
									var store = combo.getStore();
									var index = store.find('tg_id', new RegExp('^'+tg_id+'\$'));
									combo.setValue(tg_id);
									combo.fireEvent('select',combo,store.getAt(index),index);

								}catch(e){
									_dump("6484:"+e);
								}
							},
							'disable' : function(button){
								try{Ext.getCmp('ag-home-group-btn').disable();}catch(e){}
								try{button.el.dom.removeAttribute('tg_id');}catch(e){}

								try{Ext.getCmp('anatomo_comment_pick_depth').enable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_edit').enable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_up').enable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_down').enable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_delete').enable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_addurl').enable();}catch(e){}
								try{Ext.getCmp('anatomo_pin_description_draw_check').enable();}catch(e){}
								try{Ext.getCmp('anatomo_pin_shape_combo').enable();}catch(e){}

								var cmp = Ext.getCmp('anatomography-pin-grid-panel');
								if(cmp && cmp.rendered){
									try{
										var store = cmp.getStore();
										var records = store.getRange();
										if(records.length>0){
											store.removeAll();
											store.add(records);
										}
									}catch(e){}
								}

								try{Ext.getCmp('anatomography_image_comment_title').enable();}catch(e){}
								try{Ext.getCmp('anatomography_image_comment_legend').enable();}catch(e){}
								try{Ext.getCmp('anatomography_image_comment_author').enable();}catch(e){}
								try{Ext.getCmp('anatomography_image_comment_draw_check').enable();}catch(e){}

							},
							'enable' : function(button){
								try{Ext.getCmp('ag-home-group-btn').enable();}catch(e){}

								try{Ext.getCmp('anatomo_comment_pick_depth').disable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_edit').disable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_up').disable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_down').disable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_delete').disable();}catch(e){}
								try{Ext.getCmp('anatomo_comment_pick_addurl').disable();}catch(e){}
								try{Ext.getCmp('anatomo_pin_description_draw_check').disable();}catch(e){}
								try{Ext.getCmp('anatomo_pin_shape_combo').disable();}catch(e){}

								var cmp = Ext.getCmp('anatomography-pin-grid-panel');
								if(cmp && cmp.rendered){
									try{
										var store = cmp.getStore();
										var records = store.getRange();
										if(records.length>0){
											store.removeAll();
											store.add(records);
										}
									}catch(e){}
								}

								try{Ext.getCmp('anatomography_image_comment_title').disable();}catch(e){}
								try{Ext.getCmp('anatomography_image_comment_legend').disable();}catch(e){}
								try{Ext.getCmp('anatomography_image_comment_author').disable();}catch(e){}
								try{Ext.getCmp('anatomography_image_comment_draw_check').disable();}catch(e){}
							},
							scope : this
						}
					},
HTML
if($groupHidden ne 'true'){
	print qq|					'-',\n|;
}
print <<HTML;
					'<label style="font-size:14px;font-weight:bold;">'+ ag_lang.DATA_VERSION +'&nbsp;</label>',

					new Ext.form.ComboBox ({
						ctCls : 'x-small-editor',
						id : 'bp3d-version-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'tgi_name',
						valueField: 'tgi_version',
						width: 80,
						triggerAction: 'all',
						hidden : false,
						store : version_store,
						listWidth: 750,
						tpl: versionListTpl,
						listeners: {
							'select' : {
								fn : function(combo, record, index) {
									if(index>0){
										\$('label#bp3-version-msg').show();
										\$('label#ag-version-msg').show();
									}else{
										\$('label#bp3-version-msg').hide();
										\$('label#ag-version-msg').hide();
									}
									if(Ext.isEmpty(record.data.tgi_comment)){
										\$('label#bp3-version-comment').html('').hide();
										\$('label#ag-version-comment').html('').hide();
									}else{
										\$('label#bp3-version-comment').html(record.data.tgi_comment).show();
										\$('label#ag-version-comment').html(record.data.tgi_comment).show();
									}
//									_dump("select():["+combo.id+"]["+combo.getValue()+"]");
									Cookies.set('ag_annotation.images.md_id',record.data.md_id);
									Cookies.set('ag_annotation.images.mv_id',record.data.mv_id);
									Cookies.set('ag_annotation.images.mr_id',record.data.mr_id);
									Cookies.set('ag_annotation.images.ci_id',record.data.ci_id);
									Cookies.set('ag_annotation.images.cb_id',record.data.cb_id);

									init_bp3d_params.md_id = record.data.md_id;
									init_bp3d_params.mv_id = record.data.mv_id;
									init_bp3d_params.mr_id = record.data.mr_id;
									init_bp3d_params.ci_id = record.data.ci_id;
									init_bp3d_params.cb_id = record.data.cb_id;
									init_bp3d_params.version = combo.getValue();

									var cmp = Ext.getCmp('anatomo-version-combo');
									if(cmp && cmp.rendered){
										cmp.setValue(record.data.tgi_version);
									}else{
										init_bp3d_version = record.data.tgi_version;
									}
									var checked = false;
									try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
									if(!checked){
										_updateAnatomo();
									}else{
										var cmp = Ext.getCmp('anatomo-clip-predifined-plane')
										if(cmp && cmp.rendered){
											if(!cmp.fireEvent('select',cmp)) _updateAnatomo();
										}else{
											_updateAnatomo();
										}
									}

									var c_version_str = Cookies.get('ag_annotation.images.version');
									var c_version;
									if(c_version_str) c_version = Ext.util.JSON.decode(c_version_str);
									c_version = c_version || {};
									c_version[record.data.tg_id] = record.data.tgi_version;
									c_version_str = Ext.util.JSON.encode(c_version);
									Cookies.set('ag_annotation.images.version',c_version_str);

									var cmp = Ext.getCmp('bp3d-tree-type-combo');
									if(cmp && cmp.rendered){
										cmp.getStore().reload({callback:function(records,options,success){
											if(Ext.isEmpty(gParams.t_type)) return;
											var cmp = Ext.getCmp('bp3d-tree-type-combo');
											Ext.each(records,function(r,i,a){
												if(r.data.t_type!=gParams.t_type) return true;
												cmp.setValue(gParams.t_type);
												cmp.fireEvent('select',cmp,r,i);
												return false;
											})
											delete gParams.t_type;
										}});
									}

//_dump(navigate_grid.ds);
//									for(var key in navigate_grid.ds.baseParams){
//										if(key.match(/_id\$/) && navigate_grid.ds.baseParams[key] != init_bp3d_params[key]){
//											navigate_grid.ds.reload();
//											break;
//										}
//									}

									try{Ext.getCmp('anatomography-bp3d-grid-panel').getStore().reload();}catch(e){}
									var cmp = Ext.getCmp('anatomo-tree-type-combo')
									if(cmp && cmp.rendered){
										cmp.getStore().reload();
									}

												var cmp = Ext.getCmp('control-tab-partslist-panel');
												if(cmp && cmp.rendered){
													try{
														var store = cmp.getStore();
														var records = store.getRange();
//_dump("bp3d-version-combo.select():records=["+records.length+"]");
														getConvertIdList(records,store);
													}catch(e){
														_dump("cmp.getStore().loadData([],true);"+e);
													}
												}
								},
								scope : this
							},
							'render' : {
								fn : function(combo) {
//									_dump("render():["+combo.id+"]["+combo.getValue()+"]");
									setTimeout(function(){
										new Ext.ToolTip({
											target: 'bp3-version-information',
											html: get_ag_lang('VERSION_INFORMATION'),
											autoHide: false,
											closable: true,
											mouseOffset: [1,1],
											width: 500,
											showDelay: 2000,
											listeners: {
												show: function(toolTip){
													console.log('show()');
													console.log(toolTip);
//													toolTip.autoHide = false;
												},
												hide: function(toolTip){
													console.log('hide()');
													console.log(toolTip);
												}
											}
										});
									},1000);
									var cmp = Ext.getCmp('bp3d-tree-group-combo');
									if(cmp && cmp.rendered){
										var value = cmp.getValue();
										var store = cmp.getStore();
										var index = store.find('tg_id', new RegExp('^'+value+'\$'));
										if(index>=0){
											var record = store.getAt(index);
											cmp.fireEvent('select',cmp,record,index);

											if(Ext.isEmpty(gParams.version)) return;

											combo.getStore().on({
												load: {
													fn: function(store,records){
//														_dump("render():load():["+combo.id+"]["+combo.getValue()+"]["+gParams.version+"]");
														Ext.each(records,function(r,i,a){
//															_dump("render():load():["+i+"]["+r.data.tgi_renderer_version+"]");
															if(r.data.tgi_renderer_version!=gParams.version) return true;
															combo.setValue(r.data.tgi_version);
															combo.fireEvent('select',combo,r,i);
															delete gParams.version;
															return false;
														});
													},
													buffer:100,
													single: true
												}
											})
										}
									}
								},
								scope:this
							}
						}
					}),

					'<label id="bp3-version-comment" style="'+get_ag_lang('VERSION_COMMENT_STYLE')+'"></label>',
					'<label id="bp3-version-information" style="'+get_ag_lang('VERSION_INFORMATION_STYLE')+'">'+Ext.util.Format.ellipsis(get_ag_lang('VERSION_INFORMATION'),50)+'</label>',
					'<label id="bp3-version-msg" style="'+get_ag_lang('NOT_LATEST_VERSION_STYLE')+'">'+get_ag_lang('NOT_LATEST_VERSION')+'</label>',


					'-',
//					get_ag_lang('TREE_TYPE_HTML'),
////					{
////						id    : 'treeType_label',
////						xtype : 'tbtext',
////						text  : 'build-up logic :'
////					},
					{
						hidden: true,
						id: 'bp3d-tree-type-combo',
						xtype: 'combo',
						typeAhead: true,
						triggerAction: 'all',
						width: 110,
						editable: false,
						mode: 'local',
						lazyInit: false,
						disabled : true,
						readOnly: true,
						validator: function(value){
//							_dump("validator():value=["+value+"]");
							return true;
						},
						displayField: 't_name',
						valueField: 't_type',
						store : navigate_tree_type_store,
						listeners: {
							'select': function(combo,record,index){
//								_dump("select():["+combo.id+"]["+combo.getValue()+"]");

								try{var version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){version = null;}
								if(!version) return;

								Cookies.set('ag_annotation.images.ci_id',record.data.ci_id);
								Cookies.set('ag_annotation.images.cb_id',record.data.cb_id);
								Cookies.set('ag_annotation.images.bul_id',record.data.bul_id);
								Cookies.set('ag_annotation.images.bul_name',record.data.ci_name+' '+record.data.cb_name+' '+record.data.bul_name);
								Cookies.set('ag_annotation.images.butc_num',record.data.butc_num);

								init_bp3d_params.ci_id = record.data.ci_id;
								init_bp3d_params.cb_id = record.data.cb_id;
								init_bp3d_params.bul_id = record.data.bul_id;

//Ext.get('bp3d-buildup-logic-contents-label').update(combo.getValue()==3 ? 'IS-A Tree of FMA3.0' : 'HAS-PART Tree of FMA3.0');
Ext.get('navigate-north-buildup').update('<a href="'+get_ag_lang('FMA_DESCRIPTION_URL')+'" target=_blank>'+record.data.ci_name+'</a>'+get_ag_lang('FMA_INFORMATION')+'&nbsp;'+record.data.cb_name+'&nbsp;'+record.data.bul_name);

								Cookies.set('ag_annotation.images.type',combo.getValue());
								var types_str = Cookies.get('ag_annotation.images.types');
								var types;
								if(types_str){
									types = Ext.util.JSON.decode(types_str);
								}else{
									types = {};
								}
								types[version] = combo.getValue();
								Cookies.set('ag_annotation.images.types',Ext.util.JSON.encode(types));

								var activeTab = Ext.getCmp('navigate-tab-panel').getActiveTab();
								if(activeTab.id == 'navigate-tree-panel'){
									var treeCmp = activeTab;
									if(!treeCmp || !treeCmp.root) return;

									treeCmp.root.reload(
										function(node){
											if(!Ext.isEmpty(gBP3D_TPAP) && node.firstChild && node.firstChild.attributes.attr.f_id){
												gBP3D_TPAP = undefined;
												Cookies.set('ag_annotation.images.path','/'+node.firstChild.attributes.attr.f_id);
											}
											var path = Cookies.get('ag_annotation.images.path','');
											node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',function(bSuccess,oSelNode){
												if(bSuccess){
													selectPathCB(bSuccess,oSelNode);
												}else if(node.firstChild){
													Cookies.set('ag_annotation.images.path','/'+node.firstChild.attributes.attr.f_id);
													var path = Cookies.get('ag_annotation.images.path','');
													node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id',selectPathCB);
												}
											});
										}
									);
								}else if(activeTab.id == 'navigate-grid-panel'){
//									activeTab.getStore().load();
//									Ext.getCmp('navigate-grid-paging-toolbar').changePage(1);
//									getViewImages().getStore().reload();

									activeTab.getBottomToolbar().changePage(1);
//									getViewImages().getStore().reload();

								}else if(activeTab.id == 'navigate-position-panel'){
									get_ajax_zrange_object_position_task.delay(250);
								}else if(activeTab.id == 'navigate-range-panel'){
//									_dump("select():["+combo.id+"]:CALL get_ajax_zrange_object_range_task3()");
//									get_ajax_zrange_object_range_task3.delay(250);
									get_ajax_zrange_object_range_task3.delay(0);
								}else{
									activeTab.getBottomToolbar().changePage(1);
								}
								var cmp = Ext.getCmp('bp3d-tree-type-combo-ag');
								if(cmp && cmp.rendered){
									cmp.setValue(record.data.t_type);
								}
							},
							'render': function(combo){
//								_dump("render():["+combo.id+"]["+combo.getValue()+"]");
							},
							valid: function(combo){
//								_dump("valid():["+combo.id+"]");
							},
							invalid: function(combo){
//								_dump("invalid():["+combo.id+"]");
							},
							scope:this
						}
					},


					'->',

					'-',
					'<label>Concept name or ID : </label>',
					' ',
//					new Ext.app.SearchField({
					new Ext.app.SearchFieldListeners({
						id: 'bp3d-search-field',
						width : 200,
						value : Ext.isEmpty(gParams.query)?'':gParams.query,
						listeners: {
							'render' : function(comp){
								try{
									if(Ext.isEmpty(gParams.query)) return;
									comp.setRawValue(gParams.query);
									comp.onTrigger2Click();
								}catch(e){
									_dump("render():"+e);
								}
							},
							'search' : function(field,query){
								try{
									query = query.replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,"&");
									query = query.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
									var tabCmp = Ext.getCmp('navigate-tab-panel');
									var tabpanel = createSearchGridPanel(query);
									if(tabpanel) tabCmp.setActiveTab(tabCmp.add(tabpanel));
								}catch(e){
									_dump("tabpanel=["+e+"]");
								}
							},
							scope : this
						}
					}),
					'-',{
						cls: 'ag-toolbar-button-cls',
						overCls: 'ag-toolbar-button-overCls',
						text: get_ag_lang('BUTTON_OBJFILE_LIST'),
						handler: function(){click_objfiles_list_button({title:this.text});}
					},'-',{
						cls: 'ag-toolbar-button-cls',
						overCls: 'ag-toolbar-button-overCls',
						text: get_ag_lang('BUTTON_FMA2OBJFILE_LIST'),
						handler: function(){click_concept2objfiles_list_button({title:this.text});}
					},'-',{
						text:get_ag_lang('BUTTON_INFORMATION'),
						handler : function(){click_information_button();}
//					},
//					'-',{
//						text:get_ag_lang('BUTTON_ERROR_REPORT'),
//						handler : function(){click_error_report_button();}
					}
HTML
if($localeMenuHidden ne 'true'){
	print <<HTML;
					,'-',{
						text    : '$locale_label',
						icon    : '$locale_icon',
						cls     : '$locale_cls',
						handler : function(){
							var chage_locale = "$FORM{lng}".toLowerCase();
							var path = location.pathname;
HTML
if($defaultLocaleJa ne 'true'){
	print <<HTML;
							if(chage_locale=='en'){
								location.href = path + "?lng=ja";
							}else{
								location.href = path;
							}
HTML
}else{
	print <<HTML;
							if(chage_locale=='en'){
								Cookies.set('ag_annotation.locale','ja');
							}else{
								Cookies.set('ag_annotation.locale','en');
							}
							location.href = path;
HTML
}
print <<HTML;
						}
					}
HTML
}
print <<HTML;
//					,'-',{
//						text    : '$login_label',
//						icon    : 'css/openid-bg.gif',
//						cls     : 'x-btn-text-icon',
//						handler : $login_func
//					}
				]
			},
			{
				border: false,
				bodyStyle: 'height:25px;',
				html: '$LOCALE{BP3D_TITLE_HTML}',
				listeners: {
					afterlayout: function(comp){
						\$(comp.body.dom).css({height:25});
					},
					render : function(comp){
						\$(comp.body.dom).css({height:25});
					},
					resize : function(comp){
						\$(comp.body.dom).css({height:25});
					}
				},
				bbar:[
//					'<label style="color:#15428b;font-size:16px;font-weight:bold;">BodyParts3D</label>',
//					'-',

					new Ext.form.ComboBox ({
						ctCls : 'x-small-editor',
						id : 'anatomo-tree-group-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'tg_name',
						valueField: 'tg_id',
						width: 125,
						triggerAction: 'all',
						value: init_tree_group,
						hidden : $groupHidden,
						store: new Ext.data.SimpleStore({
							fields: ['tg_id','tg_name'],
							data : $tree_group
						}),
						listeners: {
							'select' : function(combo, record, index) {
//_dump("anatomo-tree-group-combo.select()=["+record.data.tg_id+"]");
								var cmp = Ext.getCmp('bp3d-tree-group-combo');
								if(cmp && cmp.rendered){
									cmp.setValue(record.data.tg_id);
									var store = cmp.getStore();
									var index = store.find('tg_id',new RegExp('^'+record.data.tg_id+'\$'));
									var rec = store.getAt(index);
									cmp.fireEvent('select',cmp,rec,index);
								}
							},
							'render' : function(combo) {
							},
							scope:this
						}
					}),

					{
						id        : 'ag-home-group-btn',
						iconCls   : 'home',
						disabled  : true,
						hidden    : $groupHidden,
						listeners : {
							'click' : function(button,e){
								var btn = Ext.getCmp('bp3d-home-group-btn');
								btn.fireEvent('click',btn,e);
							},
							'disable' : function(button){
							},
							'enable' : function(button){
							},
							scope : this
						}
					},
HTML
if($groupHidden ne 'true'){
	print qq|					'-',\n|;
}
if($coordinateSystemHidden ne 'true'){
	print qq|					'<label>'+get_ag_lang('COORDINATE_SYSTEM')+' :</label>',\n|;
}
print <<HTML;
					{
						id: 'ag-coordinate-system-combo',
						xtype: 'combo',
						hidden : $coordinateSystemHidden,
						typeAhead: true,
						triggerAction: 'all',
						width: 60,
						editable: false,
						mode: 'local',
						lazyInit: false,
						disabled : false,
						displayField: 'label',
						valueField: 'value',
						value: 'bp3d',
						store: new Ext.data.SimpleStore({
							fields : ['value', 'label'],
							data   : [
								['bp3d', 'bp3d'],
								['SPL',  'SPL']
							]
						}),
						listeners: {
							'select': function(combo,record,index){
								var prm_record = ag_param_store.getAt(0);
								prm_record.beginEdit();
								prm_record.set('coord', record.data.value);
								prm_record.endEdit();
								prm_record.commit();
								_updateAnatomo();
							},
							'render': function(combo){
							},
							scope:this
						}
					},
HTML
if($coordinateSystemHidden ne 'true'){
	print qq|					'-',\n|;
}
print <<HTML;
					'<label style="font-size:14px;font-weight:bold;">'+ ag_lang.DATA_VERSION +'&nbsp;</label>',

					new Ext.form.ComboBox ({
						ctCls : 'x-small-editor',
						id : 'anatomo-version-combo',
						editable: false,
						mode: 'local',
						lazyInit: false,
						displayField: 'tgi_name',
						valueField: 'tgi_version',
						width: 80,
						triggerAction: 'all',
						hidden : false,
						store : version_store,
						listWidth: 750,
						tpl: versionListTpl,
						listeners: {
							'select' : {
								fn:function(combo, record, index) {
									if(index>0){
										\$('label#bp3-version-msg').show();
										\$('label#ag-version-msg').show();
									}else{
										\$('label#bp3-version-msg').hide();
										\$('label#ag-version-msg').hide();
									}
									if(Ext.isEmpty(record.data.tgi_comment)){
										\$('label#bp3-version-comment').html('').hide();
										\$('label#ag-version-comment').html('').hide();
									}else{
										\$('label#bp3-version-comment').html(record.data.tgi_comment).show();
										\$('label#ag-version-comment').html(record.data.tgi_comment).show();
									}

									Cookies.set('ag_annotation.images.md_id',record.data.md_id);
									Cookies.set('ag_annotation.images.mv_id',record.data.mv_id);
									Cookies.set('ag_annotation.images.mr_id',record.data.mr_id);

									init_bp3d_params.md_id = record.data.md_id;
									init_bp3d_params.mv_id = record.data.mv_id;
									init_bp3d_params.mr_id = record.data.mr_id;
									init_bp3d_params.version = combo.getValue();

									var c_version_str = Cookies.get('ag_annotation.images.version');
									var c_version;
									if(c_version_str) c_version = Ext.util.JSON.decode(c_version_str);
									c_version = c_version || {};
									c_version[record.data.tg_id] = record.data.tgi_version;
									c_version_str = Ext.util.JSON.encode(c_version);
									Cookies.set('ag_annotation.images.version',c_version_str);


									var checked = false;
									try{checked = Ext.getCmp('anatomo-clip-check').getValue();}catch(e){checked = false;}
//_dump("anatomo-version-combo.select():checked=["+checked+"]");
									if(!checked){
										_updateAnatomo();
									}else{
										var cmp = Ext.getCmp('anatomo-clip-predifined-plane')
										if(cmp && cmp.rendered){
//_dump("anatomo-version-combo.select():checked=["+1+"]");
											if(!cmp.fireEvent('select',cmp)) _updateAnatomo();
										}else{
//_dump("anatomo-version-combo.select():checked=["+2+"]");
											_updateAnatomo();
										}
									}
									var cmp = Ext.getCmp('anatomo-tree-type-combo')
									if(cmp && cmp.rendered){
										cmp.getStore().reload();
									}
									if(contents_tabs.getActiveTab().id == 'contents-tab-anatomography-panel'){
										_updateAnatomo();
										var cmp = Ext.getCmp('bp3d-version-combo');
										if(cmp && cmp.rendered){
											cmp.setValue(record.data.tgi_version);

												var cmp = Ext.getCmp('ag-parts-gridpanel');
												if(cmp && cmp.rendered){
													try{
														var store = cmp.getStore();
														var records = store.getRange();
//_dump("anatomo-version-combo.select():records=["+records.length+"]");
														getConvertIdList(records,store);
													}catch(e){
														_dump("cmp.getStore().loadData([],true);"+e);
													}
												}

											var cmp = Ext.getCmp('bp3d-tree-type-combo');
											if(cmp && cmp.rendered){
												cmp.getStore().reload();
											}

											navigate_grid.ds.reload();
										}else{
											init_bp3d_version = record.data.tgi_version;
//_dump("anatomo-version-combo.select():init_bp3d_version=["+init_bp3d_version+"]");
										}
									}
									try{Ext.getCmp('anatomography-bp3d-grid-panel').getStore().reload();}catch(e){}
								},
								scope:this
							},
							'render' : {
								fn : function(combo) {
									setTimeout(function(){
										new Ext.ToolTip({
											target: 'ag-version-information',
											html: get_ag_lang('VERSION_INFORMATION'),
											dismissDelay: 5000,
											closable: true
										});
									},1000);
								},
								scope:this
							}
						}
					}),

					'<label id="ag-version-comment" style="'+get_ag_lang('VERSION_COMMENT_STYLE')+'"></label>',
					'<label id="ag-version-information" style="'+get_ag_lang('VERSION_INFORMATION_STYLE')+'">'+Ext.util.Format.ellipsis(get_ag_lang('VERSION_INFORMATION'),50)+'</label>',
					'<label id="ag-version-msg" style="'+get_ag_lang('NOT_LATEST_VERSION_STYLE')+'">'+get_ag_lang('NOT_LATEST_VERSION')+'</label>',

					'-',
//					get_ag_lang('TREE_TYPE_HTML'),
					{
						hidden: true,
						id: 'bp3d-tree-type-combo-ag',
						xtype: 'combo',
						typeAhead: true,
						triggerAction: 'all',
						width: 110,
						editable: false,
						mode: 'local',
						lazyInit: false,
						disabled : true,
						displayField: 't_name',
						valueField: 't_type',
						store : navigate_tree_type_store,
						listeners: {
							'select': function(combo,record,index){
								if(contents_tabs.getActiveTab().id != 'contents-tab-anatomography-panel') return;
								var cmp = Ext.getCmp('bp3d-tree-type-combo');
								if(cmp && cmp.rendered){
//_dump("anatomo-tree-type-combo-ag.select():record.data.t_type=["+record.data.t_type+"]");
									var store = cmp.getStore();
									var index = store.find('t_type', new RegExp('^'+record.data.t_type+'\$'));
									if(index>=0){
										var record = store.getAt(index);
										cmp.setValue(record.data.t_type);
										cmp.fireEvent('select',cmp,record,index);
									}
								}
								_updateAnatomo();
							},
							render: function(combo){
							},
							valid: function(combo){
//								_dump("valid():["+combo.id+"]");
							},
							invalid: function(combo){
//								_dump("invalid():["+combo.id+"]");
							},
							scope:this
						}
					},



					'->',

					'-',
					'<label>Concept name or ID : </label>',
					' ',
//					new Ext.app.SearchField({
					new Ext.app.SearchFieldListeners({
						id: 'ag-search-field',
						width:200,
						value : Ext.isEmpty(gParams.query)?'':gParams.query,
						listeners: {
							'search' : function(field,query){
								try{
									if(contents_tabs.getActiveTab().id != 'contents-tab-bodyparts-panel'){
										contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
									}
									var comp = Ext.getCmp('bp3d-search-field');
									comp.setRawValue(query);
									comp.onTrigger2Click();
								}catch(e){
									_dump("tabpanel=["+e+"]");
								}
							},
							'clear' : function(field){
								try{
									var comp = Ext.getCmp('bp3d-search-field');
									comp.setRawValue('');
								}catch(e){
									_dump("tabpanel=["+e+"]");
								}
							},
							scope : this
						}
					}),
					'-',{
						cls: 'ag-toolbar-button-cls',
						overCls: 'ag-toolbar-button-overCls',
						text: get_ag_lang('BUTTON_OBJFILE_LIST'),
						handler: function(){click_objfiles_list_button({title:this.text});}
					},'-',{
						text:get_ag_lang('BUTTON_INFORMATION'),
						handler : function(){click_information_button();}
//					},
//					'-',{
//						text:get_ag_lang('BUTTON_ERROR_REPORT'),
//						handler : function(){click_error_report_button();}
					}
HTML
if($localeMenuHidden ne 'true'){
	print <<HTML;
					,'-',{
						text    : '$locale_label',
						icon    : '$locale_icon',
						cls     : '$locale_cls',
						handler : function(){
							var chage_locale = "$FORM{lng}".toLowerCase();
							var path = location.pathname;
HTML
if($defaultLocaleJa ne 'true'){
	print <<HTML;
							if(chage_locale=='en'){
								location.href = path + "?lng=ja";
							}else{
								location.href = path;
							}
HTML
}else{
	print <<HTML;
							if(chage_locale=='en'){
								Cookies.set('ag_annotation.locale','ja');
							}else{
								Cookies.set('ag_annotation.locale','en');
							}
							location.href = path;
HTML
}
print <<HTML;
						}
					}
HTML
}
print <<HTML;
//					,'-',{
//						text    : '$login_label',
//						icon    : 'css/openid-bg.gif',
//						cls     : 'x-btn-text-icon',
//						handler : $login_func
//					}
				]
			},
			{
				border: false,
				bodyStyle: 'height:25px;',
				html: '$LOCALE{BP3D_TITLE_HTML}',
				listeners: {
					afterlayout: function(comp){
						\$(comp.body.dom).css({height:25});
					},
					render : function(comp){
						\$(comp.body.dom).css({height:25});
					},
					resize : function(comp){
						\$(comp.body.dom).css({height:25});
					}
				},
				bbar:[
//					'<label style="color:#15428b;font-size:16px;font-weight:bold;">BodyParts3D</label>',
//					'-',
					'<label>Review search : </label>', ' ',
					new Ext.app.SearchFieldStore({
						id : 'contents-tab-feedback-search',
						store: contents_tab_feedback_store,
						width:200
					}),
					'-',
					'<label>Status filter : </label>',
					{
						id : 'contents-tab-feedback-status-combo',
						xtype         : 'combo',
						typeAhead     : true,
						triggerAction : 'all',
						editable      : false,
						mode          : 'local',
						displayField  : 'cs_name',
						valueField    : 'cs_id',
						lazyInit      : false,
						value         : '0',
						store: new Ext.data.SimpleStore({
							fields : ['cs_id', 'cs_name'],
							data   : [
HTML
if(scalar @COMMENT_STATUS > 0){
	my @TEMP = (qq|['0','ALL']|);
	foreach my $cs (@COMMENT_STATUS){
		push(@TEMP,qq|[$cs->{cs_id},'$cs->{cs_name}']|);
	}
	print join(",",@TEMP),"\n";
	undef @TEMP;
}
print <<HTML;
							]
						}),
						listeners: {
							'select': {
								fn:function(combo,record,index){
									contents_tab_feedback_store.reload();
									return;

									if(index == 0){
										contents_tab_feedback_store.clearFilter()
									}else{
										contents_tab_feedback_store.filter('cs_id',combo.getValue())
									}
									return;
									var field = comment_form.getForm().findField('comment_form.cs_id');
									if(field) field.setValue(combo.getValue());
								},scope:this}
						}
					}
					,'->'
HTML
if($localeMenuHidden ne 'true'){
	print <<HTML;
					,'-',{
						text    : '$locale_label',
						icon    : '$locale_icon',
						cls     : '$locale_cls',
						handler : function(){
							var chage_locale = "$FORM{lng}".toLowerCase();
							var path = location.pathname;
HTML
if($defaultLocaleJa ne 'true'){
	print <<HTML;
							if(chage_locale=='en'){
								location.href = path + "?lng=ja";
							}else{
								location.href = path;
							}
HTML
}else{
	print <<HTML;
							if(chage_locale=='en'){
								Cookies.set('ag_annotation.locale','ja');
							}else{
								Cookies.set('ag_annotation.locale','en');
							}
							location.href = path;
HTML
}
print <<HTML;
						}
					}
HTML
}
print <<HTML;
//					,'-',{
//						text    : '$login_label',
//						icon    : 'css/openid-bg.gif',
//						cls     : 'x-btn-text-icon',
//						handler : $login_func
//					}
				]
			},
			{
				border: false,
				bodyStyle: 'height:25px;',
				html: '$LOCALE{BP3D_TITLE_HTML}',
				listeners: {
					afterlayout: function(comp){
						\$(comp.body.dom).css({height:25});
					},
					render : function(comp){
						\$(comp.body.dom).css({height:25});
					},
					resize : function(comp){
						\$(comp.body.dom).css({height:25});
					}
				},
				bbar:[
//					'<label style="color:#15428b;font-size:16px;font-weight:bold;">BodyParts3D</label>',
//					'-',
					'->',
//					'-',
//					'<label>Concept name or ID : </label>',
//					' ',
//					new Ext.app.SearchField({
//						width:200,
//						value : Ext.isEmpty(gParams.query)?'':gParams.query,
//						listeners: {
//							'render' : function(comp){
//								try{
//									if(Ext.isEmpty(gParams.query)) return;
//									comp.setRawValue(gParams.query);
//									comp.onTrigger2Click();
//								}catch(e){
//									_dump("render():"+e);
//								}
//							},
//							scope : this
//						}
//					})

					'-',{
						text:'PartsBrowser',
						handler : function(){
							Ext.getCmp('contents-tab-panel').activate(Ext.getCmp('contents-tab-bodyparts-panel'));
						}
					},'-',{
						text:'Anatomography',
						handler : function(){
							Ext.getCmp('contents-tab-panel').activate(Ext.getCmp('contents-tab-anatomography-panel'));
						}
					}
HTML
if($localeMenuHidden ne 'true'){
	print <<HTML;
					,'-',{
						text    : '$locale_label',
						icon    : '$locale_icon',
						cls     : '$locale_cls',
						handler : function(){
							var chage_locale = "$FORM{lng}".toLowerCase();
							var path = location.pathname;
HTML
if($defaultLocaleJa ne 'true'){
	print <<HTML;
							if(chage_locale=='en'){
								location.href = path + "?lng=ja";
							}else{
								location.href = path;
							}
HTML
}else{
	print <<HTML;
							if(chage_locale=='en'){
								Cookies.set('ag_annotation.locale','ja');
							}else{
								Cookies.set('ag_annotation.locale','en');
							}
							location.href = path;
HTML
}
print <<HTML;
						}
					}
HTML
}
print <<HTML;
//					,'-',{
//						text    : '$login_label',
//						icon    : 'css/openid-bg.gif',
//						cls     : 'x-btn-text-icon',
//						handler : $login_func
//					}
				]
			}

			]
		},
		contents_tabs
		],

		listeners : {
			'afterlayout' : function(panel,layout){
//_dump("viewport.afterlayout():"+panel.rendered);
//				if(panel.rendered) panel.doLayout();
			},
			'resize' : function(panel){
//_dump("viewport.resize():"+panel.rendered);
//				if(panel.rendered) panel.doLayout();
			},
			'render' : function(panel){
//_dump("viewport.render():"+panel.rendered);
//				if(panel && !panel.loadMask) panel.loadMask = new Ext.LoadMask(panel.el,{msg:'Please wait...',removeMask:true});
//				panel.loadMask.show();
			},
			scope:this
		}



	});

	try{
		var dragZone = new ImageDragZone(bp3d_contents_thumbnail_dataview, {
			containerScroll:true,
			ddGroup: 'partlistDD'
		});
		var dragZone2 = new ImageDragZone(bp3d_contents_list_dataview, {
			containerScroll:true,
			ddGroup: 'partlistDD'
		});
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
	}catch(e){alert(e)}

//2011-09-28 追加
//	var viewport = Ext.getCmp('viewport');
//	if(viewport){
//		if(viewport.rendered && !viewport.loadMask){
//			viewport.loadMask = new Ext.LoadMask(viewport.el,{msg:get_ag_lang('MSG_LOADING_DATA'),removeMask:true});
//			viewport.loadMask.show();
//		}else if(!viewport.rendered){
//			viewport.on('render',function(viewport){
//				if(viewport && !viewport.loadMask) viewport.loadMask = new Ext.LoadMask(viewport.el,{msg:get_ag_lang('MSG_LOADING_DATA'),removeMask:true});
//				viewport.loadMask.show();
//			});
//		}
//	}


_load = function(loc){
//_dump("_load()");
//_dump("_load():loc=["+loc+"]");
	var treeCmp = Ext.getCmp('navigate-tree-panel');
	var contentCmp = Ext.getCmp('content-card-panel');
	var urlOBj;
	var s = Ext.urlDecode(loc.search.substr(1));

	if(s && s._dc && _bp3d_change_location_hash[s._dc]) urlOBj = _bp3d_change_location_hash[s._dc];
	if(Ext.isEmpty(urlOBj)){
		try{
			var hash = loc.hash.substr(1)
//			_dump("_load():hash=["+hash.length+"]["+hash+"]");
			if(hash.length){
				urlOBj = Ext.decode(hash);
			}else{
				urlOBj = Ext.urlDecode(loc.search.substr(1));
			}
		}catch(e){alert("1:"+e);}
	}

	var sel_id;
	var s = Ext.urlDecode(loc.search.substr(1));
	if(s && s._dc){
//		_dump("_load():s._dc=["+s._dc+"]");
		Ext.each(_bp3d_change_location_stack,function(v,i,a){

			if(v!=s._dc) return true;
			if(i>=a.length-1) return false;
			var t = a[i+1];
			if(!_bp3d_change_location_hash[t] || !_bp3d_change_location_hash[t].sel_id) return true;
			sel_id = _bp3d_change_location_hash[t].sel_id;
//			_dump("_load(each):_bp3d_change_location_hash["+t+"].sel_id=["+_bp3d_change_location_hash[t].sel_id+"]");
			return false;

		});
	}
	if(!sel_id && urlOBj && urlOBj.sel_id){
//		_dump("_load():urlOBj.sel_id=["+urlOBj.sel_id+"]");
		sel_id = urlOBj.sel_id;
	}
	if(sel_id) Cookies.set('ag_annotation.images.fmaid',sel_id);

//	if(Ext.isEmpty(urlOBj.query) && Ext.isEmpty(gBP3D_TPAP)){
	if(Ext.isEmpty(gBP3D_TPAP)){
		if(urlOBj.params){
//			_dump(urlOBj.params);

//			var params = Ext.urlDecode(urlOBj.params);
//			for(var key in params){
//				init_bp3d_params[key] = params[key];
//			}
			bp3d_contents_store.load({
				params: Ext.urlDecode(urlOBj.params)
			});
		}else{
			bp3d_contents_store.load({
				params:{
					node     : urlOBj.node,
					txpath   : urlOBj.txpath,
					position : urlOBj.position,
					sorttype : urlOBj.sorttype,
					query    : urlOBj.query
				}
			});
		}
	}
	if(urlOBj.txpath){
		if(treeCmp){
			var txpath = "/root" + urlOBj.txpath;
			treeCmp.selectPath(txpath,'f_id',function(bSuccess,oSelNode){
			});
			Cookies.set('ag_annotation.images.path',urlOBj.txpath);
		}
	}

	if(urlOBj.position){
		Ext.getCmp('positionSelect').setValue(urlOBj.position);
	}
	if(urlOBj.sorttype){
		Ext.getCmp('sortSelect').setValue(urlOBj.sorttype);
	}

//	if(!Ext.isEmpty(urlOBj.query)){
//		try{
//			var query = urlOBj.query.replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,"&");
//			query = query.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
//			var tabCmp = Ext.getCmp('navigate-tab-panel');
//			var tabpanel = createSearchGridPanel(query);
//			if(tabpanel) tabCmp.setActiveTab(tabCmp.add(tabpanel));
//		}catch(e){
//			_dump("tabpanel=["+e+"]");
//		}
//	}

//	if(contents_tabs.getActiveTab().id != 'contents-tab-anatomography-panel' || !Ext.isEmpty(urlOBj.query)){
//		if(contents_tabs.getActiveTab().id != 'contents-tab-bodyparts-panel'){
//			contents_tabs.setActiveTab('contents-tab-bodyparts-panel');
//		}else{
//			var tabBodypartsDom = Ext.get('contents-tab-panel__contents-tab-bodyparts-panel');
//			if(tabBodypartsDom && !tabBodypartsDom.hasClass('x-tab-strip-active')){
//				var tabHomeDom = Ext.get('contents-tab-panel__contents-tab-home-panel');
//				tabHomeDom.removeClass('x-tab-strip-active');
//				tabBodypartsDom.addClass('x-tab-strip-active');
//				Ext.getCmp('header-panel').layout.setActiveItem(1);
//			}
//
//			if(!Ext.getCmp('south-panel').isVisible()){
//					Ext.getCmp('south-panel').show();
//					setTimeout(function(){
//						var viewport = Ext.getCmp('viewport');
//						if(viewport && viewport.rendered) viewport.doLayout();
//					},0);
//			}
//		}
//	}


};

//_dump("gParams.query=["+gParams.query+"]");
//var searchField = new Ext.app.SearchField({
//	renderTo : 'search_area',
//	store    : bp3d_contents_store,
//	width    : 320,
//	value    : Ext.isEmpty(gParams.query)?'':gParams.query
//});
//_dump("searchField.value=["+searchField.value+"]");

try{
	Ext.getCmp('positionSelect').setValue(image_position);
}catch(e){
	if(window.console){
		console.log(e);
	}else{
		_dump(e);
	}
}
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
try{
	var disptypeSelect = Ext.getCmp('disptypeSelect');
	var disptypeSelectStore = disptypeSelect.getStore();
	disptypeSelect.setValue(image_disptype);
	var disptypeSelectIndex = disptypeSelectStore.find('value',image_disptype);
	if(disptypeSelectIndex>=0){
		disptypeSelect.fireEvent('select',disptypeSelect,disptypeSelectStore.getAt(disptypeSelectIndex),disptypeSelectIndex);
	}
}catch(e){
	_dump("8043:"+e);
}

//_dump("10882:");
setTimeout(function(){
	var tree_panel = Ext.getCmp("navigate-tree-panel");
	if(tree_panel && tree_panel.selectPath){
		if(location.search && location.search.match(/txpath=[^&]+/)){
			try{
				var urlOBj = Ext.urlDecode(location.search.substr(1));
			}catch(e){alert("2:"+e);}
			var txpath = "/root" + urlOBj.txpath;
//_dump("txpath1=["+txpath+"]");
			tree_panel.selectPath(txpath,'f_id',selectPathCB);
		}else{
			var treeType = Cookies.get('ag_annotation.images.type',3);
			var navigate_tree_combobox = Ext.getCmp('bp3d-tree-type-combo');
			if(navigate_tree_combobox && navigate_tree_combobox.rendered && navigate_tree_combobox.getValue() != treeType){
				var index = navigate_tree_combobox.store.find('t_type',new RegExp('^'+treeType+'\$'));
				if(index<0) return;
				navigate_tree_combobox.setValue(treeType);
				navigate_tree_combobox.fireEvent('select',navigate_tree_combobox,navigate_tree_combobox.store.getAt(index),index);
			}else{
				var txpath = "/root" + Cookies.get('ag_annotation.images.path','');
//_dump("txpath2=["+txpath+"]");
				tree_panel.selectPath(txpath,'f_id',selectPathCB);
			}
		}
	}
},100);

var openWindowComment = function(aRec,aMode){
	try{
		if(Ext.isEmpty(aMode)) aMode = 'reply';

		var c_id = null;
		var c_pid = null;
		var c_name = '$user_name';
		var c_email = null;
		var ct_id = 1;
		var cs_id = 1;

		var tgi_version = null;
		var t_type = null;
		try{tgi_version=Ext.getCmp('bp3d-version-combo').getValue();}catch(e){tgi_version=null;}
		try{t_type=Ext.getCmp('bp3d-tree-type-combo').getValue();}catch(e){t_type=null;}

		var selRec = aRec;
		if(selRec){
			if(aMode == 'reply'){
				selRec.c_title = 'Re:' + selRec.c_title;
				selRec.c_comment = selRec.c_comment.replace(/^(.*)\$/mg,">\$1").replace(/&gt;/g,">").replace(/&lt;/g,"<").replace(/&nbsp;/g," ").replace(/&amp;/g,"&");
				c_pid = selRec.c_id;
				ct_id = selRec.ct_id;
				cs_id = selRec.cs_id;
			}else{
				selRec.c_comment = selRec.c_comment.replace(/&gt;/g,">").replace(/&lt;/g,"<").replace(/&nbsp;/g," ").replace(/&amp;/g,"&");
				c_id  = selRec.c_id;
				c_pid = selRec.c_pid;
				c_name = selRec.c_name;
				c_email = selRec.c_email;
				ct_id = selRec.ct_id;
				cs_id = selRec.cs_id;
			}
		}else{
			var oSelNode = null;
			var treeCmp = Ext.getCmp('navigate-tree-panel');
			if(treeCmp) oSelNode = treeCmp.getSelectionModel().getSelectedNode();
			if(oSelNode && oSelNode.id == 'root'){
				selRec = oSelNode.attributes.attr;
			}else{
				var selRecs = bp3d_contents_thumbnail_dataview.getSelectedRecords();
				if(selRecs && selRecs.length>0){
					selRec = selRecs[0].data;
				}else if(oSelNode){
					selRec = oSelNode.attributes.attr;
				}
			}
		}
		var comment_form = new Ext.form.FormPanel({
			baseCls     : 'x-plain',
			labelWidth  : 55,
			url         :'put-comment.cgi',
			fileUpload  : true,
			defaultType : 'textfield',
			items : [{
				xtype      : 'hidden',
				name       : 'parent',
				value      : '$FORM{parent}'
			},{
				xtype      : 'hidden',
				name       : 'f_id',
				value      : selRec.f_id
			},{
				xtype      : 'hidden',
				name       : 'c_id',
				value      : c_id
			},{
				xtype      : 'hidden',
				name       : 'c_pid',
				value      : c_pid
			},{
				xtype      : 'hidden',
				name       : 'ct_id',
				value      : ct_id
			},{
				xtype      : 'hidden',
				id         : 'comment_form.cs_id',
				name       : 'cs_id',
				value      : cs_id
			},{
				xtype      : 'hidden',
				name       : 'tgi_version',
				value      : tgi_version
			},{
				xtype      : 'hidden',
				name       : 't_type',
				value      : t_type
			},{
				fieldLabel : 'Name',
				name       : 'c_name',
				anchor     : '100%',
				value      : c_name,
HTML
if(!$lsdb_OpenID){
	print <<HTML;
				allowBlank : false,
HTML
}
print <<HTML;
				selectOnFocus : true
			},{
				fieldLabel : 'e-mail',
				name       : 'c_email',
				anchor     : '100%',
				value      : c_email,
				vtype      : 'email',
				selectOnFocus : true
			},{
				fieldLabel : 'Title',
				name       : 'c_title',
				anchor     : '100%',
				value      : selRec.c_title,
				selectOnFocus : true
			},{
				xtype      : 'fileuploadfield',
				id         : 'image',
				emptyText  : 'Select an image',
				fieldLabel : 'Image',
				name       : 'c_image',
				buttonCfg  : {
					text    : '',
					iconCls : 'upload-icon'
				},
				anchor     : '100%'
HTML
if(!$lsdb_OpenID){
	print <<HTML;
			},{
				fieldLabel : 'Password',
				name       : 'c_passwd',
				anchor     : '50%',
				value      : selRec.c_passwd,
				allowBlank : false,
				selectOnFocus : true
HTML
}
print <<HTML;
			},{
				hidden        : (c_pid?true:false),
				hideLabel     : (c_pid?true:false),
				hideMode      : 'display',
				fieldLabel    : 'Status',
				anchor        : '40%',
				xtype         : 'combo',
				typeAhead     : true,
				triggerAction : 'all',
				editable      : false,
				mode          : 'local',
				displayField  : 'cs_name',
				valueField    : 'cs_id',
				lazyInit      : false,
				value         : cs_id,
				store: new Ext.data.SimpleStore({
					fields : ['cs_id', 'cs_name'],
					data   : [
HTML
if(scalar @COMMENT_STATUS > 0){
my @TEMP = ();
foreach my $cs (@COMMENT_STATUS){
	push(@TEMP,qq|[$cs->{cs_id},'$cs->{cs_name}']|);
}
print join(",",@TEMP),"\n";
undef @TEMP;
}
print <<HTML;
					]
				}),
				listeners: {
					'select': {
						fn:function(combo,record,index){
							var field = comment_form.getForm().findField('comment_form.cs_id');
							if(field) field.setValue(combo.getValue());
						},scope:this}
				}

			},{
				xtype     : 'textarea',
				hideLabel : true,
				name      : 'c_comment',
HTML
if($lsdb_OpenID){
	print <<HTML;
				anchor    : '100% -102',
HTML
}else{
	print <<HTML;
				anchor    : '100% -128',
HTML
}
print <<HTML;
				value      : selRec.c_comment,
				allowBlank : false,
				selectOnFocus : true
			}]
		});

		var comment_window = new Ext.Window({
			title       : get_ag_lang('COMMENT_WIN_TITLE'),
			width       : 500,
			height      : 400,
			minWidth    : 300,
			minHeight   : 250,
			layout      : 'fit',
			plain       : true,
			bodyStyle   :'padding:5px;',
			buttonAlign :'right',
			items       : comment_form,
			modal       : true,
			autoScroll  : true,
			buttons : [{
				text    : get_ag_lang('COMMENT_WIN_TITLE_SEND'),
				handler : function(){
					if(comment_form.getForm().isValid()){
						comment_form.getForm().submit({
							url     : 'put-comment.cgi',
							waitMsg : get_ag_lang('COMMENT_WIN_WAITMSG')+'...',
							success : function(fp, o){
								try{
									if(o.result.success == true){
										Ext.MessageBox.show({
											title   : get_ag_lang('COMMENT_TITLE_PLUS'),
											msg     : get_ag_lang('COMMENT_WIN_ADDMSG'),
											buttons : Ext.MessageBox.OK,
											icon    : Ext.MessageBox.INFO,
											fn      : function(){
												comment_window.close();
												bp3d_contents_detail_annotation_store.reload();
												var cmp = comment_form.find('name','c_pid');
												if(cmp && cmp.length>0){
													var val = cmp[0].getValue();
													if(Ext.isEmpty(val)){
														contents_tab_feedback_store.reload();
													}else{
														updateFeedbackChildStore.load({params : {c_pid : val}});
													}
												}
											}
										});
										return;
									}
								}catch(e){ _dump("success():"+ e + ""); }

								Ext.MessageBox.show({
									title   : get_ag_lang('COMMENT_TITLE_PLUS'),
									msg     : get_ag_lang('COMMENT_WIN_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});

							},
							failure : function(fp, o){
								Ext.MessageBox.show({
									title   : get_ag_lang('COMMENT_TITLE_PLUS'),
									msg     : get_ag_lang('COMMENT_WIN_ERRMSG'),
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
					}
				}
			},{
				text: get_ag_lang('COMMENT_WIN_TITLE_CANCEL'),
				handler : function(){
					comment_window.close();
				}
			}],
			listeners: {
				'show': {
					fn:function(self){
					},
					scope:this
				},
				'hide': {
					fn:function(self){
					},
					scope:this
				}
			}
		});
		comment_window.show();
	}catch(e){ alert(e); }
};

HTML
if($lsdb_Auth){
	print <<HTML;

var openContentEditWindow = function(data){
	try{
		var window_title = get_ag_lang('ADMIN_FORM_UPDATE_TITLE');
		var status_bar = null;

		try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
		var content_edit_form = new Ext.form.FormPanel({
			baseCls     : 'x-plain',
			labelWidth  : 80,
			url         : 'put-lsdb-synonym.cgi',
			fileUpload  : true,
			bodyStyle   : 'padding:5px',
			width       : 600,
			items       : [{
				xtype      : 'hidden',
				name       : 'parent',
				value      : '$FORM{parent}'
			},{
				xtype      : 'hidden',
				name       : 'version',
				value      : bp3d_version
			},{
				layout      : 'form',
				border      : false,
				labelWidth  : 40,
				bodyStyle   : 'background-color:transparent',
				items: [{
					xtype         : 'textfield',
					selectOnFocus : true,
					readOnly      : true,
					fieldLabel    : 'ID',
					name          : 'f_id',
					value         : data.f_id,
					allowBlank    : false,
					anchor        : '50%'
				}]
			},{
				layout      : 'column',
				border      : false,
				bodyStyle   : 'background-color:transparent',
				items: [{
					columnWidth : .5,
					layout      : 'form',
					border      : false,
					labelWidth  : 60,
					bodyStyle   : 'background-color:transparent',
					items: [{
						xtype         : 'textfield',
						selectOnFocus : true,
						fieldLabel    : 'UniversalID',
						name          : 'common_id',
						value         : data.common_id,
						allowBlank    : false
					}]
				},{
					columnWidth : .5,
					layout      : 'form',
					border      : false,
					labelWidth  : 73,
					bodyStyle   : 'background-color:transparent',
					items: [
HTML
	if($useColorPicker eq 'true'){
		print <<HTML;
						new Ext.ux.ColorPickerField({
							ctCls : 'x-small-editor',
							width: 75,
							value:data.def_color?data.def_color:'$DEF_COLOR',
							id   : 'bp3d-content-edit-def_color',
							name:'def_color',
							selectOnFocus : true,
							fieldLabel    : 'Default color',
							menuListeners: {
								'beforeshow': function(menu){
									if(menu.palette){
										menu.palette.suspendEvents();
										menu.palette.select(Ext.getCmp('bp3d-content-edit-def_color').getValue());
										menu.palette.resumeEvents();
									}
								},
								'select' : function (palette, color) {
									Ext.getCmp('bp3d-content-edit-def_color').setValue(color);
									palette.value = color;
								}
							}
						})
HTML
	}else{
		print <<HTML;
						new Ext.ux.ColorField({
							ctCls : 'x-small-editor',
							width: 75,
							value:data.def_color?data.def_color:'$DEF_COLOR',
							id   : 'bp3d-content-edit-def_color',
							name:'def_color',
							selectOnFocus : true,
							fieldLabel    : 'Default color'
						})
HTML
	}
	print <<HTML;
					]
				}]
			},{
				xtype           : 'tabpanel',
				id              : 'bp3d-content-edit-tabpanel',
				plain           : true,
				activeTab       : 0,
				defaults        : {bodyStyle:'padding:10px'},
				enableTabScroll : true,
				deferredRender  : false
			}]
		});
		var tabpabel = Ext.getCmp('bp3d-content-edit-tabpanel');
		if(tabpabel){
			for(var i=0;i<data.lsdb_term.length;i++){
				var panel = new Ext.Panel({
					title : data.lsdb_term[i].lsdb_name,
					height : 300,
					layout:'form',
					labelAlign: 'top',
					defaults: {width: 230},
					defaultType : 'textarea',
					items: [{
						xtype      : 'hidden',
						name       : 'lsdb_id',
						value      : data.lsdb_term[i].lsdb_id
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_ENG_TITLE'),
						name          : 'lsdb_term_e',
						value         : data.lsdb_term[i].lsdb_term_e,
						anchor        : '100% -238'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_LATINA_TITLE'),
						name          : 'lsdb_term_l',
						value         : data.lsdb_term[i].lsdb_term_l,
						anchor        : '100% -238'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_JPN_TITLE'),
						name          : 'lsdb_term_j',
						value         : data.lsdb_term[i].lsdb_term_j,
						anchor        : '100% -238'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_KANA_TITLE'),
						name          : 'lsdb_term_k',
						value         : data.lsdb_term[i].lsdb_term_k,
						anchor        : '100% -238'
					}]
				});
				tabpabel.add(panel);
			}
		}
		var content_edit_window = new Ext.Window({
			title       : window_title,
			width       : 442,
			minWidth    : 400,
			height      : 470,
			minHeight   : 470,
			maxHeight   : 470,
			layout      : 'fit',
			plain       : true,
			bodyStyle   :'padding:5px;',
			buttonAlign :'right',
			items       : content_edit_form,
			modal       : true,
			bbar        : status_bar,
			buttons : [{
				text    : get_ag_lang('COMMENT_WIN_TITLE_SEND'),
				handler : function(){
					if(content_edit_form.getForm().isValid()){
						content_edit_form.getForm().submit({
							url     : 'put-lsdb-synonym.cgi',
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
												content_edit_window.close();
												getViewImages().store.reload();
												bp3d_contents_detail_annotation_store.reload();

												var treeCmp = Ext.getCmp('navigate-tree-panel');
												if(treeCmp && treeCmp.root){
													treeCmp.root.reload(
														function(node){
															var path = Cookies.get('ag_annotation.images.path','');
															node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id');
														}
													);
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
								Ext.MessageBox.show({
									title   : window_title,
									msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+o.result.msg+' ]',
									buttons : Ext.MessageBox.OK,
									icon    : Ext.MessageBox.ERROR
								});
							}
						});
					}
				}
			},{
				text: get_ag_lang('COMMENT_WIN_TITLE_CANCEL'),
				handler : function(){
					content_edit_window.close();
				}
			}],
			listeners: {
				'show': {fn:function(self){},scope:this},
				'hide': {fn:function(self){},scope:this},
				'render': {
					fn: function(){
					}
				}
			}
		});
		content_edit_window.show();
	}catch(e){
		_dump("openContentEditWindow():"+e);
		for(var key in e){
			try{
				if(typeof e[key] == "function"){
					_dump(key+":["+(typeof e[key])+"]");
				}else{
					_dump(key+":["+(typeof e[key])+"]["+(e[key])+"]");
				}
			}catch(ex){
				_dump("openContentEditWindow():"+ex);
			}
		}
	}
};





var openWindowContent = function(data,del){
	var window_title = get_ag_lang('ADMIN_FORM_UPDATE_TITLE');
	var readOnly = false;
	var allowBlank = true;
	var activeItem = 1;

	var content_openid = null;
	var content_modified = null;
	var status_bar = null;

	if(Ext.isEmpty(data)){
		var selNode = null;
		var treeCmp = Ext.getCmp('navigate-tree-panel');
		if(treeCmp) selNode = treeCmp.getSelectionModel().getSelectedNode();
		data = {pnode:selNode.id};
		window_title = get_ag_lang('ADMIN_FORM_ADD_TITLE');
	}else{
		content_openid = new Ext.Toolbar.TextItem(data.m_openid);
		content_modified = new Ext.Toolbar.TextItem(new Date(data.lastmod).format("$TIME_FORMAT"));

		status_bar = new Ext.StatusBar({
			id          : 'word-status',
			defaultText : 'Last Modified',
			items       : ['->',content_openid,'',content_modified]
		});

		if(!Ext.isEmpty(del)){
			window_title = get_ag_lang('ADMIN_FORM_DELETE_TITLE');
			readOnly = true;
			allowBlank = !Ext.isEmpty(data.delcause);
			activeItem = 0;
		}
	}
	try{var bp3d_version = Ext.getCmp('bp3d-version-combo').getValue();}catch(e){bp3d_version='$MODEL_VERSION[0][0]';}
	var fma_form = new Ext.form.FormPanel({
		baseCls     : 'x-plain',
		labelWidth  : 80,
		url         : 'put-content.cgi',
		fileUpload  : true,
		bodyStyle   : 'padding:5px',
		width       : 600,
		items       : [{
			xtype      : 'hidden',
			name       : 'parent',
			value      : '$FORM{parent}'
		},{
			xtype      : 'hidden',
			name       : 'version',
			value      : bp3d_version
		},{
			xtype      : 'hidden',
			name       : 't_id',
			value      : data.id
		},{
			xtype      : 'hidden',
			name       : 't_pid',
			value      : data.pid
		},{
			xtype      : 'hidden',
			name       : 'b_delcause_old',
			value      : data.delcause
		},{
			xtype      : 'hidden',
			name       : 'b_id_old',
			value      : data.b_id
		},{
			layout    : 'column',
			border    : false,
			bodyStyle : 'background-color:transparent',
			items:[{
				columnWidth : .5,
				layout      : 'form',
				border      : false,
				labelWidth  : 40,
				bodyStyle   : 'background-color:transparent',
				items: [{
					xtype         : 'textfield',
					selectOnFocus : true,
					readOnly      : true,
					fieldLabel    : 'FMAID',
					name          : 'b_id',
					value         : data.b_id,
					allowBlank    : false,
					anchor        : '95%'
				},{
					xtype         : 'textfield',
					selectOnFocus : true,
					readOnly      : readOnly,
					fieldLabel    : 'Phase',
					name          : 'b_phase',
					value         : data.phase,
					allowBlank    : readOnly,
					anchor        : '95%'
				}]
			},{
				columnWidth : .5,
				layout      : 'form',
				border      : false,
				bodyStyle   : 'background-color:transparent',
				items: [{
					xtype         : 'textfield',
					selectOnFocus : true,
					readOnly      : readOnly,
					fieldLabel    : 'Zmin(mm)',
					name          : 'b_zmin',
					value         : data.zmin,
					anchor        : '95%'
				},{
					xtype         : 'textfield',
					selectOnFocus : true,
					readOnly      : readOnly,
					fieldLabel    : 'Zmax(mm)',
					name          : 'b_zmax',
					value         : data.zmax,
					anchor        : '95%'
				},{
					xtype         : 'textfield',
					selectOnFocus : true,
					readOnly      : readOnly,
					fieldLabel    : get_ag_lang('ADMIN_FORM_VOLUME_TITLE')+'(cm<sup>3</sup>)',
					name          : 'b_volume',
					value         : data.volume,
					anchor        : '95%'
				}]
			}]
		},{
			layout         : 'card',
			autoScroll     : false,
			activeItem     : activeItem,
			border         : false,
			deferredRender : false,
			anchor         : '100% -80',
			items          : [{
				xtype       : 'panel',
				plain       : true,
				layout      : 'form',
				labelAlign  : 'top',
				defaults    : {width: 230},
				defaultType : 'textfield',
				bodyStyle   : 'padding: 5px;',
				frame       : true,
				anchor      : '100% -52',
				items:[{
					xtype         : 'textarea',
					selectOnFocus : true,
					fieldLabel    : get_ag_lang('ADMIN_FORM_DELETE_CAUSE_TITLE')+'(*)',
					name          : 'b_delcause',
					value         : data.delcause,
					allowBlank    : allowBlank,
					anchor        : '100% -20'
				}]
			},{
				xtype           : 'tabpanel',
				plain           : true,
				activeTab       : 0,
				defaults        : {bodyStyle:'padding:10px'},
				enableTabScroll : true,
				deferredRender  : false,
				items           : [
				{
					title:get_ag_lang('ADMIN_FORM_DETAIL_E_TITLE'),
					layout:'form',
					labelAlign: 'top',
					defaults: {width: 230},
					defaultType : 'textfield',
					items: [
					{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_NAME_TITLE'),
						name          : 'b_name_e',
						value         : data.name_e,
						anchor        : '100%'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_LATINA_TITLE'),
						name          : 'b_name_l',
						value         : data.name_l,
						anchor        : '100%'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_ORGAN_SYSTEM_TITLE'),
						name          : 'b_organsys_e',
						value         : data.organsys_e,
						anchor        : '100%'
					}]
				},
				{
					title       : get_ag_lang('ADMIN_FORM_DETAIL_J_TITLE'),
					layout      : 'form',
					labelAlign  : 'top',
					defaults    : {width: 230},
					defaultType : 'textfield',
					items       : [{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_NAME_TITLE'),
						name          : 'b_name_j',
						value         : data.name_j,
						anchor        : '100%'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_KANA_TITLE'),
						name          : 'b_name_k',
						value         : data.name_k,
						anchor        : '100%'
					},{
						selectOnFocus : true,
						fieldLabel    : get_ag_lang('ADMIN_FORM_ORGAN_SYSTEM_TITLE'),
						name          : 'b_organsys_j',
						value         : data.organsys_j,
						anchor        : '100%'
					}]
				},
				{
					title       : get_ag_lang('ADMIN_FORM_SYNONYM_E_TITLE'),
					layout      : 'form',
					labelAlign  : 'top',
					defaults    : {width: 230},
					defaultType : 'textfield',
					items: [{
						xtype         : 'textarea',
						selectOnFocus : true,
						hideLabel     : true,
						name          : 'b_syn_e',
						value         : data.syn_e,
						anchor        : '100% -3'
					}]
				},{
					title       : get_ag_lang('ADMIN_FORM_SYNONYM_J_TITLE'),
					layout      :'form',
					labelAlign  : 'top',
					defaults    : {width: 230},
					defaultType : 'textfield',
					items       : [{
						xtype         : 'textarea',
						selectOnFocus : true,
						hideLabel     : true,
						name          : 'b_syn_j',
						value         : data.syn_j,
						anchor        : '100% -3'
					}]
				}]
			}]
		}]
	});
	var fma_window = new Ext.Window({
		title       : window_title,
		width       : 442,
		height      : 380,
		minWidth    : 400,
		minHeight   : 380,
		layout      : 'fit',
		plain       : true,
		bodyStyle   :'padding:5px;',
		buttonAlign :'right',
		items       : fma_form,
		modal       : true,
		bbar        : status_bar,
		buttons : [{
			text    : get_ag_lang('COMMENT_WIN_TITLE_SEND'),
			handler : function(){
				if(fma_form.getForm().isValid()){
					fma_form.getForm().submit({
						url     : 'put-content.cgi',
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
											fma_window.close();
											getViewImages().store.reload();
											bp3d_contents_detail_annotation_store.reload();

											var treeCmp = Ext.getCmp('navigate-tree-panel');
											if(treeCmp && treeCmp.root){
												treeCmp.root.reload(
													function(node){
														var path = Cookies.get('ag_annotation.images.path','');
														node.getOwnerTree().selectPath(Ext.isEmpty(path)?'':('/root/'+ path),'f_id');
													}
												);
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
							Ext.MessageBox.show({
								title   : window_title,
								msg     : get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [ '+o.result.msg+' ]',
								buttons : Ext.MessageBox.OK,
								icon    : Ext.MessageBox.ERROR
							});
						}
					});
				}
			}
		},{
			text: get_ag_lang('COMMENT_WIN_TITLE_CANCEL'),
			handler : function(){
				fma_window.close();
			}
		}],
		listeners: {
			'show': {fn:function(self){},scope:this},
			'hide': {fn:function(self){},scope:this},
			'render': {
				fn: function(){
					if(content_openid) Ext.fly(content_openid.getEl().parentNode).addClass('x-status-text-panel').createChild({cls:'spacer'});
					if(content_modified) Ext.fly(content_modified.getEl().parentNode).addClass('x-status-text-panel').createChild({cls:'spacer'});
				}
			}
		}
	});
	fma_window.show();
};

var putTree = function(attrs,window_title,s_cb,f_cb){
	var params = {
		parent : (Ext.isEmpty(gParams.parent)?'':gParams.parent),
		lng    : gParams.lng,
		attrs  : Ext.util.JSON.encode(attrs)
	}
	Ext.Ajax.request({
		url     : 'put-tree.cgi',
		method  : 'POST',
		params  : Ext.urlEncode(params),
		success : function(conn,response,options){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			if(!results || results.success == false){
				var msg = get_ag_lang('ADMIN_FORM_REG_ERRMSG');
				if(results && results.msg) msg += ' ['+results.msg+' ]';
				Ext.MessageBox.show({
					title   : window_title,
					msg     : msg,
					buttons : Ext.MessageBox.OK,
					icon    : Ext.MessageBox.ERROR
				});
				if(f_cb) f_cb();
				return;
			}
			if(!s_cb) return;
			if(results.t_ids){
				var icnt;
				for(icnt=0;icnt<results.t_ids.length;icnt++){
					attrs[icnt].t_id = results.t_ids[icnt];
				}
			}
			s_cb(attrs);
		},
		failure : function(conn,response,options){
			try{var results = Ext.util.JSON.decode(conn.responseText);}catch(e){}
			var msg = get_ag_lang('ADMIN_FORM_REG_ERRMSG')+' [';
			if(results && results.msg){
				msg += results.msg+' ]';
			}else{
				msg += conn.status+" "+conn.statusText+' ]';
			}
			Ext.MessageBox.show({
				title   : window_title,
				msg     : msg,
				buttons : Ext.MessageBox.OK,
				icon    : Ext.MessageBox.ERROR
			});
			if(f_cb) f_cb();
		}
	});
}

HTML
}
print <<HTML;


//}catch(e){
//	alert("ag_ann_init():"+e);
//	for(var key in e){
//		_dump("ag_ann_init():e."+key+"=["+e[key]+"]");
//	}
//}



}




Ext.override(Ext.Panel, {
	addTool: function(){
		if(!this[this.toolTarget]) {
			return;
		}
		if(!this.toolTemplate){
			var tt = new Ext.Template(
				 '<div class="x-tool x-tool-{id}">&#160;</div>'
			);
			tt.disableFormats = true;
			tt.compile();
			Ext.Panel.prototype.toolTemplate = tt;
		}
		for(var i = 0, a = arguments, len = a.length; i < len; i++) {
			var tc = a[i], overCls = 'x-tool-'+tc.id+'-over';
			var t = this.toolTemplate.insertFirst((tc.align !== 'left') ? this[this.toolTarget] : this[this.toolTarget].child('span'), tc, true);
			this.tools[tc.id] = t;
			t.enableDisplayMode('block');
			t.on('click', this.createToolHandler(t, tc, overCls, this));
			if(tc.on){
				t.on(tc.on);
			}
			if(tc.hidden){
				t.hide();
			}
			t.enable = this.enableTool;
			t.disable = this.disableTool;
			if (tc.disabled) {
				t.disable();
			}
			if(tc.qtip){
				if(typeof tc.qtip == 'object'){
					Ext.QuickTips.register(Ext.apply({
						  target: t.id
					}, tc.qtip));
				} else {
					t.dom.qtip = tc.qtip;
				}
			}
			t.addClassOnOver(overCls);
		}
	},
	createToolHandler: function(t, tc, overCls, panel){
		return function(e){
			t.removeClass(overCls);
			e.stopEvent();
			if(tc.handler && !t.disabled){
				tc.handler.call(tc.scope || t, e, t, panel);
			}
		};
	},
	enableTool: function() {
		this.disabled = false;
		this.removeClass('x-item-disabled');
	},
	disableTool: function() {
		this.disabled = true;
		this.addClass('x-item-disabled');
	}
});










/**
 * Create a DragZone instance for our JsonView
 */
ImageDragZone = function(view, config){
	this.view = view;
	ImageDragZone.superclass.constructor.call(this, view.getEl(), config);
};
Ext.extend(ImageDragZone, Ext.dd.DragZone, {
	getDragData : function(e){
		var target = e.getTarget('.thumb-wrap');
		if(!target) target = e.getTarget('.thumb-list-wrap');
HTML
if($useContentsTree eq 'true'){
}
print <<HTML;
		if(target){
			var view = this.view;
			if(!view.isSelected(target)){
				view.onClick(e);
			}
			var selNodes = view.getSelectedNodes();
			var dragData = {
				nodes: selNodes
			};
			if(selNodes.length == 1){
				dragData.ddel = target;
				dragData.single = true;
			}else{
				var div = document.createElement('div'); // create the multi element drag "ghost"
				div.className = 'multi-proxy';
				for(var i = 0, len = selNodes.length; i < len; i++){
					div.appendChild(selNodes[i].firstChild.firstChild.cloneNode(true)); // image nodes only
					if((i+1) % 3 == 0){
						div.appendChild(document.createElement('br'));
					}
				}
				var count = document.createElement('div'); // selected image count
				count.innerHTML = i + ' images selected';
				div.appendChild(count);

				dragData.ddel = div;
				dragData.multi = true;
			}
			dragData.selections = view.getSelectedRecords();
			return dragData;
		}
		return false;
	},

	afterRepair:function(){
		for(var i = 0, len = this.dragData.nodes.length; i < len; i++){
			Ext.fly(this.dragData.nodes[i]).frame('#8db2e3', 1);
		}
		this.dragging = false;
	}
});

Ext.grid.CheckColumn = function(config){
	Ext.apply(this, config);
	if(!this.id){
		this.id = Ext.id();
	}
	this.renderer = this.renderer.createDelegate(this);
};

Ext.grid.CheckColumn.prototype ={
	init : function(grid){
		this.grid = grid;
		this.grid.on('render', function(){
			var view = this.grid.getView();
			view.mainBody.on('mousedown', this.onMouseDown, this);
		}, this);
	},

	onMouseDown : function(e, t){
		if(t.className && t.className.indexOf('x-grid3-cc-'+this.id) != -1){
			e.stopEvent();
			var index = this.grid.getView().findRowIndex(t);
			var record = this.grid.store.getAt(index);
			var param = {
				grid   : this.grid,
				record : record,
				field  : this.dataIndex,
				value  : record.data[this.dataIndex],
				row    : index,
				column : this.grid.getColumnModel().findColumnIndex(this.dataIndex),
				cancel : false
			};
			if(this.grid.fireEvent('beforeedit',param) && param.cancel == false){
				record.set(this.dataIndex, !record.data[this.dataIndex]);
				param.value = record.data[this.dataIndex];
				param.originalValue = !record.data[this.dataIndex];
				delete param.cancel;
				this.grid.fireEvent('afteredit',param)
			}
		}
	},

	renderer : function(v, p, record){
		p.css += ' x-grid3-check-col-td';
		return '<div class="x-grid3-check-col'+(v?'-on':'')+' x-grid3-cc-'+this.id+'">&#160;</div>';
	}
};






var bp3d_open_link_window = function(rep_id){
//	alert('link');

	var win = Ext.getCmp('bp3d-link-window');
	if(!Ext.isEmpty(win)){
		win.rep_id = rep_id;
		win.show(Ext.get('bp3d-link-a-link'));
		return false;
	}

	var bp3d_link_window = new Ext.Window({
		id          : 'bp3d-link-window',
		title       : 'Icon URL',
		width       : 450,
		height      : 170,
		layout      : 'form',
		plain       : true,
		bodyStyle   : 'padding:5px;',
		buttonAlign : 'center',
		modal       : true,
		resizable   : false,
		contentEl   : 'bp3d-link-window-contentEl',
		closeAction : 'hide',
		buttons : [{
			text    : 'OK',
			handler : function(){
				Ext.getCmp('bp3d-link-window').hide(Ext.get('bp3d-link-a-link'));
			}
		}],
		listeners : {
			beforeshow: function(comp){
				_dump("beforeshow():["+comp.id+"]");

				if(Ext.isEmpty(comp.loadMask) || typeof comp.loadMask == 'boolean') comp.loadMask = new Ext.LoadMask(comp.body,{removeMask:false});

				var button = Ext.getCmp('bp3d-link-window-image-re-use-size-s-button');
				button.suspendEvents(false);
				button.setValue(true);
				button.resumeEvents();

				var button = Ext.getCmp('bp3d-link-window-image-re-use-size-l-button');
				button.suspendEvents(false);
				button.setValue(false);
				button.resumeEvents();


				button.fireEvent('check',button,true);

			},
			show: function(comp){
				_dump("show():["+comp.id+"]");
			},
			render: function(win){
				win.rep_id = rep_id;
				_dump("render():["+win.id+"]");
				if(Ext.isEmpty(win.loadMask) || typeof win.loadMask == 'boolean') win.loadMask = new Ext.LoadMask(win.body,{removeMask:false});

					var change_link_value = function(){
						var s = 'S';
						if(Ext.getCmp('bp3d-link-window-image-re-use-size-l-button').getValue()){
							s = 'L';
						}
						var p='rotate';
						if(Ext.getCmp('bp3d-link-window-image-re-use-view-f-button').getValue()){
							p='front';
						}else if(Ext.getCmp('bp3d-link-window-image-re-use-view-b-button').getValue()){
							p='back';
						}else if(Ext.getCmp('bp3d-link-window-image-re-use-view-l-button').getValue()){
							p='left';
						}else if(Ext.getCmp('bp3d-link-window-image-re-use-view-r-button').getValue()){
							p='right';
						}

						var comp = Ext.getCmp('bp3d-link-window');

						var editURL = getEditUrl();
						editURL += 'icon.cgi?i='+comp.rep_id+'&s='+s+'&p='+p;

						Ext.getCmp('bp3d-link-window-image-re-use-still-textfield').setValue(editURL);
					};
					var show_link_image = function(url){
						var size = 'width=120,height=120';
						if(Ext.getCmp('bp3d-link-window-image-re-use-size-l-button').getValue()){
							size = 'width=640,height=640';
						}
						if(url && size) window.open(url, "_blank", "titlebar=no,toolbar=yes,status=no,menubar=yes,"+size);
					};

//					new Ext.form.Label({
//						renderTo : 'bp3d-link-window-image-re-use-label-renderTo',
//						id       : 'bp3d-link-window-image-re-use-label',
//						html     : get_ag_lang('BP3D_MODEL_ICON_LABEL')
//					});

					new Ext.form.Label({
						renderTo : 'bp3d-link-window-image-re-use-view-label-renderTo',
						id       : 'bp3d-link-window-image-re-use-view-label',
						html     : 'View&nbsp;'
					});
					new Ext.form.Radio({
						renderTo : 'bp3d-link-window-image-re-use-view-rotate-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-view-rotate-button',
						name     : 'bp3d-link-window-image-re-use-view-radio',
						checked  : true,
						boxLabel : get_ag_lang('IMAGE_POSITION_ROTATE'),
						value    : 'rotate',
						listeners : {
							check: function(checkbox,checked){
								if(!checked) return;
								change_link_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'bp3d-link-window-image-re-use-view-f-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-view-f-button',
						name     : 'bp3d-link-window-image-re-use-view-radio',
						boxLabel : get_ag_lang('IMAGE_POSITION_FRONT'),
						value    : 'front',
						listeners : {
							check: function(checkbox,checked){
								if(!checked) return;
								change_link_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'bp3d-link-window-image-re-use-view-b-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-view-b-button',
						name     : 'bp3d-link-window-image-re-use-view-radio',
						boxLabel : get_ag_lang('IMAGE_POSITION_BACK'),
						value    : 'back',
						listeners : {
							check: function(checkbox,checked){
								if(!checked) return;
								change_link_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'bp3d-link-window-image-re-use-view-l-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-view-l-button',
						name     : 'bp3d-link-window-image-re-use-view-radio',
						boxLabel : get_ag_lang('IMAGE_POSITION_LEFT'),
						value    : 'left',
						listeners : {
							check: function(checkbox,checked){
								if(!checked) return;
								change_link_value();
							}
						}
					});
					new Ext.form.Radio({
						renderTo : 'bp3d-link-window-image-re-use-view-r-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-view-r-button',
						name     : 'bp3d-link-window-image-re-use-view-radio',
						boxLabel : get_ag_lang('IMAGE_POSITION_RIGHT'),
						value    : 'right',
						listeners : {
							check: function(checkbox,checked){
								if(!checked) return;
								change_link_value();
							}
						}
					});

					new Ext.form.Label({
						renderTo : 'bp3d-link-window-image-re-use-size-label-renderTo',
						id       : 'bp3d-link-window-image-re-use-size-label',
						html     : 'Size&nbsp;'
					});
					new Ext.form.Radio({
						renderTo : 'bp3d-link-window-image-re-use-size-s-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-size-s-button',
						name     : 'bp3d-link-window-image-re-use-size-radio',
						checked  : true,
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
						renderTo : 'bp3d-link-window-image-re-use-size-l-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-size-l-button',
						name     : 'bp3d-link-window-image-re-use-size-radio',
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
						renderTo : 'bp3d-link-window-image-re-use-still-label-renderTo',
						id       : 'bp3d-link-window-image-re-use-still-label',
						html     : 'URL'
					});
					new Ext.form.TextField({
						renderTo : 'bp3d-link-window-image-re-use-still-textfield-renderTo',
						id       : 'bp3d-link-window-image-re-use-still-textfield',
						style    : 'width:100%;',
						selectOnFocus : true,
						readOnly      : true,
						listeners : {
							render: function(comp){
								_dump("render():["+comp.id+"]");
							}
						}
					});
					new Ext.Button({
						renderTo : 'bp3d-link-window-image-re-use-still-button-renderTo',
						id       : 'bp3d-link-window-image-re-use-still-button',
						text    : 'show Icon',
						listeners : {
							click: function(comp){
								_dump("click():["+comp.id+"]");
								show_link_image(Ext.getCmp('bp3d-link-window-image-re-use-still-textfield').getValue());
							}
						}
					});


			}
		}
	});
	bp3d_link_window.show(Ext.get('bp3d-link-a-link'));
	return false;
};

var bp3d_change_location = function(loc,clear){
	if(Ext.isEmpty(clear)) clear = false;
//_dump("bp3d_change_location():["+clear+"]");
	if(!Ext.isEmpty(gBP3D_TPAP)) gBP3D_TPAP = undefined;

	if(clear){
		Cookies.clear('ag_annotation.images.fmaid');
		_bp3d_change_location_hash = {};
		_bp3d_change_location_stack = [];

		var url = getEditUrl() + "location.html";
		if(url != _location.location.href){
			if(loc){
				\$('iframe#_location').one('load',function(){
					_bp3d_change_location(loc);
				});
			}
			_location.location.href = url;
		}else{
			if(loc) _bp3d_change_location(loc);
		}
	}else{
		if(loc) _bp3d_change_location(loc);
	}

};

var _prev_bp3d_change_location;
var _bp3d_change_location_hash = {};
var _bp3d_change_location_stack = [];
var _bp3d_change_location = function(loc){

//	_dump("_bp3d_change_location():ag_annotation.images.fmaid=["+Cookies.get('ag_annotation.images.fmaid')+"]");

	var date = new Date();
//	var href = '_dc='+date.getTime()+'&';
	var time = date.getTime()+"";
	var href = '_dc='+time;

	if(loc.length>=2048-(href.length)){
		href += '&' + loc.substr(0,2048-(href.length)) + '#'+ loc;
//		href += '#' + loc;
	}else{
		href += '&' + loc;
	}
	if(_prev_bp3d_change_location==href) return;

	var s = Ext.urlDecode(_location.location.search.substr(1));
	if(s && s._dc && _bp3d_change_location_hash[s._dc]){
		Ext.each(_bp3d_change_location_stack,function(v,i,a){
			if(v!=s._dc) return true;
			for(var j=i+1;j<a.length;j++){
				delete _bp3d_change_location_hash[a[j]];
			}
			a.length = i+1;
			return false;
		});
	}

	_bp3d_change_location_hash[time] = Ext.urlDecode(loc);
	_bp3d_change_location_stack.push(time);

	var sel_id = Cookies.get('ag_annotation.images.fmaid');
	if(sel_id) _bp3d_change_location_hash[time].sel_id = sel_id;

	_location.location.href = "location.html?" + '_dc='+time;
	_prev_bp3d_change_location=href;
};

HTML
