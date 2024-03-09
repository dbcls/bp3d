#!/bp3d/local/perl/bin/perl

#/ext1/project/ag/ag1/htdocs_151130/db/001_Concept/001_build_data/2015/11/04/STEP05_FINISH_FILTER_ROOT_VER02_OK.txtを想定

$|=1;

use strict;
use warnings;
use feature ':5.10';

use FindBin;
use DBD::Pg;
use File::Basename;

use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use JSON::XS;
my $JSONXS = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);

use lib qq|$FindBin::Bin/../..|,qq|$FindBin::Bin/../../../lib|,qq|$FindBin::Bin/../../../../ag-common/lib|;

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

use constant {
	USE_PARTOF_ISA_TREE => 0,	#part_ofに存在するFMAについて、is_aの親子関係を使用する
	USE_INSTANTIATED_RELATIONS => 0,	#is_aの親関係を使用する

#	PARTOF_TYPE => {
#		is_a => 0,
#
#		systemic_part_of => 1,
#		constitutional_part_of => 2,
#		regional_part_of => 3,
#
#		adheres_to => 4,
#		arterial_supply_of => 5,
#		attaches_to => 6,
#		bounded_by => 7,
#		branch_of => 8,
#		develops_from => 9,
#		efferent_to => 10,
#		receives_input_from => 11,
#		surrounded_by => 12,
#		tributary_of => 13,
#
#		member_of => 14,
#
#		nerve_supply_of => 15,
#		lymphatic_drainage_of => 16,
#		afferent_to => 17,
#		sends_output_to => 18,
#		venous_drainage_of => 19,
#		homonym_of => 20,
#		projects_from => 21,
#		projects_to => 22,
#		receives_drainage_from => 23,
#		segmental_supply_of => 24,
#		primary_segmental_supply_of => 25,
#		secondary_segmental_supply_of => 26,
#		gives_rise_to => 27,
#		segmental_composition_of => 28,
#
#		part_of => 101,
#		has_part => 102,
#
#		parallel_link => 1001,
#		converging_link => 1002,
#	}
};
=pod
#regional_part_of              : 17653
#constitutional_part_of        : 14219
#branch_of                     :  6841
#member_of                     :  2667
#nerve_supply_of               :  1867
#systemic_part_of              :  1285
#tributary_of                  :  1023
#efferent_to                   :   528
#lymphatic_drainage_of         :   450
#arterial_supply_of            :   334
#afferent_to                   :   331
#bounded_by                    :   321
#sends_output_to               :   192
#receives_input_from           :   178
#attaches_to                   :   153
#venous_drainage_of            :    95
#surrounded_by                 :    86
#homonym_of                    :    69
#projects_from                 :    42
#projects_to                   :    37
#receives_drainage_from        :    36
#segmental_supply_of           :    30
#develops_from                 :    20
#primary_segmental_supply_of   :    12
#secondary_segmental_supply_of :    12
#part_of                       :     6
#gives_rise_to                 :     5
#segmental_composition_of      :     2

INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (0,  'is_a',                          'ISA' , 0);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (14, 'member_of',                     'MBM' , 14);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (15, 'nerve_supply_of',               'NSO' , 15);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (16, 'lymphatic_drainage_of',         'LDO' , 16);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (17, 'afferent_to',                   'AFT' , 17);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (18, 'sends_output_to',               'SOT' , 18);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (19, 'venous_drainage_of',            'VDO' , 19);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (20, 'homonym_of',                    'HMO' , 20);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (21, 'projects_from',                 'PRF' , 21);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (22, 'projects_to',                   'PRT' , 22);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (23, 'receives_drainage_from',        'RDF' , 23);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (24, 'segmental_supply_of',           'SSO' , 24);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (25, 'primary_segmental_supply_of',   'PSS' , 25);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (26, 'secondary_segmental_supply_of', 'SSS' , 26);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (27, 'gives_rise_to',                 'GRT' , 27);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (28, 'segmental_composition_of',      'SCO' , 28);

INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (1001,  'parallel_link',              'PRL' , 1001);
INSERT INTO fma_partof_type (f_potid,f_potname,f_potabbr,f_order) VALUES (1002,  'converging_link',            'CVL' , 1002);
=cut

