package SetEnv;

sub new {
	my $pkg = shift;
	my $env = {
#		rendererURL  => "http://$ENV{AG_IM_HOST}:$ENV{AG_IM_PORT}/",
		rendererURL  => "http://$ENV{AG_IM_HOST}/",
		URL => {
			"image"     => undef,
			"print"     => undef,
			"animation" => undef,
			"clip"      => undef,
			"focus"     => undef,
			"focusClip" => undef,
			"pick"      => undef,
			"point"     => undef,
			"map"       => undef,
		},
		globalURL    => "http://lifesciencedb.jp/bp3d/",
		basePath     => "/bp3d/ag/htdocs/API/",
		fontPath     => "/bp3d/local/share/fonts/japanese/TrueType/sazanami-mincho.ttf",
		fontSize     => 9,
	};
	foreach my $key (keys(%{$env->{URL}})){
		$env->{URL}->{$key} = $env->{rendererURL} unless(defined $env->{URL}->{$key});
	}
	bless $env,$pkg;
}

1;

