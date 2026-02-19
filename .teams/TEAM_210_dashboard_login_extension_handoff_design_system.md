# TEAM_210 — Dashboard Login & Extension-Handoff Design System Alignment

## Status: Complete

## Summary
Audited and updated `apps/dashboard` login and extension-handoff pages to follow the design system.

## Findings

### extension-handoff/page.tsx
Already fully compliant — uses `Button`, `Card`, `CardContent`, `CardHeader`, `CardTitle`, `CardDescription` from `@encypher/design-system`.

### login/page.tsx (fixed)
Multiple raw `<button>` elements replaced with design system `Button` component:
- Google OAuth button → `Button variant="outline"` with `leftIcon`
- GitHub OAuth button → `Button variant="outline"` with `leftIcon`
- Passkey button → `Button variant="outline" fullWidth loading={passkeyLoading}`
- Submit button → `Button variant="primary" size="lg" fullWidth loading={loading}`
- Custom card markup (raw `<div>`) → `Card variant="elevated" padding="lg"` + `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`
- Suspense fallback raw div → `Card` + `CardHeader` + `CardTitle` + `CardDescription`
- Error message colors aligned to semantic `bg-destructive/10 border-destructive text-destructive`
- Link colors aligned to `text-blue-ncs` (design system brand color)
- Logo moved outside Card (above it), matching signup page pattern

## Lint
Both pages lint clean (exit 0). Pre-existing warnings in login page (any types in passkey functions, apostrophe) are unchanged.

## Git Commit Suggestion
```
feat(dashboard): align login page with design system

Replace all raw <button> elements in login/page.tsx with the design
system Button component (outline for OAuth/passkey, primary for submit).
Replace custom card markup with Card/CardHeader/CardTitle/CardDescription/
CardContent from @encypher/design-system. Align Suspense fallback and
error message colors to semantic design tokens. extension-handoff/page.tsx
was already compliant — no changes needed.
```
