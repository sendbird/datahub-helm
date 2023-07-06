#!/bin/bash

# usage:
# ./upload_image_to_ecr.sh {image_version}

if [ $# -ne 1 ];
then echo "You must specify 1 parameter: image_version" && exit 0;
fi

image_version=$1
account_id=314716043882
aws_region="ap-northeast-2"

docker buildx build --platform linux/arm64,linux/amd64 -f Dockerfile -t dataplatform/rivendell:$image_version .
docker tag dataplatform/rivendell:$image_version $account_id.dkr.ecr.$aws_region.amazonaws.com/dataplatform/rivendell:$image_version
aws ecr get-login-password --region $aws_region | docker login --username AWS --password-stdin $account_id.dkr.ecr.$aws_region.amazonaws.com
docker push $account_id.dkr.ecr.$aws_region.amazonaws.com/dataplatform/rivendell:$image_version
