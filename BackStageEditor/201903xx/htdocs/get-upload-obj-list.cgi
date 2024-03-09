#!/usr/bin/perl

use strict;
use JSON::XS;
use File::Basename;
use Cwd qw(abs_path);
use File::Spec;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Data::Dumper;

use FindBin;
use lib $FindBin::Bin,qq|$FindBin::Bin/../cgi_lib|;
use BITS::Config;
require "webgl_common.pl";

my $query = CGI->new;
my @params = $query->param();
my %PARAMS = ();
foreach my $param (@params){
	$PARAMS{$param} = defined $query->param($param) ? $query->param($param) : undef;
	$PARAMS{$param} = undef if(defined $PARAMS{$param} && length($PARAMS{$param})==0);
}

my @extlist = qw|.cgi|;
my($cgi_name,$cgi_dir,$cgi_ext) = &File::Basename::fileparse($0,@extlist);

open(LOG,"> logs/$cgi_name.txt");
foreach my $key (sort keys(%PARAMS)){
	print LOG qq|\$PARAMS{$key}=[$PARAMS{$key}]\n|;
}

$PARAMS{start} = 0 unless(defined $PARAMS{start});
$PARAMS{limit} = 25 unless(defined $PARAMS{limit});

#$PARAMS{name} = qq|120406_liver_divided01_obj|;

my @GROUPS = ();
if(defined $PARAMS{groups}){
	my $groups;
	eval{$groups = &JSON::XS::decode_json($PARAMS{groups});};
	push(@GROUPS,@$groups) if(defined $groups && ref $groups eq 'ARRAY');
}
my %FILTER;
if(defined $PARAMS{filter}){
	my $filter;
	eval{$filter = &JSON::XS::decode_json($PARAMS{filter});};
	if(defined $filter && ref $filter eq 'ARRAY'){
		foreach my $f (@$filter){
			$FILTER{$f->{property}} = $f->{value};
		}
	}
}
#foreach my $key (sort keys(%FILTER)){
#	print LOG qq|\$FILTER{$key}=[$FILTER{$key}]\n|;
#}

my @SORT;
if(defined $PARAMS{sort}){
	my $sort;
	eval{$sort = &JSON::XS::decode_json($PARAMS{sort});};
	push(@SORT,@$sort) if(defined $sort && ref $sort eq 'ARRAY');
}
push(@SORT,{
	property  => 'group',
	direction => 'ASC'
},{
	property  => 'name',
	direction => 'ASC'
});

my %SELECTED;
if(defined $PARAMS{selected}){
	my $selected;
	eval{$selected = &JSON::XS::decode_json($PARAMS{selected});};
	if(defined $selected && ref $selected eq 'ARRAY'){
		foreach my $s (@$selected){
			$SELECTED{$s->{group}} = {} unless(defined $SELECTED{$s->{group}});
			$SELECTED{$s->{group}}->{$s->{name}} = $s;
		}
	}
}
foreach my $key (sort keys(%SELECTED)){
	print LOG qq|\$SELECTED{$key}=[$SELECTED{$key}]\n|;
}

#print qq|Content-type: text/html; charset=UTF-8\n\n|;

my $DATAS = {
	"datas" => [],
	"total" => 0
};

foreach my $group (@GROUPS){
	my $all = File::Spec->catfile($BITS::Config::UPLOAD_PATH,$group,qq|all.json|);
	next unless(-e $all);

	my $json;
	my $IN;
	open($IN,"< $all") || die "[$all] $!\n";
	$/ = undef;
	eval{$json = &JSON::XS::decode_json(<$IN>);};
	close($IN);
	if(defined $json && ref $json eq 'ARRAY'){
		foreach my $j (@$json){
			my $path = File::Spec->catfile($BITS::Config::UPLOAD_PATH,$group,qq|$j->{name}.json|);
			$j->{path} = qq|$j->{name}.json| if(-e $path);
			unless(defined $j->{path}){
				$path = File::Spec->catfile($BITS::Config::UPLOAD_PATH,$group,qq|$j->{name}.obj|);
				$j->{path} = qq|$j->{name}.obj| if(-e $path);
			}
			$j->{group} = $group;

			#ファイル名からIDを抽出
			if($j->{name} =~ /^(FJ[0-9]+M*)[_\-]+[0-9]{6}[_\-]*(.+)$/){
				$j->{art_id} = $1;
				$j->{name} = $2;
#				$j->{name} =~ s/^[_\-]+[0-9]{6}[_\-]*//g;
			}


#DEBUG
#$j->{name} =~ s/^$group//g;
#$j->{name} =~ s/^_*//g;
#$j->{name} =~ s/[0-9]{14}$//g;
#$j->{name} =~ s/_*$//g;


			my $sortkey = $j->{name};
print LOG __LINE__,":\$sortkey=[$sortkey]\n";
			while($sortkey =~ /^[A-Z]{2,}/ || $sortkey =~ /^[0-9\.]{2,}/ || $sortkey =~ /^[_\-]+/){
				$sortkey =~ s/^[A-Z]{2,}//;
				$sortkey =~ s/^[0-9\.]{2,}//;
				$sortkey =~ s/^[_\-]+//;
print LOG __LINE__,":\$sortkey=[$sortkey]\n";
			}
			while($sortkey =~ /_{2,}[0-9\.]{2,}$/ || $sortkey =~ /[_\-]+$/){
				$sortkey =~ s/(_{2,})[0-9]{2,}$/$1/;
				$sortkey =~ s/[_\-]+$//;
print LOG __LINE__,":\$sortkey=[$sortkey]\n";
			}
			$sortkey =~ s/[_]+/ /g;

#			$sortkey =~ s/[_]+$//g;

			$j->{'sortname'} = lc(join("_",reverse split(/\s+/,$sortkey)));


			$j->{filesize} = $j->{size} if(defined $j->{size} && !defined $j->{filesize});
		}
		push(@{$DATAS->{datas}},@$json);
	}
	$DATAS->{total} = scalar @{$DATAS->{datas}};
}

