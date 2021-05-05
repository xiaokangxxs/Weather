#!/bin/sh

set -eux

read -p "Timezone (default: Asia/Shanghai): " TZONE
TZONE=${TZONE:-'Asia/Shanghai'}
timedatectl set-timezone $TZONE

apt install -y language-pack-zh-hans language-pack-zh-hant
`which update-locale` LANG=zh_CN.UTF-8

USER=$1
PARTY=$2
CORP_ID=$3
CORP_SECRET=$4

python MorningGreetings.py --user $USER --party $PARTY --corpid $CORP_ID --corpsecret $CORP_SECRET >> morning_greetings.html
