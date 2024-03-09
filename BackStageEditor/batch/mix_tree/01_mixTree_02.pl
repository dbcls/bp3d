# ベースのtreeと補足のtreeを入力として与え、ベースのtreeに無いFMA IDで補足のtreeにある場合、補足のtreeを足したものを生成します。
use strict;
my $baseTree = $ARGV[0];
my $suppTree = $ARGV[1];
my %id2base = ();
my %id2supp = ();
my %addId = ();
my %hasChildInBase = ();
my %name2fma = ();
my %name2ChildIDInSupp = ();
my $baseheader = "";

# ベースのtreeで、id→tree定義を保持
open BASE,$baseTree;
while (<BASE>) {
	chomp;
	s/[\r\n]*$//g;
	if (/^#/) {
		$baseheader = $_;
		# skip comment line
		next;
	}
	# store id and info
	my @data = split("\t", $_);
	my $id = $data[0];
	my $name = $data[1];
	$name2fma{$name} = $id;
	$id2base{$id} = $_;
	# ベースのtreeで子供がいる（何かの親になっている）エントリーの名前を保持しておく
	for (my $i = 10; $i < @data; $i+=2) {
		$hasChildInBase{$data[$i]}++;
	}
}
close BASE;

# 補足のtreeで、親の名前→子供のIDを探すhashを構築
open SUP,$suppTree;
while (<SUP>) {
	chomp;
	s/[\r\n]*$//g;
	if (/^#/) {
		# skip comment line
		next;
	}
	# store id and info
	my @data = split("\t", $_);
	my $id = $data[0];
	my $name = $data[1];
	for (my $i = 10; $i < @data; $i+=2) {
		push @{$name2ChildIDInSupp{$data[$i]}}, $id;
	}
}

# 補足のtreeで、追加すべき情報を探索
open SUP,$suppTree;
while (<SUP>) {
	chomp;
	s/[\r\n]*$//g;
	if (/^#/) {
		# skip comment line
		next;
	}
	# store id and info
	my @data = split("\t", $_);
	my $id = $data[0];
	my $name = $data[1];
	$id2supp{$id} = $_;
	# ベースのツリーに無い場合、IDを追加
	unless ($id2base{$id}) {
		$addId{$id}++;
		# 子供がベースのツリーで定義されていないとレンダリングできないので
		# FJIDでない（objファイルではない）場合
		unless ($id =~ /^FJ/) {
			# ベースツリーで子供がいない場合
			unless ($hasChildInBase{$name}) {
				# 名前から子供のIDを検索して
				foreach my $fmaid (@{$name2ChildIDInSupp{$name}}) {
					# 自分を親とする定義を追加しておく
					if ($id2base{$fmaid}) {
						# 該当IDがベースtreeにある場合のみ（無ければ補足treeから矛盾のないデータが追加されるはず）
						$id2base{$fmaid} .= "\t".$name."\t0";
						# debug
						print STDERR $id2base{$fmaid}."\n";
					}
				}
			}
		}
	}
}
close SUP;

# 出力
print $baseheader . "\r\n";
# ベースtree由来のデータを出力
foreach my $id (sort keys %id2base) {
	if ($id =~ /FMA/) {
		print $id2base{$id}."\r\n";
	}
}

foreach my $id (sort keys %id2base) {
	unless ($id =~ /FMA/) {
		print $id2base{$id}."\r\n";
	}
}

# 補足tree由来のデータを出力
foreach my $id (sort keys %id2supp) {
	unless ($addId{$id}) {
		next;
	}
	if ($id =~ /FMA/) {
		print $id2supp{$id}."\r\n";
	}
}

foreach my $id (sort keys %id2supp) {
	unless ($addId{$id}) {
		next;
	}
	unless ($id =~ /FMA/) {
		print $id2supp{$id}."\r\n";
	}
}
