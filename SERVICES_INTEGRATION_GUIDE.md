# Sevai Hub - New Services Integration Guide

## Overview

This guide explains how to integrate and use the newly connected services in Sevai Hub:

1. **Redis** - Caching layer for performance
2. **MinIO** - File storage (S3-compatible)
3. **Nginx** - Reverse proxy & load balancing
4. **Email/SMTP** - Email notifications
5. **Twilio** - SMS notifications

## Quick Start

### 1. Start All Services

```bash
# From project root
docker-compose up -d

# Verify all services are running
docker-compose ps
```

Expected output:
```
NAME                 STATUS
sevaihub-postgres    UP (healthy)
sevaihub-redis       UP (healthy)
sevaihub-minio       UP (healthy)
sevaihub-backend     UP (healthy)
sevaihub-frontend    UP (healthy)
sevaihub-proxy       UP (healthy)
```

### 2. Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | React app (via Nginx) |
| API | http://localhost/api | Backend API (via Nginx) |
| API Docs | http://localhost/docs | Swagger documentation |
| MinIO Console | http://localhost:9001 | File browser & management |
| Redis CLI | localhost:6379 | Cache management (CLI only) |

---

## Service Configuration

### 1. Redis Cache

**Environment Variables:**
```env
REDIS_URL=redis://redis:6379
```

**Usage in Code:**
```python
from app.services import cache_get, cache_set, cache_delete

# Set cache (1 hour expiry)
await cache_set("technician:123:status", "available", expire=3600)

# Get cache
status = await cache_get("technician:123:status")

# Delete cache
await cache_delete("technician:123:status")

# Cache technician status
await cache_technician_status(123, "busy")
```

**When to Use:**
- Caching technician availability status
- Caching service location data
- Session caching for performance
- Frequently accessed data

---

### 2. MinIO Object Storage

**Environment Variables:**
```env
MINIO_URL=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=sevaihub
```

**Initial Setup:**
```bash
# Create the default bucket (handled automatically on startup)
# Access MinIO console at http://localhost:9001
# Login with minioadmin / minioadmin123
```

**Usage in Code:**
```python
from app.services import (
    upload_file,
    upload_profile_picture,
    upload_service_document,
    download_file,
    delete_file
)

# Upload profile picture
url = await upload_profile_picture(user_id=1, file_content=file_bytes)

# Upload service document
url = await upload_service_document(service_id=5, filename="invoice.pdf", file_content=pdf_bytes)

# Download file
file_content = await download_file("profiles/1/avatar.jpg")

# Delete file
await delete_file("profiles/1/avatar.jpg")
```

**File Structure:**
```
sevaihub/
├── profiles/{user_id}/
│   └── avatar.jpg
├── services/{service_id}/
│   ├── invoice.pdf
│   └── photos/
├── technicians/{tech_id}/
│   └── certificates/
│       ├── license.pdf
│       └── certification.pdf
```

---

### 3. Nginx Reverse Proxy

**Configuration File:** `nginx.conf`

**Features:**
- Routes `/api/*` to FastAPI backend
- Routes `/` to React frontend
- Health check endpoint at `/health`
- Security headers configured
- Gzip compression enabled
- Static asset caching

**Endpoints:**
```
http://localhost:80/          → Frontend
http://localhost:80/api/*     → Backend API
http://localhost:80/docs      → Swagger docs
http://localhost:80/redoc     → ReDoc docs
http://localhost:80/health    → Health check
```

**For Production (HTTPS):**
```nginx
# Uncomment HTTPS section in nginx.conf
# Add SSL certificates to ./certs/ directory
# Ensure ports 80 & 443 are accessible
```

---

### 4. Email/SMTP Service

**Environment Variables:**
```env
# Gmail setup
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-specific-password  # NOT your main password!
EMAILS_FROM_EMAIL=noreply@sevaihub.com
```

**Gmail App Password Setup:**
1. Enable 2-factor authentication on Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows"
4. Use the generated 16-character password

**Usage in Code:**
```python
from app.services import (
    send_email,
    send_password_reset_email,
    send_technician_assignment_email
)

# Send custom email
success = await send_email(
    email_to="user@example.com",
    subject="Welcome to Sevai Hub",
    html_body="<h1>Welcome!</h1>",
    text_body="Welcome to Sevai Hub"
)

# Send password reset email
await send_password_reset_email("user@example.com", reset_token)

# Send technician assignment
await send_technician_assignment_email(
    technician_email="tech@example.com",
    service_name="Plumbing Repair",
    customer_name="John Doe"
)
```

**Email Templates:**
You can create HTML templates in `backend/app/templates/` and load them:
```python
# Example: Create backend/app/templates/email_base.html
with open("app/templates/email_base.html") as f:
    html_template = f.read()
```

---

### 5. SMS/Twilio Service

