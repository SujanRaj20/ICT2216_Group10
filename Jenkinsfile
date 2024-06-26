// pipeline {
//     agent any

//     stages {
//         stage('Build') {
//             steps {
//                 sh '''
//                     # Your build commands here
//                 '''
//             }
//         }
//         stage('Test') {
//             steps {
//                 sh '''
//                     # Your test commands here
//                 '''
//             }
//         }
//         stage('OWASP DependencyCheck') {
//             steps {
//                 dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
//             }
//         }
//         stage('Deploy') {
//             steps {
//                 dir('/home/student25/ICT2216_Group10') {
//                     git branch: 'test', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: 'd642c4ab-aa9a-4c7f-81b5-c65def995a47'
//                 }
//                 sh '''
//                     cd /home/student25/ICT2216_Group10 &&
//                     docker-compose down &&
//                     docker system prune -f &&
//                     docker-compose up --build -d
//                 '''
//             }
//         }
//     }

//     post {
//         success {
//             dependencyCheckPublisher pattern: 'dependency-check-report.xml'
//         }
//     }
// }


pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Starting Build stage..."
                sh 'pip install -r requirements.txt'
                echo "Build completed."
            }
        }
        stage('Test') {
            steps {
                echo "Starting Test stage..."
                sh 'python3 app.py'
                sh 'python3 checkdbconn.py'
                echo "Test completed."
            }
        }
        stage('Deploy') {
            steps {
                echo "Starting Deploy stage..."
                dir('/home/student25/ICT2216_Group10') {
                    // Clone the repository
                    git branch: 'test', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: 'd642c4ab-aa9a-4c7f-81b5-c65def995a47'
                }
                // Run Docker commands
                sh '''
                    cd /home/student25/ICT2216_Group10 &&
                    docker-compose down &&
                    docker system prune -f &&
                    docker-compose up --build -d
                '''
                echo "Deployment completed."
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
