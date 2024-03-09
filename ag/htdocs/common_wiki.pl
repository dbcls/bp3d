use strict;
use JSON::XS;

sub fmalist {
	my $dbh = shift;
	my $params = shift;
	my $DATAS = {
		"datas" => [],
		"total" => 0
	};

	my $sql;
	$sql  = qq|select|;
	$sql .= qq| fma.f_id|;
	$sql .= qq|,fma.f_taid as taid|;
	$sql .= qq|,fma.f_name_j as name_j|;
	$sql .= qq|,fma.f_name_k as name_k|;
	$sql .= qq|,fma.f_name_e as name_e|;
	$sql .= qq|,fma.f_name_l as name_l|;
	$sql .= qq|,fma.f_syn_j  as syn_j|;
	$sql .= qq|,fma.f_syn_e  as syn_e|;
	$sql .= qq| from fma|;

	print LOG __LINE__,":sql=[$sql]\n";

	my @bind_values;
	my $sth = $dbh->prepare($sql.qq| where f_delcause is null|);
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values);
	}else{
		$sth->execute();
	}
	$DATAS->{total} = int($sth->rows());
	$sth->finish;
	undef $sth;
	print LOG __LINE__,":\$DATAS->{total}=[$DATAS->{total}]\n";

	my $order_by = '';
	if(exists $params->{sort} && defined $params->{sort}){
		my $sorter;
		eval{$sorter = &JSON::XS::decode_json($params->{sort});};
		if(defined $sorter && ref $sorter eq 'ARRAY'){
			my @s_arr = ();
			foreach my $s (@$sorter){
#select f_id,f_name_e from fma order by to_number(substring(f_id from '[0-9]+$'),'999999999') desc;
				if($s->{'property'} eq 'f_id'){	#FMAIDを数値順にソートするため
					my $o = qq|case substring(f_id from '^[^0-9]+') when 'FMA' then to_char(to_number(substring(f_id from '[0-9]+\$'),'000000000'),'000000000') when 'BP' then to_char(to_number(substring(f_id from '[0-9]+\$'),'000000000'),'000000000') else f_id end |;
					$o .= $s->{'direction'}.' NULLS LAST';
#					push(@s_arr,qq|to_number(substring(f_id from '[0-9]+\$'),'999999999') |.$s->{'direction'}.' NULLS LAST');
					push(@s_arr,$o);
				}else{
					push(@s_arr,($s->{'property'}=~/^f_/ ? qq|lower($s->{'property'})| : qq|lower(f_$s->{'property'})|).' '.$s->{'direction'}.' NULLS LAST');
				}
			}
			$order_by = ' order by '.join(',',@s_arr) if(scalar @s_arr > 0);
		}
	}

	if(exists $params->{limit} && defined $params->{limit} && exists $params->{'target'} && defined $params->{'target'} && !defined $params->{'page'}){
#		my $s = $sql . qq| where f_id<=? order by f_id|;
#		my $s = $sql . qq| where f_id<=? and f_delcause is null|;
		my $s = $sql . qq| where |;
		if($params->{'target'} =~ /^(FMA|BP:?)/){
			$s .= qq|to_number(substring(f_id from '[0-9]+\$'),'999999999')<=to_number(substring(? from '[0-9]+\$'),'999999999')|;
		}else{
			$s .= qq|f_id<=?|;
		}
		$s .= qq| and f_delcause is null|;

		$s .= $order_by;

		print LOG __LINE__,":\$s=[$s]\n";

		my $sth = $dbh->prepare($s);
		$sth->execute($params->{'target'});
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;

		print LOG __LINE__,":\$rows=[$rows]\n";
		$rows -= 1 if($rows>0);

		$DATAS->{page} = int($rows/$params->{limit})+1;
		$params->{start} = $params->{limit} * ($DATAS->{page}-1);
	}elsif(defined $params->{'page'}){
		$DATAS->{page} = $params->{'page'};
	}

	$sql .= qq| where f_delcause is null|;

