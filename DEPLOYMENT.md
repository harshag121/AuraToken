# Deployment Guide

## Free Hosting Options for OPD Token Allocation Engine

### Option 1: Railway (Recommended)

Railway offers 500 hours/month free tier and easy deployment.

**Steps:**

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Install Railway CLI** (Optional but recommended)
   ```bash
   npm i -g @railway/cli
   ```

3. **Deploy from GitHub**
   - Push your code to GitHub
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Python and deploy

4. **Set Environment Variables**
   - In Railway project settings, add:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./opd_tokens.db
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

5. **Access Your API**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - API docs: `https://your-app.railway.app/docs`

---

### Option 2: Render

Render offers free tier with 750 hours/month.

**Steps:**

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: opd-token-engine
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python -m app.main`

3. **Environment Variables**
   - Add in Render dashboard:
   ```
   DATABASE_URL=sqlite+aiosqlite:///./opd_tokens.db
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

4. **Deploy**
   - Render will automatically deploy
   - URL: `https://opd-token-engine.onrender.com`

---

### Option 3: Fly.io

Generous free tier with good performance.

**Steps:**

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Launch App**
   ```bash
   cd c:\Users\91866\Desktop\Medoc\AuraToken
   fly launch
   ```
   
   - Answer prompts:
     - App name: opd-token-engine
     - Region: Choose closest to you
     - Database: No (we use SQLite)
     - Deploy now: Yes

4. **Set Environment Variables**
   ```bash
   fly secrets set ENVIRONMENT=production
   fly secrets set API_HOST=0.0.0.0
   fly secrets set API_PORT=8000
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

---

### Option 4: PythonAnywhere

Good for learning, has free tier.

**Steps:**

1. **Create Account**
   - Go to https://www.pythonanywhere.com
   - Sign up for free account

2. **Upload Code**
   - Use Git or upload files manually
   - Open Bash console
   ```bash
   git clone <your-repo-url>
   cd AuraToken
   ```

3. **Create Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 auratoken
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Go to "Web" tab
   - Add new web app
   - Manual configuration → Python 3.10
   - Set source code path
   - Configure WSGI file

5. **WSGI Configuration**
   Edit WSGI file:
   ```python
   import sys
   path = '/home/yourusername/AuraToken'
   if path not in sys.path:
       sys.path.append(path)
   
   from app.main import app as application
   ```

---

## Post-Deployment Verification

After deployment, test your API:

```bash
# Check health
curl https://your-app-url/health

# Check API docs
# Visit: https://your-app-url/docs

# Test system status
curl https://your-app-url/api/v1/analytics/system/status
```

## Database Considerations

### For Production (Recommended)

Switch from SQLite to PostgreSQL for better performance:

1. **Get Free PostgreSQL Database**
   - Railway: Automatically provides Postgres
   - Render: Add PostgreSQL database (free tier)
   - Supabase: Free PostgreSQL database

2. **Update requirements.txt**
   Add:
   ```
   psycopg2-binary==2.9.9
   ```

3. **Update DATABASE_URL**
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
   ```

### For Development/Testing

SQLite works fine and is included by default.

---

## Monitoring & Logs

### Railway
- View logs in dashboard
- Real-time log streaming

### Render
- Logs tab in dashboard
- Automatic log retention

### Fly.io
```bash
fly logs
```

---

## Custom Domain (Optional)

All platforms support custom domains:

1. **Railway**: Settings → Domains
2. **Render**: Settings → Custom Domain
3. **Fly.io**: `fly certs add yourdomain.com`

---

## Troubleshooting

### Port Issues
Ensure your app binds to `0.0.0.0` and uses the `PORT` environment variable:

```python
# app/main.py
import os
port = int(os.environ.get("PORT", 8000))
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

### Database Connection
For SQLite, ensure the database file path is writable:
```python
DATABASE_URL=sqlite+aiosqlite:///./data/opd_tokens.db
```

### Memory Limits
Free tiers have memory limits (512MB typically):
- Optimize queries
- Add pagination
- Use database indexes

---

## Scaling Tips

1. **Add Redis** for caching (when needed)
2. **Use PostgreSQL** for production
3. **Enable gzip** compression
4. **Add rate limiting**
5. **Monitor performance** with logging

---

## Security Checklist

- [ ] Change default CORS settings
- [ ] Add API authentication
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Use prepared statements (SQLAlchemy does this)

---

## Cost Optimization

**Free Tier Limits:**
- Railway: 500 hours/month
- Render: 750 hours/month
- Fly.io: 3 shared-cpu-1x VMs

**Tips to Stay Free:**
- Use SQLite initially
- Implement efficient queries
- Add caching where possible
- Monitor usage regularly
