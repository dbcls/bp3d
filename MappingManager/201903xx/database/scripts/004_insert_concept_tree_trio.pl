#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use File::Path;
use JSON::XS;
use Graphics::ColorObject;

use lib qq|$FindBin::Bin/../../cgi_lib|;

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

require "webgl_common.pl";

=pod
=cut

my $dbh = &get_dbh();

my $ci_id;
my $cb_id;
sub error {
	select(STDERR);
	$| = 1;
	say qq|$0 concept_info_id concept_build_id fma_x.x.x_inference_one_path_trio_bp3d.txt fma_x.x.x_inference_out.txt| ;
	say qq|#optins :|;
	say qq|# --host,-h : database host [default:$config->{'host'}]|;
	say qq|# --port,-p : database port [default:$config->{'port'}]|;
	say qq|#concept_info_id:concept_build_id:|;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_name,cb_release from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause is null) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause is null
order by cb_release,info.ci_id,cb_id;
SQL
	my $ci_name;
	my $cb_name;
	my $cb_comment;
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$cb_id, undef);
	$sth->bind_col(3, \$ci_name, undef);
	$sth->bind_col(4, \$cb_name, undef);
	$sth->bind_col(5, \$cb_comment, undef);
	while($sth->fetch){
		say sprintf("             %-2d :            %3d : %-5s : %-25s : %10s",$ci_id,$cb_id,$ci_name,$cb_name,$cb_comment);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
if(scalar @ARGV < 4){
	&error();
}
#=pod
$ci_id = $ARGV[0];
$cb_id = $ARGV[1];

my $inference_one_path_trio_file = $ARGV[2];
my $inference_out_file = $ARGV[3];

unless(
	-e $inference_one_path_trio_file && -f $inference_one_path_trio_file && -s $inference_one_path_trio_file &&
	-e $inference_out_file && -f $inference_out_file && -s $inference_out_file
){
	&error();
}

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
	my $rows;
	my $column_number;
	my $sql;
	my $sth;
	my $IN;
	my $cdi_id;
	my $cdi_name;

	my $FMAID2NAME;
	my $FMANAME2ID;
	my $TRIO;
	my $TRIO_L;
	my $TRIO_R;
	my $TRIO_P;
	my $TRIO_COUNT;
	my $INFER;

	$rows = $dbh->do(qq|DELETE FROM concept_tree_trio WHERE ci_id=$ci_id AND cb_id=$cb_id|) or die $dbh->errstr;
	&cgi_lib::common::message($rows);


	$sql = qq|select cdi_id,cdi_name from concept_data_info where ci_id=$ci_id AND is_user_data=false|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$rows = $sth->rows();
	$column_number=0;
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	while($sth->fetch){
		$FMAID2NAME->{$cdi_id} = $cdi_name;
		$FMANAME2ID->{$cdi_name} = $cdi_id;
	}
	$sth->finish;
	undef $sth;


	#FMA:10001	Pedicle of eighth thoracic vertebra	FMA:11895	Left pedicle of eighth thoracic vertebra	FMA:11894	Right pedicle of eighth thoracic vertebra
	open($IN, $inference_one_path_trio_file) or die "$! [$inference_one_path_trio_file]";
	while(<$IN>){
		chomp;
		my($cdi_pname,$cdi_pname_e,$cdi_lname,$cdi_lname_e,$cdi_rname,$cdi_rname_e) = split(/\t/);
		$cdi_pname = $1.$2 if($cdi_pname =~ /^(FMA):([0-9]+)$/);
		$cdi_lname = $1.$2 if($cdi_lname =~ /^(FMA):([0-9]+)$/);
		$cdi_rname = $1.$2 if($cdi_rname =~ /^(FMA):([0-9]+)$/);

		&cgi_lib::common::message("exists [$cdi_lname]") if(exists $TRIO_L->{$cdi_lname});
		&cgi_lib::common::message("exists [$cdi_rname]") if(exists $TRIO_R->{$cdi_rname});
		&cgi_lib::common::message("exists [$cdi_pname]") if(exists $TRIO_P->{$cdi_pname});

		$TRIO_L->{$cdi_lname} = $cdi_pname;
		$TRIO_R->{$cdi_rname} = $cdi_pname;
		$TRIO_P->{$cdi_pname} = {
			left => $cdi_lname,
			right => $cdi_rname
		};

		$TRIO->{$cdi_lname} = $cdi_pname;
		$TRIO->{$cdi_rname} = $cdi_pname;


		$TRIO_COUNT->{$cdi_lname} = ($TRIO_COUNT->{$cdi_lname} || 0) + 1;
		$TRIO_COUNT->{$cdi_rname} = ($TRIO_COUNT->{$cdi_rname} || 0) + 1;

	}
	close($IN);

	#FMA:0328327	Right fetal pterygoid process	regional_part_of	FMA:328082	Fetal sphenoid	given_in_input_data	1
	open($IN, $inference_out_file) or die "$! [$inference_out_file]";
	while(<$IN>){
		chomp;
		my($cdi_name,$cdi_name_e,$relation_partof,$cdi_pname,$cdi_pname_e,$order) = split(/\t/);
		$cdi_pname = $1.$2 if($cdi_pname =~ /^(FMA):([0-9]+)$/);
		$cdi_name = $1.$2  if($cdi_name =~ /^(FMA):([0-9]+)$/);

#		say STDERR "unknown [$cdi_name]" unless(exists $TRIO->{$cdi_name} && exists $TRIO->{$cdi_pname});
		next unless(exists $TRIO->{$cdi_name});

#		say STDERR "exists [$cdi_name]" if(exists $INFER->{$cdi_name});

		$INFER->{$cdi_name}->{$cdi_pname}->{$relation_partof} = undef;
#		delete $TRIO->{$cdi_name};

	}
	close($IN);

	&cgi_lib::common::message(scalar keys(%$INFER));
	&cgi_lib::common::message(scalar keys(%$TRIO));
#	&cgi_lib::common::message($INFER);


	$sql = qq|select * from concept_tree where ci_id=$ci_id AND cb_id=$cb_id AND crl_id=4 AND cdi_id=? AND cdi_pid=?|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;

	foreach my $cdi_name (sort keys(%$INFER)){
		my $cdi_id = $FMANAME2ID->{$cdi_name};
		foreach my $cdi_pname (sort keys(%{$INFER->{$cdi_name}})){
			my $cdi_pid = $FMANAME2ID->{$cdi_pname};
			$sth->execute($cdi_id,$cdi_pid) or die $dbh->errstr;
			$rows = $sth->rows();
			$sth->finish;
			unless($rows>0){
#				say STDERR "unknown [$cdi_name][$cdi_pname]";
				delete $INFER->{$cdi_name}->{$cdi_pname};
			}elsif($TRIO_COUNT->{$cdi_name}>1){
				say STDERR "multi [$cdi_name][$cdi_pname]";
			}
		}
	}
	undef $sth;

	my $INSERT;
	foreach my $cdi_name (sort keys(%$INFER)){
		unless(scalar keys(%{$INFER->{$cdi_name}})){
#			say STDERR "empty [$cdi_name]";
			next;
		}
		my $cdi_pname = $TRIO->{$cdi_name};
		next if(exists $INSERT->{$cdi_pname});
		$INSERT->{$cdi_pname} = undef;

		my $cdi_pid = $FMANAME2ID->{$cdi_pname};
		my $cdi_lid = $FMANAME2ID->{$TRIO_P->{$cdi_pname}->{'left'}};
		my $cdi_rid = $FMANAME2ID->{$TRIO_P->{$cdi_pname}->{'right'}};

		$rows = $dbh->do(qq|INSERT INTO concept_tree_trio (ci_id,cb_id,cdi_pid,cdi_lid,cdi_rid) VALUES ($ci_id,$cb_id,$cdi_pid,$cdi_lid,$cdi_rid)|) or die $dbh->errstr;
#		&cgi_lib::common::message($rows);
	}
	&cgi_lib::common::message(scalar keys(%$INSERT));


#	$dbh->rollback;
#	exit 1;

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
