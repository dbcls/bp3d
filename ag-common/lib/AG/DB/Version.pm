#パッケージ名を同じにすると、メソッドを追加（上書き）できる。
package AG::DB;
#package AG::DB::Version;
#use base qw/AG::DB/;

use strict;

#sub new {
#	my $class = shift;
#	my %args = @_;
#	my $self = new AG::DB(%args);
#	return bless $self, $class;
#}

sub latestDataVersion() {
#	return '2.0';
	my $self = shift;
	my $model = shift;
	$model = 'bp3d' unless(defined $model);
	my $dbh = $self->get_dbh();
	my $sql =<<SQL;
select
 mv_name_e
from
 model_version as mv
left join
 (select md_id,md_abbr,md_use from model) as model on model.md_id=mv.md_id
where
 md_use and
 mv_use and
 mv_publish and
 md_abbr=?
order by
 mv_order
limit 1
SQL
	my $sth = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
	$sth->execute($model) or &Carp::croak(DBI->errstr());
	my $column_number = 0;
	my $mv_name_e;
	$sth->bind_col(++$column_number, \$mv_name_e, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	return $mv_name_e;
}

sub latestRendererVersion() {
#	return '2.0.1304161700';
	my $self = shift;
	my $model = shift;
	$model = 'bp3d' unless(defined $model);
	my $dbh = $self->get_dbh();
	my $sql =<<SQL;
select
 mr_version
from
 model_revision as mr
left join
 (select md_id,md_abbr,md_use from model) as model on model.md_id=mr.md_id
left join
 (select md_id,mv_id,mv_use,mv_publish,mv_order,mv_name_e from model_version) as mv on mv.md_id=mr.md_id and mv.mv_id=mr.mv_id
where
 md_use and
 mv_use and
 mv_publish and
 mr_use and
 md_abbr=? and
 mv_name_e ~* '^[0-9.]+\$'
order by
 mv_order,
 mr_order
limit 1
SQL
	my $sth = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
	$sth->execute($model) or &Carp::croak(DBI->errstr());
	my $column_number = 0;
	my $model_revision;
	$sth->bind_col(++$column_number, \$model_revision, undef);
	$sth->fetch;
	$sth->finish;
	undef $sth;
	return $model_revision;
}

sub convDataVersion2RendererVersion() {
	my $self = shift;
	my $form = shift;
	my $cookie = shift;
	my $dbh = $self->get_dbh();

	unless(exists $form->{'version'} && defined $form->{'version'} && length $form->{'version'}){
		$form->{'version'} = $form->{'v'} if(exists $form->{'v'});
	}
	if(exists $form->{'version'} && defined $form->{'version'} && length $form->{'version'}){
		my $md_id;
		my $mv_id;
		my $mr_id;
		my $ci_id;
		my $cb_id;
		my $mv_version;
		my $md_abbr;

		my $sth_model_version;
		my $column_number;

		my $mr_md_id;
		my $mr_mv_id;

		my $sql =<<SQL;
select
 md_id,
 mv_id
from
SQL
		my @bind_values;
		if($form->{'version'} =~ /^[0-9]+\.[0-9]+\.[0-9]{10}$/){
			$sql .=<<SQL;
 model_revision
where
 mr_version=?
SQL
			push(@bind_values, $form->{'version'});
		}
		else{
			$sql .=<<SQL;
 model_version
where
SQL
			if(exists($form->{lng}) && $form->{lng} eq 'ja'){
				$sql .= qq|mv_name_j=? or mv_name_e=? or ?=ANY(mv_name_alias)|;
				push(@bind_values, $form->{'version'});
				push(@bind_values, $form->{'version'});
				push(@bind_values, $form->{'version'});
			}else{
				$sql .= qq|mv_name_e=? or ?=ANY(mv_name_alias)|;
				push(@bind_values, $form->{'version'});
				push(@bind_values, $form->{'version'});
			}
		}
		$sth_model_version = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
		$sth_model_version->execute(@bind_values) or &Carp::croak(DBI->errstr());
		$column_number = 0;
		$sth_model_version->bind_col(++$column_number, \$mr_md_id, undef);
		$sth_model_version->bind_col(++$column_number, \$mr_mv_id, undef);
		$sth_model_version->fetch;
		$sth_model_version->finish;
		undef $sth_model_version;

		if(defined $mr_md_id && defined $mr_mv_id){
			my $sql_fmt =<<SQL;
select
 mr.md_id,
 mr.mv_id,
 mr_version,
 md_abbr,
 mr.mr_id,
 mv.ci_id,
 mv.cb_id
from (
 select * from model_revision where (md_id,mv_id,mr_id) in (
  select
   mr.md_id,
   mr.mv_id,
   max(mr.mr_id) as mr_id
  from
   model_revision as mr
  left join (
   select md_id,mv_id,mv_publish,mv_delcause from model_version
  ) as mv on mr.md_id=mv.md_id and mr.mv_id=mv.mv_id
  where
   mv.mv_publish and
   mv.mv_delcause is null and
   mr.mr_use and
   mr.mr_delcause is null and
   mr.md_id=? and
   mr.mv_id %s ?
  group by
   mr.md_id,
   mr.mv_id
  order by
   mr.md_id,
   mr.mv_id %s
  limit 1
 )
) as mr 
left join (
  select md_id,md_abbr from model
 ) as md on mr.md_id=md.md_id
left join (
  select * from model_version
 ) as mv on mr.md_id=mv.md_id and mr.mv_id=mv.mv_id
order by
 mv.md_id,mr_order,mv_order
SQL
			$sql = sprintf($sql_fmt,'>=','asc');
			$sth_model_version = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
			$sth_model_version->execute($mr_md_id,$mr_mv_id) or &Carp::croak(DBI->errstr());

			if($sth_model_version->rows()<=0){	#指定バージョンより新しいバージョンが存在しない場合、バージョン名で検索し、指定バージョンより古いバージョンへ移行
				$sth_model_version->finish;
				undef $sth_model_version;

				$sql = sprintf($sql_fmt,'<','desc');
				$sth_model_version = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());
				$sth_model_version->execute($mr_md_id,$mr_mv_id) or &Carp::croak(DBI->errstr());
			}
		}
		if(defined $sth_model_version){
			if($sth_model_version->rows()){
				$column_number = 0;
				$sth_model_version->bind_col(++$column_number, \$md_id, undef);
				$sth_model_version->bind_col(++$column_number, \$mv_id, undef);
				$sth_model_version->bind_col(++$column_number, \$mv_version, undef);
				$sth_model_version->bind_col(++$column_number, \$md_abbr, undef);
				$sth_model_version->bind_col(++$column_number, \$mr_id, undef);
				$sth_model_version->bind_col(++$column_number, \$ci_id, undef);
				$sth_model_version->bind_col(++$column_number, \$cb_id, undef);
				$sth_model_version->fetch;
				if(defined $md_id && defined $mv_id && defined $mr_id && defined $mv_version){
					$form->{'md_id'} = $md_id;
					$form->{'mv_id'} = $mv_id;
					$form->{'mr_id'} = $mr_id;
					$form->{'ci_id'} = $ci_id;
					$form->{'cb_id'} = $cb_id;
					$form->{'version_name'} = $form->{'version'} if(exists($form->{'version'}));
					$form->{'version'} = $mv_version;
					$form->{'md_abbr'} = $md_abbr if(defined $md_abbr);
					$form->{'v'} = $mv_version if(exists($form->{'v'}));
				}
			}
			$sth_model_version->finish;
			undef $sth_model_version;
		}
	}
	return $form->{'version'};
}

1;
