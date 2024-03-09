#!/bp3d/local/perl/bin/perl

use strict;
use warnings;
use feature ':5.10';

#exit 1 unless(defined $ARGV[0] && -e $ARGV[0]);

use constant {
	DEBUG => 1,
};

select(STDERR);
$| = 1;
select(STDOUT);
$| = 1;

use JSON::XS;
use Encode;
use Archive::Zip;
use IO::File;
use Data::Dumper;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);
use Cwd;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::DensityCalc;

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	host => exists $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '8543',
	verbose => 0,
	DEBUG => 0
};
&Getopt::Long::GetOptions($config,qw/
	host|h=s
	port|p=s
	verbose|v
	DEBUG|D
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};

use make_bp3d_tree;
use cgi_lib::common;

require "webgl_common.pl";
my $dbh = &get_dbh();

my $FORM;
if(defined $ARGV[0] && -e $ARGV[0]){
	open(my $IN,"< $ARGV[0]") or die qq|$! [$ARGV[0]]|;
	flock($IN,1);
	my @DATAS = <$IN>;
	close($IN);
	$FORM = &JSON::XS::decode_json(join('',@DATAS));
	undef @DATAS;
}
elsif(defined $ARGV[0] && $ARGV[0] =~ /^[0-9]+$/ && defined $ARGV[1] && $ARGV[1] =~ /^[0-9]+$/){
	my $md_id = $ARGV[0];
	my $mv_id = $ARGV[1];
	my $mr_id;
	my $ci_id;
	my $cb_id;
&cgi_lib::common::message(\@ARGV) if($config->{'DEBUG'});

	my $sth_mr = $dbh->prepare(qq|select max(mr_id) from model_revision where md_id=$md_id and mv_id=$mv_id and mr_use and mr_delcause is null|) or die $dbh->errstr;
	$sth_mr->execute() or die $dbh->errstr;
	my $col_num = 0;
	$sth_mr->bind_col(++$col_num, \$mr_id, undef);
	$sth_mr->fetch;
	$sth_mr->finish;
	undef $sth_mr;

	if(defined $mr_id){
		my $sth_mv = $dbh->prepare(qq|select ci_id,cb_id from model_version where md_id=$md_id and mv_id=$mv_id and mv_use and mv_frozen and mv_delcause is null|) or die $dbh->errstr;
		$sth_mv->execute() or die $dbh->errstr;
		$col_num = 0;
		$sth_mv->bind_col(++$col_num, \$ci_id, undef);
		$sth_mv->bind_col(++$col_num, \$cb_id, undef);
		$sth_mv->fetch;
		$sth_mv->finish;
		undef $sth_mv;
	}
	if(defined $mr_id && defined $ci_id && defined $cb_id){
		$FORM->{'ci_id'} = $ci_id;
		$FORM->{'cb_id'} = $cb_id;
		$FORM->{'md_id'} = $md_id;
		$FORM->{'mv_id'} = $mv_id;
		$FORM->{'mr_id'} = $mr_id;
		$FORM->{sessionID} = $mv_id;
	}
}
exit 1 unless(defined $FORM);
&cgi_lib::common::message($FORM) if($config->{'DEBUG'});

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	&callback("Error:[$date] KILL THIS SCRIPT!!");
	exit(1);
}

#if($config->{'DEBUG'}){
#	my $isa_tree_mix = qq|/ext1/project/WebGL/system_150930/htdocs_150909/download/download/1/2.0.1304161700/fma_isa_bp3d.tree.mix|;
#	my $partof_tree_mix = qq|/ext1/project/WebGL/system_150930/htdocs_150909/download/download/1/2.0.1304161700/fma_partof_bp3d.tree.mix|;
#	&submitDB($dbh,$FORM,$isa_tree_mix,$partof_tree_mix);
#	exit;
#}

&exportTreeAll($dbh,$FORM);

sub callback {
	my $msg = shift;
	my $val = shift;

	$val = 0 unless(defined $val);

	&cgi_lib::common::message("\$msg=[$msg]") if($config->{'verbose'});

	$FORM->{'msg'} = &cgi_lib::common::decodeUTF8($msg);
	$FORM->{'value'} = $val;

	unless($config->{'verbose'}){
		&cgi_lib::common::writeFileJSON($ARGV[0],$FORM) if(defined $ARGV[0] && -e $ARGV[0]);
	}
}

