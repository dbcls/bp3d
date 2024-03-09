#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;

$ENV{'AG_DB_NAME'} = 'bp3d'      unless(exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'});
$ENV{'AG_DB_HOST'} = '127.0.0.1' unless(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
$ENV{'AG_DB_PORT'} = '8543'      unless(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my $element_coloring_table_file = &catfile($FindBin::Bin,'..','tools','element_coloring_table.txt');
my $group2color_file = &catfile($FindBin::Bin,'..','tools','group2color.txt');

unless(defined $element_coloring_table_file && -e $element_coloring_table_file && -f $element_coloring_table_file && -s $element_coloring_table_file){
	say STDERR "$0 element_coloring_table_xxxxxxxx.txt [group2color_xxxxxxxx.txt]";
	exit 1;
}

my $md_id = 1;
my $mv_id = 25;
my $mr_id = 1;
my $ci_id = 1;
my $cb_id = 11;
my $bul_id = 3;

my $concept_info_data_sql=<<SQL;
select
 cdi_id,
 cdi_name
from
 concept_data_info
where
 ci_id in (select ci_id from model_revision as mr left join (select * from model_version) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id where mr_use and mv_use)
SQL
my $CDI_NAME2ID;
my $CDI_ID2NAME;
my $cdi_id;
my $cdi_name;
my $concept_info_data_sth = $dbh->prepare($concept_info_data_sql) or die $dbh->errstr;
$concept_info_data_sth->execute() or die $dbh->errstr;
my $column_number = 0;
$concept_info_data_sth->bind_col(++$column_number, \$cdi_id,   undef);
$concept_info_data_sth->bind_col(++$column_number, \$cdi_name,   undef);
while($concept_info_data_sth->fetch){
	$CDI_NAME2ID->{$cdi_name} = $cdi_id;
	$CDI_ID2NAME->{$cdi_id} = $cdi_name;
}
$concept_info_data_sth->finish;
undef $concept_info_data_sth;
undef $concept_info_data_sql;



my $FMA_HASH;
my $GROUP2FMA;
open(my $IN, $element_coloring_table_file) or die "$! [$element_coloring_table_file]";
while(<$IN>){
	chomp;
	my($FMA,$e1,$FMA_name,$e2,$color_group) = split(/\t/);
	next unless(defined $FMA && length $FMA);
	$FMA =~ s/^[^0-9]+//g;
	$FMA =~ s/[^0-9]+$//g;
	unless($FMA =~ /^[0-9]+$/){
		&cgi_lib::common::message($FMA) if(defined $FMA && length $FMA);
		next;
	}
	my $cdi_name = "FMA$FMA";
	unless(exists $CDI_NAME2ID->{$cdi_name} && defined $CDI_NAME2ID->{$cdi_name}){
		say STDERR "Unknown [$cdi_name]";
		next;
	}
	my $cdi_id = $CDI_NAME2ID->{$cdi_name};

	$color_group =~ s/^0+//g;
	my $color_group_name;
	my $color_group_id = 0;
	$color_group_id = $1 - 1 if($color_group =~ /^([0-9]+)/);
	$color_group_name = $1 if($color_group =~ /^[0-9]+_([A-Z]+)$/);

	$FMA_HASH = {} unless(defined $FMA_HASH && ref $FMA_HASH eq 'HASH');
	if(exists $FMA_HASH->{$cdi_id} && defined $FMA_HASH->{$cdi_id} && $FMA_HASH->{$cdi_id}->{'color_group'} ne $color_group){
		&cgi_lib::common::message("exists $cdi_name");
	}
	$FMA_HASH->{$cdi_id} = {
		cdi_pid => $cdi_id,
		cdi_pname => $cdi_name,
		color_group => $color_group,
		color_group_id => $color_group_id,
		but_depth => 0
	};

	if(defined $color_group_name && length $color_group_name){
		$GROUP2FMA->{$color_group_name}->{$cdi_name} = undef;
	}
	else{
		say sprintf("%d:%s",__LINE__,'Unknown Group name');
	}
}
close($IN);

if(defined $GROUP2FMA && ref $GROUP2FMA eq 'HASH'){
	foreach my $color_group_name (sort keys(%$GROUP2FMA)){
		say STDERR $color_group_name;
		foreach my $cdi_name (sort keys(%{$GROUP2FMA->{$color_group_name}})){
			say STDERR "\t".$cdi_name;
		}
	}
}


my $COLORGROUP2COLOR;
if(defined $group2color_file && -e $group2color_file && -f $group2color_file && -s $group2color_file){
	open(my $IN, $group2color_file) or die "$! [$group2color_file]";
	while(<$IN>){
		chomp;
		my($color_group,$color) = split(/:/);
		next unless(defined $color_group && defined $color);
		$color_group =~ s/\s*$//g;
		$color_group =~ s/^\s*//g;
		$color =~ s/\s*$//g;
		$color =~ s/^\s*//g;
		next unless(length $color_group && length $color);
		$COLORGROUP2COLOR->{$color_group} = $color;
	}
	close($IN);
}

#&cgi_lib::common::message($COLORGROUP2COLOR);
#exit;

if(defined $FMA_HASH && ref $FMA_HASH eq 'HASH' && scalar keys(%$FMA_HASH)){

	my $cdi_id;
	my $but_cids;
	my $but_depth;



	my $buildup_tree_info_sql=<<SQL;
select
 cdi_id,
 but_cids,
 but_depth
from
 buildup_tree_info
where
 md_id=$md_id and
 mv_id=$mv_id and
 mr_id=$mr_id and
 bul_id=$bul_id and
 cdi_id in (%s)
SQL
	my $buildup_tree_info_sth;

	$buildup_tree_info_sth = $dbh->prepare(sprintf($buildup_tree_info_sql,join(',',map {'?'} keys(%$FMA_HASH)))) or die $dbh->errstr;
	$buildup_tree_info_sth->execute(keys(%$FMA_HASH)) or die $dbh->errstr;
	$column_number = 0;
	$buildup_tree_info_sth->bind_col(++$column_number, \$cdi_id,   undef);
	$buildup_tree_info_sth->bind_col(++$column_number, \$but_cids,   undef);
	$buildup_tree_info_sth->bind_col(++$column_number, \$but_depth,   undef);
	while($buildup_tree_info_sth->fetch){
		unless(exists $FMA_HASH->{$cdi_id} && defined $FMA_HASH->{$cdi_id}){
			&cgi_lib::common::message("Unknown [$CDI_ID2NAME->{$cdi_id}]");
			next;
		}
		$FMA_HASH->{$cdi_id}->{'but_depth'} = $but_depth - 0;

		$FMA_HASH->{$cdi_id}->{'but_cids'} = undef;
		next unless(defined $but_cids && length $but_cids);

		$but_cids = &cgi_lib::common::decodeJSON($but_cids);
		if(defined $but_cids && ref $but_cids eq 'ARRAY' && scalar @$but_cids){
			$FMA_HASH->{$cdi_id}->{'but_cids'}->{$_} = undef for(@$but_cids);
		}else{
			&cgi_lib::common::message($but_cids);
		}
	}
	$buildup_tree_info_sth->finish;
	undef $buildup_tree_info_sth;
	undef $buildup_tree_info_sql;

#exit;

	foreach my $cdi_id (keys(%$FMA_HASH)){

		my $but_cids = $FMA_HASH->{$cdi_id}->{'but_cids'};
		my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
		my $cdi_pname = $CDI_ID2NAME->{$cdi_id};

		if(defined $but_cids && ref $but_cids eq 'HASH' && scalar keys(%$but_cids)){
			foreach my $but_cid (keys(%$but_cids)){
				if(exists $FMA_HASH->{$but_cid} && defined $FMA_HASH->{$but_cid} && $FMA_HASH->{$but_cid}->{'color_group'} ne $color_group && $FMA_HASH->{$but_cid}->{'but_depth'} > $FMA_HASH->{$cdi_id}->{'but_depth'}){
#					&cgi_lib::common::message("exists\t$CDI_ID2NAME->{$but_cid}\t$cdi_pname\t$color_group\t$FMA_HASH->{$but_cid}->{'cdi_pname'}\t$FMA_HASH->{$but_cid}->{'color_group'}");
					if(exists $FMA_HASH->{$but_cid}->{'but_cids'} && defined $FMA_HASH->{$but_cid}->{'but_cids'} && ref $FMA_HASH->{$but_cid}->{'but_cids'} eq 'HASH'){
						foreach (keys(%{$FMA_HASH->{$but_cid}->{'but_cids'}})){
							delete $FMA_HASH->{$cdi_id}->{'but_cids'}->{$_} if(exists $FMA_HASH->{$cdi_id}->{'but_cids'}->{$_});
						}
					}
					delete $FMA_HASH->{$cdi_id}->{'but_cids'}->{$but_cid} if(exists $FMA_HASH->{$cdi_id}->{'but_cids'}->{$but_cid});
				}
			}
		}
	}

	foreach my $cdi_id (keys(%$FMA_HASH)){

		my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
		my $color_group_id = $FMA_HASH->{$cdi_id}->{'color_group_id'};
		my $cdi_pname = $CDI_ID2NAME->{$cdi_id};

		my $but_cids = $FMA_HASH->{$cdi_id}->{'but_cids'};
		if(defined $but_cids && ref $but_cids eq 'HASH' && scalar keys(%$but_cids)){
			foreach my $but_cid (keys(%$but_cids)){

				if(exists $FMA_HASH->{$but_cid} && defined $FMA_HASH->{$but_cid} && $FMA_HASH->{$but_cid}->{'color_group'} ne $color_group){
					&cgi_lib::common::message("exists\t$CDI_ID2NAME->{$but_cid}\t$cdi_pname\t$color_group\t$FMA_HASH->{$but_cid}->{'cdi_pname'}\t$FMA_HASH->{$but_cid}->{'color_group'}");
					next;
				}
				$FMA_HASH->{$but_cid} = {
					cdi_pid => $cdi_id,
					cdi_pname => $cdi_pname,
					color_group => $color_group,
					color_group_id => $color_group_id
				};

			}
		}
	}

	foreach my $cdi_id (sort {$FMA_HASH->{$a}->{'color_group_id'} <=> $FMA_HASH->{$b}->{'color_group_id'}} sort {$CDI_ID2NAME->{$a} cmp $CDI_ID2NAME->{$b}} keys(%$FMA_HASH)){
		my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
		my $cdi_name = $CDI_ID2NAME->{$cdi_id};
		my $color = defined $COLORGROUP2COLOR && exists $COLORGROUP2COLOR->{$color_group} && defined $COLORGROUP2COLOR->{$color_group} ? $COLORGROUP2COLOR->{$color_group} : '';
		say $cdi_name."\t".$cdi_id."\t".$color_group."\t".$color;
	}

#	my $OUT;

}else{
	say STDERR __LINE__;
}
