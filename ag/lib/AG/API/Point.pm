package AG::API::Point;

use strict;
use warnings;
use feature ':5.10';

#use AG::API::JSONParser;
use base qw/AG::API::JSONParser/;

use File::Basename;
use JSON::XS;
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
#	my($name,$dir,$ext) = &File::Basename::fileparse($0,@extlist);
	my($name,$dir,$ext) = &File::Basename::fileparse($0,qr/\..*$/);

#	open my $OUT,">./tmp_image/$name.txt";
	my $OUT = &cgi_lib::common::getLogFH(undef,undef,&AG::API::JSONParser::get_log_file_basename(),&AG::API::JSONParser::get_log_dir_basename($name));

	if(defined $json){
#		$parser = new AG::API::JSONParser($json);
		if(defined $parser){
			print $OUT __LINE__,":[$json]\n";
			print $OUT __LINE__,":[$parser->{json}]\n";
			$content = $parser->getMethodContent($name);
			if(defined $content){
				eval{
					my $dbh = $parser->{db}->get_dbh();

					my $obj = &cgi_lib::common::decodeJSON($content);
					my $item = shift(@{$obj->{Pin}});

					my $cdi_name;
					my $cdi_name_e;

					my $PinPartID = $item->{PinPartID};
					if(defined $PinPartID){

						my $md_id;
						my $mv_id;
						my $mr_id;
						my $ci_id;
						my $cb_id;

						my $jsonObj = &cgi_lib::common::decodeJSON($parser->{json});

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

						$PinPartID = $1 if($PinPartID =~ /^clipPlaneRect_(.+)$/);

						my $sth = $dbh->prepare(qq|select cdi_name,cdi_name_e from view_concept_art_map where cm_use and cm_delcause is null and md_id=? and mv_id=? and mr_id<=? and ci_id=? and cb_id=? and art_id=? order by mr_id desc,art_hist_serial desc limit 1|) or die $dbh->errstr;
						$sth->execute($md_id,$mv_id,$mr_id,$ci_id,$cb_id,$PinPartID) or die $dbh->errstr;
						$sth->bind_col(1, \$cdi_name, undef);
						$sth->bind_col(2, \$cdi_name_e, undef);
						$sth->fetch;
						$sth->finish;
						undef $sth;
					}

					my $MARKER = {
						id        => defined $cdi_name ? $cdi_name : $item->{PinPartID},
						name      => defined $cdi_name_e ? $cdi_name_e : $item->{PinPartName},
						worldPosX => $item->{PinX},
						worldPosY => $item->{PinY},
						worldPosZ => $item->{PinZ},
						arrVecX   => $item->{PinArrowVectorX},
						arrVecY   => $item->{PinArrowVectorY},
						arrVecZ   => $item->{PinArrowVectorZ},
						upVecX    => $item->{PinUpVectorX},
						upVecY    => $item->{PinUpVectorY},
						upVecZ    => $item->{PinUpVectorZ},
						coordId   => $item->{PinCoordinateSystemName}
					};
	#				$content = &JSON::XS::encode_json($MARKER);
					$content = &cgi_lib::common::encodeJSON($MARKER);
				};
			}else{
				$content = $parser->getContent();
			}
			$Status = $parser->getContentStatus();
			$Code = $parser->getContentCode();
			$ContentType = $parser->getContentType();
		}
	}

	print "Status:$Status\n" if(defined $Status);
	#print "Content-Type:$ContentType\n\n";
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
