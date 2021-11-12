# must run with --privileged mode in docker
FROM ntr.nwie.net/library/centos:7-latest
ARG PATCHVER=10
ENV SOURCE_DIR /opt/project
COPY . ${SOURCE_DIR}/
WORKDIR ${SOURCE_DIR}/resources
RUN cp ./pip.conf /etc
RUN yum install -y fuse-sshfs
RUN ln -s ${SOURCE_DIR}/resources/python-nwie-appimage-x86_64.AppImage /usr/bin/python3.9

ENTRYPOINT python3.9 -m pip install pytest pytest-testinfra && python3.9 -m pytest -s test_python.py

