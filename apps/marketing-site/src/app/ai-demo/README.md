# AI Company Demo - Google Analytics for AI

An immersive, scroll-driven demonstration showing how Encypher provides AI companies with performance analytics, regulatory compliance, and publisher compatibility.

## Overview

**Route:** `/ai-demo`  
**Target Audience:** AI platform architects and technical decision makers  
**Goal:** Convert visitors to technical deep dive requests

## Features

### 6 Scroll-Triggered Sections

1. **The $2.7B Blind Spot** - Empty dashboard, establish R&D waste
2. **Performance Black Hole** - Viral content with no tracking (connection breaks)
3. **Regulatory Tsunami** - World map with regulation highlights
4. **Analytics Engine** - Dashboard comes alive with real-world data
5. **Technical Safe Harbor** - Three-column benefits (R&D, Publisher, Compliance)
6. **The Integration** - Code examples and architecture diagram

### Key Animations

- **Viral Content Flow**: AI generates → Copy → Social media → Engagement metrics
- **Broken Connection**: Arrow tries to connect to dashboard, fails with red X (Section 2)
- **Successful Connection**: Glowing line connects, dashboard populates (Section 4)
- **Regulatory Map**: Sequential region highlighting with regulation details
- **Dashboard Population**: Metrics animate in with real-time data

### Technical Stack

- **Framework**: Next.js 14+ (App Router)
- **Animations**: Framer Motion
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Scroll Detection**: Intersection Observer API
- **Analytics**: Custom tracking system

## Architecture

```
/app/ai-demo/
├── page.tsx                    # Main page with metadata
├── layout.tsx                  # Demo-specific layout
├── components/
│   ├── AIDemo.tsx              # Main orchestrator
│   ├── DemoLayout.tsx          # Two-column layout
│   ├── VisualizationArea.tsx   # Left column container
│   ├── sections/               # 6 section components
│   ├── visualizations/         # Dashboard, map, diagram
│   ├── animations/             # Reusable animations
│   └── ui/                     # UI components
├── hooks/
│   ├── useScrollProgress.ts    # Scroll percentage
│   ├── useScrollTrigger.ts     # Section visibility
│   └── useAnimationState.ts    # Animation control
└── lib/
    └── analytics.ts            # Event tracking
```

## API Endpoints

### POST /api/v1/deep-dive-requests
Submit a technical deep dive request from the form.

**Request:**
```json
{
  "name": "Kenji Tanaka",
  "email": "kenji@aicompany.com",
  "organization": "AI Corp",
  "role": "VP of AI Safety",
  "modelProvider": "Custom",
  "currentVolume": "1M+/day",
  "primaryInterest": ["Analytics", "Publisher Access"],
  "message": "Interested in beta access...",
  "source": "ai-demo"
}
```

## Analytics Events

**Page:** `ai_demo_loaded`, `ai_demo_exit`  
**Sections:** `section_1_blind_spot_viewed` through `section_6_integration_viewed`  
**Animations:** `viral_content_completed`, `dashboard_population_completed`, `regulatory_map_completed`  
**CTAs:** `cta_schedule_clicked`, `cta_download_sdk_clicked`, `deep_dive_form_submitted`  

## Performance Targets

- **First Contentful Paint**: <1.5s
- **Largest Contentful Paint**: <2.5s
- **Animation Frame Rate**: 60fps
- **Bundle Size**: <500KB (gzipped)

## Development

```bash
# From frontend directory
npm run dev

# Visit http://localhost:3000/ai-demo
```

## Related Documentation

- [PRD](../../../docs/PRD-ai-demo.md) - Full product requirements
- [Content](../../../docs/ai-demo-content.md) - Copy and messaging
- [Plan](../../../docs/ai-demo-plan.md) - Implementation plan

## Differences from Publisher Demo

- **Audience**: Technical (CTOs, VPs) vs Strategic
- **Value Prop**: Analytics/R&D intelligence vs Legal burden shift
- **Tone**: Technical confidence vs Strategic urgency
- **Visualizations**: Data dashboards vs Legal frameworks
- **CTA**: Technical deep dive vs Private demo
- **Form**: Technical specs (model, volume) vs Strategic role

## Support

For issues or questions:
- **Technical**: Check GitHub issues
- **Content**: Contact marketing team
- **Analytics**: Contact product team
