#!/opt/services/ag/local/perl/bin/perl

#
# currentset_1903xx用
#
# ID形式変換スクリプト
#

$| = 1;

use strict;
use warnings;
use feature ':5.10';

use Clone;
use FindBin;
use File::Spec::Functions qw(catdir);
use lib $FindBin::Bin,&catdir($FindBin::Bin,'..','cgi_lib'),&catdir($FindBin::Bin,'..','..','cgi_lib'),,&catdir($FindBin::Bin,'..','..','..','..','ag-common','lib');;
use BITS::Config;

use constant {
	DEBUG => 0,
};

use Getopt::Long qw(:config posix_default no_ignore_case gnu_compat);
my $config = {
	db   => exists $ENV{'AG_DB_NAME'} && defined $ENV{'AG_DB_NAME'} ? $ENV{'AG_DB_NAME'} : 'currentset_1903xx',
	host => exists $ENV{'AG_DB_HOST'} && defined $ENV{'AG_DB_HOST'} ? $ENV{'AG_DB_HOST'} : '127.0.0.1',
	port => exists $ENV{'AG_DB_PORT'} && defined $ENV{'AG_DB_PORT'} ? $ENV{'AG_DB_PORT'} : '38300'
};
&Getopt::Long::GetOptions($config,qw/
	db|d=s
	host|h=s
	port|p=s
/) or exit 1;

$ENV{'AG_DB_HOST'} = $config->{'host'};
$ENV{'AG_DB_PORT'} = $config->{'port'};
$ENV{'AG_DB_NAME'} = $config->{'db'};

require "webgl_common.pl";
use cgi_lib::common;

my $dbh = &get_dbh();

my $sql;
my $sth;
my $column_number;

