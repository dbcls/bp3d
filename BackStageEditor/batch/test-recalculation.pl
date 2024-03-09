#!/bp3d/local/perl/bin/perl

use constant {
	DEBUG => 1,
};

select(STDERR);
$| = 1;
select(STDOUT);
$| = 1;

use strict;
use JSON::XS;
use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::DensityCalc;

require "webgl_common.pl";

my $dbh = &get_dbh();

#exit 1 unless(defined $ARGV[0] && -e $ARGV[0]);

my $FORM;
{
	$FORM = {
		all_datas => [{
			ci_id => 1,
			cb_id => 5,
			bul_id=> 4,
			md_id => 1,
			mv_id => 6,
			mr_id => 1,
			cdi_id=> 71888,
			rep_id=>'BP22463'
		},{
			ci_id => 1,
			cb_id => 5,
			bul_id=> 4,
			md_id => 1,
			mv_id => 6,
			mr_id => 1,
			cdi_id=> 12145,
			rep_id=>'BP22394'
		}]
	};

	$FORM->{'all_datas'} = [];
	my $sql = qq|select rep.ci_id,rep.cb_id,rep.bul_id,rep.md_id,rep.mv_id,rep.mr_id,rep.cdi_id,rep.rep_id,but.but_depth from representation as rep left join (select * from buildup_tree) as but on but.ci_id=rep.ci_id and but.cb_id=rep.cb_id and but.bul_id=rep.bul_id and but.cdi_id=rep.cdi_id where rep.rep_delcause is null AND rep.rep_primitive and rep.rep_density_ends>1 order by rep.ci_id,rep.cb_id,rep.bul_id,rep.md_id,rep.mv_id,rep.mr_id,but.but_depth desc|;
	my $sth = $dbh->prepare($sql) or die $dbh->errstr;
	my $col_num = 0;
	my $ci_id;
	my $cb_id;
	my $bul_id;
	my $md_id;
	my $mv_id;
	my $mr_id;
	my $cdi_id;
	my $rep_id;
	$sth->execute() or die $dbh->errstr;
	$sth->bind_col(++$col_num, \$ci_id, undef);
	$sth->bind_col(++$col_num, \$cb_id, undef);
	$sth->bind_col(++$col_num, \$bul_id, undef);
	$sth->bind_col(++$col_num, \$md_id, undef);
	$sth->bind_col(++$col_num, \$mv_id, undef);
	$sth->bind_col(++$col_num, \$mr_id, undef);
	$sth->bind_col(++$col_num, \$cdi_id, undef);
	$sth->bind_col(++$col_num, \$rep_id, undef);
	while($sth->fetch){
		push(@{$FORM->{'all_datas'}},{
			ci_id => $ci_id,
			cb_id => $cb_id,
			bul_id=> $bul_id,
			md_id => $md_id,
			mv_id => $mv_id,
			mr_id => $mr_id,
			cdi_id=> $cdi_id,
			rep_id=> $rep_id
		});
	}
	$sth->finish;
	undef $sth;
}
exit 1 unless(defined $FORM);

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	&callback("Error:[$date] KILL THIS SCRIPT!!");
	exit(1);
}

my $work_path;
if(DEBUG){
#	my @extlist = qw|.json|;
#	my($name,$dir,$ext) = &File::Basename::fileparse($ARGV[0],@extlist);
#	$work_path = File::Spec->catfile($dir,qq|$name.txt|);
}
&recalc($FORM);

sub callback {
	my $msg = shift;
	my $val = shift;
	my $recalc_data = shift;

	$val = 0 unless(defined $val);

	if(DEBUG){
		&utf8::encode($msg) if(&utf8::is_utf8($msg));
		print __PACKAGE__.":".__LINE__.":\$msg=[$msg]\n";
	}

	&utf8::decode($msg) unless(&utf8::is_utf8($msg));
	$FORM->{'msg'} = $msg;
	$FORM->{'value'} = $val;
	$FORM->{'recalc_data'} = $recalc_data;
	push(@{$FORM->{'recalc_datas'}},$recalc_data) if(defined $recalc_data);

#	open(OUT,"> $ARGV[0]") or die $!;
#	flock(OUT,2);
#	print OUT &JSON::XS::encode_json($FORM);
#	close(OUT);
}

