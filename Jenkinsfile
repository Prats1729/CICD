pipeline {
    agent any

    environment {
        AWS_REGION     = 'ap-south-1'
        AWS_ACCOUNT_ID = '971023774760'
        ECR_REPOSITORY = 'assigment5-repo'
        IMAGE_NAME     = 'cloud-image'
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_IMAGE      = "${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
    }

    triggers {
        pollSCM('* * * * *')
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh 'python3 -m pip install --user -r requirements.txt'
                sh 'python3 test_app.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                aws ecr get-login-password --region ${AWS_REGION} | \
                docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }

        stage('Docker Tag') {
            steps {
                sh 'docker tag ${IMAGE_NAME}:latest ${ECR_IMAGE}'
            }
        }

        stage('Push to ECR') {
            steps {
                sh 'docker push ${ECR_IMAGE}'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                kubectl apply -f deployment.yaml
                kubectl apply -f service.yaml
                kubectl rollout restart deployment/studentapp-deployment
                kubectl rollout status deployment/studentapp-deployment
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
