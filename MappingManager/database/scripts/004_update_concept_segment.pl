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
	db   => 'bp3d_manage',
	host => '127.0.0.1',
	port => '8543'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_NAME'} = $config->{'db'};
$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

require "webgl_common.pl";

=pod
ALTER TABLE concept_data DROP CONSTRAINT concept_data_seg_id_fkey;
DROP VIEW view_concept_data;
DROP TABLE IF EXISTS concept_segment;

CREATE TABLE concept_segment (
  seg_id            serial,
  seg_name          text  NOT NULL,
  seg_color         text,
  seg_thum_bgcolor  text,
  seg_thum_bocolor  text,
  seg_delcause      text,
  seg_entry         timestamp without time zone,
  seg_openid        text,
  PRIMARY KEY (seg_id),
  UNIQUE(seg_name)
);

INSERT INTO concept_segment (seg_name,seg_color,seg_thum_bgcolor,seg_entry,seg_openid) VALUES ('artery','#cc0000','#ff9999',now(),'system');   --動脈
INSERT INTO concept_segment (seg_name,seg_color,seg_thum_bgcolor,seg_entry,seg_openid) VALUES ('vein','#0000cc','#9999ff',now(),'system');     --静脈
INSERT INTO concept_segment (seg_name,seg_color,seg_thum_bgcolor,seg_entry,seg_openid) VALUES ('nerve','#cccc00','#e7e700',now(),'system');    --神経
INSERT INTO concept_segment (seg_name,seg_color,seg_thum_bgcolor,seg_entry,seg_openid) VALUES ('bone','#ffffff','#f0f0f0',now(),'system');     --骨


INSERT INTO concept_segment (seg_id,seg_name,seg_color,seg_thum_bgcolor,seg_entry,seg_openid) VALUES (0,'other','#F0D2A0','#F0D2A0',now(),'system');   --その他

--INSERT INTO concept_segment (seg_name,seg_entry,seg_openid) VALUES ('muscle','#ffcccc',now(),'system'); --筋肉

--UPDATE concept_segment set seg_color='#cc6666' WHERE seg_name='artery';    --動脈
--UPDATE concept_segment set seg_color='#6666cc' WHERE seg_name='vein';    --静脈
--UPDATE concept_segment set seg_color='#E4E400' WHERE seg_name='nerve';    --神経
--UPDATE concept_segment set seg_color='#c6c6c6' WHERE seg_name='bone';    --骨
--UPDATE concept_segment set seg_thum_bgcolor='#f0f0f0' WHERE seg_name='bone';    --骨
UPDATE concept_segment set seg_thum_bocolor='#dddddd' WHERE seg_thum_bocolor IS NULL;
UPDATE concept_segment set seg_thum_bgcolor='#e7e700' WHERE seg_name='nerve';    --神経

ALTER TABLE concept_data ADD seg_id integer;
ALTER TABLE concept_data ADD  FOREIGN KEY (seg_id) REFERENCES concept_segment (seg_id) ON DELETE CASCADE;


ALTER TABLE concept_segment ADD seg_thum_fgcolor text;
UPDATE concept_segment set seg_thum_fgcolor='#cc0000' WHERE seg_name='artery';    --動脈
UPDATE concept_segment set seg_thum_fgcolor='#0000cc' WHERE seg_name='vein';    --静脈
UPDATE concept_segment set seg_thum_fgcolor='#cccc00' WHERE seg_name='nerve';    --神経
UPDATE concept_segment set seg_thum_fgcolor='#ffffff' WHERE seg_name='bone';    --骨
UPDATE concept_segment set seg_thum_fgcolor='#ff5100' WHERE seg_name='other';    --その他

