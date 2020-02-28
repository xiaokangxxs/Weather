#!/bin/sh

set -eux

CITY=baoding
LANGUAGE="zh-CN"
UNIT=m
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0"

curl \
  -H "Accept-Language: $LANGUAGE" \
  -H "User-Agent: $UA" \
  -o weather_forecast.html \
  wttr.in/$CITY?format=3\&$UNIT
