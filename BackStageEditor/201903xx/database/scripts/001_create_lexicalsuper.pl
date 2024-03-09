#!/bp3d/local/perl/bin/perl

$|=1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use DBD::Pg;

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use JSON::XS;
my $JSONXS = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);

use lib qq|$FindBin::Bin/../../cgi_lib|;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db => 'bp3d',
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
	lexicalsuper=s
	lexicalsuper-exclude-words
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "webgl_common.pl";
my $dbh = &get_dbh();
my $ci_id;
my $cb_id;

sub print_error {
	select(STDERR);
	$| = 1;
	say qq|#optins :|;
	say qq|# --db,-d   : database name [default:$config->{'db'}]|;
	say qq|# --host,-h : database host [default:$config->{'host'}]|;
	say qq|# --port,-p : database port [default:$config->{'port'}]|;
	say qq|#concept_info_id:concept_build_id:|;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_comment,cb_release from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause IS NULL) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause IS NULL
order by info.ci_id,cb_id
SQL
	my $ci_name;
	my $cb_comment;
	my $cb_release;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$ci_id, undef);
	$sth->bind_col(2, \$cb_id, undef);
	$sth->bind_col(3, \$ci_name, undef);
	$sth->bind_col(4, \$cb_comment, undef);
	$sth->bind_col(5, \$cb_release, undef);
	while($sth->fetch){
#		say sprintf("             %-2d :            %3d : %-5s: %-13s: %-10s",$ci_id,$cb_id,$ci_name,$cb_comment,$cb_release);
		say sprintf("             %-2d :            %3d : %s: %s: %s",$ci_id,$cb_id,$ci_name,$cb_comment,$cb_release);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}

if(scalar @ARGV < 2){
	warn qq|$0 concept_info_id concept_build_id\n|;
	&print_error();
}

$ci_id = $ARGV[0];
$cb_id = $ARGV[1];

my $column_number = 0;
my $cb_raw_data;
my $cb_release;
#my $sql=<<SQL;
#select cb_raw_data,EXTRACT(EPOCH FROM cb_release) from concept_build where ci_id=? AND cb_id=?
#SQL
my $sql=<<SQL;
select cb_raw_data,cb_release from concept_build where ci_id=? AND cb_id=?
SQL

my $sth = $dbh->prepare($sql);
$sth->execute($ci_id,$cb_id) or die $dbh->errstr;
warn __LINE__,":\$sth->rows()=[",$sth->rows(),"]\n";
$column_number = 0;
$sth->bind_col(++$column_number, \$cb_raw_data, { pg_type => DBD::Pg::PG_BYTEA });
$sth->bind_col(++$column_number, \$cb_release, undef);
$sth->fetch;
$sth->finish;
undef $sth;

unless(defined $cb_raw_data && length $cb_raw_data){
	die "no data!!\n";
}
#say $cb_release;

my $FMA;
my $ID;
my $term = 0;
foreach (split(/\n/,$cb_raw_data)){
	s/\s*$//g;
	s/^\s*//g;

	if($_ eq ""){
		undef $ID;
		next;
	}

	if(/^\[(.+)\]$/){
		if($1 eq 'Term'){
			$term = 1;
		}
		else{
			$term = 0;
		}
	}
#	say $_;
	next if($term == 0);
#	say $_;

	if(/^id:\s+([A-Z]{2,3}):([0-9]+)$/){
		$ID = "$1$2";
	}elsif(/^name:\s+(\S+.*)$/){
		my $tmp = $1;
		$tmp =~ s/\s{2,}/ /g;
		$FMA->{lc $tmp}->{$ID} = $tmp;
	}elsif(/^synonym:\s+\"([^\"]+)\"\s+EXACT\s+\[\]$/){
		my $tmp = $1;
		$tmp =~ s/\s{2,}/ /g;
		$FMA->{lc $tmp}->{$ID} = $tmp;
	}elsif(/^exact_synonym:\s+\"([^\"]+)\"\s+\[\]$/){
		my $tmp = $1;
		$tmp =~ s/\s{2,}/ /g;
		$FMA->{lc $tmp}->{$ID} = $tmp;
	}
}

#say $JSONXS->encode($FMA);
if(defined $FMA && ref $FMA eq 'HASH'){
	foreach my $name (sort keys(%{$FMA})){
		next unless($name =~ /.+ of .+/);
		my @TEMP = split(' of ',$name);
		shift @TEMP;
		my $temp = join(' of ',@TEMP);
		next unless(exists $FMA->{$temp});
		foreach my $cid (keys(%{$FMA->{$name}})){
			foreach my $pid (keys(%{$FMA->{$temp}})){
				say sprintf("1!%s!%s!%s!%s",$cid,$name,$temp,$pid);
			}
		}
	}
}
