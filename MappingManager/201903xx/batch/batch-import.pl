#!/bp3d/local/perl/bin/perl

$| = 1;

use strict;

use Cwd qw(abs_path);
use File::Basename;
use File::Copy;
use File::Path;
use Archive::Extract;
use JSON::XS;
use Encode;
use Data::Dumper;
use DBD::Pg;
use Spreadsheet::Read;
use Spreadsheet::ParseExcel;
use Spreadsheet::ParseExcel::FmtJapan2;
use Spreadsheet::ParseXLSX;
use Encode;
use Encode::Guess;
use File::Spec::Functions qw(abs2rel rel2abs catdir catfile splitdir tmpdir);



#my $lib_path;
#BEGIN{ $lib_path = dirname(abs_path($0)).qq|/../local/usr/lib/perl|; }
#use lib $lib_path;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;

use BITS::Config;
use BITS::Archive;
use BITS::Obj2Hash;
#use BITS::FileConvert;
use BITS::VTK;
use BITS::Voxel;

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,qw|.pl|);

my $params_file = $ARGV[0];
exit unless(defined $params_file && -e $params_file && -f $params_file && -s $params_file);

my $LOG;
open($LOG,"> $FindBin::Bin/logs/$cgi_name.txt");
select($LOG);
$| = 1;
select(STDOUT);
$| = 1;

my $RTN = &cgi_lib::common::readFileJSON($params_file);
$RTN->{'progress'}->{'value'} = 0;

$SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Error:[$date] KILL THIS SCRIPT!!|);
	$RTN->{'success'} = JSON::XS::false;
	&cgi_lib::common::writeFileJSON($params_file,$RTN);
	exit(1);
}

#my @data_extlist = qw|.xls .xlsx .txt|;
my @data_extlist = qw|.xls .xlsx .txt .owl .obo|;
my @extlist = qw|.tar .tar.gz .tgz .gz .Z .zip .bz2 .tar.bz2 .tbz .lzma .xz .tar.xz .txz|;
push(@extlist,@data_extlist);

&cgi_lib::common::writeFileJSON($params_file,$RTN);

my $upload_file = $RTN->{'file'};

my $dir;
my @FILES;
eval{
	my $files;

	my($upload_name,$upload_dir,$upload_ext) = &File::Basename::fileparse($upload_file,@BITS::Archive::ExtList);
	$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Uncompress: $upload_name$upload_ext|);
	&cgi_lib::common::writeFileJSON($params_file,$RTN);
	$files = &extract($upload_file) if(defined $upload_file && -e $upload_file && -f $upload_file && -s $upload_file);
#	die "ERROR!! TEST";

	$dbh->{'AutoCommit'} = 0;
	$dbh->{'RaiseError'} = 1;
	eval{
		if(defined $files && ref $files eq 'ARRAY'){
			foreach my $file (@$files){
#				&cgi_lib::common::message("\$file=[$file]",$LOG) if($LOG);
				next unless(-e $file);
				my($_name,$_dir,$_ext) = &File::Basename::fileparse($file,@data_extlist);
				next unless(length($_ext));
				$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Read: $_name$_ext|);
				&cgi_lib::common::writeFileJSON($params_file,$RTN);
				if($_ext eq '.txt'){

					my @DATAS = ();
					open(my $IN,$file) or die "$! [$file]";
					while(<$IN>){
						s/\s*$//g;
						push(@DATAS,&g_encoding($_));
					}
					close($IN);

					&reg_records($RTN,\@DATAS,$file);
					undef @DATAS;

				}elsif($_ext eq '.xls'){

					my $oExcel = Spreadsheet::ParseExcel->new;
					my $oFmtJ = Spreadsheet::ParseExcel::FmtJapan2->new(Code => 'utf8'); #sjis、jisなどのコード
					my $oBook = $oExcel->Parse($file, $oFmtJ);
					my($iR, $iC, $oWkS, $oWkC);
					for(my $iSheet=0; $iSheet < $oBook->{SheetCount} ; $iSheet++) {
						$oWkS = $oBook->{Worksheet}[$iSheet];
						my @DATAS = ();
						for(my $iR = $oWkS->{MinRow} ; defined $oWkS->{MaxRow} && $iR <= $oWkS->{MaxRow} ; $iR++) {
							my @cols = ();
							for(my $iC = $oWkS->{MinCol} ; defined $oWkS->{MaxCol} && $iC <= $oWkS->{MaxCol} ; $iC++) {
								$oWkC = $oWkS->{Cells}[$iR][$iC];
								push(@cols,$oWkC ? $oWkC->Value : undef);
							}
							push(@DATAS,join("\t",@cols));
						}

						&reg_records($RTN,\@DATAS,$file);
						undef @DATAS;
					}
				}elsif($_ext eq '.xlsx'){
					my $book = &Spreadsheet::Read::ReadData($file);
					next unless(defined $book);
					my $book_info = shift @$book;
					foreach my $sheet (@$book){
						my $maxrow = $sheet->{'maxrow'};
						my @DATAS = ();
						foreach my $row (1..$maxrow){
							my @cols = &Spreadsheet::Read::cellrow($sheet, $row);
							push(@DATAS,join("\t",@cols));
						}
						&reg_records($RTN,\@DATAS,$file);
						undef @DATAS;
					}
				}elsif($_ext eq '.owl' || $_ext eq '.obo'){
					my $obo_filename;
					if($_ext eq '.owl'){
						$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Convert: $_name$_ext -> $_name.obo|);
						&cgi_lib::common::writeFileJSON($params_file,$RTN);

						$obo_filename = &catfile($_dir,$_name.'.obo');
						my $owl2obo_jar_path = &catfile($cgi_dir,'jar','owl2obo.jar');
						my $java_error_file = &catfile($_dir,$_name.'.obo.err');
						my $java_options = '-Xmx2G';
						my $java_cmd = "java $java_options -jar $owl2obo_jar_path $file $obo_filename 2>$java_error_file";
						my $rtn = &_system($java_cmd);
						if($rtn){
							say STDERR $java_cmd;
							unlink $obo_filename if(-e $obo_filename);
							unlink $java_error_file if(-e $java_error_file && -z $java_error_file);
							die $rtn;
						}
						unlink $java_error_file if(-e $java_error_file);
					}else{
						$obo_filename = $file;
					}
					$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Read: $_name.obo|);
					&cgi_lib::common::writeFileJSON($params_file,$RTN);
					my($FMA_TYPES,$ID2TERMNAME) = &load_obo_file($obo_filename);
					my($FMAID2ID,$ID2FMAID) = &make_fmaid_hash($FMA_TYPES);

					my @DATAS = ();
					if(defined $FMA_TYPES && ref $FMA_TYPES eq 'HASH' && exists $FMA_TYPES->{'Term'} && defined $FMA_TYPES->{'Term'} && ref $FMA_TYPES->{'Term'} eq 'HASH' && defined $FMAID2ID && ref $FMAID2ID eq 'HASH'){

						foreach my $FMAID (sort keys(%$FMAID2ID)){
							my $id = $FMAID2ID->{$FMAID};
							unless(exists $FMA_TYPES->{'Term'}->{$id} && defined $FMA_TYPES->{'Term'}->{$id} && exists $FMA_TYPES->{'Term'}->{$id}->{'FMAID'} && defined $FMA_TYPES->{'Term'}->{$id}->{'FMAID'}){
								next;
							}
							my $FMAID = &trim((keys(%{$FMA_TYPES->{'Term'}->{$id}->{'FMAID'}}))[0]);
							my $Name = &trim((sort keys(%{$FMA_TYPES->{'Term'}->{$id}->{'name'}}))[0]);

							unless(defined $FMAID && length $FMAID && defined $Name && length $Name){
								next;
							}
							next unless($FMAID =~ /^(FMA):*([0-9]+)$/);
							$FMAID = $1.$2;

							my @Synonyms;
							my @Definitions;

							if(exists $FMA_TYPES->{'Term'}->{$id}->{'definition'}){
								foreach my $definition (sort keys(%{$FMA_TYPES->{'Term'}->{$id}->{'definition'}})){
									$definition = &trim($definition);
									push(@Definitions, $definition) if(defined $definition && length $definition);
								}
							}

							if(scalar keys(%{$FMA_TYPES->{'Term'}->{$id}->{'name'}})>1){
								my @names = sort keys(%{$FMA_TYPES->{'Term'}->{$id}->{'name'}});
								shift @names;
								foreach my $name (@names){
									$name = &trim($name);
									push(@Synonyms, $name) if(defined $name && length $name);
								}
							}

							if(exists $FMA_TYPES->{'Term'}->{$id}->{'synonym'}){
								foreach my $synonym (sort keys(%{$FMA_TYPES->{'Term'}->{$id}->{'synonym'}})){
									$synonym = &trim($synonym);
									push(@Synonyms, $synonym) if(defined $synonym && length $synonym);
								}
							}

							if(exists $FMA_TYPES->{'Instance'}->{$id} && exists $FMA_TYPES->{'Instance'}->{$id}->{'property_value'} && exists $FMA_TYPES->{'Instance'}->{$id}->{'property_value'}->{'Synonym'}){
								foreach my $synonym_id (sort keys(%{$FMA_TYPES->{'Instance'}->{$id}->{'property_value'}->{'Synonym'}})){
									if(exists $FMA_TYPES->{'Instance'}->{$synonym_id} && exists $FMA_TYPES->{'Instance'}->{$synonym_id}->{'name'}){
										my @synonyms = grep {$_ ne $synonym_id}keys(%{$FMA_TYPES->{'Instance'}->{$synonym_id}->{'name'}});
										foreach my $synonym (sort @synonyms){
											$synonym = &trim($synonym);
											push(@Synonyms, $synonym) if(defined $synonym && length $synonym);
										}
									}
								}
							}
							my $Synonym = join(';',@Synonyms);
							my $Definition = join(';',@Definitions);
							push @DATAS, join("\t",($FMAID,$Name,$Synonym,$Definition));

							$RTN->{'msg'} = $RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Loding: $_name.obo [|.(scalar @DATAS).']');
							&cgi_lib::common::writeFileJSON($params_file,$RTN);
						}
					}
					&cgi_lib::common::message(join("\n",@DATAS),$LOG) if($LOG);
					if(scalar @DATAS){
						@DATAS = sort {(split(/\t/,$a))[0] cmp (split(/\t/,$b))[0]} @DATAS;
						unshift @DATAS, join("\t",qw/#ID Name Synonym Definition/);
						&reg_records($RTN,\@DATAS,$file);
					}
					undef @DATAS;
				}
				elsif($_ext eq '.json'){
					&reg_json_records($RTN,$file);
				}
			}
			$dbh->commit();
		}
		$RTN->{'success'} = JSON::XS::true;
		$RTN->{'progress'}->{'value'} = 1;
		$RTN->{'progress'}->{'msg'} = 'end';
	};
	if($@){
		$RTN->{'success'} = JSON::XS::false;
		$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($@);
		$RTN->{'progress'}->{'msg'} = 'error';
		&cgi_lib::common::message($RTN->{'msg'},$LOG) if(defined $LOG);
		$dbh->rollback();
	}
	$dbh->{'AutoCommit'} = 1;
	$dbh->{'RaiseError'} = 0;
};
if($@){
	$RTN->{'success'} = JSON::XS::false;
	$RTN->{'msg'} = &cgi_lib::common::decodeUTF8($@);
	$RTN->{'progress'}->{'msg'} = 'error';
}
&cgi_lib::common::writeFileJSON($params_file,$RTN);
exit;

