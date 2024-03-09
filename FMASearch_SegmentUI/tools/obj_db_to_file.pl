#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use File::Basename;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use File::Path;
use File::Copy;
use DBD::Pg;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;

$ENV{'AG_DB_NAME'} = 'bp3d'      unless(exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'});
$ENV{'AG_DB_HOST'} = '127.0.0.1' unless(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
$ENV{'AG_DB_PORT'} = '8543'      unless(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();


my $sql=<<SQL;
select 
 art_filename,
 art_timestamp
from (
select
 afi.art_id || afi.art_ext as art_filename,
 EXTRACT(EPOCH FROM afi.art_timestamp) as art_timestamp
from
 concept_art_map as cm

left join (
 select * from art_file_info
) as afi on
 afi.art_id = cm.art_id

where
 cm_use and
 cm_delcause is null
) as a
group by
 art_filename,
 art_timestamp
SQL

my $ART;

my $art_filename;
my $art_timestamp;
my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my $column_number = 0;
$sth->bind_col(++$column_number, \$art_filename,   undef);
$sth->bind_col(++$column_number, \$art_timestamp,   undef);
while($sth->fetch){
	$ART->{$art_filename} = $art_timestamp - 0;
}
$sth->finish;
undef $sth;
undef $sql;

umask(0);

my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? limit 1|) or die $dbh->errstr;

my $count = scalar keys(%$ART);
foreach my $art_filename (keys(%$ART)){
	my $art_timestamp = $ART->{$art_filename};
	my $file = &catfile('art_file',$art_filename);
	my($art_id,$dir,$ext) = &File::Basename::fileparse($file,qw/.obj/);

	printf("[%04d] : %s\r",$count,$art_id);

	unless(-e $file && -f $file && -s $file){
		my $art_data;
		$sth_data->execute($art_id) or die $dbh->errstr;
		$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
		$sth_data->fetch;
		$sth_data->finish;
		if(defined $art_data && open(my $OBJ,"> $file")){
			flock($OBJ,2);
			binmode($OBJ,':utf8');
			print $OBJ $art_data;
			close($OBJ);
			undef $OBJ;
			utime $art_timestamp,$art_timestamp,$file;
		}
		undef $art_data;
	}
	if(-e $file && -f $file && -s $file){
		my ($atime,$utime) = (stat($file))[8,9];
		utime($art_timestamp, $art_timestamp, $file) unless($utime==$ART->{$art_filename});
	}
	my $gzip_file = &catfile($dir,qq|$art_id.ogz|);
	my $gz_atime = 0;
	my $gz_utime = 0;
	($gz_atime,$gz_utime) = (stat($gzip_file))[8,9] if(-e $gzip_file && -f $gzip_file);

	unless($art_timestamp == $gz_utime){
		system(qq|/bin/gzip -c -9 $file > $gzip_file|) unless(-e $gzip_file && -f $gzip_file);
		utime $art_timestamp,$art_timestamp,$gzip_file if(-e $gzip_file && -f $gzip_file);
	}
	$count--;
}
say '';
