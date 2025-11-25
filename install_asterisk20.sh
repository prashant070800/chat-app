#!/bin/bash
set -e

echo "=== Stop existing asterisk service (if any) ==="
sudo systemctl stop asterisk || true
sudo systemctl disable asterisk || true

echo "=== Remove previous manual Asterisk installation paths ==="
sudo rm -rf /usr/local/etc/asterisk
sudo rm -rf /usr/local/lib/asterisk
sudo rm -rf /var/lib/asterisk
sudo rm -rf /usr/local/sbin/asterisk
sudo rm -rf /usr/local/sbin/safe_asterisk
sudo rm -rf /usr/lib/asterisk
sudo rm -rf /usr/sbin/asterisk

echo "=== Install build dependencies ==="
sudo apt update
sudo apt install -y \
    build-essential git wget subversion autoconf automake libtool \
    pkg-config libxml2-dev libncurses-dev uuid-dev libjansson-dev \
    libsqlite3-dev libssl-dev unixodbc-dev libsrtp2-dev libedit-dev \
    libldns-dev libtiff-dev libvorbis-dev libogg-dev libiksemel-dev \
    libspandsp-dev libspeex-dev libspeexdsp-dev

echo "=== Create asterisk system user ==="
sudo adduser --quiet --system --group --home /var/lib/asterisk asterisk || true

echo "=== Download and extract Asterisk 20-current (latest Asterisk 20.x) ==="
cd /usr/src
sudo rm -f asterisk-20-current.tar.gz
sudo wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-20-current.tar.gz

sudo tar -xvf asterisk-20-current.tar.gz
cd asterisk-20*/

echo "=== Configure and build ==="
sudo contrib/scripts/install_prereq install
sudo ./configure
sudo make menuselect.makeopts
sudo menuselect/menuselect --enable CORE-SOUNDS-EN-ULAW menuselect.makeopts
sudo menuselect/menuselect --enable MOH-OPSOUND-ULAW menuselect.makeopts
sudo make -j$(nproc)
sudo make install
sudo make samples
sudo make config
sudo ldconfig

echo "=== Fix permissions ==="
sudo chown -R asterisk:asterisk /var/lib/asterisk
sudo chown -R asterisk:asterisk /var/log/asterisk
sudo chown -R asterisk:asterisk /var/spool/asterisk
sudo chown -R asterisk:asterisk /usr/lib/asterisk
sudo chown -R asterisk:asterisk /etc/asterisk

echo "=== Enable and start Asterisk ==="
sudo systemctl enable asterisk
sudo systemctl start asterisk

echo "=== Installation Completed ==="
asterisk -V
