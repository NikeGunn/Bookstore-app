pipeline {
    agent any

    stages {
        stage("Code") {
            steps {
                echo "Cloning the code"
                // Use checkout scm to get code from the repository where Jenkinsfile is located
                checkout scm
            }
        }
        
        stage("Build") {
            steps {
                echo "Building the Docker image"
                sh "docker build -t bookstore-api ."
            }
        }
        
        stage("Test") {
            steps {
                echo "Running tests"
                sh "docker run --rm bookstore-api python manage.py test"
            }
        }
        
        stage("Push to Docker Hub") {
            steps {
                echo "Pushing to Docker Hub"
                withCredentials([usernamePassword(
                    credentialsId: "dockerHub", 
                    passwordVariable: "dockerHubPass", 
                    usernameVariable: "dockerHubUser"
                )]) {
                    sh "docker tag bookstore-api ${env.dockerHubUser}/bookstore-api:latest"
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker push ${env.dockerHubUser}/bookstore-api:latest"
                }
            }
        }
        
        stage("Deploy") {
            steps {
                echo "Deploying the container"
                
                // Create necessary directories
                sh "mkdir -p nginx/ssl nginx/conf.d"
                
                // Generate SSL certificates if they don't exist
                sh '''
                    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
                        openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj "/CN=localhost" -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
                    fi
                '''
                
                // Create or update .env file with production settings
                sh '''
                    cat > .env << EOL
DEBUG=0
SECRET_KEY=production_secret_key_change_this
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOL
                '''
                
                // Update docker-compose.prod.yml to use the Docker Hub image
                withCredentials([usernamePassword(
                    credentialsId: "dockerHub", 
                    passwordVariable: "dockerHubPass", 
                    usernameVariable: "dockerHubUser"
                )]) {
                    sh '''
                        cat > docker-compose.prod.yml << EOL
version: '3.8'

services:
  web:
    image: ${dockerHubUser}/bookstore-api:latest
    restart: always
    volumes:
      - static_volume:/app/static
    expose:
      - 8000
    env_file:
      - .env
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  db:
    image: postgres:15
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  nginx:
    image: nginx:1.25
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/app/static
    depends_on:
      - web
    command: >
      bash -c "apt-get update &&
               apt-get install -y curl &&
               rm -rf /var/lib/apt/lists/* &&
               nginx -g 'daemon off;'"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  static_volume:
EOL
                    '''
                }
                
                // Create nginx configuration file
                sh '''
                    cat > nginx/conf.d/default.conf << EOL
server {
    listen 80;
    server_name _;
    
    # Redirect all HTTP requests to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;

    # Serve static files
    location /static/ {
        alias /app/static/;
        expires 30d;
    }

    # Proxy connections to the Django app
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOL
                '''
                
                // Stop any running containers and start new ones
                sh "docker-compose -f docker-compose.prod.yml down"
                sh "docker-compose -f docker-compose.prod.yml up -d"
                
                // Wait for services to be ready
                sh "sleep 10"
                
                // Verify the deployment
                sh "curl -k https://localhost/api/v1/health/"
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful! Your Bookstore API is now running."
        }
        failure {
            echo "Deployment failed! Check the logs for details."
        }
        always {
            // Clean up local Docker images to save space
            sh "docker system prune -f"
        }
    }
}
