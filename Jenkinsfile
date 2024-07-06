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
//                     -o './'
//                     -s './'
//                     -f 'ALL'
//                     --prettyPrint
//                     --enableExperimental''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
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
//                 dir('/home/student25/bookwise') {
//                     checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
//                 }

//                 script {
//                     sh '''
//                         cd /home/student25/bookwise &&
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
//             echo "Cleaning workspace..."
//             cleanWs()
//         }
//     }
// }



ppipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sshagent(['56b8991e-7ef2-465c-92b2-fc6a31da829e']) {
                        sh '''
                        #!/bin/bash

                        # Navigate to the project directory
                        cd "/var/jenkins_home/workspace/bookwise"

                        # Set up GitHub authentication
                        GIT_REPO="git@github.com:SujanRaj20/ICT2216_Group10.git"

                        # Pull the latest changes
                        git pull $GIT_REPO main
                        ''' 
                    }
                } 
            }
        }
        stage('Test') {
            steps {
                sh '''
                # Define the target directory on the VM
                TARGET_DIR="/var/www/bookwise"
                VM_USER="student25"
                VM_HOST="3.15.19.78"
   
                # Copy files to the VM
                scp -r . ${VM_USER}@${VM_HOST}:${TARGET_DIR}

                # Run commands on the remote VM to set permissions
                ssh ${VM_USER}@${VM_HOST} << EOF
                sudo chown -R ${VM_USER}:${VM_USER} ${TARGET_DIR}
                sudo chmod -R 755 ${TARGET_DIR}
                EOF
                '''
            }
        }
        
        stage('OWASP DependencyCheck') {
            steps {
                dependencyCheck additionalArguments: '--format HTML --format XML --noupdate', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
            }
        }
    }
    post {
        success {
            // Publish Dependency-Check report
            dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        }
    }
}
