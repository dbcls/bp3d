#!/usr/bin/perl

#warn __LINE__,"\n";

$| = 1;

my $anatomo_path;
my $anatomo_IM_path;
BEGIN {
	$anatomo_path = qq|/bp3d/ag1/htdocs|;
	$anatomo_IM_path = qq|$anatomo_path/IM|;
}

use strict;

use lib $anatomo_path,$anatomo_IM_path;
use Image::Info qw(image_info dim);
use Image::Magick;
use DBI;
use DBD::Pg;
use File::Path;
use JSON::XS;

warn __LINE__,"\n";

require "common.pl";
require "common_db.pl";
require "common_locale.pl";
require "common_image.pl";
require "common_wiki.pl";
my $dbh = &get_dbh();

#my $wiki_path = qq|../|.&getMediawikiPath();
#my $script = qq|php $wiki_path/maintenance/importTextFile.php --user 'bot'|;
my $import_path = qq|/dev/shm|;
#mkdir $import_path unless(-d $import_path);
my $import_file = qq|$import_path/.$$.txt|;
my $import_link_file = qq|$import_path/.$$\_c.txt|;
#warn $import_file,"\n";
#exit;

sub import_file {
	my $title = shift;
	my $lang = shift;
#	my $script = &getTextScript($lang);
	my $script = &getTextScript();

#print $title,"\n";
#print $lang,"\n";
#print $import_file,"\n";
#unlink $import_file if(-e $import_file);
#return;

	my $command = qq|$script --title "$title" $import_file|;
	print LOG __LINE__,":$command\n";
	system($command);
	my $exit_value = $? >> 8;
	my $signal_num = $? & 127;
	my $dumped_core = $? & 128;
	print LOG __LINE__,":[$exit_value][$signal_num][$dumped_core]\n";
	unlink $import_file if(-e $import_file);
}


my $log_file = qq|$0\_log.txt|;
open(LOG,"> $log_file");

warn __LINE__,"\n";

$SIG{'PIPE'} = $SIG{'INT'} = $SIG{'HUP'} = $SIG{'QUIT'} = $SIG{'TERM'} = "sigexit";
sub sigexit {
	my($date) = `date`;
	$date =~ s/\s*$//g;
	print STDERR "[$date] KILL THIS CGI!![$ENV{SCRIPT_NAME}]\n";
	unlink $import_file if(-e $import_file);
	close(LOG);
	exit(1);
}

warn __LINE__,":",(scalar @ARGV),"\n";

my $cache_fma_path_fmt = qq|$anatomo_path/cache_fma/%s/fmastratum/%s/%s.txt|;
#my $target_version = qq|2.0.1006240000|;
my $target_version = qq|3.0|;

#my @LANG = ('en','ja');
my @LANG = ('en');
my @VERSION = ();


my $column_number = 0;
my $fmaid;
if(defined $target_version && $target_version ne ""){
	push(@VERSION,$target_version);
}else{
	my $sql_tree_group_item = qq|select tgi_version from tree_group_item where tg_id=1 and tgi_delcause is null order by tgi_order|;
	my $sth_tree_group_item = $dbh->prepare($sql_tree_group_item);
	$sth_tree_group_item->execute();
	my $tgi_version;
	$column_number = 0;
	$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
	while($sth_tree_group_item->fetch){
		push(@VERSION,$tgi_version);
	}
	$sth_tree_group_item->finish;
	undef $sth_tree_group_item;
}

#my $debug_fmaid = "FMA30278";
#my $debug_fmaid = "FMA20394";
#my $debug_fmaid = "FMA19735";
#my $debug_fmaid = "FMA10951";
#my $debug_fmaid = "FMA59655";
#my $debug_fmaid = "FMA242787";
#my $debug_fmaid = "FMA10014";
my $debug_fmaid;

