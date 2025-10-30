# 🏗️ Microservices Architecture

**Version:** 1.0  
**Last Updated:** October 30, 2025  
**Status:** 32% Complete (2/8 services)

---

## 🎯 **Architecture Overview**

EncypherAI is transitioning from a monolithic FastAPI application to a microservices architecture for improved scalability, maintainability, and fault isolation.

---

## 📊 **System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Applications                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Dashboard  │  │  Mobile App  │  │  Third-Party │              │
│  │   (Next.js)  │  │              │  │     APIs     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (8000)                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  • Request Routing    • Rate Limiting    • Load Balancing     │ │
│  │  • Authentication     • API Versioning   • Request Logging    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                             ↓
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Auth Service   │  │   Key Service   │  │ Encoding Service│
│    (8001) ✅    │  │    (8003) ✅    │  │    (8004) ⏳    │
│                 │  │                 │  │                 │
│ • JWT Auth      │  │ • Key Gen       │  │ • Sign Docs     │
│ • OAuth         │  │ • Rotation      │  │ • Embed Meta    │
│ • Sessions      │  │ • Permissions   │  │ • Crypto Ops    │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Additional Microservices                          │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │Verification  │  │  Analytics   │  │   Billing    │             │
│  │Service (8005)│  │Service (8006)│  │Service (8007)│             │
│  │     ⏳       │  │     ⏳       │  │     ⏳       │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │Notification  │  │    User      │                                │
│  │Service (8008)│  │Service (8002)│                                │
│  │     ⏳       │  │     ⏳       │                                │
│  └──────────────┘  └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        Data & Cache Layer                            │
│  ┌──────────────────┐              ┌──────────────────┐            │
│  │   PostgreSQL     │              │      Redis       │            │
│  │   (Port 5432)    │              │   (Port 6379)    │            │
│  │                  │              │                  │            │
│  │ • User Data      │              │ • Sessions       │            │
│  │ • API Keys       │              │ • Cache          │            │
│  │ • Usage Logs     │              │ • Rate Limits    │            │
│  └──────────────────┘              └──────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Service Details**

### **1. Auth Service** ✅ Port 8001

**Status:** Production Ready  
**Dependencies:** PostgreSQL, Redis

**Responsibilities:**
- User authentication (login/signup)
- JWT token generation and validation
- OAuth integration (Google, GitHub)
- Session management
- Token refresh and revocation
- Password reset

