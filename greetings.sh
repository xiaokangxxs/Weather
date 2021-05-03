#!/bin/sh

set -eux

USER=$1
PARTY=$2
CORP_ID=$3
CORP_SECRET=$4

python MorningGreetings.py --user $USER --party $PARTY --corpid $CORP_ID --corpsecret $CORP_SECRET >> morning_greetings.html
