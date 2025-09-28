# 🚀 Production Deployment Guide

## **Deployment Options Overview**

| Platform | Best For | Cost | Difficulty | Features |
|----------|----------|------|------------|----------|
| **Vercel** | FastAPI apps | Free tier | Easy | Auto-scaling, CDN |
| **Railway** | Full-stack apps | $5/month | Easy | Database, Redis |
| **Docker** | Local/Cloud | Variable | Medium | Full control |
| **Heroku** | Simple apps | $7/month | Easy | Git-based |

## **Option 1: Vercel Deployment (Recommended)**

### **Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

### **Step 2: Login to Vercel**
```bash
vercel login
```

### **Step 3: Deploy Session 04 (Production RAG)**
```bash
cd 04_Production_RAG
vercel --prod
```

### **Step 4: Set Environment Variables**
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings > Environment Variables
4. Add:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LANGSMITH_API_KEY`: Your LangSmith API key (optional)

### **Step 5: Test Your Deployment**
```bash
# Get your deployment URL from Vercel
curl https://your-app.vercel.app/api/health
```

## **Option 2: Railway Deployment**

### **Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

### **Step 2: Login to Railway**
```bash
railway login
```

### **Step 3: Deploy Session 04**
```bash
cd 04_Production_RAG
railway init
railway up
```

### **Step 4: Set Environment Variables**
```bash
railway variables set OPENAI_API_KEY=your_key_here
railway variables set LANGSMITH_API_KEY=your_key_here
```

## **Option 3: Docker Deployment (Local/Cloud)**

### **Step 1: Build and Run Locally**
```bash
# Start all services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### **Step 2: Test Your Services**
```bash
# Session 03 (Flask)
curl http://localhost:5000/api/health

# Session 04 (FastAPI)
curl http://localhost:8000/api/health

# Ollama
curl http://localhost:11434/api/tags

# ChromaDB
curl http://localhost:8001/api/v1/heartbeat
```

### **Step 3: Deploy to Cloud (AWS, GCP, Azure)**
1. **AWS ECS**: Use the Docker images
2. **Google Cloud Run**: Deploy containers
3. **Azure Container Instances**: Run containers

## **Option 4: Heroku Deployment**

### **Step 1: Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### **Step 2: Create Heroku App**
```bash
cd 04_Production_RAG
heroku create your-rag-app-name
```

### **Step 3: Set Environment Variables**
```bash
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set LANGSMITH_API_KEY=your_key_here
```

### **Step 4: Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## **Testing Your Deployment**

### **Health Checks**
```bash
# Session 03
curl https://your-session03-url.vercel.app/api/health

# Session 04
curl https://your-session04-url.vercel.app/api/health
```

### **Upload Test**
```bash
# Session 03
curl -X POST https://your-session03-url.vercel.app/api/upload \
  -F "file=@test.txt"

# Session 04
curl -X POST https://your-session04-url.vercel.app/api/documents/upload \
  -F "file=@test.txt"
```

### **Chat Test**
```bash
# Session 03
curl -X POST https://your-session03-url.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Hello, how are you?"}'

# Session 04
curl -X POST https://your-session04-url.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'
```

## **Monitoring and Maintenance**

### **Logs**
```bash
# Vercel
vercel logs

# Railway
railway logs

# Docker
docker-compose logs -f session04-rag
```

### **Scaling**
- **Vercel**: Automatic scaling
- **Railway**: Manual scaling in dashboard
- **Docker**: Use `docker-compose scale session04-rag=3`

### **Updates**
```bash
# Vercel
vercel --prod

# Railway
railway up

# Docker
docker-compose up -d --build
```

## **Troubleshooting**

### **Common Issues:**
1. **"Module not found"** - Check your `requirements.txt`
2. **"Port already in use"** - Change port numbers
3. **"Environment variable not set"** - Check your `.env` files
4. **"Build failed"** - Check your Dockerfile syntax

### **Success Indicators:**
- ✅ Health checks return 200
- ✅ Upload endpoints work
- ✅ Chat endpoints return responses
- ✅ No error messages in logs

## **Next Steps After Deployment:**
1. **Test all endpoints** thoroughly
2. **Document your APIs** with Swagger/OpenAPI
3. **Set up monitoring** (Uptime Robot, etc.)
4. **Submit your homework** with working demo links
5. **Showcase your work** to potential employers

**Happy deploying! 🚀**


