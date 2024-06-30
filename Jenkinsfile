pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ict2216_group10_web'
        DOCKER_CONTAINER = 'ict2216_group10_web_1'
        GIT_REPO_URL = 'https://github.com/SujanRaj20/ICT2216_Group10.git'  // Replace with your actual repository URL
        GIT_CREDENTIALS_ID = 'd046be28-7fcb-4b42-8b65-e717b03c009b'  // Replace with your actual Jenkins credentials ID
    }

    stages {
        stage('Test Docker') {
            steps {
                sh 'docker ps'
            }
        }

        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: "${GIT_REPO_URL}", credentialsId: "${GIT_CREDENTIALS_ID}"]]])
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker stop ${DOCKER_CONTAINER} || true"
                    sh "docker rm ${DOCKER_CONTAINER} || true"
                    sh "docker rmi ${DOCKER_IMAGE}:latest || true"
                    sh "docker build -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    docker.image("${DOCKER_IMAGE}:latest").inside {
                        sh 'pip install -r requirements.txt'
                        sh 'pytest tests'
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    sh "docker run -d -p 5000:5000 --name ${DOCKER_CONTAINER} ${DOCKER_IMAGE}:latest"
                }
            }
        }
    }

    post {
        success {
            script {
                echo 'Build and deployment succeeded!'
            }
        }
        failure {
            script {
                echo 'Build or deployment failed.'
            }
        }
        always {
            cleanWs()
        }
    }
}
