// pipeline {
//     agent any

//     environment {
//         DOCKER_IMAGE = 'ict2216_group10_web'
//         DOCKER_CONTAINER = 'ict2216_group10_web_1'
//     }

//     triggers {
//         githubPush() // Trigger build on GitHub push events
//     }

//     stages {
//         stage("List Docker Images") {
//             steps {
//                 script {
//                     echo "Listing Docker images..."
//                     sh 'docker images'
//                 }
//             }
//         }

//         stage("Test Docker") {
//             steps {
//                 echo "Testing Docker setup..."
//                 sh 'docker ps'
//             }
//         }

//         stage('Checkout') {
//             steps {
//                 echo "Checking out code from GitHub..."
//                 checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
//                 echo "Pulling latest code from GitHub..."
//                 sh 'git pull origin main'
//                 sh 'echo "Current branch:" && git branch'
//                 sh 'echo "Latest commit:" && git log -1'
//             }
//         }

//         stage('Install dependencies') {
//             steps {
//                 echo "Installing dependencies..."
//                 dir('flask_app') {
//                     sh 'docker run --rm -v $(pwd):/app -w /app python:3.8-slim pip install -r requirements.txt'
//                 }
//             }
//         }

//         stage('OWASP Dependency-Check Vulnerabilities') {
//             steps {
//                 echo "Running OWASP Dependency-Check Vulnerabilities..."
//                 dependencyCheck additionalArguments: '''
//                         -o './'
//                         -s './'
//                         -f 'ALL'
//                         --prettyPrint
//                         --enableExperimental''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
//                 dependencyCheckPublisher pattern: 'dependency-check-report.xml'
//             }
//         }

//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     echo "Building Docker image..."
//                     sh '''
//                     cd ${WORKSPACE}
//                     if [ -f Dockerfile ]; then
//                         docker build --no-cache -t ${DOCKER_IMAGE} .
//                     else
//                         echo "Dockerfile not found in root directory"
//                         exit 1
//                     fi
//                     '''
//                 }
//             }
//         }

//         stage('Run Tests') {
//             steps {
//                 script {
//                     echo "Running tests..."
//                     sh '''
//                     docker run --rm ${DOCKER_IMAGE} pytest || echo "No tests found. Skipping..."
//                     '''
//                 }
//             }
//         }

//         stage('Deploy') {
//             steps {
//                 echo "Deploying application..."
//                 dir('/home/student25/ICT2216_Group10') {
//                     echo "Pulling latest code from Git"
//                     sh '''
//                         git pull origin main
//                         echo "After git pull, listing files:"
//                         ls -la
//                         echo "Shutting down existing Docker containers..."
//                         docker-compose down
//                         echo "Pruning Docker system..."
//                         docker system prune -f
//                         echo "Building and starting Docker containers..."
//                         docker-compose up --build --force-recreate -d
//                     '''
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             echo "Cleaning workspace..."
//             cleanWs()
//         }
//     }
// }



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
                    echo "Listing Docker images..."
                    sh 'docker images'
                }
            }
        }

        stage("Test Docker") {
            steps {
                echo "Testing Docker setup..."
                sh 'docker ps'
            }
        }

        stage('Checkout') {
            steps {
                echo "Checking out code from GitHub..."
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
                echo "Pulling latest code from GitHub..."
                sh 'git pull origin main'
                sh 'echo "Current branch:" && git branch'
                sh 'echo "Latest commit:" && git log -1'
            }
        }

        stage('Install dependencies') {
            steps {
                echo "Installing dependencies..."
                dir('flask_app') {
                    sh 'docker run --rm -v $(pwd):/app -w /app python:3.8-slim pip install -r requirements.txt'
                }
            }
        }

        stage('OWASP Dependency-Check Vulnerabilities') {
            steps {
                echo "Running OWASP Dependency-Check Vulnerabilities..."
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
                    echo "Building Docker image..."
                    sh '''
                    cd ${WORKSPACE}
                    if [ -f Dockerfile ]; then
                        docker build --no-cache -t ${DOCKER_IMAGE} .
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
                    echo "Running tests..."
                    sh '''
                    docker run --rm ${DOCKER_IMAGE} pytest || echo "No tests found. Skipping..."
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application..."
                dir('/home/student25/ICT2216_Group10') {
                    script {
                        sh '''
                            echo "Shutting down existing Docker containers..."
                            docker-compose down
                            echo "Pruning Docker system..."
                            docker system prune -f
                            echo "Building and starting Docker containers..."
                            docker-compose up --build --force-recreate -d
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
    }
}
