#!/bp3d/local/perl/bin/perl
#未完成
$| = 1;

use strict;
#use cgi_lib::common;

use CGI::Cookie;
use FindBin;

#$CGI::POST_MAX = 1024 * 1024 * 20;	# 1024 * 1KBytes = 20MBytes.
$CGI::POST_MAX = 1024 * 1024 * 2000;	# 1024 * 1KBytes = 20MBytes.

use File::Basename;
use File::Path;
use File::Spec;
use File::Copy;
use JSON::XS;
use Data::Dumper;

my @extlist = qw|.cgi|;
my($name,$dir,$ext) = &File::Basename::fileparse($0,@extlist);
#open(LOG,"> logs/$name.$$.txt");
open(LOG,"> logs/$name.txt");
flock(LOG,2);

foreach my $key (sort keys(%ENV)){
	print LOG __LINE__,":[$key]=[$ENV{$key}]\n";
}

=pod
my $postdata;
if($ENV{'REQUEST_METHOD'} eq 'POST'){
	read(STDIN, $postdata, $ENV{'CONTENT_LENGTH'});
}else{
	$postdata = $ENV{'QUERY_STRING'};
}
print LOG __LINE__,":\$postdata=[$postdata]\n";

my $query = CGI->new($postdata);
=cut

my $query = CGI->new;
my @params = $query->param();
my $PARAMS = {};
foreach my $param (sort @params){
	if(defined $query->param($param)){
		$PARAMS->{$param} = $query->param($param);
#		$PARAMS->{'POSTDATA'} .= $PARAMS->{$param} if(defined $param && $param eq '' && $ENV{'REQUEST_METHOD'} eq 'POST');
	}else{
		$PARAMS->{$param} = undef;
	}
	$PARAMS->{$param} = undef if(defined $PARAMS->{$param} && length($PARAMS->{$param})==0);
#print LOG __LINE__,":[$param][",(defined $param ? 1 : 0),"][",($param eq '' ? 1 : 0),"][",length($param),"]\n";
print LOG __LINE__,":[$param][$PARAMS->{$param}]\n" if(defined $PARAMS->{$param});
}

#$PARAMS->{'POSTDATA'} = $postdata if($ENV{'REQUEST_METHOD'} eq 'POST' && defined $postdata && !defined $PARAMS->{'POSTDATA'});


my @cookie_params = $query->cookie();
my $COOKIE = {};
foreach my $cookie_param (sort @cookie_params){
	$COOKIE->{$cookie_param} = defined $query->cookie($cookie_param) ? $query->cookie($cookie_param) : undef;
#	$COOKIE->{$cookie_param} = undef if(defined $COOKIE->{$cookie_param} && length($COOKIE->{$cookie_param})==0);
print LOG __LINE__,":[$cookie_param][$COOKIE->{$cookie_param}]\n" if(defined $COOKIE->{$cookie_param});
}


my $def_json = &cgi_lib::common::getDef();
#my $RTN = Clone::clone($PARAMS);
my $RTN = {};
$RTN->{'success'} = JSON::XS::false;
$RTN->{'msg'}     = $query->cgi_error;