#結果をDBへ登録(2015/09/20)
sub readTreeFile {
	my $file = shift;
	my $TREE;
	my $ID2NAME;
	my $NAME2ID;
	open(my $IN,$file) or die qq|$! [$file]|;
	flock($IN,1);
	while(<$IN>){
		s/\s*$//g;
		my($id,$en,$kanji,$kana,$phase_number,$last_updated,$zmin,$zmax,$volume,$organ_system,@parents) = split(/\t/);
		$ID2NAME->{$id} = $en;
		$NAME2ID->{$en} = $id;
		my $HASH = {
			cdi_name => $id,
			cdi_name_e => $en,
			cdi_pname => undef,
			cdi_pname_e => undef
		};
		if(scalar @parents){
			while(scalar @parents){
				push(@{$HASH->{'cdi_pname_e'}},shift @parents);
				shift @parents;
			}
		}
		push(@$TREE,$HASH);
	}
	close($IN);
	undef $IN;
	if(defined $TREE){
		foreach my $item (@$TREE){
			next unless(defined $item->{'cdi_pname_e'});
			foreach my $en (@{$item->{'cdi_pname_e'}}){
				push(@{$item->{'cdi_pname'}}, $NAME2ID->{$en}) if(exists $NAME2ID->{$en});
			}
		}
	}
	return $TREE;
}
sub getCIDS {
	my $REG_TREE_HASH = shift;
	my $PIDS = shift;
	my $cdi_pid = shift;
	my $cdi_id = shift;
	my $rdt_depth = shift // 0;
	my $use_ids = shift // {};
	my $key_id = defined $cdi_id ? $cdi_id : $cdi_pid;

	foreach my $HASH (@{$REG_TREE_HASH->{$cdi_pid}}){
		$HASH->{'rdt_depth'} = $HASH->{'rdt_depth'} // 0;
	}

#	$REG_TREE_HASH->{$cdi_pid}->{'rdt_depth'} = $REG_TREE_HASH->{$cdi_pid}->{'rdt_depth'} // 0;
#	$REG_TREE_HASH->{$cdi_pid}->{'rdt_depth'} = $rdt_depth if($REG_TREE_HASH->{$cdi_pid}->{'rdt_depth'} < $rdt_depth);

	unless(exists $use_ids->{$key_id}){
		$use_ids->{$key_id} = undef;
		if(exists $PIDS->{$key_id}){
			$rdt_depth++;
			foreach my $cdi_cid (keys(%{$PIDS->{$key_id}})){
				foreach my $HASH (@{$REG_TREE_HASH->{$cdi_pid}}){
					$HASH->{'rdt_cids'}->{$cdi_cid} = undef;
				}
				foreach my $HASH (@{$REG_TREE_HASH->{$cdi_cid}}){
					$HASH->{'rdt_depth'} = $HASH->{'rdt_depth'} // 0;
					$HASH->{'rdt_depth'} = $rdt_depth if($HASH->{'rdt_depth'} < $rdt_depth);
				}
				&getCIDS($REG_TREE_HASH,$PIDS,$cdi_pid,$cdi_cid,$rdt_depth,$use_ids);
			}
		}
	}
}
sub submitDB {
	my $dbh = shift;
	my $FORM = shift;
	my $isa_tree_mix = shift;
	my $partof_tree_mix = shift;
	my $ci_id = $FORM->{'ci_id'};
	my $cb_id = $FORM->{'cb_id'};

	my $md_id = $FORM->{'md_id'};
	my $mv_id = $FORM->{'mv_id'};
	my $mr_id = $FORM->{'mr_id'};

	my $error_message;
	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
#		my $sth_del = $dbh->prepare(qq|delete from renderer_tree where ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
		my $sth_del = $dbh->prepare(qq|delete from renderer_tree where md_id=$md_id and mv_id=$mv_id|) or die $dbh->errstr;
		$sth_del->execute() or die $dbh->errstr;
		$sth_del->finish;
		undef $sth_del;

		my %BUL;
		my $sth_bul = $dbh->prepare(qq|select bul_id,bul_abbr from buildup_logic where bul_use and bul_delcause is null|) or die $dbh->errstr;
		$sth_bul->execute() or die $dbh->errstr;
		my $rows = $sth_bul->rows();
		my $bul_id;
		my $bul_abbr;
		my $col_num = 0;
		$sth_bul->bind_col(++$col_num, \$bul_id, undef);
		$sth_bul->bind_col(++$col_num, \$bul_abbr, undef);
		while($sth_bul->fetch){
			$BUL{$bul_abbr} = $bul_id;
		}
		$sth_bul->finish;
		undef $sth_bul;

		my %CDI;
		my $sth_cdi = $dbh->prepare(qq|select cdi_id,cdi_name from concept_data_info where ci_id=$ci_id and cdi_delcause is null|) or die $dbh->errstr;
		$sth_cdi->execute() or die $dbh->errstr;
		$rows = $sth_cdi->rows();
		my $cdi_id;
		my $cdi_name;
		$col_num = 0;
		$sth_cdi->bind_col(++$col_num, \$cdi_id, undef);
		$sth_cdi->bind_col(++$col_num, \$cdi_name, undef);
		while($sth_cdi->fetch){
			$CDI{$cdi_name} = $cdi_id;
		}
		$sth_cdi->finish;
		undef $sth_cdi;

		my $sth_rep = $dbh->prepare(qq|
select
 rep_id
from (
 select
  *
 from
  representation
 where
  (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,bul_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id),
    cdi_id,
    bul_id
   from
    representation
   where
    ci_id=$ci_id and
    cb_id=$cb_id and
    md_id=$md_id and
    mv_id=$mv_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    cdi_id,
    bul_id
  )
) as rep
where
 rep_delcause is null and
 cdi_id=? and
 bul_id=?
|) or die $dbh->errstr;

		my $sth_rep_excep = $dbh->prepare(qq|
select
 rep_id
from (
 select
  *
 from
  representation
 where
  (ci_id,cb_id,md_id,mv_id,mr_id,cdi_id,bul_id) in (
   select
    ci_id,
    cb_id,
    md_id,
    mv_id,
    max(mr_id),
    cdi_id,
    bul_id
   from
    representation
   where
    ci_id=$ci_id and
    cb_id=$cb_id and
    md_id=$md_id and
    mv_id=$mv_id
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    cdi_id,
    bul_id
  )
) as rep
where
 rep_delcause is null and
 cdi_id=? and
 bul_id<>?
|) or die $dbh->errstr;

		my $sth_rep_ins = $dbh->prepare(qq|insert into renderer_tree (ci_id,cb_id,md_id,mv_id,rdt_entry,rdt_openid,bul_id,cdi_id,cdi_pid,rdt_cids,rdt_depth,rep_id) values ($ci_id,$cb_id,$md_id,$mv_id,now(),'system',?,?,?,?,?,?)|) or die $dbh->errstr;

		if(-e $isa_tree_mix && -s $isa_tree_mix){
			my $bul_id = $BUL{'isa'};
			die "Undefined bul_id ['isa']" unless(defined $bul_id);
			my $ISA_TREE = &readTreeFile($isa_tree_mix);
			if(defined $ISA_TREE){
				my $REG_TREE;
				my $REG_TREE_HASH;
				my $PIDS;
				my $CIDS;
				foreach my $item (@$ISA_TREE){
#					die qq|Unknown cdi_name [$item->{'cdi_name'}]| unless(exists $CDI{$item->{'cdi_name'}} && defined $CDI{$item->{'cdi_name'}});
					unless(exists $CDI{$item->{'cdi_name'}} && defined $CDI{$item->{'cdi_name'}}){
						&cgi_lib::common::message($item->{'cdi_name'}) if($config->{'DEBUG'});
						next;
					}
					$item->{'cdi_id'} = $CDI{$item->{'cdi_name'}};
					my $cdi_id = $item->{'cdi_id'};

					my $rep_id;
					$sth_rep->execute($cdi_id,$bul_id) or die $dbh->errstr;
					$col_num = 0;
					$sth_rep->bind_col(++$col_num, \$rep_id, undef);
					$sth_rep->fetch;
					$sth_rep->finish;
					unless(defined $rep_id){
						$sth_rep_excep->execute($cdi_id,$bul_id) or die $dbh->errstr;
						$col_num = 0;
						$sth_rep_excep->bind_col(++$col_num, \$rep_id, undef);
						$sth_rep_excep->fetch;
						$sth_rep_excep->finish;
					}

					if(exists $item->{'cdi_pname'} && defined $item->{'cdi_pname'}){
						foreach my $cdi_pname (@{$item->{'cdi_pname'}}){
#							die qq|Unknown cdi_name [$cdi_pname]| unless(exists $CDI{$cdi_pname} && defined $CDI{$cdi_pname});
							unless(exists $CDI{$cdi_pname} && defined $CDI{$cdi_pname}){
								&cgi_lib::common::message($cdi_pname);
								next;
							}
							my $cdi_pid = $CDI{$cdi_pname};
							my $HASH = {
								bul_id  => $bul_id,
								cdi_id  => $cdi_id,
								cdi_pid => $cdi_pid,
								cdi_name => $item->{'cdi_name'},
								cdi_pname => $cdi_pname,
								rep_id => $rep_id,
								rdt_cids => undef,
								rdt_depth => undef
							};
							push(@{$REG_TREE_HASH->{$cdi_id}},$HASH);
							push(@$REG_TREE, $HASH);
							$PIDS->{$cdi_pid}->{$cdi_id} = undef;
							$CIDS->{$cdi_id}->{$cdi_pid} = undef;
						}
					}else{
						my $HASH = {
							bul_id  => $bul_id,
							cdi_id  => $cdi_id,
							cdi_pid => undef,
							cdi_name => $item->{'cdi_name'},
							cdi_pname => undef,
							rep_id => $rep_id,
							rdt_cids => undef,
							rdt_depth => undef
						};
						push(@{$REG_TREE_HASH->{$cdi_id}},$HASH);
						push(@$REG_TREE, $HASH);
					}
				}
				if(defined $REG_TREE_HASH){
					foreach my $cdi_pid (sort {$a<=>$b} keys(%$REG_TREE_HASH)){
						&getCIDS($REG_TREE_HASH,$PIDS,$cdi_pid);
					}
					foreach my $reg_tree (@$REG_TREE){
						$reg_tree->{'rdt_cids'} = &JSON::XS::encode_json([map {$_-0} sort {$a<=>$b} keys(%{$reg_tree->{'rdt_cids'}})]) if(defined $reg_tree->{'rdt_cids'} && ref $reg_tree->{'rdt_cids'} eq 'HASH');
					}
				}
				&cgi_lib::common::message($REG_TREE) if($config->{'DEBUG'});
				my %EXISTS_DATA;
				foreach my $reg_tree (sort {$a->{'cdi_id'} <=> $b->{'cdi_id'}} @$REG_TREE){
					&cgi_lib::common::message($reg_tree) if($config->{'DEBUG'});
					my $key = qq|$md_id,$mv_id,$ci_id,$cb_id,$reg_tree->{'cdi_id'},$reg_tree->{'cdi_pid'},$reg_tree->{'bul_id'}|;
					next if(exists $EXISTS_DATA{$key});
					$sth_rep_ins->execute($reg_tree->{'bul_id'},$reg_tree->{'cdi_id'},$reg_tree->{'cdi_pid'},$reg_tree->{'rdt_cids'},$reg_tree->{'rdt_depth'},$reg_tree->{'rep_id'}) or die $dbh->errstr;
					$sth_rep->finish;
					$EXISTS_DATA{$key} = undef;
				}
			}
		}
		if(-e $partof_tree_mix && -s $partof_tree_mix){
			my $bul_id = $BUL{'partof'};
			die "Undefined bul_id ['partof']" unless(defined $bul_id);
			my $PARTOF_TREE = &readTreeFile($partof_tree_mix);
			if(defined $PARTOF_TREE){
				my $REG_TREE;
				my $REG_TREE_HASH;
				my $PIDS;
				my $CIDS;
				foreach my $item (@$PARTOF_TREE){
#					die qq|Unknown cdi_name [$item->{'cdi_name'}]| unless(exists $CDI{$item->{'cdi_name'}} && defined $CDI{$item->{'cdi_name'}});
					unless(exists $CDI{$item->{'cdi_name'}} && defined $CDI{$item->{'cdi_name'}}){
						&cgi_lib::common::message($item->{'cdi_name'}) if($config->{'DEBUG'});
						next;
					}
					$item->{'cdi_id'} = $CDI{$item->{'cdi_name'}};
					my $cdi_id = $item->{'cdi_id'};

					my $rep_id;
					$sth_rep->execute($cdi_id,$bul_id) or die $dbh->errstr;
					$col_num = 0;
					$sth_rep->bind_col(++$col_num, \$rep_id, undef);
					$sth_rep->fetch;
					$sth_rep->finish;
					unless(defined $rep_id){
						$sth_rep_excep->execute($cdi_id,$bul_id) or die $dbh->errstr;
						$col_num = 0;
						$sth_rep_excep->bind_col(++$col_num, \$rep_id, undef);
						$sth_rep_excep->fetch;
						$sth_rep_excep->finish;
					}

					if(exists $item->{'cdi_pname'} && defined $item->{'cdi_pname'}){
						foreach my $cdi_pname (@{$item->{'cdi_pname'}}){
#							die qq|Unknown cdi_name [$cdi_pname]| unless(exists $CDI{$cdi_pname} && defined $CDI{$cdi_pname});
							unless(exists $CDI{$cdi_pname} && defined $CDI{$cdi_pname}){
								&cgi_lib::common::message($cdi_pname);
								next;
							}
							my $cdi_pid = $CDI{$cdi_pname};
							my $HASH = {
								bul_id  => $bul_id,
								cdi_id  => $cdi_id,
								cdi_pid => $cdi_pid,
								cdi_name => $item->{'cdi_name'},
								cdi_pname => $cdi_pname,
								rep_id => $rep_id,
								rdt_cids => undef,
								rdt_depth => undef
							};
							push(@{$REG_TREE_HASH->{$cdi_id}},$HASH);
							push(@$REG_TREE, $HASH);
							$PIDS->{$cdi_pid}->{$cdi_id} = undef;
							$CIDS->{$cdi_id}->{$cdi_pid} = undef;
						}
					}else{
						my $HASH = {
							bul_id  => $bul_id,
							cdi_id  => $cdi_id,
							cdi_pid => undef,
							cdi_name => $item->{'cdi_name'},
							cdi_pname => undef,
							rep_id => $rep_id,
							rdt_cids => undef,
							rdt_depth => undef
						};
						push(@{$REG_TREE_HASH->{$cdi_id}},$HASH);
						push(@$REG_TREE, $HASH);
					}
				}
				if(defined $REG_TREE_HASH){
					foreach my $cdi_pid (sort {$a<=>$b} keys(%$REG_TREE_HASH)){
						&getCIDS($REG_TREE_HASH,$PIDS,$cdi_pid);
					}
					foreach my $reg_tree (@$REG_TREE){
						$reg_tree->{'rdt_cids'} = &JSON::XS::encode_json([map {$_-0} sort {$a<=>$b} keys(%{$reg_tree->{'rdt_cids'}})]) if(defined $reg_tree->{'rdt_cids'} && ref $reg_tree->{'rdt_cids'} eq 'HASH');
					}
				}
				&cgi_lib::common::message($REG_TREE) if($config->{'DEBUG'});
				my %EXISTS_DATA;
				foreach my $reg_tree (sort {$a->{'cdi_id'} <=> $b->{'cdi_id'}} @$REG_TREE){
					&cgi_lib::common::message($reg_tree) if($config->{'DEBUG'});
					my $key = qq|$md_id,$mv_id,$ci_id,$cb_id,$reg_tree->{'cdi_id'},$reg_tree->{'cdi_pid'},$reg_tree->{'bul_id'}|;
					next if(exists $EXISTS_DATA{$key});
					$sth_rep_ins->execute($reg_tree->{'bul_id'},$reg_tree->{'cdi_id'},$reg_tree->{'cdi_pid'},$reg_tree->{'rdt_cids'},$reg_tree->{'rdt_depth'},$reg_tree->{'rep_id'}) or die $dbh->errstr;
					$sth_rep->finish;
					$EXISTS_DATA{$key} = undef;
				}

			}
		}

		undef $sth_rep;
		undef $sth_rep_excep;

		if($config->{'DEBUG'}){
			$dbh->rollback;
		}else{
			$dbh->commit();
		}
	};
	if($@){
		$error_message = $@;
		$dbh->rollback;
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
	die $error_message if(defined $error_message);
}

