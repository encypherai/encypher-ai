# 🏗️ Encypher Subdomain Migration & Deployment Plan

**Date:** October 29, 2025  
**Status:** Planning Phase  
**Goal:** Migrate from monolithic deployment to enterprise-grade modular architecture

---

## 📊 Current State Analysis

### Current Deployment
```
Current Architecture:
├── encypherai.com              → Next.js frontend (marketing + dashboard)
└── backend.encypherai.com      → FastAPI monolith
```

### Current Color Scheme (Unified Brand)
```css
:root {
  --delft-blue: #1b2f50;      /* Primary dark blue */
  --blue-ncs: #2a87c4;         /* Primary action blue */
  --columbia-blue: #b7d5ed;    /* Light accent blue */
  --rosy-brown: #ba8790;       /* Accent pink/brown */
  --white: #ffffff;            /* Base white */
}
```

### Current Tech Stack
- **Frontend:** Next.js 14+ with TypeScript
- **Styling:** TailwindCSS with custom theme
- **Backend:** FastAPI (Python)
- **Font:** Roboto family
- **Components:** shadcn/ui compatible

---

## 🎯 Target Architecture

### Proposed Subdomain Structure
```
Enterprise Architecture:
├── encypherai.com                  → Marketing website (static/Next.js)
├── dashboard.encypherai.com        → User dashboard (Next.js app)
├── api.encypherai.com              → API Gateway (Nginx/Traefik)
├── docs.encypherai.com             → Documentation (MkDocs/Docusaurus)
└── verify.encypherai.com           → Public verification portal
```

### Backend Microservices (Internal)
```
Internal Services (not public subdomains):
├── encoding-service               → Content encoding/signing
├── manifest-service               → Manifest CRUD & search
├── analytics-service              → Usage metrics & quotas
└── auth-service                   → Authentication (Keycloak)
```

---

## 🔄 Migration Strategy

### Phase 1: Subdomain Setup (Week 1)

#### 1.1 DNS Configuration
```bash
# Add DNS records
dashboard.encypherai.com    → A/AAAA record
api.encypherai.com          → A/AAAA record
docs.encypherai.com         → A/AAAA record
verify.encypherai.com       → A/AAAA record
```

#### 1.2 SSL Certificates
```bash
# Let's Encrypt wildcard cert
certbot certonly --dns-cloudflare \
  -d encypherai.com \
  -d *.encypherai.com
```

#### 1.3 Infrastructure Setup
- [ ] Set up Kubernetes cluster or Docker Swarm
- [ ] Configure Nginx/Traefik as API gateway
- [ ] Set up PostgreSQL cluster
- [ ] Set up Redis cluster
- [ ] Set up RabbitMQ/Kafka
- [ ] Set up MinIO for object storage
- [ ] Set up monitoring (Prometheus/Grafana)

---

### Phase 2: Frontend Separation (Week 2)

#### 2.1 Split Current Frontend

**Current Structure:**
```
encypher_website/frontend/
├── src/app/
│   ├── (marketing)/         → Marketing pages
│   ├── dashboard/           → Dashboard pages
│   └── api/                 → API routes
```

**New Structure:**

**Marketing Site** (`encypherai.com`):
```
marketing-site/
├── src/
│   ├── app/
│   │   ├── page.tsx         → Homepage
│   │   ├── pricing/         → Pricing page
│   │   ├── features/        → Features
│   │   ├── blog/            → Blog
│   │   └── contact/         → Contact
│   ├── components/
│   │   └── shared/          → Shared components
│   └── styles/
│       ├── globals.css      → Global styles
│       └── theme.css        → Brand colors
├── public/
└── package.json
```

