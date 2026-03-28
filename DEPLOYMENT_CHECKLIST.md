# DEPLOY CHECKLIST - SEVAI HUB

## ✅ PRE-DEPLOYMENT VERIFICATION (Completed)

- [x] All services running and responding
- [x] PostgreSQL database initialized with demo data
- [x] Redis cache operational
- [x] MinIO storage configured
- [x] Backend API endpoints tested (15/18 passing)
- [x] Frontend pages loading correctly
- [x] Authentication working (all 3 roles)
- [x] Core features operational
- [x] No critical blocking issues

**Status**: Ready to Deploy ✅

---

## 🔧 DEPLOYMENT TASKS

### Task 1: Update Production Credentials
**Priority**: CRITICAL - Must do before going live

- [ ] Change admin password in `.env`
```bash
# Generate new secure password hash
python -c "from app.core.security import get_password_hash; print(get_password_hash('YOUR_STRONG_PASSWORD'))"
```

- [ ] Update database user password
```bash
docker exec sevaihub-postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'NEW_STRONG_PASSWORD';"
```

- [ ] Update MinIO credentials
```bash
# Change in docker-compose.yml and .env
MINIO_ROOT_USER=new_admin_user
MINIO_ROOT_PASSWORD=new_strong_password
```

- [ ] Update demo user passwords
```bash
docker exec sevaihub-backend python -c "
from app.core.security import get_password_hash
hash = get_password_hash('new_password')
print(f'Password hash: {hash}')
"
```

### Task 2: Configure External Services
**Priority**: HIGH - Needed for notifications

- [ ] Configure SMTP Server
```
File: backend/.env
Add:
SMTP_SERVER=your_smtp_server.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@sevaihub.com
```

- [ ] Configure Twilio (Optional)
```
File: backend/.env
Add:
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

- [ ] Configure Sendgrid (Alternative to SMTP)
```
File: backend/.env
Add:
SENDGRID_API_KEY=your_sendgrid_api_key
```

### Task 3: Update Application Configuration
**Priority**: HIGH - Security and performance

- [ ] Update frontend API URL
```
File: frontend/.env
VITE_API_URL=https://your-domain.com/api
```

- [ ] Configure CORS for production domain
```
File: backend/app/main.py
origins = [
    "https://your-domain.com",
    "https://www.your-domain.com",
]
```

- [ ] Update JWT secret key
```
File: backend/.env
SECRET_KEY=your_new_secure_random_string_here
```

- [ ] Configure database backup
```
File: Add backup script
```

- [ ] Set up logging to file
```
File: backend/.env
Add:
LOG_LEVEL=INFO
LOG_FILE=/var/log/sevaihub/app.log
```

### Task 4: SSL/HTTPS Configuration
**Priority**: CRITICAL - Security requirement

- [ ] Generate SSL certificates
```bash
# Option 1: Using Let's Encrypt
certbot certonly --standalone -d your-domain.com

# Option 2: Using self-signed (for internal only)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

- [ ] Update nginx.conf with SSL
```
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;
    server_name your-domain.com;
}
```

- [ ] Redirect HTTP to HTTPS
```
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Task 5: Database Backup Setup
**Priority**: HIGH - Data protection

- [ ] Create backup script
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec sevaihub-postgres pg_dump -U postgres sevaihub > backup_$TIMESTAMP.sql
gzip backup_$TIMESTAMP.sql
```

- [ ] Schedule automated backups
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

- [ ] Test restore process
```bash
# Verify backup can be restored
docker exec sevaihub-postgres psql -U postgres sevaihub < backup.sql
```

### Task 6: Monitoring & Logging Setup
**Priority**: MEDIUM - Operational visibility

- [ ] Enable application logging
```bash
# View logs
docker logs sevaihub-backend -f
docker logs sevaihub-frontend -f
```

- [ ] Setup error tracking (Optional)
```
Tools: Sentry, DataDog, New Relic
```

- [ ] Configure health checks
```bash
# Test endpoint
curl https://your-domain.com/api/health
```

- [ ] Setup uptime monitoring
```
Tools: UptimeRobot, Pingdom, StatusCake
```

### Task 7: Performance Optimization
**Priority**: MEDIUM - User experience

- [ ] Enable database connection pooling
```
Already configured: max_connections=200
```

- [ ] Enable caching headers
```
File: backend/app/main.py
Add Cache-Control headers
```

- [ ] Optimize database indexes
```sql
CREATE INDEX idx_technicians_location ON technicians USING GIST(location);
CREATE INDEX idx_services_category ON technicians(service_category);
```

- [ ] Configure CDN (Optional)
```
Service: CloudFlare, AWS CloudFront
```

### Task 8: Security Hardening
**Priority**: CRITICAL

