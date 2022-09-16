#!/bin/bash
mkdir /etc/datahub/log
sleep 1
datahub actions -c /etc/datahub/sb-dw-mesg_mirror.yml >> /etc/datahub/log/sb-dw-mesg_mirror.log 2>&1 &
sleep 2
datahub actions -c /etc/datahub/soda_mirror.yml >> /etc/datahub/log/soda_mirror.log 2>&1 &
sleep 2
datahub actions -c /etc/datahub/sbdesk_mirror.yml >> /etc/datahub/log/sbdesk_mirror.log 2>&1 &
sleep 2
datahub actions -c /etc/datahub/es_mirror.yml >> /etc/datahub/log/es_mirror.log 2>&1 &

service cron restart

sleep 36500d