unless(defined $RTN->{'msg'}){
	if(defined &cgi_lib::common::updateAuth($PARAMS->{'authID'},$PARAMS->{'sessionID'})){
		my $auth_info = &cgi_lib::common::getAuthInfo($PARAMS->{'authID'},$PARAMS->{'sessionID'});
		if(defined $auth_info){

			umask(0);
			my $upload_path = &cgi_lib::common::getDataPath($PARAMS->{'authID'},'Upload');
			&File::Path::mkpath($upload_path,0,0777) unless(-e $upload_path);

			if(defined $PARAMS->{'file1'}){
				$RTN->{'success'} = JSON::XS::true;

				foreach my $key (sort keys(%$PARAMS)){
					print LOG __LINE__,":\$key=[$key]\n";
					next unless($key =~ /^file[0-9]+$/);
					next unless(defined $PARAMS->{$key});

					my $filename = $PARAMS->{$key};
					my $filepath = File::Spec->catdir($upload_path,$filename);

					print LOG __LINE__,":\$filename=[$filename]\n";
					print LOG __LINE__,":\$filepath=[$filepath]\n";

					my $fh = $query->upload($key);
					if(defined $fh){
						print LOG __LINE__,":\$filepath=[$filepath]\n";
						if(open(OUT,"> $filepath")){
							flock(OUT,2);
							binmode(OUT);
							binmode($fh);
							my $buffer;
							while(read($fh, $buffer, 1024)){
								print OUT $buffer;
							}
							close(OUT);
						}else{
							$RTN->{'success'} = JSON::XS::false;
							$RTN->{'msg'}     = $!;
							last;
						}
					}
				}
			}
		}
	}elsif(defined &cgi_lib::common::updateAuth($COOKIE->{'authID'},$COOKIE->{'sessionID'})){
		my $auth_info = &cgi_lib::common::getAuthInfo($COOKIE->{'authID'},$COOKIE->{'sessionID'});
		if(defined $auth_info){

			my $workfile_fmt = qq|.%s-%d|;
			my $workfileall_fmt = qq|.%s-*|;

			umask(0);
			my $upload_path = &cgi_lib::common::getDataPath($COOKIE->{'authID'},'Upload');
			&File::Path::mkpath($upload_path,0,0777) unless(-e $upload_path);
			if(
				defined $PARAMS->{'POSTDATA'} &&
				defined $COOKIE->{'upload.name'} &&
				defined $COOKIE->{'upload.type'} &&
				defined $COOKIE->{'upload.size'} &&
				defined $COOKIE->{'upload.modified'} &&
				defined $COOKIE->{'upload.slice'} &&
				defined $COOKIE->{'upload.index'}
			){
				$RTN->{'success'} = JSON::XS::true;
				if(defined $COOKIE->{'upload.remove'}){
					for(my $i=0;;$i++){
						my $filepath_c = File::Spec->catdir($upload_path,sprintf($workfile_fmt,$COOKIE->{'upload.name'},$i));
						if(-e $filepath_c){
							unlink $filepath_c;
						}else{
							last;
						}
					}
				}else{
					my $filepath_a = File::Spec->catdir($upload_path,$COOKIE->{'upload.name'});
					my $modified = $COOKIE->{'upload.modified'} / 1000;
					if(-e $filepath_a && -s $filepath_a == $COOKIE->{'upload.size'} && (stat($filepath_a))[9] == $modified){
						$RTN->{'totalSize'} = (-s $filepath_a);
					}else{
						my $filepath = File::Spec->catdir($upload_path,sprintf($workfile_fmt,$COOKIE->{'upload.name'},$COOKIE->{'upload.index'}));
						print LOG __LINE__,":\$filepath=[$filepath]\n";
						if(open(OUT,"> $filepath")){
							flock(OUT,2);
							binmode(OUT);
							print OUT $PARAMS->{'POSTDATA'};
							close(OUT);
							if(length($PARAMS->{'POSTDATA'})<$COOKIE->{'upload.slice'}){

								print LOG __LINE__,":",length($PARAMS->{'POSTDATA'}),"\n";
								print LOG __LINE__,":",$COOKIE->{'upload.slice'},"\n";

								my $filepath_c = File::Spec->catdir($upload_path,sprintf($workfileall_fmt,$COOKIE->{'upload.name'}));
								system(qq/cat `ls -v $filepath_c` > $filepath_a/);
								for(my $i=0;;$i++){
									my $filepath_c = File::Spec->catdir($upload_path,sprintf($workfile_fmt,$COOKIE->{'upload.name'},$i));
									if(-e $filepath_c){
										unlink $filepath_c;
									}else{
										last;
									}
								}
								if(-e $filepath_a && -s $filepath_a == $COOKIE->{'upload.size'}){
									utime $modified,$modified,$filepath_a;
									$RTN->{'totalSize'} = (-s $filepath_a);
								}else{
									$RTN->{'success'} = JSON::XS::false;
								}
							}else{
								$RTN->{'totalSize'} = 0;
								for(my $i=0;;$i++){
									my $filepath_c = File::Spec->catdir($upload_path,sprintf($workfile_fmt,$COOKIE->{'upload.name'},$i));
									if(-e $filepath_c){
										$RTN->{'totalSize'} += (-s $filepath_c);
									}else{
										last;
									}
								}
							}
						}else{
							print LOG __LINE__,":\n";
							$RTN->{'success'} = JSON::XS::false;
							$RTN->{'msg'}     = $!;
						}
					}
				}
			}elsif(
				defined $COOKIE->{'upload.name'} &&
				defined $COOKIE->{'upload.type'} &&
				defined $COOKIE->{'upload.size'} &&
				defined $COOKIE->{'upload.modified'} &&
				defined $COOKIE->{'upload.slice'} &&
				defined $COOKIE->{'upload.index'} &&
				defined $COOKIE->{'upload.remove'}
			){
				$RTN->{'success'} = JSON::XS::true;
				for(my $i=0;;$i++){
					my $filepath_c = File::Spec->catdir($upload_path,sprintf($workfile_fmt,$COOKIE->{'upload.name'},$i));
					if(-e $filepath_c){
						unlink $filepath_c;
					}else{
						last;
					}
				}
			}
		}
	}
}




#=pod
#print qq|Content-type: text/html; charset=UTF-8\n|;
#print qq|\n|;
#print &JSON::XS::encode_json($RTN),"\n";
&gzip_json($RTN);

print LOG __LINE__,":",Data::Dumper->Dump([$RTN]),"\n";

#=cut

close(LOG);
exit;


sub saveFile {
	my $data_path = shift;
	my $obj = shift;

#	print LOG __LINE__,":\$obj=[",(ref $obj),"][",(ref $obj eq "HASH" ? &JSON::XS::encode_json($obj) : ""),"]\n";

	$obj->{'file'} =~ s/C:\\fakepath\\//g;
	$obj->{'file'} = File::Spec->catdir($data_path,$obj->{'file'});

	print LOG __LINE__,":\$obj->{'file'}=[$obj->{'file'}]\n";

	if(defined $PARAMS->{$obj->{name}} && defined $query->upload($obj->{name})){
		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
		my $savetime = sprintf("%04d%02d%02d",$year+1900,$mon+1,$mday);
		my $save_path;
		my $cnt=0;
		do{
			$save_path = File::Spec->catdir($data_path,sprintf("%s_%03d",$savetime,++$cnt));
			print LOG __LINE__,":\$save_path=[$save_path]\n";
		}while(-e $save_path);

#		my $file = File::Spec->catdir($data_path,$save_path,$PARAMS->{$obj->{name}});
		my $file = File::Spec->catdir($save_path,$PARAMS->{$obj->{name}});
		my $fh = $query->upload($obj->{name});
		if(defined $fh){
			print LOG __LINE__,":\$file=[$file]\n";

			my $org_umask = umask();
			umask(0);
			my $dir = File::Basename::dirname($file);
			&File::Path::mkpath($dir,0,0777) unless(-e $dir);

			open(OUT,"> $file");
			binmode(OUT);
			binmode($fh);
			my $buffer;
			while(read($fh, $buffer, 1024)){
				print OUT $buffer;
			}
			close(OUT);

			umask($org_umask);
			$obj->{'file'} = $file;
		}
	}
}
