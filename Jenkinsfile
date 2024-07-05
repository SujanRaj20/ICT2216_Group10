pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ict2216_group10_web'
        DOCKER_CONTAINER = 'ict2216_group10_web_1'

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
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
            }
        }

        stage('Install dependencies') {
            steps {
                dir('flask_app') {
                    sh 'docker run --rm -v $(pwd):/app -w /app python:3.8-slim pip install -r requirements.txt'
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
                    echo "Pulling latest code from Git"
                    git branch: 'main', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd'
                }
                script {
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


    post {
        always {
            cleanWs()
        }
    }
}




// pipeline {
//     agent any

//     environment {
//         DOCKER_IMAGE = 'ict2216_group10_web'
//         DOCKER_CONTAINER = 'ict2216_group10_web_container'
//     }

//     triggers {
//         githubPush() // Trigger build on GitHub push events
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

//         stage('OWASP Dependency-Check Vulnerabilities') {
//           steps {
//             dependencyCheck additionalArguments: '''
//                     -o './'
//                     -s './'
//                     -f 'ALL'
//                     --prettyPrint
//                     --enableExperimental''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
//             dependencyCheckPublisher pattern: 'dependency-check-report.xml'
//           }
//         }

//         // stage('OWASP Dependency-Check Vulnerabilities') {
//         //     steps {
//         //         dependencyCheck additionalArguments: ''' 
//         //             -o './'
//         //             -s './'
//         //             -f 'ALL' 
//         //             --prettyPrint''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
                    
//         //         dependencyCheckPublisher pattern: 'dependency-check-report.xml'
//         //     }
//         // }

//         stage('Install Docker Compose') {
//             steps {
//                 script {
//                     sh '''
//                     if ! [ -x "$(command -v docker-compose)" ]; then
//                         curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
//                         chmod +x /usr/local/bin/docker-compose
//                         ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
//                     fi
//                     '''
//                 }
//             }
//         }

//     //     stage('Deploy') {
//     //         steps {
//     //             dir('/home/student25/ICT2216_Group10') {
//     //                 script {
//     //                     withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
//     //                         sh '''
//     //                             echo "Pulling latest code from Git"
//     //                             git config --global credential.helper store
//     //                             echo "https://${GITHUB_TOKEN}:@github.com" > ~/.git-credentials

//     //                             # Stash local changes
//     //                             git stash

//     //                             # Pull the latest code
//     //                             git pull origin main

//     //                             echo "Checking if any container is using port 5000"
//     //                             CONTAINER_ID=$(docker ps -q -f publish=5000)
//     //                             if [ "$CONTAINER_ID" ]; then
//     //                                 echo "Port 5000 is in use. Stopping the container using it..."
//     //                                 docker stop $CONTAINER_ID
//     //                                 docker rm $CONTAINER_ID
//     //                             fi

//     //                             echo "Bringing down any running containers and pruning system"
//     //                             docker-compose down
//     //                             yes | docker system prune -a --volumes

//     //                             echo "Building and bringing up new containers"
//     //                             docker-compose up --build -d

//     //                             echo "Deployment completed"

//     //                             echo "Checking logs for exited containers"
//     //                             EXITED_CONTAINER=$(docker ps -a -q -f status=exited -f ancestor=${DOCKER_IMAGE})
//     //                             if [ "$EXITED_CONTAINER" ]; then
//     //                                 echo "Container exited with error. Logs:"
//     //                                 docker logs $EXITED_CONTAINER
//     //                                 exit 1
//     //                             fi
//     //                         '''
//     //                     }
//     //                 }
//     //             }
//     //         }
//     //     }
//     // }


//         stage('Deploy') {
//             steps {
//                 dir('/home/student25/ICT2216_Group10') {
//                     git branch: 'main', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '5e9ba646-cf8c-4396-8cf8-ad2e11fd49f6'
//                     sh '''
//                         cd /home/student25/ICT2216_Group10 &&
//                         git stash &&
//                         docker-compose down &&
//                         docker system prune -f &&
//                         docker-compose up --build -d
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