# Manual Deployment of Bookstore API on AWS

This guide shows how to manually deploy the Bookstore API Docker application on an AWS EC2 instance without Jenkins.

## Step 1: Launch an EC2 Instance

1. Log in to AWS Management Console
2. Navigate to EC2 and click "Launch Instance"
3. Choose an Amazon Linux 2023 or Ubuntu 22.04 AMI
4. Select t2.micro (free tier) or t2.small instance type
5. Configure security group to allow traffic on:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443)
6. Launch the instance and download your key pair

## Step 2: Connect to Your EC2 Instance

```bash
# Set proper permissions for your key
chmod 400 your-key.pem

# Connect to your instance
ssh -i your-key.pem ec2-user@your-instance-public-ip
```

## Step 3: Install Docker and Docker Compose

```bash
# Update system packages
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

## Step 4: Clone Your Repository

```bash
# Install Git
sudo yum install -y git

# Clone your repository
git clone https://github.com/yourusername/bookstore-api.git
cd bookstore-api
```

## Step 5: Set Up Environment Variables

```bash
# Create .env file
cat > .env << EOL
DEBUG=0
SECRET_KEY=your_secure_secret_key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-instance-public-ip
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOL
```

## Step 6: Create SSL Certificates

```bash
# Create directories
mkdir -p nginx/ssl

# Generate self-signed certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -subj "/CN=localhost"
```

## Step 7: Deploy with Docker Compose

```bash
# Build and start containers
docker-compose -f docker-compose.prod.yml up -d

# Check if containers are running
docker ps
```

## Step 8: Check Application Logs

```bash
# Check logs from the web container
docker-compose -f docker-compose.prod.yml logs web

# Check logs from the nginx container
docker-compose -f docker-compose.prod.yml logs nginx
```

## Step 9: Access Your Application

Your application should now be accessible at:

- HTTPS: `https://your-instance-public-ip`
- API documentation: `https://your-instance-public-ip/api/v1/docs/`
- Health check: `https://your-instance-public-ip/api/v1/health/`

Note: You will see browser warnings about the self-signed certificate.

## Step 10: Set Up Automatic Updates

Create a script to automatically pull changes and update the application:

```bash
# Create update script
cat > update.sh << 'EOL'
#!/bin/bash

# Go to project directory
cd ~/bookstore-api

# Pull latest changes
git pull

# Restart containers with new code
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Show status
echo "Update completed at $(date)"
echo "Running containers:"
docker ps
EOL

# Make script executable
chmod +x update.sh
```

## Step 11: Schedule Regular Updates (Optional)

Set up a cron job to run the update script regularly:

```bash
# Edit crontab
crontab -e

# Add line to run update at midnight every day
0 0 * * * ~/bookstore-api/update.sh >> ~/update.log 2>&1
```

## Step 12: Set Up Domain Name (Optional)

1. Register a domain in Route 53 or your preferred domain registrar
2. Point your domain to your EC2 instance's public IP
3. Update your .env file with the domain name:
   ```
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

## Step 13: Get Valid SSL Certificates (Optional)

Install Certbot to get free Let's Encrypt certificates:

```bash
# Install Certbot
sudo dnf install -y augeas-libs
sudo python3 -m pip install certbot

# Get certificate (stop nginx first)
docker-compose -f docker-compose.prod.yml stop nginx
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Fix permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem

# Restart containers
docker-compose -f docker-compose.prod.yml up -d
```

## Step 14: Database Backups

Create a script for regular database backups:

```bash
# Create backup script
cat > backup.sh << 'EOL'
#!/bin/bash

# Set variables
BACKUP_DIR=~/backups
CONTAINER_NAME=$(docker ps -qf "name=db")
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Run backup
docker exec $CONTAINER_NAME pg_dump -U postgres postgres > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.sql.gz"
EOL

# Make script executable
chmod +x backup.sh

# Add to crontab to run daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * ~/bookstore-api/backup.sh >> ~/backup.log 2>&1") | crontab -
```

## Troubleshooting Common Issues

### Container Fails to Start

Check logs for errors:
```bash
docker-compose -f docker-compose.prod.yml logs web
```

### Database Connection Issues

Ensure the database container is running:
```bash
docker ps | grep db
```

### Permission Issues

Fix permissions if you see access denied errors:
```bash
sudo chown -R ec2-user:ec2-user ~/bookstore-api
```

### Out of Disk Space

Clean up unused Docker resources:
```bash
docker system prune -a
```

### Monitoring the Application

Check memory and CPU usage:
```bash
docker stats
```

### Restarting After a Server Reboot

Set up automatic restart after server reboot:
```bash
cat > /etc/systemd/system/bookstore-api.service << EOL
[Unit]
Description=Bookstore API Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/bookstore-api
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
User=ec2-user

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl enable bookstore-api.service
```
