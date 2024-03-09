#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
use DBD::Pg;
use POSIX;
use Data::Dumper;
use Cwd qw(abs_path);
use File::Basename;
use File::Spec::Functions;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'bp3d',
	host => exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::VTK;

require "webgl_common.pl";

=pod
my($x,$y,$z) = (0.6,-0.2,-0.3);
print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,int($x),int($y),int($z)),"\n";
print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,ceil($x),ceil($y),ceil($z)),"\n";
print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,floor($x),floor($y),floor($z)),"\n";
exit;
=cut

my $dbh = &get_dbh();

my $sql=<<SQL;
DROP TABLE IF EXISTS voxel_data;
DROP TABLE IF EXISTS voxel_index;

CREATE TABLE voxel_index (
  voxel_id  serial,
  voxel_x   integer  NOT NULL, -- x座標をfloor切捨て
  voxel_y   integer  NOT NULL, -- y座標をfloor切捨て
  voxel_z   integer  NOT NULL, -- z座標をfloor切捨て
  UNIQUE(voxel_x,voxel_y,voxel_z),
  PRIMARY KEY (voxel_id)
);

CREATE TABLE voxel_data (
  voxel_id        integer       NOT NULL,
  art_id          text          NOT NULL CHECK(art_id<>''), -- art_file
  art_hist_serial integer       NOT NULL,                   -- art登録順番号(history_art_file.hist_serial)
  art_xmin        numeric(9,4)  NOT NULL,                   -- Xmin(mm)
  art_xmax        numeric(9,4)  NOT NULL,                   -- Xmax(mm)
  art_ymin        numeric(9,4)  NOT NULL,                   -- Ymin(mm)
  art_ymax        numeric(9,4)  NOT NULL,                   -- Ymax(mm)
  art_zmin        numeric(9,4)  NOT NULL,                   -- Zmin(mm)
  art_zmax        numeric(9,4)  NOT NULL,                   -- Zmax(mm)
  PRIMARY KEY (voxel_id,art_id,art_hist_serial),
  FOREIGN KEY (voxel_id) REFERENCES voxel_index (voxel_id),
  FOREIGN KEY (art_id,art_hist_serial) REFERENCES history_art_file (art_id,hist_serial)
);
SQL

#$dbh->do($sql) or die $dbh->errstr; #テーブル生成
my $sth_id_sel = $dbh->prepare(qq|select voxel_id from voxel_index where voxel_x=? AND voxel_y=? AND voxel_z=?|) or die $dbh->errstr;
my $sth_id_ins = $dbh->prepare(qq|insert into voxel_index (voxel_x,voxel_y,voxel_z) values (?,?,?) RETURNING voxel_id|) or die $dbh->errstr;

my $voxel_id_hash;

sub getVoxelID {
	my($x,$y,$z) = @_;

	my $voxel_id;
	my $voxel_key = sprintf(qq|%d\t%d\t%d|,$x,$y,$z);
	if(exists $voxel_id_hash->{$voxel_key} && defined $voxel_id_hash->{$voxel_key}){
		$voxel_id = $voxel_id_hash->{$voxel_key};
	}
	else{
		$sth_id_sel->execute($x,$y,$z) or die $dbh->errstr;
		$sth_id_sel->bind_col(1, \$voxel_id, undef);
		$sth_id_sel->fetch;
		$sth_id_sel->finish;
	#	undef $sth_id_sel;
		unless(defined $voxel_id){
			$sth_id_ins->execute($x,$y,$z) or die $dbh->errstr;
			$sth_id_ins->bind_col(1, \$voxel_id, undef);
			$sth_id_ins->fetch;
			$sth_id_ins->finish;
	#		undef $sth_id_ins;
		}
		$voxel_id_hash->{$voxel_key} = $voxel_id;
	}
	return $voxel_id;
}
#exit;

