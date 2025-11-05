"""
Load testing for coalition endpoints.
Tests system performance under high load (10K+ members).

Run with: locust -f test_coalition_load.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between
import random
import uuid
from datetime import datetime


class CoalitionMemberUser(HttpUser):
    """Simulates a coalition member accessing the system."""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts."""
        # Simulate login
        self.user_id = str(uuid.uuid4())
        self.auth_token = "test_token"  # In real test, get from auth endpoint
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def view_coalition_stats(self):
        """Most common task: viewing coalition stats."""
        self.client.get(
            "/api/v1/coalition/stats",
            headers=self.headers,
            name="GET /coalition/stats"
        )
    
    @task(5)
    def view_revenue(self):
        """View revenue breakdown."""
        self.client.get(
            "/api/v1/coalition/revenue",
            headers=self.headers,
            name="GET /coalition/revenue"
        )
    
    @task(3)
    def view_top_content(self):
        """View top performing content."""
        self.client.get(
            "/api/v1/coalition/content/performance?limit=10",
            headers=self.headers,
            name="GET /coalition/content/performance"
        )
    
    @task(2)
    def view_member_info(self):
        """View member information."""
        self.client.get(
            "/api/v1/coalition/member",
            headers=self.headers,
            name="GET /coalition/member"
        )
    
    @task(1)
    def create_content(self):
        """Create new content (less frequent)."""
        content_data = {
            "user_id": self.user_id,
            "title": f"Article {random.randint(1, 10000)}",
            "content_type": random.choice(["article", "blog", "social_post"]),
            "word_count": random.randint(500, 3000),
            "content_hash": str(uuid.uuid4()),
            "signed_at": datetime.utcnow().isoformat()
        }
        
        self.client.post(
            "/api/v1/coalition/content",
            json=content_data,
            headers=self.headers,
            name="POST /coalition/content"
        )


class CoalitionAdminUser(HttpUser):
    """Simulates an admin user managing the coalition."""
    
    wait_time = between(5, 15)  # Admins check less frequently
    
    def on_start(self):
        """Called when admin user starts."""
        self.auth_token = "admin_token"  # In real test, get from auth endpoint
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    @task(5)
    def view_admin_overview(self):
        """View coalition overview."""
        self.client.get(
            "/api/v1/coalition/admin/overview",
            headers=self.headers,
            name="GET /coalition/admin/overview"
        )
    
    @task(3)
    def view_members_list(self):
        """View list of members."""
        skip = random.randint(0, 100) * 50
        self.client.get(
            f"/api/v1/coalition/admin/members?skip={skip}&limit=50",
            headers=self.headers,
            name="GET /coalition/admin/members"
        )
    
    @task(1)
    def create_revenue_transaction(self):
        """Create revenue transaction (rare)."""
        transaction_data = {
            "user_id": str(uuid.uuid4()),
            "amount": round(random.uniform(10.0, 500.0), 2),
            "currency": "USD",
            "period_start": "2025-01-01T00:00:00Z",
            "period_end": "2025-01-31T23:59:59Z",
            "status": "pending"
        }
        
        self.client.post(
            "/api/v1/coalition/revenue",
            json=transaction_data,
            headers=self.headers,
            name="POST /coalition/revenue"
        )


class AICompanyUser(HttpUser):
    """Simulates an AI company accessing content."""
    
    wait_time = between(0.1, 1)  # AI companies access frequently
    
    def on_start(self):
        """Called when AI company starts."""
        self.api_key = "lic_test_key"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def access_content(self):
        """Access content from coalition pool."""
        # Simulate accessing random content
        content_id = str(uuid.uuid4())
        log_data = {
            "content_id": content_id,
            "ai_company": random.choice(["OpenAI", "Anthropic", "Google", "Meta"]),
            "access_type": random.choice(["training", "inference", "verification"]),
            "accessed_at": datetime.utcnow().isoformat()
        }
        
        self.client.post(
            "/api/v1/coalition/access-log",
            json=log_data,
            headers=self.headers,
            name="POST /coalition/access-log"
        )


"""
Load Testing Scenarios:

1. Normal Load (Baseline):
   - 100 concurrent users
   - 50 members, 5 admins, 45 AI company requests
   - Run for 10 minutes
   - Command: locust -f test_coalition_load.py --users 100 --spawn-rate 10 --run-time 10m

2. Peak Load:
   - 1000 concurrent users
   - 500 members, 50 admins, 450 AI company requests
   - Run for 30 minutes
   - Command: locust -f test_coalition_load.py --users 1000 --spawn-rate 50 --run-time 30m

3. Stress Test (10K+ members):
   - 10000 concurrent users
   - 5000 members, 500 admins, 4500 AI company requests
   - Run for 1 hour
   - Command: locust -f test_coalition_load.py --users 10000 --spawn-rate 100 --run-time 1h

4. Spike Test:
   - Start with 100 users, spike to 5000, back to 100
   - Manual control via Locust web UI

Expected Performance Targets:
- GET /coalition/stats: < 200ms (p95)
- GET /coalition/revenue: < 300ms (p95)
- POST /coalition/content: < 500ms (p95)
- POST /coalition/access-log: < 100ms (p95)
- Error rate: < 1%
- Throughput: > 1000 req/s

Database Considerations:
- Ensure proper indexing on:
  - coalition_members.user_id
  - content_items.user_id
  - content_access_logs.content_id
  - revenue_transactions.user_id
- Connection pool size: 100+
- Query timeout: 30s
- Enable query caching for stats endpoints
"""
