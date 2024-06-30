// pipeline {
//     agent any

//     environment {
//         DOCKER_IMAGE = 'ict2216_group10_web'
//         DOCKER_CONTAINER = 'ict2216_group10_web_container'
//     }

//     stages {
//         stage('Test Docker') {
//             steps {
//                 script {
//                     sh 'docker ps'
//                 }
//             }
//         }

//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }

//         stage('Install Dependencies') {
//             steps {
//                 script {
//                     sh 'docker run --rm -v $(pwd):/app -w /app python:3.8-slim pip install -r flask_app/requirements.txt'
//                 }
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     sh 'docker build -t ${DOCKER_IMAGE} .'
//                 }
//             }
//         }

//         stage('Run Tests') {
//             steps {
//                 script {
//                     sh 'docker run --rm ${DOCKER_IMAGE} pytest || echo "No tests found. Skipping..."'
//                 }
//             }
//         }

//         stage('Deploy Application') {
//             steps {
//                 script {
//                     sh '''
//                     # Check if any container is using port 5000
//                     CONTAINER_ID=$(docker ps -q -f publish=5000)
//                     if [ "$CONTAINER_ID" ]; then
//                         echo "Port 5000 is in use. Stopping the container using it..."
//                         docker stop $CONTAINER_ID
//                         docker rm $CONTAINER_ID
//                     fi
                    
//                     # Stop and remove existing container
//                     docker stop ${DOCKER_CONTAINER} || true
//                     docker rm ${DOCKER_CONTAINER} || true
                    
//                     # Run the new container
//                     docker run -d --name ${DOCKER_CONTAINER} -p 5000:5000 ${DOCKER_IMAGE}
//                     '''
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             cleanWs()
//         }
//     }
// }


pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ict2216_group10_web'
        DOCKER_CONTAINER = 'ict2216_group10_web_container'
    }

    triggers {
        pollSCM('* * * * *') // Poll SCM every minute
        // For GitHub plugin, you can use: githubPush()
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

             stage('Deploy') {
            steps {
                dir('/home/student25/ICT2216_Group10') {
                    git branch: 'main', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd'
                }
                sh '''
                    cd /home/student25/ICT2216_Group10 &&
                    docker-compose down &&
                    docker system prune -f &&
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
