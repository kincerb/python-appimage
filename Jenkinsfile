pipeline {
    node('rhel7') {
        stages {
            stage('Fetch cpython source')
            steps {
                def cpythonSource = checkout([$class: 'GitSCM', branches: [[name: '**']], extensions: [], userRemoteConfigs: [[name: 'origin', refspec: '+refs/tags/*:+refs/remotes/origin/tags/*', url: 'https://github.com/python/cpython']]])
                echo "Checked out commit: ${cpythonSource.GIT_COMMIT}"
                echo "Branch: ${cpythonSource.BRANCH}"
            }
        }
    }
}