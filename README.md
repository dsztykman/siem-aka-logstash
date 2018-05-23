# Siem-aka-logstash
## [Logstash](https://www.elastic.co/guide/en/logstash/6.2/index.html) [Docker](https://www.elastic.co/guide/en/logstash/current/docker.html) Image for [Akamai SIEM connector](https://developer.akamai.com/api/luna/siem/overview.html)

To use it create an env file which will contain all the variables required.
You should setup the following variables:
```bash
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
```

In this image we're storing the offset information into [consul](https://www.consul.io/) a distributed key value store which allows multiple logstash to fetch data from Akamai