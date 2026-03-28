# 📊 Sevai Hub — Operations & Maintenance Guide

**Version:** 4.0.0  
**Last Updated:** March 27, 2026  
**Audience:** DevOps, Site Reliability Engineers (SREs)

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Monitoring & Alerts](#monitoring--alerts)
3. [Performance Tuning](#performance-tuning)
4. [Database Management](#database-management)
5. [Backup & Disaster Recovery](#backup--disaster-recovery)
6. [Scaling Considerations](#scaling-considerations)
7. [Health Checks & Diagnostics](#health-checks--diagnostics)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Architecture

### System Components

```
┌─────────────────┐
│ Load Balancer   │ (Nginx/AWS ELB)
│ (HTTPS only)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│Frontend │ │ Backend  │
│(React)  │ │(FastAPI) │
└────┬────┘ └────┬─────┘
     │            │
     └────┬───────┘
          ▼
    ┌──────────────┐
    │ PostgreSQL   │
    │ + PostGIS    │
    └──────────────┘
```

### Deployment Topology

**Production:**
- Containerized (Docker)
- Orchestrated (Docker Swarm or Kubernetes)
- Geographic distribution (CDN for frontend)
- Database replication for HA

**Staging:**
- Single machine or small cluster
- Same configuration as production
- Test new releases before prod

**Development:**
- Local machine
- Docker Compose for simplicity

---

## 📈 Monitoring & Alerts

### Key Metrics to Monitor

**Backend API:**
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Request throughput (req/sec)
- Database query time
- Memory usage
- CPU usage

**Database:**
- Connection pool usage
- Query latency
- Disk usage
- Replication lag (if applicable)
- Slow query log
- Transaction volume

**Frontend:**
- Page load time
- JavaScript errors
- API call failures
- User sessions
- Cache hit rate

### Monitoring Tools

**Docker Containers:**
```bash
# Real-time stats
docker stats sevaihub-backend sevaihub-postgres

# Inspect container logs
docker logs -f sevaihub-backend

# View resource limits
docker inspect sevaihub-backend | grep -A 5 '"Memory"'
```

**Application Metrics:**

Option 1: Prometheus + Grafana
```bash
# Install Prometheus client
pip install prometheus-client

# Export metrics in FastAPI
from prometheus_client import Counter, Histogram
request_count = Counter('requests_total', 'Total requests')
```

Option 2: Cloud-Native Solutions
- AWS CloudWatch
- Google Cloud Monitoring
- DataDog
- New Relic

**Alert Thresholds (Recommended):**

| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | > 1% | > 5% |
| Response Time (p95) | > 1s | > 5s |
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 75% | > 90% |
| Disk Usage | > 80% | > 95% |
| DB Connection Pool | > 80% | > 95% |

### Alerting Setup

```yaml
# Example: Prometheus alerts rule
groups:
  - name: sevaihub_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: SlowResponse
        expr: histogram_quantile(0.95, response_time) > 1
        annotations:
          summary: "Slow API response detected"
```

---

## ⚡ Performance Tuning

### Database Query Optimization

```sql
-- Create indexes for frequent queries
CREATE INDEX idx_technicians_available 
  ON technicians(is_available) WHERE is_available = true;

CREATE INDEX idx_technicians_category 
  ON technicians(service_category);

-- Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM technicians 
  WHERE is_available = true 
  AND service_category = 'Plumber';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

### Backend Optimization

```python
# Use connection pooling
# backend/app/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,  # Recycle connections
)
```

### Caching Strategy

```python
# Redis caching (optional)
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_service_categories():
    return db.query(ServiceCategory).all()

# Cache for 5 minutes
@router.get("/services/")
async def get_services(cache: Cache = Depends()):
    cached = cache.get("services_list")
    if cached:
        return cached
    services = db.query(Service).all()
    cache.set("services_list", services, 300)
    return services
```

### Load Balancing

**Nginx Configuration:**
```nginx
upstream backend {
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}

server {
    location /api/ {
        proxy_pass http://backend;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
}
```

---

## 🗄️ Database Management

### Regular Maintenance

**Weekly:**
```sql
-- Vacuum (reclaim storage)
VACUUM ANALYZE;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Monthly:**
```sql
-- Reindex (if needed)
REINDEX DATABASE sevaihub;

-- Analyze table statistics
ANALYZE;

-- Check for bloated tables
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size DESC;
```

### Connection Management

```sql
-- View active connections
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';

-- Monitor connection pool
-- backend/alembic/versions/...
SELECT * FROM pg_stat_database WHERE datname = 'sevaihub';
```

### Replication (High Availability)

**Master-Slave Setup:**
```bash
# On primary server
sudo su - postgres
pg_basebackup -h localhost -D /var/lib/postgresql/standby -U replicator -v -P -W -R

# On standby server
pg_ctl -D /var/lib/postgresql/standby -l logfile start
```

---

## 💾 Backup & Disaster Recovery

### Automated Backups

**Script: `/usr/local/bin/backup-sevaihub.sh`**
```bash
#!/bin/bash

BACKUP_DIR="/backups/sevaihub"
DB_NAME="sevaihub"
RETENTION_DAYS=30

# Create backup
BACKUP_FILE="$BACKUP_DIR/sevaihub-$(date +%Y%m%d-%H%M%S).sql.gz"
pg_dump $DB_NAME | gzip > $BACKUP_FILE

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE s3://backups-bucket/sevaihub-db/

# Delete old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron Schedule (daily at 2 AM):**
```bash
0 2 * * * /usr/local/bin/backup-sevaihub.sh >> /var/log/backup.log 2>&1
```

### Recovery Procedure

```bash
# List available backups
ls -lh /backups/sevaihub/

# Restore from backup
gunzip < /backups/sevaihub/sevaihub-20260327-020000.sql.gz | psql sevaihub

# Verify restore
psql sevaihub -c "SELECT COUNT(*) FROM users;"
```

### Point-in-Time Recovery (PITR)

```sql
-- Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'

-- Restore to specific point in time
-- Use recovery.target_timeline and recovery.target_time
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

**Add Backend Instances:**
```bash
# Run multiple backend containers
docker-compose up -d --scale backend=3

# Update load balancer config with new instances
```

**Database Read Replicas:**
```bash
# Create read replica
docker run -d --name postgres-replica \
  -e POSTGRES_REPLICATION_MODE=slave \
  postgis/postgis:16-3.4
```

### Vertical Scaling

**Increase Resources:**
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

---

## 🏥 Health Checks & Diagnostics

### Health Endpoints

```bash
# Backend health
curl -s http://localhost:8000/health | jq .

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "services": ["auth", "users", "technicians", "admin"]
# }

# Frontend health
curl -s http://localhost:80/health
```

### Diagnostic Commands

```bash
# Check container status
docker ps -a

# View container logs
docker logs sevaihub-backend | tail -50

# Inspect network connectivity
docker exec sevaihub-backend ping postgres

# Database connectivity
docker exec sevaihub-backend psql postgresql://user:pass@postgres:5432/sevaihub -c "SELECT 1;"
```

### Performance Diagnostics

```bash
# Generate load test
ab -n 1000 -c 10 http://localhost:8000/health

# Monitor real-time performance
watch -n 1 'docker stats sevaihub-backend'

# Check API response times
time curl http://localhost:8000/services/
```

---

## 🔧 Common Issues & Solutions

### Issue: High CPU Usage
**Diagnosis:**
```bash
docker stats sevaihub-backend
```

**Solutions:**
- Optimize slow database queries
- Increase backend instances (scale horizontally)
- Implement caching
- Review application code for infinite loops

### Issue: Database Connection Failures
**Diagnosis:**
```bash
docker logs sevaihub-postgres | grep -i error
psql postgresql://user:pass@localhost:5432/sevaihub -c "SELECT 1;"
```

**Solutions:**
- Check database is running: `docker ps | grep postgres`
- Verify DATABASE_URL in `.env`
- Check firewall rules
- Increase max_connections in PostgreSQL

### Issue: Slow API Response
**Diagnosis:**
```bash
# Check query logs
docker exec sevaihub-postgres psql -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**Solutions:**
- Add database indexes
- Optimize query
- Increase pool_size for connections
- Implement caching

### Issue: Disk Space Running Out
**Diagnosis:**
```bash
docker exec sevaihub-postgres df -h
docker exec sevaihub-postgres SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database;
```

**Solutions:**
- Delete old backups
- Vacuum database
- Implement log rotation
- Increase disk size

### Issue: Memory Leak
**Diagnosis:**
```bash
# Monitor memory over time
watch -n 10 'docker stats --no-stream sevaihub-backend'
```

**Solutions:**
- Review application code for memory leaks
- Check for unclosed database connections
- Monitor for runaway processes
- Implement memory limits: `docker run --memory 4g`

---

## 📞 Escalation & Support

**Level 1 (On-Call):**
- Monitor alerts
- Check logs for obvious issues
- Restart services if needed

**Level 2 (DevOps Team):**
- Database troubleshooting
- Network configuration
- Container orchestration

**Level 3 (Architecture Team):**
- System design issues
- Capacity planning
- Major upgrades

---

**Runbook Last Updated:** March 27, 2026  
**Next Review Due:** June 27, 2026
