package AG::API::Pick;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;
use File::Basename;
#use common;
#use common_db;
use AG::API::Log;
use cgi_lib::common;

sub parse {
	my $parser = shift;
#	my $json = shift;
	my $func = shift;
	my $json = $parser->{json};

	my $ag_log = new AG::API::Log($json);

	my $content;
	my $ContentType = qq|application/json|;
	my $Status;
	my $Code = '503';
#	my $parser;
#	my @extlist = qw|.cgi|;
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	open OUT,">./tmp_image/$name.txt";
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

	if(defined $json){
#		$parser = new AgJSONParser($json);
		if(defined $parser){
			print $OUT __LINE__,":[$json]\n";
			print $OUT __LINE__,":[$parser->{json}]\n";
			$content = $parser->getMethodContent($name);
			$content = $parser->getContent() unless(defined $content);
			if(defined $content){
				print $OUT __LINE__,":[$content]\n";
				eval{
	#				my $dbh = &common_db::get_dbh();
					my $dbh = $parser->{db}->get_dbh();

					my $md_id;
					my $mv_id;
					my $mr_id;
					my $ci_id;
					my $cb_id;

					my $jsonObj = &JSON::XS::decode_json($parser->{json});

					unless(defined $md_id){
		#				my $sth = $dbh->prepare(qq|select md_id from model where md_use and md_delcause is null and md_abbr=? order by md_order desc limit 1|) or die $dbh->errstr;
						my $sth = $dbh->prepare(qq|select md_id from model where md_delcause is null and md_abbr=? order by md_order desc limit 1|) or die $dbh->errstr;
						$sth->execute($jsonObj->{Common}->{Model}) or die $dbh->errstr;
						$sth->bind_col(1, \$md_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}
					unless(defined $mv_id && defined $mr_id){
		#				my $sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where mr_use and mr_delcause is null and md_id=? and mr_version=? order by mr_order desc limit 1|) or die $dbh->errstr;
						my $sth = $dbh->prepare(qq|select mv_id,mr_id from model_revision where mr_delcause is null and md_id=? and mr_version=? order by mr_order desc limit 1|) or die $dbh->errstr;
						$sth->execute($md_id,$jsonObj->{Common}->{Version}) or die $dbh->errstr;
						$sth->bind_col(1, \$mv_id, undef);
						$sth->bind_col(2, \$mr_id, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}
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

					my $sth = $dbh->prepare(qq|select cdi_name,cdi_name_e from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id<=? and ci_id=? and cb_id=? and art_id=? order by mr_id desc,art_hist_serial desc limit 1|) or die $dbh->errstr;

					my $obj = &JSON::XS::decode_json($content);
					foreach my $pin (@{$obj->{Pin}}){

						my $PinPartID = $pin->{PinPartID};
						$PinPartID = $1 if($PinPartID =~ /^clipPlaneRect_(.+)$/);

						my $cdi_name;
						my $cdi_name_e;
						$sth->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$PinPartID) or die $dbh->errstr;
						$sth->bind_col(1, \$cdi_name, undef);
						$sth->bind_col(2, \$cdi_name_e, undef);
						$sth->fetch;
						$sth->finish;

						$pin->{PinPartID} = $cdi_name if(defined $cdi_name);
						$pin->{PinPartName} = $cdi_name_e if(defined $cdi_name_e);
					}
					$content = &JSON::XS::encode_json($obj);
					undef $sth;
				};
			}
			$Status = $parser->getContentStatus();
			$Code = $parser->getContentCode();
			$ContentType = $parser->getContentType();
		}
	}

	print "Status:$Status\n" if(defined $Status);
#	print "Content-Type:$ContentType\n\n";
	#binmode(STDOUT);
	#print $content;


#	if(exists($parser->{jsonObj}->{callback})){
#		print $parser->{jsonObj}->{callback},"(",$content,")";
#	}else{
#		print $content;
#	}
	if($Code eq '200'){
		if(defined $parser && exists $parser->{jsonObj}->{callback}){
			say qq|Content-Type:application/javascript|;
		}else{
			say qq|Content-Type:$ContentType|;
		}
		&cgi_lib::common::_printContentJSON($content,defined $parser ? $parser->{'jsonObj'} : undef);
	}else{
		&cgi_lib::common::printContent($content,$ContentType);
	}

	print $OUT __LINE__,":[$content]\n" if(defined $content);
	close $OUT;
	$ag_log->print(defined $parser ? $parser->{'jsonObj'} : undef,$content,defined $parser ? $parser->getBalancerInformation() : undef);
}

1;
