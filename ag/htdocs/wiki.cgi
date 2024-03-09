#!/bp3d/local/perl/bin/perl

$| = 1;

use lib 'IM';

use strict;
use DBI;
use DBD::Pg;
use JSON::XS;
#use Image::Magick;
use File::Basename;
use POSIX qw(strftime);
use HTTP::Date;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

require "common.pl";
require "common_db.pl";
require "common_image.pl";
require "common_wiki.pl";
my $dbh = &get_dbh();

my @extlist = qw|.cgi|;
my($name,$dir,$ext) = fileparse($0,@extlist);

my $query = CGI->new;
my @params = $query->param();
my %PARAMS = ();
foreach my $param (@params){
	$PARAMS{$param} = defined $query->param($param) ? $query->param($param) : undef;
	$PARAMS{$param} = undef if(defined $PARAMS{$param} && length($PARAMS{$param})==0);
}

#my %FORM = ();
#&decodeForm(\%FORM);
#delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);


my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
my $session = defined $COOKIE{'ag_annotation.session'} && length($COOKIE{'ag_annotation.session'})>0 ? $COOKIE{'ag_annotation.session'} : $COOKIE{'ag_annotation_session'};
open(LOG,">> logs/$cgi_name.$session.txt");
flock(LOG,2);
print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
foreach my $key (sort keys(%PARAMS)){
	print LOG __LINE__,":\$PARAMS{$key}=[",$PARAMS{$key},"]\n";
}
foreach my $key (sort keys(%COOKIE)){
	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
}
foreach my $key (sort keys(%ENV)){
	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
}
=pod
print qq|Content-type: text/html;\n\n|;
my $base = qq|js/extjs-4.1.1|;
my $css_path = qq|$base/ag-wiki/css/$PARAMS{type}.css|;
my $js_path = qq|$base/ag-wiki/$PARAMS{type}.js|;
if(-e $css_path || -e $js_path){
	undef $css_path unless(-e $css_path);
	undef $js_path unless(-e $js_path);
	print <<HTML;
<html>
<head>
<link rel="stylesheet" href="$base/resources/css/ext-all.css" />
<link rel="stylesheet" href="$css_path" />
<script type="text/javascript" src="$base/ext-all-dev.js"></script>
<script type="text/javascript" src="$js_path"></script>
<script type="text/javascript">
Ext.BLANK_IMAGE_URL = "$base/resources/themes/images/default/tree/s.gif";
</script>
</head>
<body>
</body>
</html>
HTML
}
=cut
#DEBUG
=pod
$PARAMS{article}='{"mComment":"","mContent":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\n}}","mContentLoaded":true,"mCounter":6,"mCurID":-1,"mDataLoaded":true,"mForUpdate":true,"mGoodAdjustment":0,"mIsRedirect":0,"mLatest":150570,"mMinorEdit":false,"mOldId":0,"mPreparedEdit":{"revid":null,"newText":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\u66f8\u8fbc\u307f\u306e\u30c6\u30b9\u30c8\n}}","pst":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\u66f8\u8fbc\u307f\u306e\u30c6\u30b9\u30c8\n}}","output":{"mText":"<h2><span class=\"editsection\">[<a href=\"\/bp3d-38321\/wiki\/index.php?title=FMA20394\/Detail&amp;action=edit&amp;section=1\" title=\"Edit section: Detail\">edit<\/a>]<\/span> <span class=\"mw-headline\" id=\"Detail\">Detail<\/span><\/h2>\n<div class=\"fma_detail\"><table class=\"fma_detail\">\n<tr><td class=\"fma_detail_title\">ID<\/td><td class=\"fma_detail_colon\">:<\/td><td><a href=\"\/bp3d-38321\/wiki\/index.php\/FMA20394\" title=\"FMA20394\">FMA20394<\/a><\/td><\/tr><tr><td class=\"fma_detail_title\">Name<\/td><td class=\"fma_detail_colon\">:<\/td><td>Human body<\/td><\/tr><tr><td class=\"fma_detail_title\">(Jpn)<\/td><td class=\"fma_detail_colon\">:<\/td><td>\u4eba\u4f53<\/td><\/tr><tr><td class=\"fma_detail_title\">(Kana)<\/td><td class=\"fma_detail_colon\">:<\/td><td>\u3058\u3093\u305f\u3044<\/td><\/tr><tr><td class=\"fma_detail_title\">(Jpn)<\/td><td class=\"fma_detail_colon\">:<\/td><td>\u66f8\u8fbc\u307f\u306e\u30c6\u30b9\u30c8<\/td><\/tr><\/table><\/div>\n<p><br \/>\n<\/p>\n<!-- \nNewPP limit report\nPreprocessor node count: 76\/1000000\nPost-expand include size: 1127\/2097152 bytes\nTemplate argument size: 132\/2097152 bytes\nExpensive parser function count: 2\/100\nExtLoops count: 0\/100\n-->\n\n<!-- Saved in parser cache with key ag_wiki:pcache:idhash:137076-0!1!0!!en!2 and timestamp 20121221081843 -->\n","mLanguageLinks":[],"mCategories":[],"mContainsOldMagic":false,"mTitleText":"FMA20394\/Detail","mCacheTime":"20121221081843","mVersion":"1.6.4","mLinks":[{"FMA20394":4,"Human_body":0}],"mTemplates":{"10":{"FMA\/Detail":132325}},"mTemplateIds":{"10":{"FMA\/Detail":1049781}},"mImages":[],"mExternalLinks":[],"mNewSection":false,"mHideNewSection":false,"mNoGallery":false,"mHeadItems":[],"mOutputHooks":[],"mWarnings":[],"mSections":[{"toclevel":1,"level":"2","line":"Detail","number":"1","index":"1","fromtitle":"FMA20394\/Detail","byteoffset":0,"anchor":"Detail"}],"mProperties":[],"mTOCHTML":"","mTimestamp":"20121221081843"},"oldText":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\n}}"},"mRedirectedFrom":null,"mRedirectTarget":null,"mRedirectUrl":false,"mRevIdFetched":150570,"mRevision":{"mId":150570,"mPage":137076,"mTextId":150570,"mComment":"","mUserText":"Gogo","mUser":1,"mMinorEdit":0,"mTimestamp":"2012-11-29 06:53:32+00","mDeleted":0,"mParentId":150558,"mSize":179,"mCurrent":true,"mTitle":{"mTextform":"FMA20394\/Detail","mUrlform":"FMA20394\/Detail","mDbkeyform":"FMA20394\/Detail","mUserCaseDBKey":null,"mNamespace":0,"mInterwiki":"","mFragment":"","mArticleID":137076,"mLatestID":false,"mRestrictions":[],"mOldRestrictions":false,"mCascadeRestriction":null,"mRestrictionsExpiry":[],"mHasCascadingRestrictions":null,"mCascadeSources":null,"mRestrictionsLoaded":false,"mPrefixedText":null,"mDefaultNamespace":0,"mWatched":null,"mLength":-1,"mRedirect":null,"mNotificationTimestamp":[],"mBacklinkCache":null},"mText":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\n}}","mTextRow":null,"mUnpatrolled":null},"mTimestamp":"20121221081843","mTitle":{"mTextform":"FMA20394\/Detail","mUrlform":"FMA20394\/Detail","mDbkeyform":"FMA20394\/Detail","mUserCaseDBKey":"FMA20394\/Detail","mNamespace":0,"mInterwiki":"","mFragment":"","mArticleID":137076,"mLatestID":false,"mRestrictions":{"edit":[],"move":[]},"mOldRestrictions":false,"mCascadeRestriction":false,"mRestrictionsExpiry":{"edit":"infinity","move":"infinity"},"mHasCascadingRestrictions":null,"mCascadeSources":[],"mRestrictionsLoaded":true,"mPrefixedText":"FMA20394\/Detail","mDefaultNamespace":0,"mWatched":null,"mLength":-1,"mRedirect":null,"mNotificationTimestamp":[],"mBacklinkCache":{"partitionCache":{"templatelinks":{"500":{"numRows":1,"batches":[[false,false]]}}},"fullResultCache":{"templatelinks":{"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"},"result":null,"pos":1,"currentRow":{"page_namespace":"0","page_title":"FMA20394","page_id":"4"}}},"title":null,"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"}},"mCascadingRestrictions":[]},"mTotalAdjustment":0,"mTouched":"20121221081300","mUser":1,"mUserText":"Gogo","mParserOptions":{"mUseDynamicDates":false,"mInterwikiMagic":true,"mAllowExternalImages":true,"mAllowExternalImagesFrom":"","mEnableImageWhitelist":true,"mSkin":{"skinname":"monobook","stylename":"monobook","template":"MonoBookTemplate","useHeadElement":true,"mWatchLinkNum":0,"mTitle":{"mTextform":"FMA20394\/Detail","mUrlform":"FMA20394\/Detail","mDbkeyform":"FMA20394\/Detail","mUserCaseDBKey":"FMA20394\/Detail","mNamespace":0,"mInterwiki":"","mFragment":"","mArticleID":137076,"mLatestID":false,"mRestrictions":{"edit":[],"move":[]},"mOldRestrictions":false,"mCascadeRestriction":false,"mRestrictionsExpiry":{"edit":"infinity","move":"infinity"},"mHasCascadingRestrictions":null,"mCascadeSources":[],"mRestrictionsLoaded":true,"mPrefixedText":"FMA20394\/Detail","mDefaultNamespace":0,"mWatched":null,"mLength":-1,"mRedirect":null,"mNotificationTimestamp":[],"mBacklinkCache":{"partitionCache":{"templatelinks":{"500":{"numRows":1,"batches":[[false,false]]}}},"fullResultCache":{"templatelinks":{"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"},"result":null,"pos":1,"currentRow":{"page_namespace":"0","page_title":"FMA20394","page_id":"4"}}},"title":null,"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"}},"mCascadingRestrictions":[]}},"mDateFormat":null,"mEditSection":true,"mNumberHeadings":0,"mAllowSpecialInclusion":true,"mTidy":true,"mInterfaceMessage":false,"mTargetLanguage":null,"mMaxIncludeSize":2097152,"mMaxPPNodeCount":1000000,"mMaxPPExpandDepth":40,"mMaxTemplateDepth":40,"mRemoveComments":true,"mTemplateCallback":["Parser","statelessFetchTemplate"],"mEnableLimitReport":true,"mTimestamp":null,"mExternalLinkTarget":false,"mUser":{"mId":2,"mName":"Tyamamot","mRealName":"","mPassword":"","mNewpassword":"","mNewpassTime":null,"mEmail":"tyamamot@bits.cc","mTouched":"20121221081848","mToken":"8c8514bd26c51cd21d5cf330579b09aa","mEmailAuthenticated":null,"mEmailToken":null,"mEmailTokenExpires":null,"mRegistration":"20121128075523","mGroups":["bp3d"],"mOptionOverrides":{"nickname":"tyamamot"},"mDataLoaded":true,"mAuthLoaded":null,"mOptionsLoaded":true,"mFrom":"session","mNewtalk":-1,"mDatePreference":null,"mBlockedby":0,"mHash":"1!0!!en!2","mSkin":{"skinname":"monobook","stylename":"monobook","template":"MonoBookTemplate","useHeadElement":true,"mWatchLinkNum":0,"mTitle":{"mTextform":"FMA20394\/Detail","mUrlform":"FMA20394\/Detail","mDbkeyform":"FMA20394\/Detail","mUserCaseDBKey":"FMA20394\/Detail","mNamespace":0,"mInterwiki":"","mFragment":"","mArticleID":137076,"mLatestID":false,"mRestrictions":{"edit":[],"move":[]},"mOldRestrictions":false,"mCascadeRestriction":false,"mRestrictionsExpiry":{"edit":"infinity","move":"infinity"},"mHasCascadingRestrictions":null,"mCascadeSources":[],"mRestrictionsLoaded":true,"mPrefixedText":"FMA20394\/Detail","mDefaultNamespace":0,"mWatched":null,"mLength":-1,"mRedirect":null,"mNotificationTimestamp":[],"mBacklinkCache":{"partitionCache":{"templatelinks":{"500":{"numRows":1,"batches":[[false,false]]}}},"fullResultCache":{"templatelinks":{"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"},"result":null,"pos":1,"currentRow":{"page_namespace":"0","page_title":"FMA20394","page_id":"4"}}},"title":null,"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"}},"mCascadingRestrictions":[]}},"mRights":["autoconfirmed","createpage","createtalk","edit","minoredit","move","move-subpages","purge","read","reupload","reupload-shared","upload","writeapi","createaccount","sendemail"],"mBlockreason":null,"mBlock":{"mAddress":"","mUser":0,"mBy":0,"mReason":"","mTimestamp":"","mAuto":0,"mId":0,"mExpiry":"infinity","mRangeStart":false,"mRangeEnd":false,"mAnonOnly":0,"mEnableAutoblock":0,"mHideName":0,"mBlockEmail":0,"mByName":false,"mAngryAutoblock":false,"mAllowUsertalk":0,"mNetworkBits":null,"mIntegerAddr":null,"mForUpdate":false,"mFromMaster":true,"mCreateAccount":0},"mEffectiveGroups":["bp3d","*","user","autoconfirmed"],"mBlockedGlobally":null,"mLocked":null,"mHideName":0,"mOptions":{"quickbar":1,"underline":2,"cols":80,"rows":25,"searchlimit":20,"contextlines":5,"contextchars":50,"disablesuggest":0,"skin":"monobook","math":1,"usenewrc":0,"rcdays":7,"rclimit":50,"wllimit":250,"hideminor":0,"hidepatrolled":0,"newpageshidepatrolled":0,"highlightbroken":1,"stubthreshold":0,"previewontop":1,"previewonfirst":0,"editsection":1,"editsectiononrightclick":0,"editondblclick":0,"editwidth":0,"showtoc":1,"showtoolbar":1,"minordefault":0,"date":"default","imagesize":2,"thumbsize":2,"rememberpassword":0,"nocache":0,"diffonly":0,"showhiddencats":0,"norollbackdiff":0,"enotifwatchlistpages":0,"enotifusertalkpages":1,"enotifminoredits":0,"enotifrevealaddr":0,"shownumberswatching":1,"fancysig":0,"externaleditor":0,"externaldiff":0,"forceeditsummary":0,"showjumplinks":1,"justify":0,"numberheadings":0,"uselivepreview":0,"watchlistdays":3,"extendwatchlist":0,"watchlisthideminor":0,"watchlisthidebots":0,"watchlisthideown":0,"watchlisthideanons":0,"watchlisthideliu":0,"watchlisthidepatrolled":0,"watchcreations":0,"watchdefault":0,"watchmoves":0,"watchdeletion":0,"noconvertlink":0,"gender":"unknown","ccmeonemails":0,"disablemail":0,"editfont":"default","openid-hide":0,"openid-update-on-login-nickname":false,"openid-update-on-login-email":false,"openid-update-on-login-fullname":false,"openid-update-on-login-language":false,"openid-update-on-login-timezone":false,"variant":"en","language":"en","searchNs0":true,"searchNs1":false,"searchNs2":false,"searchNs3":false,"searchNs4":false,"searchNs5":false,"searchNs6":false,"searchNs7":false,"searchNs8":false,"searchNs9":false,"searchNs10":false,"searchNs11":false,"searchNs12":false,"searchNs13":false,"searchNs14":false,"searchNs15":false,"searchNs100":false,"searchNs101":false,"searchNs102":false,"searchNs103":false,"searchNs104":false,"searchNs105":false,"searchNs106":false,"searchNs107":false,"searchNs108":false,"searchNs109":false,"searchNs110":false,"searchNs111":false,"searchNs112":false,"searchNs113":false,"searchNs114":false,"searchNs115":false,"searchNs116":false,"searchNs117":false,"searchNs118":false,"searchNs119":false,"searchNs120":false,"searchNs121":false,"searchNs122":false,"searchNs123":false,"nickname":"tyamamot"},"mEditCount":"43","mAllowUsertalk":0},"mIsPreview":false,"mIsSectionPreview":false,"mIsPrintable":null,"mCleanSignatures":true},"mParserOutput":null,"mLastRevision":{"mId":150570,"mPage":137076,"mTextId":150570,"mComment":"","mUserText":"Gogo","mUser":1,"mMinorEdit":0,"mTimestamp":"2012-11-29 06:53:32+00","mDeleted":0,"mParentId":150558,"mSize":179,"mCurrent":true,"mTitle":{"mTextform":"FMA20394\/Detail","mUrlform":"FMA20394\/Detail","mDbkeyform":"FMA20394\/Detail","mUserCaseDBKey":null,"mNamespace":0,"mInterwiki":"","mFragment":"","mArticleID":137076,"mLatestID":false,"mRestrictions":[],"mOldRestrictions":false,"mCascadeRestriction":null,"mRestrictionsExpiry":[],"mHasCascadingRestrictions":null,"mCascadeSources":null,"mRestrictionsLoaded":false,"mPrefixedText":null,"mDefaultNamespace":0,"mWatched":null,"mLength":-1,"mRedirect":null,"mNotificationTimestamp":[],"mBacklinkCache":null},"mText":null,"mTextRow":null,"mUnpatrolled":null}}';
$PARAMS{baseRevId}='{"ok":true,"value":{"new":false,"revision":{"mId":"1052821","mPage":137076,"mTextId":"1050944","mUserText":"Tyamamot","mUser":2,"mMinorEdit":0,"mTimestamp":"20121221081843","mDeleted":0,"mSize":200,"mParentId":150570,"mComment":"\/* Detail *\/","mText":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\u66f8\u8fbc\u307f\u306e\u30c6\u30b9\u30c8\n}}","mTextRow":null,"mTitle":null,"mCurrent":false,"mUnpatrolled":null}},"successCount":0,"failCount":0,"errors":[],"cleanCallback":false}';
$PARAMS{text}=<<TEXT;
==Detail==
{{Template:FMA/Detail
|id=FMA20394
|taid=
|name_e=Human body
|name_j=人体
|name_k=じんたい
|name_l=
|organ_systems_e=
|organ_systems_j=
|synonym_e=
|synonym_j=書込みのテスト
}}
TEXT
$PARAMS{user}='{"mId":2,"mName":"Tyamamot","mRealName":"","mPassword":"","mNewpassword":"","mNewpassTime":null,"mEmail":"tyamamot@bits.cc","mTouched":"20121221081848","mToken":"8c8514bd26c51cd21d5cf330579b09aa","mEmailAuthenticated":null,"mEmailToken":null,"mEmailTokenExpires":null,"mRegistration":"20121128075523","mGroups":["bp3d"],"mOptionOverrides":{"nickname":"tyamamot"},"mDataLoaded":true,"mAuthLoaded":null,"mOptionsLoaded":true,"mFrom":"session","mNewtalk":-1,"mDatePreference":null,"mBlockedby":0,"mHash":"1!0!!en!2","mSkin":{"skinname":"monobook","stylename":"monobook","template":"MonoBookTemplate","useHeadElement":true,"mWatchLinkNum":0,"mTitle":{"mTextform":"FMA20394\/Detail","mUrlform":"FMA20394\/Detail","mDbkeyform":"FMA20394\/Detail","mUserCaseDBKey":"FMA20394\/Detail","mNamespace":0,"mInterwiki":"","mFragment":"","mArticleID":137076,"mLatestID":false,"mRestrictions":{"edit":[],"move":[]},"mOldRestrictions":false,"mCascadeRestriction":false,"mRestrictionsExpiry":{"edit":"infinity","move":"infinity"},"mHasCascadingRestrictions":null,"mCascadeSources":[],"mRestrictionsLoaded":true,"mPrefixedText":"FMA20394\/Detail","mDefaultNamespace":0,"mWatched":null,"mLength":-1,"mRedirect":null,"mNotificationTimestamp":[],"mBacklinkCache":{"partitionCache":{"templatelinks":{"500":{"numRows":1,"batches":[[false,false]]}}},"fullResultCache":{"templatelinks":{"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"},"result":null,"pos":1,"currentRow":{"page_namespace":"0","page_title":"FMA20394","page_id":"4"}}},"title":null,"db":{"mInsertId":"739247","mLastResult":null,"numeric_version":"8.3.20","mAffectedRows":null,"mPort":"5433","htmlErrors":"1"}},"mCascadingRestrictions":[]}},"mRights":["autoconfirmed","createpage","createtalk","edit","minoredit","move","move-subpages","purge","read","reupload","reupload-shared","upload","writeapi","createaccount","sendemail"],"mBlockreason":null,"mBlock":{"mAddress":"","mUser":0,"mBy":0,"mReason":"","mTimestamp":"","mAuto":0,"mId":0,"mExpiry":"infinity","mRangeStart":false,"mRangeEnd":false,"mAnonOnly":0,"mEnableAutoblock":0,"mHideName":0,"mBlockEmail":0,"mByName":false,"mAngryAutoblock":false,"mAllowUsertalk":0,"mNetworkBits":null,"mIntegerAddr":null,"mForUpdate":false,"mFromMaster":true,"mCreateAccount":0},"mEffectiveGroups":["bp3d","*","user","autoconfirmed"],"mBlockedGlobally":null,"mLocked":null,"mHideName":0,"mOptions":{"quickbar":1,"underline":2,"cols":80,"rows":25,"searchlimit":20,"contextlines":5,"contextchars":50,"disablesuggest":0,"skin":"monobook","math":1,"usenewrc":0,"rcdays":7,"rclimit":50,"wllimit":250,"hideminor":0,"hidepatrolled":0,"newpageshidepatrolled":0,"highlightbroken":1,"stubthreshold":0,"previewontop":1,"previewonfirst":0,"editsection":1,"editsectiononrightclick":0,"editondblclick":0,"editwidth":0,"showtoc":1,"showtoolbar":1,"minordefault":0,"date":"default","imagesize":2,"thumbsize":2,"rememberpassword":0,"nocache":0,"diffonly":0,"showhiddencats":0,"norollbackdiff":0,"enotifwatchlistpages":0,"enotifusertalkpages":1,"enotifminoredits":0,"enotifrevealaddr":0,"shownumberswatching":1,"fancysig":0,"externaleditor":0,"externaldiff":0,"forceeditsummary":0,"showjumplinks":1,"justify":0,"numberheadings":0,"uselivepreview":0,"watchlistdays":3,"extendwatchlist":0,"watchlisthideminor":0,"watchlisthidebots":0,"watchlisthideown":0,"watchlisthideanons":0,"watchlisthideliu":0,"watchlisthidepatrolled":0,"watchcreations":0,"watchdefault":0,"watchmoves":0,"watchdeletion":0,"noconvertlink":0,"gender":"unknown","ccmeonemails":0,"disablemail":0,"editfont":"default","openid-hide":0,"openid-update-on-login-nickname":false,"openid-update-on-login-email":false,"openid-update-on-login-fullname":false,"openid-update-on-login-language":false,"openid-update-on-login-timezone":false,"variant":"en","language":"en","searchNs0":true,"searchNs1":false,"searchNs2":false,"searchNs3":false,"searchNs4":false,"searchNs5":false,"searchNs6":false,"searchNs7":false,"searchNs8":false,"searchNs9":false,"searchNs10":false,"searchNs11":false,"searchNs12":false,"searchNs13":false,"searchNs14":false,"searchNs15":false,"searchNs100":false,"searchNs101":false,"searchNs102":false,"searchNs103":false,"searchNs104":false,"searchNs105":false,"searchNs106":false,"searchNs107":false,"searchNs108":false,"searchNs109":false,"searchNs110":false,"searchNs111":false,"searchNs112":false,"searchNs113":false,"searchNs114":false,"searchNs115":false,"searchNs116":false,"searchNs117":false,"searchNs118":false,"searchNs119":false,"searchNs120":false,"searchNs121":false,"searchNs122":false,"searchNs123":false,"nickname":"tyamamot"},"mEditCount":"43","mAllowUsertalk":0}';
$PARAMS{wgDBname}='ag_wiki';
$PARAMS{wgExtraNamespaces}='{"100":"FMA","101":"FMA_talk","102":"isa","103":"isa_talk","104":"partof","105":"partof_talk","106":"OBJ","107":"OBJ_talk","108":"density","109":"density_talk","110":"FMA_Comment","111":"FMA_Comment_talk","112":"OBJ_Comment","113":"OBJ_Comment_talk","114":"In_Bodyparts3D","115":"In_Bodyparts3D_talk","116":"bp3d","117":"bp3d_talk","118":"FMAtoBP3D","119":"FMAtoBP3D_talk","120":"bp3d_Comment","121":"bp3d_Comment_talk","122":"FENEIS","123":"FENEIS_talk"}';
$PARAMS{openid}='http://openid.dbcls.jp/user/tyamamot';
$PARAMS{revision}='{"mId":"1052821","mPage":137076,"mTextId":"1050944","mUserText":"Tyamamot","mUser":2,"mMinorEdit":0,"mTimestamp":"20121221081843","mDeleted":0,"mSize":200,"mParentId":150570,"mComment":"\/* Detail *\/","mText":"==Detail==\n{{Template:FMA\/Detail\n|id=FMA20394\n|taid=\n|name_e=Human body\n|name_j=\u4eba\u4f53\n|name_k=\u3058\u3093\u305f\u3044\n|name_l=\n|organ_systems_e=\n|organ_systems_j=\n|synonym_e=\n|synonym_j=\u66f8\u8fbc\u307f\u306e\u30c6\u30b9\u30c8\n}}","mTextRow":null,"mTitle":null,"mCurrent":false,"mUnpatrolled":null}';
=cut