#systemコール
sub _system {
	my $prog = shift;
	system($prog);
	if ($? == -1) {
		return "failed to execute: $!\n";
	}
	elsif ($? & 127) {
		return sprintf("child died with signal %d, %s coredump\n", ($? & 127),  ($? & 128) ? 'with' : 'without');
	}
	elsif ($?) {
		return sprintf("child exited with value %d\n", $? >> 8);
	}
}

sub load_obo_file {
	my $obo_filename = shift;

	my %FMA_TYPES;
	my %ID2TERMNAME;

	open(my $IN, $obo_filename) or die __LINE__.':'."$! [$obo_filename]\n";
	binmode( $IN, ":utf8" );

	my $fma_type;
	my $id;
	while(<$IN>){
		chomp;
		if(/^\[(Term|Typedef|Instance)\]$/) {
			$fma_type = $1;
			undef $id;
			next;
		}
		next unless(defined $fma_type);

		if(/^(id): (.+)$/ ){
			$id = $2;
			$FMA_TYPES{$fma_type}->{$id}->{$1}->{$2} = undef;
			$FMA_TYPES{$fma_type}->{$id}->{'FMA_TYPE'}->{$fma_type} = undef;

			if($id =~ /^fma([0-9]+)$/i){
				my $FMAID = "FMA:$1";
				$FMA_TYPES{$fma_type}->{$id}->{'FMAID'}->{$FMAID} = undef;
			}else{
				$FMA_TYPES{$fma_type}->{$id}->{'FMAID'}->{$id} = undef;
			}
			next;
		}
		next unless(defined $id);
		if(/^([^ ]+?): (.+)$/ ){
			my $key = $1;
			my $val = $2;
			if($key eq 'relationship' && $val =~ /^(\S+?)\s+?(.+)$/){
				my $relationship = $1;
				my $relationship_id = $2;
				$relationship_id = $1 if($relationship_id =~ /^(.+)\s+!\s+.+$/);
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$relationship}->{$relationship_id} = 0 unless(exists $FMA_TYPES{$fma_type}->{$id}->{$key}->{$relationship}->{$relationship_id});
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$relationship}->{$relationship_id}++;
			}elsif($key eq 'property_value' && $val =~ /^(\S+?)\s+?"([^\"]+?)"\s+?(.+)$/){
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$1}->{$2}->{$3} = 0 unless(exists $FMA_TYPES{$fma_type}->{$id}->{$key}->{$1}->{$2}->{$3});
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$1}->{$2}->{$3}++;
			}elsif($key eq 'property_value' && $val =~ /^(\S+?)\s+?(.+)$/){
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$1}->{$2} = 0 unless(exists $FMA_TYPES{$fma_type}->{$id}->{$key}->{$1}->{$2});
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$1}->{$2}++;
			}elsif($key eq 'FMAID'){
				if($val =~ /^[0-9]+$/){
					my $FMAID = "FMA:$val";
					delete $FMA_TYPES{$fma_type}->{$id}->{$key};
					$FMA_TYPES{$fma_type}->{$id}->{$key}->{$FMAID} = undef;
				}
			}else{
				if($fma_type eq 'Term' && $key eq 'name'){
					push(@{$ID2TERMNAME{$id}},$val);
				}
				if($key eq 'def' && $val =~ /^"([^"]+)"/){
					$val = $1;
					$key = 'definition';
				}
				$val = $1 if($key eq 'synonym' && $val =~ /^"([^"]+)"/);
				$val = $1 if($key eq 'is_a' && $val =~ /^(.+)\s+!\s+.+$/);
				if($key eq 'is_a'){
					$val =~ s/\s*$//g;
					$val =~ s/^\s*//g;
				}
				$FMA_TYPES{$fma_type}->{$id}->{$key}->{$val} = undef;
			}
			next;
		}
	}
	close($IN);
	return (\%FMA_TYPES,\%ID2TERMNAME);
}

sub make_fmaid_hash {
	my $FMA_TYPES = shift;
	my %FMAID2ID;
	my %ID2FMAID;
	if(defined $FMA_TYPES && ref $FMA_TYPES eq 'HASH'){
		foreach my $id (sort keys(%{$FMA_TYPES->{'Term'}})){
			my $FMAID;
			if(
				exists $FMA_TYPES->{'Term'}->{$id} && defined $FMA_TYPES->{'Term'}->{$id} && exists $FMA_TYPES->{'Term'}->{$id}->{'FMAID'} && defined $FMA_TYPES->{'Term'}->{$id}->{'FMAID'}
			){
				$FMAID = (keys(%{$FMA_TYPES->{'Term'}->{$id}->{'FMAID'}}))[0];;
				if(defined $FMAID && length $FMAID && $FMAID =~ /^FMA:[0-9]+$/){
					$FMAID2ID{$FMAID} = $id;
					$ID2FMAID{$id} = $FMAID;
				}else{
					$FMAID = undef;
				}
			}
			unless(defined $FMAID && length $FMAID && $FMAID =~ /^FMA:[0-9]+$/){
				delete $FMA_TYPES->{'Term'}->{$id};
			}
		}
	}
	return (\%FMAID2ID,\%ID2FMAID);
}

use File::Find;
my @FIND_FILES;
sub find_process {
	return unless(-e $File::Find::name && -f $File::Find::name);
	push(@FIND_FILES,$File::Find::name);
}

