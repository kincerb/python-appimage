#!/usr/bin/env groovy

pipeline {
    agent {
        docker {
            image 'library/centos:7'
            args '--privileged -u root:root'
        }
    }

    environment {
        APPIMAGE_PYTHON_VERSION = "3.10.0"
        APPIMAGE_PYTHON_VERSION_SUFFIX = "-${APPIMAGE_PYTHON_VERSION}"
        PYTHON_APPIMAGE_HOME = "AppImage"
        PYTHON_APPIMAGE_NAME = "python-nwie-appimage-x86_64.AppImage"
        ARTIFACTORY_APPIMAGE_NAME = "python"
        ARTIFACTORY_APPIMAGE_SUMMARY = "cPython interpreter AppImage"
        ARTIFACTORY_TOP_LEVEL_NAME = "appimage-local"
    }

    stages {
        stage("Prep Workspace") {
            steps {
                script {
                    sh("yum -y install bluez-libs-devel bzip2 bzip2-devel desktop-file-utils expat-devel file fuse fuse-devel gcc gcc-c++ gdm gdbm-devel glibc glibc-devel gmp-devel make mesa-libGL-devel libX11-devel libappstream-glib libffi-devel libtirpc-devel libtool ncurses-devel net-tools openssl openssl-devel openssl-static perl-core readline-devel sqlite-devel squashfs-tools systemtap-sdt-devel tcl-devel tix-devel tk tk-devel xz-devel xz-lzma-compat zlib zlib-devel")
                    sh(script: "cd ${PYTHON_APPIMAGE_HOME} && tar -xzf cpython.tar.gz && cd cpython${APPIMAGE_PYTHON_VERSION_SUFFIX} && ./configure --enable-optimizations && make altinstall && cd .. && rm -rf cpython${APPIMAGE_PYTHON_VERSION_SUFFIX}", returnStdout: true)
                    sh("touch /etc/pip.conf && echo '[global]' >> /etc/pip.conf && echo 'timeout=30' >> /etc/pip.conf && echo 'index = http://art.nwie.net/artifactory/api/pypi/pypi' >> /etc/pip.conf && echo 'index-url = http://art.nwie.net/artifactory/api/pypi/pypi/simple' >> /etc/pip.conf && echo 'trusted-host=art.nwie.net' >> /etc/pip.conf")
                }
            }
        }

        stage("Build Python") {
            steps {
                script {
                    sh("cd ${PYTHON_APPIMAGE_HOME} && python3.10 build-appimage.py './src'  './resources'")
                }
            }
        }

        stage('Test Python Image') {
            steps {
                script {
                    sh(script: "./${PYTHON_APPIMAGE_HOME}/${PYTHON_APPIMAGE_NAME} -m ensurepip --upgrade")
                    global_test_output = sh(script: "cd tests && ./../${PYTHON_APPIMAGE_HOME}/${PYTHON_APPIMAGE_NAME} -m pip install -r requirements.txt && ./../${PYTHON_APPIMAGE_HOME}/${PYTHON_APPIMAGE_NAME} -m pytest .", returnStdout: true)
                    println(global_test_output)
                    appimage_test_output = sh(script: "cd ${PYTHON_APPIMAGE_HOME} && ./${PYTHON_APPIMAGE_NAME} python_app_image.py", returnStdout: true)
                    println(appimage_test_output)
                }
            }
        }

        /*
        stage('Upload AppImage') {
            steps {
                script {
                    artifactoryServer = Artifactory.server 'art-nwie'
                    artifactoryUploadSpec = """{
                        "files": [
                            {
                                "pattern": "${PYTHON_APPIMAGE_HOME}/${PYTHON_APPIMAGE_NAME}",
                                "target": "${ARTIFACTORY_TOP_LEVEL_NAME}/${ARTIFACTORY_APPIMAGE_NAME}/${APPIMAGE_PYTHON_VERSION}/python3.10",
                                "props": "appimage.name=${ARTIFACTORY_APPIMAGE_NAME};appimage.normalized.name=${ARTIFACTORY_APPIMAGE_NAME};appimage.version=${APPIMAGE_PYTHON_VERSION};appimage.summary=${ARTIFACTORY_APPIMAGE_SUMMARY}"
                            }
                        ]
                    }"""
                    artifactoryServer.upload spec: artifactoryUploadSpec, failNoOp: true
                }
            }
        }
        */
    }

    post {
        always { node('linux') {
            cleanWs()
        }}
    }
}
