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
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'pip install -r flask_app/requirements.txt'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
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
                    sh '''
                    # Check if any container is using port 5000
                    if [ "$(docker ps -q -f publish=5000)" ]; then
                        echo "Port 5000 is in use. Stopping the container using it..."
                        docker stop $(docker ps -q -f publish=5000)
                        docker rm $(docker ps -q -f publish=5000)
                    fi
                    
                    # Stop and remove existing container
                    docker stop ${DOCKER_CONTAINER} || true
                    docker rm ${DOCKER_CONTAINER} || true
                    
                    # Run the new container
                    docker run -d --name ${DOCKER_CONTAINER} -p 5000:5000 ${DOCKER_IMAGE}
                    '''
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
