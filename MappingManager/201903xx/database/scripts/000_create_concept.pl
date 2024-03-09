#!/bp3d/local/perl/bin/perl
#既存のＤＢに定義を追加する

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use Carp;
use File::Basename;

use DBD::Pg;

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

#require "common.pl";
#require "common_db.pl";
require "webgl_common.pl";
my $dbh = &get_dbh();

my $ci_id=1;
if(scalar @ARGV < 3){
	select(STDERR);
	$| = 1;
	say qq|$0 concept_build_id obo_file_path concept_build_relation [concept_build_comment]| ;
	say qq|#optins :| ;
	say qq|# --host,-h : database host [default:$config->{'host'}]| ;
	say qq|# --port,-p : database port [default:$config->{'port'}]| ;
	say qq|#concept_build_id :| ;
	my $sql=<<SQL;
select cb_id,cb_name,cb_comment from concept_build where cb_delcause is null AND ci_id=$ci_id order by cb_id;
SQL
	my $cb_id;
	my $cb_name;
	my $cb_comment;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(1, \$cb_id, undef);
	$sth->bind_col(2, \$cb_name, undef);
	$sth->bind_col(3, \$cb_comment, undef);
	while($sth->fetch){
		say sprintf("%17d : %s : %s",$cb_id,$cb_name,$cb_comment);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}
my $cb_id=shift @ARGV;
my $path=shift @ARGV;
#my $cb_comment=shift @ARGV;
my $concept_build_relation=shift @ARGV;
my $cb_comment=shift @ARGV;


#				carp qq|$! [$File::Find::name]|;
#	AUTOFS_PATH => &Cwd::abs_path(qq|$FindBin::Bin/../sequencer|),

=pod
	$dbh->do(qq|
ALTER TABLE concept_build DROP CONSTRAINT concept_build_ci_id_key1;
ALTER TABLE concept_build DROP CONSTRAINT concept_build_ci_id_key2;
ALTER TABLE concept_build ADD cb_comment text;
|);# or die $dbh->errstr;
=cut

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;
eval{
	open(my $IN,$path) or die "$@\n";
	local $/ = undef;
	my $datas = <$IN>;
	close($IN);

	my $mtime = (stat($path))[9];
	my($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime($mtime);
	$year += 1900;
	$mon += 1;

	my $cb_release = sprintf("%04d-%02d-%02d",$year,$mon,$mday);
	my $cb_rep_key = sprintf("%s%02d%02d",substr($year,2),$mon,$mday);

	my @extlist = qw|.obo|;
	my($cb_filename,$dir,$cb_ext) = &File::Basename::fileparse($path,@extlist);
	my $cb_name = $cb_filename;
	$cb_filename =~ s/\-[0-9]{6}//g;
	$cb_filename .= $cb_ext;

	if($cb_filename =~ /fma_obo/){
		$cb_name = qq|1.0|;
	}elsif($cb_filename =~ /fma2/){
		$cb_name = qq|2.0|;
	}elsif($cb_filename =~ /fma3/){
		$cb_name = qq|3.0|;
	}
#exit;
	my $cb_raw_data_size = length($datas);

#	my $cb_comment;
	$cb_comment = qq|part_of -> $concept_build_relation| unless(defined $cb_comment);

#	$dbh->do(qq|delete from concept_build where ci_id=$ci_id and cb_id=$cb_id|) or die $dbh->errstr;

	my $sth = $dbh->prepare(qq|select cb_id from concept_build where ci_id=$ci_id and cb_id=$cb_id|);
	$sth->execute() or die;
	my $rows = $sth->rows;
	$sth->finish;
	undef $sth;
	print __LINE__.qq|:\$rows=[|.$rows."]\n";

	if($rows>0){
		my $param_num = 0;
		my $sth = $dbh->prepare(qq|update concept_build set cb_name=?,cb_filename=?,cb_release=?,cb_rep_key=?,cb_raw_data=?,cb_raw_data_size=?,cb_entry=?,cb_openid='system',cb_use=false,cb_comment=? where ci_id=? and cb_id=?|);
		$sth->bind_param(++$param_num, $cb_name);
		$sth->bind_param(++$param_num, $cb_filename);
		$sth->bind_param(++$param_num, $cb_release);
		$sth->bind_param(++$param_num, $cb_rep_key);
		$sth->bind_param(++$param_num, $datas, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_param(++$param_num, $cb_raw_data_size);
		$sth->bind_param(++$param_num, $cb_release);
		$sth->bind_param(++$param_num, $cb_comment);
		$sth->bind_param(++$param_num, $ci_id);
		$sth->bind_param(++$param_num, $cb_id);
		$sth->execute() or die;
		print __LINE__.qq|:\$rows=[|,$sth->rows,"]\n";
		$sth->finish;
		undef $sth;
	}else{
		my $param_num = 0;
		my $sth = $dbh->prepare(qq|insert into concept_build (ci_id,cb_id,cb_name,cb_filename,cb_release,cb_rep_key,cb_raw_data,cb_raw_data_size,cb_entry,cb_openid,cb_use,cb_comment) values (?,?,?,?,?,?,?,?,?,'system',false,?)|);
		$sth->bind_param(++$param_num, $ci_id);
		$sth->bind_param(++$param_num, $cb_id);
		$sth->bind_param(++$param_num, $cb_name);
		$sth->bind_param(++$param_num, $cb_filename);
		$sth->bind_param(++$param_num, $cb_release);
		$sth->bind_param(++$param_num, $cb_rep_key);
		$sth->bind_param(++$param_num, $datas, { pg_type => DBD::Pg::PG_BYTEA });
		$sth->bind_param(++$param_num, $cb_raw_data_size);
		$sth->bind_param(++$param_num, $cb_release);
		$sth->bind_param(++$param_num, $cb_comment);
		$sth->execute() or die;
		print __LINE__.qq|:\$rows=[|,$sth->rows,"]\n";
		$sth->finish;
		undef $sth;
	}


	$dbh->do(qq|
UPDATE concept_build SET cb_order=(m-cb_id+1) FROM (SELECT MAX(cb_id) as m FROM concept_build WHERE ci_id=$ci_id) as a WHERE ci_id=$ci_id
|) or die $dbh->errstr;



	$dbh->do(qq|delete from concept_build_relation where ci_id=$ci_id and cb_id=$cb_id|) or die $dbh->errstr;
	$dbh->do(qq|
INSERT INTO concept_build_relation SELECT $ci_id as ci_id,$cb_id as cb_id,crt_id FROM concept_relation_type WHERE crt_name in (
'is_a',
'afferent_to',
'arterial_supply_of',
'attaches_to',
'bounded_by',
'branch_of',
'constitutional_part_of',
'develops_from',
'efferent_to',
'gives_rise_to',
'homonym_of',
'lymphatic_drainage_of',
'member_of',
'nerve_supply_of',
'part_of',
'primary_segmental_supply_of',
'projects_from',
'projects_to',
'receives_drainage_from',
'receives_input_from',
'regional_part_of',
'secondary_segmental_supply_of',
'segmental_composition_of',
'segmental_supply_of',
'sends_output_to',
'surrounded_by',
'systemic_part_of',
'tributary_of',
'venous_drainage_of'
);
|) or die $dbh->errstr;
	foreach my $relation (split(/,/, $concept_build_relation)){
		$dbh->do(qq|UPDATE concept_build_relation set cbr_use=true where ci_id=$ci_id and cb_id=$cb_id and crt_id=(SELECT crt_id FROM concept_relation_type WHERE crt_name='$relation');|) or die $dbh->errstr;
	}

#	$dbh->rollback;
	$dbh->commit();

};
if($@){
	print $@,"\n";
	$dbh->rollback;
}
$dbh->{AutoCommit} = 1;
$dbh->{RaiseError} = 0;


$dbh->do(qq|ANALYZE;|) or die $dbh->errstr;

exit;

__END__
UPDATE concept_build SET cb_order=(select max(cb_id)+1 from concept_build)-cb_id;

ALTER TABLE model_version ADD ci_id integer;
ALTER TABLE model_version ADD cb_id integer;

ALTER TABLE model_version ADD FOREIGN KEY (ci_id) REFERENCES concept_info (ci_id) ON DELETE CASCADE;
ALTER TABLE model_version ADD FOREIGN KEY (ci_id,cb_id) REFERENCES concept_build (ci_id,cb_id) ON DELETE CASCADE;

UPDATE model_version SET ci_id=1,cb_id=4;
ALTER TABLE model_version ALTER ci_id SET NOT NULL;
ALTER TABLE model_version ALTER cb_id SET NOT NULL;

ALTER TABLE history_concept_art_map DISABLE TRIGGER trig_after_history_concept_art_map;
ALTER TABLE history_concept_art_map DISABLE TRIGGER trig_before_history_concept_art_map;
ALTER TABLE concept_art_map DISABLE TRIGGER trig_after_concept_art_map;
ALTER TABLE concept_art_map DISABLE TRIGGER trig_before_concept_art_map;

UPDATE model_version   SET cb_id=5 WHERE md_id=1 AND mv_id=5;
UPDATE concept_art_map SET cb_id=5 WHERE md_id=1 AND mv_id=5;
UPDATE history_concept_art_map SET cb_id=5 WHERE md_id=1 AND mv_id=5;
UPDATE representation  SET cb_id=5 WHERE md_id=1 AND mv_id=5;

ALTER TABLE history_concept_art_map ENABLE  TRIGGER trig_after_history_concept_art_map;
ALTER TABLE history_concept_art_map ENABLE  TRIGGER trig_before_history_concept_art_map;
ALTER TABLE concept_art_map ENABLE  TRIGGER trig_after_concept_art_map;
ALTER TABLE concept_art_map ENABLE  TRIGGER trig_before_concept_art_map;
