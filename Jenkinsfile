pipeline {
    agent any
    
    environment {
        PATH = "/usr/local/bin:$PATH"
    }
    
    tools {
        python {
            name = 'Python3'
            home = '/usr/bin/python3'
        }
    }
    
    stages {
        // Define stages here
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

    }
    
    post {
        success {
            echo 'Pipeline succeeded! Application deployed.'
        }
        failure {
            echo 'Pipeline failed! Deployment aborted.'
        }
    }
}
