package cgi_lib::common;

use strict;
use warnings;
use feature ':5.10';

use base qw/Exporter/;
use vars qw /@EXPORT/;

use File::Basename qw(!fileparse !fileparse_set_fstype !basename !dirname);
use File::Path;
use File::Spec;
use File::Spec::Functions qw(abs2rel catdir catfile splitdir);
use Cwd;# qw(abs_path);
use Encode;
use JSON::XS;
use Digest::MD5 qw(md5_hex);
use Clone qw(clone);
#use Apache::Htpasswd;
use HTTP::Date;
use Time::Local;
#use Crypt::PasswdMD5;
use Fcntl qw/:flock :mode/;
use Time::HiRes;
use String::Random;
use File::Find;
use Data::Dumper;
use Compress::Zlib;
use FindBin;
use URI::Escape;
use URI::URL;
use HTML::Entities;
use IPC::Run3;
use Time::Piece;
use MIME::Types;
use Cache::FileCache;

my $JSONXS;# = JSON::XS->new->utf8->indent(0)->canonical(1);
my $JSONXS_Extensions ;# = JSON::XS->new->utf8->indent(1)->canonical(1);
my $FileCache;

$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

use Hash::Merge qw( merge );
Hash::Merge::set_behavior('LEFT_PRECEDENT');

=pod
@EXPORT = qw/
	DEBUG
	USE_CONTENT_COMPRESS
	JAVA_PATH
	YUICOMPRESSOR_PATH
	HTMLCOMPRESSOR_PATH
	MINI_EXT
/;
=cut

use constant {
	DEBUG => 1,
	LOG_WRITE_MODE_DAILY => 'Daily',
	LOG_WRITE_MODE_SECONDS => 'Seconds'
};

use constant {
	LOG_WRITE_MODE => LOG_WRITE_MODE_SECONDS,

	USE_CONTENT_COMPRESS => DEBUG ? 0 : 1,
	JAVA_PATH           => &catfile('','usr','bin','java'),
	YUICOMPRESSOR_PATH  => &Cwd::abs_path(&catfile($FindBin::Bin,'..','..','local','yuicompressor-2.4.6','yuicompressor-2.4.6.jar')),	#https://developer.yahoo.com/yui/compressor/
	HTMLCOMPRESSOR_PATH => &Cwd::abs_path(&catfile($FindBin::Bin,'..','..','local','yuicompressor-2.4.6','htmlcompressor-1.5.3.jar')),	#https://code.google.com/p/htmlcompressor/
	MINI_EXT            => qq|.min|,
};

BEGIN{
	$JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);#->relaxed(0);
	$JSONXS_Extensions  = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);
	$FileCache = Cache::FileCache->new({
		cache_root => '/bp3d/cache',
		namespace => 'API',
#		default_expires_in  => '1h',
#		default_expires_in  => '1w',
	});
};

sub message {
	my $str = shift;
	my $fh = shift // \*STDERR;
	my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
	eval{
		$str = '' unless(defined $str && length $str);
		if(ref $str eq 'HASH' || ref $str eq 'ARRAY'){
			say $fh $package.':'.$line.':'.&encodeJSON($str,1);
		}elsif(ref $str ne ''){
			print $fh $package.':'.$line.':'.&Data::Dumper::Dumper($str);
		}else{
			say $fh $package.':'.$line.':'.&encodeUTF8($str);
		}
	};
	if($@){
		say $fh $package.':'.$line.':'.&encodeUTF8($@);
	}
}

sub dumper {
	my $obj = shift;
	my $fh = shift // \*STDERR;
	my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
	print $fh $package.':'.$line.':'.&Data::Dumper::Dumper($obj);
}

sub decodeUTF8 {
	my $str = shift;
	return $str unless(defined $str && length $str);
	$str = &Encode::decode_utf8($str) unless(&Encode::is_utf8($str));
	return $str;
}

