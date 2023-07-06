FROM acryldata/datahub-actions:v0.0.11
USER root
RUN pip install 'gql[all]==3.4.0'
RUN apt update
RUN apt install -y logrotate cron vim
ADD logrotate.conf /etc/logrotate.d/datahub-actions
RUN sed -i '136s/                "max.poll.interval.ms": "10000"/                "max.poll.interval.ms": "300000"/g' /usr/local/lib/python3.10/site-packages/datahub_actions/plugin/source/kafka/kafka_event_source.py
ADD start_datahub_actions.sh /start_datahub_actions.sh
RUN chmod 755 /start_datahub_actions.sh
ADD *.py /etc/datahub
ADD *.yml /etc/datahub
