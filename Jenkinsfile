// pipeline {
//     agent any

//     triggers {
//         githubPush() // Trigger build on GitHub push events
//     }

//     stages {
//         stage('Build') {
//             steps {
//                 withCredentials([usernamePassword(credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
//                     sh '''
//                     #!/bin/bash

//                     # Start the SSH agent and add the key
//                     eval $(ssh-agent -s)
//                     ssh-add /root/.ssh/id_rsa

//                     # Navigate to the project directory
//                     cd "/var/jenkins_home/workspace/bookwise"

//                     # Set up GitHub authentication
//                     GIT_REPO="https://github.com/SujanRaj20/ICT2216_Group10.git"
//                     GIT_URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/SujanRaj20/ICT2216_Group10.git"

//                     # Pull the latest changes
//                     git pull $GIT_URL main
//                     ''' 
//                 } 
//             }
//         }

//         stage('Install Dependencies') {
//             steps {
//                 echo "Installing dependencies..."
//                 dir('/var/www/bookwise') {
//                     sh '''
//                     docker run --rm -v $(pwd):/app -w /app python:3.8-slim /bin/sh -c "pip install pytest"
//                     '''
//                 }
//             }
//         }

//         stage('Test') {
//             steps {
//                 sh '''
//                 # Define the target directory on the VM
//                 TARGET_DIR="/var/www/bookwise"
//                 VM_USER="student25"
//                 VM_HOST="3.15.19.78"

//                 # Add remote host key to known_hosts
//                 ssh-keyscan -H ${VM_HOST} >> ~/.ssh/known_hosts

//                 # Copy files to the VM
//                 scp -r . ${VM_USER}@${VM_HOST}:${TARGET_DIR}

//                 # Run commands on the remote VM to set permissions
//                 ssh ${VM_USER}@${VM_HOST} << EOF
//                 sudo chown -R ${VM_USER}:${VM_USER} ${TARGET_DIR}
//                 sudo chmod -R 755 ${TARGET_DIR}

//                 # Run pytest
//                 docker run --rm -v $(pwd):/app -w /app python:3.8-slim pytest
    
//                 '''
//             }
//         }

//         stage('OWASP DependencyCheck') {
//             steps {
//                 dependencyCheck additionalArguments: '--format HTML --format XML --noupdate', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
//             }
//         }

//         stage('Deploy') {
//             steps {
//                 dir('/var/www/bookwise') {
//                     checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
//                 }

//                 script {
//                     sh '''
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
//         success {
//             // Publish Dependency-Check report
//             dependencyCheckPublisher pattern: 'dependency-check-report.xml'
//         }
//     }
// }


pipeline {
    agent any

    triggers {
        githubPush() // Trigger build on GitHub push events
    }

    stages {
        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sh '''
                    #!/bin/bash

                    # Start the SSH agent and add the key
                    eval $(ssh-agent -s)
                    ssh-add /root/.ssh/id_rsa

                    # Navigate to the project directory
                    cd "/var/jenkins_home/workspace/bookwise"

                    # Set up GitHub authentication
                    GIT_REPO="https://github.com/SujanRaj20/ICT2216_Group10.git"
                    GIT_URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/SujanRaj20/ICT2216_Group10.git"

                    # Pull the latest changes
                    git pull $GIT_URL main
                    ''' 
                } 
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing dependencies..."
                dir('flask_app') {
                    sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.8-slim /bin/sh -c "pip install -r requirements.txt && pip install pytest"
                    '''
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

                # Add remote host key to known_hosts
                ssh-keyscan -H ${VM_HOST} >> ~/.ssh/known_hosts

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

        stage('Run Unit Tests') {
            steps {
                dir('flask_app') {
                    sh '''
                    # Run pytest
                    docker run --rm -v $(pwd):/app -w /app python:3.8-slim pytest
                    '''
                }
            }
        }

        stage('OWASP DependencyCheck') {
            steps {
                dependencyCheck additionalArguments: '--format HTML --format XML --noupdate', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
            }
        }

        stage('Deploy') {
            steps {
                dir('/var/www/bookwise') {
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '84474bb7-b0b2-4e48-8fca-03f8e49ce5cd']]])
                }

                script {
                    sh '''
                        cd /var/www/bookwise &&
                        git stash &&
                        docker-compose down &&
                        docker system prune -f &&
                        docker-compose up --build -d
                    '''
                }
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