sub extract($;$) {
	my $file = shift;
	my $prefix = shift;
	return undef unless(-e $file);

	if(defined $prefix){
		$dir = $prefix;
	}else{
#		$dir = basename($file,@extlist);
		my($_name,$_dir,$_ext) = &File::Basename::fileparse($file,@extlist);
		$dir = &catdir($_dir,$_name);
	}
	&cgi_lib::common::message("\$file=[$file]",$LOG) if($LOG);
	&cgi_lib::common::message("\$dir=[$dir]",$LOG) if($LOG);
	&File::Path::rmtree($dir) if(-e $dir);
	&File::Path::mkpath($dir,{mode=>0777}) unless(-e $dir);
	chmod 0777,$dir;

	my $ae;
	eval{
		$Archive::Extract::WARN = 0;
		$ae = Archive::Extract->new(archive => $file) if(-e $file);
	};
	if(defined $ae){
		my $to_path = &catdir(&tmpdir(),&File::Basename::basename($dir).qq|_$$|);
		&File::Path::rmtree($to_path) if(-e $to_path);
		&File::Path::mkpath($to_path,{mode=>0777}) unless(-e $to_path);
		chmod 0777,$to_path;
		$ae->extract(to => $to_path);

		my @EXT_FILES = glob &catfile($to_path,'*');
		&File::Copy::move($_,$dir) for(@EXT_FILES);

		@FIND_FILES = ();
		&File::Find::find(\&find_process, $dir);
		push(@FILES,@FIND_FILES);

		&File::Path::rmtree($to_path) if(-e $to_path);
	}else{
		my $to = &catfile($dir,&File::Basename::basename($file));
		&File::Copy::move($file,$to);
		push(@FILES,$to) if(-e $to);
#		push(@FILES,$file) if(-e $file);
	}
	return wantarray ? @FILES : \@FILES;
}

sub g_encoding {
	my $value = shift;
	unless(&utf8::is_utf8($value)){
		# UTF8フラグ がない場合、decode して、UTF8フラグつきにする
		my $guessed_obj = &Encode::Guess::guess_encoding($value, qw/euc-jp shift-jis/);
		$value = $guessed_obj->decode($value) if(ref $guessed_obj);
		undef $guessed_obj;
	}
	return $value;
}

sub reg_records {
	my $params = shift;
	my $datas = shift;
	my $file = shift;
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($params,1),$LOG);
	if(exists $params->{'cmd'} && defined $params->{'cmd'}){
		if($params->{'cmd'} eq 'import-fma-all-list'){
			&reg_records_fma($params,$datas,$file);
		}elsif($params->{'cmd'} eq 'import-upload-all-list'){
			&reg_records_obj($params,$datas);
		}elsif($params->{'cmd'} eq 'import-concept-art-map'){
			&reg_records_obj($params,$datas,$file);
		}else{
			die 'Unknown Cmd ['.$params->{'cmd'}.']';
		}
	}else{
			die 'Undefined Cmd ['.$params->{'cmd'}.']';
	}
}

sub reg_records_fma {
	my $params = shift;
	my $datas = shift;
	my $file = shift;
	return unless(defined $datas && ref $datas eq 'ARRAY');

	my $cdi_entry;
	if(defined $file && -e $file){
		$cdi_entry = (stat($file))[9];
	}else{
		$cdi_entry = time;
	}
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($cdi_entry);
	$cdi_entry = sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

	my $sql_sel = qq|select * from concept_data_info where ci_id=? and cdi_name=?|;
	my $sth_sel = $dbh->prepare($sql_sel) or die $dbh->errstr;

	my %KEYS = (
		cdi_name   => 'ID',
		cdi_name_e => 'Name',
		cdi_name_j => 'Name(J)',
		cdi_name_k => 'Name(K)',
		cdi_name_l => 'Name(L)',
		cdi_syn_e  => 'Synonym',
		cdi_syn_j  => 'Synonym(J)',
		cdi_def_e  => 'Definition',
		cdi_def_j  => 'Definition(J)',
	);
	my $data_pos = 0;
	my $header;
	foreach my $data (@$datas){
		&cgi_lib::common::message(sprintf('[%05d/%05d]',++$data_pos,scalar @$datas),$LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/scalar @$datas,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/|.(scalar @$datas).qq|]|)
		};
		&cgi_lib::common::writeFileJSON($params_file,$RTN);
		$data = &trim($data);
		if(index($data,'#') == 0){
			undef $header;
			$header = &get_header($data);
#	my $header = qq|#ID	Name	Name(L)	Name(J)	Name(K)	Synonym	Synonym(J)	Definition	Definition(J)	TAID	Tree|;
			undef $header unless(defined $header && defined $header->{$KEYS{'cdi_name'}} && (defined $header->{$KEYS{'cdi_name_e'}} || defined $header->{$KEYS{'cdi_name_l'}} || defined $header->{$KEYS{'cdi_name_j'}} || defined $header->{$KEYS{'cdi_name_k'}} || defined $header->{$KEYS{'cdi_syn_e'}} || defined $header->{$KEYS{'cdi_syn_j'}} || defined $header->{$KEYS{'cdi_def_e'}} || defined $header->{$KEYS{'cdi_def_j'}}));
			&cgi_lib::common::message(&cgi_lib::common::encodeJSON($header,1),$LOG) if(defined $header);
		}elsif(defined $header){
			my $hash = &set_data2hash($header,$data);
			unless(defined $hash && defined $hash->{$KEYS{'cdi_name'}}){
				undef $hash;
				next;
			}
			&cgi_lib::common::message(&cgi_lib::common::encodeJSON($hash,1),$LOG);

			$RTN->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Registration: $hash->{$KEYS{'cdi_name'}}|);
			$RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|[$data_pos/|.(scalar @$datas).qq|] $hash->{$KEYS{'cdi_name'}}|);
			&cgi_lib::common::writeFileJSON($params_file,$RTN);

			$sth_sel->execute($params->{'ci_id'},$hash->{$KEYS{'cdi_name'}}) or die $dbh->errstr;
			my $rows_sel = $sth_sel->rows();
			$sth_sel->finish();

			if($rows_sel>0){
				my $sql = qq|update concept_data_info set cdi_delcause=null,cdi_entry=?|;
				my @bind_values = ($cdi_entry);
				my @col;
				foreach my $key (sort keys(%KEYS)){
					next if($key eq 'cdi_name');
					next unless(defined $header->{$KEYS{$key}});
					push(@col,qq|$key=?|);
					push(@bind_values,$hash->{$KEYS{$key}});
				}
				$sql .= ','.join(",",@col) if(scalar @col > 0);
				undef @col;

				$sql .= qq| where ci_id=? and cdi_name=? and |;
				push(@bind_values,$params->{'ci_id'});
				push(@bind_values,$hash->{$KEYS{'cdi_name'}});

				foreach my $key (sort keys(%KEYS)){
					next if($key eq 'cdi_name');
					next unless(defined $header->{$KEYS{$key}});

					if(defined $hash->{$KEYS{$key}}){
						push(@col,qq|$key<>?|);
						push(@bind_values,$hash->{$KEYS{$key}});
					}else{
						push(@col,qq|$key is not null|);
					}
				}
				push(@col,qq|cdi_entry<>?|);
				push(@bind_values,$cdi_entry);
				$sql .= '('.join(" or ",@col).')';
				undef @col;

				my $sth = $dbh->prepare($sql) or die $dbh->errstr;
				$sth->execute(@bind_values) or die $dbh->errstr;
				my $rows = $sth->rows();
				if($rows>0){
					&cgi_lib::common::message("\$rows=[$rows]",$LOG);
					&cgi_lib::common::message("\$sql=[$sql]",$LOG);
					&cgi_lib::common::message("\@bind_values=[".join(",",@bind_values)."]",$LOG);
				}
				$sth->finish();
				undef $sth;
				undef $sql;
				undef @bind_values;
			}else{

				my @bind_values = ($cdi_entry);
				my @column = qw/cdi_entry/;
				my @values = qw/?/;
				foreach my $key (sort keys(%KEYS)){
					next if($key eq 'cdi_name');
					next unless(defined $header->{$KEYS{$key}});
					push(@column,$key);
					push(@values,'?');
					push(@bind_values,$hash->{$KEYS{$key}});
				}
				if(scalar @column > 0){
					my $sql = sprintf(qq|insert into concept_data_info (%s) values (%s)|,join(',',@column),join(',',@values));
					my $sth = $dbh->prepare($sql) or die $dbh->errstr;
					$sth->execute(@bind_values) or die $dbh->errstr;
					my $rows = $sth->rows();
					if($rows>0){
						&cgi_lib::common::message("\$rows=[$rows]",$LOG);
						&cgi_lib::common::message("\$sql=[$sql]",$LOG);
						&cgi_lib::common::message("\@bind_values=[".join(",",@bind_values)."]",$LOG);
					}
					$sth->finish();
					undef $sth;
					undef $sql;
				}
				undef @bind_values;
				undef @column;
				undef @values;
			}
		}
	}
}

