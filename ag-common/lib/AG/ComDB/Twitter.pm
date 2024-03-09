package AG::ComDB::Twitter;

use base qw/AG::ComDB/;

use strict;
use Carp;

#sub new {
#	my $class = shift;
#	my %args = @_;
#	my $self = new AG::ComDB(%args);
#	return bless $self, $class;
#}

sub get_tweets {
	my $self = shift;
	my $rep_id = shift;
	my $mca_id = shift;

	my @REP_IDS;
	if(defined $rep_id){
		if(ref $rep_id eq 'ARRAY'){
			push(@REP_IDS,@$rep_id);
		}else{
			push(@REP_IDS,$rep_id);
		}
	}

	my $dbh = $self->get_dbh();

	my $tweets = undef;
	my $tweet_num = 0;
	if(scalar @REP_IDS){
		my $tw_id;
		my $tw_text;
		my $tw_created;
		my $tw_user_scname;
		my $tw_user_name;
		my $tw_user_piuhs;
		my @bind_fields = map {'?'} @REP_IDS;
		my $sql = qq|select rep_id,ts.tw_id,ts.tw_text,ts.tw_created,ts.tw_user_scname,ts.tw_user_name,ts.tw_user_piuhs from representation_twitter as rt left join(select * from twitter_search) ts on ts.tw_id=rt.tw_id where rep_id IN (|.join(",",@bind_fields).qq|) order by rtw_entry desc|;
		my $sth = $dbh->prepare($sql) or &Carp::croak(DBI->errstr());;
		$sth->execute(@REP_IDS) or &Carp::croak(DBI->errstr());;
		my $column_number = 0;
		$sth->bind_col(++$column_number, \$rep_id, undef);
		$sth->bind_col(++$column_number, \$tw_id, undef);
		$sth->bind_col(++$column_number, \$tw_text, undef);
		$sth->bind_col(++$column_number, \$tw_created, undef);
		$sth->bind_col(++$column_number, \$tw_user_scname, undef);
		$sth->bind_col(++$column_number, \$tw_user_name, undef);
		$sth->bind_col(++$column_number, \$tw_user_piuhs, undef);
		while($sth->fetch){
#					next unless(defined $tw_text && $tw_text =~ qr|http://lifesciencedb.jp|);
			$tweet_num++;
			if(defined $tw_text){
				$tw_text =~ s|http://221.186.138.155/bp3d-38321/|http://lifesciencedb.jp/bp3d/|g;
				$tw_text =~ s|http://221.186.138.155/bp3d/|http://lifesciencedb.jp/bp3d/|g;
				$tw_text =~ s|http://lifesciencedb.jp:32888/bp3d-38321/|http://lifesciencedb.jp/bp3d/|g;

				$tw_text =~ s|$rep_id|$mca_id|g if(defined $mca_id);
			}
			push(@$tweets,{
				id => $tw_id,
				text => $tw_text,
				created => $tw_created+0,
				user_scname => $tw_user_scname,
				user_name => $tw_user_name,
				user_piuhs => $tw_user_piuhs,
			});
		}
		$sth->finish;
		undef $sth;
	}
	return wantarray ? @$tweets : $tweets;
}

1;