DROP VIEW view_concept_data;
CREATE VIEW view_concept_data AS
 SELECT d.ci_id, d.cb_id, d.cdi_id, d.cd_name, d.cd_syn, d.cd_def, d.phy_id, d.seg_id, cs.seg_name, cs.seg_color, cs.seg_thum_fgcolor, cs.seg_thum_bgcolor, cs.seg_thum_bocolor, cs.seg_delcause, cs.seg_entry, d.cd_delcause, d.cd_entry, d.cd_openid, i.cdi_name, i.cdi_name_j, COALESCE(i.cdi_name_e, d.cd_name) AS cdi_name_e, i.cdi_name_k, i.cdi_name_l, i.cdi_syn_j, COALESCE(i.cdi_syn_e, d.cd_syn) AS cdi_syn_e, i.cdi_def_j, COALESCE(i.cdi_def_e, d.cd_def) AS cdi_def_e, i.cdi_taid
   FROM concept_data d
   LEFT JOIN ( SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name, concept_data_info.cdi_name_j, concept_data_info.cdi_name_e, concept_data_info.cdi_name_k, concept_data_info.cdi_name_l, concept_data_info.cdi_syn_j, concept_data_info.cdi_syn_e, concept_data_info.cdi_def_j, concept_data_info.cdi_def_e, concept_data_info.cdi_taid
           FROM concept_data_info) i ON i.ci_id = d.ci_id AND i.cdi_id = d.cdi_id
   LEFT JOIN ( SELECT * FROM concept_segment) cs ON cs.seg_id = d.seg_id
;


DROP VIEW view_concept_data;
CREATE VIEW view_concept_data AS
 SELECT
  d.ci_id,
  d.cb_id,
  d.cdi_id,
  d.cd_name,
  d.cd_syn,
  d.cd_def,
  d.phy_id,
  d.seg_id,
  cs.seg_name,
  COALESCE(cs_color.seg_color,cs_null.seg_color) as seg_color,
  COALESCE(cs_color.seg_thum_fgcolor,cs_null.seg_thum_fgcolor) as seg_thum_fgcolor,
  COALESCE(cs_color.seg_thum_bgcolor,cs_null.seg_thum_bgcolor) as seg_thum_bgcolor,
  COALESCE(cs_color.seg_thum_bocolor,cs_null.seg_thum_bocolor) as seg_thum_bocolor,
  cs.seg_delcause,
  cs.seg_entry,
  d.cd_delcause,
  d.cd_entry, d.cd_openid, i.cdi_name, i.cdi_name_j, COALESCE(i.cdi_name_e, d.cd_name) AS cdi_name_e, i.cdi_name_k, i.cdi_name_l, i.cdi_syn_j, COALESCE(i.cdi_syn_e, d.cd_syn) AS cdi_syn_e, i.cdi_def_j, COALESCE(i.cdi_def_e, d.cd_def) AS cdi_def_e, i.cdi_taid
   FROM concept_data d
   LEFT JOIN ( SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name, concept_data_info.cdi_name_j, concept_data_info.cdi_name_e, concept_data_info.cdi_name_k, concept_data_info.cdi_name_l, concept_data_info.cdi_syn_j, concept_data_info.cdi_syn_e, concept_data_info.cdi_def_j, concept_data_info.cdi_def_e, concept_data_info.cdi_taid
           FROM concept_data_info) i ON i.ci_id = d.ci_id AND i.cdi_id = d.cdi_id
   LEFT JOIN ( SELECT * FROM concept_segment) cs ON cs.seg_id = d.seg_id
   LEFT JOIN ( SELECT * FROM concept_segment where seg_delcause is null) cs_color ON cs_color.seg_id = d.seg_id
   LEFT JOIN ( SELECT * FROM concept_segment where seg_id=0) cs_null ON cs_null.seg_id = 0
;


--select ci.ci_id,ci.ci_name,cb.cb_id,cb.cb_name from concept_info as ci left join (select ci_id,cb_id,cb_name,cb_use from concept_build) as cb on cb.ci_id=ci.ci_id where ci_use and cb_use;
=cut

my %DEF_SEG = (
	'artery' => [qw|FMA86187 FMA63812|],	#動脈
#	'artery' => [qw|FMA86187 FMA63812 FMA66332|],	#動脈(後から追加、FMA66332)
	'vein' => [qw|FMA86188 FMA63814|],	#静脈
#	'vein' => [qw|FMA86188 FMA63814 FMA67319|],	#静脈(後から追加、FMA67319)
#	'nerve' => [qw|FMA11195 FMA63819|],	#神経
	'nerve' => [qw|FMA11195 FMA63819 FMA61284|],	#神経(ADD 2014/06/10)
#	'nerve' => [qw|FMA11195 FMA63819 FMA61284 FMA65132|],	#神経(後から追加、FMA61284,FMA65132)
#	'bone' => [qw|FMA5018|],	#骨
	'bone' => [qw|FMA5018 FMA23881 FMA85544 FMA71324|],	#骨
);