$dbh->{'AutoCommit'} = 0;
$dbh->{'RaiseError'} = 1;
eval{
	my $art_id;
	my $art_timestamp;
	my $art_timestamp_epoch;
	my $art_xcenter;
	my $ART_INFO;
	my $ART2ARTC;
	my $ART2USE;
	my $ART2CDI;
	my $ci_id;
	my $cdi_id;
	my $CM;
	my $cb_id;
	my $cdi_pid;
	my $cdi_lid;
	my $cdi_rid;
	my $CTT_P;
	my $CTT_L;
	my $CTT_R;
	my $cdi_name;
	my $cdi_name_e;
	my $is_user_data;
	my $cm_use;
	my $cm_entry;
	my $cm_entry_epoch;
	my $CDI;
	my $CDI_NAME2ID;
	my $CDI_ID2NAME;

	my $IN;
	my $TRIO_L;
	my $TRIO_R;
	my $TRIO_P;
	my $TRIO;
	my $TRIO_COUNT;

	my $ALL_TRIO;


	my $CDIC_NAME_COUNT;

##ParentID	ParentName	# of IS-A children	# of ParentPartOfParent	#LeftParent	LeftParent	#RightParent	RightParent	LeftID	LeftName	# of LeftPartOfParent	RightID	RightName	# of RightPartOfParent
#FMA:3724	Anatomical orifice	90	0	1	FMA:3724	1	FMA:3724	FMA:13100	Orifice of left principal bronchus	0	FMA:13105	Orifice of right principal bronchus	0	Anatomical orifice	Orifice of left principal bronchus	Orifice of right principal bronchus

	foreach my $fma_xx_xx_xx_trio_bp3d_file (@ARGV){

		open($IN, $fma_xx_xx_xx_trio_bp3d_file) or die "$! [$fma_xx_xx_xx_trio_bp3d_file]";
		while(<$IN>){
			chomp;
			my($cdi_pname,$cdi_pname_e,undef,undef,$cdi_lpname_depth,$cdi_lpname,$cdi_rpname_depth,$cdi_rpname,$cdi_lname,$cdi_lname_e,undef,$cdi_rname,$cdi_rname_e) = split(/\t/);
			next if($cdi_pname =~ /^#/);

			$cdi_pname  = $1.$2 if($cdi_pname =~ /^(FMA):([0-9]+)$/);
#			$cdi_lpname = $1.$2 if($cdi_lpname =~ /^(FMA):([0-9]+)$/);
#			$cdi_rpname = $1.$2 if($cdi_rpname =~ /^(FMA):([0-9]+)$/);
			$cdi_lname  = $1.$2 if($cdi_lname =~ /^(FMA):([0-9]+)$/);
			$cdi_rname  = $1.$2 if($cdi_rname =~ /^(FMA):([0-9]+)$/);

#			unless($cdi_lpname eq $cdi_rpname){
			unless($cdi_lpname_depth eq $cdi_rpname_depth){
	#			&cgi_lib::common::message(sprintf("%s\t%s\t%s", $cdi_pname, $cdi_lname, $cdi_rname));
				next;
			}

			$ALL_TRIO->{$cdi_lname} = $cdi_pname;
			$ALL_TRIO->{$cdi_rname} = $cdi_pname;



			my $chk_cdi_pname_e = lc $cdi_pname_e;

			my $chk_cdi_lname_e = lc $cdi_lname_e;
			$chk_cdi_lname_e =~ s/\bleft\b//g;
			$chk_cdi_lname_e =~ s/\s{2,}/ /g;
			$chk_cdi_lname_e =~ s/^\s+//g;
			$chk_cdi_lname_e =~ s/\s+$//g;

			my $chk_cdi_rname_e = lc $cdi_rname_e;
			$chk_cdi_rname_e =~ s/\bright\b//g;
			$chk_cdi_rname_e =~ s/\s{2,}/ /g;
			$chk_cdi_rname_e =~ s/^\s+//g;
			$chk_cdi_rname_e =~ s/\s+$//g;

			unless($chk_cdi_pname_e eq $chk_cdi_lname_e && $chk_cdi_pname_e eq $chk_cdi_rname_e && $chk_cdi_lname_e eq $chk_cdi_rname_e){
				&cgi_lib::common::message(sprintf("The name is different. [%s][%s][%s][%s][%s][%s]", $cdi_pname, $chk_cdi_pname_e, $cdi_lname, $cdi_lname_e, $cdi_rname, $cdi_rname_e));
				next;
			}


			&cgi_lib::common::message("exists [$cdi_lname]") if(exists $TRIO_L->{$cdi_lname} && $TRIO_L->{$cdi_lname} ne $cdi_pname);
			&cgi_lib::common::message("exists [$cdi_rname]") if(exists $TRIO_R->{$cdi_rname} && $TRIO_R->{$cdi_rname} ne $cdi_pname);
	#		&cgi_lib::common::message("exists [$cdi_pname]") if(exists $TRIO_P->{$cdi_pname});

			$TRIO_L->{$cdi_lname} = $cdi_pname;
			$TRIO_R->{$cdi_rname} = $cdi_pname;
			push(@{$TRIO_P->{$cdi_pname}}, {
				left => $cdi_lname,
				right => $cdi_rname
			});

			$TRIO->{$cdi_lname} = $cdi_pname;
			$TRIO->{$cdi_rname} = $cdi_pname;


			$TRIO_COUNT->{$cdi_lname} = ($TRIO_COUNT->{$cdi_lname} || 0) + 1;
			$TRIO_COUNT->{$cdi_rname} = ($TRIO_COUNT->{$cdi_rname} || 0) + 1;

		}
		close($IN);
	}

	foreach my $cdi_name (keys %$TRIO_COUNT){
		next if($TRIO_COUNT->{$cdi_name}<=1);
		&cgi_lib::common::message(qq|delete $cdi_name|);
		delete $TRIO->{$cdi_name};
		delete $TRIO_L->{$cdi_name} if(exists $TRIO_L->{$cdi_name});
		delete $TRIO_R->{$cdi_name} if(exists $TRIO_R->{$cdi_name});
	}
	foreach my $cdi_pname (keys %$TRIO_P){
		next if(scalar @{$TRIO_P->{$cdi_pname}} == 1);
		foreach my $trio (@{$TRIO_P->{$cdi_pname}}){
			foreach my $key (sort keys(%$trio)){
				my $cdi_name = $trio->{$key};
				&cgi_lib::common::message(qq|delete $cdi_pname -> $key -> $cdi_name|);
				delete $TRIO->{$cdi_name};
				delete $TRIO_L->{$cdi_name} if(exists $TRIO_L->{$cdi_name});
				delete $TRIO_R->{$cdi_name} if(exists $TRIO_R->{$cdi_name});
			}
		}
	}

#	&cgi_lib::common::message($TRIO);
#	&cgi_lib::common::message($TRIO_L);
#	exit;


	$dbh->do(q|UPDATE concept_data_info SET cp_id=0,cl_id=1 where cdi_name ~ E'\-L$'|) or die $dbh->errstr;
	$dbh->do(q|UPDATE concept_data_info SET cp_id=0,cl_id=2 where cdi_name ~ E'\-R$'|) or die $dbh->errstr;
	$dbh->do(q|UPDATE concept_data_info SET cp_id=cmp_id where cmp_id>2|) or die $dbh->errstr;
	$dbh->do(q|UPDATE concept_data_info SET cl_id=3 where cl_id=0 AND cdi_name ~ E'\-'|) or die $dbh->errstr;
#	$dbh->do(q|UPDATE concept_data_info SET cdi_name=regexp_replace(cdi_name,E'^(FMA[0-9]+)\-([A-Z])$',E'\\1\\2-U') where cp_id<>0 AND cdi_name ~ E'\-'|) or die $dbh->errstr;







=pod
	$sql = qq|SELECT ci_id,cdi_id,cdi_name,cdi_name_e,is_user_data FROM concept_data_info WHERE is_user_data|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	$sth->bind_col(++$column_number, \$cdi_name_e, undef);
	$sth->bind_col(++$column_number, \$is_user_data, undef);
	while($sth->fetch){
		say STDERR sprintf("%d\t%s\t%s", $cdi_id, $cdi_name, $cdi_name_e);
	}
	$sth->finish;
	undef $sth;

	exit;
=cut


	$sql = qq|SELECT ci_id,cdi_id,cdi_name,cdi_name_e,is_user_data FROM concept_data_info|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	$sth->bind_col(++$column_number, \$cdi_name_e, undef);
	$sth->bind_col(++$column_number, \$is_user_data, undef);
	while($sth->fetch){

		$CDI_NAME2ID->{$cdi_name} = $cdi_id;
		$CDI_ID2NAME->{$cdi_id} = $cdi_name;
	}
	$sth->finish;
	undef $sth;












	$dbh->do(q|ALTER TABLE art_file_info DISABLE TRIGGER trig_after_art_file_info|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE art_file_info DISABLE TRIGGER trig_before_art_file_info|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE history_art_file_info DISABLE TRIGGER trig_before_history_art_file_info|) or die $dbh->errstr;

	$dbh->do(q|ALTER TABLE concept_art_map DISABLE TRIGGER trig_after_concept_art_map|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE concept_art_map DISABLE TRIGGER trig_before_concept_art_map|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE history_concept_art_map DISABLE TRIGGER trig_before_history_concept_art_map|) or die $dbh->errstr;



	$sql = qq|SELECT concept_art_map.art_id,ci_id,cdi_id,cm_entry,EXTRACT(EPOCH FROM cm_entry),cm_use FROM concept_art_map LEFT JOIN art_file_info ON art_file_info.art_id=concept_art_map.art_id ORDER BY art_file_info.art_timestamp,concept_art_map.cm_entry|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cm_entry, undef);
	$sth->bind_col(++$column_number, \$cm_entry_epoch, undef);
	$sth->bind_col(++$column_number, \$cm_use, undef);
	while($sth->fetch){
		$cm_use = (defined $cm_use && $cm_use-0) ? JSON::XS::true : JSON::XS::false;
		if($cm_use && defined $CM && ref $CM eq 'HASH' && exists $CM->{$ci_id} && exists $CM->{$ci_id}->{$cdi_id}){
			foreach my $art_id (keys(%{$CM->{$ci_id}->{$cdi_id}})){
				$CM->{$ci_id}->{$cdi_id}->{$art_id}->{'is_use'} = JSON::XS::false;
				$ART2USE->{$art_id} = JSON::XS::false;
			}
		}
		$CM->{$ci_id}->{$cdi_id}->{$art_id} = {
			cm_entry => $cm_entry,
			cm_entry_epoch => $cm_entry_epoch - 0,
			cm_use => $cm_use,
			is_use => $cm_use
		};
		$ART2USE->{$art_id} = $cm_use unless(defined $ART2USE && ref $ART2USE eq 'HASH' && exists $ART2USE->{$art_id} && defined $ART2USE->{$art_id} && $ART2USE->{$art_id});
		$ART2CDI->{$art_id} = $CDI_ID2NAME->{$cdi_id} if(exists $CDI_ID2NAME->{$cdi_id});
	}
	$sth->finish;
	undef $sth;

#	my @ART_IDS = keys(%$ART2USE);
#	$sql = sprintf(qq|SELECT art_id,art_timestamp,EXTRACT(EPOCH FROM art_timestamp),to_number(to_char((art_xmax+art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter FROM art_file_info WHERE art_id in (%s)|,join(',', map {'?'} @ART_IDS));
	$sql = qq|SELECT art_id,art_timestamp,EXTRACT(EPOCH FROM art_timestamp),to_number(to_char((art_xmax+art_xmin)/2,'FM99990D0000'),'99990D0000S') as art_xcenter FROM art_file_info|;
#	$sql = qq|SELECT art_id,art_timestamp,(art_xmax+art_xmin)/2 as art_xcenter FROM art_file_info|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
#	$sth->execute(@ART_IDS) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$art_timestamp, undef);
	$sth->bind_col(++$column_number, \$art_timestamp_epoch, undef);
	$sth->bind_col(++$column_number, \$art_xcenter, undef);
	while($sth->fetch){

#		next unless(exists $ART2USE->{$art_id});	#マッピングされていないOBJは無視する為

		$ART_INFO->{$art_id} = {
			art_timestamp       => $art_timestamp,
			art_timestamp_epoch => $art_timestamp_epoch - 0,
			art_xcenter         => $art_xcenter - 0,
#			is_use              => exists $ART2USE->{$art_id} ? JSON::XS::true : JSON::XS::false
			is_use              => exists $ART2USE->{$art_id} ? $ART2USE->{$art_id} : JSON::XS::false,
			is_mapped           => exists $ART2USE->{$art_id} ? JSON::XS::true : JSON::XS::false
		}
	}
	$sth->finish;
	undef $sth;

	if(defined $ART_INFO && ref $ART_INFO eq 'HASH'){
		foreach my $art_id (grep {$_ =~ /^[A-Z]+[0-9]+$/} keys(%$ART_INFO)){
#			&cgi_lib::common::message($art_id);
			next unless($art_id =~ /^[A-Z]+[0-9]+$/);
			my $mirror_art_id = $art_id.'M';
#			if(exists $ART_INFO->{$mirror_art_id} && defined $ART_INFO->{$mirror_art_id} && $ART_INFO->{$art_id}->{'is_use'} == $ART_INFO->{$mirror_art_id}->{'is_use'}){
#			if($ART_INFO->{$art_id}->{'is_mapped'} && exists $ART_INFO->{$mirror_art_id} && defined $ART_INFO->{$mirror_art_id} && $ART_INFO->{$mirror_art_id}->{'is_mapped'}){
#			if(exists $ART_INFO->{$mirror_art_id} && defined $ART_INFO->{$mirror_art_id} && ($ART_INFO->{$art_id}->{'is_mapped'} || $ART_INFO->{$mirror_art_id}->{'is_mapped'})){	#どちらかが使用されていれば、変換対象とする
#			if(exists $ART_INFO->{$mirror_art_id} && defined $ART_INFO->{$mirror_art_id}){
			if(
						$ART_INFO->{$art_id}->{'is_mapped'}
				&&	$ART_INFO->{$art_id}->{'is_use'}
				&&	exists	$ART_INFO->{$mirror_art_id}
				&&	defined	$ART_INFO->{$mirror_art_id}
				&&	ref			$ART_INFO->{$mirror_art_id} eq 'HASH'
				&&	$ART_INFO->{$mirror_art_id}->{'is_mapped'}
				&&	$ART_INFO->{$mirror_art_id}->{'is_use'}
			){
				if($ART_INFO->{$art_id}->{'art_xcenter'}>=0){

					$ART2ARTC->{$art_id} = {
						artl_id             => 1,
						artc_id             => $art_id.'L',
						art_timestamp       => $ART_INFO->{$art_id}->{'art_timestamp'},
						art_timestamp_epoch => $ART_INFO->{$art_id}->{'art_timestamp_epoch'},
						art_xcenter         => $ART_INFO->{$art_id}->{'art_xcenter'},
						is_use              => $ART_INFO->{$art_id}->{'is_use'},
						is_mapped           => $ART_INFO->{$art_id}->{'is_mapped'},
					};
					$ART2ARTC->{$mirror_art_id} = {
						artl_id             => 2,
						artc_id             => $art_id.'R',
						art_timestamp       => $ART_INFO->{$mirror_art_id}->{'art_timestamp'},
						art_timestamp_epoch => $ART_INFO->{$mirror_art_id}->{'art_timestamp_epoch'},
						art_xcenter         => $ART_INFO->{$mirror_art_id}->{'art_xcenter'},
						is_use              => $ART_INFO->{$mirror_art_id}->{'is_use'},
						is_mapped           => $ART_INFO->{$mirror_art_id}->{'is_mapped'},
					};
				}
				else{

					$ART2ARTC->{$art_id} = {
						artl_id             => 2,
						artc_id             => $art_id.'R',
						art_timestamp       => $ART_INFO->{$art_id}->{'art_timestamp'},
						art_timestamp_epoch => $ART_INFO->{$art_id}->{'art_timestamp_epoch'},
						art_xcenter         => $ART_INFO->{$art_id}->{'art_xcenter'},
						is_use              => $ART_INFO->{$art_id}->{'is_use'},
						is_mapped           => $ART_INFO->{$art_id}->{'is_mapped'},
					};
					$ART2ARTC->{$mirror_art_id} = {
						artl_id             => 1,
						artc_id             => $art_id.'L',
						art_timestamp       => $ART_INFO->{$mirror_art_id}->{'art_timestamp'},
						art_timestamp_epoch => $ART_INFO->{$mirror_art_id}->{'art_timestamp_epoch'},
						art_xcenter         => $ART_INFO->{$mirror_art_id}->{'art_xcenter'},
						is_use              => $ART_INFO->{$mirror_art_id}->{'is_use'},
						is_mapped           => $ART_INFO->{$mirror_art_id}->{'is_mapped'},
					};
				}
			}
#			elsif($ART_INFO->{$art_id}->{'is_mapped'}){
			elsif($ART_INFO->{$art_id}->{'is_mapped'} && $ART_INFO->{$art_id}->{'is_use'}){
				$ART2ARTC->{$art_id} = {
					artl_id             => 3,
					artc_id             => $art_id.'U',
					art_timestamp       => $ART_INFO->{$art_id}->{'art_timestamp'},
					art_timestamp_epoch => $ART_INFO->{$art_id}->{'art_timestamp_epoch'},
					art_xcenter         => $ART_INFO->{$art_id}->{'art_xcenter'},
					is_use              => $ART_INFO->{$art_id}->{'is_use'},
					is_mapped           => $ART_INFO->{$art_id}->{'is_mapped'},
				};
			}
#			elsif(exists $ART_INFO->{$mirror_art_id} && defined $ART_INFO->{$mirror_art_id} && $ART_INFO->{$mirror_art_id}->{'is_mapped'}){
			elsif(exists $ART_INFO->{$mirror_art_id} && defined $ART_INFO->{$mirror_art_id} && $ART_INFO->{$mirror_art_id}->{'is_mapped'} && $ART_INFO->{$mirror_art_id}->{'is_use'}){
				$ART2ARTC->{$mirror_art_id} = {
					artl_id             => 3,
					artc_id             => $art_id.'U',
					art_timestamp       => $ART_INFO->{$mirror_art_id}->{'art_timestamp'},
					art_timestamp_epoch => $ART_INFO->{$mirror_art_id}->{'art_timestamp_epoch'},
					art_xcenter         => $ART_INFO->{$mirror_art_id}->{'art_xcenter'},
					is_use              => $ART_INFO->{$mirror_art_id}->{'is_use'},
					is_mapped           => $ART_INFO->{$mirror_art_id}->{'is_mapped'},
				};
			}
		}
#		&cgi_lib::common::message($ART2ARTC);
#		die __LINE__;

		#ミラー側から
		foreach my $mirror_art_id (grep {$_ =~ /^[A-Z]+[0-9]+M$/} keys(%$ART_INFO)){
			next unless($mirror_art_id =~ /^([A-Z]+[0-9]+)M$/);
			next unless($ART_INFO->{$mirror_art_id}->{'is_mapped'});
#			next unless($ART_INFO->{$mirror_art_id}->{'is_mapped'} && $ART_INFO->{$mirror_art_id}->{'is_use'});

			my $art_id = $1;
			next if(exists $ART2ARTC->{$art_id});

			&cgi_lib::common::message($mirror_art_id);

			$ART2ARTC->{$mirror_art_id} = {
				artl_id             => 3,
				artc_id             => $art_id.'U',
				art_timestamp       => $ART_INFO->{$mirror_art_id}->{'art_timestamp'},
				art_timestamp_epoch => $ART_INFO->{$mirror_art_id}->{'art_timestamp_epoch'},
				art_xcenter         => $ART_INFO->{$mirror_art_id}->{'art_xcenter'},
				is_use              => $ART_INFO->{$mirror_art_id}->{'is_use'},
				is_mapped           => $ART_INFO->{$mirror_art_id}->{'is_mapped'},
			};
		}

#		&cgi_lib::common::message($ART2ARTC);
#		exit;

		if(defined $ART2ARTC && ref $ART2ARTC eq 'HASH'){
#			&cgi_lib::common::message($ART2ARTC);
			my @TABLES;
			if(DEBUG){
				@TABLES = qw/art_file_info/;
			}
			else{
				@TABLES = qw/art_file_info history_art_file_info/;
			}
			foreach my $table (@TABLES){
				$sql = qq|UPDATE $table SET artl_id=?,artc_id=? WHERE art_id=?|;
				$sth = $dbh->prepare($sql) or die $dbh->errstr;

				foreach my $art_id (keys(%$ART2ARTC)){
#					&cgi_lib::common::message(sprintf("%s\t%s\t%s",$ART2ARTC->{$art_id}->{'artl_id'}, $ART2ARTC->{$art_id}->{'artc_id'}, $art_id));
					$sth->execute($ART2ARTC->{$art_id}->{'artl_id'}, $ART2ARTC->{$art_id}->{'artc_id'}, $art_id) or die $dbh->errstr;
					my $rows = $sth->rows;
					$sth->finish;
					if($rows >= 1){
#						&cgi_lib::common::message("OK [$rows][$table]");
					}
					else{
						&cgi_lib::common::message("NG [$rows][$table]");
						die __LINE__;
					}
				}
				undef $sth;
			}
		}
	}

#	&cgi_lib::common::message($ART2ARTC);
#	exit;

	$sql = qq|SELECT ci_id,cdi_id,cdi_name,cdi_name_e,is_user_data FROM concept_data_info|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	$sth->bind_col(++$column_number, \$cdi_name_e, undef);
	$sth->bind_col(++$column_number, \$is_user_data, undef);
	while($sth->fetch){

		$CDI_NAME2ID->{$cdi_name} = $cdi_id;
		$CDI_ID2NAME->{$cdi_id} = $cdi_name;

		if(exists $CM->{$ci_id} && defined $CM->{$ci_id} && ref $CM->{$ci_id} eq 'HASH' && exists $CM->{$ci_id}->{$cdi_id} && defined $CM->{$ci_id}->{$cdi_id} && ref $CM->{$ci_id}->{$cdi_id} eq 'HASH'){
			foreach my $art_id (keys(%{$CM->{$ci_id}->{$cdi_id}})){
#				unless($CM->{$ci_id}->{$cdi_id}->{$art_id}){
				unless(exists $CM->{$ci_id}->{$cdi_id}->{$art_id} && defined $CM->{$ci_id}->{$cdi_id}->{$art_id}){
					&cgi_lib::common::message(sprintf("%d\t%d\t%s",$ci_id,$cdi_id,$art_id));
					next;
				}
				unless(exists $ART2ARTC->{$art_id}){
					&cgi_lib::common::message(sprintf("%d\t%d\t%s",$ci_id,$cdi_id,$art_id));
					next;
				}
#				&cgi_lib::common::message(sprintf("%d\t%d\t%s",$ci_id,$cdi_id,$art_id));

				my $artl_id             = $ART2ARTC->{$art_id}->{'artl_id'};
				my $artc_id             = $ART2ARTC->{$art_id}->{'artc_id'};
				my $art_timestamp       = $ART2ARTC->{$art_id}->{'art_timestamp'};
				my $art_timestamp_epoch = $ART2ARTC->{$art_id}->{'art_timestamp_epoch'};
				my $art_xcenter         = $ART2ARTC->{$art_id}->{'art_xcenter'};
				my $is_use              = $ART2ARTC->{$art_id}->{'is_use'};
				my $is_mapped           = $ART2ARTC->{$art_id}->{'is_mapped'};

				my $cm_entry            = $CM->{$ci_id}->{$cdi_id}->{$art_id}->{'cm_entry'};
				my $cm_entry_epoch      = $CM->{$ci_id}->{$cdi_id}->{$art_id}->{'cm_entry_epoch'};
				my $cm_use              = $CM->{$ci_id}->{$cdi_id}->{$art_id}->{'cm_use'};

				unless(exists $CDI->{$ci_id} && defined $CDI->{$ci_id} && ref $CDI->{$ci_id} eq 'HASH' && exists $CDI->{$ci_id}->{$cdi_id} && defined $CDI->{$ci_id}->{$cdi_id} && ref $CDI->{$ci_id}->{$cdi_id} eq 'HASH'){
					$CDI->{$ci_id}->{$cdi_id} = {
						is_user_data => $is_user_data ? JSON::XS::true : JSON::XS::false,
  					ci_id        => $ci_id - 0,
						cdi_id       => $cdi_id - 0,
						cdi_name     => $cdi_name,
						cdi_name_e   => $cdi_name_e,
						art_id       => undef,
						'#art'       => 0,
						art          => {}
					};
				}
				$CDI->{$ci_id}->{$cdi_id}->{'art'}->{$art_id} = {
					art_id              => $art_id,
					artl_id             => $artl_id,
					artc_id             => $artc_id,
					art_timestamp       => $art_timestamp,
					art_timestamp_epoch => $art_timestamp_epoch,
					art_xcenter         => $art_xcenter,
					is_use              => $is_use,
					is_mapped           => $is_mapped,

					cm_entry            => $cm_entry,
					cm_entry_epoch      => $cm_entry_epoch,
					cm_use              => $cm_use,
				};
				$CDI->{$ci_id}->{$cdi_id}->{'#art'} = scalar keys(%{$CDI->{$ci_id}->{$cdi_id}->{'art'}});
				if($is_mapped){
					unless(exists $CDI->{$ci_id}->{$cdi_id}->{'art_id'} && defined $CDI->{$ci_id}->{$cdi_id}->{'art_id'}){
						$CDI->{$ci_id}->{$cdi_id}->{'art_id'} = $art_id;
					}
					elsif($art_timestamp_epoch>$ART2ARTC->{$CDI->{$ci_id}->{$cdi_id}->{'art_id'}}->{'art_timestamp_epoch'}){
						$CDI->{$ci_id}->{$cdi_id}->{'art_id'} = $art_id;
					}
				}
			}
		}
		else{
			if(0 && $is_user_data){
				$CDI->{$ci_id}->{$cdi_id} = undef;	#削除対象
			}
			else{
				#マップされていないFMA
				$CDI->{$ci_id}->{$cdi_id} = {
					is_user_data => $is_user_data ? JSON::XS::true : JSON::XS::false,
					ci_id        => $ci_id - 0,
					cdi_id       => $cdi_id - 0,
					cdi_name     => $cdi_name,
					cdi_name_e   => $cdi_name_e,
					art_id       => undef,
					'#art'       => 0,
					art          => undef
				};
			}
		}
	}
	$sth->finish;
	undef $sth;

#	&cgi_lib::common::message($CDI);
#	die __LINE__;

	my @HEADER;
	my @OUT;

	foreach $ci_id (sort {$a <=> $b} keys(%$CDI)){
		foreach $cdi_id (sort {$a <=> $b} keys(%{$CDI->{$ci_id}})){
			next unless(exists $CDI->{$ci_id}->{$cdi_id} && defined $CDI->{$ci_id}->{$cdi_id} && ref $CDI->{$ci_id}->{$cdi_id} eq 'HASH');

			my $cdi_name = $CDI->{$ci_id}->{$cdi_id}->{'cdi_name'};
			my $art_id   = $CDI->{$ci_id}->{$cdi_id}->{'art_id'};

=pod
			if($cdi_name =~ /^(FMA[0-9]+)\-([LR])$/){
				my $a = $1;
				my $b = $2;
				my $reverse_cdi_name = $a . '-' . ($b eq 'L' ? 'R' : 'L');
				my $reverse_cdi_id = $CDI_NAME2ID->{$reverse_cdi_name};

				if(exists $CDI->{$ci_id}->{$reverse_cdi_id} && defined $CDI->{$ci_id}->{$reverse_cdi_id} && ref $CDI->{$ci_id}->{$reverse_cdi_id} eq 'HASH'){
					$TRIO->{$cdi_name} = $a;
					$TRIO->{$reverse_cdi_name} = $a;
				}
			}
=cut
			my $cdi_pname;
			my $cdi_cname;
			my $sub_name = '';
			my $lat_name;
			if($cdi_name =~ /^(FMA[0-9]+)\-([LR])$/){
				$cdi_pname = $1;
				$lat_name = $2;
			}
			else{
				if($cdi_name =~ /^(FMA[0-9]+)\-([A-Z])$/){
					$cdi_pname = $1;
					$sub_name = $2
				}
				else{
					$cdi_pname = $cdi_name;
				}
				$lat_name = 'U';
			}
#			$cdi_pname = $TRIO->{$cdi_pname} if(defined $TRIO && ref $TRIO eq 'HASH' && exists $TRIO->{$cdi_pname} && defined $TRIO->{$cdi_pname});
			my $exists_trio = 0;
			if(defined $TRIO && ref $TRIO eq 'HASH' && exists $TRIO->{$cdi_pname} && defined $TRIO->{$cdi_pname}){
				$cdi_cname = $cdi_pname;
				$cdi_pname = $TRIO->{$cdi_pname};
				$exists_trio = 1;
			}

#			$sub_name = $1 if($cdi_name =~ /^FMA[0-9]+\-([^LR])$/);


#			say STDERR sprintf("%s -> %s",$cdi_name,$cdi_pname) unless($cdi_pname eq $cdi_name);
#			say STDERR sprintf("%s -> %s",$cdi_name,$cdi_pname);
#			next;


			next unless(exists $CDI->{$ci_id}->{$cdi_id}->{'art'} && defined $CDI->{$ci_id}->{$cdi_id}->{'art'} && ref $CDI->{$ci_id}->{$cdi_id}->{'art'} eq 'HASH');
			next unless(defined $art_id);
			next unless(exists $CDI->{$ci_id}->{$cdi_id}->{'art'}->{$art_id} && defined $CDI->{$ci_id}->{$cdi_id}->{'art'}->{$art_id} && ref $CDI->{$ci_id}->{$cdi_id}->{'art'}->{$art_id} eq 'HASH');

#			say STDERR sprintf("%s -> %s",$cdi_name,$cdi_pname);
#			next;

			#foreach my $art_id (keys(%{$CDI->{$ci_id}->{$cdi_id}->{'art'}})){
				my $art = $CDI->{$ci_id}->{$cdi_id}->{'art'}->{$art_id};



#				my $artl_id = $art->{'artl_id'};
				my $artc_id = $art->{'artc_id'};
#				my $art_xcenter = $art->{'art_xcenter'};

				my $is_user_data = $CDI->{$ci_id}->{$cdi_id}->{'is_user_data'};

#				my $cdi_name = $CDI->{$ci_id}->{$cdi_id}->{'cdi_name'};
				my $cdi_name_e = $CDI->{$ci_id}->{$cdi_id}->{'cdi_name_e'};

				my $cdic_name;

				if(defined $artc_id){
					if($artc_id =~ /[LR]$/){
						if($artc_id =~ /L$/){
							$cdic_name = $cdi_pname.$sub_name.'-L';
						}
						elsif($artc_id =~ /R$/){
							$cdic_name = $cdi_pname.$sub_name.'-R';
						}
						unless($exists_trio){
							if(defined $cdic_name){
								&cgi_lib::common::message(sprintf("[%s][%s]->[%s]",$cdi_name,$artc_id,$cdic_name));
							}
							else{
								&cgi_lib::common::message(sprintf("[%s][%s]",$cdi_name,$artc_id));
							}
						}
					}
					elsif($artc_id =~ /U$/){
						if(defined $cdi_cname && exists $TRIO_L->{$cdi_cname}){
							$cdic_name = $cdi_pname.$sub_name.'-L';
						}
						elsif(defined $cdi_cname && exists $TRIO_R->{$cdi_cname}){
							$cdic_name = $cdi_pname.$sub_name.'-R';
						}
						else{
							$cdic_name = $cdi_pname.$sub_name.'-'.$lat_name;
						}
					}
				}

				$CDI->{$ci_id}->{$cdi_id}->{'cdic_name'} = $cdic_name;
				if(defined $cdic_name){

					if($cdic_name =~ /^(FMA[0-9]+)/){
						my $temp_cdi_name = $1;
						my $temp_cdi_id = exists $CDI_NAME2ID->{$temp_cdi_name} ? $CDI_NAME2ID->{$temp_cdi_name} : undef;
						if(defined $temp_cdi_id){
							$CDI->{$ci_id}->{$cdi_id}->{'cdic_name_e'} = $CDI->{$ci_id}->{$temp_cdi_id}->{'cdi_name_e'};
						}
					}


					if(defined $CDIC_NAME_COUNT && ref $CDIC_NAME_COUNT eq 'HASH' && exists $CDIC_NAME_COUNT->{$cdic_name}){
						$CDIC_NAME_COUNT->{$cdic_name}++;
					}
					else{
						$CDIC_NAME_COUNT->{$cdic_name} = 1;
					}

				}
				else{
					&cgi_lib::common::message(sprintf("%d\t%s\t%s\t%s\t%s", $cdi_id, $cdi_name, $cdi_name_e, $art_id, $artc_id));
				}

#			}
		}
	}

#	&cgi_lib::common::message($CDI);
#	die __LINE__;

#	&cgi_lib::common::message($CDI);
#	foreach my $cdic_name (sort {$CDIC_NAME_COUNT->{$b} <=> $CDIC_NAME_COUNT->{$a}} sort keys(%$CDIC_NAME_COUNT)){
#		&cgi_lib::common::message(sprintf("%s : %d", $cdic_name, $CDIC_NAME_COUNT->{$cdic_name}));
#	}
#	exit;

	my $CDIC;
	if(defined $CDI && ref $CDI eq 'HASH'){
		foreach my $ci_id (sort {$a<=>$b} keys(%{$CDI})){
			foreach my $cdi_id (sort {$a<=>$b} keys(%{$CDI->{$ci_id}})){
				next unless(exists $CDI->{$ci_id}->{$cdi_id}->{'art'} && defined $CDI->{$ci_id}->{$cdi_id}->{'art'} && ref $CDI->{$ci_id}->{$cdi_id}->{'art'} eq 'HASH');
				next unless(exists $CDI->{$ci_id}->{$cdi_id}->{'cdic_name'} && defined $CDI->{$ci_id}->{$cdi_id}->{'cdic_name'} && length $CDI->{$ci_id}->{$cdi_id}->{'cdic_name'});
				my $cdic_name = $CDI->{$ci_id}->{$cdi_id}->{'cdic_name'};
				my $cdic_name_e = $CDI->{$ci_id}->{$cdi_id}->{'cdic_name_e'};
				my $cdi = &Clone::clone($CDI->{$ci_id}->{$cdi_id});
				$cdi->{'ci_id'} = $ci_id - 0;
				delete $cdi->{'cdic_name'};
				delete $cdi->{'cdic_name_e'};
				push(@{$CDIC->{$cdic_name}->{'items'}},$cdi);
				$CDIC->{$cdic_name}->{'total'} = scalar @{$CDIC->{$cdic_name}->{'items'}};
				$CDIC->{$cdic_name}->{'cdic_name_e'} = $cdic_name_e;
			}
		}
	}
#	&cgi_lib::common::message($CDIC);
#	if(defined $CDIC_NAME_COUNT && ref $CDIC_NAME_COUNT eq 'HASH'){
#		foreach my $cdic_name (sort keys(%$CDIC_NAME_COUNT)){
#			&cgi_lib::common::message(sprintf("%s\t%d",$cdic_name,$CDIC_NAME_COUNT->{$cdic_name})) if(exists $CDIC_NAME_COUNT->{$cdic_name} && defined $CDIC_NAME_COUNT->{$cdic_name} && $CDIC_NAME_COUNT->{$cdic_name}>1);
#		}
#	}
#	exit;

#	&cgi_lib::common::message($CDIC);
#	die __LINE__;


	my $CDIC_CONV;
	my $SUB_PART_CLASS;
	my $LATERALITY;
	if(defined $CDIC && ref $CDIC eq 'HASH'){
		my ($cp_id,$cp_title,$cp_abbr,$cp_prefix,$cp_order,$crl_id);
		$sql = qq|SELECT cp_id,cp_title,cp_abbr,cp_prefix,cp_order,crl_id FROM concept_part WHERE cp_use|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cp_id, undef);
		$sth->bind_col(++$column_number, \$cp_title, undef);
		$sth->bind_col(++$column_number, \$cp_abbr, undef);
		$sth->bind_col(++$column_number, \$cp_prefix, undef);
		$sth->bind_col(++$column_number, \$cp_order, undef);
		$sth->bind_col(++$column_number, \$crl_id, undef);
		while($sth->fetch){
			$SUB_PART_CLASS->{$cp_abbr} = {
				cp_id     => $cp_id-0,
				cp_title  => $cp_title,
				cp_abbr   => $cp_abbr,
				cp_prefix => $cp_prefix,
				cp_order  => $cp_order-0,
				crl_id    => defined $crl_id ? $crl_id-0 : 3,	#ここでは、is_aにする
			};
		}
		$sth->finish;
		undef $sth;

		my ($cl_id,$cl_title,$cl_abbr,$cl_prefix,$cl_order);
		$sql = qq|SELECT cl_id,cl_title,cl_abbr,cl_prefix,cl_order FROM concept_laterality WHERE cl_use|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$cl_id, undef);
		$sth->bind_col(++$column_number, \$cl_title, undef);
		$sth->bind_col(++$column_number, \$cl_abbr, undef);
		$sth->bind_col(++$column_number, \$cl_prefix, undef);
		$sth->bind_col(++$column_number, \$cl_order, undef);
		while($sth->fetch){
			$LATERALITY->{$cl_abbr} = {
				cl_id     => $cl_id-0,
				cl_title  => $cl_title,
				cl_abbr   => $cl_abbr,
				cl_prefix => $cl_prefix,
				cl_order  => $cl_order-0,
			};
		}
		$sth->finish;
		undef $sth;

		my $CDI_MAX_ID;
		my ($cdi_max_id);
		$sql = qq|SELECT ci_id,max(cdi_id) FROM concept_data_info GROUP BY ci_id|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		$column_number = 0;
		$sth->bind_col(++$column_number, \$ci_id, undef);
		$sth->bind_col(++$column_number, \$cdi_max_id, undef);
		while($sth->fetch){
			$CDI_MAX_ID->{$ci_id} = defined $cdi_max_id ? $cdi_max_id-0 : 0;
		}
		$sth->finish;
		undef $sth;
		&cgi_lib::common::message($CDI_MAX_ID);


		my @SUB_CLASS = split('','NFOABCDEGH');
		my @SUB_PART  = split('','QSTUVWX');

		$sql = qq|INSERT INTO concept_data_info (ci_id,cdi_id,cdi_name,cdi_name_e,is_user_data,cp_id,cl_id,cdi_pid) VALUES (?,?,?,?,true,?,?,?) RETURNING cdi_id|;
		$sth = $dbh->prepare($sql) or die $dbh->errstr;

		foreach my $cdic_name (keys(%{$CDIC})){
			&cgi_lib::common::message($cdic_name);

			next unless($cdic_name =~ /^(FMA[0-9]+)([A-Z]*)\-([LRU])$/);

			my $temp_cdi_name = $1;
			my $sub_part_class = $2;
			my $laterality = $3;

			unless(exists $CDI_NAME2ID->{$temp_cdi_name}){
				die qq|unknown [$temp_cdi_name]|;
			}


			if($CDIC->{$cdic_name}->{'total'}==1){
				$CDIC_CONV->{$cdic_name} = &Clone::clone($CDIC->{$cdic_name});


				$CDIC_CONV->{$cdic_name}->{'cdi_name_e'} = $CDIC->{$cdic_name}->{'cdic_name_e'};
				$CDIC_CONV->{$cdic_name}->{'cdic_name_e'}  = '';
				$CDIC_CONV->{$cdic_name}->{'cdic_name_e'} .= length $SUB_PART_CLASS->{$sub_part_class}->{'cp_prefix'} ? $SUB_PART_CLASS->{$sub_part_class}->{'cp_prefix'}.' ' : '';
				$CDIC_CONV->{$cdic_name}->{'cdic_name_e'} .= length $LATERALITY->{$laterality}->{'cl_prefix'}         ? $LATERALITY->{$laterality}->{'cl_prefix'}.' '         : '';
				$CDIC_CONV->{$cdic_name}->{'cdic_name_e'} .= length $CDIC_CONV->{$cdic_name}->{'cdic_name_e'} ? lc $CDIC->{$cdic_name}->{'cdic_name_e'} : $CDIC->{$cdic_name}->{'cdic_name_e'};

				$CDIC_CONV->{$cdic_name}->{'ci_id'} = $CDIC->{$cdic_name}->{'items'}->[0]->{'ci_id'};
				$CDIC_CONV->{$cdic_name}->{'cp_id'} = $SUB_PART_CLASS->{$sub_part_class}->{'cp_id'};
				$CDIC_CONV->{$cdic_name}->{'crl_id'} = $SUB_PART_CLASS->{$sub_part_class}->{'crl_id'};
				$CDIC_CONV->{$cdic_name}->{'cl_id'} = $LATERALITY->{$laterality}->{'cl_id'};
				$CDIC_CONV->{$cdic_name}->{'cdi_pid'} = $CDI_NAME2ID->{$temp_cdi_name};


				unless(exists $CDI_NAME2ID->{$cdic_name} && defined $CDI_NAME2ID->{$cdic_name}){

					$CDI_MAX_ID->{$ci_id}++;

					my $cdic_id;
					$sth->execute($CDIC_CONV->{$cdic_name}->{'ci_id'}, $CDI_MAX_ID->{$ci_id}, $cdic_name, $CDIC_CONV->{$cdic_name}->{'cdic_name_e'}, $CDIC_CONV->{$cdic_name}->{'cp_id'}, $CDIC_CONV->{$cdic_name}->{'cl_id'}, $CDIC_CONV->{$cdic_name}->{'cdi_pid'}) or die $dbh->errstr;
					$column_number = 0;
					$sth->bind_col(++$column_number, \$cdic_id, undef);
					$sth->fetch;
					$sth->finish;

					$CDIC_CONV->{$cdic_name}->{'cdic_id'}  = defined $cdic_id ? $cdic_id-0 : undef;

					$CDI_NAME2ID->{$cdic_name} = $cdic_id-0 if(defined $cdic_id);
				}
				else{
					$CDIC_CONV->{$cdic_name}->{'cdic_id'} = $CDI_NAME2ID->{$cdic_name};
				}


			}
			elsif($CDIC->{$cdic_name}->{'total'}>1){

#					&cgi_lib::common::message(sprintf("%s\t%s\t%s\t%s\t%s",$temp_cdi_name,$sub_part_class,$SUB_PART_CLASS->{$sub_part_class}->{'cp_title'},$laterality,$LATERALITY->{$laterality}->{'cl_title'}));
				my $SUB = $SUB_PART_CLASS->{$sub_part_class}->{'crl_id'}==3 ? \@SUB_CLASS : \@SUB_PART;
				my $i = -1;
				foreach my $item (@{$CDIC->{$cdic_name}->{'items'}}){
					&cgi_lib::common::message($item);
					$i++;
					my $temp_cdic_name;# = $temp_cdi_name.$SUB->[$i].'-'.$laterality;
					while(1){
						die __LINE__ unless(defined $SUB->[$i]);
						$temp_cdic_name = $temp_cdi_name.$SUB->[$i].'-'.$laterality;
#						last unless(exists $CDIC_CONV->{$temp_cdic_name});
						last unless(exists $CDIC_CONV->{$temp_cdic_name} || exists $CDIC->{$temp_cdic_name});
						$i++;
					}
					&cgi_lib::common::message(sprintf("%s\t%d",$temp_cdic_name, exists $CDIC_CONV->{$temp_cdic_name} ? 1 : 0));
					unless(exists $CDIC_CONV->{$temp_cdic_name}){
						push(@{$CDIC_CONV->{$temp_cdic_name}->{'items'}}, &Clone::clone($item));
#							&cgi_lib::common::message($temp_cdic_name);
						$CDIC_CONV->{$temp_cdic_name}->{'total'} = scalar @{$CDIC_CONV->{$temp_cdic_name}->{'items'}};
						$CDIC_CONV->{$temp_cdic_name}->{'cdi_name_e'} = $CDIC->{$cdic_name}->{'cdic_name_e'};
						$CDIC_CONV->{$temp_cdic_name}->{'cdic_name_e'}  = '';
						$CDIC_CONV->{$temp_cdic_name}->{'cdic_name_e'} .= length $SUB_PART_CLASS->{$SUB->[$i]}->{'cp_prefix'} ? $SUB_PART_CLASS->{$SUB->[$i]}->{'cp_prefix'}.' ' : '';
						$CDIC_CONV->{$temp_cdic_name}->{'cdic_name_e'} .= length $LATERALITY->{$laterality}->{'cl_prefix'}    ? $LATERALITY->{$laterality}->{'cl_prefix'}.' '    : '';
						$CDIC_CONV->{$temp_cdic_name}->{'cdic_name_e'} .= sprintf("%s [%d]",length $CDIC_CONV->{$temp_cdic_name}->{'cdic_name_e'} ? lc $CDIC->{$cdic_name}->{'cdic_name_e'} : $CDIC->{$cdic_name}->{'cdic_name_e'}, $i+1);

						$CDIC_CONV->{$temp_cdic_name}->{'ci_id'} = $item->{'ci_id'};
						$CDIC_CONV->{$temp_cdic_name}->{'cp_id'} = $SUB_PART_CLASS->{$SUB->[$i]}->{'cp_id'};
						$CDIC_CONV->{$temp_cdic_name}->{'crl_id'} = $SUB_PART_CLASS->{$SUB->[$i]}->{'crl_id'};
						$CDIC_CONV->{$temp_cdic_name}->{'cl_id'} = $LATERALITY->{$laterality}->{'cl_id'};
						$CDIC_CONV->{$temp_cdic_name}->{'cdi_pid'} = $CDI_NAME2ID->{$temp_cdi_name};

#=pod
						unless(exists $CDI_NAME2ID->{$temp_cdic_name} && defined $CDI_NAME2ID->{$temp_cdic_name}){

							$CDI_MAX_ID->{$ci_id}++;

							my $cdic_id;
							$sth->execute($CDIC_CONV->{$temp_cdic_name}->{'ci_id'}, $CDI_MAX_ID->{$ci_id}, $temp_cdic_name, $CDIC_CONV->{$temp_cdic_name}->{'cdic_name_e'}, $CDIC_CONV->{$temp_cdic_name}->{'cp_id'}, $CDIC_CONV->{$temp_cdic_name}->{'cl_id'}, $CDIC_CONV->{$temp_cdic_name}->{'cdi_pid'}) or die $dbh->errstr;
							$column_number = 0;
							$sth->bind_col(++$column_number, \$cdic_id, undef);
							$sth->fetch;
							$sth->finish;

							$CDIC_CONV->{$temp_cdic_name}->{'cdic_id'}  = defined $cdic_id ? $cdic_id-0 : undef;

							$CDI_NAME2ID->{$temp_cdic_name} = $cdic_id-0 if(defined $cdic_id);
						}
						else{
							$CDIC_CONV->{$temp_cdic_name}->{'cdic_id'} = $CDI_NAME2ID->{$temp_cdic_name};
						}
#=cut

					}
					else{
						&cgi_lib::common::message(qq|exists [$cdic_name][$temp_cdic_name]|);
						die __LINE__;
					}

				}
#				$CDIC_CONV->{$cdic_name}->{'is_delete'} = JSON::XS::true;
			}
		}
		undef $sth;
	}

	&cgi_lib::common::message($CDIC_CONV);
