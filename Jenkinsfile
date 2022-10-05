pipeline {
    agent any
    stages {
        stage('Testing') {
            parallel {
                stage('Unit Testing') {
                    agent {
                        dockerfile {
                            filename 'docker/application/Dockerfile'
                            dir '.'
                            additionalBuildArgs '--target dev'
                            args '--network host'
                        }
                    }
                    steps {
                        echo 'Testing..'
                        sh './run_tests.sh'
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