my $DATAS = {
	"datas" => [],
	"total" => 0,
	"success" => JSON::XS::false
};

if(exists $PARAMS{'type'} && defined $PARAMS{'type'}){
	if($PARAMS{'type'} eq 'fmalist'){
		$DATAS = &fmalist($dbh,\%PARAMS);
	}elsif($PARAMS{'type'} eq 'objlist'){
		$DATAS = &objlist($dbh,\%PARAMS);
	}elsif($PARAMS{'type'} eq 'representationlist'){
		$DATAS = &representationlist($dbh,\%PARAMS);
	}
}elsif(
	exists $PARAMS{'article'} && defined $PARAMS{'article'} &&
	exists $PARAMS{'baseRevId'} && defined $PARAMS{'baseRevId'} &&
	exists $PARAMS{'revision'} && defined $PARAMS{'revision'} &&
	exists $PARAMS{'text'} && defined $PARAMS{'text'} &&
	exists $PARAMS{'user'} && defined $PARAMS{'user'} &&
	exists $PARAMS{'wgDBname'} && defined $PARAMS{'wgDBname'} &&
	exists $PARAMS{'wgExtraNamespaces'} && defined $PARAMS{'wgExtraNamespaces'}
){
	my $article;
	my $baseRevId;
	my $user;
	my $wgExtraNamespaces;
	my $text = $PARAMS{'text'};
	my $openid = defined $PARAMS{'openid'} && length($PARAMS{'openid'})>0 ? $PARAMS{'openid'} : undef;
	my $wgDBname = $PARAMS{'wgDBname'};

	&utf8::decode($text)     unless(&utf8::is_utf8($text));
	&utf8::decode($wgDBname) unless(&utf8::is_utf8($wgDBname));
	&utf8::decode($wgDBname) unless(&utf8::is_utf8($wgDBname));

	eval{ $article = &JSON::XS::decode_json($PARAMS{'article'}) };
	eval{ $baseRevId = &JSON::XS::decode_json($PARAMS{'baseRevId'}) };
	eval{ $user = &JSON::XS::decode_json($PARAMS{'user'}) };
	eval{ $wgExtraNamespaces = &JSON::XS::decode_json($PARAMS{'wgExtraNamespaces'}) };

	if(defined $article && defined $baseRevId && defined $user && defined $wgExtraNamespaces){
		if($baseRevId->{'ok'}==JSON::XS::true && defined $user->{mRights} && ref $user->{mRights} eq 'ARRAY'){
			my %mRights = map {$_=>undef} @{$user->{mRights}};
			if(exists $mRights{'edit'}){	#編集権限をチェック
				print LOG __LINE__,"\n";
				if(defined $article->{'mTitle'} && defined $article->{'mTitle'}->{'mTextform'} && $article->{'mTitle'}->{'mTextform'} ne ''){
					if($article->{'mTitle'}->{'mTextform'} =~ /^(FMA.+)\/Detail$/){
						my $title_f_id = $1;
						print LOG __LINE__,":",$article->{'mTitle'}->{'mTextform'},"\n";
						print LOG __LINE__,":\$title_f_id=[$title_f_id]\n";
						my %HASH = ();
						if(defined $text){
							foreach my $t (split(/\n/,$text)){
								next unless($t =~ /^\s*\|(.+?)=(.*)$/);
								print LOG __LINE__,":[$1][$2]\n";
								$HASH{$1} = defined $2 && length($2)>0 ? $2 : undef;
							}
						}
						$HASH{'id'} = $title_f_id unless(defined $HASH{'id'});
						$openid = $user->{'mName'} unless(defined $openid);

						$DATAS->{'success'} = JSON::XS::true if(&update_fma($dbh,\%HASH,$openid)>0);
					}
				}
			}
		}
	}
}



