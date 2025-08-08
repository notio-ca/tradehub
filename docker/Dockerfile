FROM ubuntu:22.04


RUN apt-get update \
    && apt-get install -y tzdata \
    && ln -fs /usr/share/zoneinfo/Canada/Eastern /etc/localtime && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get install -y curl tar wget unzip nano

# PYTHON
RUN apt-get install -y python3.10 python3-pip default-libmysqlclient-dev pkg-config \
    && echo "alias python=python3.10" >> /root/.bashrc \
    && echo "alias pip=pip3" >> /root/.bashrc


# PYTHON REQUIREMENTS
RUN pip install --upgrade pip
RUN pip install --no-cache-dir uwsgi
RUN pip install --no-cache-dir Django==4.2.11
RUN pip install --no-cache-dir django-unfold==0.47.0
RUN pip install --no-cache-dir django-debug-toolbar==4.3.0
RUN pip install --no-cache-dir python-decouple
RUN pip install --no-cache-dir requests
RUN pip install --no-cache-dir django-json-widget


COPY ./docker-entrypoint.sh /
CMD ["/docker-entrypoint.sh"]