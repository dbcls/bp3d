#!/bp3d/local/perl/bin/perl

$| = 1;


use strict;
use JSON::XS;
use File::Basename;

my @extlist = qw|.cgi|;
my($name,$dir,$ext) = fileparse($0,@extlist);

use lib '/bp3d/ag1/htdocs','/bp3d/ag1/htdocs/IM';#DEBUG
require "common.pl";
require "common_db.pl";
my $dbh = &get_dbh();

my $disEnv = &getDispEnv();
my $addPointElementHidden = $disEnv->{addPointElementHidden};
$addPointElementHidden = 'false' unless(defined $addPointElementHidden);

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> tmp_image/$name.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "\$ENV{$key}=[",$ENV{$key},"]\n";
#}

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "en" unless(exists($FORM{lng}));

#$FORM{tg_id} = qq|1|;
#$FORM{version} = qq|3.0|;
#$FORM{query} = qq|brain|;

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);

my $bp3d_table = &getBP3DTablename($FORM{version});


$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit{
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	exit(1);
}

#=pod
if(exists($FORM{version}) && (!exists($FORM{tg_id}) || !exists($FORM{tgi_id}))){
	my $tg_id;
	my $tgi_id;
	my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
	$sth_tree_group_item->execute($FORM{version});
	my $column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
	$sth_tree_group_item->fetch;
	if(defined $tg_id && defined $tgi_id){
		$FORM{tg_id} = $tg_id;
		$FORM{tgi_id} = $tgi_id;
	}
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}
my $wt_version = qq|tg_id=$FORM{tg_id} and tgi_id=$FORM{tgi_id}| if(exists($FORM{tg_id}) && exists($FORM{tgi_id}));
#=cut

#####
#####
print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $IMAGES = {
	"records" => [],
	"total" => 0
};

my @bind_values = ();
my @LIST1 = ();
unless(exists($FORM{query})){
	$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
	my $json = encode_json($IMAGES);
	if(exists($FORM{callback})){
		print $FORM{callback},"(",$json,")";
	}else{
		print $json;
	}
	print LOG __LINE__,":",$json,"\n";
	exit;
}

#my $operator = &get_ludia_operator();
my $operator = qq|~* |;
my $query = $FORM{query};
my $space = qq|　|;
utf8::decode($query) unless(utf8::is_utf8($query));
utf8::decode($space) unless(utf8::is_utf8($space));
$query =~ s/$space/ /g;
$query =~ s/\s*$//g;
$query =~ s/^\s*//g;
utf8::encode($query);
if(length($query)<1){
	$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
	my $json = encode_json($IMAGES);
	if(exists($FORM{callback})){
		print $FORM{callback},"(",$json,")";
	}else{
		print $json;
	}
	print LOG __LINE__,":",$json,"\n";
	exit;
}
my @QUERY = split(/\s+/,$query);
my $target_word = pop @QUERY;

my $snippet_length = 100;
#my $opentag = qq|<b><i>|;
#my $closetag = qq|</i></b>|;
my $opentag = qq|<b>|;
my $closetag = qq|</b>|;

my $sql = <<SQL;
select word,pgs2snippet1(1,$snippet_length,1,'$opentag','$closetag',-1,'$target_word',word) as markup from bp3d_words
where $wt_version AND word is not null AND word $operator ?
SQL
#push(@bind_values,qq|*D+ $target_word|);
push(@bind_values,qq|^$target_word|);

$sql .= qq| order by lower(word),word|;


print LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql);
if(scalar @bind_values > 0){
	$sth->execute(@bind_values);
}else{
	$sth->execute();
}
$IMAGES->{total} = $sth->rows();
$sth->finish;
undef $sth;
print LOG __LINE__,":\$IMAGES->{total}=[$IMAGES->{total}]\n";


if(exists($FORM{limit})){
	$sql .= qq| limit $FORM{limit}|;
}else{
#	$sql .= qq| limit 400|;
	$sql .= qq| limit 3000|;
}
$sql .= qq| offset $FORM{start}| if(exists($FORM{start}));

print LOG __LINE__,":sql=[$sql]\n";

my $sth = $dbh->prepare($sql);

if(scalar @bind_values > 0){
	$sth->execute(@bind_values);
}else{
	$sth->execute();
}
print LOG __LINE__,":rows=[",$sth->rows(),"]\n";

my $f_id;
my $keyword;
my $markup;
my $parts_exists;
my $score;

my $column_number = 0;
$sth->bind_col(++$column_number, \$keyword, undef);
$sth->bind_col(++$column_number, \$markup, undef);

#my %DISP_FMA = ();


my $q_keyword = join(" ",@QUERY);
my $q_markup = join(" ",@QUERY);
#my $q_markup  = join("$closetag $opentag",@QUERY);
utf8::decode($q_keyword) unless(utf8::is_utf8($q_keyword));
utf8::decode($q_markup) unless(utf8::is_utf8($q_markup));

while($sth->fetch){
	next unless(defined $keyword);

	utf8::decode($keyword);
	utf8::decode($markup) if(defined $markup);

	push(@{$IMAGES->{records}},{
		keyword => (length($q_keyword)>0 ? $q_keyword.' ' : '') . $keyword,
#		markup => (length($q_markup)>0 ? $opentag.$q_markup.$closetag.' ' : '') . $markup
		markup => (length($q_markup)>0 ? $q_markup.' ' : '') . $markup
	});

}
$sth->finish;


undef $sth;

$IMAGES->{success} = JSON::XS::true if(exists($FORM{callback}));
#my $json = to_json($IMAGES);
my $json = encode_json($IMAGES);
$json =~ s/"(true|false)"/$1/mg;

if(exists($FORM{callback})){
	print $FORM{callback},"(",$json,")";
}else{
	print $json;
}
print LOG __LINE__,":",$json,"\n";


close(LOG);
exit;
