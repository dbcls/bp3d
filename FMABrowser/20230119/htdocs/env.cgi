#!/usr/bin/perl

$| = 1;

#use Image::Info qw(image_info dim);
#use Image::Magick;

#----------------------------------#
#　ENV_Checker ( Full List Type )　#
#----------------------------------#

$host = $ENV{'REMOTE_HOST'}; $addr = $ENV{'REMOTE_ADDR'};
$host = gethostbyaddr(pack('C4',split(/\./,$host)),2) || $addr;

print <<HTML;
Content-type: text/html

<html>
<head>
<title>env_checker</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta http-equiv="Content-Script-Type" content="text/javascript" />
<!--
<link media="only screen and (max-device-width:480px)" href="css/small-device.css" type="text/css" rel="stylesheet">
<link media="screen and (min-device-width:481px)" href="css/not-small-device.css" type="text/css" rel="stylesheet">
<meta name="viewport" content="width = 320" />
<meta name="viewport" content="initial-scale=1, user-scalable=no" />
-->
<link rel="stylesheet" href="resources/css/ext-all.css" type="text/css" media="all">
<script type="text/javascript" src="ext-2.2.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="ext-2.2.1/ext-all.js"></script>
<script type="text/javascript">
<!--//
Ext.BLANK_IMAGE_URL = "resources/images/default/s.gif";

var _dump = function(aStr){
	if(window.dump) window.dump(aStr+"\\n")
};

var captureEvents = function(observable) {
	Ext.util.Observable.capture(
		observable,
		function(eventName) {
			_dump(eventName);
			alert('');
		},
		this
	);
};
/*
Ext.EventManager.on(window,'load',function(e){
	var p = new Ext.Panel({
		title: 'My Panel',
		collapsible:true,
		renderTo: 'panel-basic',
		width:400,
		html: '<img id="iphone_image" src="bp3d_images/1247139970/BP10_front_zoom.png"/>'
	});
	captureEvents(p);

});
*/
//-->
</script>
</head>
<body>
<h3>env_checker</h3>
HTML

foreach $key ( sort keys %ENV ) {
	if ($key =~ /REMOTE_HOST/i) { print "$key = $host<br>\n";} 
	else { print "$key = $ENV{$key}<br>\n";}
}
print "<!--\n";
&decode;
print "<BR><BR><h3>form_checker</h3>\n";
foreach $key ( sort keys %FORM ) {
	print "$key = $FORM{$key}<br>\n";
}

print "<BR>";
print &getBrowserMSIE;

print "<BR>";
print &isIPHONE;

print <<HTML;
<br><a href="env.cgi">env.cgi</a>
<br><img src="bp3d_images/3.0/FMA10014_front_640x640.png">
<div id="panel-basic"></div>
<hr>
<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://221.186.138.155/bp3d/?shorten=vyWn8P4DCObu9za8v8H1H9vu"></iframe><br /><small><a href="http://221.186.138.155/bp3d/?shorten=vyWn8P4DCObu9za8v8H1H9vu" target="_blank" style="color:#0000FF;text-align:left">View Larger Image</a></small>
-->
</body></html>
HTML

exit;

###<--------------------------------------------------------------
###<---   デコード＆変数代入
###<--------------------------------------------------------------
sub decode {
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	} else { $buffer = $ENV{'QUERY_STRING'}; }
	@pairs = split(/&/,$buffer);

	$wk = "pass=" . $password ;
	if ( index($buffer,$wk) >= 0 )	{$mast = 1 ; }

	foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value  =~ s/\r\n/\<br\>/g;
		$value  =~ s/\r|\n/\<br\>/g;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		if ($mast != 1 && $tag == 0 ) {	$value =~ s/</&lt;/g;	$value =~ s/>/&gt;/g;	}
		$value =~ s/\,/，/g;
#		&jcode'convert(*value,'sjis');
		$FORM{$name} = $value;
	}
	$FORM{'comment'} =~ s/\r\n/<br>/g;	$FORM{'comment'} =~ s/\r|\n/<br>/g;
}

#------------------------------------------------------------------------------
# IE又はIE以外かを判定する
#------------------------------------------------------------------------------
sub getBrowserMSIE {
	if($ENV{HTTP_USER_AGENT} =~ /(MSIE)\s(\d+\.\d+)/){
		return($1,$2);
#	}elsif($ENV{HTTP_USER_AGENT} =~ /(Netscape)\d*\/(\d+\.\d+)/){
#		return($1,$2);
#	}elsif($ENV{HTTP_USER_AGENT} =~ /(Mozilla)\/(\d+\.\d+)/){
#		return($1,$2);
#	}elsif($ENV{HTTP_USER_AGENT} =~ /(Opera)\w*\/(\d+\.\d+)/){
#		return($1,$2);
	}elsif($ENV{HTTP_USER_AGENT} =~ /(\w*)?\/(\d+\.\d+)/){
		return($1,$2);
	}else{
		return(0);
	}
}

sub isIPHONE {

#Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
#Mozilla/5.0 (iPod; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16
#Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20
#Mozilla/5.0 (iPod; U; CPU iPhone OS 2_2_1 like Mac OS X; en-us) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5H11 Safari/525.20
#Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A102 Safari/419.3
#Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A102 Safari/419.3

	if($ENV{HTTP_USER_AGENT} =~ /^Mozilla\/5\.0\s\((iPhone|iPod);\s*U;\s(CPU\s*[^;]+);[^\)]+\)/){
		return 1;
	}else{
		return 0;
	}
}