sub recalc {
	my $FORM = shift;
	&callback('Start',0.1);
	my $all_datas;
#	$all_datas = &JSON::XS::decode_json($FORM->{'all_datas'}) if(defined $FORM->{'all_datas'});
	$all_datas = $FORM->{'all_datas'} if(defined $FORM->{'all_datas'});

print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);

	if(defined $all_datas && ref $all_datas eq 'ARRAY'){

print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);

		$dbh->{AutoCommit} = 0;
		$dbh->{RaiseError} = 1;
		eval{
			my $IDS;
			if(DEBUG && defined $work_path && -e $work_path && -s $work_path){
				open(IN,"< $work_path") or die $!;
				flock(IN,1);
				my @DATAS = <IN>;
				close(IN);
				$IDS = &JSON::XS::decode_json(join('',@DATAS));
				undef @DATAS;
			}
			my $rows = scalar @$all_datas;
			my $row = 0;
			my $sth_cdi = $dbh->prepare(qq|select cdi_name from concept_data_info where ci_id=? and cdi_id=? and cdi_delcause is null|) or die $dbh->errstr;
			my $col_num;
			my $cdi_name;
			foreach my $data (@$all_datas){
				$row++;
				$col_num = 0;
				$sth_cdi->execute($data->{'ci_id'},$data->{'cdi_id'}) or die $dbh->errstr;
				$sth_cdi->bind_col(++$col_num, \$cdi_name, undef);
				$sth_cdi->fetch;
				$sth_cdi->finish;
				next unless(defined $cdi_name);
				&callback('ReCalc: ['.$cdi_name.']',$row/($rows+1),$data);


#				sleep(2);
#				next;


				if(defined $data->{'rep_id'}){
print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);
					my $rtn_rows = &BITS::DensityCalc::clear_representation_density(dbh=>$dbh,ci_id=>$data->{'ci_id'},cb_id=>$data->{'cb_id'},bul_id=>$data->{'bul_id'},md_id=>$data->{'md_id'},mv_id=>$data->{'mv_id'},mr_id=>$data->{'mr_id'},cdi_id=>$data->{'cdi_id'},forcing=>1);
print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);
					print __PACKAGE__.":".__LINE__.":\$rtn_rows=[$rtn_rows]\n" if(DEBUG);
				}
				unless(defined $data->{'rep_id'}){
					$data->{'rep_id'} = &BITS::DensityCalc::ins_representation(dbh=>$dbh,ci_id=>$data->{'ci_id'},cb_id=>$data->{'cb_id'},bul_id=>$data->{'bul_id'},md_id=>$data->{'md_id'},mv_id=>$data->{'mv_id'},mr_id=>$data->{'mr_id'},cdi_id=>$data->{'cdi_id'});
				}
				if(defined $data->{'rep_id'}){
print __PACKAGE__.":".__LINE__.":".$data->{'rep_id'}."\n" if(DEBUG);
					my($cdi_ids,$route_ids,$use_ids);
					my @k = ($data->{'ci_id'},$data->{'cb_id'},$data->{'bul_id'},$data->{'md_id'},$data->{'mv_id'},$data->{'mr_id'});
					my $key = join("\t",@k);
					unless(defined $IDS->{$key}){
print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);
						($cdi_ids,$route_ids,$use_ids) = &BITS::DensityCalc::get_rep_parent_id(dbh=>$dbh,ci_id=>$data->{'ci_id'},cb_id=>$data->{'cb_id'},bul_id=>$data->{'bul_id'},md_id=>$data->{'md_id'},mv_id=>$data->{'mv_id'},mr_id=>$data->{'mr_id'});
						$IDS->{$key}->{'cdi_ids'} = $cdi_ids;
						$IDS->{$key}->{'route_ids'} = $route_ids;
						$IDS->{$key}->{'use_ids'} = $use_ids;

						if(DEBUG && defined $work_path){
							open(OUT,"> $work_path") or die $!;
							flock(OUT,2);
							print OUT &JSON::XS::encode_json($IDS);
							close(OUT);
							chmod 0666,$work_path;
						}

					}else{
print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);
						$cdi_ids = $IDS->{$key}->{'cdi_ids'};
						$route_ids = $IDS->{$key}->{'route_ids'};
						$use_ids = $IDS->{$key}->{'use_ids'};
					}
print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);
					&BITS::DensityCalc::update_representation_density(dbh=>$dbh,ci_id=>$data->{'ci_id'},cb_id=>$data->{'cb_id'},bul_id=>$data->{'bul_id'},md_id=>$data->{'md_id'},mv_id=>$data->{'mv_id'},mr_id=>$data->{'mr_id'},cdi_id=>$data->{'cdi_id'},rep_id=>$data->{'rep_id'},cdi_ids=>$cdi_ids);
				}

			}
			undef $sth_cdi;

#			if(DEBUG){
#				$dbh->rollback();
#			}else{
				$dbh->commit();
#			}
print __PACKAGE__.":".__LINE__.":\n" if(DEBUG);
		};
		if($@){
			$dbh->rollback();
			&callback('Error:'.$@,1);
print __PACKAGE__.":".__LINE__.":".$@."\n" if(DEBUG);
		}
		$dbh->{AutoCommit} = 1;
		$dbh->{RaiseError} = 0;
	}
	&callback('End',1);
}
