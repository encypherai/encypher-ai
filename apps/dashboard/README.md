# Encypher Dashboard

**Domain:** `dashboard.encypherai.com`  
**Purpose:** User dashboard for API key management, usage tracking, and content authentication

## 🚀 Getting Started

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3001](http://localhost:3001)

### Build

```bash
npm run build
npm start
```

## 🎨 Design System

This app uses the unified Encypher design system (`@encypher/design-system`).

## 📁 Structure

```
src/
├── app/
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Dashboard home
│   └── globals.css      # Global styles
├── components/          # Shared components
└── lib/                 # Utilities
```

## 🔐 Features

### Core Features
- **API Key Management** - Generate, view, and revoke API keys
- **Usage Statistics** - Track API calls, documents signed, verifications
- **Quick Actions** - Sign documents, verify content, view analytics
- **Responsive Design** - Works on all devices with mobile navigation
- **Admin Controls** - Manage users, roles, tiers, and invoices without touching the database

### User Experience
- **Onboarding Flow** - Welcome modal for new users with step-by-step guide
- **Password Reset** - Forgot password and reset password flows
- **Command Palette** - Quick navigation with Cmd+K / Ctrl+K
- **Dark Mode** - Theme toggle with system preference detection
- **Notification Center** - In-app notifications with bell icon

### Team & Organization
- **Team Management** - Invite members, manage roles, view audit logs
- **Organization Switcher** - Switch between organizations (business tier)
- **Org-Scoped API Keys** - API keys are created/listed for the active organization
- **Create Organization** - Team page supports creating a new organization and setting it active
- **Webhooks** - Configure webhook endpoints for real-time notifications

### Data & Export
- **Activity Feed** - Recent activity timeline
- **CSV Export** - Export analytics and API keys data
- **Audit Logs** - View organization activity history

## 🌐 Deployment

This site will be deployed to `dashboard.encypherai.com`.

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://api.encypherai.com/api/v1
NEXT_PUBLIC_SITE_URL=https://encypherai.com
NEXTAUTH_URL=https://dashboard.encypherai.com
NEXTAUTH_SECRET=your-secret-here
```

### Backend Integration

All dashboard API calls proxy directly to the [Enterprise API](../enterprise_api/README.md) and the microservice gateway in [services/README.md](../services/README.md). `NEXT_PUBLIC_API_URL` must include the `/api/v1` base (e.g., `https://api.encypherai.com/api/v1`) so routes like `/auth/login`, `/api-keys`, and `/admin/users` reach the live backend.

## 📚 Documentation

- [Design System](../../packages/design-system/README.md)
- [Migration Plan](../../docs/architecture/SUBDOMAIN_MIGRATION_PLAN.md)
