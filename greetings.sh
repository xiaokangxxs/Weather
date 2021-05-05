#!/bin/sh

set -eux

sudo timedatectl set-timezone "Asia/Shanghai"

sudo apt install -y language-pack-zh-hans language-pack-zh-hant
sudo `which update-locale` LANG=zh_CN.UTF-8

USER=$1
PARTY=$2
CORP_ID=$3
CORP_SECRET=$4

python MorningGreetings.py --user $USER --party $PARTY --corpid $CORP_ID --corpsecret $CORP_SECRET >> morning_greetings.html
