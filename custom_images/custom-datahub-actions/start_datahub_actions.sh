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

# Copyright 2021 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

touch /tmp/datahub/logs/actions/actions.out

# Deploy System Actions
if [ "$(ls -A /etc/datahub/actions/system/conf/)" ]; then
    config_files=""
    # .yml
    for file in /etc/datahub/actions/system/conf/*.yml;
    do
        if [ -f "$file" ]; then
            config_files+="-c $file "
        fi
    done
    #.yaml
    for file in /etc/datahub/actions/system/conf/*.yaml;
    do
        if [ -f "$file" ]; then
            config_files+="-c $file "
        fi
    done
else
    echo "No system action configurations found. Not starting system actions."
fi

# Deploy User Actions
if [ "$(ls -A /etc/datahub/actions/conf/)" ]; then
    # .yml
    for file in /etc/datahub/actions/conf/*.yml;
    do
        if [ -f "$file" ]; then
            config_files+="-c $file "
        fi
    done
    #.yaml
    for file in /etc/datahub/actions/conf/*.yaml;
    do
        if [ -f "$file" ]; then
            config_files+="-c $file "
        fi
    done
else
    echo "No user action configurations found. Not starting user actions."
fi

sleep 36500d
