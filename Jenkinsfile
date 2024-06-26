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
//                     git branch: 'test', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '77deb650-7c28-4370-81f8-c512f6f03f16'
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
                sh 'npm install' 
            }
        }
    }
