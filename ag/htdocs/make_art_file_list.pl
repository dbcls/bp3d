#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use File::Basename;
use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/IM|;

use constant VIEW_PREFIX => qq|reference_|;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %SQL;

my $view_name = VIEW_PREFIX.qq|representation|;
$SQL{$view_name}=<<SQL;
CREATE TEMPORARY VIEW $view_name AS
SELECT distinct
  ci.ci_name||cb.cb_name    as concept,
  cdi.cdi_name  as concept_id,
--  rep.art_id    as art,
--  rep.rep_id    as representation,

  md.md_name_e              as model,
  mv.mv_name_e              as version,
  art.art_id                as art_id,
  art.art_name||art.art_ext as filename,
  art.art_xmin              as xmin,
  art.art_xmax              as xmax,
  art.art_ymin              as ymin,
  art.art_ymax              as ymax,
  art.art_zmin              as zmin,
  art.art_zmax              as zmax,
  art.art_volume            as volume,
  art.art_cube_volume       as cube_volume

FROM history_representation rep
LEFT JOIN (
    SELECT concept_data_info.ci_id, concept_data_info.cdi_id, concept_data_info.cdi_name
    FROM concept_data_info
  ) cdi ON cdi.ci_id  = rep.ci_id AND
           cdi.cdi_id = rep.cdi_id
LEFT JOIN (
    SELECT concept_info.ci_id, concept_info.ci_name
    FROM concept_info
  ) ci ON ci.ci_id  = rep.ci_id
LEFT JOIN (
    SELECT concept_build.ci_id, concept_build.cb_id, concept_build.cb_name
    FROM concept_build
  ) cb ON cb.ci_id = rep.ci_id AND
          cb.cb_id = rep.cb_id

LEFT JOIN (
    SELECT *
    FROM history_art_file
  ) art ON art.art_id  = rep.art_id AND
           art.hist_serial  = rep.art_hist_serial

LEFT JOIN (
    SELECT model.md_id, model.md_name_e, model.md_name_j
    FROM model
  ) md ON md.md_id  = art.md_id
LEFT JOIN (
    SELECT model_version.md_id, model_version.mv_id, model_version.mv_version, model_version.mv_name_e, model_version.mv_name_j
    FROM model_version
  ) mv ON mv.md_id = art.md_id AND
          mv.mv_id = art.mv_id

WHERE
  rep.rep_delcause IS NULL
  AND md.md_id=1
  AND mv.mv_id=2
--  AND (mv.mv_id=2 or mv.mv_id is null)
SQL

#my $view_name = VIEW_PREFIX.qq|art_file|;

#DEBUG
if(&existsView($view_name)){
	$dbh->do(qq|drop view $view_name|) or die $dbh->errstr;
}


unless(&existsView($view_name)){
	$dbh->do($SQL{$view_name}) or die $dbh->errstr if(exists $SQL{$view_name});
}
my $columns = &getDbTableColumns($view_name);
exit unless(defined $columns);

my @cols;
my $delcause;
my %name2type;
foreach my $col (@$columns){
	next if($col->{'data_type'} eq 'bytea');
	push(@cols,$col->{'column_name'});
	$name2type{$col->{'column_name'}} = $col->{'data_type'};
}
my $sql = qq|select |.join(",",@cols).qq| from $view_name|;
$sql .= qq| where $delcause is null| if(defined $delcause);
#	print $sql;

my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
my $rows = $sth->rows();
$sth->finish;
undef $sth;

#$sql .= qq| limit $FORM{'limit'}| if(defined $FORM{'limit'});
#$sql .= qq| offset $FORM{'start'}| if(defined $FORM{'start'});

my @arr;
foreach my $col (@$columns){
	my $column_name = $col->{'column_name'};
	push(@arr,$column_name);
}
print join("\t",@arr),"\n";

my $sth = $dbh->prepare($sql) or die $dbh->errstr;
$sth->execute() or die $dbh->errstr;
while(my $href = $sth->fetchrow_hashref){

	my @arr;
	foreach my $col (@$columns){
		my $column_name = $col->{'column_name'};
		next unless(exists $href->{$column_name});
		push(@arr,$href->{$column_name});
	}
	print join("\t",@arr),"\n";
}
$sth->finish;
undef $sth;
