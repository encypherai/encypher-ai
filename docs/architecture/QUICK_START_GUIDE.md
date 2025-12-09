# 🚀 Microservices Quick Start Guide

**Get up and running with Encypher microservices in 5 minutes!**

---

## ⚡ **Quick Start (Docker Compose)**

### **1. Start All Services**

```bash
cd services
docker-compose -f docker-compose.dev.yml up
```

**That's it!** Services will be available at:
- **Auth Service:** http://localhost:8001
- **Key Service:** http://localhost:8003
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

---

## 🧪 **Test the Services**

### **1. Check Health**

```bash
# Auth Service
curl http://localhost:8001/health

# Key Service
curl http://localhost:8003/health
```

### **2. Create a User**

```bash
curl -X POST http://localhost:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### **3. Login**

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Save the `access_token` from the response!**

### **4. Generate API Key**

```bash
curl -X POST http://localhost:8003/api/v1/keys/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Key",
    "permissions": ["sign", "verify", "read"]
  }'
```

**Save the `key` from the response - it's only shown once!**

### **5. Verify API Key**

```bash
curl -X POST http://localhost:8003/api/v1/keys/verify \
  -H "Content-Type: application/json" \
  -d '{
    "key": "ency_YOUR_KEY_HERE"
  }'
```

---

## 🛠️ **Development Setup**

### **Prerequisites**

- Python 3.11+
- UV package manager
- Docker & Docker Compose
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)

### **Install UV**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### **Run Individual Services**

#### **Auth Service**

```bash
cd services/auth-service

# Create environment file
cp .env.example .env.local
# Edit .env.local with your settings

# Install dependencies
uv sync

# Run service
uv run python -m app.main
```

#### **Key Service**

```bash
cd services/key-service

# Create environment file
cp .env.example .env.local
# Edit .env.local with your settings

# Install dependencies
uv sync

# Run service
uv run python -m app.main
```

---

## 📖 **API Documentation**

### **Interactive Docs**

Once services are running, visit:
- **Auth Service:** http://localhost:8001/docs
- **Key Service:** http://localhost:8003/docs

### **Endpoints**

#### **Auth Service (8001)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create account |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/auth/logout` | Logout |
| POST | `/api/v1/auth/verify` | Verify token |
| GET | `/health` | Health check |

#### **Key Service (8003)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/keys/generate` | Generate key |
| GET | `/api/v1/keys` | List keys |
| GET | `/api/v1/keys/{key_id}` | Get key |
| PUT | `/api/v1/keys/{key_id}` | Update key |
| DELETE | `/api/v1/keys/{key_id}` | Revoke key |
| POST | `/api/v1/keys/{key_id}/rotate` | Rotate key |
| POST | `/api/v1/keys/verify` | Verify key |
| GET | `/api/v1/keys/{key_id}/usage` | Usage stats |

---

## 🔧 **Configuration**

### **Environment Variables**

#### **Auth Service**

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/encypher
JWT_SECRET_KEY=your-secret-key

# Optional
SERVICE_PORT=8001
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379/0
```

#### **Key Service**

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/encypher
AUTH_SERVICE_URL=http://localhost:8001

# Optional
SERVICE_PORT=8003
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379/1
KEY_PREFIX=ency_
```

---

## 🐛 **Troubleshooting**

### **Services won't start**

```bash
# Check if ports are in use
netstat -an | grep 8001
netstat -an | grep 8003

# Check Docker logs
docker-compose -f docker-compose.dev.yml logs auth-service
docker-compose -f docker-compose.dev.yml logs key-service
```

### **Database connection errors**

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Check connection
psql -h localhost -U encypher -d encypher
```

### **Authentication errors**

```bash
# Verify token is valid
curl -X POST http://localhost:8001/api/v1/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 **Next Steps**

1. **Read the Documentation**
   - [Migration Plan](./MICROSERVICES_MIGRATION_PLAN.md)
   - [Architecture Overview](./MICROSERVICES_ARCHITECTURE.md)
   - [Progress Tracker](./MICROSERVICES_PROGRESS.md)

2. **Explore the Services**
   - [Auth Service README](../../services/auth-service/README.md)
   - [Key Service README](../../services/key-service/README.md)

3. **Start Developing**
   - Write tests
   - Add features
   - Deploy to staging

---

## 🆘 **Getting Help**

- **Documentation:** `docs/architecture/`
- **Service READMEs:** `services/*/README.md`
- **Issues:** Create a GitHub issue
- **Team:** Slack #encypher-dev

---

<div align="center">

**Happy Coding!** 🚀

[Architecture](./MICROSERVICES_ARCHITECTURE.md) • [Progress](./MICROSERVICES_PROGRESS.md) • [Migration Plan](./MICROSERVICES_MIGRATION_PLAN.md)

</div>