#my $sth_data_sel = $dbh->prepare(qq|select * from voxel_data where voxel_id=? AND art_id=? AND art_hist_serial=?|) or die $dbh->errstr;
my $sth_data_sel = $dbh->prepare(qq|select art_hist_serial from voxel_data where voxel_id=? AND art_id=?|) or die $dbh->errstr;
my $sth_data_ins = $dbh->prepare(qq|insert into voxel_data (voxel_id,art_id,art_hist_serial,art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax) values (?,?,?,?,?,?,?,?,?)|) or die $dbh->errstr;

my $sth_data_get = $dbh->prepare(qq|select art_data from history_art_file where art_id=? and hist_serial=?|) or die $dbh->errstr;

sub insVoxelData {
#	my($art_id,$art_hist_serial,$art_data) = @_;
	my($art_id,$art_hist_serials) = @_;
	return unless(defined $art_id && defined $art_hist_serials && ref $art_hist_serials eq 'ARRAY' && scalar @{$art_hist_serials});
	my $art_data;
	unless(defined $art_data && length $art_data){
		my $file = &catfile($FindBin::Bin,'..','art_file',qq|${art_id}.obj|);
		unless(-e $file && -f $file && -r $file && -s $file){
#			my $art_hist_serial = (sort {$b <=> $a} @{$art_hist_serials})[0];
			my $art_hist_serial = (sort {$a <=> $b} @{$art_hist_serials})[0];
			$file = &catfile($FindBin::Bin,'..','art_file',qq|${art_id}.${art_hist_serial}.obj|);
		}
		if(-e $file && -f $file && -r $file && -s $file){
			if(open(my $IN, $file)){
				local $/ = undef;
				$art_data = <$IN>;
				close($IN);
			}
		}
	}
	unless(defined $art_data && length $art_data){
		my $column_number = 0;
#		my $art_hist_serial = (sort {$b <=> $a} @{$art_hist_serials})[0];
		my $art_hist_serial = (sort {$a <=> $b} @{$art_hist_serials})[0];
		$sth_data_get->execute($art_id,$art_hist_serial) or die $dbh->errstr;
		$sth_data_get->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth_data_get->fetch;
		$sth_data_get->finish;
	}
#	return unless(defined $art_id && defined $art_hist_serial && defined $art_data);
	return unless(defined $art_data && length $art_data);

	my @D = grep {/^v\s+/} split(/\n/,$art_data);
#	print qq|$art_id:$art_hist_serial:|,scalar @D,"\n";
	print sprintf("%-8s:%3d:%10d:",$art_id,scalar @{$art_hist_serials},scalar @D);
	my $VOXEL;
	foreach (@D){
		next unless(/v\s+(\-*[0-9\.]+)\s+(\-*[0-9\.]+)\s+(\-*[0-9\.]+)/);
		my($x,$y,$z) = ($1,$2,$3);
#		print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,floor($x),floor($y),floor($z)),"\n";

		my $voxel_key = sprintf(qq|%d\t%d\t%d|,floor($x),floor($y),floor($z));
#		my $art_key = sprintf(qq|%s\t%d|,$art_id,$art_hist_serial);
		my $art_key = $art_id;
		unless(defined $VOXEL->{$voxel_key}){
			$VOXEL->{$voxel_key} = {
				xmin => $x,
				xmax => $x,
				ymin => $y,
				ymax => $y,
				zmin => $z,
				zmax => $z,
			};
		}else{
			$VOXEL->{$voxel_key}->{'xmin'} = $x if($VOXEL->{$voxel_key}->{'xmin'} > $x);
			$VOXEL->{$voxel_key}->{'xmax'} = $x if($VOXEL->{$voxel_key}->{'xmax'} < $x);
			$VOXEL->{$voxel_key}->{'ymin'} = $y if($VOXEL->{$voxel_key}->{'ymin'} > $y);
			$VOXEL->{$voxel_key}->{'ymax'} = $y if($VOXEL->{$voxel_key}->{'ymax'} < $y);
			$VOXEL->{$voxel_key}->{'zmin'} = $z if($VOXEL->{$voxel_key}->{'zmin'} > $z);
			$VOXEL->{$voxel_key}->{'zmax'} = $z if($VOXEL->{$voxel_key}->{'zmax'} < $z);
		}
	}
	print '.';
	if(defined $VOXEL){
		print '.';
		foreach my $voxel_key (keys(%$VOXEL)){
			my($x,$y,$z) = split(/\t/,$voxel_key);
			my $vd = $VOXEL->{$voxel_key};
			my $voxel_id = &getVoxelID($x,$y,$z);
			die __LINE__,":($x,$y,$z)\n" unless(defined $voxel_id);

			my $voxel_data_hash;
			my $column_number = 0;
			my $art_hist_serial;
			$sth_data_sel->execute($voxel_id,$art_id) or die $dbh->errstr;
			$sth_data_sel->bind_col(++$column_number, \$art_hist_serial, undef);
			while($sth_data_sel->fetch){
				$voxel_data_hash->{$voxel_id}->{$art_id}->{$art_hist_serial} = undef;
			}
			$sth_data_sel->finish;

			foreach my $art_hist_serial (sort {$b <=> $a} @{$art_hist_serials}){
#				next if(exists $voxel_data_hash->{$voxel_id}->{$art_id}->{$art_hist_serial});
				next if(exists $voxel_data_hash->{$voxel_id}->{$art_id});
				$sth_data_ins->execute($voxel_id,$art_id,$art_hist_serial,$vd->{'xmin'},$vd->{'xmax'},$vd->{'ymin'},$vd->{'ymax'},$vd->{'zmin'},$vd->{'zmax'}) or die $dbh->errstr;
				$sth_data_ins->finish;
			}
		}
		undef $VOXEL;
	}
	print "\n";
	undef @D;
#	undef $sth_data_ins;
#	undef $sth_data_sel;
}

