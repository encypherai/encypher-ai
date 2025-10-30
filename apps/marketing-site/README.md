# Encypher Marketing Site

**Domain:** `encypherai.com`  
**Purpose:** Marketing website for Encypher

## 🚀 Getting Started

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
npm start
```

## 🎨 Design System

This app uses the unified Encypher design system (`@encypher/design-system`).

### Components

```typescript
import { Button, Card, Input } from '@encypher/design-system';
```

### Brand Colors

- **Delft Blue** (#1b2f50) - Dark blue
- **Blue NCS** (#2a87c4) - Action blue
- **Columbia Blue** (#b7d5ed) - PRIMARY CTA (high contrast)
- **Rosy Brown** (#ba8790) - Accent

### Usage

```typescript
// High-contrast CTA
<Button variant="primary" size="lg">
  Get Started Free
</Button>

// Outline button
<Button variant="outline">
  Learn More
</Button>
```

## 📁 Structure

```
src/
├── app/
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Homepage
│   └── globals.css      # Global styles
└── components/          # Shared components
```

## 🌐 Deployment

This site will be deployed to `encypherai.com`.

### Environment Variables

Create `.env.local`:

```bash
# Add any environment variables here
```

## 📚 Documentation

- [Design System](../../packages/design-system/README.md)
- [Migration Plan](../../docs/architecture/SUBDOMAIN_MIGRATION_PLAN.md)
