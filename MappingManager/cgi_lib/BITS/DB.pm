package BITS::DB;

#use strict;
#use warnings;
#use feature ':5.10';

#------------------------------------------------------------------------------
# 共通変数
#------------------------------------------------------------------------------
use DBI;
use Exporter;

my @ISA = qw(Exporter);
my @EXPORT = qw(get_dbh);

my $DB_user = 'postgres';
my $DB_pwd  = '';
my $DB_dbname = 'bp3d_manage';
my $DB_host = defined $ENV{AG_DB_HOST} ? $ENV{AG_DB_HOST} : '127.0.0.1';
my $DB_port = defined $ENV{AG_DB_PORT} ? $ENV{AG_DB_PORT} : '8543';
my $mydb;
my $mydb_local;

#my $LUDIA_OPERATOR='@@';
my $LUDIA_OPERATOR='%%'; #Ludiaが1.5.0以上で、PostgreSQLが8.3以上の場合、こちらを使用すること

#&connectDB;

#------------------------------------------------------------------------------
# データベース共通関数
#------------------------------------------------------------------------------
sub connectDB {
	my $DB_name;
	if(exists($FORM{db}) && $FORM{db} ne ""){
		$DB_name = "dbname=$FORM{db}";
	}elsif(defined $DB_host){
		$DB_name = "dbname=$DB_dbname;host=$DB_host;port=$DB_port";
	}else{
		$DB_name = "dbname=$DB_dbname;port=$DB_port";
	}
	$mydb = DBI->connect("dbi:Pg:$DB_name","$DB_user","$DB_pwd") || die DBI->errstr;
	return $mydb;
}

sub disconnectDB {
	$mydb->disconnect();
}

sub get_dbh {
	return $mydb;
}

sub get_ludia_operator {
	return $LUDIA_OPERATOR;
}

sub ExecuteSQL {
	my $sql = $_[0];
	my @DATA = ();
	my $sth = $mydb->prepare($sql);
	$sth->execute();
	while(my @row = $sth->fetchrow_array()){
		push(@DATA,join("\t",@row));
		undef @row;
	}
	$sth->finish();
	undef $sth;
	return(@DATA);
}

