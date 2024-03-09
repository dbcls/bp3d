package BITS::Voxel;

use strict;
use warnings;
use feature ':5.10';

#use Exporter;

#our @ISA = (Exporter);

use strict;
use POSIX;

sub getVoxelID {
	my($dbh,$x,$y,$z) = @_;

	my $voxel_id;
	my $sth = $dbh->prepare(qq|select voxel_id from voxel_index where voxel_x=? AND voxel_y=? AND voxel_z=?|) or die $dbh->errstr;
	$sth->execute($x,$y,$z) or die $dbh->errstr;
	$sth->bind_col(1, \$voxel_id, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	unless(defined $voxel_id){
		$sth = $dbh->prepare(qq|select COALESCE(MAX(voxel_id),0) from voxel_index|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$sth->bind_col(1, \$voxel_id, undef);
		$sth->fetch;
		$sth->finish;
		undef $sth;

		$voxel_id = 0 unless(defined $voxel_id);
		$voxel_id++;

		$sth = $dbh->prepare(qq|insert into voxel_index (voxel_id,voxel_x,voxel_y,voxel_z) values (?,?,?,?)|) or die $dbh->errstr;
		$sth->execute($voxel_id,$x,$y,$z) or die $dbh->errstr;
		$sth->finish;
		undef $sth;
	}
	return $voxel_id;
}
#exit;

sub insVoxelData {
	my($dbh,$art_id,$art_data) = @_;
	return unless(defined $dbh && defined $art_id && defined $art_data);

	my $sth_sel = $dbh->prepare(qq|select * from voxel_data where voxel_id=? AND art_id=?|) or die $dbh->errstr;
	my $sth_ins = $dbh->prepare(qq|insert into voxel_data (voxel_id,art_id,art_xmin,art_xmax,art_ymin,art_ymax,art_zmin,art_zmax) values (?,?,?,?,?,?,?,?)|) or die $dbh->errstr;

	my @D = grep {/^v\s+/} split(/\n/,$art_data);
	my $VOXEL;
	foreach (@D){
		next unless(/v\s+(\-*[0-9\.]+)\s+(\-*[0-9\.]+)\s+(\-*[0-9\.]+)/);
		my($x,$y,$z) = ($1,$2,$3);
#		print qq|[$x:$y:$z]=[|,sprintf(qq|[%d:%d:%d]|,floor($x),floor($y),floor($z)),"\n";

		my $voxel_key = sprintf(qq|%d\t%d\t%d|,floor($x),floor($y),floor($z));
#		my $art_key = sprintf(qq|%s\t%d|,$art_id);
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
			my $voxel_id = &getVoxelID($dbh,$x,$y,$z);
			die __LINE__,":($x,$y,$z)\n" unless(defined $voxel_id);

			$sth_sel->execute($voxel_id,$art_id) or die $dbh->errstr;
			my $rows = $sth_sel->rows();
			$sth_sel->finish;
			unless($rows>0){
				$sth_ins->execute($voxel_id,$art_id,$vd->{'xmin'},$vd->{'xmax'},$vd->{'ymin'},$vd->{'ymax'},$vd->{'zmin'},$vd->{'zmax'}) or die $dbh->errstr;
				$sth_ins->finish;
			}
		}
		undef $VOXEL;
	}
	undef @D;
	undef $sth_ins;
	undef $sth_sel;
}

1;
