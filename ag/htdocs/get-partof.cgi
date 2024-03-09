#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use File::Basename;
use File::Path;
use File::Spec;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|;

require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my %FORM = ();
my %COOKIE = ();
if(exists($ENV{'REQUEST_METHOD'})){
	my $query = CGI->new;
	&getParams($query,\%FORM,\%COOKIE);
}else{
	&decodeForm(\%FORM);
	delete $FORM{_formdata} if(exists($FORM{_formdata}));
	&getCookie(\%COOKIE);
}

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = fileparse($0,@extlist);
#open(LOG,"> $FindBin::Bin/logs/$COOKIE{'ag_annotation.session'}.$cgi_name.txt");
#flock(LOG,2);
#print LOG "\n[$logtime]:$0\n";
#foreach my $key (sort keys(%FORM)){
#	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
#}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG __LINE__,":\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "en" if(!exists($FORM{lng}));

&setDefParams(\%FORM,\%COOKIE);

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $TREE = {
	"data"  => [],
	"total" => 0
};

unless(exists $FORM{f_id} && defined $FORM{f_id}){
	print qq|Content-type: text/html; charset=UTF-8\n\n| if(exists($ENV{'REQUEST_METHOD'}));
	print &JSON::XS::encode_json($TREE);
#	print LOG __LINE__,":",&JSON::XS::encode_json($TREE),"\n";
#	close(LOG);
	exit;
}

umask(0);
my $cache_path = File::Spec->catdir($FindBin::Bin,qq|cache_fma|,$FORM{'version'},$cgi_name,$FORM{'lng'});
&File::Path::mkpath($cache_path,0,0777) unless(-e $cache_path);

my $cache_file = File::Spec->catfile($cache_path,qq|$FORM{f_id}.txt|);
unlink $cache_file if(-e $cache_file); #DEBUG
if(-e $cache_file && -s $cache_file){
	my $mtime = (stat($cache_file))[9];
	open(CACHE,$cache_file) or die;
	flock(CACHE,1);
	close(CACHE);
	print qq|Location: |,File::Spec->abs2rel( $cache_file, $FindBin::Bin ),qq|?$mtime\n\n|;
#	close(LOG);
	exit;
}else{
	exit unless(exists $ENV{'REQUEST_METHOD'});
	open(CACHE,"> $cache_file") or die;
	flock(CACHE,2);
}

print qq|Content-type: text/html; charset=UTF-8\n\n|;
#my $sql = qq|select fma_partof.f_pid from fma_partof where fma_partof.f_id=?|;
my $sql=<<SQL;
SELECT
 i2.cdi_name AS f_pid
FROM concept_tree
LEFT JOIN ( SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name
            FROM concept_data_info) i1 ON i1.ci_id = concept_tree.ci_id AND i1.cdi_id = concept_tree.cdi_id
LEFT JOIN ( SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name
            FROM concept_data_info) i2 ON i2.ci_id = concept_tree.ci_id AND i2.cdi_id = concept_tree.cdi_pid
WHERE concept_tree.ci_id = $FORM{'ci_id'} AND concept_tree.bul_id=(select bul_id from buildup_logic where bul_rep_key='P') AND concept_tree.cb_id = $FORM{'cb_id'} and i1.cdi_name=?
SQL
my $sth_partof  = $dbh->prepare($sql);

my($f_id,$f_name_j,$f_name_e,$f_name_k,$f_name_l,$f_syn_j,$f_syn_e,$f_detail_j,$f_detail_e,$f_organsys_j,$f_organsys_e,$f_phase,$f_zmin,$f_zmax,$f_volume,$f_delcause,$f_entry,$f_modified,$e_openid,$m_openid,$f_taid,$phy_name,$phy_id);

my @ROUTE = ();

sub getPartof {
	my $f_id = shift;
	my $route = shift;

	unless(defined $route){
		$route = $f_id;
	}else{
		$route .= qq|\t$f_id|;
	}

	my $exists_flag = 0;
	my @CHK = split(/\t/,$route);
	pop @CHK;
	for(my $i=0;$i<=$#CHK;$i++){
		next if($CHK[$i] ne $f_id);
		$exists_flag = 1;
		last;
	}

	my $f_id2 = $f_id;
#	$f_id2 =~ s/\D+$//g;

	my @F_PID = ();
	unless($exists_flag){
		$sth_partof->execute($f_id2);
		if($sth_partof->rows>0){
			my $f_pid;
			my $column_number = 0;
			$sth_partof->bind_col(++$column_number, \$f_pid, undef);
			while($sth_partof->fetch){
				push(@F_PID,$f_pid);
			}
		}
		$sth_partof->finish;
	}
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			&getPartof($f_pid,$route);
			last if($#ROUTE>10);
		}
	}else{
		push(@ROUTE,$route) unless($exists_flag);
	}
}


&getPartof($FORM{f_id});

foreach my $route (@ROUTE){
	my @R = split(/\t/,$route);
	$route = \@R;
}
@ROUTE = sort {
	if($a->[(scalar @$a)-1] eq 'FMA20394' && $b->[(scalar @$b)-1]  eq 'FMA20394'){
		scalar @$a <=> scalar @$b;
	}elsif($a->[(scalar @$a)-1] eq 'FMA20394'){
		-1;
	}elsif($b->[(scalar @$b)-1]  eq 'FMA20394'){
		1;
	}else{
		0;
	}
} sort {scalar @$a <=> scalar @$b} sort {$a->[(scalar @$a)-1] cmp $b->[(scalar @$b)-1] } @ROUTE;


$#ROUTE = 10 if($#ROUTE>10);
my $form;
foreach my $key (keys(%FORM)){
	$form->{$key} = $FORM{$key};
}
$form->{bul_id} = 4;
foreach my $route (@ROUTE){
	push(@{$TREE->{data}},{});
	foreach my $f_id (@$route){
		push(@{$TREE->{data}},&getFMA($dbh,$form,$f_id));
	}
}

$TREE->{total} = scalar @{$TREE->{data}};

#my $json = to_json($TREE);
my $json = &JSON::XS::encode_json($TREE);

print $json;
#print LOG __LINE__,":",$json,"\n";

print CACHE $json;
close(CACHE);

#close(LOG);

#rmdir($cache_lock);

exit;
