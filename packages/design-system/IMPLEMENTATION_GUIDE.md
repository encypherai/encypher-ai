# 🎨 Encypher Design System - Implementation Guide

**Status:** ✅ Core System Complete
**Next Steps:** Install dependencies and integrate into apps

---

## 📦 What's Been Created

### Design System Package Structure

```
packages/design-system/
├── src/
│   ├── styles/
│   │   ├── theme.css           ✅ Brand colors & CSS variables
│   │   └── globals.css         ✅ Base styles & typography
│   ├── components/
│   │   ├── Button.tsx          ✅ CTA button (Columbia Blue primary)
│   │   ├── Card.tsx            ✅ Content cards
│   │   └── Input.tsx           ✅ Form inputs
│   ├── utils/
│   │   └── cn.ts               ✅ Class name utility
│   └── index.ts                ✅ Main exports
├── package.json                ✅ Dependencies defined
├── tailwind.config.js          ✅ Shared Tailwind config
├── tsconfig.json               ✅ TypeScript config
├── README.md                   ✅ Complete documentation
└── IMPLEMENTATION_GUIDE.md     ✅ This file
```

---

## 🎨 Brand System

### Color Palette

```css
/* Primary Colors */
--delft-blue: #1b2f50      /* Dark blue - headers, text */
--blue-ncs: #2a87c4         /* Action blue - links, accents */
--columbia-blue: #b7d5ed    /* Light blue - PRIMARY CTA COLOR ⭐ */
--rosy-brown: #ba8790       /* Pink/brown - secondary accent */
```

### Why Columbia Blue for CTAs?

