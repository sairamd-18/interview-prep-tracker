
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t interview-tracker .'
            }
        }

        stage('Deploy Container') {
            steps {
                bat 'docker rm -f interview-tracker 2>NUL || ver >NUL'
                bat 'docker run -d --name interview-tracker -p 8000:8000 interview-tracker'
            }
        }
    }
}