sub encodeUTF8 {
	my $str = shift;
	return $str unless(defined $str && length $str);
	$str = &Encode::encode_utf8($str) if(&Encode::is_utf8($str));
	return $str;
}

sub decodeJSON {
	my $json_str = shift;
	my $ext = shift;
	my $json;
	return $json unless(defined $json_str && length $json_str);
	$ext = 1 unless(defined $ext);
	$json_str = &encodeUTF8($json_str);
	eval{$json = $ext ? $JSONXS_Extensions->decode($json_str) : $JSONXS->decode($json_str);};
	if($@){
		say STDERR __FILE__.':'.__LINE__.':'.$@;
		say STDERR __FILE__.':'.__LINE__.':'.$json_str;
	}
	return $json;
}

sub decodeExtensionsJSON {
	my $json_str = shift;
	return &decodeJSON($json_str,1);
}

sub encodeJSON {
	my $json = shift;
	my $ext = shift;
	$ext = 0 unless(defined $ext);
	my $json_str;
	eval{$json_str = $ext ? $JSONXS_Extensions->encode($json) : $JSONXS->encode($json);};
	if($@){
		say STDERR __FILE__.':'.__LINE__.':'.$@ ;
		my($package, $file, $line, $subname, $hasargs, $wantarray, $evaltext, $is_require) = caller();
		say STDERR $package.':'.$line;
	}

	return $json_str;
}

sub encodeExtensionsJSON {
	my $json = shift;
	return &encodeJSON($json,1);
}

sub readFileJSON {
	my $file_path = shift;
	my $json;
	eval{
		if(defined $file_path && -e $file_path && -r $file_path && -s $file_path){
			local $/ = undef;
			open(my $IN,$file_path) or die __FILE__.':'.__LINE__.':'.$!.qq|[$file_path]|;
			flock($IN,1);
			$json = &decodeExtensionsJSON(<$IN>);
			close($IN);
		}else{
#			say STDERR __LINE__.':'.$file_path;
		}
	};
	warn $@,"\n" if($@);
	return $json;
}
sub writeFileJSON {
	my $file_path = shift;
	my $json = shift;
	my $ext = shift;
	my $OUT;
	open($OUT,qq|> $file_path|) or die __FILE__.':'.__LINE__.':'.$!.qq|[$file_path]|;
	flock($OUT,2);
	print $OUT &encodeJSON($json,$ext);
	close($OUT);
	chmod 0666,$file_path;
}

sub url_encode($) {
	my $str = shift;
	$str =~ s/([^\w ])/'%'.unpack('H2', $1)/eg;
	$str =~ tr/ /+/;
	return $str;
}

sub url_decode($) {
	my $str = shift;
	$str =~ tr/+/ /;
	$str =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack('H2', $1)/eg;
	return $str;
}

sub getCookie {
	my $cookie = shift;
	if(exists $ENV{'HTTP_COOKIE'} && defined $ENV{'HTTP_COOKIE'} && $ENV{'HTTP_COOKIE'}){
		my($xx, $name, $value);
		foreach $xx (split(/; */, $ENV{'HTTP_COOKIE'})) {
			($name, $value) = split(/=/, $xx);
			$value =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C", hex($1))/eg;
			$cookie->{$name} = $value;
		}
	}
}

sub setCookie {
	my $name = shift;
	my $val  = shift;

	my $t = &Time::Piece::localtime();
	$t->add_years(10);

	my $tmp;
#	$name =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$val  =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$tmp  = "Set-Cookie: ";
	$tmp .= "$name=$val; ";
#	$tmp .= sprintf(qq|expires=Tue, 1-Jan-2030 00:00:00 GMT;";
	$tmp .= sprintf(qq|expires=%s;|,$t->strftime());
	return($tmp);
}

sub setCookieSession {
	my $name = shift;
	my $val  = shift;
	my $tmp;
#	$name =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$val  =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	$tmp  = "Set-Cookie: ";
	$tmp .= "$name=$val; ";
#	$tmp .= "expires=Tue, 1-Jan-2030 00:00:00 GMT;";
	return($tmp);
}

