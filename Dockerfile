FROM quay.io/bkincer/python:centos7-3.10

ARG PYTHON_SRC_VERSION=3.10.0
ARG OPENSSL_VERSION=1.1.1l
ARG PROJECT_DIR=/opt/project

ENV PYTHON_VERSION ${PYTHON_VERSION}
ENV OPENSSL_VERSION ${OPENSSL_VERSION}
ENV PROJECT_DIR ${PROJECT_DIR}
ENV SOURCE_DIR ${PROJECT_DIR}/src

RUN mkdir -p ${SOURCE_DIR} && \
    python3.10 -m pip install -r ./requirements.txt

WORKDIR ${SOURCE_DIR}

RUN wget --output-document=openssl.tar.gz https://openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz && \
    wget --output-document=cpython.tar.gz https://python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xzvf openssl.tar.gz && \
    tar -xzvf cpython.tar.gz

WORKDIR ${SOURCE_DIR}/openssl-${OPENSSL_VERSION}
RUN umask 0022 && \
    ./config no-shared -fPIC --prefix=/opt/openssl --openssldir=/usr/local/ssl && \
    make -j$(nproc) && \
    make test && \
    make install

WORKDIR ${SOURCE_DIR}/Python-${PYTHON_VERSION}
RUN umask 0022 && \
    ./configure --with-openssl=/opt/openssl && \
    make -j$(nproc) && \
    make test && \
    make altinstall

WORKDIR ${PROJECT_DIR}
RUN find ${SOURCE_DIR} -mindepth 1 -maxdepth 1 -exec rm -rf {} \; && \
    rm -rf ${SOURCE_DIR}

