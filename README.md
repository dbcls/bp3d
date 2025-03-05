# bp3d
BodyParts3D development by BITS

## �V�X�e���̃A�b�v�f�[�^�y�ђǉ��C���X�g�[��
```
apt update
apt upgrade
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
apt install python3-pip
```

## APR�̃C���X�g�[��
```
cd /bp3d/local/download
wget https://dlcdn.apache.org//apr/apr-1.7.4.tar.gz
tar xvfz apr-1.7.4.tar.gz
cd apr-1.7.4
./configure --prefix=/bp3d/local/apache2
make
make install
```

## APR-util�̃C���X�g�[��
```
cd /bp3d/local/download
wget https://dlcdn.apache.org//apr/apr-util-1.6.3.tar.gz
tar xvfz apr-util-1.6.3.tar.gz
cd apr-util-1.6.3
./configure --prefix=/bp3d/local/apache2 --with-apr=/bp3d/local/apache2/bin
make
make install
```

## Apache 2.4�̃C���X�g�[��
```
cd /bp3d/local/download
wget https://dlcdn.apache.org/httpd/httpd-2.4.58.tar.gz
tar xvfz httpd-2.4.56.tar.gz
cd httpd-2.4.56
./configure --prefix=/bp3d/local/apache2 --enable-mods-shared=all --enable-proxy=shared --enable-ssl=shared --with-apr=/bp3d/local/apache2/bin --with-apr-util=/bp3d/local/apache2/bin
make
make install
```

## PostgreSQL�̃C���X�g�[��
```
cd /bp3d/local/download
wget https://ftp.postgresql.org/pub/source/v15.6/postgresql-15.6.tar.gz
tar xvfz postgresql-15.6.tar.gz
cd postgresql-15.6
./configure --prefix=/bp3d/local/ --with-perl --with-systemd
make
make install
/bp3d/local/bin/initdb /bp3d/ag/pgdata
```

## VTK�̃C���X�g�[��
```
cd /bp3d/local/download
wget https://www.vtk.org/files/release/9.2/VTK-9.2.6.tar.gz
tar xvfz VTK-9.2.6.tar.gz
cd VTK-9.2.6/build
ccmake ..
make
make install
```

## perl�ւ̃V���{���b�N�����N���쐬
```
mkdir -p /bp3d/local/perl/bin
cd /bp3d/local/perl/bin
ln -s `which perl` .
```

## ���ϐ��uPATH�v�Ɂu/bp3d/local/bin�v�ւ̃p�X��擪�ɒǉ�����
```
PATH=/bp3d/local/bin:$PATH
```

## perl���W���[���̃C���X�g�[��
```
cd /bp3d
cpanm -L local --notest --prompt --installdeps .
```

## Systemd �𗘗p���ăT�[�r�X��ǉ��E�o�^����
```
cd /etc/systemd/system
sudo ln -s /bp3d/local/etc/systemd/system/ag-pgsql.service .
sudo ln -s /bp3d/local/etc/systemd/system/ag-apache2.service .
sudo systemctl enable ag-pgsql.service
sudo systemctl enable ag-apache2.service
sudo systemctl start ag-pgsql.service
sudo systemctl start ag-apache2.service
```
