# HOSTING GUIDE - SEVAI HUB

## Quick Start Options

Choose your hosting platform and follow the steps below.

---

## 🌐 Option 1: AWS EC2 (Recommended for Scale)

### Prerequisites
- AWS account with EC2 access
- Ubuntu 22.04 LTS instance (t3.medium or larger)
- 20GB storage minimum

### Step-by-Step Deployment

**1. Launch EC2 Instance**
```bash
# Use Ubuntu 22.04 LTS AMI
# Security groups: Allow ports 22, 80, 443
Instance type: t3.medium (2 vCPU, 4GB RAM minimum)
Storage: 20GB+ SSD
```

**2. Connect and Update System**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
sudo apt update && sudo apt upgrade -y
```

**3. Install Required Software**
```bash
# Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Nginx
sudo apt install nginx -y

# Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

**4. Clone and Deploy**
```bash
cd /opt
sudo git clone https://github.com/youruser/sevaihub.git
cd sevaihub
sudo chown -R ubuntu:ubuntu .

# Create .env file
cp .env.example .env
nano .env  # Update with your configuration

# Start services
docker-compose up -d
```

**5. Configure SSL**
```bash
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com
```

**6. Configure Nginx**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/sevaihub
sudo ln -s /etc/nginx/sites-available/sevaihub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**7. Verify Deployment**
```bash
curl https://your-domain.com/api/health
```

**Cost**: ~$10-20/month with AWS free tier

---

## 🚀 Option 2: DigitalOcean App Platform (Easiest)

### Prerequisites
- DigitalOcean account
- Docker images pushed to Docker Hub

### Step-by-Step Deployment

**1. Push Docker Images to Docker Hub**
```bash
docker tag sevaihub-backend:latest yourusername/sevaihub-backend:latest
docker tag sevaihub-frontend:latest yourusername/sevaihub-frontend:latest

docker login
docker push yourusername/sevaihub-backend:latest
docker push yourusername/sevaihub-frontend:latest
```

**2. Create App on DigitalOcean**
```
Dashboard → Apps → Create App
Connect your Docker Hub registry
Select repository: yourusername/sevaihub-backend
```

**3. Add Services**
- Service 1: Backend (yourusername/sevaihub-backend)
- Service 2: Frontend (yourusername/sevaihub-frontend)
- Database: PostgreSQL (managed)
- Cache: Redis (managed)

**4. Configure Environment Variables**
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your_secret_here
```

**5. Deploy**
- Click "Deploy" button
- Wait for services to start
- Get auto-generated URL

**Cost**: ~$12-15/month with managed databases

**Advantage**: No server management, automatic SSL, easy scaling

---

## 🏗️ Option 3: Render (Fast & Free Tier Available)

### Prerequisites
- Render account
- GitHub repository linked

### Step-by-Step Deployment

**1. Connect GitHub**
```
Render Dashboard → New → Web Service → Connect Repository
```

**2. Create Backend Service**
```
Name: sevaihub-backend
Environment: Docker
Build Command: docker-compose build backend
Start Command: docker-compose up
```

**3. Add Environment Variables**
```
Database credentials
Redis connection string
JWT secret
```

**4. Create Frontend Service**
```
Name: sevaihub-frontend
Build command: npm run build
Start command: npm run preview
Publish directory: dist
```

**5. Deploy**
- Click "Deploy Web Service"
- Services will auto-start
- Get permanent URL (FREE tier limits apply)

**Cost**: Free tier available (with limitations)

**Note**: Free tier may have cold starts

---

## 🐳 Option 4: Docker Swarm (Self-Managed)

### Prerequisites
- VPS or dedicated server
- Linux (Ubuntu 22.04 recommended)
- Minimum: 2GB RAM, 10GB storage

### Step-by-Step Deployment

**1. Setup VPS**
```bash
# Rent VPS from: Linode, Hetzner, UpCloud
# Ubuntu 22.04 LTS recommended
# Minimum specs: 2 vCPU, 2GB RAM, 10GB SSD
```

**2. Install Docker**
```bash
ssh root@your-vps-ip
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**3. Initialize Swarm**
```bash
docker swarm init
docker node ls
```

**4. Deploy Stack**
```bash
# Create docker-compose.yml with replicas
docker stack deploy -c docker-compose.yml sevaihub
docker stack services sevaihub
```

**5. Setup Nginx Reverse Proxy**
```bash
apt install nginx certbot python3-certbot-nginx -y
# Configure nginx to route to swarm
```

**6. Monitor**
```bash
docker stats
docker logs sevaihub_backend.1
```

**Cost**: ~$5-10/month for basic VPS

---

## 📱 Option 5: Heroku (Deprecated - Alternative: Railway)

### Prerequisites
- Railway account (Heroku alternative)
- GitHub repository

### Step-by-Step Deployment

