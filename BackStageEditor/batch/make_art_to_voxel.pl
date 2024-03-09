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

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
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

sub getVoxelID {
	my($x,$y,$z) = @_;

	my $voxel_id;
	my $sth = $dbh->prepare(qq|select voxel_id from voxel_index where voxel_x=? AND voxel_y=? AND voxel_z=?|) or die $dbh->errstr;
	$sth->execute($x,$y,$z) or die $dbh->errstr;
	$sth->bind_col(1, \$voxel_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	unless(defined $voxel_id){
		my $sth = $dbh->prepare(qq|insert into voxel_index (voxel_x,voxel_y,voxel_z) values (?,?,?) RETURNING voxel_id|) or die $dbh->errstr;
		$sth->execute($x,$y,$z) or die $dbh->errstr;
		$sth->bind_col(1, \$voxel_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;
	}
	return $voxel_id;
}
#exit;

sub insVoxelData {
	my($art_id,$art_hist_serial,$art_data) = @_;
	unless(defined $art_id && defined $art_hist_serial && defined $art_data){
		my $file = &catfile($FindBin::Bin,'..','art_file',qq|${art_id}.obj|);
		unless(-e $file && -f $file && -r $file && -s $file){
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
	return unless(defined $art_id && defined $art_hist_serial && defined $art_data);

	my $sth_sel = $dbh->prepare(qq|select * from voxel_data where voxel_id=? AND art_id=? AND art_hist_serial=?|) or die $dbh->errstr;
	my $sth_ins = $dbh->prepare(qq|insert into voxel_data (voxel_id,art_id,art_hist_serial,art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax) values (?,?,?,?,?,?,?,?,?)|) or die $dbh->errstr;

	my @D = grep {/^v\s+/} split(/\n/,$art_data);
	print qq|$art_id:$art_hist_serial:|,scalar @D,"\n";
	my $VOXEL;
	foreach (@D){
		next unless(/v\s+(\-*[0-9\.]+)\s+(\-*[0-9\.]+)\s+(\-*[0-9\.]+)/);
		my($x,$y,$z) = ($1,$2,$3);
#		print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,floor($x),floor($y),floor($z)),"\n";

		my $voxel_key = sprintf(qq|%d\t%d\t%d|,floor($x),floor($y),floor($z));
		my $art_key = sprintf(qq|%s\t%d|,$art_id,$art_hist_serial);
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
	if(defined $VOXEL){
		foreach my $voxel_key (keys(%$VOXEL)){
			my($x,$y,$z) = split(/\t/,$voxel_key);
			my $vd = $VOXEL->{$voxel_key};
			my $voxel_id = &getVoxelID($x,$y,$z);
			die __LINE__,":($x,$y,$z)\n" unless(defined $voxel_id);

			$sth_sel->execute($voxel_id,$art_id,$art_hist_serial) or die $dbh->errstr;
			my $rows = $sth_sel->rows();
			$sth_sel->finish;
			unless($rows>0){
				$sth_ins->execute($voxel_id,$art_id,$art_hist_serial,$vd->{'xmin'},$vd->{'xmax'},$vd->{'ymin'},$vd->{'ymax'},$vd->{'zmin'},$vd->{'zmax'}) or die $dbh->errstr;
				$sth_ins->finish;
			}
		}
		undef $VOXEL;
	}
	undef @D;
	undef $sth_ins;
	undef $sth_sel;
}

sub makeVoxelData {

	my $art_data;
	my $art_id;
	my $art_hist_serial;
	my $column_number = 0;
	my $sth = $dbh->prepare(qq|
select
  art_id
 ,hist_serial
-- ,art_data
from
  history_art_file
order by
  art_serial DESC
 ,hist_serial DESC
|) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_hist_serial, undef);
#	$sth->bind_col(++$column_number, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
	while($sth->fetch){
#		next unless(defined $art_id && defined $art_hist_serial && defined $art_data);
		&insVoxelData($art_id,$art_hist_serial,$art_data);
	}
	$sth->finish;
	undef $sth;
}

&makeVoxelData();

#print Dumper($VOXEL),"\n";
