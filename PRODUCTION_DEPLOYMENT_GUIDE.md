# 🚀 PRODUCTION DEPLOYMENT GUIDE for Sevai Hub

**Last Updated:** March 28, 2026  
**Version:** 4.0.0 - Production Ready  
**Status:** ✅ READY FOR LIVE DEPLOYMENT

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Security Issues Fixed ✅
- ✅ Frontend API URLs use environment variables (`VITE_API_URL`)
- ✅ Backend secrets in `.env` (git-ignored securely)
- ✅ CORS configured via environment variables (not hardcoded)
- ✅ Admin password uses bcrypt hashing (never plaintext)
- ✅ Database credentials via environment variables
- ✅ JWT tokens with 32+ character SECRET_KEY
- ✅ Nginx security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- ✅ Non-root user in Docker containers
- ✅ Health checks configured
- ✅ Database migrations with Alembic
- ✅ PostGIS extensions properly initialized

### Infrastructure Requirements
- ✅ Docker 20.10+ and Docker Compose 2.0+
- ✅ PostgreSQL 14+ with PostGIS extension
- ✅ Redis 7+ for caching
- ✅ MinIO or S3-compatible object storage
- ✅ SSL/TLS certificate (Let's Encrypt recommended)
- ✅ Domain name configured with DNS

---

## 🔧 STEP 1: ENVIRONMENT SETUP

### 1.1 Create Production Environment File

```bash
cd /path/to/sevaihub
cp .env.docker.example .env.production
```

### 1.2 Configure Environment Variables

Edit `.env.production` with your production values:

```bash
# ============================================================================
# Database Configuration
# ============================================================================
# Use a STRONG password (minimum 20 characters with mixed case, numbers, symbols)
DB_PASSWORD=YourSuper$ecureDBPassword123!
POSTGRES_INITDB_ARGS=-c max_connections=500

# ============================================================================
# Backend (FastAPI) Security
# ============================================================================
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=YourSecure32CharacterOrLongerSecretKey123456789!

# Set to production - enables validation
ENVIRONMENT=production

# MUST be False for production
DEBUG=False

# ============================================================================
# Admin Credentials (CHANGE IMMEDIATELY)
# ============================================================================
ADMIN_MOBILE=9999999999
ADMIN_AADHAAR=123456789012

# Generate new admin secret with: python -c "import secrets; print(secrets.token_urlsafe(32))"
ADMIN_SECRET_KEY=YourAdminSecretKey32CharsMinimum1234567890!

# Generate bcrypt hash with:
# python -c "from passlib.context import CryptContext; 
# pwd_context = CryptContext(schemes=['bcrypt']); 
# print(pwd_context.hash('YourNewAdminPassword!'))"
ADMIN_PASSWORD_HASH=$2b$12$YourBcryptHashedPasswordHere...

# ============================================================================
# CORS Configuration (Set to your domain)
# ============================================================================
# Example: https://app.yourdomain.com,https://web.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ============================================================================
# Frontend Configuration
# ============================================================================
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production

# ============================================================================
# Redis Configuration
# ============================================================================
REDIS_URL=redis://redis:6379

# ============================================================================
# MinIO Configuration
# ============================================================================
# Use strong credentials
MINIO_ROOT_USER=YourMinIOUser123
MINIO_ROOT_PASSWORD=YourMinIOPassword123456789!
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=YourMinIOUser123
MINIO_SECRET_KEY=YourMinIOPassword123456789!

# ============================================================================
# SMTP Configuration (for notifications)
# ============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
EMAILS_FROM_EMAIL=noreply@yourdomain.com
EMAILS_FROM_NAME=Sevai Hub

# ============================================================================
# SMS Configuration (Optional - Twilio)
# ============================================================================
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### 1.3 Security Validation

```bash
# Ensure SECRET_KEY is at least 32 characters
# Ensure ADMIN_PASSWORD_HASH starts with $2b$ (bcrypt)
# Ensure ENVIRONMENT=production
# Ensure DEBUG=False
# Ensure CORS_ORIGINS does not include localhost
```

---

## 🐳 STEP 2: DOCKER DEPLOYMENT

### 2.1 Build Docker Images

```bash
# Production build with optimizations
docker-compose -f docker-compose.yml build --no-cache

# Verify images were created
docker images | grep sevaihub
```

### 2.2 Start Services

```bash
# Start all services in detached mode
docker-compose -f docker-compose.yml up -d

# Verify all services are healthy
docker-compose ps
docker-compose logs -f

# Expected output:
# sevaihub-postgres    running ✓
# sevaihub-redis       running ✓
# sevaihub-minio       running ✓
# sevaihub-backend     running ✓
# sevaihub-frontend    running ✓
# sevaihub-proxy       running ✓
```

### 2.3 Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed demo data (optional)
docker-compose exec backend python seed.py

# Verify database
docker-compose exec postgres psql -U postgres -d sevaihub -c "SELECT * FROM users;"
```

---

## 🌐 STEP 3: NGINX & SSL SETUP

### 3.1 Configure SSL Certificate

#### Option A: Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificate location: /etc/letsencrypt/live/yourdomain.com/
```

#### Option B: Using Self-Signed Certificate (Testing Only)

```bash
sudo openssl req -x509 -newkey rsa:4096 \
  -keyout /etc/nginx/certs/private.key \
  -out /etc/nginx/certs/certificate.crt \
  -days 365 -nodes
```

### 3.2 Update nginx.conf for HTTPS

```nginx
# Replace HTTP redirect block in /root/sevaihub/nginx.conf

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2 default_server;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Include rest of server block...
}
```

### 3.3 Update docker-compose.yml for SSL

```yaml
services:
  nginx:
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro  # Mount SSL certs
    ports:
      - "80:80"
      - "443:443"
