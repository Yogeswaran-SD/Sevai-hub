# 🔐 Sevai Hub — Security Hardening Guide

**Version:** 4.0.0  
**Last Updated:** March 27, 2026  
**Security Level:** Production-Ready

---

## 📋 Security Checklist

### CRITICAL Issues (Fixed ✅)
- [x] Removed hardcoded secrets from code
- [x] Implemented CORS restrictions (no `allow_origins=["*"]`)
- [x] Hash admin password with bcrypt
- [x] Exclude `.env` files from git tracking
- [x] Replace hardcoded API URLs with environment variables

### HIGH Priority (Implemented ✅)
- [x] Require environment variables for all secrets
- [x] Add input validation for authentication
- [x] Database migrations with Alembic
- [x] Docker containerization for isolation
- [x] Nginx reverse proxy configuration

### MEDIUM Priority (Recommended)
- [ ] Enable HTTPS/TLS with Let's Encrypt
- [ ] Set up rate limiting on auth endpoints
- [ ] Implement logging with structured format
- [ ] Add security headers (CSP, HSTS, X-Frame-Options)
- [ ] Configure database encryption at rest

---

## 🔒 Secrets Management

### Environment Variables (NOT in Code)

**Required Secrets:**
- `SECRET_KEY` - JWT signing key (minimum 32 characters)
- `DATABASE_URL` - Database connection string
- `ADMIN_PASSWORD_HASH` - Bcrypt-hashed admin password
- `ADMIN_SECRET_KEY` - Admin operations secret

**Location: `.env` file**
```bash
# Example (CHANGE THESE VALUES!)
SECRET_KEY=generated_32_character_minimum_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/sevaihub
ADMIN_PASSWORD_HASH=$2b$12$your_bcrypt_hash_here
ADMIN_SECRET_KEY=your_admin_secret_here
```

### Generating Secure Secrets

```bash
# Generate SECRET_KEY (Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ADMIN_PASSWORD_HASH (from plaintext)
python -c "from passlib.context import CryptContext; \
pwd_context = CryptContext(schemes=['bcrypt']); \
print(pwd_context.hash('YourPassword123!'))"

# Generate strong random password (Bash)
openssl rand -base64 32
```

### Git Security

```bash
# Verify .env is in .gitignore
cat .gitignore | grep ".env"

# Remove accidentally committed .env files
git rm --cached .env
git commit -m "Remove sensitive .env file"

# Prevent future commits of .env
git update-index --skip-worktree .env
```

---

## 🔐 Authentication Security

### Password Requirements

**Admin Account:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- NOT stored in plaintext (use bcrypt hash)
- Change password before first production deployment

**User/Technician Passwords:**
- Minimum 8 characters (enforced in backend)
- Recommended: Mix of uppercase, lowercase, numbers

### JWT Token Security

**Token Configuration:**
```python
# backend/app/core/config.py
SECRET_KEY: str          # Secret key for signing
ALGORITHM: str = "HS256" # Token signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
```

**Best Practices:**
- Tokens expire after 24 hours
- Store tokens in secure HTTP-only cookies (if possible)
- Never expose tokens in logs
- Implement token refresh endpoints

### API Authentication

**All protected endpoints require bearer token:**
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  https://api.sevaihub.com/dashboard/user
```

---

## 🌐 CORS & API Security

### CORS Configuration

**Production (Restricted):**
```env
# .env
CORS_ORIGINS=https://app.sevaihub.com,https://www.sevaihub.com
```

**What This Does:**
- Only allows requests from specified domains
- Blocks CSRF attacks
- Rejects wildcard origins

**Development (Flexible):**
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### API Endpoint Security

**Protected Endpoints Require Authentication:**
- `GET /dashboard/user` - User role
- `GET /dashboard/technician` - Technician role
- `GET /admin/dashboard` - Admin role
- `POST /admin/users/{id}/toggle` - Admin only

**Rate Limiting (Recommended):**
```python
# backend/app/routers/auth.py
@router.post("/login/user")
@limiter.limit("5/minute")  # 5 attempts per minute
def login_user(...):
    pass
```

---

## 🛡️ HTTPS/TLS Configuration

### Enable HTTPS (Production Required)

**Using Let's Encrypt with Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx \
  -d api.sevaihub.com \
  -d www.sevaihub.com

# Auto-renewal (runs daily)
sudo systemctl enable certbot.timer
```

### Security Headers

**Nginx Configuration:**
```nginx
# /etc/nginx/conf.d/sevaihub.conf
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

---

## 🗄️ Database Security

### PostgreSQL Hardening

**Connection Security:**
```sql
-- Use SSL for remote connections
ALTER SYSTEM SET ssl = on;

