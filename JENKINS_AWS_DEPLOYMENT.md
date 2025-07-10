# AWS Deployment with Jenkins

This guide explains how to set up continuous deployment of your Bookstore API to AWS EC2 using Jenkins.

## Architecture Overview

```
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   GitHub    │          │   Jenkins   │          │ Amazon ECR  │
│ Repository  │───Push───►   Server    │──Build───►  Registry   │
└─────────────┘          └─────────────┘          └─────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Amazon EC2 Instance                         │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│  Docker     │  Nginx      │  Django     │  PostgreSQL │  SSL    │
│  Engine     │  Container  │  Container  │  Container  │  Certs  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
```

## Prerequisites

1. An AWS account
2. A Jenkins server (can be on AWS or elsewhere)
3. Git repository for your code
4. Docker and Docker Compose installed on both Jenkins and EC2

## Step 1: Set Up AWS Resources

### Create an EC2 Instance

1. Go to AWS EC2 console
2. Launch a new EC2 instance (t2.small or larger recommended)
   - Amazon Linux 2023 or Ubuntu Server 22.04
   - At least 20GB storage
3. Configure security group:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443)
4. Create and download key pair
5. Connect to your instance:
   ```
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

### Install Docker on EC2

```bash
# For Amazon Linux 2023
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes to take effect
```

### Create ECR Repository

1. Go to Amazon ECR console
2. Create a repository named 'bookstore-api'
3. Note the repository URI

## Step 2: Set Up Jenkins

### Install Required Plugins

1. Go to Manage Jenkins > Manage Plugins > Available
2. Install the following plugins:
   - Docker Pipeline
   - AWS Steps
   - SSH Agent
   - Pipeline
   - Git Integration

### Configure Jenkins Credentials

1. Go to Manage Jenkins > Manage Credentials > Jenkins > Global credentials > Add Credentials
2. Add the following credentials:
   - **AWS Credentials**: ID: `aws-credentials`, Type: AWS Credentials
   - **ECR Registry URL**: ID: `aws-ecr-registry-url`, Type: Secret text (format: `123456789012.dkr.ecr.us-east-1.amazonaws.com`)
   - **EC2 SSH Key**: ID: `aws-ec2-ssh-key`, Type: SSH Username with private key
   - **EC2 Instance IP**: ID: `aws-ec2-instance-ip`, Type: Secret text
   - **Database Password**: ID: `db-password`, Type: Secret text
   - **Django Secret Key**: ID: `django-secret-key`, Type: Secret text

### Create Jenkins Pipeline

1. Go to Jenkins dashboard
2. Create a new item, select "Pipeline"
3. Configure Pipeline:
   - **Pipeline**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your Git repository URL
   - **Credentials**: Your Git credentials
   - **Script Path**: Jenkinsfile

## Step 3: Configure AWS IAM

1. Create an IAM user for Jenkins with the following permissions:
   - AmazonECR-FullAccess
   - AmazonEC2ContainerRegistryFullAccess
2. Generate access and secret keys
3. Add these credentials to Jenkins

## Step 4: Deploy the Application

1. Push your code to the Git repository
2. Jenkins will automatically trigger the pipeline (or manually trigger it)
3. The pipeline will:
   - Build the Docker image
   - Test the application
   - Push the image to ECR
   - Deploy to EC2
   - Verify the deployment

## Step 5: Set Up Domain and SSL (Optional)

1. Register a domain in Route 53
2. Point your domain to the EC2 instance's public IP
3. Create an SSL certificate:
   - Use AWS Certificate Manager for managed certificates
   - Or use Let's Encrypt with Certbot

## Common Issues and Solutions

### Jenkins Cannot Connect to EC2

- Verify EC2 security group allows SSH from Jenkins IP
- Check if the SSH key permissions are correct
- Make sure the EC2 instance is running

### Docker Permission Issues

- Ensure Jenkins user has permissions to run Docker
- Add Jenkins to the Docker group

### ECR Authentication Failures

- Check IAM permissions
- Verify the ECR registry URL is correct
- Make sure AWS credentials are valid

## Monitoring and Maintenance

1. Set up CloudWatch for logs and metrics
2. Configure SNS alerts for health checks
3. Create a regular backup schedule for the database
4. Implement a rolling update strategy

## Security Best Practices

1. Store all secrets in Jenkins credentials or AWS Secrets Manager
2. Never hardcode credentials in files
3. Use HTTPS for all communications
4. Keep Docker images updated
5. Regularly update dependencies

## Cost Management

To optimize costs:
- Use t2 or t3 instances for development
- Consider spot instances for non-critical environments
- Set up billing alerts
- Use auto-scaling for variable workloads
