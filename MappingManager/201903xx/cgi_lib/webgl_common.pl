use strict;
#use warnings;
use feature ':5.10';
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI::Cookie;
use JSON::XS;
use File::Basename;
use File::Path;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir);
use Clone;
use Cwd;
use Data::Dumper;

use FindBin;
my $htdocs_path;

use Encode;
use JSON::XS;
my $JSONXS;
my $JSONXS_Extensions;

BEGIN{
#	$htdocs_path = qq|/bp3d/ag1/htdocs_130903|;
#	$htdocs_path = qq|/bp3d/ag-test/htdocs_131011|;
	$htdocs_path = qq|/bp3d/ag-test/htdocs| unless(defined $htdocs_path && -e $htdocs_path);
	$JSONXS = JSON::XS->new->utf8->indent(0)->canonical(1);#->relaxed(0);
	$JSONXS_Extensions  = JSON::XS->new->utf8->indent(1)->canonical(1)->relaxed(1);
}
use lib $htdocs_path,&catdir($htdocs_path,'API'),&catdir($htdocs_path,'..','lib'),&catdir($htdocs_path,'..','..','ag-common','lib');

#DEBUG
$ENV{'AG_DB_NAME'} = 'bp3d_manage' unless(exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'});
$ENV{'AG_DB_HOST'} = '127.0.0.1'   unless(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'});
$ENV{'AG_DB_PORT'} = '8543'        unless(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'});

require "common.pl";
#require "common_db.pl";
use cgi_lib::common;

my $DB_user = 'postgres';
my $DB_pwd  = '';
my $DB_dbname = defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'bp3d_manage';
my $DB_host = defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1';
my $DB_port = defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '8543';#ag1
my $mydb;
my $mydb_local;

#my $LUDIA_OPERATOR='@@';
my $LUDIA_OPERATOR='%%'; #Ludiaが1.5.0以上で、PostgreSQLが8.3以上の場合、こちらを使用すること

&connectDB;

#------------------------------------------------------------------------------
# データベース共通関数
#------------------------------------------------------------------------------
sub connectDB {
	my %args = (
		dbname => $DB_dbname,
		host   => $DB_host,
		port   => $DB_port,
		user   => $DB_user,
		passwd => $DB_pwd,
		@_
	);
	my $DB_name = qq|dbname=$args{'dbname'};host=$args{'host'};port=$args{'port'}|;
#	&cgi_lib::common::message($DB_name);
	$mydb = DBI->connect("dbi:Pg:$DB_name",$args{'user'},$args{'passwd'}) or carp DBI->errstr;
	$mydb->{pg_enable_utf8} = 1 if(defined $mydb);
}

sub disconnectDB {
	$mydb->disconnect();
	undef $mydb;
}

sub get_dbh {
	return $mydb;
}

sub get_ludia_operator {
	return $LUDIA_OPERATOR;
}

sub existsTable {
	my $tablename = shift;
	return 0 unless(defined $tablename);
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|select tablename from pg_tables where tablename=?|);
	$sth->execute($tablename);
	my $rows = $sth->rows();
	undef $sth;
#	&cgi_lib::common::message($tablename);
#	&cgi_lib::common::message($rows);
	return $rows;
}

sub existsTableColumn {
	my $tablename = shift;
	my $columnname = shift;
	return 0 unless(defined $tablename && defined $columnname);
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|SELECT column_name FROM information_schema.columns WHERE table_name=? AND column_name=?|);
	$sth->execute($tablename,$columnname);
	my $rows = $sth->rows();
	undef $sth;
	return $rows;
}

sub getIndexnamesFromTablename {
	my $tablename = shift;
	return undef unless(defined $tablename);
	my @RTN = ();
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|select indexname from pg_indexes where tablename=?|);
	$sth->execute($tablename);
	my $rows = $sth->rows();
	my $indexname;
	my $column_number = 0;
	$sth->bind_col(++$column_number, \$indexname, undef);
	while($sth->fetch){
		push(@RTN,$indexname) if(defined $indexname);
	}
	$sth->finish;
	undef $sth;
	return wantarray ? @RTN : \@RTN;
}

sub getLogDir {
	my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime();
	$year+=1900;
	$mon+=1;
	my $s_year =  sprintf(qq|%04d|,$year);
	my $s_month = sprintf(qq|%02d|,$mon);
	my $s_mday =  sprintf(qq|%02d|,$mday);
	my $log_dir = &catdir($FindBin::Bin,'logs',$s_year,$s_month,$s_mday);
	&File::Path::make_path($log_dir) unless(-e $log_dir);
	return $log_dir;
}

sub getLogFile {
	my $cookie = shift;
	$cookie = {} unless(defined $cookie);
	my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0, qr/\..*$/);

	my $log_dir = &getLogDir();
	my $file_name = exists $cookie->{'ag_annotation.session'} ? qq|$cookie->{'ag_annotation.session'}.$cgi_name.txt| : qq|$cgi_name.txt|;
	my $file = &catfile($log_dir,$file_name);
	return wantarray ? ($file,$cgi_name,$cgi_dir,$cgi_ext) : $file;
}