sub is_reg_obj_hash {
	my $header = shift;
	my $hash = shift;
	my $KEYS = shift;

	my $rtn = 1;
	$rtn = 0 unless(
		exists $header->{$KEYS->{'cm_entry'}} && defined $header->{$KEYS->{'cm_entry'}} && length $header->{$KEYS->{'cm_entry'}} &&
		exists $hash->{  $KEYS->{'cm_entry'}} && defined $hash->{  $KEYS->{'cm_entry'}} && length $hash->{  $KEYS->{'cm_entry'}} &&
		exists $header->{$KEYS->{'art_filename'}} && defined $header->{$KEYS->{'art_filename'}} && length $header->{$KEYS->{'art_filename'}} &&
		exists $hash->{  $KEYS->{'art_filename'}} && defined $hash->{  $KEYS->{'art_filename'}} && length $hash->{  $KEYS->{'art_filename'}} &&
		exists $header->{$KEYS->{'art_timestamp'}} && defined $header->{$KEYS->{'art_timestamp'}} && length $header->{$KEYS->{'art_timestamp'}} &&
		exists $hash->{  $KEYS->{'art_timestamp'}} && defined $hash->{  $KEYS->{'art_timestamp'}} && length $hash->{  $KEYS->{'art_timestamp'}} &&
		exists $header->{$KEYS->{'art_xmin'}} && defined $header->{$KEYS->{'art_xmin'}} && length $header->{$KEYS->{'art_xmin'}} &&
		exists $hash->{  $KEYS->{'art_xmin'}} && defined $hash->{  $KEYS->{'art_xmin'}} && length $hash->{  $KEYS->{'art_xmin'}} &&
		exists $header->{$KEYS->{'art_xmax'}} && defined $header->{$KEYS->{'art_xmax'}} && length $header->{$KEYS->{'art_xmax'}} &&
		exists $hash->{  $KEYS->{'art_xmax'}} && defined $hash->{  $KEYS->{'art_xmax'}} && length $hash->{  $KEYS->{'art_xmax'}} &&

		exists $header->{$KEYS->{'art_ymin'}} && defined $header->{$KEYS->{'art_ymin'}} && length $header->{$KEYS->{'art_ymin'}} &&
		exists $hash->{  $KEYS->{'art_ymin'}} && defined $hash->{  $KEYS->{'art_ymin'}} && length $hash->{  $KEYS->{'art_ymin'}} &&
		exists $header->{$KEYS->{'art_ymax'}} && defined $header->{$KEYS->{'art_ymax'}} && length $header->{$KEYS->{'art_ymax'}} &&
		exists $hash->{  $KEYS->{'art_ymax'}} && defined $hash->{  $KEYS->{'art_ymax'}} && length $hash->{  $KEYS->{'art_ymax'}} &&

		exists $header->{$KEYS->{'art_zmin'}} && defined $header->{$KEYS->{'art_zmin'}} && length $header->{$KEYS->{'art_zmin'}} &&
		exists $hash->{  $KEYS->{'art_zmin'}} && defined $hash->{  $KEYS->{'art_zmin'}} && length $hash->{  $KEYS->{'art_zmin'}} &&
		exists $header->{$KEYS->{'art_zmax'}} && defined $header->{$KEYS->{'art_zmax'}} && length $header->{$KEYS->{'art_zmax'}} &&
		exists $hash->{  $KEYS->{'art_zmax'}} && defined $hash->{  $KEYS->{'art_zmax'}} && length $hash->{  $KEYS->{'art_zmax'}} &&

		exists $header->{$KEYS->{'art_volume'}} && defined $header->{$KEYS->{'art_volume'}} && length $header->{$KEYS->{'art_volume'}} &&
		exists $hash->{  $KEYS->{'art_volume'}} && defined $hash->{  $KEYS->{'art_volume'}} && length $hash->{  $KEYS->{'art_volume'}} &&
		exists $header->{$KEYS->{'art_data_size'}} && defined $header->{$KEYS->{'art_data_size'}} && length $header->{$KEYS->{'art_data_size'}} &&
		exists $hash->{  $KEYS->{'art_data_size'}} && defined $hash->{  $KEYS->{'art_data_size'}} && length $hash->{  $KEYS->{'art_data_size'}} &&

		exists $header->{$KEYS->{'art_nsn'}} && defined $header->{$KEYS->{'art_nsn'}} && length $header->{$KEYS->{'art_nsn'}} &&

		exists $header->{$KEYS->{'art_entry'}} && defined $header->{$KEYS->{'art_entry'}} && length $header->{$KEYS->{'art_entry'}} &&
		exists $hash->{  $KEYS->{'art_entry'}} && defined $hash->{  $KEYS->{'art_entry'}} && length $hash->{  $KEYS->{'art_entry'}} &&
		exists $header->{$KEYS->{'prefix_char'}} && defined $header->{$KEYS->{'prefix_char'}} && length $header->{$KEYS->{'prefix_char'}} &&
		exists $hash->{  $KEYS->{'prefix_char'}} && defined $hash->{  $KEYS->{'prefix_char'}} && length $hash->{  $KEYS->{'prefix_char'}} &&
		exists $header->{$KEYS->{'art_serial'}} && defined $header->{$KEYS->{'art_serial'}} && length $header->{$KEYS->{'art_serial'}} &&
		exists $hash->{  $KEYS->{'art_serial'}} && defined $hash->{  $KEYS->{'art_serial'}} && length $hash->{  $KEYS->{'art_serial'}} &&
		exists $header->{$KEYS->{'art_md5'}} && defined $header->{$KEYS->{'art_md5'}} && length $header->{$KEYS->{'art_md5'}} &&
		exists $hash->{  $KEYS->{'art_md5'}} && defined $hash->{  $KEYS->{'art_md5'}} && length $hash->{  $KEYS->{'art_md5'}} &&
		exists $header->{$KEYS->{'art_cube_volume'}} && defined $header->{$KEYS->{'art_cube_volume'}} && length $header->{$KEYS->{'art_cube_volume'}} &&
		exists $hash->{  $KEYS->{'art_cube_volume'}} && defined $hash->{  $KEYS->{'art_cube_volume'}} && length $hash->{  $KEYS->{'art_cube_volume'}} &&

		exists $header->{$KEYS->{'arto_id'}} && defined $header->{$KEYS->{'arto_id'}} && length $header->{$KEYS->{'arto_id'}}# &&

#		exists $header->{$KEYS->{'art_folder'}} && defined $header->{$KEYS->{'art_folder'}} && length $header->{$KEYS->{'art_folder'}}
	);
	return $rtn;
}