require "common_db.pl";
my $dbh = &get_dbh();
my $ci_id;
my $cb_id;

sub print_error {
	warn qq|#optins :\n| ;
	warn qq|# --host,-h : database host [default:$config->{'host'}]\n| ;
	warn qq|# --port,-p : database port [default:$config->{'port'}]\n| ;
	warn qq|#concept_info_id:concept_build_id:\n| ;
	my $sql=<<SQL;
select info.ci_id,cb_id,ci_name,cb_comment,cb_release from concept_build
left join (select ci_id,ci_name from concept_info where ci_delcause IS NULL) as info on (concept_build.ci_id=info.ci_id)
where cb_delcause IS NULL
order by cb_release,info.ci_id,cb_id;
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
		print STDERR sprintf("             %-2d :            %3d : %-5s: %-13s: %-10s\n",$ci_id,$cb_id,$ci_name,$cb_comment,$cb_release);
	}
	$sth->finish;
	undef $sth;
	exit 1;
}

if(USE_INSTANTIATED_RELATIONS && scalar @ARGV < 3){
#	warn qq|$0 concept_info_id concept_build_id InstantiatedRelations.txt\n|;
	warn qq|$0 concept_info_id concept_build_id Trio.txt\n|;
	&print_error();
}
elsif(!USE_INSTANTIATED_RELATIONS && scalar @ARGV < 2){
	warn qq|$0 concept_info_id concept_build_id\n|;
	&print_error();
}
$ci_id = $ARGV[0];
$cb_id = $ARGV[1];

my %IS_A = ();
my %PART_OF = ();
my %PART_OF_EXT = ();


my $sql_relation=<<SQL;
select f_potid,f_potname from fma_partof_type
SQL

my $PARTOF_TYPE;
my $f_potid;
my $f_potname;
my $sth_relation = $dbh->prepare($sql_relation);
$sth_relation->execute() or die $dbh->errstr;
my $column_number = 0;
$sth_relation->bind_col(++$column_number, \$f_potid, undef);
$sth_relation->bind_col(++$column_number, \$f_potname, undef);
while($sth_relation->fetch){
	$PARTOF_TYPE->{$f_potname} = $f_potid;
}
$sth_relation->finish;
undef $sth_relation;