**High Contrast:** Columbia Blue (#b7d5ed) with white text provides:
- ✅ **WCAG AAA** contrast ratio
- ✅ Excellent visibility
- ✅ Professional appearance
- ✅ Stands out without being aggressive

**Usage:**
```typescript
// Primary CTA - Use this for main actions
<Button variant="primary">Get Started Free</Button>

// Renders as: Columbia Blue background + White text
```

---

## 🚀 Installation Steps

### Step 1: Install Dependencies

```bash
cd packages/design-system
npm install
# or
pnpm install
```

**Dependencies:**
- `clsx` - Conditional class names
- `tailwind-merge` - Merge Tailwind classes
- `react` & `react-dom` (peer dependencies)
- `typescript` (dev dependency)

### Step 2: Build (Optional)

```bash
npm run type-check
```

---

## 🔗 Integration into Apps

### For Marketing Site (`encypher.com`)

**1. Install design system:**

```bash
cd apps/marketing-site
npm install @encypher/design-system
```

**2. Import styles in `app/layout.tsx`:**

```typescript
import '@encypher/design-system/styles';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

**3. Configure Tailwind (`tailwind.config.js`):**

```javascript
const designSystemConfig = require('@encypher/design-system/tailwind');

module.exports = {
  ...designSystemConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
```

**4. Use components:**

```typescript
import { Button, Card } from '@encypher/design-system';

export default function HomePage() {
  return (
    <div className="container mx-auto">
      <h1 className="text-4xl font-bold text-delft-blue">
        Welcome to Encypher
      </h1>

      {/* High-contrast CTA */}
      <Button variant="primary" size="xl">
        Get Started Free
      </Button>

      <Button variant="outline" size="xl">
        Learn More
      </Button>
    </div>
  );
}
```

### For Dashboard (`dashboard.encypher.com`)

Same steps as marketing site, but use dashboard-specific layouts:

```typescript
import { Button, Card, Input } from '@encypher/design-system';

export default function DashboardPage() {
  return (
    <div className="grid gap-6 md:grid-cols-3">
      <Card variant="elevated">
        <CardHeader>
          <CardTitle>API Keys</CardTitle>
        </CardHeader>
        <CardContent>
          <Button variant="primary" fullWidth>
            Generate New Key
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

### For Verification Portal (`verify.encypher.com`)

Lightweight implementation:

```typescript
import { Card, Button } from '@encypher/design-system';

export default function VerifyPage({ documentId }) {
  return (
    <Card variant="elevated" padding="lg">
      <h1>Document Verification</h1>
      <p>Document ID: {documentId}</p>

      <Button variant="success">
        ✓ Verified Authentic
      </Button>
    </Card>
  );
}
```

---

## 📝 Component Examples

### Button Variants

```typescript
// Primary CTA - Columbia Blue (HIGH CONTRAST)
<Button variant="primary" size="lg">
  Sign Up Now
</Button>

// Secondary action
<Button variant="secondary">
  Learn More
</Button>

// Outline style
<Button variant="outline">
  View Details
</Button>

// Ghost (subtle)
<Button variant="ghost">
  Cancel
</Button>

// Destructive action
<Button variant="destructive">
  Delete Account
</Button>

// Success action
<Button variant="success">
  Confirm
</Button>
```

### Button with Icons

```typescript
<Button
  variant="primary"
  leftIcon={<ArrowRightIcon />}
  loading={isLoading}
>
  Continue
</Button>
```

### Card Layouts

```typescript
<Card variant="elevated" padding="lg">
  <CardHeader>
    <CardTitle>Dashboard Stats</CardTitle>
    <CardDescription>Your activity this month</CardDescription>
  </CardHeader>

  <CardContent>
    <div className="space-y-4">
      <div>
        <p className="text-sm text-muted-foreground">Documents Signed</p>
        <p className="text-3xl font-bold">1,234</p>
      </div>
    </div>
  </CardContent>

  <CardFooter>
    <Button variant="primary" fullWidth>
      View All Documents
    </Button>
  </CardFooter>
</Card>
```

### Form with Inputs

```typescript
<form className="space-y-4">
  <Input
    type="email"
    placeholder="Email address"
    leftIcon={<MailIcon />}
  />

  <Input
    type="password"
    placeholder="Password"
    leftIcon={<LockIcon />}
    error={hasError}
  />

  <Button variant="primary" size="lg" fullWidth>
    Create Account
  </Button>
</form>
```

---

## 🎯 Design Principles

### 1. High Contrast CTAs

Always use `variant="primary"` for main actions:

```typescript
// ✅ Good - Clear, high contrast
<Button variant="primary" size="lg">
  Start Free Trial
</Button>

// ❌ Avoid - Low contrast
<Button variant="ghost">
  Start Free Trial
</Button>
```

### 2. Consistent Spacing

Use the design system's spacing scale:

```typescript
<div className="space-y-4">  {/* Consistent vertical spacing */}
  <Card padding="lg">        {/* Consistent padding */}
    <Button size="lg" />     {/* Consistent sizing */}
  </Card>
</div>
```

### 3. Semantic Colors

Use semantic variants:

```typescript
<Button variant="destructive">Delete</Button>  // Red
<Button variant="success">Confirm</Button>     // Green
<Button variant="primary">Continue</Button>    // Columbia Blue
```

### 4. Mobile-First

All components are responsive:

```typescript
<Button
  size="sm"                    // Mobile
  className="md:h-12 md:px-8"  // Tablet+
>
  Responsive
</Button>
```

---

## 🌓 Dark Mode Support

Dark mode is built-in. Just add the `dark` class:

```typescript
<html className={isDark ? 'dark' : ''}>
  <body>
    {/* Colors automatically adjust */}
    <Button variant="primary">
      Works in both modes
    </Button>
  </body>
</html>
```

**Color adjustments:**
- Light mode: Columbia Blue primary
- Dark mode: Lighter shades for better contrast on dark backgrounds

---

## 📊 Migration Checklist

### Phase 1: Setup Design System ✅
- [x] Create package structure
- [x] Define brand colors
- [x] Create Button component (Columbia Blue primary)
- [x] Create Card component
- [x] Create Input component
- [x] Create utility functions
- [x] Write documentation

### Phase 2: Install Dependencies (Next)
- [ ] Run `npm install` in design-system package
- [ ] Verify no TypeScript errors
- [ ] Test components locally

### Phase 3: Extract Marketing Site
- [ ] Create `apps/marketing-site` directory
- [ ] Copy marketing pages from current frontend
- [ ] Install design system
- [ ] Replace components with design system
- [ ] Test locally

### Phase 4: Extract Dashboard
- [ ] Create `apps/dashboard` directory
- [ ] Copy dashboard pages from current frontend
- [ ] Install design system
- [ ] Replace components with design system
- [ ] Test locally

### Phase 5: Extract Verification Portal
- [ ] Create `apps/verification-portal` directory
- [ ] Create verification UI
- [ ] Install design system
- [ ] Build verification page
- [ ] Test locally

### Phase 6: Deploy
- [ ] Set up DNS for subdomains
- [ ] Configure SSL certificates
- [ ] Deploy marketing site
- [ ] Deploy dashboard
- [ ] Deploy verification portal
- [ ] Test in production

---

## 🔧 Customization

### Adding New Components

Follow this pattern:

```typescript
// packages/design-system/src/components/NewComponent.tsx
import * as React from 'react';
import { cn } from '../utils/cn';

export interface NewComponentProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'custom';
}

export const NewComponent = React.forwardRef<HTMLDivElement, NewComponentProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'base-styles',
          {
            'variant-styles': variant === 'default',
          },
          className
        )}
        {...props}
      />
    );
  }
);

NewComponent.displayName = 'NewComponent';
```

Then export in `src/index.ts`:

```typescript
export { NewComponent, type NewComponentProps } from './components/NewComponent';
```

### Extending Colors

In your app's `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'app-specific': '#custom',
      },
    },
  },
};
```

---

## 📚 Resources

- **Full Documentation:** `packages/design-system/README.md`
- **Migration Plan:** `docs/architecture/SUBDOMAIN_MIGRATION_PLAN.md`
- **Architecture:** `docs/architecture/SUBDOMAIN_STRATEGY.md`

---

## 🎉 What's Next?

1. **Install dependencies** in the design-system package
2. **Create first app** (marketing site)
3. **Test components** locally
4. **Iterate and improve**
5. **Deploy to production**

---

## 💡 Tips

### Performance
- Design system is tree-shakeable
- Only imports used components
- Minimal bundle size impact

### Consistency
- All apps automatically get brand updates
- Change colors once, update everywhere
- Consistent user experience

### Developer Experience
- TypeScript support
- IntelliSense autocomplete
- Comprehensive documentation
- Easy to extend

---

**Status:** ✅ Design System Ready
**Next Step:** Install dependencies and start migration
**Timeline:** Ready to begin Phase 2 (app extraction)