sub reg_records_obj {
	my $params = shift;
	my $datas = shift;
	my $file = shift;
	return unless(defined $datas && ref $datas eq 'ARRAY');

	my $dir;
	$dir = &File::Basename::dirname($file) if(defined $file && -e $file && -f $file);

	my %KEYS = (
		art_id        => 'FJID',
		cdi_name      => 'FMA_ID',
		art_comment   => 'Comment',
		art_category  => 'Category',
		art_judge     => 'Judge',
		art_class     => 'Class',

		cm_entry      => 'MAP_Timestamp',
		art_filename  => 'OBJ_Filename',
		art_timestamp => 'OBJ_Timestamp',

		art_xmin      => 'Xmin',
		art_xmax      => 'Xmax',
		art_ymin      => 'Ymin',
		art_ymax      => 'Ymax',
		art_zmin      => 'Zmin',
		art_zmax      => 'Zmax',
		art_volume    => 'Volume',
		art_data_size => 'Size',

		art_nsn         => uc('art_nsn'),
		art_entry       => uc('art_entry'),
		prefix_char     => uc('prefix_char'),
		art_serial      => uc('art_serial'),
		art_md5         => uc('art_md5'),
		art_cube_volume => uc('art_cube_volume'),
		arto_id         => uc('arto_id'),

		art_folder      => uc('art_folder'),
	);

	my $sth_id_prefix = $dbh->prepare(qq|select prefix_id from id_prefix where prefix_char=?|) or die $dbh->errstr;
	my $sth_art_file = $dbh->prepare(qq|select art_id,art_serial from art_file where md5(art_data)=md5(?) AND art_data=? AND prefix_id=? order by art_serial|) or die $dbh->errstr;

	my $sql_art_sel =<<SQL;
select
 prefix_id,
 art_serial,
 art_name,
 art_ext,
 art_timestamp
from
 art_file_info
where art_id=?
SQL
	my $sth_art_sel = $dbh->prepare($sql_art_sel) or die $dbh->errstr;

	my $sql_art_mirror_ins =<<SQL;
insert into art_file (
  prefix_id,
  art_id,
  art_serial,
  art_name,
  art_ext,
  art_timestamp,
  art_md5,
  art_data,
  art_data_size,
  art_xmin,
  art_xmax,
  art_ymin,
  art_ymax,
  art_zmin,
  art_zmax,
  art_volume,
  art_cube_volume,
  art_nsn,
  art_mirroring,
  art_entry
) values (
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?,
  ?
)
;
SQL
	my $sth_art_mirror_ins = $dbh->prepare($sql_art_mirror_ins) or die $dbh->errstr;
	my $sth_art_ins = $dbh->prepare($sql_art_mirror_ins) or die $dbh->errstr;


	my $sql_art_upd =<<SQL;
UPDATE art_file SET
  prefix_id=?,
  art_serial=?,
  art_name=?,
  art_ext=?,
  art_timestamp=?,
  art_md5=?,
  art_data=?,
  art_data_size=?,
  art_xmin=?,
  art_xmax=?,
  art_ymin=?,
  art_ymax=?,
  art_zmin=?,
  art_zmax=?,
  art_volume=?,
  art_cube_volume=?,
  art_nsn=?,
  art_mirroring=?,
  art_entry=?
WHERE
  art_id=?
;
SQL
	my $sth_art_upd = $dbh->prepare($sql_art_upd) or die $dbh->errstr;

	my $sth_art_upd2 = $dbh->prepare('UPDATE art_file SET art_delcause=NULL WHERE art_delcause IS NOT NULL AND art_id=?') or die $dbh->errstr;


	my $sql_insert_art_file_info =<<SQL;
INSERT INTO
 art_file_info
 (
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_nsn,
 art_mirroring,
 art_entry,
 art_openid,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume,
 art_cube_volume,
 prefix_id,
 art_serial,
 art_md5
 )
SELECT
 art_id,
 art_name,
 art_ext,
 art_timestamp,
 art_nsn,
 art_mirroring,
 art_entry,
 art_openid,
 art_data_size,
 art_xmin,
 art_xmax,
 art_ymin,
 art_ymax,
 art_zmin,
 art_zmax,
 art_volume,
 art_cube_volume,
 prefix_id,
 art_serial,
 art_md5
FROM
 art_file
WHERE
 art_id IN (SELECT art_id FROM art_file WHERE art_delcause is NULL AND art_id NOT IN (SELECT art_id FROM art_file_info))
SQL

	my $sql_update_art_file_info =<<SQL;
UPDATE ONLY
 art_file_info
SET
 prefix_id = art_file.prefix_id,
 art_serial = art_file.art_serial,
 art_md5 = art_file.art_md5,
 art_data_size = art_file.art_data_size,
 art_xmin = art_file.art_xmin,
 art_xmax = art_file.art_xmax,
 art_ymin = art_file.art_ymin,
 art_ymax = art_file.art_ymax,
 art_zmin = art_file.art_zmin,
 art_zmax = art_file.art_zmax,
 art_volume = art_file.art_volume,
 art_cube_volume = art_file.art_cube_volume,
 art_nsn = art_file.art_nsn,
 art_mirroring = art_file.art_mirroring
FROM
 art_file
WHERE
 art_file_info.art_id = art_file.art_id AND art_file.art_delcause IS NULL;
SQL

	my $sql_cm_sel = qq|select * from concept_art_map where ci_id=? and art_id=?|;
	my $sth_cm_sel = $dbh->prepare($sql_cm_sel) or die $dbh->errstr;

	my $sql_cm_del = qq|delete from concept_art_map where ci_id=? and art_id=?|;
	my $sth_cm_del = $dbh->prepare($sql_cm_del) or die $dbh->errstr;

	my $sql_cm_upd = qq|update concept_art_map set cm_delcause=null,cm_entry=now(),cdi_id=?,cmp_id=?  where ci_id=? and art_id=?|;
	my $sth_cm_upd = $dbh->prepare($sql_cm_upd) or die $dbh->errstr;

	my $sql_cm_ins = qq|insert into concept_art_map (ci_id,art_id,cdi_id,cmp_id) values (?,?,?,?)|;
	my $sth_cm_ins = $dbh->prepare($sql_cm_ins) or die $dbh->errstr;

	my $sth_cm_ins2 = $dbh->prepare(qq|insert into concept_art_map (ci_id,art_id,cdi_id,cmp_id,cm_id,cm_serial) values (?,?,?,?,?,?)|) or die $dbh->errstr;
	my $sth_hcm_sel = $dbh->prepare(qq|select cm_id,cm_serial from history_concept_art_map where ci_id=? and art_id=? order by cm_serial limit 1|) or die $dbh->errstr;

	my $sql_cdi_sel = qq|select cdi_id from concept_data_info where ci_id=? and cdi_name=?|;
	my $sth_cdi_sel = $dbh->prepare($sql_cdi_sel) or die $dbh->errstr;

	my $sql_arti_upd = qq|update art_file_info set art_entry=now(),art_comment=?,art_category=?,art_judge=?,art_class=?,arto_id=?,arto_comment=? where art_id=?|;
	my $sth_arti_upd = $dbh->prepare($sql_arti_upd) or die $dbh->errstr;

	my $sth_artf_sel = $dbh->prepare(qq|select artf_id from art_folder where COALESCE(artf_name,'')=COALESCE(?,'') and COALESCE(artf_pid,0)=COALESCE(?,0)|) or die $dbh->errstr;
	my $sth_artff_sel = $dbh->prepare(qq|select art_id from art_folder_file where art_id=? and artf_id is not null|) or die $dbh->errstr;
	my $sth_artff_del = $dbh->prepare(qq|delete from art_folder_file where art_id=?|) or die $dbh->errstr;
	my $sth_artff_ins = $dbh->prepare(qq|insert into art_folder_file (artf_id,art_id) values (?,?)|) or die $dbh->errstr;
	my %FOLDER_PATH2ID;

	my $sql_cdi_sel_all = qq|select cdi_id,cdi_name from concept_data_info where ci_id=?|;
	my $sth_cdi_sel_all = $dbh->prepare($sql_cdi_sel_all) or die $dbh->errstr;
	my $cdi_id;
	my $cdi_name;
	my %CDI_NAME;
	$sth_cdi_sel_all->execute($params->{'ci_id'}) or die $dbh->errstr;
	$sth_cdi_sel_all->bind_col(1, \$cdi_id, undef);
	$sth_cdi_sel_all->bind_col(2, \$cdi_name, undef);
	while($sth_cdi_sel_all->fetch){
		next unless(defined $cdi_id && defined $cdi_name);
		$CDI_NAME{$cdi_name} = $cdi_id;
	}
	$sth_cdi_sel_all->finish();
	undef $sth_cdi_sel_all;

	my $sql_cmp_sel_all = qq|select cmp_id,cmp_abbr from concept_art_map_part where cmp_use and cmp_delcause is null|;
	my $sth_cmp_sel_all = $dbh->prepare($sql_cmp_sel_all) or die $dbh->errstr;
	my $cmp_id;
	my $cmp_abbr;
	my %CMP_DATA;
	$sth_cmp_sel_all->execute() or die $dbh->errstr;
	$sth_cmp_sel_all->bind_col(1, \$cmp_id, undef);
	$sth_cmp_sel_all->bind_col(2, \$cmp_abbr, undef);
	while($sth_cmp_sel_all->fetch){
		next unless(defined $cmp_id && defined $cmp_abbr);
		$CMP_DATA{$cmp_abbr} = $cmp_id;
	}
	$sth_cmp_sel_all->finish();
	undef $sth_cmp_sel_all;

	my $sql_cm_sel_all = qq|select art_id from concept_art_map where ci_id=?|;
	my $sth_cm_sel_all = $dbh->prepare($sql_cm_sel_all) or die $dbh->errstr;
	my $art_id;
	my %MAPPED_ART_ID;
	$sth_cm_sel_all->execute($params->{'ci_id'}) or die $dbh->errstr;
	$sth_cm_sel_all->bind_col(1, \$art_id, undef);
	while($sth_cm_sel_all->fetch){
		next unless(defined $art_id);
		$MAPPED_ART_ID{$art_id} = 0;
	}
	$sth_cm_sel_all->finish();
	undef $sth_cm_sel_all;

	&cgi_lib::common::message('['.(scalar @$datas).']',$LOG);
	my $data_pos = 0;

	my $dir;
	$dir = &File::Basename::dirname($file) if(defined $file && -e $file && -f $file && -s $file);

	umask(0);
	my $art_path = &catdir($FindBin::Bin,'..','art_file');
	&File::Path::mkpath($art_path,{mode=>0777}) unless(-e $art_path);

	$RTN->{'messages'} = [];

	my %art_id_2_hash;
	my $header;
	my $total = scalar @$datas;
	foreach my $data (@$datas){
		$data_pos++;
#		&cgi_lib::common::message(sprintf('[%05d/%05d]',$data_pos,$total),$LOG);
#		$RTN->{'progress'} = {
#			'value' => $data_pos/scalar @$datas,
#			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total]|)
#		};
#		&cgi_lib::common::writeFileJSON($params_file,$RTN);

		$data = &trim($data);
		next unless(defined $data);
		if(index($data,'#') == 0){
			undef $header;
			$header = &get_header($data);
#	my $header = qq|#FJID	BPID	Use_Map	FMA_ID	FMA_Name	FMA_Synonym	OBJ_Filename	OBJ_Group	OBJ_Timestamp	Comment	Category	Judge	Class|;
			undef $header unless(defined $header && exists $header->{$KEYS{'art_id'}} && (exists $header->{$KEYS{'cdi_name'}} || exists $header->{$KEYS{'art_comment'}} || exists $header->{$KEYS{'art_category'}} || exists $header->{$KEYS{'art_judge'}} || exists $header->{$KEYS{'art_class'}}));
			&cgi_lib::common::message(&cgi_lib::common::encodeJSON($header,1),$LOG) if(defined $header);
		}elsif(defined $header){
			my $hash = &set_data2hash($header,$data);
			unless(defined $hash && exists $hash->{$KEYS{'art_id'}} && defined $hash->{$KEYS{'art_id'}}){
				undef $hash;
				next;
			}
			$art_id_2_hash{$hash->{$KEYS{'art_id'}}} = $hash;
			next;
		}
	}



	#既存のOBJと同じかの確認
	$data_pos = 0;
	$total = (scalar keys %art_id_2_hash) * 3;
	my $exec_ins = 0;
	foreach my $hash_art_id (sort {$a cmp $b} keys %art_id_2_hash){
		my $hash = $art_id_2_hash{$hash_art_id};
		$data_pos++;
		&cgi_lib::common::message(sprintf('[%05d/%05d] %s',$data_pos,$total,$hash_art_id),$LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/$total,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total] $hash_art_id|)
		};
		&cgi_lib::common::writeFileJSON($params_file,$RTN);

		my $art_mirroring = 0;
		my $org_art_id;
		my $mir_art_id;
		if($hash_art_id =~ /^([A-Z]+[0-9]+)M$/){
			$org_art_id = $1;
			$mir_art_id = $hash_art_id;
			$art_mirroring = 1;
		}else{
			$org_art_id = $hash_art_id;
			$mir_art_id = $hash_art_id.'M';
		}

		my $obj_file = &catfile($dir,sprintf('%s.obj',$hash->{$KEYS{'art_id'}}));
		unless(
			-e $obj_file && -f $obj_file && -s $obj_file &&
			&is_reg_obj_hash($header,$hash,\%KEYS)
		){
			&cgi_lib::common::message('情報不足',$LOG);
			next;
		}

		my $art_data = &readObjFile($obj_file);
		unless(defined $art_data && length $art_data){
			&cgi_lib::common::message('データ無し',$LOG);
			next;
		}

		$sth_id_prefix->execute($hash->{$KEYS{'prefix_char'}}) or die $dbh->errstr;
		my $prefix_id;
		my $column_number = 0;
		$sth_id_prefix->bind_col(++$column_number, \$prefix_id, undef);
		$sth_id_prefix->fetch;
		$sth_id_prefix->finish;
		unless(defined $prefix_id && $prefix_id =~ /^[0-9]+$/){
			&cgi_lib::common::message('prefix_id無し',$LOG);
			next;
		}

		my $db_art_id;
		my $db_art_serial;
		$column_number = 0;
		$sth_art_file->execute($art_data,$art_data,$prefix_id) or die $dbh->errstr;
