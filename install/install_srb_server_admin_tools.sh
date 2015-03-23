#!/bin/bash

# This script is for installing server-packages.
# Some of them must be configured later.
# Testet with ubuntu-server 14.04 in 2015
#
# Dieses kleine Script uebernimmt die Instalaltion 
# der SRB-Tools fuer Admin-SRB auf dem Server
# Bei einigen ist eine spaetere Configuration noetig
# Author: Joerg Sorge
# Distributed under the terms of GNU GPL version 2 or later
# Copyright (C) Joerg Sorge joergsorge@gmail.com
# 2013-05-27
#


echo "SRB-Admin-Tools Installation..."
echo "Load Admin-SRB from git..."

git clone https://github.com/srb-fm/admin-srb.git

echo "Make Path ~/srb-tools"
mkdir ~/srb-tools

echo "Copy Tools"
cp "$(pwd)"/admin-srb/tools/*.py ~/srb-tools
cp "$(pwd)"/admin-srb/tools/*.sh ~/srb-tools
cp "$(pwd)"/admin-srb/tools/*.template ~/srb-tools
echo "Make Tools executable"
chmod u+x ~/srb-tools/*.py
chmod u+x ~/srb-tools/*.sh

echo "Make path ~/srb-intra"
sudo mkdir /var/www/srb-intra
echo "Change User:Group for srb-intra"
sudo chown $USER:www-data /var/www/srb-intra
echo "Make symbolic link from /var/www/srb-intra to home"
ln -s /var/www/srb-intra ~/
mkdir ~/srb-intra/public_html
mkdir ~/srb-intra/cgi-bin
mkdir ~/srb-intra/cgi-bin/admin_srb_libs

echo "Copy intra" 
sudo cp -R "$(pwd)"/admin-srb/intra/* ~/srb-intra/public_html
sudo cp -R "$(pwd)"/admin-srb/intra/admin_srb_libs/ ~/srb-intra/cgi-bin/

echo "Change user:group for srb-export"
sudo chown -R www-data:www-data ~/srb-intra/public_html/admin_srb_export

echo "Folder admin-srb will continue stay for later use of install-scripts..."
echo "To complete intra-webserver-config check your webserver-config, especially the doc-root-definition"
echo "...finish"
read -p "Press Enter to close..."
exit
