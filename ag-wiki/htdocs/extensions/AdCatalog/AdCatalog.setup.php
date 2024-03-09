<?php

if (!defined('MEDIAWIKI')) {
	exit( 1 );
}

define('MEDIAWIKI_ADCATALOG_VERSION', '0.0.1');

$wgAdCatalogDBserver         = "127.0.0.1";
$wgAdCatalogDBport           = "5432";
#$wgAdCatalogDBport           = "32433";
$wgAdCatalogDBname           = "abcatalog_db2";
$wgAdCatalogDBuser           = "postgres";
$wgAdCatalogDBpassword       = "";
$wgAdCatalogAuthOpenID       = "http://lifesciencedb.jp/lsdb_ag_auth.cgi?openid_url=";

#DEBUG
$wgAdCatalogDefOpenID        = "http://openid.dbcls.jp/user/tyamamot";
#$wgAdCatalogDefOpenID        = null;

$wgCustomVariables = array('USER_LANGUAGE');

$wgExtensionCredits['other'][] = array(
	'name' => 'AdCatalog',
	'version' => MEDIAWIKI_ADCATALOG_VERSION,
	'author' => 'BITS',
	'url' => 'http://www.mediawiki.org/wiki/Extension:AdCatalog',
	'description' => 'AdCatalog',
	'descriptiomsg' => 'adcatalog-desc',
);

$dir = dirname( __FILE__ ) . '/';
$wgExtensionMessagesFiles['AdCatalog'] = $dir . 'AdCatalog.i18n.php';
#$wgExtensionAliasesFiles['AdCatalog'] = $dir . 'AdCatalog.alias.php';
$wgAutoloadClasses['AdCatalogHooks'] = $dir . 'AdCatalog.hooks.php';
$wgAutoloadClasses['AdCatalogDB'] = $dir . 'AdCatalog.db.php';

$wgHooks['UserLoginComplete'][]          = 'AdCatalogHooks::onUserLoginComplete';
$wgHooks['AbortMove'][]                  = 'AdCatalogHooks::onAbortMove';
$wgHooks['TitleMoveComplete'][]          = 'AdCatalogHooks::onTitleMoveComplete';
$wgHooks['AlternateEdit'][]              = 'AdCatalogHooks::onAlternateEdit';
$wgHooks['ArticleDelete'][]              = 'AdCatalogHooks::onArticleDelete';
$wgHooks['ArticleDeleteComplete'][]      = 'AdCatalogHooks::onArticleDeleteComplete';
$wgHooks['ArticleInsertComplete'][]      = 'AdCatalogHooks::onArticleInsertComplete';
$wgHooks['ArticleProtect'][]             = 'AdCatalogHooks::onArticleProtect';
$wgHooks['ArticleProtectComplete'][]     = 'AdCatalogHooks::onArticleProtectComplete';
$wgHooks['ArticleSave'][]                = 'AdCatalogHooks::onArticleSave';
$wgHooks['ArticleSaveComplete'][]        = 'AdCatalogHooks::onArticleSaveComplete';
$wgHooks['SkinTemplateContentActions'][] = 'AdCatalogHooks::onSkinTemplateContentActions';
$wgHooks['BeforePageDisplay'][]          = 'AdCatalogHooks::onBeforePageDisplay';
$wgHooks['OutputPageBeforeHTML'][]       = 'AdCatalogHooks::onOutputPageBeforeHTML';

$wgHooks['MagicWordMagicWords'][]          = 'AdCatalogHooks::onMagicWordMagicWords';
$wgHooks['MagicWordwgVariableIDs'][]       = 'AdCatalogHooks::onMagicWordwgVariableIDs';
$wgHooks['LanguageGetMagic'][]             = 'AdCatalogHooks::onLanguageGetMagic';
$wgHooks['ParserGetVariableValueSwitch'][] = 'AdCatalogHooks::onParserGetVariableValueSwitch';

$wgHooks['ArticleAfterFetchContent'][]                  = 'AdCatalogHooks::onArticleAfterFetchContent';
$wgHooks['ArticleEditUpdateNewTalk'][]                  = 'AdCatalogHooks::onArticleEditUpdateNewTalk';
$wgHooks['ArticleEditUpdates'][]                        = 'AdCatalogHooks::onArticleEditUpdates';
$wgHooks['ArticleEditUpdatesDeleteFromRecentchanges'][] = 'AdCatalogHooks::onArticleEditUpdatesDeleteFromRecentchanges';
$wgHooks['ArticlePageDataAfter'][]                      = 'AdCatalogHooks::onArticlePageDataAfter';
$wgHooks['ArticlePageDataBefore'][]                     = 'AdCatalogHooks::onArticlePageDataBefore';
$wgHooks['ArticlePurge'][]                              = 'AdCatalogHooks::onArticlePurge';
$wgHooks['ArticleRollbackComplete'][]                   = 'AdCatalogHooks::onArticleRollbackComplete';
$wgHooks['ArticleUpdateBeforeRedirect'][]               = 'AdCatalogHooks::onArticleUpdateBeforeRedirect';
$wgHooks['ArticleViewRedirect'][]                       = 'AdCatalogHooks::onArticleViewRedirect';
$wgHooks['ArticleViewHeader'][]                         = 'AdCatalogHooks::onArticleViewHeader';
$wgHooks['DisplayOldSubtitle'][]                        = 'AdCatalogHooks::onDisplayOldSubtitle';
$wgHooks['IsFileCacheable'][]                           = 'AdCatalogHooks::onIsFileCacheable';
$wgHooks['NewRevisionFromEditComplete'][]               = 'AdCatalogHooks::onNewRevisionFromEditComplete';
$wgHooks['ShowRawCssJs'][]                              = 'AdCatalogHooks::onShowRawCssJs';
$wgHooks['UnwatchArticle'][]                            = 'AdCatalogHooks::onUnwatchArticle';
$wgHooks['UnwatchArticleComplete'][]                    = 'AdCatalogHooks::onUnwatchArticleComplete';
$wgHooks['WatchArticle'][]                              = 'AdCatalogHooks::onWatchArticle';
$wgHooks['WatchArticleComplete'][]                      = 'AdCatalogHooks::onWatchArticleComplete';
