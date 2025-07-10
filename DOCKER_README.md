# Bookstore API - Django REST Framework Application

A comprehensive RESTful API for a bookstore management system built with Django REST Framework.

## Project Features

- Full CRUD operations for book management
- Advanced filtering and searching
- Pagination support
- Input validation with proper error responses
- API documentation with Swagger/OpenAPI
- Dockerized deployment for local development and production

## Docker Setup

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd pyhon-store-v2
```

2. Start the development server:
```bash
docker-compose up --build
```

3. Access the API at `http://localhost:8000/api/v1/` and the Swagger documentation at `http://localhost:8000/api/v1/docs/`

### Production Deployment

1. Create a `.env` file based on the `.env.example` template:
```bash
cp .env.example .env
```

2. Edit `.env` file with your production settings.

3. Generate SSL certificates:
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
```

4. Deploy with Docker Compose:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## AWS Deployment

### Prerequisites
- AWS Account
- AWS CLI installed and configured
- Docker and Docker Compose installed

### Deploying to Amazon EC2

1. Launch an EC2 instance with Amazon Linux 2 or Ubuntu.

2. Install Docker and Docker Compose:
```bash
# For Amazon Linux 2
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in
```

3. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd pyhon-store-v2
```

4. Create and configure the .env file:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Generate SSL certificates:
```bash
mkdir -p nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
```

6. Start the application:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Using Amazon RDS (Optional)

For production use, you can use Amazon RDS for PostgreSQL instead of the containerized database:

1. Create an RDS PostgreSQL instance.

2. Update the `.env` file with your RDS endpoint:
```
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
```

3. Modify the `docker-compose.prod.yml` to remove the db service.

### Using AWS ECS (Elastic Container Service)

You can also deploy this application to AWS ECS:

1. Install the AWS CLI and configure your credentials.

2. Build and push your Docker image to Amazon ECR:
```bash
aws ecr create-repository --repository-name bookstore-api
aws ecr get-login-password | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<region>.amazonaws.com
docker build -t <your-account-id>.dkr.ecr.<region>.amazonaws.com/bookstore-api:latest .
docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/bookstore-api:latest
```

3. Create an ECS cluster, task definition, and service using the AWS Console or CLI.

## API Endpoints

- `GET /api/v1/books/` - List all books
- `POST /api/v1/books/` - Create a new book
- `GET /api/v1/books/{id}/` - Retrieve a book by UUID
- `PUT /api/v1/books/{id}/` - Update a book
- `PATCH /api/v1/books/{id}/` - Partially update a book
- `DELETE /api/v1/books/{id}/` - Delete a book

For full API documentation, visit `/api/v1/docs/` when the server is running.