if(USE_INSTANTIATED_RELATIONS){
	open(my $IN,$ARGV[2]) or die $!;
	while(<$IN>){
		next if(/^#/);
		chomp;
		my @DATA = split(/\t/);
		my $cdi_pname_left;
		my $cdi_name_left;
		my $cdi_pname_right;
		my $cdi_name_right;
		my $cdi_pname;
		my $relationship = lc($DATA[21]);
		$relationship =~ s/ /_/g;

		if($DATA[10] =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
			$cdi_name_left = "$1$2";
		}
#		if($DATA[25] =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
		if(defined $DATA[27] && length $DATA[27]){
#			$cdi_pname_left = "$1$2";
			$cdi_pname_left = $DATA[27];
		}
		if($DATA[15] =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
			$cdi_name_right = "$1$2";
		}
#		if($DATA[27] =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
		if(defined $DATA[30] && length $DATA[30]){
#			$cdi_pname_right = "$1$2";
			$cdi_pname_right = $DATA[30];
		}
		if($DATA[0] =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
			$cdi_pname = "$1$2";
		}
		unless(exists $PARTOF_TYPE->{$relationship}){
			die qq|Unknown relationship [$relationship]\n|;
		}
		my $p_type = $PARTOF_TYPE->{$relationship};

		if($relationship eq 'parallel_link'){
			if(defined $cdi_name_left && defined $cdi_pname_left){
				foreach my $cdi_name (split(/,/,$cdi_pname_left)){
					unless($cdi_name =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
#						say __LINE__.':'.$cdi_name;
						next;
					}
					$PART_OF{$cdi_name_left}->{"$1$2"}->{$p_type} = undef;
				}
			}
			if(defined $cdi_name_right && defined $cdi_pname_right){
				foreach my $cdi_name (split(/,/,$cdi_pname_right)){
					unless($cdi_name =~ /^\s*([A-Z]{2,3}):([0-9]+)$/){
#						say __LINE__.':'.$cdi_name;
						next;
					}
					$PART_OF{$cdi_name_right}->{"$1$2"}->{$p_type} = undef;
				}
			}
		}elsif($relationship eq 'converging_link' && defined $cdi_pname){
			$PART_OF{$cdi_name_left}->{$cdi_pname}->{$p_type} = undef if(defined $cdi_name_left);
			$PART_OF{$cdi_name_right}->{$cdi_pname}->{$p_type} = undef if(defined $cdi_name_right);
		}
	}
	close($IN);
}
#print &Data::Dumper::Dumper(\%PART_OF);
#say $JSONXS->encode(\%PART_OF);
#exit 0;

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

unless(defined $cb_raw_data){
	die "no data!!\n";
}
say $cb_release;

#my $mtime = (stat($path))[9];
#my($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime($cb_release);
#$year += 1900;
#$mon += 1;


#exit;

my $admin_openid = 'system';



my $table = qq|concept_data|;

if(&existsTable($table)){
#	my $sql =<<SQL;
#DELETE FROM buildup_tree_route where ci_id=$ci_id AND cb_id=$cb_id;
#SQL
#	print $sql;
#	$dbh->do($sql) or die $dbh->errstr;

#	$sql =<<SQL;
#DELETE FROM buildup_tree_cnum where ci_id=$ci_id AND cb_id=$cb_id;
#SQL
#	print $sql;
#	$dbh->do($sql) or die $dbh->errstr;

#	$sql =<<SQL;
#DELETE FROM buildup_tree where ci_id=$ci_id AND cb_id=$cb_id;
#SQL
#	print $sql;
#	$dbh->do($sql) or die $dbh->errstr;

	$sql =<<SQL;
DELETE FROM concept_tree where ci_id=$ci_id AND cb_id=$cb_id;
SQL
	print $sql;
	$dbh->do($sql) or die $dbh->errstr;

#	$sql =<<SQL;
#DELETE FROM concept_data where ci_id=$ci_id AND cb_id=$cb_id;
#SQL
	my $sql_fmt =<<SQL;
UPDATE concept_data SET cd_delcause='DELETE [%s]' WHERE ci_id=$ci_id AND cb_id=$cb_id;
SQL
	$sql = sprintf($sql_fmt,&File::Basename::basename($0));
	print $sql;
	my $rows_do = $dbh->do($sql) or die $dbh->errstr;
	print sprintf("%5d:[%s]\n",__LINE__,$rows_do);


	foreach my $tb (($table,qq|concept_tree|)){
		my $indexes = &getIndexnamesFromTablename($tb);
		if(defined $indexes){
			foreach my $indexname (@$indexes){
				next unless($indexname =~ /^idx_/);
				$dbh->do(qq|DROP INDEX $indexname;|) or die $dbh->errstr;
			}
		}
	}
	$dbh->do(qq|SELECT pgs2destroy();|) or die $dbh->errstr;


}else{
	die qq|Unknown table $table\n|;
}
#exit;


$sql =<<SQL;
select concept_data.cdi_id from concept_data
left join (select ci_id,cdi_id,cdi_name from concept_data_info) as i on i.ci_id=concept_data.ci_id and i.cdi_id=concept_data.cdi_id
where
  concept_data.ci_id=$ci_id and
  concept_data.cb_id=$cb_id and
  i.cdi_name=?
SQL
my $sth_sel_fma = $dbh->prepare($sql);

my $sth_ins_isa    = $dbh->prepare(qq|insert into concept_tree (ci_id,cb_id,cdi_id,cdi_pid,bul_id) values ($ci_id,$cb_id,?,?,3)|);
my $sth_ins_partof = $dbh->prepare(qq|insert into concept_tree (ci_id,cb_id,cdi_id,cdi_pid,f_potids,bul_id) values ($ci_id,$cb_id,?,?,?,4)|);

my $sth_cd_sel    = $dbh->prepare(qq|select * from concept_data where ci_id=$ci_id and cb_id=$cb_id and cdi_id=?|);
my $sth_cd_ins    = $dbh->prepare(qq|insert into concept_data (ci_id,cb_id,cd_name,cd_syn,cd_def,cdi_id,cd_entry,cd_openid) values ($ci_id,$cb_id,?,?,?,?,'$cb_release','$admin_openid')|);
my $sth_cd_upd    = $dbh->prepare(qq|update concept_data set cd_name=?,cd_syn=?,cd_def=?,cd_entry='$cb_release',cd_openid='$admin_openid',cd_delcause=null where ci_id=$ci_id and cb_id=$cb_id and cdi_id=?|);
my $sql_cd_del    = qq|delete from concept_data where ci_id=$ci_id and cb_id=$cb_id and cd_delcause is not null|;

my $sth_sel_info = $dbh->prepare(qq|select cdi_id,cdi_name_e,cdi_syn_e,cdi_def_e,cdi_openid from concept_data_info where ci_id=$ci_id and cdi_name=?|);
my $sth_ins_info = $dbh->prepare(qq|insert into concept_data_info (ci_id,cdi_name,cdi_name_e,cdi_syn_e,cdi_def_e,cdi_entry,cdi_openid) values ($ci_id,?,?,?,?,'now()','$admin_openid') RETURNING cdi_id|);
my $sth_upd_info = $dbh->prepare(qq|update concept_data_info  set cdi_name_e=?,cdi_syn_e=?,cdi_def_e=? where ci_id=$ci_id and cdi_id=?|);

sub get_cdi {
	my $cdi_name = shift;
	my $cdi_id;
	my $cdi_name_e;
	my $cdi_syn_e;
	my $cdi_def_e;
	my $cdi_openid;
	$sth_sel_info->execute($cdi_name) or die $dbh->errstr;
	$sth_sel_info->bind_col(1, \$cdi_id, undef);
	$sth_sel_info->bind_col(2, \$cdi_name_e, undef);
	$sth_sel_info->bind_col(3, \$cdi_syn_e, undef);
	$sth_sel_info->bind_col(4, \$cdi_def_e, undef);
	$sth_sel_info->bind_col(5, \$cdi_openid, undef);
	$sth_sel_info->fetch;
	$sth_sel_info->finish;
	return wantarray ? ($cdi_id,$cdi_name_e,$cdi_syn_e,$cdi_def_e,$cdi_openid) : [$cdi_id,$cdi_name_e,$cdi_syn_e,$cdi_def_e,$cdi_openid];
}

	my $term = 0;
	my %FMA;
	my $ID;
	my $rows = 0;

	foreach (split(/\n/,$cb_raw_data)){
		s/\s*$//g;
		s/^\s*//g;
		if($_ eq ""){
			if($term == 1){
#				if(defined $ID && $rows == 0){
				if(defined $ID){
					if(exists $FMA{'name'}){
						if(defined $FMA{'name'}){
							$FMA{'name'} =~ s/\s*$//g;
							$FMA{'name'} =~ s/^\s*//g;
							delete $FMA{'name'} unless(length $FMA{'name'});
						}else{
							delete $FMA{'name'};
						}
					}
					if(exists $FMA{'synonym'}){
						if(defined $FMA{'synonym'} && ref $FMA{'synonym'} eq 'ARRAY'){
							my @synonym;
							foreach my $s (@{$FMA{'synonym'}}){
								next unless(defined $s);
								$s =~ s/\s*$//g;
								$s =~ s/^\s*//g;
								push(@synonym, $s) if(length $s);
							}
							$FMA{'synonym'} = join(';',@synonym);
							delete $FMA{'synonym'} unless(length $FMA{'synonym'});
						}else{
							delete $FMA{'synonym'};
						}
					}
					if(exists $FMA{'def'}){
						if(defined $FMA{'def'}){
							$FMA{'def'} =~ s/\s*$//g;
							$FMA{'def'} =~ s/^\s*//g;
							delete $FMA{'def'} unless(length $FMA{'def'});
						}else{
							delete $FMA{'def'};
						}
					}

					my $name    = exists $FMA{'name'}    ? $FMA{'name'}    : undef;
					my $synonym = exists $FMA{'synonym'} ? $FMA{'synonym'} : undef;
					my $def     = exists $FMA{'def'}     ? $FMA{'def'}     : undef;
					my $f_sort_e;
					if(defined $name){
						my @S = ();
						foreach my $s (reverse(split(/\s+of\s+/,lc($name)))){
							$s =~ s/\s+/_/g;
							push(@S,$s);
						}
						$f_sort_e = join(" ",@S);
#						warn __LINE__,"[$f_sort_e]\n";
					}

					my($cdi_id,$cdi_name_e,$cdi_syn_e,$cdi_def_e,$cdi_openid) = &get_cdi($ID);
					unless(defined $cdi_id){
						$sth_ins_info->execute($ID,$name,$synonym,$def) or die $dbh->errstr;
						$sth_ins_info->bind_col(1, \$cdi_id, undef);
						$sth_ins_info->fetch;
						$sth_ins_info->finish;
#						$cdi_id = (&get_cdi($ID))[0];
						print sprintf("%5d:[INSERT INFO FMA %-10s][%10d]\n",__LINE__,$ID,$cdi_id);
					}elsif(
						defined $cdi_openid &&
						defined $admin_openid &&
						$cdi_openid eq $admin_openid
					){
						unless(
							defined $name &&
							defined $cdi_name_e &&
							$name eq $cdi_name_e &&
							defined $synonym &&
							defined $cdi_syn_e &&
							$synonym eq $cdi_syn_e &&
							defined $def &&
							defined $cdi_def_e &&
							$def eq $cdi_def_e
						){
							$sth_upd_info->execute($name,$synonym,$def,$cdi_id) or die $dbh->errstr;
							$sth_upd_info->finish;
							print sprintf("%5d:[UPDATE INFO FMA %-10s][%10d]\n",__LINE__,$ID,$cdi_id);
						}
					}

					$sth_cd_sel->execute($cdi_id) or die $dbh->errstr;
					my $rows_sel = $sth_cd_sel->rows();
					$sth_cd_sel->finish;
#					say $cdi_id.':'.$rows_sel;
#					exit;
					if($rows_sel>0){
						$sth_cd_upd->execute($name,$synonym,$def,$cdi_id) or die $dbh->errstr;
						$sth_cd_upd->finish;
						print sprintf("%5d:[UPDATE DATA FMA %-10s][%10d]\n",__LINE__,$ID,$cdi_id);
					}else{
						$sth_cd_ins->execute($name,$synonym,$def,$cdi_id) or die $dbh->errstr;
						$sth_cd_ins->finish;
						print sprintf("%5d:[INSERT DATA FMA %-10s][%10d]\n",__LINE__,$ID,$cdi_id);
					}

#					warn __LINE__,":[INSERT FMA $ID]\n";
#					print sprintf("\r%5d:[INSERT FMA %-9s]\r",__LINE__,$ID);

					map { delete $FMA{$_}; } keys %FMA;
					undef %FMA;
				}
			}
			$term = 0;
			undef $ID;
			next;
		}
		$term = 1 if(/^\[Term\]$/);
		next if($term == 0);

		if(/^id:\s+([A-Z]{2,3}):([0-9]+)$/){
			$ID = "$1$2";
			$sth_sel_fma->execute($ID) or die $dbh->errstr;
			$rows = $sth_sel_fma->rows();
			$sth_sel_fma->finish;

		}elsif(/^(name):\s+(\S+.*)$/){
			$FMA{$1} = $2;
		}elsif(/^(synonym):\s+\"([^\"]+)\"\s+EXACT\s+\[\]$/){
			push(@{$FMA{$1}},$2);

		}elsif(/^exact_synonym:\s+\"([^\"]+)\"\s+\[\]$/){#fma_obo.obo
			push(@{$FMA{'synonym'}},$1);

		}elsif(/^(def):\s+\"([^\"]+)\"\s+\[\]$/){
			$FMA{$1} = $2;

		}elsif(/^is_a:\s+([A-Z]{2,3}):([0-9]+)/){
			my $is_a = "$1$2";
			if(defined $ID){
#				push(@{$IS_A{$ID}},$is_a);
				$IS_A{$ID}->{$is_a} = undef;
			}
#		}elsif(/^relationship:\s+part_of\s+([A-Z]{2,3}):([0-9]+)/){
#			my $part_of = "$1$2";
#			$PART_OF{qq|$ID\t$part_of|} = "" if(defined $ID);
		}elsif(/^relationship:\s+([a-z_]+)\s+([A-Z]{2,3}):([0-9]+)/){
#			die qq|Unlnown relationship [$1]| unless(exists $PARTOF_TYPE->{$1});
			unless(exists $PARTOF_TYPE->{$1}){
				print STDERR qq|Unknown relationship [$1]\n|;
			}else{
				my $p_type = $PARTOF_TYPE->{$1};
				my $part_of = "$2$3";
				$PART_OF{$ID}->{$part_of}->{$p_type} = undef if(defined $ID);
			}
		}elsif(/^relationship:\s+(constitutional_part_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $part_of = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$part_of|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$part_of}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(regional_part_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $part_of = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$part_of|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$part_of}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(systemic_part_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $part_of = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$part_of|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$part_of}->{$p_type} = undef;
			}

		}elsif(/^relationship:\s+(adheres_to)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(arterial_supply_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(attaches_to)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(bounded_by)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(branch_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(develops_from)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(efferent_to)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
#		}elsif(/^relationship:\s+(receives_input_from)\s+([A-Z]{2,3}):([0-9]+)/){
#			my $p_type = $PARTOF_TYPE->{$1};
#			my $fmaid = "$2$3";
#			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
#			}
		}elsif(/^relationship:\s+(surrounded_by)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(tributary_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}


		#fma_obo.obo用
		}elsif(/^relationship:\s+(part_of)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				warn __LINE__,":$po_key\n";
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}
		}elsif(/^relationship:\s+(has_part)\s+([A-Z]{2,3}):([0-9]+)/){
			my $p_type = $PARTOF_TYPE->{$1};
			my $fmaid = "$2$3";
			if(defined $ID){
#				my $po_key = qq|$ID\t$fmaid|;
#				warn __LINE__,":$po_key\n";
#				$PART_OF{$po_key} = {} if(!exists($PART_OF{$po_key}));
#				$PART_OF{$po_key}->{$p_type} = "";
				$PART_OF{$ID}->{$fmaid}->{$p_type} = undef;
			}


		}else{
#			print $_,"\n";
		}


#		$sth->execute($ta_id,$ID) or die $dbh->errstr;
#		$sth->finish;

	}
#	close(IN);

=pod
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_ludia ON concept_data USING fulltexta ((ARRAY[cd_id,cd_name_j,cd_name_e,cd_name_k,cd_name_l,cd_syn_j,cd_syn_e,ta_id]));|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_name_j_b ON concept_data USING fulltextb (cd_name_j);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_name_e_b ON concept_data USING fulltextb (cd_name_e);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_name_k_b ON concept_data USING fulltextb (cd_name_k);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_name_l_b ON concept_data USING fulltextb (cd_name_l);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_syn_j_b ON concept_data USING fulltextb (cd_syn_j);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_syn_e_b ON concept_data USING fulltextb (cd_syn_e);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_decd_j_b ON concept_data USING fulltextb (cd_def_j);|) or die;
	warn __LINE__,":[CREATE INDEX]\n";
	$dbh->do(qq|CREATE INDEX idx_concept_data_cd_decd_e_b ON concept_data USING fulltextb (cd_def_e);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_data_ta_id ON concept_data USING btree (ta_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_data_phy_id ON concept_data USING btree (phy_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_data_ci_id ON concept_data USING btree (ci_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_data_cb_id ON concept_data USING btree (cb_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE UNIQUE INDEX idx_concept_data ON concept_data USING btree (ci_id,cb_id,cd_id);|) or die;
=cut

	print "\n";

	my $count = scalar keys(%IS_A);
	foreach my $f_id (sort keys(%IS_A)){
		$count--;
		$sth_sel_fma->execute($f_id) or die $dbh->errstr;
		$rows = $sth_sel_fma->rows();
		$sth_sel_fma->finish;
		unless($rows>0){
			print "\n";
			warn __LINE__,":Unknown is_a \$f_id=[$f_id]\n";
			next;
		}
#		foreach my $f_pid (sort @{$IS_A{$f_id}}){
		foreach my $f_pid (sort keys(%{$IS_A{$f_id}})){

			$sth_sel_fma->execute($f_pid) or die $dbh->errstr;
			$rows = $sth_sel_fma->rows();
			$sth_sel_fma->finish;
			unless($rows>0){
				print "\n";
				warn __LINE__,":Unknown is_a \$f_pid=[$f_pid][$f_id]\n";
				next;
			}

			my $cdi_id = (&get_cdi($f_id))[0];
			my $cdi_pid = (&get_cdi($f_pid))[0];
			$sth_ins_isa->execute($cdi_id,$cdi_pid) or die $dbh->errstr;
			$rows = $sth_ins_isa->rows();
			$sth_ins_isa->finish;
			unless($rows>0){
				print "\n";
				die __LINE__,":\n";
			}
			print sprintf("\r%5d:[%7d][INSERT FMA_ISA][%-10s][%-10s]\r",__LINE__,$count,$f_id,$f_pid);
		}
	}
	print "\n";

	if(USE_PARTOF_ISA_TREE){
		my %PART_OF_P;
		foreach my $f_id (sort keys(%PART_OF)){
			foreach my $f_pid (sort keys(%{$PART_OF{$f_id}})){
				foreach my $p_type (keys(%{$PART_OF{$f_id}->{$f_pid}})){
					$PART_OF_P{$f_pid}->{$f_id}->{$p_type} = undef;
				}
			}
		}
		my $p_type_isa = $PARTOF_TYPE->{'is_a'};
		foreach my $f_id (sort keys(%PART_OF)){
			foreach my $f_pid (sort keys(%{$IS_A{$f_id}})){
				next unless(exists $PART_OF{$f_pid} || exists $PART_OF_P{$f_pid});
				$PART_OF{$f_id}->{$f_pid}->{$p_type_isa} = undef;
				print __LINE__,":add part_of \$f_id=[$f_id]->[$f_pid]\n";

				next unless($f_pid ne 'FMA20394' && exists $IS_A{$f_pid});
				foreach my $f_ppid (sort keys(%{$IS_A{$f_pid}})){
					next unless(exists $PART_OF{$f_ppid} || exists $PART_OF_P{$f_ppid});
					$PART_OF{$f_pid}->{$f_ppid}->{$p_type_isa} = undef;
					print __LINE__,":add part_of \$f_pid=[$f_pid]->[$f_ppid]\n";
				}
			}
		}
	}

#	if(USE_INSTANTIATED_RELATIONS && scalar keys(%PART_OF_EXT) > 0){
#		foreach my $cdi_name (keys(%PART_OF_EXT)){
#			foreach my $cdi_pname (keys(%{$PART_OF_EXT{$cdi_name}})){
#				foreach my $p_type (keys(%{$PART_OF_EXT{$cdi_name}->{$cdi_pname}})){
#					foreach my $cdi_pp_name (keys(%{$PART_OF_EXT{$cdi_name}->{$cdi_pname}->{$p_type}})){
#						$PART_OF{$cdi_pname}->{$cdi_pp_name}->{$p_type} = undef unless(exists $PART_OF{$cdi_pname});
#						$PART_OF{$cdi_name}->{$cdi_pname}->{$p_type} = undef;
#					}
#				}
#			}
#		}
#	}


	$count = scalar keys(%PART_OF);
#	foreach my $key (sort keys(%PART_OF)){
	foreach my $f_id (sort keys(%PART_OF)){
		$count--;
#		my($f_id,$f_pid) = split(/\t/,$key);

		$sth_sel_fma->execute($f_id) or die $dbh->errstr;
		$rows = $sth_sel_fma->rows();
		$sth_sel_fma->finish;
		unless($rows>0){
			print "\n";
			warn __LINE__,":Unknown part_of \$f_id=[$f_id]\n";
			next;
		}

=pod
		if(USE_PARTOF_ISA_TREE && exists $IS_A{$f_id}){
			foreach my $f_pid (sort keys(%{$IS_A{$f_id}})){
				next unless(exists $PART_OF{$f_pid} || exists $PART_OF_P{$f_pid});
				$PART_OF{$f_id}->{$f_pid}->{ $PARTOF_TYPE->{'is_a'} } = undef;
				warn __LINE__,":add part_of \$f_id=[$f_id]->[$f_pid]\n";

				next unless($f_pid ne 'FMA20394' && exists $IS_A{$f_pid});
				foreach my $f_ppid (sort keys(%{$IS_A{$f_pid}})){
					next unless(exists $PART_OF{$f_ppid} || exists $PART_OF_P{$f_ppid});
					$PART_OF{$f_pid}->{$f_ppid}->{ $PARTOF_TYPE->{'is_a'} } = undef;
					warn __LINE__,":add part_of \$f_pid=[$f_pid]->[$f_ppid]\n";
				}

			}
		}
=cut

		foreach my $f_pid (sort keys(%{$PART_OF{$f_id}})){

			$sth_sel_fma->execute($f_pid) or die $dbh->errstr;
			$rows = $sth_sel_fma->rows();
			$sth_sel_fma->finish;
			unless($rows>0){
				print "\n";
				warn __LINE__,":Unknown part_of \$f_pid=[$f_pid][$f_id]\n";
				next;
			}


#			my $p_type = join(";",sort {$a<=>$b} keys(%{$PART_OF{$key}}));
			my $p_type = join(";",sort {$a<=>$b} keys(%{$PART_OF{$f_id}->{$f_pid}}));
			my $cdi_id = (&get_cdi($f_id))[0];
			my $cdi_pid = (&get_cdi($f_pid))[0];
			$sth_ins_partof->execute($cdi_id,$cdi_pid,$p_type) or die $dbh->errstr;
			$rows = $sth_ins_partof->rows();
			$sth_ins_partof->finish;
			unless($rows>0){
				print "\n";
				die __LINE__,":\n";
			}
			print sprintf("\r%5d:[%7d][INSERT FMA_PARTOF][%-10s][%-10s]\r",__LINE__,$count,$f_id,$f_pid);
		}
	}
	print "\n";

#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE UNIQUE INDEX idx_concept_tree ON concept_tree USING btree (ci_id,cb_id,cd_id,cd_pid,bul_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_tree_cd_id ON concept_tree USING btree (ci_id,cb_id,cd_id,bul_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_tree_cd_pid ON concept_tree USING btree (ci_id,cb_id,cd_pid,bul_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_tree_bul_id ON concept_tree USING btree (ci_id,cb_id,bul_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_tree_cb_id ON concept_tree USING btree (ci_id,cb_id);|) or die;
#	warn __LINE__,":[CREATE INDEX]\n";
#	$dbh->do(qq|CREATE INDEX idx_concept_tree_ci_id ON concept_tree USING btree (ci_id);|) or die;


undef $sth_ins_isa;
undef $sth_ins_partof;
#undef $sth_haspart;

=pod
$dbh->do(qq|DELETE FROM history_concept_data_info WHERE ci_id=$ci_id|) or die;
my @COLS = ();
my $column_name;
my $sth = $dbh->prepare(qq|SELECT column_name FROM information_schema.columns WHERE table_name='concept_data_info'|);
$sth->execute() or die;
$sth->bind_col(1, \$column_name, undef);
while($sth->fetch){
	push(@COLS,$column_name) if(defined $column_name);
}
$sth->finish;
undef $sth;
$column_name = join(",",@COLS);

$dbh->do(qq|INSERT INTO history_concept_data_info ($column_name,hist_event) SELECT $column_name,h.he_id as hist_event FROM concept_data_info LEFT JOIN (select he_id,he_name from history_event) as h on h.he_name='INSERT' WHERE ci_id=$ci_id|) or die;
=cut

#my $rows_do = $dbh->do($sql_cd_del) or die $dbh->errstr;
#print sprintf("%5d:[%s]\n",__LINE__,$rows_do);


#$dbh->do(qq|ANALYZE;|) or die;