**Dashboard App** (`dashboard.encypherai.com`):
```
dashboard-app/
├── src/
│   ├── app/
│   │   ├── page.tsx         → Dashboard home
│   │   ├── signup/          → Signup flow
│   │   ├── login/           → Login flow
│   │   ├── api-keys/        → API key management
│   │   ├── usage/           → Usage & billing
│   │   ├── documents/       → Document list
│   │   └── settings/        → Settings
│   ├── components/
│   │   ├── dashboard/       → Dashboard components
│   │   └── shared/          → Shared components
│   ├── lib/
│   │   ├── api.ts           → API client
│   │   └── auth.ts          → Auth helpers
│   └── styles/
│       ├── globals.css      → Global styles (same theme)
│       └── theme.css        → Brand colors (same)
├── public/
└── package.json
```

**Verification Portal** (`verify.encypherai.com`):
```
verification-portal/
├── src/
│   ├── app/
│   │   └── [documentId]/    → Verification page
│   ├── components/
│   │   └── verification/    → Verification UI
│   └── styles/
│       ├── globals.css      → Global styles (same theme)
│       └── theme.css        → Brand colors (same)
├── public/
└── package.json
```

#### 2.2 Shared Design System

Create a shared package for consistency:

```
packages/design-system/
├── src/
│   ├── styles/
│   │   ├── theme.css        → Brand colors
│   │   ├── globals.css      → Base styles
│   │   └── animations.css   → Shared animations
│   ├── components/
│   │   ├── Button/
│   │   ├── Card/
│   │   ├── Input/
│   │   └── ...
│   └── utils/
│       └── cn.ts            → Class name utility
├── tailwind.config.js       → Shared Tailwind config
└── package.json
```

**Install in each app:**
```json
{
  "dependencies": {
    "@encypher/design-system": "workspace:*"
  }
}
```

---

### Phase 3: Backend Microservices (Week 3-4)

#### 3.1 Extract Services from Monolith

**API Gateway** (`api.encypherai.com`):
```nginx
# nginx.conf
upstream encoding_service {
    server encoding:8001;
}

upstream manifest_service {
    server manifest:8002;
}

upstream analytics_service {
    server analytics:8003;
}

server {
    listen 443 ssl http2;
    server_name api.encypherai.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/encypherai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/encypherai.com/privkey.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=200 nodelay;

    # Routing
    location /api/v1/sign {
        proxy_pass http://encoding_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/verify {
        proxy_pass http://encoding_service;
    }

    location /api/v1/documents {
        proxy_pass http://manifest_service;
    }

    location /api/v1/analytics {
        proxy_pass http://analytics_service;
    }
}
```

#### 3.2 Service Implementation

**Encoding Service** (Port 8001):
```python
# encoding_service/main.py
from fastapi import FastAPI
from encypher_enterprise import EncypherClient

app = FastAPI(title="Encoding Service")

@app.post("/api/v1/sign")
async def sign_content(request: SignRequest):
    """Sign content using Encypher SDK"""
    client = EncypherClient(api_key=settings.ENCYPHER_API_KEY)
    result = client.sign(
        text=request.text,
        metadata=request.metadata
    )
    return result
```

**Manifest Service** (Port 8002):
```python
# manifest_service/main.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Manifest Service")

@app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str, db: AsyncSession):
    """Retrieve document manifest"""
    document = await db.get(Document, document_id)
    return document
```

**Analytics Service** (Port 8003):
```python
# analytics_service/main.py
from fastapi import FastAPI
from prometheus_client import Counter, Histogram

app = FastAPI(title="Analytics Service")

sign_counter = Counter('encypher_signs_total', 'Total signatures')
sign_duration = Histogram('encypher_sign_duration_seconds', 'Sign duration')

@app.post("/api/v1/analytics/track")
async def track_event(event: AnalyticsEvent):
    """Track usage event"""
    sign_counter.inc()
    # Store in database for billing
    await store_event(event)
```

---

### Phase 4: Shared Theme Implementation (Week 5)

#### 4.1 Create Shared Theme Package

