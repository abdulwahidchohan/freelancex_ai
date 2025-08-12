# FreelanceX.AI Deployment Guide 🚀

> **Complete Deployment Guide for Enhanced AI-Powered Freelance Assistant**

## 🎯 Overview

This guide provides comprehensive instructions for deploying FreelanceX.AI in various environments, from local development to production cloud deployments.

## 📋 Prerequisites

### System Requirements
- **CPU**: 2+ cores (4+ recommended for production)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 10GB+ available space
- **Network**: Stable internet connection for API calls
- **OS**: Linux, macOS, or Windows

### Software Requirements
- **Python**: 3.8 or higher
- **Git**: Latest version
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-service deployment)

## 🏠 Local Development Deployment

### Step 1: Environment Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/freelancex_ai.git
cd freelancex_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-anthropic-key

# Security
FREELANCEX_SESSION_SECRET=your-super-secret-key-here

# Database
FREELANCEX_DATABASE_URL=sqlite:///freelancex.db

# Server Configuration
FREELANCEX_HOST=0.0.0.0
FREELANCEX_PORT=8000
```

### Step 3: Database Initialization
```bash
# Initialize database (automatic on first run)
python -c "from memory.sqlite_memory import get_memory; get_memory()"
```

### Step 4: Start the Application
```bash
# Option 1: Start Chainlit frontend
chainlit run chainlit_app/main.py

# Option 2: Start FastAPI backend
python api_gateway.py

# Option 3: Start both (in separate terminals)
# Terminal 1: Backend
python api_gateway.py

# Terminal 2: Frontend
chainlit run chainlit_app/main.py
```

### Step 5: Verify Deployment
```bash
# Test the application
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "version": "2.0.0"
}
```

## 🐳 Docker Deployment

### Single Container Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 freelancex && chown -R freelancex:freelancex /app
USER freelancex

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "api_gateway.py"]
```

#### Build and Run
```bash
# Build the image
docker build -t freelancex-ai .

# Run the container
docker run -d \
  --name freelancex-ai \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e FREELANCEX_SESSION_SECRET=your-secret \
  -v $(pwd)/data:/app/data \
  freelancex-ai
```

### Multi-Service Deployment with Docker Compose

#### docker-compose.yml
```yaml
version: '3.8'

services:
  freelancex-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - FREELANCEX_SESSION_SECRET=${FREELANCEX_SESSION_SECRET}
      - FREELANCEX_DATABASE_URL=sqlite:///data/freelancex.db
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  freelancex-frontend:
    build: .
    ports:
      - "8001:8000"
    command: ["chainlit", "run", "chainlit_app/main.py"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FREELANCEX_BACKEND_URL=http://freelancex-backend:8000
    depends_on:
      - freelancex-backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - freelancex-backend
      - freelancex-frontend
    restart: unless-stopped

volumes:
  redis_data:
```

#### Deploy with Docker Compose
```bash
# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Deployment
```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git nginx

# Clone repository
git clone https://github.com/yourusername/freelancex_ai.git
cd freelancex_ai

# Setup application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Setup systemd service
sudo nano /etc/systemd/system/freelancex.service
```

**Systemd Service Configuration:**
```ini
[Unit]
Description=FreelanceX.AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/freelancex_ai
Environment=PATH=/home/ubuntu/freelancex_ai/venv/bin
ExecStart=/home/ubuntu/freelancex_ai/venv/bin/python api_gateway.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable freelancex
sudo systemctl start freelancex

# Setup Nginx
sudo nano /etc/nginx/sites-available/freelancex
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/freelancex /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### AWS ECS Deployment
```yaml
# task-definition.json
{
  "family": "freelancex-ai",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "freelancex-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/freelancex-ai:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your-openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/freelancex-ai",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform Deployment

#### Cloud Run Deployment
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/your-project/freelancex-ai

# Deploy to Cloud Run
gcloud run deploy freelancex-ai \
  --image gcr.io/your-project/freelancex-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key
```

### Azure Deployment

#### Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry yourregistry --image freelancex-ai .

# Deploy to Container Instances
az container create \
  --resource-group your-rg \
  --name freelancex-ai \
  --image yourregistry.azurecr.io/freelancex-ai:latest \
  --dns-name-label freelancex-ai \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your-key
```

## 🔒 Production Security Configuration

### SSL/TLS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration
```bash
# UFW firewall setup
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Environment Security
```bash
# Secure environment variables
export OPENAI_API_KEY="your-key"
export FREELANCEX_SESSION_SECRET="your-secret"

# Use secrets management
# AWS: AWS Secrets Manager
# GCP: Secret Manager
# Azure: Key Vault
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

# Custom metrics
requests_total = Counter('freelancex_requests_total', 'Total requests')
request_duration = Histogram('freelancex_request_duration_seconds', 'Request duration')

# Add to your FastAPI app
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration
```python
# logging.conf
[loggers]
keys=root,freelancex

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=normalFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_freelancex]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=freelancex
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=normalFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=normalFormatter
args=('logs/freelancex.log', 'a', 10485760, 5)

[formatter_normalFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: |
          python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t freelancex-ai .
          docker tag freelancex-ai your-registry/freelancex-ai:${{ github.sha }}
          docker push your-registry/freelancex-ai:${{ github.sha }}
      - name: Deploy to production
        run: |
          # Deploy to your cloud platform
          kubectl set image deployment/freelancex-ai freelancex-ai=your-registry/freelancex-ai:${{ github.sha }}
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- SQLite optimizations
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;
```

### Caching Strategy
```python
# Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached_result = redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Load Balancing
```nginx
# Nginx load balancer configuration
upstream freelancex_backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://freelancex_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. API Key Issues
```bash
# Check API key configuration
echo $OPENAI_API_KEY

# Test API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### 2. Database Issues
```bash
# Check database connection
python -c "from memory.sqlite_memory import get_memory; print('DB OK')"

# Reset database (if needed)
rm freelancex.db
python -c "from memory.sqlite_memory import get_memory; get_memory()"
```

#### 3. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 $(lsof -t -i:8000)
```

#### 4. Memory Issues
```bash
# Monitor memory usage
htop

# Check Python memory
python -c "import psutil; print(psutil.virtual_memory())"
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/api/agent-status

# API provider status
curl http://localhost:8000/api/providers
```

## 📚 Additional Resources

### Documentation
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chainlit Documentation](https://docs.chainlit.io/)

### Monitoring Tools
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Logging
- **Sentry** - Error tracking

### Security Tools
- **OWASP ZAP** - Security testing
- **Bandit** - Python security linting
- **Safety** - Dependency vulnerability scanning

---

**Deployment Guide**  
*FreelanceX.AI - Enhanced AI-Powered Freelance Assistant*  
*Version: 2.0.0 | Last Updated: 2024-01-01*