=pod
if(defined $PARAMS{filter}){
	my $filter;
	eval{$filter = decode_json($PARAMS{filter});};
	if(defined $filter){
		foreach my $f (@$filter){
			next unless($f->{property} eq 'group');

			my $all = File::Spec->catfile($BITS::Config::UPLOAD_PATH,$f->{value},qq|all.json|);
			if(-e $all){
				my $json;
				my $IN;
				open($IN,"< $all") || die "[$all] $!\n";
				$/ = undef;
				eval{$json = decode_json(<$IN>);};
				close($IN);
				if(defined $json){
					foreach my $j (@$json){
						$j->{group} = $f->{value};
#						$j->{path} = File::Spec->catfile($f->{value},qq|$j->{name}.json|);
						$j->{path} = qq|$j->{name}.json|;
#						$j->{path} = qq|$j->{name}.obj|;
						$j->{filesize} = $j->{size} if(defined $j->{size} && !defined $j->{filesize});
					}
					push(@{$DATAS->{datas}},@$json);
				}
			}
		}
	}
}
=cut

foreach my $s (reverse @SORT){
	print LOG __LINE__,":$s->{property}\n";
	if(
		$s->{property} eq 'group' ||
		$s->{property} eq 'name' ||
		$s->{property} eq 'sortname'
	){
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {$a->{$s->{property}} cmp $b->{$s->{property}} } @{$DATAS->{datas}}
		}else{
			@{$DATAS->{datas}} = sort {$b->{$s->{property}} cmp $a->{$s->{property}} } @{$DATAS->{datas}}
		}

	}elsif(
		$s->{property} eq 'name' ||
		$s->{property} eq 'sortname'
	){
=pod
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {
				my $a1 = $a->{$s->{property}};
				my $b1 = $b->{$s->{property}};
				$a1 =~ s/^[DBCLSFUJIEA_0-9\-\.]+//g;
				$b1 =~ s/^[DBCLSFUJIEA_0-9\-\.]+//g;
				$a1 =~ s/[_0-9]+$//g;
				$b1 =~ s/[_0-9]+$//g;
				print LOG __LINE__,":\$a1=[$a1]\n";
				print LOG __LINE__,":\$b1=[$b1]\n";

				$a1 cmp $b1
			} @{$DATAS->{datas}}

		}else{
			@{$DATAS->{datas}} = sort {
				my $a1 = $a->{$s->{property}};
				my $b1 = $b->{$s->{property}};
				$a1 =~ s/^[DBCLSFUJIEA_0-9\-\.]+//g;
				$b1 =~ s/^[DBCLSFUJIEA_0-9\-\.]+//g;
				$a1 =~ s/[_0-9]+$//g;
				$b1 =~ s/[_0-9]+$//g;
				print LOG __LINE__,":\$a1=[$a1]\n";
				print LOG __LINE__,":\$b1=[$b1]\n";

				$b1 cmp $a1
			} @{$DATAS->{datas}}
		}