#	die __LINE__;

	if(defined $CDIC_CONV && ref $CDIC_CONV eq 'HASH'){
		my @TABLES;
		if(DEBUG){
			@TABLES = qw/concept_art_map/;
		}
		else{
			@TABLES = qw/concept_art_map history_concept_art_map/;
		}
		foreach my $table (@TABLES){
			$sql = qq|UPDATE $table SET cdi_id=? WHERE ci_id=? AND cdi_id=? AND art_id=? RETURNING cdi_id|;
			$sth = $dbh->prepare($sql) or die $dbh->errstr;

			foreach my $cdic_name (keys(%{$CDIC_CONV})){
				my $ci_id   = $CDIC_CONV->{$cdic_name}->{'ci_id'};
				my $cdic_id = $CDIC_CONV->{$cdic_name}->{'cdic_id'};
				my $cdi_id  = $CDIC_CONV->{$cdic_name}->{'items'}->[0]->{'cdi_id'};

				next if($cdic_id == $cdi_id);

				foreach my $art_id (keys(%{$CDIC_CONV->{$cdic_name}->{'items'}->[0]->{'art'}})){

	#				&cgi_lib::common::message(sprintf("%d\t%d\t%d\t%s", $ci_id, $cdic_id, $cdi_id, $art_id));
					&cgi_lib::common::message(sprintf("%d\t%s\t%d\t%s\t%s\t%s", $cdi_id, $CDIC_CONV->{$cdic_name}->{'items'}->[0]->{'cdi_name'}, $cdic_id, $cdic_name, $art_id, $CDIC_CONV->{$cdic_name}->{'items'}->[0]->{'art'}->{$art_id}->{'artc_id'}));

					$sth->execute($cdic_id,$ci_id,$cdi_id,$art_id) or die $dbh->errstr;
					my $rows = $sth->rows;
					my $temp_cdi_id;
					$column_number = 0;
					$sth->bind_col(++$column_number, \$temp_cdi_id, undef);
					$sth->fetch;
					$sth->finish;

	#				&cgi_lib::common::message(sprintf("%s\t%s\t%s\t%s", $CDIC_CONV->{$cdic_name}->{'items'}->[0]->{'cdi_name'}, $cdic_name, $art_id, $CDIC_CONV->{$cdic_name}->{'items'}->[0]->{'art'}->{$art_id}->{'artc_id'})) if($rows != 1);
					if($rows >= 1){
						&cgi_lib::common::message("OK [$temp_cdi_id][$rows][$table]");
					}
					else{
						&cgi_lib::common::message("NG [$rows][$table]");
						die __LINE__;
					}
				}
			}

			undef $sth;
		}

	}


	#結果出力
	if(defined $CDIC_CONV && ref $CDIC_CONV eq 'HASH'){
		@HEADER = qw/art_id art_xcenter artc_id cdi_name cdi_name_e cdic_name cdic_name_e/;
		$HEADER[0] = '#'.$HEADER[0];
		@OUT = ();
		foreach my $cdic_name (keys(%{$CDIC_CONV})){
			my @LINE;
			my $item = $CDIC_CONV->{$cdic_name}->{'items'}->[0];
			foreach my $art_id (keys(%{$item->{'art'}})){
				push(@LINE, $item->{'art'}->{$art_id}->{'art_id'});
				push(@LINE, $item->{'art'}->{$art_id}->{'art_xcenter'});
				push(@LINE, $item->{'art'}->{$art_id}->{'artc_id'});
			}
			push(@LINE, $item->{'cdi_name'});
			push(@LINE, $item->{'cdi_name_e'});

			push(@LINE, $cdic_name);
			push(@LINE, $CDIC_CONV->{$cdic_name}->{'cdic_name_e'});

			push(@OUT, join("\t", @LINE));
		}
	}

	say join("\t", @HEADER);
	say join("\n", sort {(split(/\t/,$a))[0] cmp (split(/\t/,$b))[0]} @OUT);

	&cgi_lib::common::message($CDIC_CONV);