#効率が悪いが取りあえず、英語の情報を生成する
foreach my $lang (@LANG){
#	my $script = &getTextScript($lang);
	my $script = &getTextScript();
	foreach my $version (@VERSION){
		my %FORM = (
			'tg_id' => '1',
			'tg_model' => 'bp3d',
			'version' => $version
		);
		my %COOKIE;
		&convVersionName2RendererVersion($dbh,\%FORM,\%COOKIE);
		my $bp3d_table = &getBP3DTablename($FORM{version});

		my($b_density_bp3d,$b_density_end_ids_bp3d,$b_density_isa,$b_density_end_ids_isa,$b_density_partof,$b_density_end_ids_partof,$b_primitive);

		my $sql_fma = qq|select COALESCE(f_name_e,b_name_e) from $bp3d_table as bp3d|;
		$sql_fma .= qq| left join (select f_id,f_name_e from fma) as f on bp3d.f_id=f.f_id|;
		$sql_fma .= qq| where b_id=?|;
		my $sth_fma = $dbh->prepare($sql_fma);

		my $sql_fma = qq|select COALESCE(f_name_e,b_name_e) from $bp3d_table as bp3d|;
		$sql_fma .= qq| left join (select f_id,f_name_e from fma) as f on bp3d.f_id=f.f_id|;
		$sql_fma .= qq| where b_id=?|;
		my $sth_fma = $dbh->prepare($sql_fma);


		my $sql_bp3d = qq|select b_id|;
		$sql_bp3d .= qq|,(b_density_objs::real/b_density_ends::real) as b_density_bp3d|;
		$sql_bp3d .= qq|,b_density_end_ids as b_density_end_ids_bp3d|;
		$sql_bp3d .= qq|,(b_density_objs_isa::real/b_density_ends_isa::real) as b_density_isa|;
		$sql_bp3d .= qq|,b_density_end_ids_isa|;
		$sql_bp3d .= qq|,(b_density_objs_partof::real/b_density_ends_partof::real) as b_density_partof|;
		$sql_bp3d .= qq|,b_density_end_ids_partof|;
		$sql_bp3d .= qq|,b_primitive|;
#		$sql_bp3d .= qq| from $bp3d_table where f_id is not null and b_delcause is null order by f_id|;
		$sql_bp3d .= qq| from $bp3d_table where b_delcause is null order by b_id|;
		my $sth_bp3d = $dbh->prepare($sql_bp3d);
		$sth_bp3d->execute();
		my $column_number = 0;
		$sth_bp3d->bind_col(++$column_number, \$fmaid, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_density_bp3d, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_density_end_ids_bp3d, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_density_isa, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_density_end_ids_isa, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_density_partof, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_density_end_ids_partof, undef);
		$sth_bp3d->bind_col(++$column_number, \$b_primitive, undef);
		while($sth_bp3d->fetch){
			next unless(defined $fmaid);
			next if(defined $debug_fmaid && $debug_fmaid ne $fmaid);

			open(OUT,"> $import_file");
			print OUT qq|<noinclude><div id="contentSub"><span class="subpages">&lt; [[:{{BASEPAGENAME}}]]</span></div></noinclude>\n|;
			if(defined $b_primitive){
				print OUT qq|==Representation density (Primitive)==\n|;
			}else{
				print OUT qq|==Representation density==\n|;
			}
			print OUT qq|<div class="fma_density_base">\n|;
			if(defined $b_density_bp3d && defined $b_density_end_ids_bp3d){
				my $density = int($b_density_bp3d*10000)/100;
				print OUT qq|<div class="fma_density">|;
				print OUT qq|<h4>Conventional ($density %)</h4>\n|;
				$FORM{t_type} = '1';
				print OUT &make_density_table($fmaid,$b_density_end_ids_bp3d,$sth_fma,\%FORM);
				print OUT qq|</div>\n|;
			}
			if(defined $b_density_isa && defined $b_density_end_ids_isa){
				my $density = int($b_density_isa*10000)/100;
				print OUT qq|<div class="fma_density">|;
				print OUT qq|<h4>FMA is_a ($density %)</h4>\n|;
				$FORM{t_type} = '3';
				print OUT &make_density_table($fmaid,$b_density_end_ids_isa,$sth_fma,\%FORM);
				print OUT qq|</div>\n|;
			}
			if(defined $b_density_partof && defined $b_density_end_ids_partof){
				my $density = int($b_density_partof*10000)/100;
				print OUT qq|<div class="fma_density">|;
				print OUT qq|<h4>FMA part_of ($density %)</h4>\n|;
				$FORM{t_type} = '4';
				print OUT &make_density_table($fmaid,$b_density_end_ids_partof,$sth_fma,\%FORM);
				print OUT qq|</div>\n|;
			}
			print OUT qq|<br clear="all"></div>|;
			close(OUT);
			if(-s $import_file){
#				print __LINE__,":$import_file\n";
#				exit;
				&import_file(qq|density:$fmaid|,$lang);
			}

			last if(defined $debug_fmaid && $debug_fmaid eq $fmaid);

		}
		$sth_bp3d->finish;
		undef $sth_bp3d;
		undef $sth_fma;
	}
}
unlink $import_file if(-e $import_file);

