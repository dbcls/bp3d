#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use Data::Dumper;

require "common.pl";
require "common_db.pl";
require "common_image.pl";
my $dbh = &get_dbh();

if(scalar @ARGV != 1){
	die "$0 [path]\n";
}

my $param_path = $ARGV[0];
my @TEMP = split(/\//,$param_path);
my @PATH;
foreach (@TEMP){
	push(@PATH,$_);
	my $path = join("/",@PATH);
	next if(-e $path);
	mkdir $path;
	chmod 0777,$path;
}
undef @TEMP;
undef @PATH;

my $lock = "$param_path/make_thumbnail_batch.lock";
my $lock_common_image;

$SIG{'PIPE'} = $SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	rmdir $lock if(defined $lock && -e $lock);
	rmdir $lock_common_image if(defined $lock_common_image && -e $lock_common_image);
	exit(1);
}
exit unless(mkdir($lock));
#warn qq|$lock\n|;


opendir(DIR,$param_path) || die "Can't open dir. $!\n";
my @FILES = grep /^_[0-9]+\.gif$/, readdir(DIR);
closedir(DIR);
if(scalar @FILES > 0){
	foreach (@FILES){
		unlink qq|$param_path/$_|;
	}
}

my %SKIP_FILES = ();
while(1){
	opendir(DIR,$param_path) || die "Can't open dir. $!\n";
	my @FILES = grep /\.prm$/, readdir(DIR);
	closedir(DIR);
	last if(scalar @FILES == 0);

	@FILES = sort {(stat(qq|$param_path/$a|))[9]<=>(stat(qq|$param_path/$b|))[9]} sort @FILES;

	my $json_file;
	foreach (@FILES){
		next if(exists($SKIP_FILES{$_}));
		$json_file = $_;
		last;
	}
	last unless(defined $json_file);

#	my $json_file = shift @FILES;
	my $json_file_path = qq|$param_path/$json_file|;
warn __LINE__,":[$json_file_path]\n";
	open(JSON_IN,"< $json_file_path");
	my @TEMP = <JSON_IN>;
	close(JSON_IN);
	my $json_text = join("",@TEMP);
#	my $param = from_json($json_text);
	my $param = decode_json($json_text);
	$lock_common_image = qq|$param->{out_dir}/$param->{f_id}.lock|;

	if(exists($param->{version}) && (!exists($param->{tg_id}) || !exists($param->{tgi_id}))){
		my $tg_id;
		my $tgi_id;
warn __LINE__,":[",$dbh->ping,"]\n";
		unless($dbh->ping){
			&connectDB();
			$dbh = &get_dbh();
		}
		my $sth_tree_group_item = $dbh->prepare(qq|select tg_id,tgi_id from tree_group_item where tgi_version=?|);
		$sth_tree_group_item->execute($param->{version});
warn __LINE__,":[",$sth_tree_group_item->rows,"]\n";

		my $column_number = 0;
		$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
		$sth_tree_group_item->fetch;
		if(defined $tg_id && defined $tgi_id){
			$param->{tg_id} = $tg_id;
			$param->{tgi_id} = $tgi_id;
		}
		$sth_tree_group_item->finish;
		undef $sth_tree_group_item;
	}
	my $fma = &getFMA($dbh,$param,$param->{f_id});
	if(defined $fma &&
		exists($fma->{elem_type}) && defined $fma->{elem_type} &&
		exists($fma->{point_parent}) && defined $fma->{point_parent} && scalar @{$fma->{point_parent}} > 0){
		$param->{point_parent} = $fma->{point_parent};
	}
	undef $fma;

	my $AgBoundingBox = &make_image($param->{out_dir},$param->{version},$param->{type},$param->{f_id},$param->{f_pid},$param->{point_parent});
	if(defined $AgBoundingBox){
		unlink $json_file_path;
#		if($param->{type} eq "1" && (
#			$AgBoundingBox->{xmax} ne "0.0" || $AgBoundingBox->{xmin} ne "0.0" ||
#			$AgBoundingBox->{ymax} ne "0.0" || $AgBoundingBox->{ymin} ne "0.0" ||
#			$AgBoundingBox->{zmax} ne "0.0" || $AgBoundingBox->{zmin} ne "0.0"
#		)){
#			my $bp3d_table = &getBP3DTablename($param->{version});
#			my $sth_update = $dbh->prepare(qq|update $bp3d_table set b_xmin=?,b_xmax=?,b_ymin=?,b_ymax=?,b_zmin=?,b_zmax=? where b_id=?|);
#			$sth_update->execute($AgBoundingBox->{xmin},$AgBoundingBox->{xmax},$AgBoundingBox->{ymin},$AgBoundingBox->{ymax},$AgBoundingBox->{zmin},$AgBoundingBox->{zmax},$param->{f_id});
#			$sth_update->finish;
#			undef $sth_update;
#		}
	}else{
		$SKIP_FILES{$json_file} = "";
	}
	undef $json_file;
	undef $lock_common_image;
}
rmdir($lock) if(-e $lock);