```typescript
// packages/design-system/src/styles/theme.ts
export const colors = {
  // Brand colors
  'delft-blue': '#1b2f50',
  'blue-ncs': '#2a87c4',
  'columbia-blue': '#b7d5ed',
  'rosy-brown': '#ba8790',
  white: '#ffffff',
  
  // Semantic colors
  primary: '#2a87c4',      // blue-ncs
  secondary: '#b7d5ed',    // columbia-blue
  accent: '#ba8790',       // rosy-brown
  background: '#ffffff',
  foreground: '#1b2f50',   // delft-blue
} as const;

export const darkColors = {
  primary: '#b7d5ed',      // columbia-blue (lighter in dark mode)
  secondary: '#2a87c4',    // blue-ncs
  accent: '#ba8790',       // rosy-brown
  background: '#1b2f50',   // delft-blue
  foreground: '#ffffff',
} as const;
```

#### 4.2 Shared Tailwind Config

```javascript
// packages/design-system/tailwind.config.js
const { colors, darkColors } = require('./src/styles/theme');

module.exports = {
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        ...colors,
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
      },
      fontFamily: {
        sans: ['Roboto', 'Arial', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
    },
  },
};
```

#### 4.3 Apply to All Apps

**Marketing Site:**
```typescript
// marketing-site/tailwind.config.js
const baseConfig = require('@encypher/design-system/tailwind.config');

module.exports = {
  ...baseConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
```

**Dashboard:**
```typescript
// dashboard-app/tailwind.config.js
const baseConfig = require('@encypher/design-system/tailwind.config');

module.exports = {
  ...baseConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
```

**Verification Portal:**
```typescript
// verification-portal/tailwind.config.js
const baseConfig = require('@encypher/design-system/tailwind.config');

module.exports = {
  ...baseConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
```

---

## 📦 Monorepo Structure

```
encypherai-commercial/
├── apps/
│   ├── marketing-site/          → encypherai.com
│   ├── dashboard/               → dashboard.encypherai.com
│   ├── verification-portal/     → verify.encypherai.com
│   └── docs-site/               → docs.encypherai.com
│
├── services/
│   ├── api-gateway/             → Nginx/Traefik config
│   ├── encoding-service/        → Content signing
│   ├── manifest-service/        → Document management
│   ├── analytics-service/       → Usage tracking
│   └── auth-service/            → Keycloak config
│
├── packages/
│   ├── design-system/           → Shared UI components
│   ├── api-client/              → TypeScript API client
│   └── shared-types/            → Shared TypeScript types
│
├── enterprise_sdk/              → Python SDK (existing)
├── enterprise_api/              → Legacy API (to be migrated)
│
├── infrastructure/
│   ├── kubernetes/              → K8s manifests
│   ├── docker-compose/          → Local development
│   └── terraform/               → Infrastructure as code
│
└── docs/
    └── architecture/
        └── SUBDOMAIN_MIGRATION_PLAN.md  → This file
```

---

## 🚀 Deployment Configuration

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Frontend Apps
  marketing:
    build: ./apps/marketing-site
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  dashboard:
    build: ./apps/dashboard
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  verification:
    build: ./apps/verification-portal
    ports:
      - "3002:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  # API Gateway
  api-gateway:
    image: nginx:alpine
    ports:
      - "8000:80"
    volumes:
      - ./services/api-gateway/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - encoding-service
      - manifest-service
      - analytics-service
  
  # Backend Services
  encoding-service:
    build: ./services/encoding-service
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/encypher
      - REDIS_URL=redis://redis:6379
  
  manifest-service:
    build: ./services/manifest-service
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/encypher
      - REDIS_URL=redis://redis:6379
  
  analytics-service:
    build: ./services/analytics-service
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/encypher
      - PROMETHEUS_URL=http://prometheus:9090
  
  # Infrastructure
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=encypher
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./infrastructure/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3003:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Kubernetes (Production)

```yaml
# infrastructure/kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: encypher-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - encypherai.com
    - dashboard.encypherai.com
    - api.encypherai.com
    - verify.encypherai.com
    secretName: encypher-tls
  rules:
  - host: encypherai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: marketing-site
            port:
              number: 3000
  
  - host: dashboard.encypherai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dashboard
            port:
              number: 3000
  
  - host: api.encypherai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 80
  
  - host: verify.encypherai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: verification-portal
            port:
              number: 3000
```