sub makeImagePath {
	my $img_path = shift;
	my $img_name = shift;
	if($img_name =~ /^([A-Z]+)/){
		$img_path = &catdir($img_path,$1);
		if($img_name =~ /^[A-Z]+([0-9]+)/){
#			my $s = sprintf("%04d",$1);
			my $s = $1;
			$s = '0'.$s while(length($s)<4);
			for(my $i=0;$i<4;$i+=2){
				my $t = substr($s,$i,2);
				last if(length($t)<2);
				$img_path = &catdir($img_path,$t);
			}
		}
	}elsif($img_name =~ /^([0-9]+)$/){
#		my $s = sprintf("%04d",$1);
		my $s = $1;
		$s = '0'.$s while(length($s)<4);
		for(my $i=0;$i<4;$i+=2){
			my $t = substr($s,$i,2);
			last if(length($t)<2);
			$img_path = &catdir($img_path,$t);
		}
	}else{
		my $s = $img_name;
		for(my $i=0;$i<4;$i+=2){
			my $t = substr($s,$i,2);
			last if(length($t)<2);
			$img_path = &catdir($img_path,$t);
		}
	}
	return $img_path;
}
sub getObjImagePrefix {
	my $obj_name = shift;
	my $md_id = shift;
	my $mv_id = shift;

	my @DIR = ($FindBin::Bin);
#	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
#	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'art_images');
	push(@DIR,$md_id) if(defined $md_id);
	push(@DIR,$mv_id) if(defined $mv_id);
	my $prefix = &catdir(@DIR);
	my $img_path = &makeImagePath($prefix,$obj_name);
	my $img_prefix = &catdir($img_path,$obj_name);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getRepImagePrefix {
	my $mr_version = shift;
	my $bul_id = shift;
	my $cdi_name = shift;

	my @DIR = ($FindBin::Bin);
#	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
#	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'bp3d_images');
	push(@DIR,$mr_version) if(defined $mr_version && length $mr_version);
	my $prefix = &catdir(@DIR);
#	return $prefix unless(defined $bul_id && defined $cdi_name);
	return $prefix unless(defined $cdi_name);
	my $img_path;
	if(defined $bul_id){
		$img_path = &makeImagePath(&catdir($prefix,$bul_id),$cdi_name);
	}else{
		$img_path = &makeImagePath($prefix,$cdi_name);
	}
	my $img_prefix = &catdir($img_path,$cdi_name);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getCmImagePrefix {
	my $md_id = shift;
	my $mv_id = shift;
	my $bul_id = shift;
	my $cdi_name = shift;

	my @DIR = ($FindBin::Bin);
#	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
#	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'cm_images');
	push(@DIR,$md_id) if(defined $md_id);
	push(@DIR,$mv_id) if(defined $mv_id);
	my $prefix = &catdir(@DIR);

#	return $prefix unless(defined $bul_id && defined $cdi_name);
	return $prefix unless(defined $cdi_name);
	my $img_path;
	if(defined $bul_id){
		$img_path = &makeImagePath(&catdir($prefix,$bul_id),$cdi_name);
	}else{
		$img_path = &makeImagePath($prefix,$cdi_name);
	}
	my $img_prefix = &catdir($img_path,$cdi_name);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getMcaImagePrefix {
	my $mca_id = shift;

	my @DIR = ($FindBin::Bin);
#	push(@DIR,$ENV{'AG_DB_HOST'}) if(exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} && length $ENV{'AG_DB_HOST'});
#	push(@DIR,$ENV{'AG_DB_PORT'}) if(exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} && length $ENV{'AG_DB_PORT'});
	push(@DIR,'mca_images');
	my $prefix = &catdir(@DIR);

	return $prefix unless(defined $mca_id);
	my $img_path = &makeImagePath($prefix,$mca_id);
	my $img_prefix = &catdir($img_path,$mca_id);
	return wantarray ? ($img_prefix,$img_path) : $img_prefix;
}

sub getImageFileList {
	my $img_prefix = shift;
	my $img_size = shift;

#	my @SIZES = ([640,640],[120,120],[40,40],[16,16]);
#	my @SIZES = (undef,[120,120],undef,[16,16]);
	my @SIZES;
	my @DIR = qw|front left back right|;

	if(defined $img_size && ref $img_size eq 'ARRAY'){
		push(@SIZES,@$img_size);
	}else{
		@SIZES = ([640,640],[120,120],[40,40],[16,16]);
	}

	my $sizeL = shift @SIZES;
	my $sizeM = shift @SIZES;
	my $sizeS = shift @SIZES;
	my $sizeXS = shift @SIZES;

	my $sizeStrL = join("x",@$sizeL)   if(defined $sizeL && ref $sizeL eq 'ARRAY');
	my $sizeStrM = join("x",@$sizeM)   if(defined $sizeM && ref $sizeM eq 'ARRAY');
	my $sizeStrS = join("x",@$sizeS)   if(defined $sizeS && ref $sizeS eq 'ARRAY');
	my $sizeStrXS = join("x",@$sizeXS) if(defined $sizeXS && ref $sizeXS eq 'ARRAY');

	my $gif_prefix_fmt = qq|%s_%s|;
	my $gif_fmt = qq|$gif_prefix_fmt.gif|;

	my $png_prefix_fmt = qq|%s_%s_%s|;
	my $png_fmt = qq|$png_prefix_fmt.png|;

	my $imgsL;
	my $imgsM;
	my $imgsS;
	my $imgsXS;

	if(defined $img_prefix){
		if(defined $sizeStrL){
			push(@$imgsL,sprintf($gif_fmt,$img_prefix,$sizeStrL));
			foreach my $dir (@DIR){
				push(@$imgsL,sprintf($png_fmt,$img_prefix,$dir,$sizeStrL));
			}
		}

		if(defined $sizeStrM){
			push(@$imgsM,sprintf($gif_fmt,$img_prefix,$sizeStrM));
			foreach my $dir (@DIR){
				push(@$imgsM,sprintf($png_fmt,$img_prefix,$dir,$sizeStrM));
			}
		}

		if(defined $sizeStrS){
			push(@$imgsS,sprintf($gif_fmt,$img_prefix,$sizeStrS));
			foreach my $dir (@DIR){
				push(@$imgsS,sprintf($png_fmt,$img_prefix,$dir,$sizeStrS));
			}
		}

		if(defined $sizeStrXS){
			push(@$imgsXS,sprintf($gif_fmt,$img_prefix,$sizeStrXS));
			foreach my $dir (@DIR){
				push(@$imgsXS,sprintf($png_fmt,$img_prefix,$dir,$sizeStrXS));
			}
		}
	}

	my $RTN;
	if(wantarray){
		push(@$RTN,defined $imgsL && ref $imgsL eq 'ARRAY' ? @$imgsL : undef);
		push(@$RTN,defined $imgsM && ref $imgsM eq 'ARRAY' ? @$imgsM : undef);
		push(@$RTN,defined $imgsS && ref $imgsS eq 'ARRAY' ? @$imgsS : undef);
		push(@$RTN,defined $imgsXS && ref $imgsXS eq 'ARRAY' ? @$imgsXS : undef);
		return @$RTN;
	}else{
		$RTN = {
			'imgsL'=>$imgsL,
			'imgsM'=>$imgsM,
			'imgsS'=>$imgsS,
			'imgsXS'=>$imgsXS,

			'sizeL'=>$sizeL,
			'sizeM'=>$sizeM,
			'sizeS'=>$sizeS,
			'sizeXS'=>$sizeXS,

			'sizeStrL'=>$sizeStrL,
			'sizeStrM'=>$sizeStrM,
			'sizeStrS'=>$sizeStrS,
			'sizeStrXS'=>$sizeStrXS,

			'gif_prefix_fmt'=>$gif_prefix_fmt,
			'gif_fmt'=>$gif_fmt,

			'png_prefix_fmt'=>$png_prefix_fmt,
			'png_fmt'=>$png_fmt,
		};
		return $RTN;
	}

}

sub getApachectlPath {
	my $path = &Cwd::abs_path(&rel2abs(&catdir($htdocs_path,'..','..','local','apache','bin','apachectl')));
	return $path;
}

sub Truncated {
	my $v = shift;
	return undef unless(defined $v);
	my $rate = 100000;
	return int($v * $rate + 0.5) / $rate;
}

sub readFile {
	my $path = shift;
#	return undef unless(defined $path && -f $path);
	return undef unless(defined $path);
#	print __LINE__,":\$path=[$path]\n";
	my $rtn;
	my $IN;
	if(open($IN,$path)){
		local $/ = undef;
		$rtn = <$IN>;
		close($IN);
	}
	return $rtn;
}

sub readObjFile {
	my $path = shift;
	return undef unless(defined $path && -f $path && -s $path);

	my $cmd = sprintf(qq{sed -e "/^mtllib/d" "%s" | sed -e "/^#/d" | sed -e "/^ *\$/d" |},$path);
	my $rtn;
	if(open(my $IN,$cmd)){
		local $/ = undef;
		$rtn = <$IN>;
		close($IN);
	}
	return $rtn;
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
	say STDERR __FILE__.':'.__LINE__.':'.$@ if($@);
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
		say STDERR __FILE__.':'.__LINE__.':'.$@;
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
			open(my $IN,$file_path) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
			flock($IN,1);
			$json = &decodeExtensionsJSON(<$IN>);
			close($IN);
		}else{
#			say STDERR __LINE__.':'.$file_path;
			$json = undef;
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
	if(-e $file_path){
		open($OUT,qq|+< $file_path|) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
		flock($OUT,2) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
		seek($OUT, 0, 0) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
		print $OUT &encodeJSON($json,$ext);
		truncate($OUT, tell($OUT)) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
	}
	else{
		open($OUT,qq|> $file_path|) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
		flock($OUT,2) or die __FILE__.':'.__LINE__.':'.$!.':'.$file_path;
		print $OUT &encodeJSON($json,$ext);
	}
	close($OUT);
	chmod 0666,$file_path;
}

1;
