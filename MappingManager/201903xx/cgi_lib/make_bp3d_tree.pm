package make_bp3d_tree;
#!/bp3d/local/perl/bin/perl
#bp3d.treeを作成するコマンド

#use strict;
#use warnings;
#use feature ':5.10';
use vars qw($VERSION);
$VERSION = "0.01";

use constant {
	DEBUG => 1,
	USE_NSN => 1
};

use DBD::Pg;
use File::Basename;
use File::Spec;
use Cwd qw(abs_path);
use Data::Dumper;

use strict;
use FindBin;
use lib $FindBin::Bin,$FindBin::Bin.qq|/cgi_lib|;
use BITS::DensityCalc;
#require "webgl_common.pl";

#my $dbh = &get_dbh();

#use density_calc;

#print __PACKAGE__,":",__LINE__,":",Dumper(&get_rep_parent_id(ci_id=>1,cb_id=>4,bul_id=>3,md_id=>1,mv_id=>1,cdi_name=>'FMA61993')),"\n" if(DEBUG);
#exit;

sub make_bp3d_tree {
	my %arg = @_;
	my $dbh    = $arg{'dbh'};
	my $prefix = $arg{'prefix'};
	my $ci_id  = $arg{'ci_id'};
	my $cb_id  = $arg{'cb_id'};
	my $md_id  = $arg{'md_id'};
	my $mv_id  = $arg{'mv_id'};
	my $mr_id  = $arg{'mr_id'};
	my $callback  = $arg{'callback'};

warn __PACKAGE__,":",__LINE__,":[",ref $callback,"]\n" if(DEBUG);

	undef $callback unless(defined $callback && ref $callback eq 'CODE');

	my $files;
	my $use_art_ids;

	umask(0);
	&File::Path::mkpath($prefix,0,0777) unless(-e $prefix);


#------------------------------------------------------------------------------
	my $sql_model_revision=<<SQL;
select 
 mr_version,md_abbr
from
 model_revision as mr
left join(
  select md_id,md_order,md_abbr from model where md_delcause is null
) md on md.md_id = mr.md_id
where
 mr_delcause is null and
 mr.md_id=? and
 mr.mv_id=? and
 mr_id=?
order by
 md_order,mr_order
SQL
	my $sth_model_revision = $dbh->prepare($sql_model_revision);
#------------------------------------------------------------------------------
	my $sql_buildup_logic=<<SQL;
select bul_id,bul_name_e from buildup_logic where bul_use and bul_delcause is null order by bul_order
SQL
	my $sth_buildup_logic = $dbh->prepare($sql_buildup_logic);
#------------------------------------------------------------------------------
	my $sql_concept=<<SQL;
select
 ci_name,cb_name
from
 concept_build as cb
left join(
  select ci_id,ci_name from concept_info where ci_delcause is null
) ci on ci.ci_id = cb.ci_id
where
 cb_delcause is null and
 cb.ci_id=? and
 cb_id=?
order by
 cb.ci_id,cb_id
SQL
	my $sth_concept = $dbh->prepare($sql_concept);
#------------------------------------------------------------------------------
	my $sql_art=<<SQL;
select art_id from concept_art_map where ci_id=? and cb_id=? and md_id=? and mv_id=? and cm_use
SQL
	my $sth_art = $dbh->prepare($sql_art);
#------------------------------------------------------------------------------

	my $sql_rep_primitive=<<SQL;
select
 cdi.cdi_name,
 cdi.cdi_name_e,
 rep.rep_id,
 rep_a.art_id,
 rep.cdi_id
from 
 representation as rep

left join (
  select
   ci_id,
   cdi_id,
   cdi_name,
   cdi_name_e
  from
   concept_data_info
) as cdi on
  cdi.ci_id=rep.ci_id and
  cdi.cdi_id=rep.cdi_id

left join (
  select
   rep_id,
   art_id
  from
   representation_art
  group by
   rep_id,
   art_id
) as rep_a on
  rep_a.rep_id=rep.rep_id

left join (
  select
   art_id,
   ci_id,
   cb_id,
   md_id,
   mv_id,
   cdi_id
  from
   concept_art_map
  where
   cm_use and
   cm_delcause is null
) as cm on
  cm.art_id=rep_a.art_id AND
  cm.ci_id=rep.ci_id AND
  cm.cb_id=rep.cb_id AND
  cm.md_id=rep.md_id AND
  cm.mv_id=rep.mv_id AND
  cm.cdi_id=rep.cdi_id

--where
-- rep_a.art_id='FJ1005';

where
 cm.cdi_id is not null and
 (rep.md_id,rep.mv_id,rep.mr_id,rep.ci_id,rep.cb_id,rep.bul_id,rep.cdi_id) in (
   select
    md_id,
    mv_id,
    max(mr_id) as mr_id,
    ci_id,
    cb_id,
    bul_id,
    cdi_id
   from
    view_representation
   where
    md_id=? and 
    mv_id=? and 
    mr_id<=? and 
    ci_id=? and 
    cb_id=? and 
    bul_id=? and 
    rep_delcause is null
   group by
    ci_id,
    cb_id,
    md_id,
    mv_id,
    bul_id,
    cdi_id
 )
order by
-- rep_a.art_id
 cdi.cdi_name
SQL

	my $sth_rep_primitive = $dbh->prepare($sql_rep_primitive);
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


	my $ci_name;
	my $cb_name;
	my $mr_version;
	my $md_abbr;
	my $bul_id;
	my $bul_name;
	my $cdi_name;
	my $cdi_name_e;
	my $rep_id;
	my $art_id;
	my $cdi_id;

	$sth_concept->execute($ci_id,$cb_id) or die $dbh->errstr;
warn __PACKAGE__,":",__LINE__,":[",$sth_concept->rows(),"]\n" if(DEBUG);
	$sth_concept->bind_col(1, \$ci_name, undef);
	$sth_concept->bind_col(2, \$cb_name, undef);
	while($sth_concept->fetch){
warn __PACKAGE__,":",__LINE__,":[$ci_id,$cb_id,$ci_name,$cb_name]\n" if(DEBUG);
		$sth_model_revision->execute($md_id,$mv_id,$mr_id) or die $dbh->errstr;
warn __PACKAGE__,":",__LINE__,":[",$sth_model_revision->rows(),"]\n" if(DEBUG);
		$sth_model_revision->bind_col(1, \$mr_version, undef);
		$sth_model_revision->bind_col(2, \$md_abbr, undef);
		while($sth_model_revision->fetch){
warn __PACKAGE__,":",__LINE__,":\t[$md_id,$mv_id,$mr_id,$mr_version,$md_abbr]\n" if(DEBUG);
			$sth_art->execute($ci_id,$cb_id,$md_id,$mv_id) or die $dbh->errstr;
warn __PACKAGE__,":",__LINE__,":[",$sth_art->rows(),"]\n" if(DEBUG);
			if($sth_art->rows()>0){
				$sth_buildup_logic->execute() or die $dbh->errstr;
				my $buildup_logic_rows = $sth_buildup_logic->rows();
				my $buildup_logic_row = 0;
				$sth_buildup_logic->bind_col(1, \$bul_id, undef);
				$sth_buildup_logic->bind_col(2, \$bul_name, undef);
				while($sth_buildup_logic->fetch){
warn __PACKAGE__,":",__LINE__,":\t\t[$bul_id,$bul_name]\n" if(DEBUG);

	#				next unless($mv_id==1 && $bul_id==4);


					$sth_rep_primitive->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$bul_id) or die $dbh->errstr;
warn __PACKAGE__,":",__LINE__,":[",$sth_rep_primitive->rows(),"]\n" if(DEBUG);
					if($sth_rep_primitive->rows()>0){
#exit;
						my $path = File::Spec->catdir($prefix,$mr_version);
						&File::Path::mkpath($path,0,0777) unless(-e $path);
						my $bul_name_temp = $bul_name;
						$bul_name_temp =~ s/_//g;
						my $file = File::Spec->catfile($path,lc(qq|$ci_name\_$bul_name_temp\_$md_abbr.tree|));
						push(@$files,$file);
warn __PACKAGE__,":",__LINE__,":[$file]\n" if(DEBUG);
						&$callback("Create ".basename($file),++$buildup_logic_row/($buildup_logic_rows+1)) if(defined $callback);


warn __PACKAGE__,":",__LINE__,":CALL &BITS::DensityCalc::get_rep_parent_id()\n" if(DEBUG);
						my($cdi_ids,$route_ids,$use_ids) = &BITS::DensityCalc::get_rep_parent_id(dbh=>$dbh, ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,md_id=>$md_id,mv_id=>$mv_id,mr_id=>$mr_id);
#warn __PACKAGE__,":",__LINE__,":\$cdi_ids=[",Dumper($cdi_ids),"]\n" if(DEBUG);
warn __PACKAGE__,":",__LINE__,":RTN &BITS::DensityCalc::get_rep_parent_id()\n" if(DEBUG);
warn __PACKAGE__,":",__LINE__,":\$cdi_ids=[",(scalar keys(%$cdi_ids)),"]\n" if(DEBUG);
warn __PACKAGE__,":",__LINE__,":\$route_ids=[",(scalar keys(%$route_ids)),"]\n" if(DEBUG);
warn __PACKAGE__,":",__LINE__,":\$use_ids=[",(scalar keys(%$use_ids)),"]\n" if(DEBUG);
#exit;

						my %ART_ID;
						my %CDI_ID;

warn __PACKAGE__,":",__LINE__,":[$md_id,$mv_id,$mr_id,$ci_id,$cb_id,$bul_id][",$sth_rep_primitive->rows(),"]\n" if(DEBUG);
						$sth_rep_primitive->bind_col(1, \$cdi_name, undef);
						$sth_rep_primitive->bind_col(2, \$cdi_name_e, undef);
						$sth_rep_primitive->bind_col(3, \$rep_id, undef);
						$sth_rep_primitive->bind_col(4, \$art_id, undef);
						$sth_rep_primitive->bind_col(5, \$cdi_id, undef);
						while($sth_rep_primitive->fetch){
#warn __PACKAGE__,":",__LINE__,":[$cdi_id][$cdi_name][$art_id][$rep_id][$cdi_name_e]\n" if(DEBUG);
							next unless(defined $cdi_id && defined $cdi_name);

							unless(exists $cdi_ids->{$cdi_id}){
								&BITS::DensityCalc::get_rep_parent_id(dbh=>$dbh, cdi_ids=>$cdi_ids,route_ids=>$route_ids,use_ids=>$use_ids,ci_id=>$ci_id,cb_id=>$cb_id,bul_id=>$bul_id,md_id=>$md_id,mv_id=>$mv_id,cdi_id=>$cdi_id,cdi_name=>$cdi_name);
							}
							unless(exists $cdi_ids->{$cdi_id}){
								warn __PACKAGE__,":",__LINE__,":Unknown CDI:[$cdi_id][$cdi_name]\n" if(DEBUG);
								next;
							}

							if(defined $art_id){
								$ART_ID{$art_id} = {} unless(defined $ART_ID{$art_id});
								$ART_ID{$art_id}->{$cdi_name} = lc($cdi_name_e);
							}else{
								warn __PACKAGE__,":",__LINE__,":Unknown ART:[$cdi_id][$cdi_name]\n" if(DEBUG);
							}
	#						$CDI_ID{$cdi_name} = {} unless(defined $CDI_ID{$cdi_name});
	#						$CDI_ID{$cdi_name}->{'name'} = lc($cdi_name_e);
						}

warn __PACKAGE__,":",__LINE__,":\n" if(DEBUG);

						foreach my $cdi_id (keys(%$cdi_ids)){
							my $cdi_name = $cdi_ids->{$cdi_id}->{'cdi_name'};
							next if(exists $CDI_ID{$cdi_name} && exists $CDI_ID{$cdi_name}->{'pname'});
							my $cdi_name_e = $cdi_ids->{$cdi_id}->{'name'};

	#						print __PACKAGE__,":",__LINE__,":[$cdi_id][$cdi_name][$cdi_name_e]\n" if(DEBUG);

							$CDI_ID{$cdi_name} = {} unless(defined $CDI_ID{$cdi_name});
							$CDI_ID{$cdi_name}->{'name'} = lc($cdi_name_e);
							$CDI_ID{$cdi_name}->{'id'} = $cdi_id;
							next unless(exists $cdi_ids->{$cdi_id}->{'cdi_pname'});

							foreach my $cdi_pname (keys(%{$cdi_ids->{$cdi_id}->{'cdi_pname'}})){
								my $cdi_pname_e = $cdi_ids->{$cdi_id}->{'cdi_pname'}->{$cdi_pname};
								$CDI_ID{$cdi_name}->{'pname'} = {} unless(defined $CDI_ID{$cdi_name}->{'pname'});
								$CDI_ID{$cdi_name}->{'pname'}->{$cdi_pname} = lc($cdi_pname_e);
							}

						}

warn __PACKAGE__,":",__LINE__,":\$cdi_ids=[",(scalar keys(%$cdi_ids)),"]\n" if(DEBUG);
warn __PACKAGE__,":",__LINE__,":\$route_ids=[",(scalar keys(%$route_ids)),"]\n" if(DEBUG);
warn __PACKAGE__,":",__LINE__,":\$use_ids=[",(scalar keys(%$use_ids)),"]\n" if(DEBUG);
#exit;

	#					print __PACKAGE__,":",__LINE__,":",Dumper($cdi_ids),"\n" if(DEBUG);
	#					print __PACKAGE__,":",__LINE__,":",Dumper(\%ART_ID),"\n" if(DEBUG);
	#					print __PACKAGE__,":",__LINE__,":",Dumper(\%CDI_ID),"\n" if(DEBUG);
	#					exit;

warn __PACKAGE__,":",__LINE__,":\n" if(DEBUG);

						if(open(OUT,"> $file")){
							flock(OUT,2);

							my $entries = scalar keys(%CDI_ID) + scalar keys(%ART_ID);
							print OUT qq|# $entries entries, [id]\t[en]\t[kanji]\t[kana]\t[phase_number]\t[last_updated]\t[zmin]\t[zmax]\t[volume]\t[organ_system]\t[parents]\n|;


							my %cdi_ids_hash = map {$CDI_ID{$_}->{'id'} => undef} sort keys(%CDI_ID);
							my $cdi_ids_str = join(",",keys %cdi_ids_hash);

							my $sql_cdi =<<SQL;
select
 COALESCE(cdi_name_j,cdi_name_e),
 COALESCE(cdi_name_k,cdi_name_e),
 COALESCE(to_char(rep_entry,'YYYY/MM/DD'),'2010/1/1'),
 COALESCE(rep_zmin,0),
 COALESCE(rep_zmax,0),
 COALESCE(rep_volume,0),
 cdi_name,
 lower(cdi_name_e)
from
 (
   select * from view_representation where (ci_id,cb_id,md_id,mv_id,mr_id,bul_id,cdi_id) in (
     select
      ci_id,cb_id,md_id,mv_id,max(mr_id),bul_id,cdi_id
     from
      representation
     where
      ci_id=$ci_id and cb_id=$cb_id and md_id=$md_id and mv_id=$mv_id and mr_id<=$mr_id and bul_id=$bul_id and cdi_id in ($cdi_ids_str)
     group by
      ci_id,cb_id,md_id,mv_id,bul_id,cdi_id
   )
 ) as rep
order by
 cdi_name asc
SQL
							my $sth_cdi = $dbh->prepare($sql_cdi) or die $dbh->errstr;
							my $cdi_name;
							my $cdi_name_e;
							my $cdi_name_j;
							my $cdi_name_k;
							my $rep_entry;
							my $rep_zmin;
							my $rep_zmax;
							my $rep_volume;
							$sth_cdi->execute() or die $dbh->errstr;
							$sth_cdi->bind_col(1, \$cdi_name_j, undef);
							$sth_cdi->bind_col(2, \$cdi_name_k, undef);
							$sth_cdi->bind_col(3, \$rep_entry, undef);
							$sth_cdi->bind_col(4, \$rep_zmin, undef);
							$sth_cdi->bind_col(5, \$rep_zmax, undef);
							$sth_cdi->bind_col(6, \$rep_volume, undef);
							$sth_cdi->bind_col(7, \$cdi_name, undef);
							$sth_cdi->bind_col(8, \$cdi_name_e, undef);
							while($sth_cdi->fetch){
								print OUT qq|$cdi_name\t$cdi_name_e|;

								&utf8::encode($cdi_name_j) if(&utf8::is_utf8($cdi_name_j));
								&utf8::encode($cdi_name_k) if(&utf8::is_utf8($cdi_name_k));

								print OUT qq|\t$cdi_name_j\t$cdi_name_k\t$mr_version\t$rep_entry\t$rep_zmin\t$rep_zmax\t$rep_volume\tOrganSystem|;
								if(exists($CDI_ID{$cdi_name}->{'pname'})){
									foreach my $cdi_pname (keys(%{$CDI_ID{$cdi_name}->{'pname'}})){
										my $cdi_pname_e = $CDI_ID{$cdi_name}->{'pname'}->{$cdi_pname};
										print OUT qq|\t$cdi_pname_e\t0|;
									}
								}else{
									print OUT qq|\t\t|;
								}
								print OUT "\r\n";
							}
							$sth_cdi->finish;


							undef $sth_cdi;

warn __PACKAGE__,":",__LINE__,":\n" if(DEBUG);


							my $art_ids_str = "'".join("','",keys %ART_ID)."'";
							my $sql_art_info =<<SQL;
select
 COALESCE(to_char(arti.art_timestamp,'YYYY/MM/DD'),'2010/1/1'),
 COALESCE(art.art_zmin,0),
 COALESCE(art.art_zmax,0),
 COALESCE(art.art_volume,0),
 arti.art_id
from
 art_file_info as arti
left join (
  select * from art_file
) as art on art.art_id=arti.art_id
left join (
  select * from art_group
) as artg on artg.artg_id=arti.artg_id
where
 artg.atrg_use and
 artg.artg_delcause is null and
 art.art_delcause is null and
 arti.art_delcause is null and
 arti.art_id in ($art_ids_str)
order by
 arti.art_id asc
SQL
							my $sth_art_info = $dbh->prepare($sql_art_info);
							my $art_timestamp;
							my $art_zmin;
							my $art_zmax;
							my $art_volume;
							my $art_id;

							$sth_art_info->execute() or die $dbh->errstr;
							$sth_art_info->bind_col(1, \$art_timestamp, undef);
							$sth_art_info->bind_col(2, \$art_zmin, undef);
							$sth_art_info->bind_col(3, \$art_zmax, undef);
							$sth_art_info->bind_col(4, \$art_volume, undef);
							$sth_art_info->bind_col(5, \$art_id, undef);
							while($sth_art_info->fetch){
								$use_art_ids->{$art_id} = undef;
								print OUT qq|$art_id\t$art_id\t$art_id\t$art_id|;
								print OUT qq|\t$mr_version\t$art_timestamp\t$art_zmin\t$art_zmax\t$art_volume\tOrganSystem|;
								foreach my $cdi_name (sort keys(%{$ART_ID{$art_id}})){
									print OUT qq|\t$ART_ID{$art_id}->{$cdi_name}\t0|;
								}
								print OUT "\r\n";
							}
							$sth_art_info->finish;
							undef $sth_art_info;

							close(OUT);
	#						exit;
						}
					}
					$sth_rep_primitive->finish;
warn __PACKAGE__,":",__LINE__,":\n\n" if(DEBUG);
#exit;
				}
				$sth_buildup_logic->finish;
			}
			$sth_art->finish;
		}
		$sth_model_revision->finish;
	}
	$sth_concept->finish;

	undef $sth_model_revision;
	undef $sth_buildup_logic;
	undef $sth_concept;

	return ($files,$use_art_ids,$mr_version);
}

1;