```

### 3.4 Restart Services with SSL

```bash
docker-compose restart nginx
# Access https://yourdomain.com
```

---

## ✅ STEP 4: HEALTH & VERIFICATION

### 4.1 Test Endpoints

```bash
# Test Frontend
curl https://yourdomain.com/

# Test Backend Health
curl https://yourdomain.com/health

# Test API Docs
curl https://yourdomain.com/docs

# Test Login Endpoint
curl -X POST https://yourdomain.com/api/auth/login/user \
  -H "Content-Type: application/json" \
  -d '{"identifier":"1234567890","password":"demo123"}'
```

### 4.2 Verify Database Connection

```bash
docker-compose exec backend python -c "
from app.database import SessionLocal
db = SessionLocal()
result = db.execute('SELECT COUNT(*) FROM users')
print(f'Users in database: {result.scalar()}')
"
```

### 4.3 Check Security Headers

```bash
curl -I https://yourdomain.com

# Expected headers:
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
```

### 4.4 Performance Check

```bash
# Check Docker container performance
docker stats

# Check disk usage
df -h
du -sh /mnt/data  # MinIO data directory

# Check database size
docker-compose exec postgres psql -U postgres -d sevaihub \
  -c "SELECT pg_size_pretty(pg_database_size('sevaihub'));"
```

---

## 📊 STEP 5: MONITORING & LOGGING

### 5.1 Enable Logging

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Nginx logs
docker-compose logs -f nginx

# Database logs
docker-compose logs -f postgres
```

### 5.2 Setup Log Rotation

Create `/etc/logrotate.d/sevaihub`:

```bash
/var/log/sevaihub/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
```

### 5.3 Container Health Monitoring

```bash
# Check health status
docker-compose ps

# Investigate unhealthy container
docker-compose logs backend-name

# Restart specific service
docker-compose restart backend
```

---

## 🔐 STEP 6: SECURITY HARDENING

### 6.1 Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 6.2 Database Backups

```bash
# Daily backup script
cat > /usr/local/bin/backup-sevaihub.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/mnt/backups
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose exec -T postgres pg_dump -U postgres sevaihub \
  | gzip > $BACKUP_DIR/sevaihub_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "sevaihub_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/sevaihub_$DATE.sql.gz"
EOF

chmod +x /usr/local/bin/backup-sevaihub.sh

# Add to cron (daily at 2 AM)
crontab -e
# 0 2 * * * /usr/local/bin/backup-sevaihub.sh
```

### 6.3 Update System

```bash
# Update OS and packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker images periodically
docker-compose pull
docker-compose up -d
```

### 6.4 Monitor for Vulnerabilities

```bash
# Scan Docker images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image sevaihub-backend:latest
```

---

## 🆘 TROUBLESHOOTING

### Issue: "Connection refused" to API