&cgi_lib::common::message('確認:'.$sth_art_file->rows(),$LOG) if(defined $LOG);
		$sth_art_file->bind_col(++$column_number, \$db_art_id, undef);
		$sth_art_file->bind_col(++$column_number, \$db_art_serial, undef);
		while($sth_art_file->fetch){
			last if(defined $db_art_id && $db_art_id eq $hash_art_id);
		}
		$sth_art_file->finish;
		if(defined $db_art_id){
			unless($db_art_id eq $hash_art_id){
				push(@{$RTN->{'messages'}}, qq|[$hash_art_id]<>[$db_art_id] |.&cgi_lib::common::decodeUTF8('登録されているIDが異なります'));
				&cgi_lib::common::message(qq|[$hash_art_id]<>[$db_art_id] |.&cgi_lib::common::decodeUTF8('登録されているIDが異なります'),$LOG);
			}else{
				$sth_art_upd2->execute($hash_art_id) or die $dbh->errstr;
				if($sth_art_upd2->rows()>0){
					$exec_ins++;
				}
				$sth_art_upd2->finish();
				&cgi_lib::common::message('登録済み',$LOG);
			}
		}else{
			&cgi_lib::common::message('未登録',$LOG);

			my($art_name,$art_dir,$art_ext) = &File::Basename::fileparse($hash->{$KEYS{'art_filename'}},qw|.obj|);
			my $art_nsn = exists $hash->{$KEYS{'art_nsn'}} && defined $hash->{$KEYS{'art_nsn'}} ? $hash->{$KEYS{'art_nsn'}} - 0 : 0;


			$column_number = 0;
			$sth_art_sel->execute($hash_art_id) or die $dbh->errstr;
			my $art_id_rows = $sth_art_sel->rows();
			$sth_art_sel->finish();
			if($art_id_rows>0){
=pod
				$sth_art_upd->bind_param(++$column_number, $prefix_id);
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_serial'}});
				$sth_art_upd->bind_param(++$column_number, $art_name);
				$sth_art_upd->bind_param(++$column_number, $art_ext);
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_timestamp'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_md5'}});
				$sth_art_upd->bind_param(++$column_number, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_data_size'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_xmin'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_xmax'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_ymin'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_ymax'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_zmin'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_zmax'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_volume'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_cube_volume'}});
				$sth_art_upd->bind_param(++$column_number, $art_nsn);
				$sth_art_upd->bind_param(++$column_number, $art_mirroring);
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_entry'}});
				$sth_art_upd->bind_param(++$column_number, $hash->{$KEYS{'art_id'}});
				$sth_art_upd->execute() or die $dbh->errstr;
	&cgi_lib::common::message('更新:'.$sth_art_upd->rows(),$LOG) if(defined $LOG);
				$sth_art_upd->finish();
=cut
#				$sth_art_upd2->execute($hash_art_id) or die $dbh->errstr;
#				$sth_art_upd2->finish();
			}else{
				$sth_art_ins->bind_param(++$column_number, $prefix_id);
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_id'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_serial'}});
				$sth_art_ins->bind_param(++$column_number, $art_name);
				$sth_art_ins->bind_param(++$column_number, $art_ext);
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_timestamp'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_md5'}});
				$sth_art_ins->bind_param(++$column_number, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_data_size'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_xmin'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_xmax'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_ymin'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_ymax'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_zmin'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_zmax'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_volume'}});
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_cube_volume'}});
				$sth_art_ins->bind_param(++$column_number, $art_nsn);
				$sth_art_ins->bind_param(++$column_number, $art_mirroring);
				$sth_art_ins->bind_param(++$column_number, $hash->{$KEYS{'art_entry'}});
				$sth_art_ins->execute() or die $dbh->errstr;
	&cgi_lib::common::message('登録:'.$sth_art_ins->rows(),$LOG) if(defined $LOG);
				$sth_art_ins->finish();
			}
			$exec_ins++;
		}
	}
&cgi_lib::common::message('登録数:'.$exec_ins,$LOG) if(defined $LOG);
	if($exec_ins){
		$dbh->do($sql_insert_art_file_info) or die $dbh->errstr;
		$dbh->do($sql_update_art_file_info) or die $dbh->errstr;
	}

	my $exec_folder_file_ins = 0;
	foreach my $hash_art_id (sort {$a cmp $b} keys %art_id_2_hash){
		my $hash = $art_id_2_hash{$hash_art_id};
		$data_pos++;
		&cgi_lib::common::message(sprintf('[%05d/%05d]',$data_pos,$total),$LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/$total,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total]|)
		};
		&cgi_lib::common::writeFileJSON($params_file,$RTN);

