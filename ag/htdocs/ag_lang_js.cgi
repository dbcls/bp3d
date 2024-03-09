#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use JSON::XS;
use Encode;
use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;

require "common.pl";

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
$FORM{lng} = "en" if(!exists($FORM{lng}));

my %LOCALE = ();

require "anatomography_locale.pl";
my %LOCALE_ANA = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_ANA)){
	$LOCALE{$key} = &cgi_lib::common::decodeUTF8($LOCALE_ANA{$key});
}
undef %LOCALE_ANA;

require "common_locale.pl";
my %LOCALE_BP3D = &getLocale($FORM{lng});
foreach my $key (keys(%LOCALE_BP3D)){
	$LOCALE{$key} = &cgi_lib::common::decodeUTF8($LOCALE_BP3D{$key});
}
undef %LOCALE_BP3D;

my @CONTENTS;
push(@CONTENTS,qq|var ag_lang=|.&cgi_lib::common::encodeJSON(\%LOCALE).';');
push(@CONTENTS,qq|
var get_ag_lang = function(key){
	if(!key) return undefined;
	if(ag_lang[key]===undefined && window.console){
		window.console.error('Undefined ['+key+']');
	}
	if(ag_lang[key].match(/^[\\-+]*[0-9\\.]+\$/)){
		return Number(ag_lang[key]);
	}else{
		return ag_lang[key];
	}
};
|);

my $DEF = {
	DEF_COLOR => &getDefaultColor()
};
push(@CONTENTS,qq|var ag_def=|.&cgi_lib::common::encodeJSON($DEF).';');

if(exists $ENV{REQUEST_METHOD}){
	&cgi_lib::common::printContent(join('',@CONTENTS),'application/javascript');
}
else{
	say join('',@CONTENTS);
}