#	$sql .= qq| order by f_id|;
	$sql .= $order_by;


	if(exists $params->{limit} && defined $params->{limit}){
		$sql .= qq| limit $params->{limit}|;
	}else{
		$sql .= qq| limit 3000|;
	}
	$sql .= qq| offset $params->{start}| if(exists($params->{start}));

	print LOG __LINE__,":sql=[$sql]\n";

	my $sth = $dbh->prepare($sql);

	if(scalar @bind_values > 0){
		$sth->execute(@bind_values);
	}else{
		$sth->execute();
	}
	print LOG __LINE__,":rows=[",$sth->rows(),"]\n";

	my $f_id;
	my $taid;
	my $name_j;
	my $name_k;
	my $name_e;
	my $name_l;
	my $syn_j;
	my $syn_e;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$f_id, undef);
	$sth->bind_col(++$column_number, \$taid, undef);
	$sth->bind_col(++$column_number, \$name_j, undef);
	$sth->bind_col(++$column_number, \$name_k, undef);
	$sth->bind_col(++$column_number, \$name_e, undef);
	$sth->bind_col(++$column_number, \$name_l, undef);
	$sth->bind_col(++$column_number, \$syn_j, undef);
	$sth->bind_col(++$column_number, \$syn_e, undef);

	while($sth->fetch){
=pod
		&utf8::decode($f_id)   unless(&utf8::is_utf8($f_id));
		&utf8::decode($taid)   unless(&utf8::is_utf8($taid));
		&utf8::decode($name_j) unless(&utf8::is_utf8($name_j));
		&utf8::decode($name_k) unless(&utf8::is_utf8($name_k));
		&utf8::decode($name_e) unless(&utf8::is_utf8($name_e));
		&utf8::decode($name_l) unless(&utf8::is_utf8($name_l));
		&utf8::decode($syn_j)  unless(&utf8::is_utf8($syn_j));
		&utf8::decode($syn_e)  unless(&utf8::is_utf8($syn_e));
=cut
		push(@{$DATAS->{datas}},{
			f_id => $f_id,
			taid => $taid,
			name_j => $name_j,
			name_k => $name_k,
			name_e => $name_e,
			name_l => $name_l,
			syn_j  => $syn_j,
			syn_e  => $syn_e,
		});
	}
	$sth->finish;
	undef $sth;

	return $DATAS;
}

=pod
55:$PARAMS{basepagename}=[skin.obj]
55:$PARAMS{limit}=[50]
55:$PARAMS{namespace}=[bp3d]
55:$PARAMS{sort}=[[{"property":"f_id","direction":"ASC"}]]
55:$PARAMS{start}=[0]
55:$PARAMS{target}=[bp3d:skin.obj]
55:$PARAMS{title}=[bp3d_frame]
55:$PARAMS{type}=[objlist]

select distinct
 o1.tg_id,
 o1.tgi_id,
 o1.obj_id,
 o1.obj_revision
,tg.tg_model
,tgi.tgi_name_e
from obj_files as o1
left join (select tg_id,tg_model from tree_group) as tg on (tg.tg_id=o1.tg_id)
left join (select tg_id,tgi_id,tgi_name_e from tree_group_item) as tgi on (tgi.tg_id=o1.tg_id and tgi.tgi_id=o1.tgi_id)
where
 o1.obj_delcause is null and
 o1.tg_id=1 and
 (o1.tg_id,o1.obj_id,o1.obj_revision) = (select o2.tg_id,o2.obj_id,o2.obj_revision from obj_files as o2 where o1.tg_id=o2.tg_id and o1.obj_id=o2.obj_id order by o2.obj_revision desc limit 1)
