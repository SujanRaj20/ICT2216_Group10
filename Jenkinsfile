pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest' // Adjust this to match your test command
            }
        }

        stage('OWASP DependencyCheck') {
            steps {
                dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    def workspace = pwd()
                    dir(workspace) {
                        git branch: 'test', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: 'd642c4ab-aa9a-4c7f-81b5-c65def995a47'
                    }
                    sh '''
                        docker-compose down &&
                        docker system prune -f -a --volumes &&
                        docker-compose up --build -d
                    '''
                }
            }
        }
    }
    
    post {
        success {
            dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        }
    }
}
