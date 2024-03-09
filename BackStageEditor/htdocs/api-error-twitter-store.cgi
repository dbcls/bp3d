#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|,qq|/bp3d/ag-common/lib|;

require "webgl_common.pl";
use AG::ComDB::Twitter;

my $dbh = &get_dbh();

my $Twitter = new AG::ComDB::Twitter;
my $db_dblink = $Twitter->get_dblink();

my %FORM = ();
my %COOKIE = ();
my $cgi = CGI->new;
&getParams($cgi,\%FORM,\%COOKIE);
my($logfile,$cgi_name,$cgi_dir,$cgi_ext) = &getLogFile(\%COOKIE);

=pod
$FORM{ag_data}=qq|obj/bp3d/4.0|;
$FORM{f_id}=qq|root|;
$FORM{model}=qq|bp3d|;
$FORM{node}=qq|root|;
$FORM{tree}=qq|isa|;
$FORM{version}=qq|4.0|;
=cut

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
$logfile .= qq|.$FORM{'cmd'}| if(exists $FORM{'cmd'} && defined $FORM{'cmd'});
open(LOG,"> $logfile");
flock(LOG,2);
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "\$COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG __LINE__,":\$ENV{$key}=[",$ENV{$key},"]\n";
#}

&setDefParams(\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
foreach my $key (sort keys(%FORM)){
	print LOG __LINE__,":\$FORM{$key}=[",$FORM{$key},"]\n";
}

$FORM{'cmd'} = 'read' unless(defined $FORM{'cmd'});

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0,
	'success' => JSON::XS::false
};