**Endpoints:**
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/verify` - Token verification
- `GET /health` - Health check

**Database Models:**
- User
- RefreshToken
- PasswordResetToken

---

### **2. Key Service** ✅ Port 8003

**Status:** Production Ready  
**Dependencies:** PostgreSQL, Redis, Auth Service

**Responsibilities:**
- API key generation
- Key rotation and revocation
- Permission management
- Usage tracking
- Key verification (public endpoint)

**Endpoints:**
- `POST /api/v1/keys/generate` - Generate new key
- `GET /api/v1/keys` - List keys
- `GET /api/v1/keys/{key_id}` - Get key details
- `PUT /api/v1/keys/{key_id}` - Update key
- `DELETE /api/v1/keys/{key_id}` - Revoke key
- `POST /api/v1/keys/{key_id}/rotate` - Rotate key
- `POST /api/v1/keys/verify` - Verify key
- `GET /api/v1/keys/{key_id}/usage` - Usage stats

**Database Models:**
- ApiKey
- KeyUsage
- KeyRotation

---

### **3. Encoding Service** ⏳ Port 8004

**Status:** Planned  
**Dependencies:** PostgreSQL, Key Service

**Responsibilities:**
- Document signing
- Metadata embedding
- Cryptographic operations
- C2PA manifest generation
- Signature generation

**Planned Endpoints:**
- `POST /api/v1/encode/sign` - Sign document
- `POST /api/v1/encode/embed` - Embed metadata
- `GET /api/v1/encode/manifest/{doc_id}` - Get manifest
- `GET /health` - Health check

---

### **4. Verification Service** ⏳ Port 8005

**Status:** Planned  
**Dependencies:** PostgreSQL, Key Service

**Responsibilities:**
- Signature verification
- Document validation
- Authenticity checks
- Tamper detection
- Verification logs

**Planned Endpoints:**
- `POST /api/v1/verify/signature` - Verify signature
- `POST /api/v1/verify/document` - Verify document
- `GET /api/v1/verify/history/{doc_id}` - Verification history
- `GET /health` - Health check

---

### **5. Analytics Service** ⏳ Port 8006

**Status:** Planned  
**Dependencies:** PostgreSQL, Redis

**Responsibilities:**
- Usage statistics
- Performance metrics
- Activity tracking
- Report generation
- Real-time analytics

**Planned Endpoints:**
- `GET /api/v1/analytics/usage` - Usage stats
- `GET /api/v1/analytics/performance` - Performance metrics
- `GET /api/v1/analytics/activity` - Activity logs
- `POST /api/v1/analytics/report` - Generate report
- `GET /health` - Health check

---

### **6. Billing Service** ⏳ Port 8007

**Status:** Planned  
**Dependencies:** PostgreSQL, Analytics Service

**Responsibilities:**
- Subscription management
- Payment processing
- Invoice generation
- Usage-based billing
- Plan upgrades/downgrades

**Planned Endpoints:**
- `GET /api/v1/billing/subscription` - Get subscription
- `PUT /api/v1/billing/subscription` - Update subscription
- `GET /api/v1/billing/invoices` - List invoices
- `POST /api/v1/billing/payment` - Process payment
- `GET /health` - Health check

---

### **7. Notification Service** ⏳ Port 8008

**Status:** Planned  
**Dependencies:** Redis, Message Queue

**Responsibilities:**
- Email notifications
- SMS notifications
- Usage alerts
- Security alerts
- Webhook delivery

**Planned Endpoints:**
- `POST /api/v1/notify/email` - Send email
- `POST /api/v1/notify/sms` - Send SMS
- `POST /api/v1/notify/webhook` - Trigger webhook
- `GET /api/v1/notify/templates` - List templates
- `GET /health` - Health check

---

### **8. User Service** ⏳ Port 8002

**Status:** Planned  
**Dependencies:** PostgreSQL, Auth Service

**Responsibilities:**
- User profile management
- Team management
- Organization management
- User preferences
- Account settings

**Planned Endpoints:**
- `GET /api/v1/users/profile` - Get profile
- `PUT /api/v1/users/profile` - Update profile
- `GET /api/v1/users/team` - Get team
- `POST /api/v1/users/team/invite` - Invite member
- `GET /health` - Health check

---

### **9. API Gateway** ⏳ Port 8000

**Status:** Planned  
**Dependencies:** All services

**Responsibilities:**
- Request routing
- Rate limiting
- Load balancing
- API versioning
- Request/response logging
- Authentication middleware

---

## 🔄 **Communication Patterns**

### **Synchronous (HTTP/REST)**
```
Client → API Gateway → Service → Response
```
Used for:
- User-facing requests
- Real-time operations
- Service-to-service verification

### **Asynchronous (Message Queue)**
```
Service → Queue → Consumer Service
```
Used for:
- Background processing
- Email notifications
- Analytics tracking
- Audit logging

### **Event-Driven**
```
Service → Event Bus → Subscribed Services
```
Used for:
- User actions (signup, login)
- Key operations (generate, revoke)
- Document operations (sign, verify)

---

## 🔐 **Security Architecture**

### **Authentication Flow**
```
1. User → Dashboard
   POST /login {email, password}

2. Dashboard → Auth Service
   POST /api/v1/auth/login

3. Auth Service → Response
   {access_token, refresh_token}

4. Dashboard → Other Services
   Authorization: Bearer <access_token>

5. Service → Auth Service
   POST /api/v1/auth/verify
   Validates token

6. Service → Response
   Returns data
```

### **API Key Flow**
```
1. Client → Key Service (with JWT)
   POST /api/v1/keys/generate

2. Key Service → Response
   {key: "ency_..."}  (shown once!)

3. Client → Any Service
   X-API-Key: ency_...

4. Service → Key Service
   POST /api/v1/keys/verify

5. Key Service → Response
   {valid: true, user_id, permissions}

6. Service → Response
   Returns data
```

---

## 🗄️ **Database Strategy**

### **Current: Shared Database**
```
┌─────────────────────────────────┐
│        PostgreSQL               │
│                                 │
│  ┌──────────┐  ┌──────────┐   │
│  │  users   │  │ api_keys │   │
│  └──────────┘  └──────────┘   │
│                                 │
│  ┌──────────┐  ┌──────────┐   │
│  │ tokens   │  │  usage   │   │
│  └──────────┘  └──────────┘   │
└─────────────────────────────────┘
         ↑
         │
    All Services