my $dbh = &get_dbh();

#my $root_cdi_id = undef;
#eval{$root_cdi_id = ROOT_CDI_ID;};
my $root_cdi_id;

my $ci_id;
my $cb_id;
sub error {
	select(STDERR);
	$| = 1;
	say qq|$0 concept_info_id concept_build_id| ;
	say qq|#optins :|;
	say qq|# --db,-d   : database name [default:$config->{'db'}]|;
	say qq|# --host,-h : database host [default:$config->{'host'}]|;
	say qq|# --port,-p : database port [default:$config->{'port'}]|;
	say qq|#concept_info_id:concept_build_id:|;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_name,cb_release from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause is null) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause is null
order by info.ci_id,cb_id;
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
if(scalar @ARGV < 2){
	&error();
}
#=pod
$ci_id = $ARGV[0];
$cb_id = $ARGV[1];


#$dbh->{'AutoCommit'} = 0;
#$dbh->{'RaiseError'} = 1;
eval{

	$dbh->do(qq|update concept_data set seg_id=0 where ci_id=$ci_id and cb_id=$cb_id|) or die $dbh->errstr;
	my $sql_cd = qq|update concept_data set seg_id=? where ci_id=? and cb_id=? and cdi_id in (%s) and seg_id=0|;

=pod
#	my %ID2COLOR;
	my $sql_but = qq|select cdi_id,cti_cids from view_buildup_tree where ci_id=? and cb_id=? and cdi_name=?|;
	my $sth_but = $dbh->prepare($sql_but);

	my $sql_seg = qq|select seg_id from concept_segment where seg_name=?|;
	my $sth_seg = $dbh->prepare($sql_seg);




	foreach my $seg_name (sort keys(%DEF_SEG)){

		$sth_seg->execute($seg_name);
		my $seg_id;
		$sth_seg->bind_col(1, \$seg_id, undef);
		$sth_seg->fetch;
		$sth_seg->finish;
		next unless(defined $seg_id);

		foreach my $cdi_name (@{$DEF_SEG{$seg_name}}){

			$sth_but->execute($ci_id,$cb_id,$cdi_name);
			my $cdi_id;
			my $cti_cids;
			$sth_but->bind_col(1, \$cdi_id, undef);
			$sth_but->bind_col(2, \$cti_cids, undef);
			while($sth_but->fetch){
				next unless(defined $cdi_id);

				$cti_cids = &JSON::XS::decode_json($cti_cids) if(defined $cti_cids);
				push(@$cti_cids,$cdi_id);

				my $sth_cd = $dbh->prepare(sprintf($sql_cd,join(",",@$cti_cids)));
				$sth_cd->execute($seg_id,$ci_id,$cb_id);
				$sth_cd->finish;
				undef $sth_cd;

			}
			$sth_but->finish;

		}
	}
=cut

	my $column_number;
	my $FMA_HASH;
	my $GROUP2SEGID;
	my $CDI_ID2NAME;

	my $group2color_file = '/bp3d/FMASearch_SegmentUI/tools/group2color.txt';
	my $element_coloring_table_file = '/bp3d/FMASearch_SegmentUI/tools/element_coloring_table.txt';
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

			$FMA_HASH = {} unless(defined $FMA_HASH && ref $FMA_HASH eq 'HASH');
			if(exists $FMA_HASH->{$cdi_id} && defined $FMA_HASH->{$cdi_id} && $FMA_HASH->{$cdi_id}->{'color_group'} ne $color_group_name){
				&cgi_lib::common::message("exists $cdi_name");
			}
			$FMA_HASH->{$cdi_id} = {
				cdi_id => $cdi_id,
				cdi_name => $cdi_name,
				color_group => $color_group_name,
				but_depth => 0
			};

			$GROUP2FMAID = {} unless(defined $GROUP2FMAID && ref $GROUP2FMAID eq 'HASH');
			push(@{$GROUP2FMAID->{$color_group_name}}, $cdi_id-0);
		}
		close($IN);

		if(defined $FMA_HASH && ref $FMA_HASH eq 'HASH'){
			my $concept_tree_info_sql = sprintf('SELECT cdi_id,cti_depth FROM concept_tree_info WHERE ci_id=%d AND cb_id=%d AND crl_id=%d AND cdi_id IN (%s)',$ci_id,$cb_id,3,join(',',keys(%$FMA_HASH)));
			my $concept_tree_info_sth = $dbh->prepare($concept_tree_info_sql) or die $dbh->errstr;
			$concept_tree_info_sth->execute() or die $dbh->errstr;
			my $cdi_id;
			my $cti_depth;
			$column_number = 0;
			$concept_tree_info_sth->bind_col(++$column_number, \$cdi_id, undef);
			$concept_tree_info_sth->bind_col(++$column_number, \$cti_depth, undef);
			while($concept_tree_info_sth->fetch){
				next unless(exists $FMA_HASH->{$cdi_id});
				$FMA_HASH->{$cdi_id}->{'but_depth'} = $cti_depth - 0;
			}
			$concept_tree_info_sth->finish;
			undef $concept_tree_info_sth;
			undef $concept_tree_info_sql;
		}


		&cgi_lib::common::message($GROUP2COLOR);
		if(defined $GROUP2COLOR && ref $GROUP2COLOR eq 'HASH'){

			my $sth_seg = $dbh->prepare(qq|select seg_id,seg_name,seg_color from concept_segment WHERE seg_name=lower('VENOUS'::text)|);
			$sth_seg->execute();
			unless($sth_seg->rows()>0){
				$dbh->do(qq|UPDATE concept_segment SET seg_name=lower('VENOUS'::text) WHERE seg_name='vein'|) or die $dbh->errstr;
			}
			$sth_seg->finish;
			undef $sth_seg;

			$sth_seg = $dbh->prepare(qq|select seg_id,seg_name,seg_color from concept_segment WHERE seg_name=lower('NEURAL'::text)|);
			$sth_seg->execute();
			unless($sth_seg->rows()>0){
				$dbh->do(qq|UPDATE concept_segment SET seg_name=lower('NEURAL'::text) WHERE seg_name='nerve'|) or die $dbh->errstr;
			}
			$sth_seg->finish;
			undef $sth_seg;

			$sth_seg = $dbh->prepare(qq|select seg_id,seg_name,seg_color from concept_segment|);
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

	if(defined $FMA_HASH && ref $FMA_HASH eq 'HASH' && defined $GROUP2SEGID && ref $GROUP2SEGID eq 'HASH'){
		my $sth_but = $dbh->prepare(sprintf(qq|select cdi_id,cti_cids,cti_depth from concept_tree_info where ci_id=$ci_id and cb_id=$cb_id and crl_id=3 and cdi_id in (%s) order by cti_depth desc|,join(',',keys(%$FMA_HASH)))) or die $dbh->errstr;
		$sth_but->execute() or die $dbh->errstr;
		my $cdi_id;
		my $cti_cids;
		my $cti_depth;
		$column_number = 0;
		$sth_but->bind_col(++$column_number, \$cdi_id, undef);
		$sth_but->bind_col(++$column_number, \$cti_cids, undef);
		$sth_but->bind_col(++$column_number, \$cti_depth, undef);
		while($sth_but->fetch){
			$cti_cids = &cgi_lib::common::decodeJSON($cti_cids);
			$cti_cids = [] unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
			push(@$cti_cids,$cdi_id);

			my $color_group = $FMA_HASH->{$cdi_id}->{'color_group'};
			my $seg_id = $GROUP2SEGID->{$color_group};
			&cgi_lib::common::message($color_group) unless(defined $seg_id);

			my $sth_cd = $dbh->prepare(sprintf($sql_cd,join(',',@$cti_cids))) or die $dbh->errstr;
			$sth_cd->execute($seg_id,$ci_id,$cb_id) or die $dbh->errstr;
			&cgi_lib::common::message(sprintf('GROUP:[%-10s] : NAME:[%-10s] : ID:[%6d] : SEG:[%2d] : DEPTH:[%2d] : NUM:[%4d]',$color_group,$CDI_ID2NAME->{$cdi_id},$cdi_id,$seg_id,$cti_depth,$sth_cd->rows()));
			$sth_cd->finish;
			undef $sth_cd;

		}
		$sth_but->finish;
		undef $sth_but;

		my $sql_upd = qq|
update concept_data set seg_id=a.seg_pid
from (
select
 ct.ci_id,
 ct.cb_id,
 ct.cdi_id,
 ct.cdi_pid,
 cdc.seg_id as seg_cid,
 cdp.seg_id as seg_pid
from
 concept_tree as ct

left join (
 select * from concept_data
) as cdc on
 cdc.ci_id=ct.ci_id and
 cdc.cb_id=ct.cb_id and
 cdc.cdi_id=ct.cdi_id

left join (
 select * from concept_data
) as cdp on
 cdp.ci_id=ct.ci_id and
 cdp.cb_id=ct.cb_id and
 cdp.cdi_id=ct.cdi_pid

where (ct.ci_id,ct.cb_id,ct.crl_id,ct.cdi_id) in (
 select ci_id,cb_id,min(crl_id) as crl_id,cdi_id from concept_tree where ci_id=$ci_id and cb_id=$cb_id and cdi_id in ( select cdi_id from concept_data_info where is_user_data ) group by ci_id,cb_id,cdi_id
)
and cdc.seg_id <> cdp.seg_id
) as a
where
 concept_data.ci_id=a.ci_id and
 concept_data.cb_id=a.cb_id and
 concept_data.cdi_id=a.cdi_id
;
|;
		my $rows = $dbh->do($sql_upd) or die $dbh->errstr;
		&cgi_lib::common::message($rows);



#		$dbh->rollback;
#		&cgi_lib::common::message('');
#		exit;

	}
	else{
		my $sql_seg = qq|select seg_id,cdi_ids from concept_segment where seg_delcause is null and cdi_ids is not null|;
		my $sth_seg = $dbh->prepare($sql_seg) or die $dbh->errstr;
		$sth_seg->execute() or die $dbh->errstr;
		my $seg_id;
		my $cdi_ids;
		$sth_seg->bind_col(1, \$seg_id, undef);
		$sth_seg->bind_col(2, \$cdi_ids, undef);
		while($sth_seg->fetch){
			next unless(defined $cdi_ids);
			$cdi_ids = &JSON::XS::decode_json($cdi_ids);
			if(defined $cdi_ids && ref $cdi_ids eq 'ARRAY'){
				my $sql_but = sprintf(qq|select cdi_id,cti_cids from concept_tree_info where ci_id=$ci_id and cb_id=$cb_id and crl_id=0 and cdi_id in (%s)|, join(',',@$cdi_ids));
				my $sth_but = $dbh->prepare($sql_but) or die $dbh->errstr;
				$sth_but->execute() or die $dbh->errstr;
				my $cdi_id;
				my $cti_cids;
				$sth_but->bind_col(1, \$cdi_id, undef);
				$sth_but->bind_col(2, \$cti_cids, undef);
				while($sth_but->fetch){
					next unless(defined $cdi_id);
					$cti_cids = &JSON::XS::decode_json($cti_cids) if(defined $cti_cids);
					$cti_cids = [] unless(defined $cti_cids && ref $cti_cids eq 'ARRAY');
					push(@$cti_cids,$cdi_id);
					my $sth_cd = $dbh->prepare(sprintf($sql_cd,join(",",@$cti_cids))) or die $dbh->errstr;
					$sth_cd->execute($seg_id,$ci_id,$cb_id) or die $dbh->errstr;
					$sth_cd->finish;
					undef $sth_cd;
				}
				$sth_but->finish;
				undef $sth_but;
				undef $sql_but;
			}
		}
		$sth_seg->finish;
	}


#	$dbh->do(qq|UPDATE concept_build SET cb_use=true WHERE ci_id=$ci_id AND cb_id=$cb_id|) or die $dbh->errstr;

#	$dbh->commit();
};
if($@){
	print $@,"\n";
#	$dbh->rollback;
}
#$dbh->{'AutoCommit'} = 1;
#$dbh->{'RaiseError'} = 0;

=pod
my $base_path = qq|$FindBin::Bin/../../data/$mr_version|;
unless(-e $base_path){
	umask(0);
	&File::Path::make_path($base_path, {mode => 0711});
}
$base_path .= qq|/bp3d.color|;
open(OUT,qq|> $base_path|) or die $!;
foreach my $cdi_name (sort keys(%ID2COLOR)){
	print OUT qq|$cdi_name\t$ID2COLOR{$cdi_name}\n|;
}
=cut

#print STDERR __LINE__.':ANALYZE;'."\n";
#$dbh->do(qq|ANALYZE;|) or die $!;
