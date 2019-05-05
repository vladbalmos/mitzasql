ARG VERSION
FROM python:$VERSION
ARG USER_ID

RUN mkdir -p /home/mitzasql/src
RUN useradd -U -u $USER_ID -d /home/mitzasql mitzasql
RUN chown -R mitzasql:mitzasql /home/mitzasql

RUN pip install tox
WORKDIR /home/mitzasql/src
COPY mitzasql mitzasql
COPY tests tests
COPY bin bin
COPY README.md README.md
COPY requirements.txt requirements.txt
COPY setup.py setup.py
COPY tox.ini tox.ini
ARG TOXENV
USER mitzasql
RUN tox -e $TOXENV --notest
