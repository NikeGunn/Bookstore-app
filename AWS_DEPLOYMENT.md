# AWS Deployment Guide for Bookstore API

This guide provides detailed instructions for deploying the Bookstore API to AWS using Docker.

## Option 1: Deploy to EC2

### Step 1: Launch an EC2 Instance

1. Login to AWS Console and navigate to EC2
2. Launch a new instance:
   - Choose Amazon Linux 2023 or Ubuntu 22.04
   - Select t2.micro for free tier or t2.small/medium for better performance
   - Configure security group to allow:
     - SSH (port 22)
     - HTTP (port 80)
     - HTTPS (port 443)
   - Create and download a key pair

### Step 2: Connect to Your Instance

```bash
# For Amazon Linux 2023
ssh -i /path/to/your-key.pem ec2-user@your-instance-public-dns

# For Ubuntu
ssh -i /path/to/your-key.pem ubuntu@your-instance-public-dns
```

### Step 3: Install Docker and Docker Compose

```bash
# For Amazon Linux 2023
sudo dnf update -y
sudo dnf install -y docker
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

### Step 4: Deploy the Application

```bash
# Clone your repository
git clone https://your-repository-url.git
cd pyhon-store-v2

# Create .env file from example
cp .env.example .env
nano .env  # Edit with your production values

# Create SSL certificates directory
mkdir -p nginx/ssl

# Generate self-signed SSL certificate (replace with real certificate in production)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem

# Start the application
docker-compose -f docker-compose.prod.yml up -d
```

### Step 5: Set Up Domain and SSL (Optional)

1. Register a domain in Route 53 or your preferred domain registrar
2. Point your domain to your EC2 instance's public IP
3. Use Certbot to get a Let's Encrypt certificate:

```bash
# Install Certbot
sudo dnf install -y certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx ssl folder
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Set proper permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem

# Restart nginx container
docker-compose -f docker-compose.prod.yml restart nginx
```

## Option 2: Deploy with AWS ECS and RDS

For a more scalable deployment, you can use ECS (Elastic Container Service) with RDS:

### Step 1: Set Up RDS

1. Go to RDS in AWS Console
2. Create a PostgreSQL database
3. Note the endpoint, username, password, and database name

### Step 2: Create ECR Repository

1. Go to ECR in AWS Console
2. Create a new repository
3. Follow the push commands:

```bash
# Login to ECR
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com

# Build and push the image
docker build -t your-account-id.dkr.ecr.your-region.amazonaws.com/bookstore-api:latest .
docker push your-account-id.dkr.ecr.your-region.amazonaws.com/bookstore-api:latest
```

### Step 3: Set Up ECS Task Definition

1. Go to ECS in AWS Console
2. Create a new task definition:
   - Use Fargate for serverless deployment
   - Configure memory and CPU based on needs
   - Add container with your ECR image
   - Add environment variables:
     - DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
     - SECRET_KEY=your-secret-key
     - DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
     - DEBUG=0

### Step 4: Create ECS Cluster and Service

1. Create an ECS cluster
2. Create a service using your task definition
3. Configure load balancer for your service

### Step 5: Set Up Route 53 and ACM

1. Create a certificate in ACM
2. Configure DNS with Route 53
3. Connect your load balancer to your domain

## Automating Deployment with AWS CodePipeline

For automated CI/CD:

1. Store your code in AWS CodeCommit or GitHub
2. Create a CodeBuild project to build your Docker image
3. Set up CodePipeline to:
   - Pull code from your repository
   - Build the Docker image
   - Push to ECR
   - Deploy to ECS

## Monitoring and Maintenance

1. Set up CloudWatch for logs and metrics
2. Configure alerts for high CPU/memory usage
3. Set up regular database backups
4. Create a deployment rollback strategy

## Estimated AWS Costs

For a small to medium application:
- EC2 (t2.small): ~$20/month
- RDS (db.t3.micro): ~$15/month
- Load Balancer: ~$20/month
- Route 53: ~$0.50/month per hosted zone
- Data Transfer: Varies based on traffic

Total: ~$60-100/month for basic setup
