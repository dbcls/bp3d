#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
print qq|Content-type: text/javascript; charset=UTF-8\n\n| if(exists $ENV{REQUEST_METHOD});
print <<HTML;
var AgImages = {
	lis : []
};
HTML

unless(exists $ENV{REQUEST_METHOD}){
	if(open(CMD,q{find css js img -type f \( -name "*.png" -or -name "*.gif" \) ! -iregex ".*\/welcome\/.*" ! -iregex ".*\/examples\/.*" ! -iregex ".*\/docs\/.*" ! -iregex ".*\/resources\/themes\/images\/gray\/.*" ! -iregex ".*\/resources\/themes\/images\/access\/.*" ! -iregex ".*\/resources\/themes\/images\/neptune\/.*" |})){
		my @FILES = ();
		while(<CMD>){
			s/\s*$//g;
			push(@FILES,$_);
		}
		close(CMD);
		print qq|AgImages.lis.push("|.join(qq|","|,@FILES).qq|");| if(scalar @FILES > 0);
	}
}
print <<HTML;
Ext.onReady(function(){
	if(!Ext.isEmpty(AgImages.lis)){
		var img = new Image();
		img.onload = img.onabort = img.onerror = function(){
			if(Ext.isEmpty(AgImages.lis)){
				img = undefined;
				return;
			}
			img.src = AgImages.lis.shift();
		};
		img.src = AgImages.lis.shift();
	}
});
HTML