#	&cgi_lib::common::message($CDIC);
#	&cgi_lib::common::message($CDI);
#	&cgi_lib::common::message($CDIC_NAME_COUNT);
#	die __LINE__;

	$dbh->do(q|ALTER TABLE art_file_info ENABLE TRIGGER trig_after_art_file_info|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE art_file_info ENABLE TRIGGER trig_before_art_file_info|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE history_art_file_info ENABLE TRIGGER trig_before_history_art_file_info|) or die $dbh->errstr;

	$dbh->do(q|ALTER TABLE concept_art_map ENABLE TRIGGER trig_after_concept_art_map|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE concept_art_map ENABLE TRIGGER trig_before_concept_art_map|) or die $dbh->errstr;
	$dbh->do(q|ALTER TABLE history_concept_art_map ENABLE TRIGGER trig_before_history_concept_art_map|) or die $dbh->errstr;



#	$dbh->rollback;
#	$dbh->commit();

=pod
	$sql = qq|SELECT cdi.ci_id,cdi.cdi_id,cdi.cdi_name,cdi.cdi_name_e,cdi.is_user_data,cm.art_id,cm.cm_use FROM concept_data_info AS cdi LEFT JOIN concept_art_map AS cm ON cm.ci_id=cdi.ci_id AND cm.cdi_id=cdi.cdi_id WHERE (cdi.ci_id,cdi.cdi_id) IN (SELECT ci_id,cdi_id FROM concept_art_map)|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	$sth->bind_col(++$column_number, \$cdi_name_e, undef);
	$sth->bind_col(++$column_number, \$is_user_data, undef);
	$sth->bind_col(++$column_number, \$art_id, undef);
	$sth->bind_col(++$column_number, \$cm_use, undef);
	while($sth->fetch){
		say STDERR sprintf("%d\t%s\t%s\t%s\t%s", $cdi_id, $cdi_name, $cdi_name_e, $art_id, $cm_use ? 'true' : 'false');
	}
	$sth->finish;
	undef $sth;


	#未使用のユーザ定義FMAIDのIDを削除する
	my $NO_USE_CDI;
	$sql = qq|SELECT cdi.ci_id,cdi.cdi_id,cdi.cdi_name FROM concept_data_info AS cdi WHERE (cdi.ci_id,cdi.cdi_id) NOT IN (SELECT ci_id,cdi_id FROM concept_art_map) AND is_user_data|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	$sth->execute() or die $dbh->errstr;
	$column_number = 0;
	$sth->bind_col(++$column_number, \$ci_id, undef);
	$sth->bind_col(++$column_number, \$cdi_id, undef);
	$sth->bind_col(++$column_number, \$cdi_name, undef);
	while($sth->fetch){
		$NO_USE_CDI->{$ci_id}->{$cdi_id} = $cdi_name;
	}
	$sth->finish;
	undef $sth;

	$sql = qq|DELETE FROM concept_data_info WHERE ci_id=? AND cdi_id=?|;
	$sth = $dbh->prepare($sql) or die $dbh->errstr;
	foreach $ci_id (sort {$a <=> $b} keys(%$NO_USE_CDI)){
		foreach $cdi_id (sort {$a <=> $b} keys(%{$NO_USE_CDI->{$ci_id}})){
			$sth->execute($ci_id,$cdi_id) or die $dbh->errstr;
			$sth->finish;
		}
	}
	undef $sth;
=cut

	if(DEBUG){
		$dbh->rollback;
	}
	else{
		$dbh->commit();
	}
	exit;





=pod
=cut








#	die __LINE__;

	$dbh->commit();
};
if($@){
	&cgi_lib::common::message($@);
	$dbh->rollback;
}
$dbh->{'AutoCommit'} = 1;
$dbh->{'RaiseError'} = 0;
