pipeline {
  agent any
    stages {
      stage('Build') {
        steps {
          echo("Build")
        }
      }
      stage('Unit Test') {
        steps {
        sh 'pip install --upgrade pip'
        sh'pip install -r requirements.txt'
        }
        post{
          always{
            junit testResults: 'logs/unitreport.xml'
          }
        }
      }

      stage ('Integration Test'){
        steps{
          sh 'pip install --upgrade pip'
          sh 'pip install -r requirements.txt'
        }
      }

      stage('OWASP DependencyCheck') {
        steps {
          dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
        }
      }

      stage('Deploy') {
              steps {
                  dir('/home/student25/ICT2216_Group10/flask_app') {
                      git branch: 'test', url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: 'd642c4ab-aa9a-4c7f-81b5-c65def995a47'
                  }
                  sh '''
                      cd /home/student25/ICT2216_Group10/flask_app &&
                      docker-compose down &&
                      docker system prune -f &&
                      docker-compose up --build -d
                  '''
              }
          }
    
    post {
      success {
        dependencyCheckPublisher pattern: 'dependency-check-report.xml'
      }
    }
  }
}




// pipeline {
//     agent any
//     tools {
//         nodejs '22.3.0'
//     }

//     stages {

//         stage("Test Docker") {
//             agent any
//             steps {
//                 sh 'docker ps'
//             }
//         }

//         stage('Checkout') {
//             agent any
//             steps {
//                 checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/SujanRaj20/ICT2216_Group10.git', credentialsId: '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']]])
//             }
//         }

//         stage('Install dependencies') {
//             agent any 
//             steps {
//                 dir('ICT2216_Group10') {
//                     sh 'npm install'
//                 }
//             }
//         }

//         stage('OWASP Dependency Check') {
//             agent any 
//             steps {
//                 dir('ICT2216_Group10') {
//                     dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
//                 }
//             }
//         }

//         stage('Build Frontend Docker Image') {
//             steps {
//                 script {
//                     // Build Docker image for deployment
//                     // Stop and remove any existing container with the same name
//                     sh 'docker stop frontend  true'
//                     sh 'docker rm frontend  true'
//                     sh 'docker image rm frontend-image:latest || true'
//                     sh 'docker build -t frontend-image:latest inf2216-lion-lockers'
//                 }
//             }
//         }

//         stage('Test Frontend') {
//             agent {
//                 docker {
//                     image 'frontend-image:latest'
//                     reuseNode true
//                 }
//             }
//             steps {
//                 script {
//                     sh 'echo Testing Frontend'
//                     // sh 'npm test'
//                 }
//             }
//         }

//         stage('Deploy Frontend') {
//             steps {
//                 script {
//                     // Run Docker container on the host machine
//                     sh 'docker run -d -p 3000:3000 --name frontend --network=containers_jenkins frontend-image:latest'
//                 }
//             }
//         }
//     }

//     post {
//         success {
//             dir('inf2216-lion-lockers') {
//                 dependencyCheckPublisher pattern: './dependency-check-report.xml'
//             }
//         }
//         always {
//             cleanWs()
//         }
//     }
// }