#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;
use JSON::XS;
#use SetEnv;
#use AgPRM;
#use LWP::UserAgent;
#use HTTP::Request::Common;
use Image::Info qw(image_info dim);
use Image::Magick;
use GD;
use DBI;
use DBD::Pg;

use File::Spec::Functions qw(catdir catfile);
use Cwd;
use FindBin;
use lib $FindBin::Bin,&catdir($FindBin::Bin,'API'),&Cwd::abs_path(&catdir($FindBin::Bin,'..','lib')),&Cwd::abs_path(&catdir($FindBin::Bin,'..','..','ag-common','lib'));
use cgi_lib::common;
use AG::login;

require "common.pl";
require "common_db.pl";

my $dbh = &get_dbh();

my %FORM = ();
&decodeForm(\%FORM);
delete $FORM{_formdata} if(exists($FORM{_formdata}));

my %COOKIE = ();
&getCookie(\%COOKIE);

#$FORM{lng} = $COOKIE{"ag_annotation.locale"} if(!exists($FORM{lng}) && exists($COOKIE{"ag_annotation.locale"})); #とりあえず
#$FORM{lng} = "ja" if(!exists($FORM{lng}));

my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $file = sprintf("%04d%02d%02d%02d%02d%02d_%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$$);
my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
open(LOG,">> log.txt");
print LOG "\n[$logtime]:$0\n";
foreach my $key (sort keys(%FORM)){
	print LOG "FORM{$key}=[",$FORM{$key},"]\n";
}
#foreach my $key (sort keys(%COOKIE)){
#	print LOG "COOKIE{$key}=[",$COOKIE{$key},"]\n";
#}
#foreach my $key (sort keys(%ENV)){
#	print LOG "ENV{$key}=[",$ENV{$key},"]\n";
#}





print qq|Content-type: application/json; charset=UTF-8\n\n|;

my $parentURL = $FORM{parent} if(exists($FORM{parent}));
my $lsdb_OpenID;
my $lsdb_Auth;
my $lsdb_Config;
my $lsdb_Identity;
if(defined $parentURL){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config) = &openidAuth($parentURL);
}elsif(exists($COOKIE{openid_url}) && exists($COOKIE{openid_session})){
	($lsdb_OpenID,$lsdb_Auth,$lsdb_Config,$lsdb_Identity) = &AG::login::openidAuthSession($COOKIE{openid_url},$COOKIE{openid_session});
}
$lsdb_Auth = int($lsdb_Auth) if(defined $lsdb_Auth);

$FORM{type} = "sample" unless(exists($FORM{type}));

my $base_dir;
my $ins_sql;
if($FORM{type} eq "sample"){
	unless(defined $lsdb_Auth){
		print qq|{success:false,msg:"There is no administrative privileges."}|;
		print LOG __LINE__,qq|:{success:false,msg:"There is no administrative privileges."}\n|;
		close(LOG);
		exit;
	}
	$base_dir = "samples";
	$ins_sql = qq|insert into sample (sp_id,sp_info,sp_image,sp_openid,sp_entry) values (?,?,?,?,'now()')|;
}elsif($FORM{type} eq "user"){
	unless(defined $lsdb_OpenID){
		print qq|{success:false,msg:"Please login with OpenID."}|;
		print LOG __LINE__,qq|:{success:false,msg:"Please login with OpenID."}\n|;
		close(LOG);
		exit;
	}
	$base_dir = "users";
	$ins_sql = qq|insert into save (sv_id,sv_info,sv_image,sv_openid,sv_entry) values (?,?,?,?,'now()')|;
}elsif(exists($FORM{type})){
	print qq|{success:false,msg:"Unknown Type!!"}|;
	print LOG __LINE__,qq|:{success:false,msg:"Unknown Type!!"}\n|;
	close(LOG);
	exit;
}

unless(exists($FORM{param})){
	print qq|{success:false,msg:"There is not Category information"}|;
	print LOG __LINE__,qq|:{success:false,msg:"There is not Category information"}\n|;
	close(LOG);
	exit;
}


my $param_info = decode_json($FORM{param});

my $RTN = {
	"success" => JSON::XS::false,
};

$dbh->{AutoCommit} = 0;
$dbh->{RaiseError} = 1;

