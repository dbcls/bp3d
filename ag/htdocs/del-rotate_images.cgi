#!/bp3d/local/perl/bin/perl

use strict;
use File::Path;

require "common.pl";

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

exit unless(exists($FORM{dt}));

my $dirname = &getBasePath()."ag_images/$FORM{dt}";
#warn __LINE__,"\$dirname=[$dirname]\n";
#exit unless(-d $dirname);
rmtree($dirname,0,1) if(-e $dirname);

#opendir(DIR, $dirname) or die;
#my @tmpfiles = sort grep { -f "$dirname/$_"} readdir(DIR);
#closedir(DIR);
#foreach my $file (@tmpfiles){
#	my $filename = "$dirname/$file";
#	unlink $filename;
#}
#rmdir $dirname;
print qq|Content-type: text/html; charset=UTF-8\n\n|;