---

## 🎨 Design System Components

### Shared Button Component

```typescript
// packages/design-system/src/components/Button.tsx
import { cn } from '../utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  className,
  children,
  ...props 
}: ButtonProps) {
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center rounded-lg font-medium',
        'transition-colors focus-visible:outline-none focus-visible:ring-2',
        'focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        
        // Variants
        {
          'bg-blue-ncs text-white hover:bg-blue-ncs/90': variant === 'primary',
          'bg-columbia-blue text-delft-blue hover:bg-columbia-blue/80': variant === 'secondary',
          'border-2 border-blue-ncs text-blue-ncs hover:bg-blue-ncs hover:text-white': variant === 'outline',
        },
        
        // Sizes
        {
          'h-9 px-3 text-sm': size === 'sm',
          'h-10 px-4 py-2': size === 'md',
          'h-11 px-8 text-lg': size === 'lg',
        },
        
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

### Usage Across Apps

```typescript
// apps/marketing-site/src/app/page.tsx
import { Button } from '@encypher/design-system';

export default function HomePage() {
  return (
    <div>
      <h1>Welcome to Encypher</h1>
      <Button variant="primary" size="lg">
        Get Started Free
      </Button>
    </div>
  );
}
```

```typescript
// apps/dashboard/src/app/page.tsx
import { Button } from '@encypher/design-system';

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Button variant="secondary">
        Create New Document
      </Button>
    </div>
  );
}
```

---

## 📋 Migration Checklist

### Pre-Migration
- [ ] Backup current production database
- [ ] Document all current API endpoints
- [ ] Create feature parity checklist
- [ ] Set up staging environment
- [ ] Create rollback plan

### Infrastructure Setup
- [ ] Configure DNS records for all subdomains
- [ ] Obtain SSL certificates
- [ ] Set up Kubernetes cluster or Docker Swarm
- [ ] Configure API gateway (Nginx/Traefik)
- [ ] Set up PostgreSQL with replication
- [ ] Set up Redis cluster
- [ ] Set up message queue (RabbitMQ/Kafka)
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Set up logging (Loki/ELK)
- [ ] Set up tracing (Jaeger)

### Frontend Migration
- [ ] Create design system package
- [ ] Extract marketing site
- [ ] Extract dashboard app
- [ ] Extract verification portal
- [ ] Set up shared component library
- [ ] Configure build pipelines
- [ ] Test cross-browser compatibility
- [ ] Test mobile responsiveness
- [ ] Set up CDN for static assets

### Backend Migration
- [ ] Extract encoding service
- [ ] Extract manifest service
- [ ] Extract analytics service
- [ ] Set up API gateway routing
- [ ] Implement service-to-service auth
- [ ] Set up database migrations
- [ ] Implement caching strategy
- [ ] Set up background job processing
- [ ] Configure rate limiting
- [ ] Implement circuit breakers

### Testing
- [ ] Unit tests for all services
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Load testing
- [ ] Security testing
- [ ] Performance testing
- [ ] Disaster recovery testing

### Deployment
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production (blue-green)
- [ ] Monitor for errors
- [ ] Verify all features working
- [ ] Update DNS if needed
- [ ] Monitor performance metrics

### Post-Migration
- [ ] Update all documentation
- [ ] Notify users of new URLs
- [ ] Set up redirects from old URLs
- [ ] Monitor error rates
- [ ] Optimize performance
- [ ] Decommission old infrastructure

---

## 🔒 Security Considerations

### API Gateway Security
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

# DDoS protection
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_conn addr 10;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Service-to-Service Auth
```python
# Internal JWT for service communication
from jose import jwt

