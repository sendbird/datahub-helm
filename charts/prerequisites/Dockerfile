# elasticsearch custom docker image (repository-s3 plugin installed)
#ARG elasticsearch_version
#FROM docker.elastic.co/elasticsearch/elasticsearch:${elasticsearch_version}
FROM docker.elastic.co/elasticsearch/elasticsearch:7.16.2
RUN bin/elasticsearch-plugin install --batch repository-s3
