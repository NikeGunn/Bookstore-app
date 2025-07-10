# Troubleshooting Guide

This guide addresses common issues that might occur when running the Bookstore API in Docker containers.

## CORS_ALLOW_ALL_ORIGINS Error

**Error:**
```
ERRORS:
?: (corsheaders.E005) CORS_ALLOW_ALL_ORIGINS should be a bool.
```

**Solution:**
This error occurs when the `DEBUG` environment variable is passed as a string instead of a boolean. Ensure that in your settings.py:

```python
# Convert DEBUG string to bool properly
DEBUG = bool(int(os.environ.get("DEBUG", "1")))
CORS_ALLOW_ALL_ORIGINS = bool(int(os.environ.get("DEBUG", "0")))
```

## Database Connection Issues

**Error:**
```
Database is unavailable - sleeping
```

**Solution:**
1. Ensure the database container is running: `docker ps`
2. Check database logs: `docker-compose logs db`
3. Verify the DATABASE_URL in your .env file is correct
4. Make sure the port is not in use by another service

## Missing entrypoint.sh or Permission Denied

**Error:**
```
/bin/bash: /app/entrypoint.sh: No such file or directory
```
or
```
/bin/bash: /app/entrypoint.sh: Permission denied
```

**Solution:**
1. Make sure entrypoint.sh exists in your project root
2. Ensure it has executable permissions:
   ```bash
   chmod +x entrypoint.sh
   ```
3. Make sure the line endings are Unix-style (LF, not CRLF)
   ```bash
   dos2unix entrypoint.sh
   ```

## SSL Certificate Issues

**Error:**
```
nginx: [emerg] cannot load certificate "/etc/nginx/ssl/cert.pem"
```

**Solution:**
1. Make sure you've generated or copied SSL certificates to the nginx/ssl directory
2. Create certificates if needed:
   ```bash
   mkdir -p nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
   ```

## Static Files Not Serving

**Solution:**
1. Make sure the STATIC_ROOT is set correctly in settings.py
2. Verify the volumes in docker-compose.yml and docker-compose.prod.yml
3. Run collectstatic manually:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

## "No module named dj_database_url" Error

**Solution:**
1. Add the package to requirements.txt: `dj-database-url>=2.1.0`
2. Rebuild the container:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up
   ```

## Health Check Failing

**Error:**
```
health-check-name unhealthy: CMD-SHELL curl -f http://localhost:8000/api/v1/health/ exited with 7
```

**Solution:**
1. Make sure curl is installed in the container
2. Verify the health check endpoint is correctly implemented and accessible
3. Check the URL and port in the health check command

## General Debugging Tips

1. **Check container logs:**
   ```bash
   docker-compose logs web
   docker-compose logs db
   docker-compose logs nginx
   ```

2. **Access a running container:**
   ```bash
   docker-compose exec web bash
   ```

3. **Restart containers:**
   ```bash
   docker-compose restart
   ```

4. **Clean up and rebuild:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

5. **Check running containers and ports:**
   ```bash
   docker ps
   netstat -tuln
   ```