def create_service_token(service_name: str) -> str:
    payload = {
        "sub": service_name,
        "type": "service",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SERVICE_SECRET_KEY, algorithm="HS256")
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics
```python
# In each service
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Business metrics
documents_signed = Counter('documents_signed_total', 'Total documents signed')
active_users = Gauge('active_users', 'Number of active users')
```

### Grafana Dashboards
- **System Health:** CPU, memory, disk, network
- **API Performance:** Request rate, latency, error rate
- **Business Metrics:** Signups, signatures, verifications
- **User Activity:** Active users, API usage, quota consumption

---

## 💰 Cost Optimization

### Resource Allocation
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Caching Strategy
- **Redis:** API responses, user sessions, rate limit counters
- **CDN:** Static assets, images, fonts
- **Database:** Query result caching, connection pooling

### Auto-scaling
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dashboard-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dashboard
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 🎯 Success Metrics

### Performance Targets
- **Page Load Time:** < 2 seconds
- **API Response Time:** < 200ms (p95)
- **Uptime:** 99.9%
- **Error Rate:** < 0.1%

### Business Metrics
- **User Signups:** Track conversion from marketing to dashboard
- **API Usage:** Monitor free vs paid tier usage
- **Feature Adoption:** Track which features are most used
- **Customer Satisfaction:** NPS score, support tickets

---

## 📅 Timeline

### Week 1: Infrastructure Setup
- DNS configuration
- SSL certificates
- Kubernetes/Docker setup
- Database setup
- Monitoring setup

### Week 2: Frontend Separation
- Create design system package
- Extract marketing site
- Extract dashboard
- Extract verification portal
- Test all apps locally

### Week 3-4: Backend Microservices
- Extract encoding service
- Extract manifest service
- Extract analytics service
- Set up API gateway
- Test service communication

### Week 5: Integration & Testing
- End-to-end testing
- Load testing
- Security testing
- Performance optimization
- Documentation updates

### Week 6: Deployment
- Deploy to staging
- User acceptance testing
- Deploy to production
- Monitor and optimize
- Celebrate! 🎉

---

## 🚨 Rollback Plan

### If Issues Arise:
1. **Immediate:** Switch DNS back to old infrastructure
2. **Database:** Restore from backup if needed
3. **Services:** Roll back to previous Docker images
4. **Monitoring:** Keep old infrastructure running for 2 weeks
5. **Communication:** Notify users of any downtime

### Rollback Triggers:
- Error rate > 5%
- Response time > 2 seconds
- Uptime < 99%
- Critical bugs reported
- Database corruption

---

## 📞 Support & Communication

### Internal Communication
- **Slack Channel:** #migration-updates
- **Daily Standups:** 9 AM during migration
- **Incident Response:** On-call rotation

### User Communication
- **Email:** Notify users 1 week before migration
- **In-app Banner:** Show migration notice
- **Status Page:** status.encypherai.com
- **Support:** support@encypherai.com

---

## 🎓 Training & Documentation

### Developer Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Service architecture diagrams
- [ ] Deployment runbooks
- [ ] Troubleshooting guides
- [ ] Code style guides

### User Documentation
- [ ] New dashboard guide
- [ ] API migration guide
- [ ] Feature comparison
- [ ] FAQ updates
- [ ] Video tutorials

---

## ✅ Conclusion

This migration plan provides a comprehensive roadmap for transitioning from a monolithic architecture to an enterprise-grade modular system while maintaining brand consistency and user experience.

**Key Benefits:**
- ✅ Better scalability and performance
- ✅ Independent service deployment
- ✅ Improved security boundaries
- ✅ Consistent brand experience
- ✅ Professional subdomain structure
- ✅ Enterprise-ready infrastructure

**Next Steps:**
1. Review and approve this plan
2. Set up staging environment
3. Begin Phase 1 (Infrastructure Setup)
4. Regular progress reviews
5. Execute migration with minimal downtime

---

**Document Version:** 1.0  
**Last Updated:** October 29, 2025  
**Owner:** Engineering Team  
**Status:** Ready for Review