sub exportTreeAll {
	my $dbh = shift;
	my $FORM = shift;

	eval{

		my $ci_id = $FORM->{'ci_id'};
		my $cb_id = $FORM->{'cb_id'};

		my $md_id = $FORM->{'md_id'};
		my $mv_id = $FORM->{'mv_id'};
		my $mr_id = $FORM->{'mr_id'};

		my $md5 = $FORM->{sessionID};
		unless(defined $md5){
			my @extlist = qw|.json|;
			my($name,$dir,$ext) = &File::Basename::fileparse($ARGV[0],@extlist);
			$md5 = $name;
		}

		my $title = $FORM->{'title'} || 'All FMA List';
		my $format = $FORM->{'format'} || 'tree';

		&callback('Start',0.1);

		my $htdocs_path = &Cwd::abs_path(&catdir($FindBin::Bin,'..','htdocs','download'));
		my $out_path = &catdir($htdocs_path,'download');
		my $prefix = &catdir($out_path,$md5);
	#	print __LINE__,":\$prefix=[$prefix]\n";

		my $art_file_dir = &catdir($htdocs_path,'art_file');
		unless(-e $art_file_dir){
			my $old = umask(0);
			&File::Path::mkpath($art_file_dir,0,0777);
			umask($old);
		}

		my ($tree_files,$use_art_ids,$mr_version) = &make_bp3d_tree::make_bp3d_tree(
			dbh    => $dbh,
			prefix => $prefix,
			ci_id  => $ci_id,
			cb_id  => $cb_id,
			md_id  => $md_id,
			mv_id  => $mv_id,
			mr_id  => $mr_id,
			callback => \&callback,
			LOG => $config->{'DEBUG'} ? \*STDERR : undef
		);

		if(defined $tree_files && defined $use_art_ids && defined $mr_version){

			#レンダラー用のツリーを武藤さん作成のツールでミックスする
			my $isa_tree = $tree_files->[0];
			my $isa_tree_mix = qq|$isa_tree.mix|;
			my $isa_tree_log = qq|$isa_tree.log|;
			my $partof_tree = $tree_files->[1];
			my $partof_tree_mix = qq|$partof_tree.mix|;
			my $partof_tree_log = qq|$partof_tree.log|;
			my $mix_tool = &catfile($FindBin::Bin,'mix_tree','01_mixTree_02.pl');
			if(-e $mix_tool && -s $mix_tool && -e $isa_tree && -s $isa_tree && -e $partof_tree && -s $partof_tree){
				system(qq|/bp3d/local/perl/bin/perl $mix_tool $isa_tree $partof_tree 1>$isa_tree_mix 2>$isa_tree_log|);
				push(@$tree_files,$isa_tree_mix) if(-e $isa_tree_mix);
				push(@$tree_files,$isa_tree_log) if(-e $isa_tree_log);
				system(qq|/bp3d/local/perl/bin/perl $mix_tool $partof_tree $isa_tree 1>$partof_tree_mix 2>$partof_tree_log|);
				push(@$tree_files,$partof_tree_mix) if(-e $partof_tree_mix);
				push(@$tree_files,$partof_tree_log) if(-e $partof_tree_log);
			}

#結果をDBへ登録(2015/09/20)
			&submitDB($dbh,$FORM,$isa_tree_mix,$partof_tree_mix);
#			exit;


			my ($sec,$min,$hour,$mday,$month,$year,$wday,$stime) = localtime();
			my @weekly = ('Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sut');
	#		my $file = sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);

			my $file = defined $mr_version ? $mr_version : sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec);
			$FORM->{'zip_file'} = qq|$file.zip|;

	#		my $file_basename = qq|$file.$format|;
	#		my $file_base_ext = qq|$title.$format|;
	#		my $file_name = &catdir($out_path,$file_basename);

			$file = defined $md5 ? $md5 : (defined $mr_version ? $mr_version : sprintf("%04d%02d%02d%02d%02d%02d", $year+1900,$month+1,$mday,$hour,$min,$sec));
			my $zip_file = qq|$file.zip|;
			my $zip_file_path = &catdir($out_path,$zip_file);
			$FORM->{zip_file_path} = $zip_file_path;

			my $LF = "\n";
			my $CODE = "utf8";
			if($ENV{HTTP_USER_AGENT}=~/Windows/){
				$LF = "\r\n";
				$CODE = "shiftjis";
			}elsif($ENV{HTTP_USER_AGENT}=~/Macintosh/){
				$LF = "\r";
				$CODE = "shiftjis";
			}

			&utf8::encode($zip_file) if(&utf8::is_utf8($zip_file));
			my $zip = Archive::Zip->new();
			my $mtime = 0;
			foreach my $file_path (@$tree_files){
				my $file_basename = &File::Basename::basename($file_path);
				&callback(qq|Zip $file_basename|,0.1);

				my $temp_mtime = (stat($file_path))[9];
				$mtime = $temp_mtime if($mtime<$temp_mtime);

				&utf8::encode($file_path) if(&utf8::is_utf8($file_path));
				&utf8::decode($file_basename) unless(&utf8::is_utf8($file_basename));
				my $encoded_filename = &Encode::encode($CODE, $file_basename);

				$zip->addFile($file_path,$encoded_filename);
			}

			my $sth_art = $dbh->prepare(qq|select art_data from art_file where art_id=?|) or die $dbh->errstr;

			my $art_ids = "'".join("','",keys(%$use_art_ids))."'";
			my $sql =<<SQL;
select
 art_id,
 art_ext,
 EXTRACT(EPOCH FROM art_timestamp)
from
 art_file_info as arti
left join (
  select * from art_group
) as artg on
   artg.artg_id=arti.artg_id
where
 artg.atrg_use and
 artg.artg_delcause is null and
 arti.art_delcause is null and
 arti.art_id in ($art_ids)
group by
 art_id,
 art_ext,
 art_timestamp
order by
 art_id
SQL
			my $art_id;
			my $art_ext;
			my $art_timestamp;
			my $art_data;
			my $col_num=0;
			my $sth = $dbh->prepare($sql) or die $dbh->errstr;
			$sth->execute() or die $dbh->errstr;
			my $rows = $sth->rows();
			my $row = 0;
			$sth->bind_col(++$col_num, \$art_id, undef);
			$sth->bind_col(++$col_num, \$art_ext, undef);
			$sth->bind_col(++$col_num, \$art_timestamp, undef);
			while($sth->fetch){
				my $file_path = &catfile($art_file_dir,qq|$art_id$art_ext|);

				$row++;
				&callback(qq|[$row/$rows] Zip |.&File::Basename::basename($file_path),$row/($rows+1));

				unless(-e $file_path && (stat($file_path))[9]<=$art_timestamp){
					$sth_art->execute($art_id) or die $dbh->errstr;
					$sth_art->bind_col(1, \$art_data, { pg_type => DBD::Pg::PG_BYTEA });
					$sth_art->fetch;
					$sth_art->finish;
					next unless(defined $art_data);
					open(my $OUT,"> $file_path") or die qq|$! [$file_path]|;
					flock($OUT,2);
					binmode($OUT);
					print $OUT $art_data;
					close($OUT);
					undef $OUT;
					utime $art_timestamp,$art_timestamp,$file_path;
				}
				$mtime = $art_timestamp if($mtime<$art_timestamp);

				my $file_basename = &File::Basename::basename($file_path);
				&utf8::encode($file_path) if(&utf8::is_utf8($file_path));
				&utf8::decode($file_basename) unless(&utf8::is_utf8($file_basename));
				my $encoded_filename = &Encode::encode($CODE, $file_basename);
				$zip->addFile($file_path,$encoded_filename);
			}
			$sth->finish;
			undef $sth;
			undef $sth_art;


			&utf8::encode($zip_file_path) if(&utf8::is_utf8($zip_file_path));

			&callback('Create '.$FORM->{'zip_file'},$rows/($rows+1));
			$zip->writeToFileNamed($FORM->{'zip_file_path'});

=pod
			my $stdout = IO::File->new->fdopen(fileno(STDOUT), "w") || croak($!);
			$stdout->printflush("Content-Type: application/zip\n");
			$stdout->printflush("Content-Disposition: filename=$zip_file\n");
			$stdout->printflush("Last-Modified: ".&HTTP::Date::time2str($mtime)."\n");
		#	$stdout->printflush("Accept-Ranges: bytes\n");
		#	$stdout->printflush("Content-Length: $size\n");
			$stdout->printflush("Pragma: no-cache\n\n");
			$zip->writeToFileHandle($stdout, 0);
			$stdout->close;
=cut
		}

		&File::Path::rmtree($prefix) if(-e $prefix);
		&callback('End',1);
	};
	if($@){
		&callback('Error ['.$@.']',1);
	}
};