sub makeVoxelData {

	my $art_hist_serials_hash;
	my $art_ids_hash;
	my $art_ids;

	my $art_data;
	my $art_id;
	my $art_hist_serial;
	my $column_number = 0;
#	my $sth = $dbh->prepare(qq|select art_id,hist_serial,art_data from history_art_file order by art_serial DESC,hist_serial DESC|) or die $dbh->errstr;
	my $sth = $dbh->prepare(qq|
select
  art_id
 ,hist_serial
-- ,art_data
from
 history_art_file
LEFT JOIN id_prefix ON id_prefix.prefix_id=history_art_file.prefix_id
WHERE (art_id,hist_serial) IN (
  SELECT
   art_id,art_hist_serial
  FROM
   concept_art_map
  WHERE
       cm_use
   AND cm_delcause IS NULL
   AND (md_id,mv_id) IN (SELECT md_id,mv_id FROM model_version WHERE mv_use AND mv_frozen AND mv_delcause IS NULL)
   AND (md_id,mv_id,mr_id) IN (SELECT md_id,mv_id,mr_id FROM model_revision WHERE mr_use AND mr_delcause IS NULL)
)
group by
  id_prefix.prefix_char
 ,art_serial
 ,art_id
 ,hist_serial
order by
  id_prefix.prefix_char DESC
 ,art_serial DESC
 ,hist_serial DESC
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_hist_serial, undef);
#	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth->fetch){
#		next unless(defined $art_id && defined $art_hist_serial && defined $art_data);
#		&insVoxelData($art_id,$art_hist_serial,$art_data);
		push(@{$art_ids}, $art_id) unless(exists $art_ids_hash->{$art_id});
		$art_ids_hash->{$art_id} = undef;
		$art_hist_serials_hash->{$art_id}->{$art_hist_serial} = undef;
	}
	$sth->finish;
	undef $sth;

	foreach $art_id (@{$art_ids}){
		&insVoxelData($art_id,[keys(%{$art_hist_serials_hash->{$art_id}})]);
	}
}

&makeVoxelData();

#print Dumper($VOXEL),"\n";
