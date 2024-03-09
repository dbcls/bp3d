package AG::API::Data;

use strict;
use warnings;
use feature ':5.10';

#no warnings 'redefine';
use base qw/AG::API::JSONParser/;

use File::Basename;
use JSON::XS;
use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;

use AG::API::Log;
use cgi_lib::common;

#use AG::DB;
#use AG::DB::ArtFile;
#use AgJSONParser;
use AG::Representation;


use constant {
	DEBUG => (exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'}) ? 0 : 1
};

use Data::Dumper;
if(DEBUG){
	$Data::Dumper::Indent = 1;
	$Data::Dumper::Sortkeys = 1;
}

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};

	my $ag_log = new AG::API::Log($json) if(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'});

	my $content;
	my $Status;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

	my $OUT;
	unless(DEBUG){
		$OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));
		open $OUT,">./tmp_image/$name.txt" unless(defined $OUT);
	}else{
		$OUT = \*STDERR;
	}

say $OUT __PACKAGE__.':'.__LINE__.':$name=['.$name.']';
say $OUT __PACKAGE__.':'.__LINE__.':$dir=['.$dir.']';
say $OUT __PACKAGE__.':'.__LINE__.':$ext=['.$ext.']';

	my $format = 'json';
	$format = 'json' if($name =~ /\.json$/);
	if($format eq 'json'){
		$content = '[]';
	}else{
		$content = '';
	}