**Solution:**
```bash
# Check if backend is running
docker-compose ps backend

# Check logs
docker-compose logs backend

# Verify CORS configuration
grep CORS_ORIGINS .env.production

# Restart backend
docker-compose restart backend
```

### Issue: Database migration failed

**Solution:**
```bash
# Check migration status
docker-compose exec backend alembic current
docker-compose exec backend alembic history

# Run migration
docker-compose exec backend alembic upgrade head

# Rollback if needed
docker-compose exec backend alembic downgrade -1
```

### Issue: SSL certificate not working

**Solution:**
```bash
# Verify certificate file permissions
ls -la /etc/letsencrypt/live/yourdomain.com/

# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -noout -dates

# Renew certificate
sudo certbot renew

# Restart nginx
docker restart nginx
```

### Issue: High memory usage

**Solution:**
```bash
# Check memory usage
docker stats

# Reduce replica count in docker-compose
# Increase swap space
# Optimize database queries

# Restart services to clear memory
docker-compose restart
```

### Issue: Login failing (401 Unauthorized)

**Solution:**
```bash
# Verify JWT SECRET_KEY is set
grep SECRET_KEY .env.production

# Check authentication logs
docker-compose logs backend | grep -i "auth\|login"

# Verify admin credentials are hashed correctly
docker-compose exec backend python -c "
from app.core.security import verify_password
from app.core.config import settings
result = verify_password('YourPassword', settings.ADMIN_PASSWORD_HASH)
print(f'Password matches: {result}')
"
```

---

## 📈 PERFORMANCE OPTIMIZATION

### Database Optimization

```bash
# Create indexes (run automatically via migrations)
docker-compose exec postgres psql -U postgres -d sevaihub -c "
CREATE INDEX IF NOT EXISTS idx_technicians_location 
ON technicians USING gist(location);

CREATE INDEX IF NOT EXISTS idx_technicians_service 
ON technicians(service_category);

CREATE INDEX IF NOT EXISTS idx_users_phone 
ON users(phone);
"
```

### Caching Strategy

```bash
# Monitor Redis
docker-compose exec redis redis-cli
> INFO stats
> DBSIZE
> FLUSHDB  # Clear cache if needed
```

### Frontend Optimization

```bash
# Built-in optimizations (already configured):
# - Gzip compression (nginx)
# - CSS/JS minification (Vite)
# - Code splitting (Vite)
# - Image optimization
```

---

## 📞 SUPPORT & MAINTENANCE

### Regular Maintenance Tasks

```bash
# Daily
- Monitor logs for errors
- Check system resources
- Verify all services are healthy

# Weekly
- Review access logs
- Update SSL certificates (auto-renewal)
- Check backup completion
- Monitor database growth

# Monthly
- Update Docker images
- Review security logs
- Test disaster recovery
- Update system packages

# Quarterly
- Database optimization
- Performance analysis
- Security audit
- Capacity planning
```

### Useful Commands

```bash
# View all running containers
docker-compose ps

# View logs for all services
docker-compose logs -f

# Stop all services
docker-compose down

# Remove all data (CAREFUL!)
docker-compose down -v

# Backup configuration
tar -czf sevaihub_backup_$(date +%Y%m%d).tar.gz .env.production nginx.conf docker-compose.yml

# Restart specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend bash

# Check resource usage
docker stats

# View container details
docker-compose config
```

---

## ✨ POST-DEPLOYMENT CHECKLIST

- [ ] Environment variables configured securely
- [ ] SSL/TLS certificate installed and working
- [ ] Database initialized and migrated
- [ ] Health checks passing
- [ ] All API endpoints responding
- [ ] Frontend loaded and functional
- [ ] Backups configured and tested
- [ ] Firewall rules configured
- [ ] Monitoring and logging active
- [ ] SSL certificate auto-renewal configured
- [ ] Update strategy planned
- [ ] Incident response plan documented
- [ ] Team trained on operations
- [ ] Documentation updated

---

## 🎉 LIVE DEPLOYMENT SUCCESSFUL

Your Sevai Hub application is now running in production!

**Access Points:**
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api
- API Docs: https://yourdomain.com/docs

**Quick Start Commands:**
```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Start services
docker-compose up -d
```

For any issues or questions, refer to the troubleshooting section above.

---

**Version:** 4.0.0  
**Last Updated:** March 28, 2026  
**Status:** Production Ready ✅
