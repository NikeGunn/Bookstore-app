#!/bin/bash
# Bookstore API Docker Deployment Script

# Color codes for prettier output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Bookstore API Deployment Script ===${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your settings.${NC}"
    echo -e "${YELLOW}Please edit your .env file now before continuing.${NC}"
    read -p "Press enter to continue..."
fi

# Ask for deployment environment
echo -e "${GREEN}Select deployment environment:${NC}"
echo "1) Development (with hot-reloading)"
echo "2) Production"
read -p "Enter choice [1-2]: " env_choice

case $env_choice in
    1)
        echo -e "${GREEN}Starting development environment...${NC}"
        docker-compose down
        docker-compose up --build
        ;;
    2)
        echo -e "${GREEN}Starting production environment...${NC}"

        # Check if SSL certificates exist
        if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
            echo -e "${YELLOW}SSL certificates not found. Do you want to generate self-signed certificates?${NC}"
            read -p "Generate certificates? [y/n]: " gen_cert

            if [[ $gen_cert == "y" || $gen_cert == "Y" ]]; then
                mkdir -p nginx/ssl
                openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
                echo -e "${GREEN}Generated self-signed certificates.${NC}"
            else
                echo -e "${RED}SSL certificates required for production deployment.${NC}"
                echo -e "${YELLOW}Please place your certificates in the nginx/ssl directory:${NC}"
                echo "  - nginx/ssl/cert.pem (certificate file)"
                echo "  - nginx/ssl/key.pem (private key file)"
                exit 1
            fi
        fi

        # Start production containers
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml up --build -d

        echo -e "${GREEN}Production environment started in detached mode.${NC}"
        echo -e "${GREEN}To see logs, run: docker-compose -f docker-compose.prod.yml logs -f${NC}"

        # Show access information
        echo -e "\n${GREEN}Your application is now running!${NC}"
        echo -e "Access your application at:"
        echo -e "  - ${YELLOW}Local: https://localhost${NC}"
        echo -e "  - ${YELLOW}API endpoints: https://localhost/api/v1/books/${NC}"
        echo -e "  - ${YELLOW}API documentation: https://localhost/api/v1/docs/${NC}"
        echo -e "  - ${YELLOW}Health check: https://localhost/api/v1/health/${NC}"

        # Get server IP if available
        SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [ ! -z "$SERVER_IP" ]; then
            echo -e "  - ${YELLOW}Server IP: https://$SERVER_IP${NC}"
        fi
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac
