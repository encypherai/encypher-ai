# @encypher/design-system

Unified design system for all Encypher properties. Provides consistent branding, components, and styles across:

- `encypherai.com` (Marketing)
- `dashboard.encypherai.com` (Dashboard)
- `verify.encypherai.com` (Verification)
- `docs.encypherai.com` (Documentation)

## 🎨 Brand Colors

```css
--delft-blue: #1b2f50      /* Primary dark blue */
--blue-ncs: #2a87c4         /* Action blue */
--columbia-blue: #b7d5ed    /* Light blue - PRIMARY CTA COLOR */
--rosy-brown: #ba8790       /* Secondary accent */
```

**Primary CTA:** Columbia Blue (#b7d5ed) with white text provides **high contrast** and excellent visibility for call-to-action buttons.

## 📦 Installation

```bash
# In your app directory
npm install @encypher/design-system
# or
pnpm add @encypher/design-system
```

## 🚀 Usage

### 1. Import Styles

In your app's root layout or `_app.tsx`:

```typescript
import '@encypher/design-system/styles';
```

### 2. Configure Tailwind

In your `tailwind.config.js`:

```javascript
const designSystemConfig = require('@encypher/design-system/tailwind');

module.exports = {
  ...designSystemConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    // Include design system components
    '../../packages/design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
```

### 3. Use Components

```typescript
import { Button, Card, Input } from '@encypher/design-system';

export default function MyPage() {
  return (
    <Card>
      <h1>Welcome to Encypher</h1>
      
      {/* Primary CTA - Columbia Blue with white text */}
      <Button variant="primary" size="lg">
        Get Started Free
      </Button>
      
      {/* Secondary action */}
      <Button variant="outline">
        Learn More
      </Button>
      
      <Input 
        placeholder="Enter your email"
        leftIcon={<MailIcon />}
      />
    </Card>
  );
}
```

## 🎯 Components

### Button

High-contrast button with Columbia Blue as the primary CTA color.

```typescript
<Button 
  variant="primary"    // Columbia Blue (HIGH CONTRAST)
  size="lg"
  fullWidth
  loading={isLoading}
  leftIcon={<Icon />}
>
  Sign Up Now
</Button>
```

**Variants:**
- `primary` - Columbia Blue with white text (best for CTAs)
- `secondary` - Light gray background
- `outline` - Border only
- `ghost` - Transparent background
- `destructive` - Red for dangerous actions
- `success` - Green for positive actions

**Sizes:** `sm` | `md` | `lg` | `xl`

### Card

Elevated surface for grouping content.

```typescript
<Card variant="elevated" padding="lg">
  <CardHeader>
    <CardTitle>Dashboard</CardTitle>
    <CardDescription>Manage your content</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Your content */}
  </CardContent>
  <CardFooter>
    <Button>Save Changes</Button>
  </CardFooter>
</Card>
```

### Input

Form input with consistent styling.

```typescript
<Input
  variant="default"
  inputSize="md"
  placeholder="Search..."
  leftIcon={<SearchIcon />}
  error={hasError}
  success={isValid}
/>
```

## 🎨 Using Brand Colors

### In Tailwind Classes

```typescript
<div className="bg-columbia-blue text-white">
  High contrast CTA section
</div>

<div className="bg-delft-blue text-white">
  Dark header
</div>

<button className="bg-blue-ncs hover:bg-blue-ncs/90">
  Action button
</button>
```

### In CSS Variables

```css
.custom-element {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
}
```

## 🌓 Dark Mode

Dark mode is supported via the `.dark` class:

```typescript
<html className={isDark ? 'dark' : ''}>
  {/* Your app */}
</html>
```

Colors automatically adjust:
- Light mode: Columbia Blue primary
- Dark mode: Lighter shades for better contrast

## 📐 Utilities

### cn() - Class Name Utility

Merge Tailwind classes with proper precedence:

```typescript
import { cn } from '@encypher/design-system';

<div className={cn(
  'px-4 py-2',
  isActive && 'bg-columbia-blue text-white',
  className
)} />
```

## 🎯 Best Practices

### 1. Use Primary Variant for CTAs

```typescript
// ✅ Good - High contrast, clear action
<Button variant="primary" size="lg">
  Start Free Trial
</Button>

// ❌ Avoid - Less visible
<Button variant="ghost">
  Start Free Trial
</Button>
```

### 2. Consistent Spacing

Use the design system's spacing scale:

```typescript
<Card padding="lg">  {/* Consistent padding */}
  <div className="space-y-4">  {/* Consistent gaps */}
    <Button size="lg" />  {/* Consistent sizing */}
  </div>
</Card>
```

### 3. Semantic Colors

Use semantic color names for better maintainability:

```typescript
// ✅ Good
<Button variant="destructive">Delete</Button>
<Button variant="success">Confirm</Button>

// ❌ Avoid
<Button className="bg-red-500">Delete</Button>
```

## 📱 Responsive Design

All components are mobile-first and responsive:

```typescript
<Button 
  size="sm"           // Mobile
  className="md:h-12" // Tablet+
>
  Responsive Button
</Button>
```

## 🔧 Customization

### Extending Colors

In your app's `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Add app-specific colors
        'app-purple': '#9333ea',
      },
    },
  },
};
```

### Custom Components

Build on top of design system components:

```typescript
import { Button, type ButtonProps } from '@encypher/design-system';

export function CTAButton(props: ButtonProps) {
  return (
    <Button 
      variant="primary" 
      size="lg"
      className="shadow-lg hover:shadow-xl transition-shadow"
      {...props}
    />
  );
}
```

## 📚 Examples

### Marketing Page

```typescript
import { Button, Card } from '@encypher/design-system';

export default function HomePage() {
  return (
    <div className="container mx-auto py-12">
      <h1 className="text-4xl font-bold text-delft-blue mb-4">
        Welcome to Encypher
      </h1>
      
      <p className="text-lg text-muted-foreground mb-8">
        Cryptographic content authentication
      </p>
      
      <div className="flex gap-4">
        <Button variant="primary" size="xl">
          Get Started Free
        </Button>
        <Button variant="outline" size="xl">
          View Demo
        </Button>
      </div>
    </div>
  );
}
```

### Dashboard Page

```typescript
import { Card, CardHeader, CardTitle, CardContent, Button } from '@encypher/design-system';

export default function DashboardPage() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">1,234</p>
          <Button variant="primary" className="mt-4" fullWidth>
            View All
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Form Example

```typescript
import { Input, Button, Card } from '@encypher/design-system';

export default function SignupForm() {
  return (
    <Card padding="lg">
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
        />
        
        <Button variant="primary" size="lg" fullWidth>
          Create Account
        </Button>
      </form>
    </Card>
  );
}
```

## 🤝 Contributing

When adding new components:

1. Follow existing patterns
2. Use brand colors
3. Support dark mode
4. Add TypeScript types
5. Document with examples

## 📄 License

MIT © Encypher Team
