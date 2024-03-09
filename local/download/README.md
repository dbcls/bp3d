apt install update-manager-core
apt install cmake
apt install cmake-curses-gui/jammy-updates
apt install g++
apt install libglu1-mesa/jammy
apt install libgles2-mesa/jammy-updates libgles2-mesa-dev/jammy-updates
apt install python3-dev/jammy-updates
apt install libxcursor-dev/jammy
apt install libosmesa6-dev/jammy-updates
apt install cpanminus/jammy
apt install apache2/jammy-updates apache2-suexec-pristine/jammy-updates
apt install libgmp-dev/jammy
apt install libgd-dev/jammy
apt install imagemagick/jammy
apt install libmagick++-dev/jammy
apt install libmagickcore-dev/jammy
apt install perlmagick/jammy
apt install libssl-dev/jammy-updates
apt install icinga2
apt install unzip

cd /bp3d/local/download
tar xvfz apr-1.7.3.tar.gz
cd apr-1.7.3
./configure --prefix=/bp3d/local/apache2

cd /bp3d/local/download
tar xvfz apr-util-1.6.3.tar.gz
cd apr-util-1.6.3
./configure --prefix=/bp3d/local/apache2 --with-apr=/bp3d/local/apache2/bin

cd /bp3d/local/download
tar xvfz httpd-2.4.56.tar.gz
cd httpd-2.4.56
./configure --prefix=/bp3d/local/apache2 --enable-mods-shared=all --enable-proxy=shared --enable-ssl=shared --with-apr=/bp3d/local/apache2/bin --with-apr-util=/bp3d/local/apache2/bin

cd /bp3d/local/download
tar xvfz postgresql-15.2.tar.gz
cd postgresql-15.2
./configure --prefix=/bp3d/local/ --with-perl --with-systemd

cd /bp3d/local/download
tar xvfz VTK-9.2.6.tar.gz
cd VTK-9.2.6/build
ccmake ..

mkdir -p /bp3d/local/perl/bin
cd /bp3d/local/perl/bin
ln -s `which perl` .

# cpanmのインストール
cd /bp3d/local/bin
curl -L -O http://xrl.us/cpanm > cpanm
chmod 755 cpanm

# perlモジュールのインストール
cd /bp3d
cpanm -L local --notest --prompt --installdeps .