#		&cgi_lib::common::message(&cgi_lib::common::encodeJSON($hash,1),$LOG);
#		next;

		$RTN->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Registration: $hash->{$KEYS{'art_id'}}|);
		$RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total] $hash->{$KEYS{'art_id'}}|);
		&cgi_lib::common::writeFileJSON($params_file,$RTN);

		if(defined $header && exists $header->{$KEYS{'art_id'}} && exists $header->{$KEYS{'art_folder'}}){
			$hash->{$KEYS{'art_folder'}} = '/' unless(exists $hash->{$KEYS{'art_folder'}} && defined $hash->{$KEYS{'art_folder'}} && length $hash->{$KEYS{'art_folder'}});
			my @FOLDERS = split(';',$hash->{$KEYS{'art_folder'}});
			my %ARTF_IDS;
			my $column_number = 0;

			$sth_artff_sel->execute($hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
			my $rows_artff_sel = $sth_artff_sel->rows();
			$sth_artff_sel->finish;

			if($rows_artff_sel==0){	#root以外にobjが割り当てられている場合は処理しない
				$sth_artff_del->execute($hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
				$sth_artff_del->finish;
				foreach my $folder (@FOLDERS){
					my $artf_id;
					unless(exists $FOLDER_PATH2ID{$folder}){
						foreach my $artf_name (split('/',$folder)){
							$sth_artf_sel->execute($artf_name,$artf_id) or die $dbh->errstr;
							$column_number = 0;
							$sth_artf_sel->bind_col(++$column_number, \$artf_id, undef);
							$sth_artf_sel->fetch;
							$sth_artf_sel->finish;
						}
						$FOLDER_PATH2ID{$folder} = $artf_id;
					}else{
						$artf_id = $FOLDER_PATH2ID{$folder};
					}
					$ARTF_IDS{$artf_id} = $folder;
				}
				foreach my $artf_id (keys(%ARTF_IDS)){
					my $folder = $ARTF_IDS{$artf_id};
					$artf_id = undef if(length $artf_id == 0);
					&cgi_lib::common::message($folder.':artf_id='.(defined $artf_id ? $artf_id : 'null'),$LOG) if(defined $LOG);
					$sth_artff_ins->execute($artf_id,$hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
					$sth_artff_ins->finish;
					$exec_folder_file_ins++;
				}
			}
		}
	}
	$RTN->{'exec_folder_file_ins'} = $exec_folder_file_ins;

	if($exec_ins){
		#何らかの原因で迷子のOBJをルートに追加する
		my $sth = $dbh->prepare(qq|insert into art_folder_file (art_id) select art_id from art_file_info where art_id not in (select art_id from art_folder_file where artff_delcause is null) and art_delcause is null|) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
&cgi_lib::common::message($sth->rows(),$LOG) if(defined $LOG);
		$sth->finish;
		undef $sth;
	}

#	$data_pos = 0;
#	$total = scalar keys %art_id_2_hash;
	foreach my $hash_art_id (sort {$a cmp $b} keys %art_id_2_hash){
		my $hash = $art_id_2_hash{$hash_art_id};
		$data_pos++;
		&cgi_lib::common::message(sprintf('[%05d/%05d]',$data_pos,$total),$LOG);
		$RTN->{'progress'} = {
			'value' => $data_pos/$total,
			'msg' => &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total]|)
		};
		&cgi_lib::common::writeFileJSON($params_file,$RTN);

#		&cgi_lib::common::message(&cgi_lib::common::encodeJSON($hash,1),$LOG);
#		next;

		$RTN->{'msg'} = &cgi_lib::common::decodeUTF8(qq|Registration: $hash->{$KEYS{'art_id'}}|);
		$RTN->{'progress'}->{'msg'} = &cgi_lib::common::decodeUTF8(qq|[$data_pos/$total] $hash->{$KEYS{'art_id'}}|);
		&cgi_lib::common::writeFileJSON($params_file,$RTN);

		my $org_art_id;
		my $mirror_art_id;
		my $art_mirroring;

		if($hash->{$KEYS{'art_id'}} =~ /^([A-Z]+[0-9]+)M$/){
			$org_art_id = $1;
			$mirror_art_id = $hash->{$KEYS{'art_id'}};
			$art_mirroring = 1;
		}else{
			$art_mirroring = 0;
		}

=pod
		#art_idがtableに存在するか確認
		$sth_art_sel->execute($hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
		my $art_id_rows = $sth_art_sel->rows();
		$sth_art_sel->finish();
		&cgi_lib::common::message("\$art_id_rows=[$art_id_rows]",$LOG);



		$sth_art_sel->execute($art_id) or die $dbh->errstr;
		$art_id_rows = $sth_art_sel->rows();
		$sth_art_sel->finish();
		&cgi_lib::common::message("\$art_id_rows=[$art_id_rows]",$LOG);
		next unless($art_id_rows>0);
=cut

		if(defined $mirror_art_id){

			$sth_art_sel->execute($mirror_art_id) or die $dbh->errstr;
			my $mirror_rows = $sth_art_sel->rows();
			$sth_art_sel->finish();
			$sth_art_sel->execute($art_id) or die $dbh->errstr;
			my $original_rows = $sth_art_sel->rows();
			$sth_art_sel->finish();

			if($mirror_rows==0 && $original_rows==0){
				undef $hash;
				next;
			}elsif($mirror_rows==0 && $original_rows>0){

				$sth_art_sel->execute($art_id) or die $dbh->errstr;
				my $rows = $sth_art_sel->rows();

				&cgi_lib::common::message("\$art_id=[$art_id]",$LOG);
				&cgi_lib::common::message("\$rows=[$rows]",$LOG);

				my($prefix_id,$art_serial,$art_name,$art_ext,$art_timestamp);
				if($rows>0){
					my $column_number = 0;
					$sth_art_sel->bind_col(++$column_number, \$prefix_id, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_serial, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_name, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_ext, undef);
					$sth_art_sel->bind_col(++$column_number, \$art_timestamp, undef);
					$sth_art_sel->fetch;
				}
				$sth_art_sel->finish;
				undef $sth_art_sel;

				if(defined $art_id && defined $art_ext){
					my $org_file_path = &catfile($art_path,qq|$art_id$art_ext|);
					my $mir_file_prefix = &catfile($art_path,$mirror_art_id);
					my $mir_file_path = qq|$mir_file_prefix$art_ext|;
					my $mir_prop = &BITS::VTK::reflection($org_file_path,$mir_file_prefix);
					die __LINE__,qq|:ERROR: reflection()[$mir_file_path]| unless(defined $mir_prop);
					if(
						defined $mir_prop &&
						ref $mir_prop eq 'HASH' &&
						exists $mir_prop->{'bounds'} &&
						defined $mir_prop->{'bounds'} &&
						ref $mir_prop->{'bounds'} eq 'ARRAY' &&
						scalar @{$mir_prop->{'bounds'}} == 6
					){
						my $art_xmin = $mir_prop->{'bounds'}->[0] - 0;
						my $art_xmax = $mir_prop->{'bounds'}->[1] - 0;
						my $art_ymin = $mir_prop->{'bounds'}->[2] - 0;
						my $art_ymax = $mir_prop->{'bounds'}->[3] - 0;
						my $art_zmin = $mir_prop->{'bounds'}->[4] - 0;
						my $art_zmax = $mir_prop->{'bounds'}->[5] - 0;
						my $art_volume = defined $mir_prop->{'volume'} && $mir_prop->{'volume'} > 0 ?  &Truncated($mir_prop->{'volume'} / 1000) : 0;
						my $art_cube_volume = &Truncated(($art_xmax-$art_xmin)*($art_ymax-$art_ymin)*($art_zmax-$art_zmin)/1000);

						if(-e $mir_file_path && -s $mir_file_path){
							my $art_data = &readObjFile($mir_file_path);
							my $art_data_size = length($art_data);
							if($art_data_size>0){
								my $art_md5 = &Digest::MD5::md5_hex($art_data);

								my $param_num = 0;
								$sth_art_mirror_ins->bind_param(++$param_num, $prefix_id);
								$sth_art_mirror_ins->bind_param(++$param_num, $mirror_art_id);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_serial);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_name);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_ext);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_timestamp);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_md5);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_data, { pg_type => DBD::Pg::PG_BYTEA });
								$sth_art_mirror_ins->bind_param(++$param_num, $art_data_size);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_xmin);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_xmax);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_ymin);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_ymax);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_zmin);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_zmax);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_volume);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_cube_volume);
								$sth_art_mirror_ins->bind_param(++$param_num, $art_mirroring);
								$sth_art_mirror_ins->execute() or die $dbh->errstr;
								$mirror_rows = $sth_art_mirror_ins->rows();
								$sth_art_mirror_ins->finish();

								$dbh->do($sql_insert_art_file_info) or die $dbh->errstr;
								$dbh->do($sql_update_art_file_info) or die $dbh->errstr;

								&BITS::Voxel::insVoxelData($dbh,$mirror_art_id,0,$art_data);
							}
						}
					}
				}

			}else{
				#データは既に存在するので何もしない
			}
		}


		#art_idがtableに存在するか確認
		$sth_art_sel->execute($hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
		my $art_id_rows = $sth_art_sel->rows();
		$sth_art_sel->finish();
		&cgi_lib::common::message("\$art_id_rows=[$art_id_rows]",$LOG);
		next unless($art_id_rows>0);




		if(defined $header->{$KEYS{'cdi_name'}}){
			unless(defined $hash->{$KEYS{'cdi_name'}}){

				my @bind_values;
				push(@bind_values,$params->{'ci_id'});
				push(@bind_values,$hash->{$KEYS{'art_id'}});
				$sth_cm_del->execute(@bind_values) or die $dbh->errstr;
				$sth_cm_del->finish();
				undef @bind_values;

			}else{

				my $cdi_id;
				my $cdi_name;
				my $cmp_abbr;
				my $cmp_id;
				if($hash->{$KEYS{'cdi_name'}} =~ /^([A-Z]+[0-9]+)\-*([A-Z]*)$/){
					$cdi_name = $1;
					$cmp_abbr = $2 || '';
				}
				die qq|Unknown $KEYS{'cdi_name'}:[$hash->{$KEYS{'cdi_name'}}]| unless(defined $cdi_name);
				$cmp_id = $CMP_DATA{$cmp_abbr} if(exists $CMP_DATA{$cmp_abbr});
				die qq|Unknown $KEYS{'cdi_name'}:[$hash->{$KEYS{'cdi_name'}}]| unless(defined $cmp_id);
				unless(exists $CDI_NAME{$cdi_name} && defined $CDI_NAME{$cdi_name} && length $CDI_NAME{$cdi_name}){
					$sth_cdi_sel->execute($params->{'ci_id'},$cdi_name) or die $dbh->errstr;
					$sth_cdi_sel->bind_col(1, \$cdi_id, undef);
					$sth_cdi_sel->fetch;
					$sth_cdi_sel->finish();
					&cgi_lib::common::message("\$cdi_id=[$cdi_id]",$LOG);
					die qq|Unknown $KEYS{'cdi_name'}:[$hash->{$KEYS{'cdi_name'}}]| unless(defined $cdi_id);
				}else{
					$cdi_id = $CDI_NAME{$cdi_name};
				}

#					$sth_cm_sel->execute($params->{'ci_id'},$hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
#					my $cm_rows = $sth_cm_sel->rows();
#					$sth_cm_sel->finish();
#					if($cm_rows>0){
				if(exists $MAPPED_ART_ID{$hash->{$KEYS{'art_id'}}}){
					$sth_cm_upd->execute($cdi_id,$cmp_id,$params->{'ci_id'},$hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
#						my $rows = $sth_cm_upd->rows();
#						if($rows>0){
#							&cgi_lib::common::message("\$rows=[$rows]",$LOG);
#						}
					$sth_cm_upd->finish();
					$MAPPED_ART_ID{$hash->{$KEYS{'art_id'}}}++;
				}
				else{
					my $cm_id;
					my $cm_serial;
					$sth_hcm_sel->execute($params->{'ci_id'},$hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
					$sth_hcm_sel->bind_col(1, \$cm_id, undef);
					$sth_hcm_sel->bind_col(2, \$cm_serial, undef);
					$sth_hcm_sel->fetch;
					$sth_hcm_sel->finish();
					if(defined $cm_id && defined $cm_serial){
						$sth_cm_ins2->execute($params->{'ci_id'},$hash->{$KEYS{'art_id'}},$cdi_id,$cmp_id,$cm_id,$cm_serial) or die $dbh->errstr;
#							my $rows = $sth_cm_ins2->rows();
#							if($rows>0){
#								&cgi_lib::common::message("\$rows=[$rows]",$LOG);
#							}
						$sth_cm_ins2->finish();
					}else{
						$sth_cm_ins->execute($params->{'ci_id'},$hash->{$KEYS{'art_id'}},$cdi_id,$cmp_id) or die $dbh->errstr;
#							my $rows = $sth_cm_ins->rows();
#							if($rows>0){
#								&cgi_lib::common::message("\$rows=[$rows]",$LOG);
#							}
						$sth_cm_ins->finish();
					}
					$MAPPED_ART_ID{$hash->{$KEYS{'art_id'}}} = ($MAPPED_ART_ID{$hash->{$KEYS{'art_id'}}} || 0) +1;
				}
			}
		}

		my $arto_id;
		my $arto_comment;
		if(defined $hash->{$KEYS{'arto_id'}} && length $hash->{$KEYS{'arto_id'}}){
			my $arto = &cgi_lib::common::decodeJSON($hash->{$KEYS{'arto_id'}});
			if(defined $arto && ref $arto eq 'HASH'){
				$arto_id = $arto->{'arto_id'};
				$arto_comment = $arto->{'arto_comment'};
			}
		}
		$sth_arti_upd->execute($hash->{$KEYS{'art_comment'}},$hash->{$KEYS{'art_category'}},$hash->{$KEYS{'art_judge'}},$hash->{$KEYS{'art_class'}},$arto_id,$arto_comment,$hash->{$KEYS{'art_id'}}) or die $dbh->errstr;
		$sth_arti_upd->finish();



		undef $hash;
	}

	&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\%MAPPED_ART_ID,1),$LOG);

	my @DELETE_MAPPED_ART_ID = grep {$MAPPED_ART_ID{$_}==0} keys(%MAPPED_ART_ID);
	&cgi_lib::common::message('['.(scalar @DELETE_MAPPED_ART_ID).']',$LOG);
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON(\@DELETE_MAPPED_ART_ID,1),$LOG);
	if(scalar @DELETE_MAPPED_ART_ID){
		my $sql_cm_del_all = sprintf(qq|delete from concept_art_map where ci_id=? and art_id in (%s)|,join(',',map {'?'} @DELETE_MAPPED_ART_ID));;
		my $sth_cm_del_all = $dbh->prepare($sql_cm_del_all) or die $dbh->errstr;
		$sth_cm_del_all->execute($params->{'ci_id'},@DELETE_MAPPED_ART_ID) or die $dbh->errstr;
		$sth_cm_del_all->finish();
		undef $sth_cm_del_all;
	}
}

