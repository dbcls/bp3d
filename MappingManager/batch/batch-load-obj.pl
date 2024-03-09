#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use warnings;
use feature ':5.10';
use DBD::Pg;

unless(defined $ARGV[0] && -e $ARGV[0] && -f $ARGV[0]){
	exit;
}

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
require "webgl_common.pl";
use cgi_lib::common;
my $dbh = &get_dbh();


my $DATAS = &cgi_lib::common::readFileJSON($ARGV[0]);
if(defined $DATAS && ref $DATAS eq 'HASH' && exists $DATAS->{'datas'} && defined $DATAS->{'datas'} && ref $DATAS->{'datas'} eq 'ARRAY'){

	umask(0);
	my $art_abs_path = &catdir($FindBin::Bin,'art_file');
	&File::Path::mkpath($art_abs_path,{mode=>0777}) unless(-e $art_abs_path);

	my $sth_data = $dbh->prepare(qq|select art_data from art_file where art_id=? order by art_serial desc NULLS FIRST limit 1|) or die $dbh->errstr;

	foreach my $data (@{$DATAS->{'datas'}}){
		next unless(defined $data && ref $data eq 'HASH');
		my $art_data_size = $data->{'art_data_size'};
		my $art_timestamp = $data->{'art_timestamp'};
		my $art_path = $data->{'art_path'};
		my $art_id = $data->{'art_id'};

		next unless(defined $art_data_size && defined $art_timestamp && defined $art_path && defined $art_id);

		my $file_path = &catfile($FindBin::Bin,$art_path);
		print STDERR __LINE__.":\$file_path=[$file_path]\n";

		my($s,$t) = (0,0);
		($s,$t) = (stat($file_path))[7,9] if(-e $file_path);
		unless($s==$art_data_size && $t==$art_timestamp){
			print STDERR __LINE__.":\$file_path=[$file_path]\n";
			my $art_data;
			$sth_data->execute($art_id) or die $dbh->errstr;
			$sth_data->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
			$sth_data->fetch;
			$sth_data->finish;

			if(defined $art_data && open(my $OBJ,"> $file_path")){
				flock($OBJ,2);
				binmode($OBJ,':utf8');
				print $OBJ $art_data;
				close($OBJ);
				undef $OBJ;
				utime $art_timestamp,$art_timestamp,$file_path;
			}
			undef $art_data;
		}
	}
}
else{
	die "Unknown format file!!";
}

unlink $ARGV[0];
