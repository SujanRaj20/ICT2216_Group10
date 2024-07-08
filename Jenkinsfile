pipeline {
    agent any

    triggers {
        githubPush() // Trigger build on GitHub push events
    }

    stages {
        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'eedd512c-d44b-417e-bdc7-dd81de50b856', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
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

        stage('Setup Python Environment') {
            steps {
                dir('/var/www/bookwise/flask_app') {
                    sh '''
                    # Ensure Python 3 is being used
                    python3 --version

                    # Ensure the python3-venv package is installed
                    apt-get update
                    apt-get install -y python3-venv

                    # Check if the virtual environment already exists
                    if [ ! -d "venv" ]; then
                        # Create a virtual environment if it doesn't exist
                        python3 -m venv venv

                        # Install pip in the virtual environment if not already installed
                        venv/bin/python -m ensurepip --upgrade

                        # Install setuptools and wheel
                        venv/bin/python -m pip install --upgrade pip setuptools wheel
                    fi

                    # Activate the virtual environment
                    . venv/bin/activate

                    # List directory contents for troubleshooting
                    ls -la

                    # Install dependencies using pip from the virtual environment
                    pip install -r requirements.txt
                    pip install pytest
                    pip install python-dotenv
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                # Define the target directory on the VM
                TARGET_DIR="/var/www/bookwise/flask_app"
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
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                dir('/var/www/bookwise/flask_app') {
                    script {
                    def results = sh (script: '''
                    . venv/bin/activate
                    cd "/var/jenkins_home/workspace/bookwise/flask_app/"
                    ls -la
                    cd tests
                    pytest --junitxml=unit-test-results.xml
                    ''', returnStatus: true)

                    if (results != 0) {
                        error("Build failed")
                    }
                }
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
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: 'eedd512c-d44b-417e-bdc7-dd81de50b856']]])
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
