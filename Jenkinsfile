pipeline {
    agent any
 
    environment {
        DOCKER_IMAGE = 'ict2216_group10_web'
        DOCKER_CONTAINER = 'ict2216_group10_web_container'
    }

    stages {

        stage("Test Docker") {
            steps {
                sh 'docker ps'
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                script {
                    // Run the installation inside a Python Docker container
                    docker.image('python:3.8-slim').inside {
                        sh 'pip install -r flask_app/requirements.txt'
                    }
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    sh """
                    docker stop ${DOCKER_CONTAINER} || true
                    docker rm ${DOCKER_CONTAINER} || true
                    docker run -d --name ${DOCKER_CONTAINER} -p 5000:5000 ${DOCKER_IMAGE}
                    """
                }
            }
        }
    }

    post {
        success {
            // Publish dependency check report if required
            dependencyCheckPublisher pattern: './dependency-check-report.xml'
        }
        always {
            cleanWs()
        }
    }
}
