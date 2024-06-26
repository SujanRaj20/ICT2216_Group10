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
    agent { 
        node {
            label 'bookwise'
            }
      }
    triggers {
        pollSCM '* * * * *'
    }
    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh '''
                cd myapp
                pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                echo "Testing.."
                sh '''
                cd myapp
                python3 hello.py
                python3 hello.py --name=Brad
                '''
            }
        }
        stage('Deliver') {
            steps {
                echo 'Deliver....'
                sh '''
                echo "doing delivery stuff.."
                '''
            }
        }
    }
}