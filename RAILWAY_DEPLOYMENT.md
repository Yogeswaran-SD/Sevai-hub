# SevaiHub Deployment on Railway

Complete step-by-step guide to deploy SevaiHub on Railway.

## Prerequisites

Before deploying, make sure you've pushed the latest code to GitHub:

```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

The repository includes:
- ✅ `backend/Dockerfile` - Python FastAPI container
- ✅ `backend/start.sh` - Backend initialization script
- ✅ `frontend/Dockerfile` - Node.js + Nginx container
- ✅ `frontend/start.sh` - Frontend build & serve
- ✅ `railway.json` - Service configuration

---

## Step 1: Create Railway Account

1. Go to https://railway.app
2. Click **"Sign Up"**
3. Choose **"GitHub"** to sign up with your GitHub account
4. Authorize Railway to access your GitHub account
5. Create a new project

## Step 3: Services Will Build Automatically

Railway will:
1. ✅ Detect `Dockerfile` in `backend/` folder
2. ✅ Detect `Dockerfile` in `frontend/` folder
3. ✅ Build Docker images for both services
4. ✅ Deploy to Railway infrastructure

You'll see build progress in the Railway dashboard. Wait for both services to show **green** checkmarks.

---

## Step 4: Add Database Services

### Add PostgreSQL

1. In Railway Dashboard, click **"+ New"**
2. Select **"Add from marketplace"** → **"PostgreSQL"**
3. Select your project
4. Wait for PostgreSQL to initialize (green status)
5. Copy the auto-generated connection variables

### Add Redis

1. Click **"+ New"** → **"Add from marketplace"** → **"Redis"**
2. Select your project
3. Wait for Redis to initialize (green status)

---

## Step 5: Configure Environment Variables

### For Backend Service:

1. Click on **Backend** service in Railway dashboard
2. Go to **"Variables"** tab
3. Add the following variables (Railway auto-fills database credentials from linked services):

```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_DB=sevaihub
REDIS_URL=redis://redis:6379
SECRET_KEY=<generate-secure-32-char-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=production
```

### For Frontend Service:

1. Click on **Frontend** service
2. Go to **"Variables"** tab
3. Add:

```
VITE_API_URL=https://your-backend-railway-url
```

Get the backend URL from: Backend service → Settings → Domain

---

---

## Step 6: Initialize Database

After PostgreSQL and Backend are running:

1. Go to **PostgreSQL** service → **"Connect"** → **"Query"**
2. Run this command to enable PostGIS:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

3. The backend will auto-run migrations and seed data on startup

---

## Step 7: Test Your Deployment

✅ **Test Backend API:**
- Visit: `https://your-backend-url/docs` (Swagger UI)
- You should see all API endpoints

✅ **Test Frontend:**
- Visit: `https://your-frontend-url`
- Go to `/search` page
- Verify technicians appear on the map

✅ **Test Technician Search:**
```bash
curl -X GET "https://your-backend-url/technicians/nearby?latitude=13.0827&longitude=80.2707&service_category=Plumber&radius_km=3"
```

---

## Troubleshooting Railway Deployment

### Error: "Script start.sh not found"

**Solution:** We've added `backend/start.sh` and `frontend/start.sh` scripts. Make sure files are committed:

```bash
git add backend/start.sh frontend/start.sh
git commit -m "Add start scripts for Railway"
git push origin main
```

Then **re-trigger deployment** in Railway.

### Error: "Railpack could not determine how to build the app"

**Solution:** This happens when Railway auto-detects instead of using Dockerfile. Fix:

1. delete the old deployment
2. Create a new deployment from GitHub
3. Make sure to select the **root directory correctly** at deploy time
4. Or remove any railway.json/railpack config and let Dockerfile take over

### Services Not Connecting

**Problem:** Backend can't connect to PostgreSQL

**Solution:**
1. PostgreSQL must be in the **same Railway project**
2. Use service name `postgres` not `localhost`
3. Set `POSTGRES_HOST=postgres` in Backend variables
4. Wait 30 seconds for databases to be ready before backend connects

### Frontend Not Finding Backend API

**Problem:** Frontend shows "Demo Mode" or "No technicians"

**Solution:**
1. Check `VITE_API_URL` environment variable
2. Must be the full HTTPS URL (e.g., `https://sevaihub-backend-prod.railway.app`)
3. Rebuild frontend after changing variable: Trigger new deployment
4. Check browser DevTools → Network tab for API calls

### Build Logs Show Errors

**Solution:** Check build logs in Railway:

1. Click on service → **"Deployments"** → Latest deployment
2. Click **"View logs"** button
3. Look for error messages
4. Common issues:
   - Missing `requirements.txt` or `package.json`
   - Wrong file paths in Dockerfile
   - Port already in use

---

## Quick Start: Deploy in 3 Steps

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

### Step 2: Create Project on Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"+ New Project"**
4. Select **"Deploy from GitHub"** → Select **sevaihub**
5. Click **"Deploy"**

Railway will automatically:
- ✅ Build backend using `backend/Dockerfile`
- ✅ Build frontend using `frontend/Dockerfile`
- ✅ Deploy both services

### Step 3: Add Databases

1. In Railway dashboard, click **"+ New"**
2. Add **PostgreSQL** from marketplace
3. Add **Redis** from marketplace
4. Wait for green status ✅

That's it! Your project is live on Railway! 🎉

---
```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=sevaihub
```

### Redis
```
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=optional
```

### Backend
```
SECRET_KEY=your-random-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=production
```

### Frontend
```
VITE_API_URL=https://your-railway-backend-url
```

---

## Troubleshooting

### Services Not Starting
- Check **Logs** for each service
- Verify **environment variables** are set correctly
- Ensure **ports** are not conflicting

### Connection Refused Errors
- Database takes time to initialize (5-10 minutes)
- Wait for PostgreSQL and Redis to show green status
- Restart backend service after database is ready

### PostGIS Not Found
- Make sure to create the extension: `CREATE EXTENSION postgis;`
- Remix Railway's PostgreSQL template includes PostGIS

### Frontend Not Loading
- Check `VITE_API_URL` matches your backend URL
- Rebuild frontend: Clear cache and redeploy
- Check browser console for CORS errors

---

## Custom Domain Setup (Optional)

1. Go to **Frontend service** → **Settings**
2. Click **"Custom Domain"**
3. Enter your domain (e.g., `sevaihub.yourdomain.com`)
4. Update **DNS records** at your domain provider with Railway's nameservers
5. Wait 24-48 hours for propagation

---

## Useful Railway Commands

```bash
# View project info
railway status

# View logs
railway logs --service backend

# Open Railway dashboard
railway open

# List all services
railway service list

# Set environment variable
railway variable set KEY=VALUE
```

---

## Next Steps After Deployment

1. ✅ Verify all services are running
2. ✅ Test technician search on the map
3. ✅ Seed production database with technicians
4. ✅ Set up monitoring/alerts
5. ✅ Configure custom domain
6. ✅ Set up CI/CD for auto-deployments