order by o1.obj_id;
=cut
#=pod
sub objlist {
	my $dbh = shift;
	my $params = shift;
	my $DATAS = {
		"datas" => [],
		"total" => 0
	};

	my $sql;
	$sql  = qq|select|;
	$sql .= qq| o1.tg_id|;
	$sql .= qq|,o1.tgi_id|;
	$sql .= qq|,o1.obj_id as id|;
	$sql .= qq|,o1.obj_revision as revision|;
	$sql .= qq|,to_char(o1.obj_data_size,'999,999,990') as data_size|;
	$sql .= qq|,to_char(o1.obj_decimate_size,'999,999,990') as decimate_size|;
	$sql .= qq|,to_char(o1.obj_xmin,'99,990.9999') as xmin|;
	$sql .= qq|,to_char(o1.obj_xmax,'99,990.9999') as xmax|;
	$sql .= qq|,to_char(o1.obj_ymin,'99,990.9999') as ymin|;
	$sql .= qq|,to_char(o1.obj_ymax,'99,990.9999') as ymax|;
	$sql .= qq|,to_char(o1.obj_zmin,'99,990.9999') as zmin|;
	$sql .= qq|,to_char(o1.obj_zmax,'99,990.9999') as zmax|;

	$sql .= qq|,to_char((o1.obj_xmax+o1.obj_xmin)/2,'99,990.9999') as xcenter|;
	$sql .= qq|,to_char((o1.obj_ymax+o1.obj_ymin)/2,'99,990.9999') as ycenter|;
	$sql .= qq|,to_char((o1.obj_zmax+o1.obj_zmin)/2,'99,990.9999') as zcenter|;

	$sql .= qq|,to_char(o1.obj_volume,'99,990.9999') as volume|;
	$sql .= qq|,to_char(o1.obj_cube_volume,'999,990.9999') as cube_volume|;
	$sql .= qq|,o1.obj_comment as comment|;

#	$sql .= qq|,EXTRACT(EPOCH FROM o1.obj_entry) as entry|;
	$sql .= qq|,to_char(o1.obj_entry,'YYYY/MM/DD HH24:MI:SS') as entry|;

	$sql .= qq|,o1.obj_e_openid as openid|;
	$sql .= qq|,tg.tg_model as model|;
	$sql .= qq|,tgi.tgi_name_e as tag|;
	$sql .= qq| from obj_files as o1|;

	$sql .= qq| left join (select tg_id,tg_model from tree_group) as tg on (tg.tg_id=o1.tg_id)|;
	$sql .= qq| left join (select tg_id,tgi_id,tgi_name_e from tree_group_item) as tgi on (tgi.tg_id=o1.tg_id and tgi.tgi_id=o1.tgi_id)|;

	my $where = qq| where|;
	$where .= qq| o1.obj_delcause is null|;
	$where .= qq| and (o1.tg_id,o1.obj_id,o1.obj_revision) = (select o2.tg_id,o2.obj_id,o2.obj_revision from obj_files as o2 where o1.tg_id=o2.tg_id and o1.obj_id=o2.obj_id order by o2.obj_revision desc limit 1)|;

	my @bind_values;

#	if(exists($params->{obj_id})){
#		$where .= qq| and o1.obj_id=?|;
#		push(@bind_values,$params->{obj_id});
#	}

	if(exists($params->{namespace})){
		my $tg_id;
		my $sql_tree_group;
		$sql_tree_group  = qq|select|;
		$sql_tree_group .= qq| tree_group.tg_id|;
		$sql_tree_group .= qq| from tree_group|;
		$sql_tree_group .= qq| where tg_model~*?|;
		my $sth_tree_group = $dbh->prepare($sql_tree_group);
		$sth_tree_group->execute('^'.$params->{namespace}.'$');
		$sth_tree_group->bind_col(1, \$tg_id, undef);
		$sth_tree_group->fetch;
		$sth_tree_group->finish;
		undef $sth_tree_group;
		if(defined $tg_id){
			$where .= qq| and o1.tg_id=?|;
			push(@bind_values,$tg_id);
		}
	}

	print LOG __LINE__,":sql=[$sql$where]\n";

	my $sth = $dbh->prepare(qq|$sql$where|);
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values);
	}else{
		$sth->execute();
	}
	$DATAS->{total} = int($sth->rows());
	$sth->finish;
	undef $sth;
	print LOG __LINE__,":\$DATAS->{total}=[$DATAS->{total}]\n";

	my $order_by = '';
	if(exists $params->{sort} && defined $params->{sort}){
		my $sorter;
		eval{$sorter = &JSON::XS::decode_json($params->{sort});};
		if(defined $sorter && ref $sorter eq 'ARRAY'){
			my @s_arr = ();
			foreach my $s (@$sorter){
				if($s->{'property'} eq 'model'){
					push(@s_arr, qq|lower(tg.tg_model) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'tag'){
					push(@s_arr, qq|lower(tgi.tgi_name_e) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'obj_id'){
					push(@s_arr, qq|lower(o1.obj_id) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'revision' || $s->{'property'} eq 'comment' || $s->{'property'} eq 'e_openid'){
					push(@s_arr, qq|lower(o1.obj_$s->{'property'}) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'xcenter' || $s->{'property'} eq 'ycenter' || $s->{'property'} eq 'zcenter'){
					if($s->{'property'} eq 'xcenter'){
						push(@s_arr, qq|(o1.obj_xmax+o1.obj_xmin)/2 |.$s->{'direction'}.' NULLS LAST');
					}elsif($s->{'property'} eq 'ycenter'){
						push(@s_arr, qq|(o1.obj_ymax+o1.obj_ymin)/2 |.$s->{'direction'}.' NULLS LAST');
					}elsif($s->{'property'} eq 'zcenter'){
						push(@s_arr, qq|(o1.obj_zmax+o1.obj_zmin)/2 |.$s->{'direction'}.' NULLS LAST');
					}
				}else{
					push(@s_arr, qq|o1.obj_$s->{'property'} |.$s->{'direction'}.' NULLS LAST');
				}
			}
			$order_by = ' order by '.join(',',@s_arr) if(scalar @s_arr > 0);
		}
	}

#=pod
	if(exists $params->{limit} && defined $params->{limit} && exists $params->{'basepagename'} && defined $params->{'basepagename'} && !defined $params->{'page'}){
		my $s = qq|$sql$where|;
		$s .= qq| and o1.obj_id<=?|;

		$s .= $order_by;

		print LOG __LINE__,":\$s=[$s]\n";

		my @b;
		push(@b,@bind_values);
		push(@b,$params->{'basepagename'});

		my $sth = $dbh->prepare($s);
		$sth->execute(@b);
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;

		print LOG __LINE__,":\$rows=[$rows]\n";
		$rows -= 1 if($rows>0);

		$DATAS->{page} = int($rows/$params->{limit})+1;
		$params->{start} = $params->{limit} * ($DATAS->{page}-1);
	}elsif(defined $params->{'page'}){
		$DATAS->{page} = $params->{'page'};
	}
#=cut

	$sql .= $where;

#	$sql .= qq| order by f_id|;
	$sql .= $order_by;


	if(exists $params->{limit} && defined $params->{limit}){
		$sql .= qq| limit $params->{limit}|;
	}else{
		$sql .= qq| limit 3000|;
	}
	$sql .= qq| offset $params->{start}| if(exists($params->{start}));

	print LOG __LINE__,":sql=[$sql]\n";

	my $sth = $dbh->prepare($sql);

	if(scalar @bind_values > 0){
		$sth->execute(@bind_values);
	}else{
		$sth->execute();
	}
	print LOG __LINE__,":rows=[",$sth->rows(),"]\n";

	my $tg_id;
	my $tgi_id;
	my $obj_id;
	my $revision;
	my $data_size;
	my $decimate_size;
	my $xmin;
	my $xmax;
	my $ymin;
	my $ymax;
	my $zmin;
	my $zmax;

	my $xcenter;
	my $ycenter;
	my $zcenter;

	my $volume;
	my $cube_volume;
	my $comment;
	my $entry;
	my $openid;
	my $model;
	my $tag;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$tg_id, undef);
	$sth->bind_col(++$column_number, \$tgi_id, undef);
	$sth->bind_col(++$column_number, \$obj_id, undef);
	$sth->bind_col(++$column_number, \$revision, undef);
	$sth->bind_col(++$column_number, \$data_size, undef);
	$sth->bind_col(++$column_number, \$decimate_size, undef);
	$sth->bind_col(++$column_number, \$xmin, undef);
	$sth->bind_col(++$column_number, \$xmax, undef);
	$sth->bind_col(++$column_number, \$ymin, undef);
	$sth->bind_col(++$column_number, \$ymax, undef);
	$sth->bind_col(++$column_number, \$zmin, undef);
	$sth->bind_col(++$column_number, \$zmax, undef);

	$sth->bind_col(++$column_number, \$xcenter, undef);
	$sth->bind_col(++$column_number, \$ycenter, undef);
	$sth->bind_col(++$column_number, \$zcenter, undef);

	$sth->bind_col(++$column_number, \$volume, undef);
	$sth->bind_col(++$column_number, \$cube_volume, undef);
	$sth->bind_col(++$column_number, \$comment, undef);
	$sth->bind_col(++$column_number, \$entry, undef);
	$sth->bind_col(++$column_number, \$openid, undef);
	$sth->bind_col(++$column_number, \$model, undef);
	$sth->bind_col(++$column_number, \$tag, undef);

	while($sth->fetch){
=pod
		&utf8::decode($tg_id)         unless(&utf8::is_utf8($tg_id));
		&utf8::decode($tgi_id)        unless(&utf8::is_utf8($tgi_id));
		&utf8::decode($obj_id)        unless(&utf8::is_utf8($obj_id));
		&utf8::decode($revision)      unless(&utf8::is_utf8($revision));
		&utf8::decode($data_size)     unless(&utf8::is_utf8($data_size));
		&utf8::decode($decimate_size) unless(&utf8::is_utf8($decimate_size));
		&utf8::decode($xmin)          unless(&utf8::is_utf8($xmin));
		&utf8::decode($xmax)          unless(&utf8::is_utf8($xmax));
		&utf8::decode($ymin)          unless(&utf8::is_utf8($ymin));
		&utf8::decode($ymax)          unless(&utf8::is_utf8($ymax));
		&utf8::decode($zmin)          unless(&utf8::is_utf8($zmin));
		&utf8::decode($zmax)          unless(&utf8::is_utf8($zmax));

		&utf8::decode($xcenter)       unless(&utf8::is_utf8($xcenter));
		&utf8::decode($ycenter)       unless(&utf8::is_utf8($ycenter));
		&utf8::decode($zcenter)       unless(&utf8::is_utf8($zcenter));

		&utf8::decode($volume)        unless(&utf8::is_utf8($volume));
		&utf8::decode($cube_volume)   unless(&utf8::is_utf8($cube_volume));
		&utf8::decode($comment)       unless(&utf8::is_utf8($comment));
		&utf8::decode($entry)         unless(&utf8::is_utf8($entry));
		&utf8::decode($openid)        unless(&utf8::is_utf8($openid));
		&utf8::decode($model)         unless(&utf8::is_utf8($model));
		&utf8::decode($tag)           unless(&utf8::is_utf8($tag));
=cut
		push(@{$DATAS->{datas}},{
			tg_id         => $tg_id,
			tgi_id        => $tgi_id,
			obj_id        => $obj_id,
			revision      => $revision,
			data_size     => $data_size,
			decimate_size => $decimate_size,
			xmin          => $xmin,
			xmax          => $xmax,
			ymin          => $ymin,
			ymax          => $ymax,
			zmin          => $zmin,
			zmax          => $zmax,

			xcenter       => $xcenter,
			ycenter       => $ycenter,
			zcenter       => $zcenter,

			volume        => $volume,
			cube_volume   => $cube_volume,
			comment       => $comment,
			entry         => $entry,
			e_openid      => $openid,
			model         => $model,
			tag           => $tag,
		});
	}
	$sth->finish;
	undef $sth;

	return $DATAS;
}
#=cut

sub representationlist {
	my $dbh = shift;
	my $params = shift;
	my $DATAS = {
		"datas" => [],
		"total" => 0
	};

	my $sql;
	$sql  = qq|select|;
	$sql .= qq| r2.tg_id|;
	$sql .= qq|,r2.tgi_id|;
	$sql .= qq|,r2.rep_id as id|;
	$sql .= qq|,r2.rep_revision as revision|;

	$sql .= qq|,to_char(r2.rep_xmin,'99,990.9999') as xmin|;
	$sql .= qq|,to_char(r2.rep_xmax,'99,990.9999') as xmax|;
	$sql .= qq|,to_char(r2.rep_ymin,'99,990.9999') as ymin|;
	$sql .= qq|,to_char(r2.rep_ymax,'99,990.9999') as ymax|;
	$sql .= qq|,to_char(r2.rep_zmin,'99,990.9999') as zmin|;
	$sql .= qq|,to_char(r2.rep_zmax,'99,990.9999') as zmax|;

	$sql .= qq|,to_char((r2.rep_xmax+r2.rep_xmin)/2,'99,990.9999') as xcenter|;
	$sql .= qq|,to_char((r2.rep_ymax+r2.rep_ymin)/2,'99,990.9999') as ycenter|;
	$sql .= qq|,to_char((r2.rep_zmax+r2.rep_zmin)/2,'99,990.9999') as zcenter|;

	$sql .= qq|,to_char(r2.rep_volume,'99,990.9999') as volume|;
	$sql .= qq|,to_char(r2.rep_cube_volume,'999,990.9999') as cube_volume|;
	$sql .= qq|,r2.rep_comment as comment|;

	$sql .= qq|,to_char(r2.rep_entry,'YYYY/MM/DD HH24:MI:SS') as entry|;
	$sql .= qq|,r2.rep_e_openid as e_openid|;

	$sql .= qq|,tg.tg_model as model|;
	$sql .= qq|,tgi.tgi_name_e as tag|;

	$sql .= qq|,tt.t_name_e as tree|;
	$sql .= qq|,r1.ic_id as ic_id|;

	$sql .= qq| from representation_data as r2|;

	$sql .= qq| left join (select tg_id,tg_model from tree_group) as tg on (tg.tg_id=r2.tg_id)|;
	$sql .= qq| left join (select tg_id,tgi_id,tgi_name_e from tree_group_item) as tgi on (tgi.tg_id=r2.tg_id and tgi.tgi_id=r2.tgi_id)|;

	$sql .= qq| left join (select tg_id,t_type,ic_id,rep_id,rep_comment,rep_delcause,rep_entry,rep_e_openid from representation) as r1 on (r1.tg_id=r2.tg_id and r1.rep_id=r2.rep_id)|;

	$sql .= qq| left join (select t_type,t_name_e from tree_type where t_delcause is null) as tt on (tt.t_type=r1.t_type)|;

	my $where = qq| where|;
	$where .= qq| r2.rep_delcause is null|;
	$where .= qq| and r1.rep_delcause is null|;
	$where .= qq| and (r2.tg_id,r2.rep_id,r2.rep_revision) = (select r3.tg_id,r3.rep_id,r3.rep_revision from representation_data as r3 where r2.tg_id=r3.tg_id and r2.rep_id=r3.rep_id order by r3.rep_revision desc limit 1)|;

	my @bind_values;

	if(exists($params->{namespace})){
		my $tg_id;
		my $sql_tree_group;
		$sql_tree_group  = qq|select|;
		$sql_tree_group .= qq| tree_group.tg_id|;
		$sql_tree_group .= qq| from tree_group|;
		$sql_tree_group .= qq| where tg_model~*?|;
		my $sth_tree_group = $dbh->prepare($sql_tree_group);
		$sth_tree_group->execute('^'.$params->{namespace}.'$');
		$sth_tree_group->bind_col(1, \$tg_id, undef);
		$sth_tree_group->fetch;
		$sth_tree_group->finish;
		undef $sth_tree_group;
		if(defined $tg_id){
			$where .= qq| and r2.tg_id=?|;
			push(@bind_values,$tg_id);
		}
	}

	print LOG __LINE__,":sql=[$sql$where]\n";

	my $sth = $dbh->prepare(qq|$sql$where|);
	if(scalar @bind_values > 0){
		$sth->execute(@bind_values);
	}else{
		$sth->execute();
	}
	$DATAS->{total} = int($sth->rows());
	$sth->finish;
	undef $sth;
	print LOG __LINE__,":\$DATAS->{total}=[$DATAS->{total}]\n";

	my $order_by = '';
	if(exists $params->{sort} && defined $params->{sort}){
		my $sorter;
		eval{$sorter = &JSON::XS::decode_json($params->{sort});};
		if(defined $sorter && ref $sorter eq 'ARRAY'){
			my @s_arr = ();
			foreach my $s (@$sorter){
				if($s->{'property'} eq 'model'){
					push(@s_arr, qq|lower(tg.tg_model) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'tag'){
					push(@s_arr, qq|lower(tgi.tgi_name_e) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'tree'){
					push(@s_arr, qq|lower(tt.t_name_e) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'ic_id'){
					push(@s_arr, qq|lower(r1.ic_id) |.$s->{'direction'}.' NULLS LAST');

				}elsif($s->{'property'} eq 'rep_id'){
					push(@s_arr, qq|lower(r2.rep_id) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'revision' || $s->{'property'} eq 'comment' || $s->{'property'} eq 'e_openid'){
					push(@s_arr, qq|lower(r2.rep_$s->{'property'}) |.$s->{'direction'}.' NULLS LAST');
				}elsif($s->{'property'} eq 'xcenter' || $s->{'property'} eq 'ycenter' || $s->{'property'} eq 'zcenter'){
					if($s->{'property'} eq 'xcenter'){
						push(@s_arr, qq|(r2.rep_xmax+r2.rep_xmin)/2 |.$s->{'direction'}.' NULLS LAST');
					}elsif($s->{'property'} eq 'ycenter'){
						push(@s_arr, qq|(r2.rep_ymax+r2.rep_ymin)/2 |.$s->{'direction'}.' NULLS LAST');
					}elsif($s->{'property'} eq 'zcenter'){
						push(@s_arr, qq|(r2.rep_zmax+r2.rep_zmin)/2 |.$s->{'direction'}.' NULLS LAST');
					}
				}else{
					push(@s_arr, qq|r2.rep_$s->{'property'} |.$s->{'direction'}.' NULLS LAST');
				}
			}
			$order_by = ' order by '.join(',',@s_arr) if(scalar @s_arr > 0);
		}
	}

	if(exists $params->{limit} && defined $params->{limit} && exists $params->{'basepagename'} && defined $params->{'basepagename'} && !defined $params->{'page'}){
		my $s = qq|$sql$where|;
		$s .= qq| and r2.rep_id<=?|;
		$s .= $order_by;
		print LOG __LINE__,":\$s=[$s]\n";

		my @b;
		push(@b,@bind_values);

		if($params->{'basepagename'} =~ /^(FMA|BP:?)/){
			my $rep_id;
			my $sth = $dbh->prepare(qq|select rep_id from representation where rep_delcause is null and ic_id=? order by rep_id|);
			$sth->execute($params->{'basepagename'});
			my $column_number = 0;
			$sth->bind_col(++$column_number, \$rep_id, undef);
			$sth->fetch;
			$sth->finish;
			undef $sth;
			if(defined $rep_id){
				push(@b,$rep_id);
				$DATAS->{'rep_id'} = $rep_id;
			}else{
				push(@b,$params->{'basepagename'});
			}
		}else{
			push(@b,$params->{'basepagename'});
		}

		my $sth = $dbh->prepare($s);
		$sth->execute(@b);
		my $rows = $sth->rows();
		$sth->finish;
		undef $sth;

		print LOG __LINE__,":\$rows=[$rows]\n";
		$rows -= 1 if($rows>0);

		$DATAS->{page} = int($rows/$params->{limit})+1;
		$params->{start} = $params->{limit} * ($DATAS->{page}-1);
	}elsif(defined $params->{'page'}){
		$DATAS->{page} = $params->{'page'};
	}

	$sql .= $where;

#	$sql .= qq| order by f_id|;
	$sql .= $order_by;


	if(exists $params->{limit} && defined $params->{limit}){
		$sql .= qq| limit $params->{limit}|;
	}else{
		$sql .= qq| limit 3000|;
	}
	$sql .= qq| offset $params->{start}| if(exists($params->{start}));

	print LOG __LINE__,":sql=[$sql]\n";

	my $sth = $dbh->prepare($sql);

	if(scalar @bind_values > 0){
		$sth->execute(@bind_values);
	}else{
		$sth->execute();
	}
	print LOG __LINE__,":rows=[",$sth->rows(),"]\n";

	my $tg_id;
	my $tgi_id;
	my $rep_id;
	my $revision;
	my $xmin;
	my $xmax;
	my $ymin;
	my $ymax;
	my $zmin;
	my $zmax;

	my $xcenter;
	my $ycenter;
	my $zcenter;

	my $volume;
	my $cube_volume;
	my $comment;
	my $entry;
	my $openid;
	my $model;
	my $tag;

	my $type;
	my $ic_id;

	my $column_number = 0;
	$sth->bind_col(++$column_number, \$tg_id, undef);
	$sth->bind_col(++$column_number, \$tgi_id, undef);
	$sth->bind_col(++$column_number, \$rep_id, undef);
	$sth->bind_col(++$column_number, \$revision, undef);

	$sth->bind_col(++$column_number, \$xmin, undef);
	$sth->bind_col(++$column_number, \$xmax, undef);
	$sth->bind_col(++$column_number, \$ymin, undef);
	$sth->bind_col(++$column_number, \$ymax, undef);
	$sth->bind_col(++$column_number, \$zmin, undef);
	$sth->bind_col(++$column_number, \$zmax, undef);

	$sth->bind_col(++$column_number, \$xcenter, undef);
	$sth->bind_col(++$column_number, \$ycenter, undef);
	$sth->bind_col(++$column_number, \$zcenter, undef);

	$sth->bind_col(++$column_number, \$volume, undef);
	$sth->bind_col(++$column_number, \$cube_volume, undef);
	$sth->bind_col(++$column_number, \$comment, undef);

	$sth->bind_col(++$column_number, \$entry, undef);
	$sth->bind_col(++$column_number, \$openid, undef);

	$sth->bind_col(++$column_number, \$model, undef);
	$sth->bind_col(++$column_number, \$tag, undef);

	$sth->bind_col(++$column_number, \$type, undef);
	$sth->bind_col(++$column_number, \$ic_id, undef);

	while($sth->fetch){
=pod
		&utf8::decode($tg_id)         unless(&utf8::is_utf8($tg_id));
		&utf8::decode($tgi_id)        unless(&utf8::is_utf8($tgi_id));
		&utf8::decode($obj_id)        unless(&utf8::is_utf8($obj_id));
		&utf8::decode($revision)      unless(&utf8::is_utf8($revision));
		&utf8::decode($data_size)     unless(&utf8::is_utf8($data_size));
		&utf8::decode($decimate_size) unless(&utf8::is_utf8($decimate_size));
		&utf8::decode($xmin)          unless(&utf8::is_utf8($xmin));
		&utf8::decode($xmax)          unless(&utf8::is_utf8($xmax));
		&utf8::decode($ymin)          unless(&utf8::is_utf8($ymin));
		&utf8::decode($ymax)          unless(&utf8::is_utf8($ymax));
		&utf8::decode($zmin)          unless(&utf8::is_utf8($zmin));
		&utf8::decode($zmax)          unless(&utf8::is_utf8($zmax));

		&utf8::decode($xcenter)       unless(&utf8::is_utf8($xcenter));
		&utf8::decode($ycenter)       unless(&utf8::is_utf8($ycenter));
		&utf8::decode($zcenter)       unless(&utf8::is_utf8($zcenter));

		&utf8::decode($volume)        unless(&utf8::is_utf8($volume));
		&utf8::decode($cube_volume)   unless(&utf8::is_utf8($cube_volume));
		&utf8::decode($comment)       unless(&utf8::is_utf8($comment));
		&utf8::decode($entry)         unless(&utf8::is_utf8($entry));
		&utf8::decode($openid)        unless(&utf8::is_utf8($openid));
		&utf8::decode($model)         unless(&utf8::is_utf8($model));
		&utf8::decode($tag)           unless(&utf8::is_utf8($tag));
=cut
		push(@{$DATAS->{datas}},{
			tg_id         => $tg_id,
			tgi_id        => $tgi_id,
			rep_id        => $rep_id,
			revision      => $revision,

			xmin          => $xmin,
			xmax          => $xmax,
			ymin          => $ymin,
			ymax          => $ymax,
			zmin          => $zmin,
			zmax          => $zmax,

			xcenter       => $xcenter,
			ycenter       => $ycenter,
			zcenter       => $zcenter,

			volume        => $volume,
			cube_volume   => $cube_volume,
			comment       => $comment,
			entry         => $entry,
			e_openid      => $openid,
			model         => $model,
			tag           => $tag,

			tree          => $type,
			ic_id         => $ic_id,
		});
	}
	$sth->finish;
	undef $sth;

	return $DATAS;
}

1;
