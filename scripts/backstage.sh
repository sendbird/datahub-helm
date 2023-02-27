#!/bin/bash
# This script creates/updates creates a YAML spec to the repo
# for Backstage for Data Platform

while getopts p:d:k:t: flag
do
    case "${flag}" in
        p) project=${OPTARG};;
        d) description=${OPTARG};;
        k) kind=${OPTARG};;
        t) type=${OPTARG};;
	esac
done
echo "===========Here are the args received:=============="
echo "Project: $project";
echo "Description: $description";
echo "Kind: $kind";
echo "Type: $type";

echo "=====Wrote following lines to project $project====="

tee $(pwd)/$project/catalog-info.yaml <<EOF
apiVersion: backstage.io/v1alpha1
kind: $kind
metadata:
  name: $project
  description: $description
  annotations:
    github.com/project-slug: sendbird/$project
spec:
  type: $type
  lifecycle: production
  owner: team-data-platform
  system: sendbird-data-platform
EOF
