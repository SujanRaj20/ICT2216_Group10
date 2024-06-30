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
                    // Check if Docker is running and list running containers
                    sh 'docker ps'
                }
            }
        }

        stage('Checkout') {
            steps {
                // Checkout the source code from the SCM
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests using the built Docker image
                    sh 'docker run --rm ${DOCKER_IMAGE} pytest'
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    // Stop and remove any existing container, then run a new one
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
            // Clean the workspace after build
            cleanWs()
        }
    }
}