sub clearCookie {
	my $name = shift;

	my $t = &Time::Piece::localtime();
	$t->add_years(-10);

#	$name =~ s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
	my $tmp = "Set-Cookie: ";
	$tmp .= "$name=; ";
#	$tmp .= " expires=Tue, 1-Jan-1980 00:00:00 GMT;";
	$tmp .= sprintf(qq|expires=%s;|,$t->strftime());
	return($tmp);
}

sub yuiCSS {
	my $file_list = shift;
	my $rtn = '';
	if(defined $file_list && ref $file_list eq 'ARRAY'){
		my $java = JAVA_PATH;
		my $yui = YUICOMPRESSOR_PATH;
		my $mini_ext = MINI_EXT;
		my @extlist = (qq|$mini_ext.css|,'.css');
		foreach my $css (@$file_list){
			next unless(-e $css);
			if(USE_CONTENT_COMPRESS){
				my($css_name,$css_dir,$css_ext) = &File::Basename::fileparse($css,@extlist);
				if(defined $css_ext && length($css_ext)>0 && $css_ext eq '.css'){
					my $mini_css = &catfile($css_dir,$css_name.$mini_ext.$css_ext);
					if(-w $css_dir){
						unlink $mini_css if(-e $mini_css && (stat($css))[9]>(stat($mini_css))[9]);
						unless(-e $mini_css){
							system(qq|$java -jar $yui --type css --nomunge --charset utf-8 -o $mini_css $css|) if(-e $java && -e $yui);
							chmod 0666,$mini_css if(-e $mini_css);
						}
					}
					$css = $mini_css if(-e $mini_css);
				}
			}
			my $mtime = (stat($css))[9];
			my $t = &Time::Piece::localtime($mtime);
			$mtime = $t->strftime('%y%m%d%H%M%S');
			$css .= '?'.$mtime;
			$css = &HTML::Entities::encode_entities($css, q{&<>"'});
			$rtn .= qq|<link rel="stylesheet" href="$css" type="text/css" media="all" charset="UTF-8">\n|;
		}
	}
	return $rtn;
}

sub yuiJS {
	my $file_list = shift;
	my $PARAMS = shift;
	my $rtn = qq||;
	if(defined $file_list && ref $file_list eq 'ARRAY'){
		my $java = JAVA_PATH;
		my $yui = YUICOMPRESSOR_PATH;
		my $mini_ext = MINI_EXT;
		my @extlist = (qq|$mini_ext.js|,'.js','.cgi');
		foreach my $file (@$file_list){
			my $url = new URI::URL $file;
			my @query_form = $url->query_form();
			my $js = $url->path;
			next unless(-e $js);
			my($js_name,$js_dir,$js_ext) = &File::Basename::fileparse($js,@extlist);
			if(USE_CONTENT_COMPRESS){
				my $mini_js = &catfile($js_dir,$js_name.$mini_ext.'.js');
				if(defined $js_ext && length($js_ext)>0 && $js_ext eq '.js'){
					if(-w $js_dir){
						unlink $mini_js if(-e $mini_js && (stat($js))[9]>(stat($mini_js))[9]);
						unless(-e $mini_js){
							&message('');
							system(qq|$java -jar $yui --type js --nomunge --charset utf-8 -o $mini_js $js|) if(-e $java && -e $yui);
							chmod 0666,$mini_js if(-e $mini_js);
						}
					}
					if(-e $mini_js){
						$js = $mini_js;
						undef $url;
						$url = new URI::URL $js;
					}
				}
			}

			my $mtime = (stat($js))[9];
			my $t = &Time::Piece::localtime($mtime);
			$mtime = $t->strftime('%y%m%d%H%M%S');
			if($js_ext eq '.cgi' && exists($PARAMS->{'lng'})){
				push(@query_form,'lng',$PARAMS->{'lng'});
				push(@query_form,$mtime,undef);
				$url->query_form(@query_form);
			}else{
				$url->keywords($mtime);
			}
			my $src = $url->as_string;
			$src =~ s/[\&\=\?]$//g;
			$src = &HTML::Entities::encode_entities($src, q{&<>"'});
			$rtn .= qq|<script type="text/javascript" src="$src" charset="utf-8"></script>\n|;

		}
	}
	return $rtn;
}

sub js_compress {
	my $in = shift;
	my $out;
	my $err;
	if(USE_CONTENT_COMPRESS){
		my @cmd = (JAVA_PATH, '-jar', YUICOMPRESSOR_PATH, '--type', 'js', '--nomunge', '--charset', 'utf-8');
		&IPC::Run3::run3(\@cmd, \$in, \$out, \$err);
	}else{
		$out = $in;
	}
#	return wantarray ? ($out,$err) : $out;
	return $out;
}

sub css_compress {
	my $in = shift;
	my $out;
	my $err;
	if(USE_CONTENT_COMPRESS){
		my @cmd = (JAVA_PATH, '-jar', YUICOMPRESSOR_PATH, '--type', 'css', '--nomunge', '--charset', 'utf-8');
		&IPC::Run3::run3(\@cmd, \$in, \$out, \$err);
	}else{
		$out = $in;
	}
#	return wantarray ? ($out,$err) : $out;
	return $out;
}

sub html_compress {
	my $in = shift;
	my $out;
	my $err;
	if(USE_CONTENT_COMPRESS){
		my @cmd = (JAVA_PATH, '-jar', HTMLCOMPRESSOR_PATH, '--type', 'html', '--remove-intertag-spaces', '--simple-doctype', '--compress-js', '--compress-css', '--nomunge', '--charset', 'utf-8');
		&IPC::Run3::run3(\@cmd, \$in, \$out, \$err);
	}else{
		$out = $in;
	}
#	return wantarray ? ($out,$err) : $out;
	return $out;
}

sub useGZip {
	my $usegzip;
	if(exists $ENV{'HTTP_ACCEPT_ENCODING'} && defined $ENV{'HTTP_ACCEPT_ENCODING'} && length $ENV{'HTTP_ACCEPT_ENCODING'}){
		foreach my $enc (split(/\s*,\s*/,$ENV{'HTTP_ACCEPT_ENCODING'})){
			next unless(defined $enc && length $enc);
			$enc =~ s/;.*$//s;
			next unless($enc =~ /^(x-)?gzip$/);
			$usegzip = $enc;
			last;
		}
	}
	return $usegzip;
}

sub printContentJSON {
	my $json = shift;
	my $PARAMS = shift // {};
	if($@){
		$json = {
			success => JSON::XS::false,
			msg => $@
		};
	}
	return unless(defined $json);

	if(ref $json eq 'HASH' && exists $json->{'msg'} && defined $json->{'msg'}){
		$json->{'msg'} = &decodeUTF8($json->{'msg'});
		$json->{'msg'} =~ s/\s+at\s+\/.+$//g;# unless(DEBUG);
		$json->{'msg'} =~ s/\s*$//g;
		$json->{'msg'} =~ s/^\s*//g;
	}

	my $jsonstr;
	if(ref $json eq 'HASH' || ref $json eq 'ARRAY'){
		$jsonstr = &encodeJSON($json);
	}else{
		$jsonstr = $json;
	}
	if(exists $PARAMS->{'callback'} && defined $PARAMS->{'callback'} && length $PARAMS->{'callback'}){
		&printContent($PARAMS->{'callback'}.qq|($jsonstr)|,'application/javascript');
	}else{
		&printContent($jsonstr,'application/javascript');
	}
	return $jsonstr;
}

sub _printContentJSON {
	my $json = shift;
	my $PARAMS = shift // {};
	if($@){
		$json = {
			success => JSON::XS::false,
			msg => $@
		};
	}
	unless(defined $json){
		&_printContent($json);
		return undef;
	}

	if(ref $json eq 'HASH' && exists $json->{'msg'} && defined $json->{'msg'}){
		$json->{'msg'} = &decodeUTF8($json->{'msg'});
		$json->{'msg'} =~ s/\s+at\s+\/.+$//g;# unless(DEBUG);
		$json->{'msg'} =~ s/\s*$//g;
		$json->{'msg'} =~ s/^\s*//g;
	}

	my $jsonstr;
	if(ref $json eq 'HASH' || ref $json eq 'ARRAY'){
		$jsonstr = &encodeJSON($json);
	}else{
		$jsonstr = $json;
	}
	if(exists $PARAMS->{'callback'} && defined $PARAMS->{'callback'} && length $PARAMS->{'callback'}){
		&_printContent($PARAMS->{'callback'}.qq|($jsonstr)|);
	}else{
		&_printContent($jsonstr);
	}
	return $jsonstr;
}

sub printContent {
	my $content = shift;
	my $contentType = shift;
	my $cookie = shift;
#	my $usegzip = &useGZip();
#	$content= &Compress::Zlib::memGzip($content) if(defined $usegzip);

	$contentType //= 'text/html';

	if(exists $ENV{'REQUEST_METHOD'} && defined $cookie){
		my(@cookie) = ref($cookie) && ref($cookie) eq 'ARRAY' ? @{$cookie} : $cookie;
		for (@cookie) {
			my $cs = UNIVERSAL::isa($_,'CGI::Cookie') ? $_->as_string : $_;
			next if $cs eq '';
			if($cs =~ /^Set-Cookie:/){
				say $cs;
			}else{
				say qq|Set-Cookie: $cs|;
			}
		}
	}

	say qq|Content-type: $contentType; charset=UTF-8| if(exists $ENV{'REQUEST_METHOD'});
#	say qq|Content-Encoding: $usegzip| if(defined $usegzip);
#	say qq||;
#	say $content;
	&_printContent($content);
}
sub _printContent {
	my $content = shift;
	if(defined $content && $content){
		if(exists $ENV{'REQUEST_METHOD'}){
			my $usegzip = &useGZip();
			if(defined $usegzip){
				$content= &Compress::Zlib::memGzip($content);
				say qq|Content-Encoding: $usegzip|;
			}
			say 'Accept-Ranges: bytes';
			say 'Content-Length: '.length($content);
			say qq||;
		}
		say $content;
	}else{
		say qq||;
	}
}

sub printDownloadResponseHeaders {
	my $file_path = shift;
	my $lastModified = shift;
	my $contentLength = shift;

	my $filename = &File::Basename::basename($file_path) if(defined $file_path && length $file_path);

	$filename = 'download' unless(defined $filename);
	$lastModified = time unless(defined $lastModified);

#	print qq|Content-Type: text/plain\n|;
#	print qq|Pragma: no-cache\n|;
#	print qq|\n|;
#	return;

	my $types = MIME::Types->new;
	my $mimeType = $types->mimeTypeOf($file_path);
	my $mime = $mimeType->type() if(defined $mimeType);
	$mime = qq|application/octet-stream| unless(defined $mime);

	print qq|X-Content-Type-Options: nosniff\n|;
	print qq|Content-Type: $mime\n|;
	print qq|Content-Disposition: attachment; filename=$filename\n|;
	print qq|Last-Modified: |.&HTTP::Date::time2str($lastModified).qq|\n|;
	if(defined $contentLength){
		print qq|Accept-Ranges: bytes\n|;
		print qq|Content-Length: $contentLength\n|;
	}
	print qq|Pragma: no-cache\n|;
	print qq|\n|;
}

sub printNotFound {
	say qq|Status: 404 Not Found|;
	exit;
}

sub printRequestTimeout {
	say qq|Status: 408 Request Timeout|;
	exit;
}

sub getLogFH {
	my $PARAMS = shift // {};
	my $COOKIE = shift // {};
	my $log_filename = shift;
	my $log_dirname = shift // 'logs';

	my($seconds, $microseconds) = &Time::HiRes::gettimeofday();
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($seconds);
	my $logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d.%d",$year+1900,$mon+1,$mday,$hour,$min,$sec,$microseconds);
	my $filetime = sprintf("%04d/%02d/%02d",$year+1900,$mon+1,$mday);
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);
	my $log_dir = &catdir($FindBin::Bin,$log_dirname,$filetime);
	if(exists $ENV{'HTTP_X_FORWARDED_FOR'}){
#		my @H = split(/,\s*/,$ENV{'HTTP_X_FORWARDED_FOR'});
#		$log_dir = &catdir($log_dir,@H);
		$log_dir = &catdir($log_dir,$ENV{'HTTP_X_FORWARDED_FOR'});
	}elsif(exists $ENV{'REMOTE_ADDR'}){
		$log_dir = &catdir($log_dir,$ENV{'REMOTE_ADDR'});
	}else{
		$log_dir = &catdir($log_dir,'localhost');
	}
	$log_dir = &catdir($log_dir,$COOKIE->{'ag_annotation.session'}) if(exists $COOKIE->{'ag_annotation.session'} && defined $COOKIE->{'ag_annotation.session'} && $COOKIE->{'ag_annotation.session'});
#	$log_dir = &catdir($log_dir,sprintf("%02d/%02d/%02d/%05d",$hour,$min,$sec,$$)) if(DEBUG);
#	$log_dir = &catdir($log_dir,sprintf("%02d/%02d/%05d",$hour,$min,$$)) if(DEBUG);
#	$log_dir = &catdir($log_dir,sprintf("%02d/%02d",$hour,$min)) if(DEBUG);
	unless(-e $log_dir){
		my $old_umask = umask(0);
		&File::Path::mkpath($log_dir,0,0777);
		umask($old_umask);
	}
	if(LOG_WRITE_MODE() eq LOG_WRITE_MODE_SECONDS()){
		$log_filename = sprintf(qq|%02d-%02d-%02d-%05d-%s.txt|,$hour,$min,$sec,$$,defined $log_filename && length $log_filename ? $log_filename : $cgi_name);
	}else{
		$log_filename = (defined $log_filename && length $log_filename ? $log_filename : $cgi_name).qq|.txt|;
	}
	my $log_file = &catfile($log_dir,$log_filename);
#	&message($log_file);
	open(my $LOG,qq|>> $log_file|) or die qq|$! [$log_file]|;
	if(flock($LOG,6)){
		my $oldfh = select($LOG);
		$| = 1;
		select($oldfh);
		binmode($LOG,':utf8');
		say $LOG "\n[$logtime]:$0";
		print $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':$PARAMS='.&Data::Dumper::Dumper($PARAMS);
		print $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':$COOKIE='.&Data::Dumper::Dumper($COOKIE);
		print $LOG __PACKAGE__.':'.__FILE__.':'.__LINE__.':%ENV='.&Data::Dumper::Dumper(\%ENV);

	}elsif(defined $LOG){
		undef $LOG;
		$LOG = \*STDERR if(DEBUG);
	}
	return $LOG;
}

sub get_cache {
	my $uri;
	my $data;
	$uri = $ENV{'REQUEST_URI'} if(uc $ENV{'REQUEST_METHOD'} eq 'GET');
	undef $uri unless(defined $uri && $uri =~ /shorten=[^\&]+/);
	$data = $FileCache->get($uri) if(defined $FileCache && defined $uri);
	return $data;
}

sub set_cache {
	my $data = shift;
	my $uri;
	$uri = $ENV{'REQUEST_URI'} if(uc $ENV{'REQUEST_METHOD'} eq 'GET');
	undef $uri unless(defined $uri && $uri =~ /shorten=[^\&]+/);
	if(defined $FileCache && defined $uri && defined $data){
		$FileCache->set($uri, $data);
		$FileCache->Purge();
	}
}

1;
