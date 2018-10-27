FROM docker.elastic.co/elasticsearch/elasticsearch:6.2.4

ADD ./docker/elasticsearch/stopwords.txt /usr/share/elasticsearch/config

RUN mkdir /usr/share/elasticsearch/config/hunspell

ADD ./docker/elasticsearch/hunspell /usr/share/elasticsearch/config/hunspell