my $json = &JSON::XS::encode_json($DATAS);
print qq|Content-type: text/html; charset=UTF-8\n|;
print sprintf(qq|Content-Length: %d\n|,length($json));
#print sprintf(qq|Last-Modified: %s\n|,&HTTP::Date::time2str((stat($cache_file))[9]));
print "\n";
print $json;

close(LOG);

exit;

sub update_fma {
	my $dbh = shift;
	my $params = shift;
	my $openid = shift;

	my $sth_upd = $dbh->prepare(qq|update fma set f_name_j=?,f_name_e=?,f_name_k=?,f_name_l=?,f_syn_j=?,f_syn_e=?,f_modified='now()',m_openid=? where f_id=?|);
	$sth_upd->execute(
		$params->{'name_j'},
		$params->{'name_e'},
		$params->{'name_k'},
		$params->{'name_l'},
		$params->{'synonym_j'},
		$params->{'synonym_e'},
		$openid,
		$params->{'id'}
	);
	my $rows = $sth_upd->rows();
	$sth_upd->finish;
	undef $sth_upd;
	if($rows<1){
		my $sth_ins = $dbh->prepare(qq|insert into fma (f_id,f_name_j,f_name_e,f_name_k,f_name_l,f_syn_j,f_syn_e,f_entry,f_modified,e_openid,m_openid) values (?,?,?,?,?,?,?,'now()','now()',?,?)|);
		$sth_ins->execute(
			$params->{'id'},
			$params->{'name_j'},
			$params->{'name_e'},
			$params->{'name_k'},
			$params->{'name_l'},
			$params->{'synonym_j'},
			$params->{'synonym_e'},
			$openid,
			$openid
		);
		$rows = $sth_ins->rows();
		$sth_ins->finish;
		undef $sth_ins;
	}
	return $rows;
}