**Environment Variables:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_PHONE_NUMBER=+12025551234
```

**Twilio Setup:**
1. Create free account at https://www.twilio.com/console
2. Get trial phone number
3. Verify your personal number (for testing)
4. Copy Account SID and Auth Token

**Usage in Code:**
```python
from app.services import (
    send_sms,
    send_technician_assignment_sms,
    send_verification_code_sms,
    send_service_update_sms,
    send_technician_reminder_sms
)

# Send custom SMS
sms_sid = await send_sms("+911234567890", "Hello from Sevai Hub!")

# Send technician assignment
await send_technician_assignment_sms("+919876543210", "Plumbing", "John")

# Send verification code
await send_verification_code_sms("+919876543210", "123456")

# Send service update
await send_service_update_sms("+919876543210", 5, "In Progress")

# Send reminder
await send_technician_reminder_sms("+919876543210", "Plumbing", "2 PM")
```

**Phone Number Format:**
Must be in E.164 format: `+[country code][number]`
- India: `+91XXXXXXXXXX`
- USA: `+1XXXXXXXXXX`
- UK: `+44XXXXXXXXXX`

---

## Integration Examples

### Example 1: Service Assignment Workflow

```python
from app.services import (
    send_technician_assignment_email,
    send_technician_assignment_sms,
    cache_technician_status
)

async def assign_service_to_technician(technician_id, service_id, service_name):
    # Update cache
    await cache_technician_status(technician_id, "assigned")
    
    # Get technician details from DB
    technician = db.query(Technician).get(technician_id)
    
    # Send email notification
    await send_technician_assignment_email(
        technician.email,
        service_name,
        "Customer Name"
    )
    
    # Send SMS notification
    await send_technician_assignment_sms(
        technician.phone,
        service_name,
        "Customer Name"
    )
```

### Example 2: Profile Management

```python
from app.services import upload_profile_picture, download_file

async def update_user_profile(user_id, profile_picture):
    # Upload new picture
    picture_url = await upload_profile_picture(
        user_id,
        await profile_picture.read()
    )
    
    # Save URL to database
    user = db.query(User).get(user_id)
    user.profile_picture_url = picture_url
    db.commit()
```

### Example 3: Document Management

```python
from app.services import upload_service_document, download_file

async def create_service_invoice(service_id, invoice_pdf):
    # Upload invoice
    url = await upload_service_document(
        service_id,
        "invoice.pdf",
        await invoice_pdf.read()
    )
    
    # Send via email
    await send_email(
        customer_email,
        "Your Invoice",
        f"Invoice: {url}"
    )
```

---

## Troubleshooting

### Redis Connection Issues
```bash
# Test Redis connection
docker exec sevaihub-redis redis-cli ping
# Expected: PONG

# Check Redis logs
docker logs sevaihub-redis
```

### MinIO Connection Issues
```bash
# Test MinIO health
curl http://localhost:9000/minio/health/live

# Access MinIO console
# http://localhost:9001
# Username: minioadmin
# Password: minioadmin123
```

### Email Not Sending
```python
# Check if configured
from app.core.config import settings
print(settings.SMTP_USER)  # Should not be empty/None
print(settings.SMTP_PASSWORD)  # Should not be empty/None

# Test SMTP connection
python -m smtplib -c "SMTP('smtp.gmail.com', 587).starttls()"
```

### SMS Not Sending
```python
# Verify Twilio config
from app.core.config import settings
print(settings.TWILIO_ACCOUNT_SID)      # Should not be empty
print(settings.TWILIO_AUTH_TOKEN)       # Should not be empty
print(settings.TWILIO_PHONE_NUMBER)     # Should be E.164 format

# Check Twilio logs at https://www.twilio.com/console/sms/logs
```

### Nginx Routing Issues
```bash
# Check Nginx logs
docker logs sevaihub-proxy

# Test backend availability
curl http://localhost:8000/health

# Test frontend availability
curl http://localhost:8080/health
```

---

## Production Deployment Checklist

- [ ] Change Redis password (add AUTH in docker-compose.yml)
- [ ] Change MinIO credentials
- [ ] Set up email SMTP (preferably SendGrid, AWS SES, or Mailgun)
- [ ] Set up Twilio account with production phone number
- [ ] Update CORS_ORIGINS to your domain
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS in Nginx (uncomment HTTPS section)
- [ ] Set DEBUG=False
- [ ] Test all services before deployment
- [ ] Set up monitoring/logging
- [ ] Configure backup for data volumes

---

## Development Tips

### Reset Services
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data!)
docker-compose down -v

# Start fresh
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f minio
```

### Access Service CLIs
```bash
# Redis CLI
docker exec sevaihub-redis redis-cli

# MinIO console
# http://localhost:9001
```

---

## Next Steps

1. Implement email templates for different notification types
2. Add file upload endpoints to API
3. Implement service assignment with notifications
4. Set up SMS reminders for technicians
5. Add document download API endpoints
6. Configure CloudFlare CDN for static assets (production)
7. Set up automated backups for MinIO data
8. Implement email delivery tracking
