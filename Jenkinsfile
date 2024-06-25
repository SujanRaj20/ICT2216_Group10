pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 
        '''
        
        '''
      }
    }
    stage('Test') {
      steps {
        sh 
        '''
        
        '''
      }
    }

    stage('OWASP DependencyCheck') {
      steps {
        dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
      }
    }
  }  
  post {
    success {
      dependencyCheckPublisher pattern: 'dependency-check-report.xml'
    }
  }
}