=cut

		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {$a->{'sortname'} cmp $b->{'sortname'} } @{$DATAS->{datas}}
		}else{
			@{$DATAS->{datas}} = sort {$b->{'sortname'} cmp $a->{'sortname'} } @{$DATAS->{datas}}
		}

	}elsif($s->{property} eq 'reduction'){
		my @TEMP1 = ();
		my @TEMP2 = ();
		foreach my $data (@{$DATAS->{datas}}){
			if($data->{'points'} eq '-' || $data->{'org_points'} eq '-'){
				push(@TEMP2,$data);
			}else{
				push(@TEMP1,$data);
			}
		}
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort { 1 - $a->{'polys'} / $a->{'org_polys'} <=> 1 - $b->{'polys'} / $b->{'org_polys'} } @TEMP1;
		}else{
			@{$DATAS->{datas}} = sort { 1 - $b->{'polys'} / $b->{'org_polys'} <=> 1 - $a->{'polys'} / $a->{'org_polys'} } @TEMP1;
		}
		push(@{$DATAS->{datas}},@TEMP2);
		undef @TEMP1;
		undef @TEMP2;
	}elsif(
		$s->{property} eq 'filesize' ||
		$s->{property} eq 'conv_size' ||
		$s->{property} eq 'json_size' ||
		$s->{property} eq 'org_points' ||
		$s->{property} eq 'org_polys' ||
		$s->{property} eq 'points' ||
		$s->{property} eq 'polys'
	){
		my @TEMP1 = ();
		my @TEMP2 = ();
		foreach my $data (@{$DATAS->{datas}}){
			if($data->{$s->{property}} eq '-'){
				push(@TEMP2,$data);
			}else{
				push(@TEMP1,$data);
			}
		}
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {$a->{$s->{property}} <=> $b->{$s->{property}} } @TEMP1
		}else{
			@{$DATAS->{datas}} = sort {$b->{$s->{property}} <=> $a->{$s->{property}} } @TEMP1
		}
		push(@{$DATAS->{datas}},@TEMP2);
		undef @TEMP1;
		undef @TEMP2;


	}elsif($s->{property} eq 'color'){
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {
				(defined $SELECTED{$a->{'group'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} ? uc($SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}}) : '#F0D2A0')
				cmp
				(defined $SELECTED{$b->{'group'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} ? uc($SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}}) : '#F0D2A0')
			} @{$DATAS->{datas}}
		}else{
			@{$DATAS->{datas}} = sort {
				(defined $SELECTED{$b->{'group'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} ? uc($SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}}) : '#F0D2A0')
				cmp
				(defined $SELECTED{$a->{'group'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} ? uc($SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}}) : '#F0D2A0')
			} @{$DATAS->{datas}}
		}

	}elsif($s->{property} eq 'opacity'){
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {
				(defined $SELECTED{$a->{'group'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} ? $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} : 1.0)
				<=>
				(defined $SELECTED{$b->{'group'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} ? $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} : 1.0)
			} @{$DATAS->{datas}}
		}else{
			@{$DATAS->{datas}} = sort {
				(defined $SELECTED{$b->{'group'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} ? $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} : 1.0)
				<=>
				(defined $SELECTED{$a->{'group'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} ? $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} : 1.0)
			} @{$DATAS->{datas}}
		}

	}elsif($s->{property} eq 'selected'){
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {
				(defined $SELECTED{$a->{'group'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} ? $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} : JSON::XS::false)
				<=>
				(defined $SELECTED{$b->{'group'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} ? $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} : JSON::XS::false)
			} @{$DATAS->{datas}}
		}else{
			@{$DATAS->{datas}} = sort {
				(defined $SELECTED{$b->{'group'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}} && defined $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} ? $SELECTED{$b->{'group'}}->{$b->{'name'}}->{$s->{property}} : JSON::XS::false)
				<=>
				(defined $SELECTED{$a->{'group'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}} && defined $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} ? $SELECTED{$a->{'group'}}->{$a->{'name'}}->{$s->{property}} : JSON::XS::false)
			} @{$DATAS->{datas}}
		}

	}else{
		if($s->{direction} eq 'ASC'){
			@{$DATAS->{datas}} = sort {$a->{$s->{property}} <=> $b->{$s->{property}} } @{$DATAS->{datas}}
		}else{
			@{$DATAS->{datas}} = sort {$b->{$s->{property}} <=> $a->{$s->{property}} } @{$DATAS->{datas}}
		}
	}
}


if(defined $PARAMS{start} && defined $PARAMS{limit} && $PARAMS{limit}>0){
	my $start = $PARAMS{start};
	my $end = $PARAMS{start} + $PARAMS{limit} - 1;
	$end = $DATAS->{total}-1 if($end >= $DATAS->{total});
	my @DATAS = @{$DATAS->{datas}}[$start..$end];
#	$DATAS->{datas} = \@DATAS;
	$DATAS->{datas} = [];
	push(@{$DATAS->{datas}},@DATAS);
}


#my $json = &JSON::XS::encode_json($DATAS);
#print $json;
&gzip_json($DATAS);
#print LOG $json,"\n";
print LOG __LINE__,":",Dumper($DATAS),"\n";

close(LOG);