sub trim {
	my $str = shift;
	return undef unless(defined $str);
	$str =~ s/^\s*//g;
	$str =~ s/\s*$//g;
	$str = undef if(length($str)==0);
	return $str;
}

sub get_header {
	my $data = shift;
	return undef unless(index($data,'#') == 0);

	my $idx = 0;
	my %h = map {
		$_ = &trim($_);
		$_ => $idx++;
	} split(/\t/,substr($data,1));
	return \%h;
}

sub set_data2hash {
	my $header = shift;
	my $data = shift;
	my @d = split(/\t/,$data);
	my $h;
	foreach my $key (keys(%$header)){
		next unless(exists $header->{$key} && defined $header->{$key});
		$h->{$key} = &trim(&cgi_lib::common::decodeUTF8($d[$header->{$key}]));
	}
	return $h;
}

sub reg_json_records {
	my $params = shift;
	my $file = shift;
	&cgi_lib::common::message(&cgi_lib::common::encodeJSON($params,1),$LOG);
	if(exists $params->{'cmd'} && defined $params->{'cmd'}){
		if($params->{'cmd'} eq 'import-fma-all-list'){
			&reg_json_records_fma($params,$file);
		}
		elsif($params->{'cmd'} eq 'import-concept-art-map'){
			&reg_json_records_obj($params,$file);
		}
		else{
			die 'Unknown Cmd ['.$params->{'cmd'}.']';
		}
	}else{
			die 'Undefined Cmd ['.$params->{'cmd'}.']';
	}
}