close(LOG);

exit;

sub make_density_table {
	my $objid = shift;
	my $b_density_end_ids = shift;
	my $sth_fma = shift;
	my $form = shift;

	my $density_ends;

	my $max_density_ends_num = 10;
	my $end_ids = JSON::XS::decode_json($b_density_end_ids);
	my $density_ends_num = scalar @$end_ids;
	if($density_ends_num<=$max_density_ends_num){

		my $sth_fma2 = $dbh->prepare(qq|select f_name_e from fma where f_id=?|);

		my $arr;

		my $t_type = '1';
		my $t_key = 'conventional';
		$t_type = $form->{t_type} if(defined $form->{t_type});
		if($t_type eq '3'){
			$t_key = 'is_a';
		}elsif($t_type eq '4'){
			$t_key = 'part_of';
		}


		my $tg_model = defined $form->{'tg_model'} ? $form->{'tg_model'} : 'bp3d';
		my $obj_path = qq|$anatomo_path/obj/$tg_model/$form->{version}|;
		foreach my $objid (@$end_ids){
			my $path = qq|$obj_path/$objid.obj|;
#			warn __LINE__,":$path\n";
			my $obj_hash = {
				f_id => $objid,
				primitive => -e $path ? JSON::XS::true : JSON::XS::false
			};
			$obj_hash->{path} = "{{SERVER}}{{SCRIPTPATH}}/../icon.cgi?i=$objid&p=rotate&t=$t_key&c=0&m=bp3d&s=S&.gif" if(-e $path);
			my $obj_f_name_e;
			$sth_fma->execute($objid);
			my $column_number = 0;
			$sth_fma->bind_col(++$column_number, \$obj_f_name_e, undef);
			$sth_fma->fetch;
			$sth_fma->finish;
			unless(defined $obj_f_name_e){
				$sth_fma2->execute($objid);
				my $column_number = 0;
				$sth_fma2->bind_col(++$column_number, \$obj_f_name_e, undef);
				$sth_fma2->fetch;
				$sth_fma2->finish;
			}
			$obj_hash->{name} = $obj_f_name_e;
			push(@$arr,$obj_hash);
		}
		@$arr = sort {
			if($a->{primitive} == $b->{primitive}){
				$a->{f_id} cmp $b->{f_id};
			}elsif($a->{primitive}){
				-1;
			}elsif($b->{primitive}){
				1;
			}else{
				0;
			}
		} @$arr;
		$density_ends = qq|<table class="fma_density">|;
		foreach my $ends (@$arr){
			$density_ends .= qq|<tr>|;
			$density_ends .= qq|<td>[[|.$ends->{f_id}.qq|]]</td>|;
			if(defined $ends->{path}){
				$density_ends .= qq|<td class="is_primitive">|.$ends->{name}.qq|</td>|;
				$density_ends .= qq|<td class="is_primitive">|.$ends->{path}.qq|</td>|;
			}else{
				$density_ends .= qq|<td class="is_not_primitive" colspan=2>|.$ends->{name}.qq|</td>|;
			}
			$density_ends .= qq|</tr>|;
		}
		$density_ends .= qq|</table>|;
	}else{
		$density_ends = sprintf(qq|* too many children (%d)|,$density_ends_num);
	}
	return $density_ends;
}
