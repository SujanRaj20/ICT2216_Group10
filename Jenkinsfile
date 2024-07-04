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
        stage("List Docker Images") {
            steps {
                script {
                    sh 'docker images'
                }
            }
        }

        stage("Test Docker") {
            steps {
                sh 'docker ps'
            }
        }

        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '5e9ba646-cf8c-4396-8cf8-ad2e11fd49f6']]])
            }
        }

        stage('Install dependencies') {
            steps {
                dir('flask_app') {
                    sh 'docker run --rm -v $(pwd):/app -w /app python:3.8-slim pip install -r requirements.txt'
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                dir('flask_app') {
                    dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                    cd ${WORKSPACE}
                    if [ -f Dockerfile ]; then
                        docker build -t ${DOCKER_IMAGE} .
                    else
                        echo "Dockerfile not found in root directory"
                        exit 1
                    fi
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    docker run --rm ${DOCKER_IMAGE} pytest || echo "No tests found. Skipping..."
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('/home/student25/ICT2216_Group10') {
                    script {
                        withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                            sh '''
                                echo "Pulling latest code from Git"
                                git config --global credential.helper store
                                echo "https://${GITHUB_TOKEN}:@github.com" > ~/.git-credentials

                                # Stash local changes
                                git stash

                                # Pull the latest code
                                git pull origin main

                                echo "Checking if any container is using port 5000"
                                CONTAINER_ID=$(docker ps -q -f publish=5000)
                                if [ "$CONTAINER_ID" ]; then
                                    echo "Port 5000 is in use. Stopping the container using it..."
                                    docker stop $CONTAINER_ID
                                    docker rm $CONTAINER_ID
                                fi

                                echo "Bringing down any running containers and pruning system"
                                docker-compose down
                                docker system prune -f

                                echo "Building and bringing up new containers"
                                docker-compose up --build -d

                                echo "Deployment completed"
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            dir('flask_app') {
                dependencyCheckPublisher pattern: './dependency-check-report.xml'
            }
        }
        always {
            cleanWs()
        }
    }
}
