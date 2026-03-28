#!/bin/bash
# Pre-Deployment Verification Checklist for Sevai Hub
# Run this script before deploying to production
# Usage: bash pre-deployment-check.sh

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🔐 SEVAI HUB — PRE-DEPLOYMENT SECURITY & CONFIGURATION VERIFICATION"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

PASSED=0
FAILED=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test helper functions
check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
}

# 1. Environment File Checks
echo -e "${BLUE}1. Environment Configuration${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if [ -f ".env.production" ]; then
    check_pass ".env.production exists"
else
    check_fail ".env.production not found - copy from .env.docker.example"
fi

if [ -f ".env" ]; then
    check_warn ".env file exists in repo - ensure it's in .gitignore"
else
    check_pass ".env file not tracked (git-ignored)"
fi

if grep -q "ENVIRONMENT=production" .env.production 2>/dev/null; then
    check_pass "ENVIRONMENT set to production"
else
    check_fail "ENVIRONMENT not set to production"
fi

if grep -q "DEBUG=False" .env.production 2>/dev/null; then
    check_pass "DEBUG mode is disabled"
else
    check_fail "DEBUG mode is enabled - disable for production"
fi

# 2. Secret Key Validation
echo ""
echo -e "${BLUE}2. Security Credentials Validation${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if grep -q "SECRET_KEY=your_secure" .env.production 2>/dev/null; then
    check_fail "SECRET_KEY is default placeholder - generate new secure key"
elif [ -f ".env.production" ]; then
    secret_key=$(grep "SECRET_KEY=" .env.production | cut -d'=' -f2)
    if [ ${#secret_key} -ge 32 ]; then
        check_pass "SECRET_KEY is 32+ characters"
    else
        check_fail "SECRET_KEY must be minimum 32 characters"
    fi
else
    check_warn "Cannot verify SECRET_KEY"
fi

if grep -q 'ADMIN_PASSWORD_HASH=\$2b\$' .env.production 2>/dev/null; then
    check_pass "ADMIN_PASSWORD_HASH is bcrypt hashed"
else
    check_fail "ADMIN_PASSWORD_HASH must be bcrypt hash (starts with \$2b\$)"
fi

if grep -q "CORS_ORIGINS=http://localhost" .env.production 2>/dev/null; then
    check_fail "CORS_ORIGINS contains localhost - set to production domain"
else
    check_pass "CORS_ORIGINS configured for production"
fi

if grep -q "VITE_API_URL=http://localhost" .env.production 2>/dev/null; then
    check_fail "VITE_API_URL contains localhost - set to production URL"
else
    check_pass "VITE_API_URL configured for production"
fi

# 3. Database Configuration
echo ""
echo -e "${BLUE}3. Database Configuration${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if grep -q "DB_PASSWORD=" .env.production 2>/dev/null; then
    db_pass=$(grep "DB_PASSWORD=" .env.production | cut -d'=' -f2)
    if [ ${#db_pass} -ge 16 ]; then
        check_pass "Database password is strong (16+ chars)"
    else
        check_fail "Database password should be 16+ characters"
    fi
else
    check_fail "DB_PASSWORD not configured"
fi

if grep -q "DATABASE_URL=" .env.production 2>/dev/null; then
    check_pass "DATABASE_URL is configured"
else
    check_fail "DATABASE_URL not configured"
fi

# 4. Git Configuration
echo ""
echo -e "${BLUE}4. Git Configuration${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if grep -q "\.env" .gitignore 2>/dev/null; then
    check_pass ".env is in .gitignore"
else
    check_fail ".env should be in .gitignore"
fi

if [ -d ".git" ]; then
    check_pass "Repository is initialized"
    
    if git ls-files --others --excluded-standard | grep -q ".env"; then
        check_fail ".env files are untracked (good - keep it this way)"
    else
        check_pass ".env is properly git-ignored"
    fi
else
    check_fail "Git repository not initialized"
fi

# 5. Docker Configuration
echo ""
echo -e "${BLUE}5. Docker & Containerization${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml not found"
fi

if [ -f "backend/Dockerfile" ]; then
    check_pass "Backend Dockerfile exists"
else
    check_fail "Backend Dockerfile not found"
fi

if [ -f "frontend/Dockerfile" ]; then
    check_pass "Frontend Dockerfile exists"
else
    check_fail "Frontend Dockerfile not found"
fi

# Check for non-root user in Dockerfiles
if grep -q "USER appuser" backend/Dockerfile 2>/dev/null; then
    check_pass "Backend uses non-root user"
else
    check_warn "Backend should use non-root user for security"
fi

# 6. Code Quality
echo ""
echo -e "${BLUE}6. Code Quality & Standards${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if [ -f "backend/requirements.txt" ]; then
    check_pass "Backend requirements.txt exists"
    
    # Check for security packages
    if grep -q "passlib" backend/requirements.txt && grep -q "python-jose" backend/requirements.txt; then
        check_pass "Required security packages installed"
    else
        check_fail "Missing security packages (passlib, python-jose)"
    fi
else
    check_fail "Backend requirements.txt not found"
fi

if [ -f "frontend/package.json" ]; then
    check_pass "Frontend package.json exists"
else
    check_fail "Frontend package.json not found"
fi

# 7. Database Migrations
echo ""
echo -e "${BLUE}7. Database Migrations${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if [ -d "backend/alembic" ]; then
    check_pass "Alembic migration directory exists"
    
    if [ -f "backend/alembic/versions/001_initial_schema.py" ]; then
        check_pass "Initial migration file exists"
    else
        check_fail "Initial migration file missing"
    fi
else
    check_fail "Alembic migrations not configured"
fi

# 8. Documentation
echo ""
echo -e "${BLUE}8. Documentation${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if [ -f "PRODUCTION_DEPLOYMENT_GUIDE.md" ]; then
    check_pass "Production deployment guide exists"
else
    check_fail "Production deployment guide missing"
fi

if [ -f "README.md" ]; then
    check_pass "README.md exists"
else
    check_fail "README.md missing"
fi

# TLS/SSL Warning
echo ""
echo -e "${BLUE}9. SSL/TLS Certificate${NC}"
echo "──────────────────────────────────────────────────────────────────────────────────"

if [ -f "/etc/letsencrypt/live/*/fullchain.pem" ] 2>/dev/null || [ -d "/etc/letsencrypt/live" ] 2>/dev/null; then
    check_pass "SSL certificate directory exists"
else
    check_warn "SSL certificate not yet configured - will need to be configured after deployment"
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo -e "📊 VERIFICATION SUMMARY"
echo "════════════════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}PASSED:${NC}  $PASSED"
echo -e "${YELLOW}WARNINGS:${NC} $WARNINGS"
echo -e "${RED}FAILED:${NC}  $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the PRODUCTION_DEPLOYMENT_GUIDE.md"
    echo "2. Build Docker images: docker-compose build --no-cache"
    echo "3. Start services: docker-compose up -d"
    echo "4. Initialize database: docker-compose exec backend alembic upgrade head"
    echo "5. Test endpoints: curl http://localhost:8000/health"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Critical issues found - fix before deploying${NC}"
    echo ""
    echo "Issues found:"
    echo "- Ensure all secrets are properly configured"
    echo "- Change all placeholder values to production values"
    echo "- Verify all security settings are correct"
    echo ""
    exit 1
fi
