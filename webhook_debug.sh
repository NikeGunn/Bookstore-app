#!/bin/bash
# Script to diagnose GitHub webhook issues with Jenkins
# Run this script on your Jenkins server

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}  GitHub Webhook Troubleshooting Script      ${NC}"
echo -e "${BLUE}==============================================${NC}"

# Check if Jenkins is running
echo -e "\n${YELLOW}Checking if Jenkins is running...${NC}"
if systemctl is-active --quiet jenkins; then
    echo -e "${GREEN}✓ Jenkins is running${NC}"
else
    echo -e "${RED}✗ Jenkins is not running. Try: sudo systemctl start jenkins${NC}"
fi

# Check if Jenkins port is open
echo -e "\n${YELLOW}Checking if Jenkins port (8080) is open...${NC}"
if netstat -tuln | grep -q ':8080 '; then
    echo -e "${GREEN}✓ Port 8080 is open and listening${NC}"
else
    echo -e "${RED}✗ Port 8080 is not open. Check Jenkins configuration.${NC}"
fi

# Get public IP address
echo -e "\n${YELLOW}Getting public IP address...${NC}"
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || wget -qO- http://checkip.amazonaws.com)
if [ -n "$PUBLIC_IP" ]; then
    echo -e "${GREEN}✓ Public IP: $PUBLIC_IP${NC}"
else
    echo -e "${RED}✗ Could not determine public IP${NC}"
fi

# Check if the webhook URL is accessible from the server
echo -e "\n${YELLOW}Testing webhook URL from this server...${NC}"
JENKINS_URL="http://localhost:8080/github-webhook/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $JENKINS_URL)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "403" ]; then
    echo -e "${GREEN}✓ Webhook URL is accessible (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Webhook URL returned HTTP $HTTP_CODE${NC}"
    echo -e "  Try accessing ${JENKINS_URL} in a browser"
fi

# Check firewall
echo -e "\n${YELLOW}Checking firewall settings...${NC}"
if command -v iptables >/dev/null; then
    if iptables -L | grep -q "8080"; then
        echo -e "${YELLOW}! Found iptables rules for port 8080${NC}"
    else
        echo -e "${GREEN}✓ No blocking iptables rules found for port 8080${NC}"
    fi
else
    echo -e "${YELLOW}! iptables command not found${NC}"
fi

# Check AWS security group if we're on AWS
echo -e "\n${YELLOW}Checking if we're on AWS and security groups...${NC}"
if curl -s http://169.254.169.254/latest/meta-data/ >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Running on AWS EC2${NC}"
    echo -e "${YELLOW}! Reminder: Make sure your AWS security group allows inbound traffic on port 8080${NC}"
else
    echo -e "${YELLOW}! Not running on AWS or metadata service unavailable${NC}"
fi

# Check Jenkins logs for webhook-related entries
echo -e "\n${YELLOW}Checking Jenkins logs for webhook-related entries...${NC}"
if [ -f /var/log/jenkins/jenkins.log ]; then
    WEBHOOK_LOGS=$(grep -i "webhook\|github" /var/log/jenkins/jenkins.log | tail -10)
    if [ -n "$WEBHOOK_LOGS" ]; then
        echo -e "${GREEN}✓ Found webhook-related log entries:${NC}"
        echo "$WEBHOOK_LOGS"
    else
        echo -e "${YELLOW}! No recent webhook-related log entries found${NC}"
    fi
else
    echo -e "${RED}✗ Jenkins log file not found at /var/log/jenkins/jenkins.log${NC}"
    echo -e "  Check your Jenkins installation or look for logs in another location"
fi

# Print webhook URL information
echo -e "\n${YELLOW}GitHub webhook setup information:${NC}"
echo -e "  Webhook URL should be: ${GREEN}http://$PUBLIC_IP:8080/github-webhook/${NC}"
echo -e "  Content-Type should be: ${GREEN}application/json${NC}"
echo -e "  Events to trigger: ${GREEN}Just the push event${NC} (or customize based on your needs)"

# Final instructions
echo -e "\n${BLUE}==============================================${NC}"
echo -e "${BLUE}  Recommendations:                           ${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "1. In GitHub, go to your repository > Settings > Webhooks"
echo -e "2. Check if your webhook is configured with the correct URL"
echo -e "3. Look at 'Recent Deliveries' for any error messages"
echo -e "4. In Jenkins, verify the 'GitHub hook trigger for GITScm polling' is enabled"
echo -e "5. Check if Jenkins URL is configured properly in Jenkins > Configure System"
echo -e "6. Verify the GitHub Integration Plugin is installed and up to date"
echo -e "\nFor more detailed instructions, see the WEBHOOK_TROUBLESHOOTING.md file"
