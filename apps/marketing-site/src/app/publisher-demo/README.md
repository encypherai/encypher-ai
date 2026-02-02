# Publisher Demo - The Interactive Proof

An immersive, scroll-driven demonstration showing how Encypher shifts the burden of proof from publishers to AI companies through cryptographic provenance.

## Overview

**Route:** `/publisher-demo`  
**Target Audience:** Publisher strategists and decision-makers  
**Goal:** Convert visitors to demo requests

## Features

### 6 Scroll-Triggered Sections

1. **Value & Vulnerability** - Hero section establishing the stakes
2. **"We Didn't Know" Loophole** - Animated copy-paste showing AI's plausible deniability
3. **Inescapable Notice** - Scanner animation demonstrating C2PA embedding
4. **Burden of Proof Shifts** - Red alert showing the transformation
5. **New Legal Reality** - Flowchart comparing before/after
6. **Coalition** - CTA with demo request form

### Key Animations

- **Copy-Paste Animation**: Cursor highlights text, copies to AI chatbot
- **Scanner Animation**: Blue bar scans article, leaves C2PA badge
- **Red Alert**: Un-dismissible licensing notice in chatbot
- **Flowchart**: Staggered nodes showing legal framework shift

### Technical Stack

- **Framework**: Next.js 14+ (App Router)
- **Animations**: Framer Motion
- **Styling**: TailwindCSS
- **Scroll Detection**: Intersection Observer API
- **Analytics**: Custom tracking system

## Architecture

```
/app/publisher-demo/
├── page.tsx                    # Main page with metadata
├── layout.tsx                  # Demo-specific layout
├── components/
│   ├── PublisherDemo.tsx       # Main orchestrator
│   ├── DemoLayout.tsx          # Two-column layout
│   ├── ArticleIframe.tsx       # Mock article container
│   ├── sections/               # 6 section components
│   ├── animations/             # Reusable animations
│   └── ui/                     # UI components
├── hooks/
│   ├── useScrollProgress.ts    # Scroll percentage
│   ├── useScrollTrigger.ts     # Section visibility
│   └── useViewportIntersection.ts
└── lib/
    └── analytics.ts            # Event tracking
```

## API Endpoints

### POST /api/v1/demo-requests
Submit a demo request from the form.

**Request:**
```json
{
  "name": "Jane Smith",
  "email": "jane@publisher.com",
  "organization": "The Times",
  "role": "VP Strategy",
  "message": "Interested in...",
  "source": "publisher-demo",
  "consent": true
}
```

**Response:**
```json
{
  "success": true,
  "id": "uuid-here",
  "message": "Demo request received..."
}
```

### POST /api/v1/marketing-analytics/events
Track user interactions and scroll events via the marketing analytics endpoint.

**Request:**
```json
{
  "event": "section_2_viewed",
  "properties": {
    "sectionName": "Loophole"
  },
  "sessionId": "session_123",
  "timestamp": 1697299200000
}
```

## Analytics Events

### Page Events
- `publisher_demo_loaded`
- `publisher_demo_exit`

### Section Events
- `section_1_viewed` through `section_6_viewed`

### Interaction Events
- `copy_paste_animation_completed`
- `scanner_animation_completed`
- `red_alert_animation_completed`
- `flowchart_animation_completed`
- `cta_button_clicked`
- `demo_form_opened`
- `demo_form_submitted`
- `demo_form_error`

### Scroll Milestones
- `scroll_25_percent`
- `scroll_50_percent`
- `scroll_75_percent`
- `scroll_100_percent`

## Performance Targets

- **First Contentful Paint**: <1.5s
- **Largest Contentful Paint**: <2.5s
- **Animation Frame Rate**: 60fps
- **Bundle Size**: <500KB (gzipped)

## Accessibility

- **WCAG 2.1 AA** compliant
- Full keyboard navigation
- Screen reader support with ARIA labels
- Reduced motion support via `prefers-reduced-motion`

## Development

### Local Development

```bash
# From frontend directory
npm run dev

# Visit http://localhost:3000/publisher-demo
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Testing

```bash
# Type check
npm run type-check

# Lint
npm run lint

# E2E tests
npm run test:e2e
```

## Deployment

The demo is automatically deployed with the main frontend application. No special configuration required.

### Database Migration

Run the Alembic migration to create required tables:

```bash
cd backend
alembic upgrade head
```

## Monitoring

### Key Metrics to Track

- **Engagement**: Scroll completion rate (target: 80%+)
- **Conversion**: CTA click rate (target: 15%+)
- **Performance**: Load time, animation FPS
- **Quality**: Error rate (target: <1%)

### Analytics Dashboard

Access analytics data via:
- Database queries on `demo_requests` and `analytics_events` tables
- Future: Admin dashboard for real-time metrics

## Troubleshooting

### Animations Not Triggering

- Check scroll position and Intersection Observer thresholds
- Verify Framer Motion is installed
- Check browser console for errors

### Form Submission Failing

- Verify backend API is running
- Check CORS configuration
- Verify database tables exist (run migrations)

### Performance Issues

- Check bundle size with `npm run build`
- Verify images are optimized
- Check for memory leaks in animations

## Future Enhancements

- [ ] A/B testing framework
- [ ] Personalization by industry
- [ ] Multi-language support
- [ ] Video testimonials
- [ ] Live coalition member counter
- [ ] Calendar integration for demo booking

## Related Documentation

- [PRD](../../../docs/PRD-publisher-demo.md) - Full product requirements
- [Storyboard](../../../docs/publisher-demo-storyboard.md) - Visual guide
- [Content](../../../docs/publisher-demo-content.md) - Copy and messaging

## Support

For issues or questions:
- **Technical**: Check GitHub issues
- **Content**: Contact marketing team
- **Analytics**: Contact product team
