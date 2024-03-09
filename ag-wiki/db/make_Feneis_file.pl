#!/usr/bin/perl

#warn __LINE__,"\n";

$| = 1;

my $anatomo_path;
BEGIN {
	$anatomo_path = qq|/ext1/project/ag/ag1/htdocs|;
}

use strict;

use lib $anatomo_path;
use Image::Info qw(image_info dim);
use Image::Magick;
use DBI;
use DBD::Pg;
use File::Path;
use JSON::XS;

warn __LINE__,"\n";

require "common.pl";
require "common_db.pl";
require "common_locale.pl";
require "common_image.pl";
require "common_wiki.pl";
my $dbh = &get_dbh();

#my $wiki_path = qq|../|.&getMediawikiPath();
#my $script = qq|php $wiki_path/maintenance/importTextFile.php --user 'bot'|;
my $import_path = qq|/dev/shm|;
#mkdir $import_path unless(-d $import_path);
my $import_file = qq|$import_path/.$$.txt|;
my $import_link_file = qq|$import_path/.$$\_c.txt|;
#warn $import_file,"\n";
#exit;

sub import_file {
	my $title = shift;
#	my $lang = shift;
#	my $script = &getTextScript($lang);
	my $script = &getTextScript();

#print $title,"\n";
#print $lang,"\n";
#print $import_file,"\n";
#unlink $import_file if(-e $import_file);
#return;

	my $command = qq|$script --title "$title" $import_file|;
	print LOG __LINE__,":$command\n";
	system($command);
	my $exit_value = $? >> 8;
	my $signal_num = $? & 127;
	my $dumped_core = $? & 128;
	print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
	unlink $import_file if(-e $import_file);
}


my $log_file = qq|$0\_log.txt|;
open(LOG,"> $log_file");

warn __LINE__,"\n";

$SIG{'PIPE'} = $SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	unlink $import_file if(-e $import_file);
	close(LOG);
	exit(1);
}

warn __LINE__,":",(scalar @ARGV),"\n";

my $del_file = qq|$0\_del.txt|;
open(DEL,"> $del_file");

=pod
my $file = qq|FeneisDB_FMA_NoDup.txt|;
my %FENESIS;
if(open(IN,"< $file")){
	while(<IN>){
		chomp;
		my($FENESIS_ID,$FENESIS_Name_English,$FENESIS_Name_latin,$FENESIS_description,$FMA_Info) = split(/\t/);
		$FENESIS_description =~ s/[\s\/]+$//g;
		my $fmd_id = $FMA_Info;
		$fmd_id =~ s/^(FMA\d+).*$/$1/;
		if(defined $fmd_id && $fmd_id =~ /^FMA\d+$/){
			print DEL qq|FENEIS:$fmd_id\n|;
		}
	}
	close(IN);
}
close(DEL);
exit;
=cut

my $file = qq|F2F_nodup.txt|;
my %FENESIS;
if(open(IN,"< $file")){
	while(<IN>){
		chomp;
		my($FENESIS_ID,$FENESIS_Name_English,$FENESIS_Name_latin,$FENESIS_description,$FMA_Info) = split(/\t/);
		$FENESIS_description =~ s/[\s\/]+$//g;
		my $fmd_id = $FMA_Info;
		$fmd_id =~ s/^(FMA\d+).*$/$1/;
		if(defined $fmd_id && $fmd_id =~ /^FMA\d+$/){
			push(@{$FENESIS{$fmd_id}},{
				FENESIS_ID => $FENESIS_ID,
				FENESIS_Name_English => $FENESIS_Name_English,
				FENESIS_Name_latin => $FENESIS_Name_latin,
				FENESIS_description => $FENESIS_description
			});
		}
	}
	close(IN);
}

#my $debug_fmaid = "FMA30278";
#my $debug_fmaid = "FMA20394";
#my $debug_fmaid = "FMA19735";
#my $debug_fmaid = "FMA10951";
#my $debug_fmaid = "FMA59655";
#my $debug_fmaid = "FMA242787";
#my $debug_fmaid = "FMA10014";
my $debug_fmaid;

foreach my $fmaid (sort keys(%FENESIS)){
	next unless(defined $fmaid);
	next if(defined $debug_fmaid && $debug_fmaid ne $fmaid);

	open(OUT,"> $import_file");
	print OUT <<TEXT;
<noinclude><div id="contentSub"><span class="subpages">← [[:{{BASEPAGENAME}}]]</span></div></noinclude>
==FENEIS==
<div class="fma_detail FENESIS">
TEXT
	foreach my $f (@{$FENESIS{$fmaid}}){
		my $FENESIS_ID = $f->{'FENESIS_ID'};
		my $FENESIS_Name_English = $f->{'FENESIS_Name_English'};
		my $FENESIS_Name_latin = $f->{'FENESIS_Name_latin'};
		my $FENESIS_description = $f->{'FENESIS_description'};
		print OUT <<TEXT;
<table class="fma_detail FENESIS">
<tr><td class="fma_detail_title">ID</td><td class="fma_detail_colon">:</td><td>$FENESIS_ID</td></tr>
<tr><td class="fma_detail_title">Name English</td><td class="fma_detail_colon">:</td><td>$FENESIS_Name_English</td></tr>
<tr><td class="fma_detail_title">Name Latin</td><td class="fma_detail_colon">:</td><td>$FENESIS_Name_latin</td></tr>
<tr><td class="fma_detail_title">Description</td><td class="fma_detail_colon">:</td><td>$FENESIS_description</td></tr>
</table>
TEXT
	}
	print OUT <<TEXT;
<br clear="all"></div>
TEXT
	close(OUT);
	if(-s $import_file){
		&import_file(qq|FENEIS:$fmaid|);
	}
}
unlink $import_file if(-e $import_file);

close(LOG);
