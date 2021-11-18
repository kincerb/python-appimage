#!/usr/bin/env groovy

node('rhel7') {
    stage('Fetch cpython source') {
        def cpythonSource = checkout([$class: 'GitSCM', branches: [[name: '**']], extensions: [], userRemoteConfigs: [[name: 'origin', refspec: '+refs/tags/v3*:+refs/remotes/origin/tags/v3*', url: 'https://github.com/python/cpython']]])
        echo "Checked out commit: ${cpythonSource.GIT_COMMIT}"
        echo "Branch: ${cpythonSource.BRANCH}"
    }
}