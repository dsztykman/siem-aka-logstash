FROM docker.elastic.co/logstash/logstash:latest

USER root

# Remove any unused stuff
RUN rm /usr/share/logstash/pipeline/logstash.conf && \
    /usr/share/logstash/bin/logstash-plugin install logstash-filter-translate && \
    /usr/share/logstash/bin/logstash-plugin install logstash-filter-kv

RUN yum -y install python-setuptools && \
    easy_install pip && \
    pip install edgegrid-python && \
    pip install python-consul

# Copy all the configuration files
COPY json_siem.conf /usr/share/logstash/pipeline/

# Copy python script to fetch data
COPY siem-aka.py /
COPY akamai-siem_template.json /

RUN chmod +x /siem-aka.py

# The script writes its state to consul
ENV CONSUL_HOST "consul"
ENV CONSUL_PORT "9500"
ENV CONSUL_SCHEME "http"

# This is the SIEM connector ID that is sent with API calls
ENV CONNECTORID ""

# Edgegrid credentials
ENV EG_CLIENT_TOKEN ""
ENV EG_CLIENT_SECRET ""
ENV EG_ACCESS_TOKEN ""
ENV EG_BASE_URL ""

# Set this to the actual elasticsearch URL if required
ENV ES_URL "elasticsearch:9200"

# Elasticsearch indexes will be created with this prefix
ENV ES_INDEX ""


CMD ["--path.settings=/usr/share/logstash/config"]
