#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

require "common.pl";
require "common_db.pl";
require "common_locale.pl";
my $dbh = &get_dbh();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

$FORM{lng} = "ja" if(!exists($FORM{lng}));

my %LOCALE = &getLocale($FORM{lng});

print qq|Content-type: text/html; charset=UTF-8\n|;
print qq|\n|;

print <<HTML;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<link rel="stylesheet" href="resources/css/ext-all.css" type="text/css" media="all">
<link rel="stylesheet" href="css/chooser.css" type="text/css"/>
<title>$LOCALE{DOCUMENT_TITLE}</title>
</head>
<body>
HTML

print <<HTML;
<div class="details" style="width:250px;">
	<img src="$FORM{src}" width="120" height="120">
	<div class="details-info">
		<b style="display: inline;">FMAID:</b>
		<span style="display: inline;">$FORM{f_id}</span><br>
	</div>
	<div class="details-info">
		<b>$LOCALE{DETAIL_TITLE_ICON_URL}:</b>
		<span><a href="$FORM{srcstr}" target="_blank">$FORM{srcstr}</a></span>
		<b>$LOCALE{DETAIL_TITLE_NAME_E}:</b>
		<span>$FORM{name_e}</span>
		<b>$LOCALE{DETAIL_TITLE_NAME_J}:</b>
		<span>$FORM{name_j}</span>
		<b>$LOCALE{DETAIL_TITLE_NAME_K}:</b>
		<span>$FORM{name_k}</span>
HTML
if(exists($FORM{name_l})){
	print <<HTML;
		<b>$LOCALE{DETAIL_TITLE_NAME_L}:</b>
		<span>$FORM{name_l}</span>
HTML
}
if(exists($FORM{organsys_e})){
	print <<HTML;
		<b>$LOCALE{DETAIL_TITLE_ORGAN_SYSTEM_E}:</b>
		<span>$FORM{organsys_e}</span>
HTML
}
if(exists($FORM{organsys_j})){
	print <<HTML;
		<b>$LOCALE{DETAIL_TITLE_ORGAN_SYSTEM_J}:</b>
		<span>$FORM{organsys_j}</span>
HTML
}
if(exists($FORM{syn_e})){
	print <<HTML;
		<b>$LOCALE{DETAIL_TITLE_SYNONYM_E}:</b>
		<span>$FORM{syn_e}</span>
HTML
}
if(exists($FORM{syn_j})){
	print <<HTML;
		<b>$LOCALE{DETAIL_TITLE_SYNONYM_J}:</b>
		<span>$FORM{syn_j}</span>
HTML
}
print <<HTML;
		<div class="details-info">
			<b>BodyParts3D Information</b>
			<div style="padding-left: 5px;">
HTML
if(exists($FORM{phase})){
	print <<HTML;
				<b>Phase:</b>
				<span>$FORM{phase}</span>
HTML
}
if(exists($FORM{zmin})){
	print <<HTML;
				<b>$LOCALE{DETAIL_TITLE_ZMIN}:</b>
				<span>$FORM{zmin} mm</span>
HTML
}
if(exists($FORM{zmax})){
	print <<HTML;
				<b>$LOCALE{DETAIL_TITLE_ZMAX}:</b>
				<span>$FORM{zmax} mm</span>
HTML
}
if(exists($FORM{volume})){
	print <<HTML;
				<b>$LOCALE{DETAIL_TITLE_VOLUME}:</b>
				<span>$FORM{volume} cm<sup>3</sup></span>
HTML
}
print <<HTML;
			</div>
		</div>
		<div class="details-info">
			<b>$LOCALE{DETAIL_TITLE_LAST}:</b>
			<span>$FORM{dateString}</span>
		</div>
	</div>
</div>

</body>
</html>
HTML