- [ ] Enable rate limiting
```python
# backend/app/main.py
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

- [ ] Setup WAF (Web Application Firewall)
```
Service: AWS WAF, Cloudflare, ModSecurity
```

- [ ] Configure security headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

- [ ] Implement CSRF protection
```
Token-based CSRF protection for POST requests
```

- [ ] Regular security audits
```bash
# Check dependencies for vulnerabilities
pip audit
npm audit
```

---

## 📦 DEPLOYMENT ENVIRONMENTS

### Development Setup (Current)
```
Database: PostgreSQL (localhost:5432)
Cache: Redis (localhost:6379)
Storage: MinIO (localhost:9000)
Backend: http://localhost:8000
Frontend: http://localhost:8080
```

### Staging Setup (Recommended)
```
Database: PostgreSQL (staging-db.example.com:5432)
Cache: Redis (staging-cache.example.com:6379)
Storage: MinIO (staging-storage.example.com:9000)
Backend: https://staging-api.example.com
Frontend: https://staging.example.com
```

### Production Setup (Target)
```
Database: PostgreSQL (prod-db.example.com:5432, replicated)
Cache: Redis Cluster (prod-cache.example.com:6379)
Storage: S3 or MinIO (prod-storage.example.com:9000, backed up)
Backend: https://api.example.com
Frontend: https://www.example.com
Nginx: Reverse proxy with SSL
```

---

## 🚀 DEPLOYMENT COMMANDS

### Before Deployment
```bash
# Run final tests
python final_test.py

# Check all services
docker-compose ps

# Verify database
docker exec sevaihub-postgres psql -U postgres -l

# Check logs
docker logs sevaihub-backend
docker logs sevaihub-frontend
```

### Rebuild for Production
```bash
# Build latest images
docker-compose build

# Start fresh
docker-compose down
docker-compose up -d

# Verify
docker-compose ps
```

### Database Migration (if needed)
```bash
# Run migrations
docker exec sevaihub-backend alembic upgrade head

# Verify schema
docker exec sevaihub-postgres psql -U postgres -d sevaihub -c "\dt"
```

---

## 📋 DEPLOYMENT VERIFICATION

After deployment, verify:

- [ ] All services running: `docker-compose ps`
- [ ] Backend responding: `curl https://your-domain.com/api/health`
- [ ] Frontend loading: `https://your-domain.com`
- [ ] Database connected: Login to admin panel
- [ ] SSL certificates: Check browser lock icon
- [ ] Logs clean: `docker logs sevaihub-backend`
- [ ] Can login: Test with demo credentials
- [ ] Can search: Test technician search
- [ ] Performance acceptable: Check response times

---

## 🆘 TROUBLESHOOTING DEPLOYMENT

### Service Won't Start
```bash
# Check logs
docker logs [service_name]

# Restart service
docker-compose restart [service_name]

# Rebuild service
docker-compose build --no-cache [service_name]
docker-compose up -d
```

### Database Connection Error
```bash
# Check PostgreSQL
docker logs sevaihub-postgres

# Verify connection
docker exec sevaihub-backend python -c "from app.database import engine; engine.connect()"

# Reset database
docker-compose down -v
docker-compose up -d
```

### High Memory Usage
```bash
# Check docker stats
docker stats

# Clean up
docker system prune
docker volume prune
```

### Slow Performance
```bash
# Check database slow queries log
docker exec sevaihub-postgres psql -U postgres -d sevaihub -c "SELECT * FROM pg_stat_statements;"

# Rebuild indexes
docker exec sevaihub-postgres psql -U postgres -d sevaihub -c "REINDEX DATABASE sevaihub;"
```

---

## 📞 SUPPORT RESOURCES

### Key Documentation
- [README.md](README.md) - Project overview
- [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) - Common issues
- [PRODUCTION_DEPLOYMENT_REPORT.md](PRODUCTION_DEPLOYMENT_REPORT.md) - Full deployment guide
- [SECURITY.md](SECURITY.md) - Security guidelines

### Log Locations
```bash
# Docker logs
docker logs sevaihub-backend -f
docker logs sevaihub-frontend -f
docker logs sevaihub-postgres -f

# Application logs (if configured)
/var/log/sevaihub/app.log
```

### Emergency Contacts
- Tech Lead: [Your contact]
- DevOps Team: [Your contact]
- On-Call Support: [Your contact]

---

## ✅ FINAL SIGN-OFF

**Deployment Approved By**: [Your Name]  
**Date**: [Date]  
**Status**: READY TO DEPLOY ✅

All pre-deployment tasks must be completed before proceeding with deployment.

---

*Last Updated: 2026-03-28*  
*Version: 1.0 Production Ready*