#	my $parser = new AgJSONParser($json) if(defined $json && length $json);
	if(defined $parser){
		print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($parser);
		say $OUT __PACKAGE__.':'.__LINE__.':'.($parser->{db}->can('get_artfile_obj_format_data') ? 1 : 0);
		say $OUT __PACKAGE__.':'.__LINE__.':'.($parser->{db}->can('get_dbh') ? 1 : 0);
		say $OUT __PACKAGE__.':'.__LINE__.":[$json]";
		say $OUT __PACKAGE__.':'.__LINE__.":[$parser->{json}]";

		my $copyright_file = &Cwd::abs_path(&catfile($FindBin::Bin,'..','download',qq|copyright.txt|));
		say $OUT __PACKAGE__.':'.__LINE__.':$copyright_file=['.$copyright_file.']' if(DEBUG);
		my $copyright;
		if(-e $copyright_file && -f $copyright_file && -s $copyright_file && -r $copyright_file){
			if(open(my $IN,$copyright_file)){
				my $old = $/;
				$/ = undef;
				$copyright = <$IN>;
				$/ = $old;
				close($IN);
			}
		}

		my $jsonObj = $parser->{jsonObj};
print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper($parser->{jsonObj});
		if(defined $jsonObj){
			eval{
				my $dbh = $parser->{db}->get_dbh();
				my $obj = $parser->{jsonObj};

				my $md_id;
				my $mv_id;
				my $mr_id;
				my $ci_id;
				my $cb_id;
				my $bul_id;

				my $jsonObj = &JSON::XS::decode_json($parser->{json});

				unless(defined $md_id){
					my $sth = $dbh->prepare(qq|select md_id from model where md_delcause is null and md_abbr=? order by md_order desc limit 1|) or die $dbh->errstr;
					$sth->execute($jsonObj->{Common}->{Model}) or die $dbh->errstr;
					$sth->bind_col(1, \$md_id, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;
				}
				say $OUT __PACKAGE__.':'.__LINE__.':$md_id=['.$md_id.']' if(DEBUG);

				unless(defined $mv_id && defined $mr_id){
					my $sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where mr_delcause is null and md_id=? and mr_version=? order by mr_order desc limit 1|) or die $dbh->errstr;
					$sth->execute($md_id,$jsonObj->{Common}->{Version}) or die $dbh->errstr;
					$sth->bind_col(1, \$mv_id, undef);
					$sth->bind_col(2, \$mr_id, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;
				}
				say $OUT __PACKAGE__.':'.__LINE__.':$mv_id=['.$mv_id.']' if(DEBUG);
				say $OUT __PACKAGE__.':'.__LINE__.':$mr_id=['.$mr_id.']' if(DEBUG);
				unless(defined $ci_id && defined $cb_id){
					my $sth = $dbh->prepare(qq|select max(ci_id) from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id=?|) or die $dbh->errstr;
					$sth->execute($md_id,$mv_id,$mr_id) or die $dbh->errstr;
					$sth->bind_col(1, \$ci_id, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;

					$sth = $dbh->prepare(qq|select max(cb_id) from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id=? and ci_id=?|) or die $dbh->errstr;
					$sth->execute($md_id,$mv_id,$mr_id,$ci_id) or die $dbh->errstr;
					$sth->bind_col(1, \$cb_id, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;
				}
				say $OUT __PACKAGE__.':'.__LINE__.':$ci_id=['.$ci_id.']' if(DEBUG);
				say $OUT __PACKAGE__.':'.__LINE__.':$cb_id=['.$cb_id.']' if(DEBUG);

				unless(defined $bul_id){
	#				my $sth = $dbh->prepare(qq|select bul_id from buildup_logic where bul_use and bul_delcause is null and bul_abbr=? order by bul_order desc limit 1|) or die $dbh->errstr;
					my $sth = $dbh->prepare(qq|select bul_id from buildup_logic where bul_delcause is null and bul_abbr=? order by bul_order desc limit 1|) or die $dbh->errstr;
					$sth->execute($jsonObj->{Common}->{TreeName}) or die $dbh->errstr;
					$sth->bind_col(1, \$bul_id, undef);
					$sth->fetch;
					$sth->finish;
					undef $sth;
				}
				say $OUT __PACKAGE__.':'.__LINE__.':$bul_id=['.$bul_id.']' if(DEBUG);

				my %PartID;
				foreach my $Part (@{$obj->{Part}}){
					$PartID{$Part->{PartID}} = undef;
				}
print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%PartID) if(defined $OUT);



				my $sth = $dbh->prepare(qq|
select
 rep.rep_id,
 rep.cdi_name
from
 view_representation as rep
where
 rep.rep_delcause is null and 
 (rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (
  select
   md_id,
   mv_id,
   max(mr_id) as mr_id,
   bul_id,
   cdi_id
  from
   view_representation
  where
   rep_delcause is null and md_id=? and mv_id=? and mr_id<=? and bul_id=? and cdi_name in (|.join(',',map {'?'} keys(%PartID)).qq|)
  group by
   md_id,
   mv_id,
   bul_id,
   cdi_id
 )
|) or die $dbh->errstr;

#				my $sth = $dbh->prepare(qq|select rep_id,cdi_name from view_representation where md_id=? and mv_id=? and mr_id<=? and ci_id=? and cb_id=? and bul_id=? and cdi_name in (|.join(',',map {'?'} keys(%PartID)).')') or die $dbh->errstr;
				my $rep_id;
				my $cdi_name;
				my %REP_IDS;
#				$sth->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$bul_id,keys(%PartID)) or die $dbh->errstr;
				$sth->execute($md_id,$mv_id,$mr_id,$bul_id,keys(%PartID)) or die $dbh->errstr;
				$sth->bind_col(1, \$rep_id, undef);
				$sth->bind_col(2, \$cdi_name, undef);
				while($sth->fetch){
					$REP_IDS{$rep_id} = undef if(defined $rep_id);
					delete $PartID{$cdi_name} if(defined $cdi_name && exists $PartID{$cdi_name});
				}
				$sth->finish;
				undef $sth;
print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%REP_IDS) if(defined $OUT);

				if(scalar keys(%PartID)){
print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%PartID) if(defined $OUT);

					my $sth = $dbh->prepare(qq|
select
 rep.rep_id,
 rep.cdi_name
from
 view_representation as rep
where
 rep.rep_delcause is null and 
 (rep.md_id,rep.mv_id,rep.mr_id,rep.bul_id,rep.cdi_id) in (
  select
   md_id,
   mv_id,
   max(mr_id) as mr_id,
   bul_id,
   cdi_id
  from
   view_representation
  where
   rep_delcause is null and md_id=? and mv_id=? and mr_id<=? and bul_id<>? and cdi_name in (|.join(',',map {'?'} keys(%PartID)).qq|)
  group by
   md_id,
   mv_id,
   bul_id,
   cdi_id
 )
|) or die $dbh->errstr;

#					my $sth = $dbh->prepare(qq|select rep_id,cdi_name from view_representation where md_id=? and mv_id=? and mr_id<=? and ci_id=? and cb_id=? and bul_id<>? and cdi_name in (|.join(',',map {'?'} keys(%PartID)).')') or die $dbh->errstr;
					my $rep_id;
					my $cdi_name;
#					$sth->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$bul_id,keys(%PartID)) or die $dbh->errstr;
					$sth->execute($md_id,$mv_id,$mr_id,$bul_id,keys(%PartID)) or die $dbh->errstr;
					$sth->bind_col(1, \$rep_id, undef);
					$sth->bind_col(2, \$cdi_name, undef);
					while($sth->fetch){
						$REP_IDS{$rep_id} = undef if(defined $rep_id);
						delete $PartID{$cdi_name} if(defined $cdi_name && exists $PartID{$cdi_name});
					}
					$sth->finish;
					undef $sth;
print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%REP_IDS) if(defined $OUT);
				}
print $OUT __PACKAGE__.':'.__LINE__.':'.&Data::Dumper::Dumper(\%PartID) if(defined $OUT);

#				my $artfile_obj_format_data = $parser->{db}->get_artfile_obj_format_data({rep_ids=>[keys %REP_IDS],'__LOG__'=>$OUT},$copyright);
				my $artfile_obj_format_data = &AG::Representation::get_artfile_obj_format_data(
					{
						dbh      => $parser->{db}->get_dbh(),
						rep_ids  => [keys %REP_IDS],
						'__LOG__'=> $OUT
					},
					$copyright
				);
				$content = &cgi_lib::common::encodeJSON($artfile_obj_format_data) if(defined $artfile_obj_format_data);
			};
			if($@){
				say $OUT __PACKAGE__.':'.__LINE__.":[$@]";
			}
		}
	}

	if(exists $ENV{'REQUEST_METHOD'} && defined $ENV{'REQUEST_METHOD'} && $ENV{'REQUEST_METHOD'}){
		if(exists($parser->{jsonObj}->{callback})){
			print "Content-Type:application/javascript\n";
		}else{
			print "Content-Type:text/javascript\n";
		}
	}
	&cgi_lib::common::_printContentJSON($content,$parser->{jsonObj});

#	print $OUT __LINE__,":[$content]\n";
	close $OUT unless(DEBUG);
#	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,$content, undef) if(defined $ag_log);
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef, undef, undef) if(defined $ag_log);
}

1;