-- Restrict user privileges
GRANT CONNECT ON DATABASE sevaihub TO sevaihub_user;
GRANT USAGE ON SCHEMA public TO sevaihub_user;
REVOKE ALL ON DATABASE postgres FROM PUBLIC;
```

**Encryption:**
- Enable transparent data encryption (TDE) at OS level
- Use encrypted network connections (SSL/TLS)
- Encrypt backups before storing

### Database Backups

```bash
# Encrypted backup
pg_dump sevaihub | gpg --encrypt --recipient you@example.com > backup.sql.gpg

# Verify backup integrity
gpg --decrypt backup.sql.gpg | pg_dump -U postgres --compare-only sevaihub

# Schedule daily backups (crontab)
0 2 * * * pg_dump sevaihub | gzip > /backups/sevaihub-$(date +\%Y\%m\%d).sql.gz
```

---

## 🔍 Input Validation & Sanitization

### Implemented Validations

**Phone Numbers:**
```python
# Must be 10 digits for Indian numbers
import re
def validate_phone(phone: str) -> bool:
    return bool(re.match(r'^\d{10}$', phone))
```

**Email Addresses:**
```python
from pydantic import EmailStr
# Pydantic validates email format
```

**Service Categories:**
```python
from enum import Enum
class ServiceCategory(str, Enum):
    PLUMBER = "Plumber"
    # Limited to predefined categories
```

### SQL Injection Prevention

**Using SQLAlchemy ORM:**
```python
# ✅ Safe - uses parameterized queries
user = db.query(User).filter(User.email == email).first()

# ❌ DANGEROUS - SQL injection risk
user = db.query(User).filter_by(f"email = '{email}'").first()
```

---

## 📝 Logging & Monitoring

### Structured Logging

**Backend:**
```python
import logging
logger = logging.getLogger(__name__)

# Log security events
logger.warning(f"Failed login attempt: {identifier}")
logger.error(f"Unauthorized access to admin panel: {user_id}")
```

**Centralize logs to:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- CloudWatch (AWS)
- Stackdriver (Google Cloud)

### Error Tracking

**Set up Sentry:**
```bash
pip install sentry-sdk

# backend/app/main.py
import sentry_sdk
sentry_sdk.init("https://your-sentry-dsn@sentry.io/project-id")
```

---

## 🔐 Container Security

### Docker Security Best Practices

**Non-root User:**
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

**Minimal Base Image:**
```dockerfile
FROM python:3.11-slim  # Smaller, fewer vulnerabilities
```

**Vulnerability Scanning:**
```bash
# Scan image for known vulnerabilities
docker scan sevaihub-backend:latest

# Use Trivy for detailed scanning
trivy image sevaihub-backend:latest
```

---

## 🎯 Firewall & Network Security

### Firewall Rules (Production)

**Allow:**
- `80/tcp` (HTTP, redirect to HTTPS)
- `443/tcp` (HTTPS - web traffic)
- `22/tcp` (SSH - for admins only, restricted IPs)

**Deny:**
- All other ports
- Database ports (5432) from public internet
- Admin panel ports from public internet

### Network Segmentation

```dockerfile
# Use Docker networks to isolate services
services:
  postgres:
    networks:
      - sevaihub_network  # Only backend can access
  
  backend:
    networks:
      - sevaihub_network
  
  frontend:
    networks:
      - sevaihub_network
```

---

## 🚨 Incident Response

### Security Incident Checklist

1. **Detect** - Monitor logs for suspicious activity
2. **Contain** - Isolate affected services
3. **Investigate** - Analyze logs and backups
4. **Eradicate** - Remove threat, rotate secrets
5. **Recover** - Restore systems from backups
6. **Learn** - Post-incident review

### Compromised Secrets Recovery

```bash
# If SECRET_KEY is compromised:
1. Generate new SECRET_KEY
2. Update all active tokens (force re-login)
3. Deploy new version with new key
4. Audit login history for unauthorized access

# If ADMIN_PASSWORD is compromised:
1. Generate new password hash
2. Update .env file
3. Restart backend service
4. Review admin activity logs
```

---

## ✅ Security Audit Checklist

Before Production Deployment:

- [ ] All secrets are in `.env` (not in code)
- [ ] CORS is restrictive (not `["*"]`)
- [ ] HTTPS/TLS is enabled
- [ ] Security headers are set
- [ ] Database encryption is enabled
- [ ] Backups are encrypted
- [ ] Logging is enabled and centralized
- [ ] Rate limiting is configured
- [ ] Input validation is strict
- [ ] SQL injection prevention verified
- [ ] Admin credentials are strong (bcrypt hashed)
- [ ] JWT tokens expire after reasonable time
- [ ] Firewall rules are restrictive
- [ ] Container images are scanned for vulnerabilities
- [ ] Database user has minimal privileges
- [ ] Debug mode is disabled
- [ ] All dependencies are current (no known CVEs)
- [ ] API keys are rotated regularly
- [ ] Incident response plan is documented
- [ ] Security training is current for team

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-syntax.html)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Last Security Review:** March 27, 2026  
**Next Review Due:** June 27, 2026  
**Contact Security Team:** security@sevaihub.com
