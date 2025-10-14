FROM solr:9.9.0

USER root
COPY configset /opt/solr/server/solr/configsets/mylistings
RUN chown -R solr:solr /opt/solr/server/solr/configsets/mylistings

USER solr
CMD ["solr-precreate","mylistings","/opt/solr/server/solr/configsets/mylistings"]
