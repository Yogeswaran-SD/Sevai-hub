# 🚀 Sevai Hub — Production Deployment Guide

**Version:** 4.0.0  
**Last Updated:** March 27, 2026  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Deployment Options](#deployment-options)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Troubleshooting](#troubleshooting)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Quick Start (Docker)

The fastest way to deploy Sevai Hub is using Docker Compose.

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-org/sevaihub.git
cd sevaihub

# 2. Copy environment template
cp .env.docker.example .env

# 3. Edit .env with your secrets (IMPORTANT!)
# - Change DB_PASSWORD
# - Change SECRET_KEY (use: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - Change ADMIN_PASSWORD_HASH (use script in Backend Setup section)
# - Set CORS_ORIGINS to your domain
# nano .env

# 4. Build and start all services
docker-compose up -d

# 5. Verify all services are running
docker-compose ps

# 6. Check logs (watch for errors)
docker-compose logs -f
```

**Access the application:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Pre-Deployment Checklist

Before deploying to production, verify these critical items:

### Security ✅
- [ ] `.env` file is NOT committed to git
- [ ] All `.env` files are in `.gitignore`
- [ ] `SECRET_KEY` is strong (32+ random characters)
- [ ] `ADMIN_PASSWORD_HASH` is bcrypt hash (starts with `$2b$`)
- [ ] `DEBUG=False` in production
- [ ] `ALLOW_ORIGINS_ALL=False` in production
- [ ] CORS origins are set to real domain(s) only
- [ ] No hardcoded secrets in source code

### Database ✅
- [ ] PostgreSQL 12+ is installed
- [ ] PostGIS extension is enabled
- [ ] Database user has limited privileges
- [ ] Database backups are configured
- [ ] Database URL is correct in `.env`

### Frontend ✅
- [ ] `VITE_API_URL` points to correct backend URL
- [ ] Build succeeds without errors: `cd frontend && npm run build`
- [ ] No console.log() statements in production code
- [ ] Environment variables are loaded from `.env`

### Backend ✅
- [ ] Python 3.9+ is installed
- [ ] All dependencies installed: `pip install -r backend/requirements.txt`
- [ ] Database migrations ready: `alembic upgrade head`
- [ ] CORS configuration is restrictive
- [ ] Email/SMS delivery is configured (if needed)

### Infrastructure ✅
- [ ] HTTPS certificate obtained (Let's Encrypt recommended)
- [ ] Reverse proxy (Nginx) configured
- [ ] Firewall rules allow 80, 443 only
- [ ] DNS records point to correct IP
- [ ] Health check endpoints are accessible

---

## Environment Configuration

### Backend (.env in root)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@db.example.com:5432/sevaihub

# Security
SECRET_KEY=generated_secret_key_32_chars_minimum
ENVIRONMENT=production
DEBUG=False

# Admin (high security)
ADMIN_MOBILE=9999999999
ADMIN_AADHAAR=123456789012
ADMIN_SECRET_KEY=admin_secret_key_here
ADMIN_PASSWORD_HASH=$2b$12$your_bcrypt_hash_here

# CORS
CORS_ORIGINS=https://app.sevaihub.com,https://www.sevaihub.com

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env in frontend/)

```bash
VITE_API_URL=https://api.sevaihub.com
VITE_ENVIRONMENT=production
VITE_ENABLE_DEBUG_LOGS=false
```

---

## Database Setup

### PostgreSQL with PostGIS

**Option 1: Docker (Recommended)**
```bash
docker run -d \
  --name sevaihub-postgres \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=sevaihub \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgis/postgis:16-3.4
```

**Option 2: Manual Installation**

```bash
# Install PostgreSQL and PostGIS
sudo apt-get install postgresql postgresql-contrib postgis

# Create database and extensions
sudo -u postgres psql <<EOF
CREATE DATABASE sevaihub;
\connect sevaihub
CREATE EXTENSION postgis;
CREATE EXTENSION uuid-ossp;
EOF

# Create application user
sudo -u postgres psql <<EOF
CREATE USER sevaihub_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE sevaihub TO sevaihub_user;
GRANT USAGE ON SCHEMA public TO sevaihub_user;
GRANT CREATE ON SCHEMA public TO sevaihub_user;
EOF
```

### Run Migrations

```bash
cd backend

# Upgrade to latest schema
alembic upgrade head

# Seed demo data (optional)
python seed.py
```

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Backup database
docker-compose exec postgres pg_dump -U postgres sevaihub > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres sevaihub < backup.sql
```

### Option 2: Kubernetes

```bash
# Build images
docker build -t sevaihub-backend:latest backend/
docker build -t sevaihub-frontend:latest frontend/

# Push to registry
docker tag sevaihub-backend:latest your-registry/sevaihub-backend:latest
docker push your-registry/sevaihub-backend:latest

# Deploy with kubectl
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

### Option 3: Traditional Server (Linux/Ubuntu)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3.11 python3-pip postgres nginx certbot

# Clone and setup
git clone https://github.com/your-org/sevaihub.git
cd sevaihub/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 app.main:app

# Configure Nginx (see nginx-config-example.conf)
sudo cp deployment/nginx.conf /etc/nginx/sites-available/sevaihub
sudo ln -s /etc/nginx/sites-available/sevaihub /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## Post-Deployment Verification

### Health Checks

```bash
# Backend health
curl https://api.sevaihub.com/health

# Frontend accessibility
curl https://app.sevaihub.com/

# API documentation
curl https://api.sevaihub.com/docs
```

### Test Authentication

```bash
# User login
curl -X POST https://api.sevaihub.com/auth/login/user \
  -H "Content-Type: application/json" \
  -d '{"identifier":"1234567890","password":"demo123"}'

# Admin login
curl -X POST https://api.sevaihub.com/auth/login/admin \
  -H "Content-Type: application/json" \
  -d '{"mobile":"9999999999","aadhaar":"123456789012","password":"Admin@SevaiHub2024"}'
```

### Database Verification

```bash
# Connect to database
psql -h db.example.com -U postgres -d sevaihub

# Check tables
\dt

# Check users and technicians count
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM technicians;
```

---

## Troubleshooting

### Database Connection Failed
```bash
# Check database is running
docker-compose ps postgres

# Check connection string in .env
grep DATABASE_URL .env

# Test connection manually
psql postgresql://user:password@host:5432/db
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

### CORS Errors
- Check `CORS_ORIGINS` in `.env` includes your frontend domain
- Ensure frontend is making requests to correct API URL
- Check browser console for full error message

### Static Files Not Loading
```bash
# Rebuild frontend
cd frontend && npm run build

# Check nginx is serving dist folder correctly
# See default.conf for proper configuration
```

### Slow Performance
```bash
# Check database indexes
\d technicians

# Monitor database queries
EXPLAIN ANALYZE SELECT * FROM technicians WHERE is_available = true;

# Check API response times
docker-compose logs backend | grep "duration"
```

---

## Monitoring & Maintenance

### Docker Logs
```bash
# View all logs
docker-compose logs

# Follow backend logs
docker-compose logs -f backend

# Filter by service
docker-compose logs postgres
```

### Database Backups

```bash
# Automated daily backup (crontab)
0 2 * * * cd /home/sevaihub && docker-compose exec -T postgres pg_dump -U postgres sevaihub > backups/backup-$(date +\%Y\%m\%d).sql

# Manual backup
docker-compose exec postgres pg_dump -U postgres sevaihub > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres sevaihub < backup.sql
```

### Certificate Renewal (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d api.sevaihub.com -d app.sevaihub.com

# Auto-renewal (runs daily)
sudo certbot renew --dry-run
```

### Performance Monitoring

- Use Docker stats: `docker stats`
- Monitor database: `SELECT * FROM pg_stat_statements;`
- Check error logs: `docker-compose logs backend | grep ERROR`
- Set up Sentry for error tracking
- Use New Relic or DataDog for APM

---

## Production Security Hardening

1. **Firewall Rules**
   - Allow only 80, 443 (HTTP/HTTPS)
   - Restrict database access to application server only
   - Use security groups/network policies

2. **HTTPS/TLS**
   - Use Let's Encrypt for free certificates
   - Set `HSTS` header (force HTTPS)
   - Enable `X-Frame-Options: DENY`

3. **Secrets Management**
   - Use AWS Secrets Manager or HashiCorp Vault
   - Never commit `.env` files
   - Rotate secrets regularly

4. **Rate Limiting**
   - Enable rate limiting on auth endpoints
   - Configure DDoS protection

5. **Logging**
   - Send logs to centralized system (ELK, Splunk, etc.)
   - Monitor error rates
   - Set up alerts for critical errors

---

## Support & Troubleshooting

For issues and questions:
1. Check deployment logs: `docker-compose logs -f`
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Check [SECURITY.md](SECURITY.md) for security concerns
4. Open issue on GitHub with error logs

---

**Version History:**
- v4.0.0 (2026-03-27) - Added Docker and Kubernetes support
- v3.0.0 (2026-03-01) - Initial production release
