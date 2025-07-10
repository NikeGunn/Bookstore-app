# Setting Up Jenkins on AWS for Docker Deployment

This guide will help you set up Jenkins on an AWS EC2 instance to automate the deployment of your Bookstore API application.

## Step 1: Launch an AWS EC2 Instance

1. Log in to your AWS Management Console
2. Navigate to EC2 and click "Launch Instance"
3. Choose Amazon Linux 2023 or Ubuntu 22.04
4. Select t2.medium (or larger) instance type (Jenkins needs at least 2GB RAM)
5. Configure security group to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443)
   - Jenkins (port 8080)
6. Launch the instance and download your key pair (.pem file)

## Step 2: Connect to Your EC2 Instance

```bash
# Set proper permissions for your key file
chmod 400 your-key.pem

# SSH into your instance
ssh -i your-key.pem ec2-user@your-instance-public-ip
```

## Step 3: Install Docker and Docker Compose

```bash
# Update package manager
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes to take effect
exit
# SSH back in
```

## Step 4: Install Jenkins

```bash
# Add Jenkins repository
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install Java (required for Jenkins)
sudo yum install -y java-17-amazon-corretto

# Install Jenkins
sudo yum install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Add Jenkins to docker group so it can use Docker
sudo usermod -a -G docker jenkins
sudo systemctl restart jenkins
```

## Step 5: Configure Jenkins

1. Get the Jenkins admin password:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

2. Open Jenkins in your browser:
```
http://your-instance-public-ip:8080
```

3. Follow the setup wizard:
   - Enter the admin password
   - Install suggested plugins
   - Create an admin user

4. Install additional plugins:
   - Go to "Manage Jenkins" → "Manage Plugins" → "Available"
   - Install these plugins:
     - Docker Pipeline
     - Pipeline
     - Git Integration
     - Credentials Binding

## Step 6: Set Up Docker Hub Credentials

1. Go to "Manage Jenkins" → "Manage Credentials"
2. Click on "Jenkins" → "Global credentials" → "Add Credentials"
3. Set up Docker Hub credentials:
   - Kind: Username with password
   - ID: dockerHub
   - Username: Your Docker Hub username
   - Password: Your Docker Hub password
   - Description: Docker Hub Credentials

## Step 7: Create a Jenkins Pipeline

1. On the Jenkins dashboard, click "New Item"
2. Enter a name (e.g., "Bookstore API")
3. Select "Pipeline" and click "OK"
4. In the pipeline configuration:
   - Under "Pipeline", select "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: Your GitHub repository URL
   - Credentials: Add your GitHub credentials if it's a private repo
   - Branch Specifier: */main (or your default branch)
   - Script Path: Jenkinsfile
5. Click "Save"

## Step 8: Run the Pipeline

1. Go to your pipeline and click "Build Now"
2. Jenkins will:
   - Clone your repository
   - Build a Docker image
   - Push it to Docker Hub
   - Deploy the application

## Step 9: Set Up Webhook for Automatic Builds

1. In your Jenkins pipeline, click "Configure"
2. Check "GitHub hook trigger for GITScm polling"
3. Save the configuration
4. In your GitHub repository:
   - Go to Settings → Webhooks → Add webhook
   - Payload URL: http://your-instance-public-ip:8080/github-webhook/
   - Content type: application/json
   - Secret: (leave empty or create a secret)
   - Events: Just the push event
   - Click "Add webhook"

## Step 10: Access Your Deployed Application

After successful deployment, your application will be available at:

- HTTPS: https://your-instance-public-ip
- API Documentation: https://your-instance-public-ip/api/v1/docs/
- Health Check: https://your-instance-public-ip/api/v1/health/

## Common Issues

### Docker Permission Issues

If Jenkins can't run Docker commands:
```bash
sudo chmod 666 /var/run/docker.sock
```

### Memory Issues

If Jenkins or Docker runs out of memory:
1. Increase your EC2 instance size
2. Add swap space:
```bash
sudo dd if=/dev/zero of=/swapfile bs=128M count=32
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

### SSL Certificate Warnings

The setup uses self-signed certificates. For production:
1. Purchase a domain name
2. Use Let's Encrypt to get free SSL certificates:
```bash
sudo amazon-linux-extras install epel
sudo yum install -y certbot
sudo certbot certonly --standalone -d yourdomain.com
```

## Next Steps

1. Set up monitoring with CloudWatch
2. Configure automatic backups
3. Implement proper domain name and SSL certificates
4. Set up staging and production environments