eval{

	my $image_file;
	my $sp_image;
	my $text_file = qq|$base_dir/$file.txt|;
	open(OUT,"> $text_file");
	foreach my $key (sort keys(%FORM)){
		print OUT "$key\t",$FORM{$key},"\n";
	}

	if(defined $param_info && exists($param_info->{anatomoprm})){
		my @CMDs = ();
#		foreach my $key (keys %{$param_info->{anatomoprm}}){
#			push(@CMDs,qq|$key=|.$param_info->{anatomoprm}->{$key});
#		}
#		my $agprm = AgPRM->new(\@CMDs);
#		$agprm->parseURL();
#		$agprm->mapComment();
#		my $imgurl = $agprm->{AgSOAP}->sendGetImageWithMarker();
#		my $ua = LWP::UserAgent->new;
#		my $req = HTTP::Request->new(GET => $imgurl);
#		my $res = $ua->request($req);
#		my $c_image = $res->content;

		my $c_image;
		foreach my $key (keys %{$param_info->{anatomoprm}}){
			push(@CMDs,qq|$key=|.&url_encode($param_info->{anatomoprm}->{$key}));
		}
		my $json = join("&",@CMDs);

		use AgJSONParser;
		my $parser = new AgJSONParser($json);
		if(defined $parser){
			$parser->{jsonObj}->{Window} = {} unless(defined $parser->{jsonObj}->{Window});
			$parser->{jsonObj}->{Window}->{ImageWidth} = 500 unless(defined $parser->{jsonObj}->{Window}->{ImageWidth});
			$parser->{jsonObj}->{Window}->{ImageHeight} = 500 unless(defined $parser->{jsonObj}->{Window}->{ImageHeight});
			if($parser->{jsonObj}->{Window}->{ImageWidth}>$parser->{jsonObj}->{Window}->{ImageHeight}){
				$parser->{jsonObj}->{Window}->{ImageWidth} = $parser->{jsonObj}->{Window}->{ImageHeight};
			}else{
				$parser->{jsonObj}->{Window}->{ImageHeight} = $parser->{jsonObj}->{Window}->{ImageWidth};
			}
			$parser->{json} = encode_json($parser->{jsonObj});
			$c_image = $parser->getMethodPicture('image');
		}
		undef $parser;
		undef $json;

		my $image_info = image_info(\$c_image) if(defined $c_image);
		if(defined $image_info){
			$image_file = qq|$base_dir/$file.$image_info->{file_ext}|;
#			open IMGOUT, ">".$image_file;
#			binmode(IMGOUT);
#			print IMGOUT $c_image;
#			close IMGOUT;

#			for(my $i=0;$i<@{$agprm->{AgComments}};$i++){
#				my $agCom = $agprm->{AgComments}[$i];
#				my $color = $image->colorAllocate($agCom->{r}, $agCom->{g}, $agCom->{b});
#				$image->filledArc($agCom->{x2d}, $agCom->{y2d}, 10, 10, 0, 360, $color) if($agCom->{shape} eq "SC");
#				$image->string(gdMediumBoldFont, $agCom->{x2d} + 5, $agCom->{y2d} + 5, $agCom->{no}, $color);
#			}

#			my $env = SetEnv->new;
#			# Draw Characters
#			my $drawX = 10;
#			my $drawY = 10;
#			my $fontSize = 9;
#			# Draw Legend
#			my $legend = $agprm->{AgLegend};
#			if($legend->{position} eq "UL"){
#				$drawX = 10;
#				$drawY = 10;
#				my $color = $image->colorAllocate(hex($legend->{r}), hex($legend->{g}), hex($legend->{b}));
#				my @bounds = $image->stringFT($color, $env->{fontPath}, $fontSize, 0, $drawX, $drawY, url_decode($legend->{title})."\n".url_decode($legend->{legend})."\n".url_decode($legend->{author}));
#				$drawY = $bounds[1] + $fontSize + 1;
#			}
#			# Draw Pin Description
#			for(my $i=0;$i<@{$agprm->{AgComments}};$i++){
#				my $agCom = $agprm->{AgComments}[$i];
#				if($agCom->{drawFlag}){
#					my $color = $image->colorAllocate($agCom->{dr}, $agCom->{dg}, $agCom->{db});
#					my @bounds = $image->stringFT($color, $env->{fontPath}, $fontSize, 0, $drawX, $drawY, url_decode($agCom->{no})." : ".url_decode($agCom->{oname})." : ".url_decode($agCom->{comment}));
#					$drawY = $bounds[1] + $fontSize + 1;
#				}
#			}

#			my @blob = ($image->png);
			my $im = Image::Magick->new(magick=>$image_info->{file_ext});
#			$im->BlobToImage(@blob);
			$im->BlobToImage($c_image);
			$im->Resize(geometry=>"60x60",blur=>0.7);
			$im->Write($image_file);
#			@blob = $im->ImageToBlob();
#			$sp_image = $blob[0];
			$sp_image = $im->ImageToBlob();
			chmod 0666,$image_file;

			undef $im;
#			undef @blob;
			print OUT qq|thumb\t$file.$image_info->{file_ext}\n|;
			undef $image_info;
		}
	}
	close(OUT);
	chmod 0666,$text_file;

	open(IN,"< $text_file");
	my @TEMP = <IN>;
	close(IN);
	my $sp_info = join("",@TEMP);

	my $param_num = 0;
	my $sth;
	my $rows = -1;
	$sth = $dbh->prepare($ins_sql);
	$sth->bind_param(++$param_num, $file);
	$sth->bind_param(++$param_num, $sp_info);
	$sth->bind_param(++$param_num, $sp_image, { pg_type => DBD::Pg::PG_BYTEA });
	$sth->bind_param(++$param_num, $lsdb_OpenID);
	$sth->execute();
	$rows = $sth->rows;
	$sth->finish;
	undef $sth;

	my $success = ($rows>=0? JSON::XS::true : JSON::XS::false);
	if($rows>=0){
		$dbh->commit();
	}else{
		$dbh->rollback();
	}

	$RTN->{success} = $success;
	my $json = encode_json($RTN);
	print $json;
	print LOG __LINE__,":",$json,"\n";
};
if($@){
	my $msg = $@;

	$dbh->rollback();

	$msg =~ s/\s*$//g;
	$msg =~ s/^\s*//g;
	my $RTN = {
		"success" => JSON::XS::false,
		"msg"     => $msg
	};
	my $json = encode_json($RTN);
	print $json;
	print LOG __LINE__,":",$json,"\n";
}

close(LOG);
exit;