if($FORM{'cmd'} eq 'read'){
	eval{
		my @SORT;
		if(defined $FORM{'sort'}){
			my $sort;
			eval{$sort = &JSON::XS::decode_json($FORM{'sort'});};
			push(@SORT,@$sort) if(defined $sort);
		}
		if(scalar @SORT == 0){
			push(@SORT,{
				property  => 'rep_serial',
				direction => 'ASC'
			});
		}
		foreach my $s (@SORT){
			$s->{'property'} = 'rep_serial' if($s->{'property'} eq 'rep_id');
		}

		my %SELECTED;
		if(defined $FORM{'selected'}){
			my $selected;
			eval{$selected = &JSON::XS::decode_json($FORM{'selected'});};
			%SELECTED = map{ $_->{'f_id'} => $_ } @$selected if(defined $selected);
		}



		my $sql=<<SQL;
select * from (
select
 rep.ci_id,
 rep.cb_id,
 rep.md_id,
 rep.mv_id,
 rep.mr_id,
 rep.bul_id,
 rep.rep_id,
 rep_xmin,
 rep_xmax,
 to_number(to_char((rep_xmax+rep_xmin)/2,'FM99990D0000'),'99990D0000S') as rep_xcenter,
 rep_ymin,
 rep_ymax,
 to_number(to_char((rep_ymax+rep_ymin)/2,'FM99990D0000'),'99990D0000S') as rep_ycenter,
 rep_zmin,
 rep_zmax,
 to_number(to_char((rep_zmax+rep_zmin)/2,'FM99990D0000'),'99990D0000S') as rep_zcenter,
 rep_volume,
 EXTRACT(EPOCH FROM rep_entry),
 cdi_name,
 cdi_name_j,
 cdi_name_e,
 cdi_name_k,
 cdi_name_l,
 md.md_abbr,
 mv.mv_name_e,
 bul.bul_abbr,
 rep_primitive,
 to_number(to_char((rep_density_objs/rep_density_ends)*100,'FM99990D0000'),'99990D0000S') as rep_density,

-- tw.tw_id,
-- tw.tw_text,
-- tw.tw_created as tw_date,
-- tw.tw_user_name as tw_user,

 rtw.tw_id,
 rtw.tw_text,
 rtw.tw_created as tw_date,
 rtw.tw_user_name as tw_user,

 rtw.rtw_fixed,
 rtw.rtw_fixed_version,
 EXTRACT(EPOCH FROM rtw.rtw_fixed_date),
 rtw.rtw_fixed_comment,

 rep.mca_id,
 rep.rep_serial -- sort用
from
-- representation_twitter as rtw
--left join (
--  select * from twitter_search
-- ) as tw on tw.tw_id=rtw.tw_id

 dblink('$db_dblink','SELECT rtw.rep_id,rtw.tw_id,rtw.rtw_delcause,rtw.rtw_entry,rtw.rtw_openid,rtw.rtw_fixed,rtw.rtw_fixed_version,rtw.rtw_fixed_date,rtw.rtw_fixed_comment,tw.tw_text,tw.tw_created,tw.tw_user_name FROM representation_twitter as rtw left join (select * from twitter_search) as tw on tw.tw_id=rtw.tw_id') as rtw (
  rep_id            text,
  tw_id             text,
  rtw_delcause      text,
  rtw_entry         timestamp without time zone,
  rtw_openid        text,
  rtw_fixed         boolean,
  rtw_fixed_version text,
  rtw_fixed_date    timestamp without time zone,
  rtw_fixed_comment text,
  tw_text           text,
  tw_created        bigint,
  tw_user_name      text
 )



left join (
  select * from view_representation
 ) as rep on rep.rep_id=rtw.rep_id
left join (
  select * from model
 ) as md on md.md_id=rep.md_id
left join (
  select * from model_version
 ) as mv on mv.md_id=rep.md_id and mv.mv_id=rep.mv_id
left join (
  select * from buildup_logic
 ) as bul on bul.bul_id=rep.bul_id
where
 rep.rep_delcause is null and
 (rep.ci_id,rep.cb_id,rep.cdi_id,rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id) in (
   select
    ci_id,cb_id,cdi_id,md_id,mv_id,max(mr_id) as mr_id,bul_id
   from
    representation
   where
    ci_id=$FORM{ci_id} AND
    cb_id=$FORM{cb_id}
--    AND
--    md_id=$FORM{md_id} AND
--    mv_id=$FORM{mv_id} AND
--    mr_id<=$FORM{mr_id}
--    AND bul_id=$FORM{bul_id}
   group by
    ci_id,cb_id,cdi_id,md_id,mv_id,bul_id
 )
) as a
SQL

		my @bind_values;
		if(exists $FORM{'query'} && defined $FORM{'query'}){
			my $operator = &get_ludia_operator();
			my $query = $FORM{'query'};
			my $space = qq|　|;
			&utf8::decode($query) unless(&utf8::is_utf8($query));
			&utf8::decode($space) unless(&utf8::is_utf8($space));
			$query =~ s/$space/ /g;
			&utf8::encode($query);

			$sql .= qq| where (ARRAY[tw_text,tw_user] $operator ?) OR (ARRAY[rtw_fixed_comment] $operator ?) OR (ARRAY[cdi_name,cdi_name_j,cdi_name_e,cdi_name_k,cdi_name_l] $operator ?) OR rep_id ~* ?|;

			push(@bind_values,qq|*D+ $query|);
			push(@bind_values,qq|*D+ $query|);
			push(@bind_values,qq|*D+ $query|);
			push(@bind_values,$query);
		}

		if(scalar @SORT > 0){
			my @orderby;
			foreach (@SORT){
				push(@orderby,qq|$_->{property} $_->{direction}|);
			}
			$sql .= qq| order by | . join(",",@orderby) if(scalar @orderby > 0);
		}

		print LOG __LINE__,":\$sql=[$sql]\n";

		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}
		$DATAS->{'total'} = $sth->rows();
		$sth->finish;
		undef $sth;

		$sql .= qq| limit $FORM{limit}| if(defined $FORM{limit});
		$sql .= qq| offset $FORM{start}| if(defined $FORM{start});
		my $sth = $dbh->prepare($sql) or die $dbh->errstr;
		if(scalar @bind_values > 0){
			$sth->execute(@bind_values) or die $dbh->errstr;
		}else{
			$sth->execute() or die $dbh->errstr;
		}

		my $ci_id;
		my $cb_id;
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $bul_id;

		my $rep_id;
		my $rep_xmin;
		my $rep_xmax;
		my $rep_xcenter;
		my $rep_ymin;
		my $rep_ymax;
		my $rep_ycenter;
		my $rep_zmin;
		my $rep_zmax;
		my $rep_zcenter;
		my $rep_volume;
		my $rep_entry;
		my $cdi_name;
		my $cdi_name_j;
		my $cdi_name_e;
		my $cdi_name_k;
		my $cdi_name_l;
		my $md_abbr;
		my $mv_name_e;
		my $bul_abbr;
		my $mca_id;

		my $rep_primitive;
		my $rep_density;

		my $tw_id;
		my $tw_text;
		my $tw_created;
		my $tw_user_name;

		my $rtw_fixed;
		my $rtw_fixed_version;
		my $rtw_fixed_date;
		my $rtw_fixed_comment;

		my $column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id,   undef);
		$sth->bind_col(++$column_number, \$cb_id,   undef);
		$sth->bind_col(++$column_number, \$md_id,   undef);
		$sth->bind_col(++$column_number, \$mv_id,   undef);
		$sth->bind_col(++$column_number, \$mr_id,   undef);
		$sth->bind_col(++$column_number, \$bul_id,   undef);

		$sth->bind_col(++$column_number, \$rep_id,   undef);
		$sth->bind_col(++$column_number, \$rep_xmin,   undef);
		$sth->bind_col(++$column_number, \$rep_xmax,   undef);
		$sth->bind_col(++$column_number, \$rep_xcenter,   undef);

		$sth->bind_col(++$column_number, \$rep_ymin,   undef);
		$sth->bind_col(++$column_number, \$rep_ymax,   undef);
		$sth->bind_col(++$column_number, \$rep_ycenter,   undef);

		$sth->bind_col(++$column_number, \$rep_zmin,      undef);
		$sth->bind_col(++$column_number, \$rep_zmax,      undef);
		$sth->bind_col(++$column_number, \$rep_zcenter,   undef);

		$sth->bind_col(++$column_number, \$rep_volume,    undef);
		$sth->bind_col(++$column_number, \$rep_entry,     undef);
		$sth->bind_col(++$column_number, \$cdi_name,      undef);
		$sth->bind_col(++$column_number, \$cdi_name_j,    undef);
		$sth->bind_col(++$column_number, \$cdi_name_e,    undef);
		$sth->bind_col(++$column_number, \$cdi_name_k,    undef);
		$sth->bind_col(++$column_number, \$cdi_name_l,    undef);
		$sth->bind_col(++$column_number, \$md_abbr,       undef);
		$sth->bind_col(++$column_number, \$mv_name_e,     undef);
		$sth->bind_col(++$column_number, \$bul_abbr,      undef);

		$sth->bind_col(++$column_number, \$rep_primitive, undef);
		$sth->bind_col(++$column_number, \$rep_density,   undef);

		$sth->bind_col(++$column_number, \$tw_id,   undef);
		$sth->bind_col(++$column_number, \$tw_text,   undef);
		$sth->bind_col(++$column_number, \$tw_created,   undef);
		$sth->bind_col(++$column_number, \$tw_user_name,   undef);

		$sth->bind_col(++$column_number, \$rtw_fixed,   undef);
		$sth->bind_col(++$column_number, \$rtw_fixed_version,   undef);
		$sth->bind_col(++$column_number, \$rtw_fixed_date,   undef);
		$sth->bind_col(++$column_number, \$rtw_fixed_comment,   undef);

		$sth->bind_col(++$column_number, \$mca_id,   undef);

		while($sth->fetch){

			my $iconCls;
			if(defined $rep_primitive){
				if($rep_primitive==1){
					$iconCls = qq|timgfolder_primitive|;
				}else{
					if($rep_density<=5){
						$iconCls = qq|timgfolder_005|;
					}elsif($rep_density<=15){
						$iconCls = qq|timgfolder_015|;
					}elsif($rep_density<=25){
						$iconCls = qq|timgfolder_025|;
					}elsif($rep_density<=35){
						$iconCls = qq|timgfolder_035|;
					}elsif($rep_density<=45){
						$iconCls = qq|timgfolder_045|;
					}elsif($rep_density<=50){
						$iconCls = qq|timgfolder_050|;
					}elsif($rep_density<=55){
						$iconCls = qq|timgfolder_055|;
					}elsif($rep_density<=65){
						$iconCls = qq|timgfolder_065|;
					}elsif($rep_density<=75){
						$iconCls = qq|timgfolder_075|;
					}elsif($rep_density<=85){
						$iconCls = qq|timgfolder_085|;
					}elsif($rep_density<=95){
						$iconCls = qq|timgfolder_095|;
					}elsif($rep_density<=99){
						$iconCls = qq|timgfolder_099|;
					}else{
						$iconCls = qq|timgfolder_100|;
					}
				}
			}

			my $HASH = {
				ci_id      => $ci_id,
				cb_id      => $cb_id,
				md_id      => $md_id,
				mv_id      => $mv_id,
				mr_id      => $mr_id,
				bul_id      => $bul_id,

				rep_id      => $rep_id,
	#			rep_xmin    => $rep_xmin,
	#			rep_xmax    => $rep_xmax,
	#			rep_xcenter => $rep_xcenter,
	#			rep_ymin    => $rep_ymin,
	#			rep_ymax    => $rep_ymax,
	#			rep_ycenter => $rep_ycenter,
	#			rep_zmin    => $rep_zmin,
	#			rep_zmax    => $rep_zmax,
	#			rep_zcenter => $rep_zcenter,
	#			rep_volume  => $rep_volume,
	#			rep_entry   => $rep_entry,
				cdi_name    => $cdi_name,
				cdi_name_j  => $cdi_name_j,
				cdi_name_e  => $cdi_name_e,
				cdi_name_k  => $cdi_name_k,
				cdi_name_l  => $cdi_name_l,
				md_abbr     => $md_abbr,
				mv_name_e   => $mv_name_e,
				bul_abbr    => $bul_abbr,
				mca_id    => $mca_id,

	#			rep_primitive       => $rep_primitive ? JSON::XS::true : JSON::XS::false,
	#			rep_density         => $rep_density,
	#			rep_density_iconCls => $iconCls,

				tw_id => $tw_id,
				tw_text => $tw_text,
				tw_date => $tw_created,
				tw_user => $tw_user_name,

				rtw_fixed => $rtw_fixed ? JSON::XS::true : JSON::XS::false,
				rtw_fixed_version => $rtw_fixed_version,
				rtw_fixed_date => $rtw_fixed_date,
				rtw_fixed_comment => $rtw_fixed_comment,
			};

			if(defined $SELECTED{$cdi_name}){
				foreach my $key (qw(color opacity remove selected)){
					next unless(defined $SELECTED{$cdi_name}->{$key});
					$HASH->{$key} = $SELECTED{$cdi_name}->{$key};
				}
			}

=pod
			if(defined $rep_id){
				my $sql_art =<<SQL;
	select distinct
	 art_id,
	 artg_id
	from
	 history_art_file
	where
	 (art_id,hist_serial) in (
	  select art_id,art_hist_serial from representation_art where rep_id=?
	 )
	SQL
				my $sth_art = $dbh->prepare($sql_art) or die $dbh->errstr;
				$sth_art->execute($rep_id) or die $dbh->errstr;
				my $art_id;
				my $artg_id;
				my $column_number = 0;
				$sth_art->bind_col(++$column_number, \$art_id,   undef);
				$sth_art->bind_col(++$column_number, \$artg_id,   undef);
				while($sth_art->fetch){
					next unless(defined $art_id && defined $artg_id);
					push(@{$HASH->{'artg_ids'}->{$artg_id}},$art_id);
					$HASH->{'art_ids'}->{$art_id} = $artg_id;
				}
				$sth_art->finish;
				undef $sth_art;
			}
=cut

			push(@{$DATAS->{'datas'}},$HASH);
		}
		$sth->finish;
		undef $sth;

		$DATAS->{'success'} = JSON::XS::true;
	};
	if($@){
		$DATAS->{'msg'} = $@;
	}
}elsif($FORM{'cmd'} eq 'update'){

	$dbh = $Twitter->get_dbh();

	$dbh->{AutoCommit} = 0;
	$dbh->{RaiseError} = 1;
	eval{
		my $datas  = &JSON::XS::decode_json($FORM{'datas'});
		if(defined $datas && ref $datas eq 'ARRAY'){
			foreach my $data (@$datas){
				my $rep_id            = $data->{'rep_id'};
				my $tw_id             = $data->{'tw_id'};
				my $rtw_fixed         = $data->{'rtw_fixed'};
				my $rtw_fixed_version = $data->{'rtw_fixed_version'};
				my $rtw_fixed_comment = $data->{'rtw_fixed_comment'};
				my $rtw_fixed_date;
				my $rtw_fixed_epoc;
				if(defined $data->{'rtw_fixed_epoc'}){
					$rtw_fixed_epoc = $data->{'rtw_fixed_epoc'} / 1000;
					my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($rtw_fixed_epoc);
					$rtw_fixed_date = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
				}

				my $sql_fmt = qq|update representation_twitter set rtw_fixed=?,rtw_fixed_version=?,rtw_fixed_comment=?,rtw_fixed_date=? where rep_id=? and tw_id=? and (%s)|;
				my @B = ($rtw_fixed,$rtw_fixed_version,$rtw_fixed_comment,$rtw_fixed_date,$rep_id,$tw_id);
				my @W;
				if(defined $rtw_fixed){
					if($rtw_fixed){
						push(@W,qq|rtw_fixed<>true|);
					}else{
						push(@W,qq|rtw_fixed<>false|);
					}
				}else{
					push(@W,qq|rtw_fixed is not null|);
				}
				if(defined $rtw_fixed_version){
					push(@W,qq|rtw_fixed_version<>?|);
					push(@W,qq|rtw_fixed_version is null|);
					push(@B,$rtw_fixed_version);
				}else{
					push(@W,qq|rtw_fixed_version is not null|);
				}
				if(defined $rtw_fixed_comment){
					push(@W,qq|rtw_fixed_comment<>?|);
					push(@W,qq|rtw_fixed_comment is null|);
					push(@B,$rtw_fixed_comment);
				}else{
					push(@W,qq|rtw_fixed_comment is not null|);
				}
				if(defined $rtw_fixed_date){
					push(@W,qq|EXTRACT(EPOCH FROM rtw_fixed_date)<>?|);
					push(@W,qq|rtw_fixed_date is null|);
					push(@B,$rtw_fixed_epoc);
				}else{
					push(@W,qq|rtw_fixed_date is not null|);
				}

				print LOG __LINE__,":\$sql=[",sprintf($sql_fmt,join(" or ",@W)),"]\n";
				print LOG __LINE__,":\@B=[",join(",",@B),"]\n";

				my $sth = $dbh->prepare(sprintf($sql_fmt,join(" or ",@W))) or die $dbh->errstr;

				$sth->execute(@B) or die $dbh->errstr;
				$DATAS->{'total'} = $sth->rows();
				$sth->finish;
				undef $sth;
			}
#			$dbh->rollback();
			$dbh->commit();
			$DATAS->{'success'} = JSON::XS::true;
		}
	};
	if($@){
		$dbh->rollback();
		$DATAS->{'msg'} = $@;
	}
	$dbh->{AutoCommit} = 1;
	$dbh->{RaiseError} = 0;

	print LOG __LINE__,":",&JSON::XS::encode_json($DATAS),"\n";
}

#print &JSON::XS::encode_json($DATAS);
&gzip_json($DATAS);

close(LOG);
