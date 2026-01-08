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

## 🤖 AI Summary & SEO Content (Internal Only)

The marketing site uses `AISummary` components for AI crawler optimization and SEO. These components render hidden semantic content and JSON-LD structured data for search engines.

### Component Location
- **Component:** `src/components/seo/AISummary.tsx`
- **Props:** `title`, `whatWeDo`, `whoItsFor`, `keyDifferentiator`, `primaryValue`, `faq?`, `pagePath?`, `pageType?`

### Pages with AISummary Components
All major pages include an `AISummary` component. To update messaging across the site:

| Page | File Location |
|------|---------------|
| Homepage | `src/app/page.tsx` |
| Pricing | `src/app/pricing/page.tsx` |
| Blog | `src/app/(marketing)/blog/page.tsx` |
| AI Copyright | `src/app/ai-copyright-infringement/page.tsx` |
| AI Demo | `src/app/ai-demo/page.tsx` |
| AI Detector | `src/app/ai-detector/page.tsx` |
| Company | `src/app/company/page.tsx` |
| Deepfake Detection | `src/app/deepfake-detection/page.tsx` |
| Platform | `src/app/platform/page.tsx` |
| Publisher Demo | `src/app/publisher-demo/page.tsx` |
| Solutions Overview | `src/app/solutions/page.tsx` |
| Solutions - AI Companies | `src/app/solutions/ai-companies/page.tsx` |
| Solutions - Enterprises | `src/app/solutions/enterprises/page.tsx` |
| Solutions - Publishers | `src/app/solutions/publishers/page.tsx` |
| Tools | `src/app/tools/page.tsx` |

### Key Messaging Guidelines
When updating AISummary content, ensure alignment with:
- **Marketing Guidelines:** `docs/company_internal_strategy/Encypher_Marketing_Guidelines.md`
- **ICPs:** `docs/company_internal_strategy/Encypher_ICPs.md`

### Current Messaging Standards (as of Dec 2025)
- **Co-Chair positioning:** "Co-Chair of C2PA Text Provenance Task Force (c2pa.org)"
- **Partners:** "NYT, BBC, AP, Google, OpenAI, Adobe, Microsoft and others"
- **Standard date:** "January 8, 2026"
- **API/SDKs:** "Python, TypeScript, Go, and Rust"
- **Tone:** Collaborative, not adversarial (avoid "willful infringement", "eliminates defense" language)
- **Do NOT advertise:** Syracuse Symposium (internal only)

### How to Update
1. Review the Marketing Guidelines and ICPs documents
2. Update the `AISummary` props in each page file
3. Run `npx next lint` to verify no syntax errors
4. Test locally with `npm run dev`

---

## 📚 Documentation

- [Design System](../../packages/design-system/README.md)
- [Subdomain Strategy](../../docs/architecture/SUBDOMAIN_STRATEGY.md)
- [Pricing Config (SSOT)](../../packages/pricing-config/README.md)
- [Pricing Strategy & OEM Guidelines](../../docs/pricing/PRICING_STRATEGY.md)
- [Marketing Guidelines](../../docs/company_internal_strategy/Encypher_Marketing_Guidelines.md) (Internal)
- [ICPs](../../docs/company_internal_strategy/Encypher_ICPs.md) (Internal)
