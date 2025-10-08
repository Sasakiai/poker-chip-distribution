# Deployment Guide

This guide covers deploying the Poker Chip Distribution application to various platforms.

## 🚀 Quick Deploy

### Railway (Recommended)

Railway is the recommended platform for deploying this FastAPI application.

#### Why Railway?
- ✅ Built-in Docker support
- ✅ Automatic HTTPS
- ✅ Simple environment variable management
- ✅ Free tier available
- ✅ Excellent for Python/FastAPI apps

#### Deploy Steps:

1. **Install Railway CLI (optional)**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize and Deploy**
   ```bash
   railway init
   railway up
   ```

4. **Set Environment Variables (if needed)**
   ```bash
   railway variables set API_HOST=0.0.0.0
   railway variables set API_PORT=8000
   ```

5. **Generate Domain**
   - Go to your Railway dashboard
   - Click on your service
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"

#### Alternative: Deploy via GitHub

1. Push your code to GitHub
2. Go to [Railway Dashboard](https://railway.app/dashboard)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the Dockerfile and deploy

---

## 🔧 Other Deployment Options

### Render

Render is another great option for FastAPI apps.

1. Create a `render.yaml`:
   ```yaml
   services:
     - type: web
       name: poker-chip-distribution
       env: docker
       plan: free
       dockerfilePath: ./Dockerfile
       envVars:
         - key: PORT
           value: 8000
   ```

2. Push to GitHub and connect via Render dashboard

### Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and Launch**
   ```bash
   fly auth login
   fly launch
   ```

3. **Deploy**
   ```bash
   fly deploy
   ```

### Heroku

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   ```

2. **Create app**
   ```bash
   heroku create your-poker-chip-app
   ```

3. **Set stack to container**
   ```bash
   heroku stack:set container
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Vercel (Not Recommended for this project)

⚠️ **Note**: Vercel is optimized for serverless functions and static sites. While it can run FastAPI, Railway or Render are better choices for this application because:
- Better support for long-running processes
- Simpler Docker deployment
- Better suited for stateful applications
- More predictable performance

If you still want to use Vercel, you'd need to convert to serverless functions, which is not ideal for this use case.

---

## 🐳 Manual Docker Deployment

### Build and Run Locally

```bash
# Build the image
docker build -t poker-chip-distribution .

# Run the container
docker run -p 8000:8000 poker-chip-distribution
```

### Deploy to Your Own Server

1. **Build and tag the image**
   ```bash
   docker build -t your-registry/poker-chip-distribution:latest .
   ```

2. **Push to container registry**
   ```bash
   docker push your-registry/poker-chip-distribution:latest
   ```

3. **On your server, pull and run**
   ```bash
   docker pull your-registry/poker-chip-distribution:latest
   docker run -d -p 8000:8000 --name poker-chips your-registry/poker-chip-distribution:latest
   ```

### Docker Compose (for development)

```bash
docker-compose up -d
```

---

## 🔐 Environment Variables

The application uses these environment variables (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Host to bind the server to |
| `API_PORT` | `8000` | Port to run the server on |
| `PORT` | `8000` | Alternative port variable (used by some platforms) |

Most platforms will automatically set `PORT` for you.

---

## ✅ Post-Deployment Checklist

After deploying, verify your application:

1. **Check Health Endpoint**
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **Visit the UI**
   - Open `https://your-app.railway.app` in your browser
   - You should see the Poker Chip Distribution interface

3. **Test API Documentation**
   - Visit `https://your-app.railway.app/docs`
   - Test the endpoints using the Swagger UI

4. **Test a Distribution**
   - Use the web interface to calculate a distribution
   - Verify results are displayed correctly

---

## 🔧 Troubleshooting

### Application won't start

**Check logs:**
```bash
# Railway
railway logs

# Docker
docker logs poker-chips
```

**Common issues:**
- Port binding: Make sure the app binds to `0.0.0.0` not `localhost`
- Missing dependencies: Verify `requirements.txt` is complete
- Static files: Ensure `static/` directory is copied in Dockerfile

### Static files not loading

1. Verify static files are in the `static/` directory
2. Check Dockerfile includes: `COPY static/ ./static/`
3. Ensure FastAPI is mounting static files (check `api.py`)

### CORS errors

If accessing from a different domain, update CORS settings in `api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring

### Railway Metrics

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Deployment history

Access via the Railway dashboard.

### Custom Health Checks

The `/health` endpoint returns application status:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

Use this for:
- Uptime monitoring (UptimeRobot, Pingdom, etc.)
- Load balancer health checks
- CI/CD pipeline verification

---

## 🔄 Updates and Maintenance

### Deploy Updates

**Railway (GitHub integration):**
- Push to your main branch
- Railway auto-deploys

**Railway (CLI):**
```bash
railway up
```

**Docker:**
```bash
docker build -t poker-chip-distribution .
docker stop poker-chips
docker rm poker-chips
docker run -d -p 8000:8000 --name poker-chips poker-chip-distribution
```

### Database Considerations

Currently, the app uses in-memory state for chip inventory. For production:

1. **Add Persistent Storage** (if needed for custom inventory)
   - Use Railway's PostgreSQL plugin
   - Or connect to external database
   - Modify `main.py` to load/save inventory

2. **Or Keep Stateless** (recommended for simplicity)
   - Current design works well for most use cases
   - Inventory resets on restart (use default values)
   - Consider environment variables for default inventory

---

## 💰 Cost Estimates

### Railway
- **Free Tier**: $0/month (500 hours, perfect for hobby projects)
- **Developer Plan**: $5/month (hobby projects with more usage)
- **Team Plan**: $20/month (production apps)

### Render
- **Free Tier**: $0/month (with automatic sleep after inactivity)
- **Starter**: $7/month (no sleep)

### Fly.io
- **Free Tier**: Generous free tier for small apps
- **Paid**: Scales based on usage

### Recommended for this project
**Railway Free Tier** - Perfect for personal use, small groups, and testing. Upgrade only if you exceed usage limits.

---

## 🎯 Best Practices

1. **Use Environment Variables** for configuration
2. **Enable HTTPS** (automatic on Railway/Render)
3. **Monitor Logs** regularly
4. **Set up Health Checks** for reliability
5. **Version Control** - always deploy from Git
6. **Test Locally** with Docker before deploying
7. **Document Changes** in your README
8. **Backup Configuration** - save environment variables

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)

---

## 🆘 Support

If you encounter issues:

1. Check the logs first
2. Verify environment variables
3. Test locally with Docker
4. Review this deployment guide
5. Check platform-specific documentation

---

**Happy Deploying! 🎰♠♥♣♦**