```

**Pros:**
- Simpler to start
- No data duplication
- Easier transactions
- Lower infrastructure cost

**Cons:**
- Tight coupling
- Scaling limitations
- Schema conflicts

### **Future: Database per Service**
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Auth    │  │   Key    │  │ Encoding │
│   DB     │  │   DB     │  │    DB    │
└──────────┘  └──────────┘  └──────────┘
     ↑             ↑              ↑
     │             │              │
Auth Service  Key Service  Encoding Service
```

**Pros:**
- True service independence
- Optimized schemas
- Better scaling
- Fault isolation

**Cons:**
- Data duplication
- Complex transactions
- More infrastructure

---

## 📡 **Service Discovery**

### **Current: Static Configuration**
```yaml
services:
  auth-service:
    url: http://localhost:8001
  key-service:
    url: http://localhost:8003
```

### **Future: Dynamic Discovery (Consul)**
```
Service → Consul → Service Registry
                 ↓
            Health Checks
                 ↓
          Load Balancing
```

---

## 📊 **Monitoring & Observability**

### **Metrics (Prometheus)**
```
Service → Prometheus → Grafana Dashboard
```
Tracked metrics:
- Request rate
- Response time
- Error rate
- CPU/Memory usage
- Database connections

### **Logging (ELK Stack)**
```
Service → Logstash → Elasticsearch → Kibana
```
Log levels:
- DEBUG: Development
- INFO: Production
- WARNING: Issues
- ERROR: Failures
- CRITICAL: System down

### **Tracing (Jaeger)**
```
Request → Service A → Service B → Service C
            ↓           ↓           ↓
         Trace ID    Trace ID    Trace ID
                      ↓
                   Jaeger
```

---

## 🚀 **Deployment Architecture**

### **Development**
```
Docker Compose
├── PostgreSQL
├── Redis
├── Auth Service
├── Key Service
└── Other Services
```

### **Staging**
```
Kubernetes Cluster
├── Namespace: staging
├── 1 replica per service
├── Shared database
└── Redis cluster
```

### **Production**
```
Kubernetes Cluster
├── Namespace: production
├── 3+ replicas per service
├── Auto-scaling enabled
├── Database cluster
├── Redis cluster
└── CDN for static assets
```

---

## 📈 **Scaling Strategy**

### **Horizontal Scaling**
```
Load Balancer
    ↓
┌───┴───┬───────┬───────┐
│       │       │       │
Service Service Service Service
  #1      #2      #3      #4
```

### **Vertical Scaling**
```
Service
├── CPU: 2 cores → 4 cores
└── RAM: 2GB → 4GB
```

### **Database Scaling**
```
Primary DB
    ↓
┌───┴───┬───────┐
│       │       │
Read    Read    Read
Replica Replica Replica
```

---

## 🔄 **Migration Progress**

| Week | Services | Progress |
|------|----------|----------|
| 1 ✅ | Auth, Key | 32% |
| 2 ⏳ | Encoding, Verification | 50% |
| 3 ⏳ | Analytics | 62% |
| 4 ⏳ | Billing, Notification | 75% |
| 5 ⏳ | User, API Gateway | 87% |
| 6 ⏳ | Testing, Deployment | 100% |

---

## 📚 **Documentation**

- **[Migration Plan](./MICROSERVICES_MIGRATION_PLAN.md)** - Complete 6-week plan
- **[Progress Tracker](./MICROSERVICES_PROGRESS.md)** - Current status
- **[Auth Service](../../services/auth-service/README.md)** - Auth documentation
- **[Key Service](../../services/key-service/README.md)** - Key documentation

---

## 🎯 **Success Criteria**

### **Performance**
- ✅ Response time < 200ms (p95)
- ✅ Uptime > 99.9%
- ✅ Error rate < 0.1%

### **Scalability**
- ✅ Handle 10x current load
- ✅ Auto-scaling works
- ✅ No single point of failure

### **Maintainability**
- ✅ Clear service boundaries
- ✅ Comprehensive documentation
- ✅ Automated testing
- ✅ Easy deployment

---

<div align="center">

**EncypherAI Microservices Architecture**  
**Version 1.0 | October 2025**

[View Progress](./MICROSERVICES_PROGRESS.md) • [Migration Plan](./MICROSERVICES_MIGRATION_PLAN.md)

</div>
