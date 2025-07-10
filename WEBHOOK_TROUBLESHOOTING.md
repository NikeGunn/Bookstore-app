# Debugging GitHub Webhooks with Jenkins

This guide will help you troubleshoot and fix issues with GitHub webhooks not automatically triggering Jenkins builds.

## Common Issues and Solutions

### 1. Jenkins Configuration Issues

**Check Build Triggers:**
1. Go to your Jenkins pipeline configuration
2. Under "Build Triggers", ensure that "GitHub hook trigger for GITScm polling" is checked
3. Save the configuration

**Check Jenkins URL Configuration:**
1. Go to Jenkins > Manage Jenkins > Configure System
2. Find "Jenkins URL" and ensure it's set correctly (e.g., `http://your-aws-ip:8080/` or your proper domain)
3. Save the configuration

### 2. GitHub Webhook Configuration Issues

**Check Webhook URL:**
1. Go to your GitHub repository
2. Go to Settings > Webhooks
3. Check the Webhook URL - it should be:
   - `http://your-jenkins-server:8080/github-webhook/` (note the trailing slash)
4. Make sure the URL is publicly accessible from GitHub's servers
5. Verify the Content-Type is set to `application/json`

**Check Recent Deliveries:**
1. In GitHub repository > Settings > Webhooks
2. Expand your webhook
3. Click on "Recent Deliveries"
4. Check if there are any failed deliveries and their error messages
5. For each delivery, check both the request and response tabs

### 3. Network and Security Issues

**Firewall Settings:**
1. Make sure port 8080 (or your Jenkins port) is open on your AWS instance
2. Verify security group settings allow incoming traffic to this port from GitHub's IP ranges

**Jenkins Security:**
1. Go to Jenkins > Manage Jenkins > Configure Global Security
2. Ensure "Enable security" is checked
3. Under "CSRF Protection", make sure "Enable proxy compatibility" is checked if you're behind a proxy

### 4. Plugin Issues

**Verify GitHub Plugin:**
1. Go to Jenkins > Manage Jenkins > Manage Plugins > Installed
2. Make sure "GitHub Integration Plugin" is installed and enabled
3. If not, install it from the "Available" tab

**Update Plugins:**
1. Go to Jenkins > Manage Jenkins > Manage Plugins > Updates
2. Update all GitHub-related plugins

### 5. Manual Webhook Test

**Test Webhook Manually:**
1. In GitHub, go to your webhook settings
2. Scroll down to "Recent Deliveries"
3. Click on "Redeliver" button to manually trigger a webhook
4. Check if Jenkins receives and processes the webhook

### 6. Jenkins Log Inspection

**Check Jenkins Logs:**
1. Go to Jenkins > Manage Jenkins > System Log
2. Look for any errors related to webhook reception
3. Check for messages containing "GitHub" or "webhook"

## Complete Webhook Setup Process

If your webhook is still not working, here's a complete setup process:

### On Jenkins:

1. Install GitHub Integration Plugin:
   - Jenkins > Manage Jenkins > Manage Plugins > Available
   - Search for "GitHub Integration" and install

2. Configure GitHub Server:
   - Jenkins > Manage Jenkins > Configure System
   - Scroll to GitHub section
   - Add GitHub Server
   - Add GitHub credentials if needed
   - Test the connection

3. Configure Your Pipeline:
   - Go to your pipeline configuration
   - Under "Build Triggers", check "GitHub hook trigger for GITScm polling"
   - Save

### On GitHub:

1. Create a new webhook:
   - Repository > Settings > Webhooks > Add webhook
   - Payload URL: `http://your-jenkins-ip:8080/github-webhook/`
   - Content Type: `application/json`
   - Secret: (optional, but recommended for security)
   - Which events to trigger: "Just the push event" or customize
   - Check "Active"
   - Click "Add webhook"

### Troubleshooting Commands

SSH into your AWS instance and run these commands to diagnose network issues:

```bash
# Check if Jenkins is running
sudo systemctl status jenkins

# Check if port 8080 is open and listening
sudo netstat -tulpn | grep 8080

# Check firewall settings
sudo iptables -L

# Test webhook reception with curl (replace with your Jenkins URL)
curl -X POST http://localhost:8080/github-webhook/ -H "Content-Type: application/json" -d '{"test":"payload"}'

# Check Jenkins logs
sudo tail -f /var/log/jenkins/jenkins.log
```

## Advanced Solutions

### 1. Use a Ngrok Tunnel for Testing

If your Jenkins server is behind a firewall or NAT, you can use Ngrok to create a public URL:

```bash
# Install Ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz

# Create tunnel to Jenkins
./ngrok http 8080
```

Then use the provided Ngrok URL (e.g., `https://abcd1234.ngrok.io/github-webhook/`) in your GitHub webhook settings.

### 2. Create a Jenkins API Token for Authentication

1. Go to Jenkins > People > (your username) > Configure
2. Under API Token, click "Add new Token"
3. Generate a token and copy it
4. Use basic auth with this token in your webhook URL: `http://username:apitoken@your-jenkins-ip:8080/github-webhook/`

### 3. Check for IP Filtering

If you've restricted Jenkins access to specific IPs:

1. Go to Jenkins > Manage Jenkins > Configure Global Security
2. Check "Enable security" settings
3. Make sure GitHub's IP ranges are allowed (or temporarily disable IP filtering for testing)

## Next Steps After Fixing

Once your webhook is working:

1. Make a small change to your repository and commit/push it
2. Check if Jenkins automatically triggers a build
3. Verify the build log shows it was triggered by a webhook
4. Implement a more secure webhook setup with a shared secret
