#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use File::Path;
use JSON::XS;
use Graphics::ColorObject;

use lib qq|/bp3d/ag/htdocs|,qq|/bp3d/ag/lib|,qq|/bp3d/ag-common/lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

use cgi_lib::common;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

#my $root_cdi_id = undef;
#eval{$root_cdi_id = ROOT_CDI_ID;};
my $root_cdi_id;

my $ci_id;
my $cb_id;
sub error {
	select(STDERR);
	$| = 1;
	say qq|$0 concept_info_id| ;
	say qq|#optins :|;
	say qq|# --host,-h : database host [default:$config->{'host'}]|;
	say qq|# --port,-p : database port [default:$config->{'port'}]|;
	say qq|#concept_info_id:|;
	my $sql=<<SQL;
select ci_id,ci_name from concept_info where ci_delcause is null
order by ci_id
SQL
	my $ci_name;
	my $cb_name;
	my $cb_comment;
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$ci_name, undef);
	while($sth->fetch){
		say sprintf("             %-2d : %s",$ci_id,$ci_name);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
if(scalar @ARGV < 1){
	&error();
}
#=pod
$ci_id = $ARGV[0];
#$cb_id = $ARGV[1];


$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{

#	$dbh->do(qq|update concept_data set seg_id=0 where ci_id=$ci_id and cb_id=$cb_id|) or die $dbh->errstr;
	my $sql_cd = qq|update concept_data set seg_id=? where ci_id=? and cb_id=? and cdi_id in (%s) and seg_id=0|;

	my $column_number;
	my $GROUP2SEGID;
	my $CDI_ID2NAME;

	my $group2color_file = &catfile($FindBin::Bin,'group2color.txt');
	my $element_coloring_table_file = &catfile($FindBin::Bin,'element_coloring_table.txt');
	if(
		-e $group2color_file && -f $group2color_file && -s $group2color_file &&
		-e $element_coloring_table_file && -f $element_coloring_table_file && -s $element_coloring_table_file
	){
		my $concept_info_data_sql=<<SQL;
select
 cdi_id,
 cdi_name
from
 concept_data_info
where
 ci_id=$ci_id
SQL
		my $CDI_NAME2ID;
		my $cdi_id;
		my $cdi_name;
		my $concept_info_data_sth = $dbh->prepare($concept_info_data_sql) or die $dbh->errstr;
		$concept_info_data_sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$concept_info_data_sth->bind_col(++$column_number, \$cdi_id,   undef);
		$concept_info_data_sth->bind_col(++$column_number, \$cdi_name,   undef);
		while($concept_info_data_sth->fetch){
			$CDI_NAME2ID->{$cdi_name} = $cdi_id;
			$CDI_ID2NAME->{$cdi_id} = $cdi_name;
		}
		$concept_info_data_sth->finish;
		undef $concept_info_data_sth;
		undef $concept_info_data_sql;


		my $GROUP2COLOR;
		my $GROUP2FMAID;
		my $FMANAME2GROUP;
		my $IN;

		open($IN, $group2color_file) or die "$! [$group2color_file]";
		while(<$IN>){
			chomp;
			my($color_group,$color) = split(/:/);
			next unless($color_group =~ /^[0-9]+_.+$/);
			$color_group =~ s/^[0-9]+_//g;
			my $color_group_name = lc($color_group);
			$GROUP2COLOR->{$color_group_name} = $color;
		}
		close($IN);


		open($IN, $element_coloring_table_file) or die "$! [$element_coloring_table_file]";
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

			next unless($color_group =~ /^[0-9]+_.+$/);
			$color_group =~ s/^[0-9]+_//g;
			my $color_group_name = lc($color_group);

			$GROUP2FMAID = {} unless(defined $GROUP2FMAID && ref $GROUP2FMAID eq 'HASH');
			push(@{$GROUP2FMAID->{$color_group_name}}, $cdi_id-0);
		}
		close($IN);

		&cgi_lib::common::message($GROUP2COLOR);
		if(defined $GROUP2COLOR && ref $GROUP2COLOR eq 'HASH'){

			$dbh->do(qq|UPDATE concept_segment SET seg_name=lower('VENOUS'::text) WHERE seg_name='vein'|) or die $dbh->errstr;
			$dbh->do(qq|UPDATE concept_segment SET seg_name=lower('NEURAL'::text) WHERE seg_name='nerve'|) or die $dbh->errstr;

			my $sth_seg = $dbh->prepare(qq|select seg_id,seg_name,seg_color from concept_segment|);
			$sth_seg->execute();
			my $seg_id;
			my $seg_name;
			my $seg_color;
			$column_number = 0;
			$sth_seg->bind_col(++$column_number, \$seg_id, undef);
			$sth_seg->bind_col(++$column_number, \$seg_name, undef);
			$sth_seg->bind_col(++$column_number, \$seg_color, undef);
			while($sth_seg->fetch){
				$GROUP2SEGID->{$seg_name} = $seg_id;
				$GROUP2COLOR->{$seg_name} = uc $seg_color unless(exists $GROUP2COLOR->{$seg_name});
			}
			$sth_seg->finish;
			undef $sth_seg;

			&cgi_lib::common::message($GROUP2COLOR);

			my $k = 0.7 ** 0.35;
	#		my $color_rgb = Graphics::Color::RGB->new();
	#		my $color_hsl;

			my $max_seg_id;
			my $sth_seg_sel = $dbh->prepare(qq|SELECT COALESCE(MAX(seg_id),0)+1 FROM concept_segment|);
			$sth_seg_sel->execute();
			$column_number = 0;
			$sth_seg_sel->bind_col(++$column_number, \$max_seg_id, undef);
			$sth_seg_sel->fetch;
			$sth_seg_sel->finish;
			undef $sth_seg_sel;
			&cgi_lib::common::message($max_seg_id);

			$dbh->do(qq|SELECT setval('concept_segment_seg_id_seq', $max_seg_id, true)|) or die $dbh->errstr;

			my $sth_seg_ins = $dbh->prepare(qq|INSERT INTO concept_segment (seg_name) VALUES (?) RETURNING seg_id|);
			my $sth_seg_upd = $dbh->prepare(qq|UPDATE concept_segment SET seg_color=?,seg_thum_bgcolor=?,seg_thum_fgcolor=?,cdi_ids=? WHERE seg_id=?|);
			foreach $seg_name (sort keys %$GROUP2COLOR){
				&cgi_lib::common::message($seg_name);
				unless(exists $GROUP2SEGID->{$seg_name}){
					$sth_seg_ins->execute($seg_name);
					$column_number = 0;
					$sth_seg_ins->bind_col(++$column_number, \$seg_id, undef);
					$sth_seg_ins->fetch;
					$sth_seg_ins->finish;
					$GROUP2SEGID->{$seg_name} = $seg_id;
				}else{
					$seg_id = $GROUP2SEGID->{$seg_name};
				}
				&cgi_lib::common::message($seg_id);

				my $seg_color = $GROUP2COLOR->{$seg_name};
				my $seg_thum_fgcolor = $GROUP2COLOR->{$seg_name};
	#			&cgi_lib::common::message($seg_thum_fgcolor);
#				$seg_thum_fgcolor = '#FF5100' if($seg_thum_fgcolor eq '#F0D2A0');

				my ($H, $S, $L) = @{ &Graphics::ColorObject::RGB_to_HSL(&Graphics::ColorObject::RGBhex_to_RGB($seg_color)) };
				my $seg_thum_bgcolor =  '#' . &Graphics::ColorObject::RGB_to_RGBhex( &Graphics::ColorObject::HSL_to_RGB([$H, $S, $L / $k]) );

				$seg_thum_bgcolor = $seg_color if($seg_thum_bgcolor eq '#FFFFFF');
				$seg_thum_bgcolor = '#F0F0F0' if($seg_color eq '#FFFFFF');

	#			&cgi_lib::common::message($seg_thum_bgcolor);
	#			exit;

				my $cdi_ids;
				if(exists $GROUP2FMAID->{$seg_name} && ref $GROUP2FMAID->{$seg_name} eq 'ARRAY'){
					$cdi_ids = &cgi_lib::common::encodeJSON([map {$_-0} sort {$a <=> $b} @{$GROUP2FMAID->{$seg_name}}]);
				}else{
					&cgi_lib::common::message($seg_name);
				}

				$sth_seg_upd->execute($seg_color,$seg_thum_bgcolor,$seg_thum_fgcolor,$cdi_ids,$seg_id);
				$sth_seg_upd->finish;
			}
		}
		&cgi_lib::common::message($GROUP2COLOR);
	}
	$dbh->commit();
};
if($@){
	print $@,"\n";
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;

print STDERR __LINE__.':ANALYZE;'."\n";
$dbh->do(qq|ANALYZE;|) or die $!;