sub existsTable {
	my $tablename = shift;
	return 0 unless(defined $tablename);
	my $dbh = &get_dbh();
	my $sth = $dbh->prepare(qq|select tablename from pg_tables where tablename=?|);
	$sth->execute($tablename);
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

my $sth_tree_path2root;
sub getTree_Path2Root {
	my $form = shift;
	my $f_id = shift;
	my $TREE_ROUTE = shift;
	my $route = shift;

	my $dbh = &get_dbh();
	$sth_tree_path2root = $dbh->prepare(qq|select f_pid,t_delcause from tree where f_id=? and t_type=? and tg_id=? and tgi_id=?|) unless(defined $sth_tree_path2root);

	my $exists_flag;
	my $t_delcause_flag;

	unless(defined $route){
		$route = $f_id;
	}else{
		my @TEMP_ROUTE = split(/\t/,$route);
		foreach my $temp_fid (@TEMP_ROUTE){
			next if(!($temp_fid eq $f_id));
			$exists_flag = 1;
			last;
		}
		$route .= qq|\t$f_id|;
	}

	my @F_PID = ();
	unless(defined $exists_flag){
		$sth_tree_path2root->execute($f_id,$form->{t_type},$form->{tg_id},$form->{tgi_id});
		if($sth_tree_path2root->rows>0){
			my $f_pid;
			my $t_delcause;
			my $column_number = 0;
			$sth_tree_path2root->bind_col(++$column_number, \$f_pid, undef);
			$sth_tree_path2root->bind_col(++$column_number, \$t_delcause, undef);
			while($sth_tree_path2root->fetch){
				if(defined $t_delcause){
					$t_delcause_flag = 1;
				}else{
					push(@F_PID,$f_pid);
				}
			}
		}
		$sth_tree_path2root->finish;
	}
	if(scalar @F_PID > 0){
		foreach my $f_pid (@F_PID){
			&getTree_Path2Root($form,$f_pid,$TREE_ROUTE,$route);
			last if(scalar @TREE_ROUTE > 100);
		}
	}elsif(!defined $exists_flag && !defined $t_delcause_flag){
		push(@$TREE_ROUTE,$route);
	}
}

my $sth_fma_phy;
sub get_phy_id {
	my $f_id = shift;
	my $phy_id;
	my $dbh = &get_dbh();
	$f_id =~ s/\D+$//g if($f_id =~ /^FMA\d+/);
	$sth_fma_phy = $dbh->prepare(qq|select phy_id from fma where f_id=?|) unless(defined $sth_fma_phy);
	$sth_fma_phy->execute($f_id);
	my $column_number = 0;
	$sth_fma_phy->bind_col(++$column_number, \$phy_id, undef);
	$sth_fma_phy->fetch;
	$sth_fma_phy->finish;
	return $phy_id;
}

sub getBP3DTablename {
	my $version = shift;
	return undef unless(defined $version);
	my $table = "bp3d_$version";
	$table =~ s/\./_/g;
	return $table;
}

sub convVersionName2RendererVersion() {
	my $form = shift;
	my $dbh = &get_dbh();

	$form->{version} = $form->{v} if(!exists($form->{version}) && exists($form->{v}));

#print LOG __LINE__,":\$form->{tg_id}=[$form->{tg_id}]\n";
#print LOG __LINE__,":\$form->{version}=[$form->{version}]\n";

	if(exists($form->{version})){
		my $tg_id;
		my $tgi_id;
		my $tgi_version;
		my $tg_model;
		my $sql = qq|select tree_group_item.tg_id,tgi_id,tgi_version,tg_model from tree_group_item left join (select tg_id,tg_model from tree_group) as g on tree_group_item.tg_id=g.tg_id where |;
		my $sth_tree_group_item;
		if(exists($form->{tg_id})){
			$sql .= qq|tree_group_item.tg_id=? and |;
			if(exists($form->{lng}) && $form->{lng} eq 'ja'){
				$sql .= qq|COALESCE(tgi_name_j,tgi_name_e)=?|;
			}else{
				$sql .= qq|tgi_name_e=?|;
			}
			$sth_tree_group_item = $dbh->prepare($sql);
			$sth_tree_group_item->execute($form->{tg_id},$form->{version});
		}else{
			if(exists($form->{lng}) && $form->{lng} eq 'ja'){
				$sql .= qq|COALESCE(tgi_name_j,tgi_name_e)=?|;
			}else{
				$sql .= qq|tgi_name_e=?|;
			}
			$sql .= qq| order by tree_group_item.tg_id,tgi_order|;
			$sth_tree_group_item = $dbh->prepare($sql);
			$sth_tree_group_item->execute($form->{version});
		}
		my $column_number = 0;
		$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_version, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tg_model, undef);
		$sth_tree_group_item->fetch;
		if(defined $tg_id && defined $tgi_id && defined $tgi_version){
			$form->{tg_id} = $tg_id;
			$form->{tgi_id} = $tgi_id;
			$form->{version_name} = $form->{version} if(exists($form->{version}));
			$form->{version} = $tgi_version;
			$form->{tg_model} = $tg_model if(defined $tg_model);
			$form->{v} = $tgi_version if(exists($form->{v}));
		}
		$sth_tree_group_item->finish;
		undef $sth_tree_group_item;
	}

#print LOG __LINE__,":\$form->{version}=[$form->{version}]\n";

	return $form->{version};
}

sub convRendererVersion2VersionName($) {
	my $form = shift;
	my $dbh = &get_dbh();

#print LOG __LINE__,":\$form->{tg_id}=[$form->{tg_id}]\n";
#print LOG __LINE__,":\$form->{version}=[$form->{version}]\n";

	if(exists($form->{version})){
		my $tg_id;
		my $tgi_id;
		my $tgi_name;
		my $sql = qq|select tg_id,tgi_id,|;
		if(exists($form->{lng}) && $form->{lng} eq 'ja'){
			$sql .= qq|COALESCE(tgi_name_j,tgi_name_e)|;
		}else{
			$sql .= qq|tgi_name_e|;
		}
		$sql .= qq| from tree_group_item where tgi_version=?|;

		my $sth_tree_group_item;
		$sth_tree_group_item = $dbh->prepare($sql);
		$sth_tree_group_item->execute($form->{version});

		my $column_number = 0;
		$sth_tree_group_item->bind_col(++$column_number, \$tg_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_id, undef);
		$sth_tree_group_item->bind_col(++$column_number, \$tgi_name, undef);
		$sth_tree_group_item->fetch;
		if(defined $tg_id && defined $tgi_id && defined $tgi_name){
			$form->{tg_id} = $tg_id;
			$form->{tgi_id} = $tgi_id;
			$form->{version_renderer} = $form->{version};
			$form->{version} = $tgi_name;
		}
		$sth_tree_group_item->finish;
		undef $sth_tree_group_item;
	}

#print LOG __LINE__,":\$form->{version}=[$form->{version}]\n";

	return $form->{version};
}

1;
