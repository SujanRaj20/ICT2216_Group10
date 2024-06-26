pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh '''
                    # Your build commands here
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    # Your test commands here
                '''
            }
        }
        stage('OWASP DependencyCheck') {
            steps {
                dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
            }
        }
        stage('Deploy') {
            steps {
                dir('/home/student25/ICT2216_Group10') {
                    git branch: 'test', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: 'd642c4ab-aa9a-4c7f-81b5-c65def995a47'
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

    post {
        success {
            dependencyCheckPublisher pattern: 'dependency-check-report.xml'
        }
    }
}
