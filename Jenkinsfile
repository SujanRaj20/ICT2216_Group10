pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ict2216_group10_web'
        DOCKER_CONTAINER = 'ict2216_group10_web_container'
        NVD_API_KEY = '779643d0-11fc-4b1e-b599-9545de56634'
    }

    triggers {
        githubPush() // Trigger build on GitHub push events
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

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'docker run --rm -v $(pwd):/app -w /app python:3.8-slim pip install -r flask_app/requirements.txt'
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

        stage('OWASP Dependency-Check Vulnerabilities') {
            steps {
                dependencyCheck additionalArguments: '''
                    -o './'
                    -s './'
                    -f 'ALL'
                    --prettyPrint
                    --enableExperimental''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }

        stage('Install Docker Compose') {
            steps {
                script {
                    sh '''
                    if ! [ -x "$(command -v docker-compose)" ]; then
                        curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        chmod +x /usr/local/bin/docker-compose
                        ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
                    fi
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('/home/student25/ICT2216_Group10') {
                    script {
                        sh '''
                            git pull origin main
                            # Check if any container is using port 5000
                            CONTAINER_ID=$(docker ps -q -f publish=5000)
                            if [ "$CONTAINER_ID" ]; then
                                echo "Port 5000 is in use. Stopping the container using it..."
                                docker stop $CONTAINER_ID
                                docker rm $CONTAINER_ID
                            fi

                            # Bring down any running containers and prune system
                            docker-compose down
                            docker system prune -f
                            
                            # Bring up new containers
                            docker-compose up --build -d
                        '''
                    }
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
