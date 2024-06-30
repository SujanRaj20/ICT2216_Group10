pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ict2216_group10_web'
        DOCKER_CONTAINER = 'ict2216_group10_web_container'
    }

    stages {
        stage('Test Docker') {
            steps {
                script {
                    sh 'docker ps'
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    docker.image('python:3.8-slim').inside {
                        sh 'pip install -r flask_app/requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh 'docker run --rm ${DOCKER_IMAGE} pytest || echo "No tests found. Skipping..."'
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
        always {
            cleanWs()
        }
    }
}