**1. Create Railway Project**
```
Railway.app Dashboard → New Project
```

**2. Add Services**
```
- PostgreSQL (add plugin)
- Redis (add plugin)
- Deploy from GitHub
```

**3. Configure Buildpack**
```
Buildpack: Heroku/Docker or Python (for backend)
```

**4. Set Environment Variables**
```
DATABASE_URL
REDIS_URL
SECRET_KEY
```

**5. Deploy**
```bash
git push  # Auto-deploys on push
```

**Cost**: ~$7-15/month

---

## 💻 Option 6: Home Server / Local VPS

### Prerequisites
- Linux server (Ubuntu 22.04)
- Static IP address
- Domain name pointing to your IP

### Step-by-Step Deployment

**1. Setup Home Server**
```bash
# Install Ubuntu Server 22.04
# Open ports 80 and 443 in router
# Setup port forwarding to your server
```

**2. Install Requirements**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose nginx certbot -y
```

**3. Deploy Application**
```bash
git clone https://github.com/youruser/sevaihub.git
cd sevaihub
docker-compose up -d
```

**4. Setup SSL and Domain**
```bash
sudo certbot certonly --standalone -d your-domain.com
sudo certbot install --nginx
```

**5. Configure Nginx**
```bash
# Configure reverse proxy
sudo nano /etc/nginx/sites-available/sevaihub
sudo systemctl restart nginx
```

**Cost**: FREE (only electricity)

**Caution**: Home internet ISP may block port 80/443

---

## Comparison Table

| Platform | Cost | Difficulty | Scalability | Uptime SLA |
|----------|------|-----------|-------------|-----------|
| AWS EC2 | $10-20 | Medium | Excellent | 99.95% |
| DigitalOcean | $12-15 | Easy | Very Good | 99.99% |
| Render | Free-$7 | Very Easy | Good | 99.9% |
| Docker Swarm | $5-10 | Hard | Excellent | Manual |
| Railway | $7-15 | Easy | Good | 99.9% |
| Home Server | Free | Hard | Limited | Variable |

---

## Configuration Files for Deployment

### .env.production (Create for production)
```env
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/sevaihub
DB_PASSWORD=your_secure_password

# Cache
REDIS_URL=redis://redis-host:6379

# Storage
MINIO_ENDPOINT=storage-host:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

# API
API_URL=https://api.your-domain.com
FRONTEND_URL=https://www.your-domain.com

# Security
SECRET_KEY=your_super_secret_key_minimum_32_chars
ADMIN_PASSWORD_HASH=$2b$12$...

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# CORS
CORS_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]
```

### docker-compose.production.yml (For production scaling)
```yaml
version: '3.8'

services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "127.0.0.1:5432:5432"  # Only local access
    
  backend:
    replicas: 2
    environment:
      DATABASE_URL: ${DATABASE_URL}
    
  frontend:
    replicas: 2
```

---

## Pre-Deployment Checklist

Before going live, verify:

- [ ] All services running correctly
- [ ] SSL certificates installed
- [ ] Database backup configured
- [ ] CORS origins updated
- [ ] Email/SMS configured
- [ ] Monitoring setup
- [ ] Logs configured
- [ ] Scaling policies set
- [ ] Disaster recovery plan ready
- [ ] Team trained on deployment

---

## Post-Deployment Monitoring

### Monitor These Metrics
```bash
# CPU and Memory
docker stats

# Database Performance
docker logs sevaihub-postgres | grep slow

# API Response Times
curl -w "@curl-format.txt" -o /dev/null https://your-domain.com/api/health

# Error Rates
docker logs sevaihub-backend | grep ERROR
```

### Set Up Alerts For
- Service down (HTTP 5xx)
- High memory usage (>80%)
- Database connection errors
- Certificate expiration (30 days before)
- Low disk space (<10% free)

---

## Domain Setup

### For Your Domain (example.com)
```
1. Buy domain from: GoDaddy, Namecheap, Route53
2. Point nameservers to your host provider
3. Create A record pointing to your server IP
4. Wait for DNS propagation (15-30 mins)
5. Install SSL certificate
```

---

## Support & Troubleshooting

### Common Issues

**Services won't start**
```bash
docker-compose logs
docker-compose up -d --no-deps --build backend
```

**SSL certificate errors**
```bash
certbot renew --force-renewal
systemctl restart nginx
```

**Database connection issues**
```bash
docker exec sevaihub-postgres psql -U postgres -d sevaihub
```

**Port already in use**
```bash
sudo lsof -i :8000
sudo kill -9 PID
```

---

## Recommended Hosting Choice

**For beginners**: DigitalOcean or Render  
**For enterprise**: AWS with RDS + ElastiCache  
**For low budget**: Docker Swarm on VPS  
**For production**: AWS or DigitalOcean with managed databases

---

*Deployment Guide v1.0*  
*Last Updated: 2026-03-28*
