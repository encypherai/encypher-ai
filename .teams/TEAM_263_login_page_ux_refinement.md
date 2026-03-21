# TEAM_263 - Login Page UX Refinement

## Status: COMPLETE

## Current Goal
Refine the dashboard login page: quiet zone overlay, dual-market copy, sign-up prominence, passkey grouping, marketing-site redirect verification, and mobile-friendly responsive fixes.

## Tasks
- [x] 2. Frosted-glass quiet zone behind right panel text -- backdrop-blur-md overlay
- [x] 3. Refine right panel copy for dual-sided market -- neutral infrastructure positioning, C2PA standard badge
- [x] 4. Sign-up path prominence (outlined button) -- border border-accent/40 hover:bg-accent/10
- [x] 5. Passkey button grouping into OAuth row -- Google | GitHub | Passkey unified row
- [x] 6. Verify marketing-site -> dashboard login redirect -- navbar and CTA links updated
- [x] 7. Match animation to marketing-site style -- dark navy gradient, forcedTheme="dark"
- [x] 8. UX audit and mobile-friendly fixes -- icon-only OAuth on mobile, lg: breakpoint for right panel, unified shadows

## Completed Changes

### Files Modified
- `apps/dashboard/src/app/login/page.tsx` -- All login page UX changes
- `apps/marketing-site/src/components/layout/navbar.tsx` -- Sign In/Get Started redirect to dashboard
- `apps/marketing-site/src/app/page.tsx` -- Hero CTA redirect to dashboard signup

### Key Decisions
- Right panel hidden below `lg:` (1024px) -- tablet gets full-width form instead of cramped split
- OAuth button labels hidden below `sm:` (640px) -- icon-only on mobile prevents overflow
- Dark navy gradient via inline style instead of Tailwind -- `linear-gradient(135deg, #1a2332 0%, #1e3a5f 40%, #1b2f50 100%)`
- `NextThemesProvider forcedTheme="dark"` wraps MetadataBackground so animation always uses bright particle colors
- Marketing-site auth links point directly to dashboard URLs via `NEXT_PUBLIC_DASHBOARD_URL` env var

### Verification
- Build passes (login page: 5.21 kB)
- Puppeteer screenshots verified at 375px, 768px, and 1440px in both light and dark modes
- Pre-existing `/audit-logs` build error is unrelated to these changes

## Suggested Commit Message
```
feat: login page UX refinement -- frosted-glass overlay, dual-market copy, mobile responsiveness

- Add frosted-glass quiet zone (backdrop-blur-md) behind right panel text
- Refine copy for dual-sided market: neutral infrastructure positioning, C2PA standard badge
- Add outlined sign-up button for prominence
- Group passkey into OAuth row (Google | GitHub | Passkey)
- Match animation to marketing-site: dark navy gradient, forced dark theme particles
- Mobile fixes: icon-only OAuth buttons below sm:, right panel hidden below lg:
- Redirect marketing-site Sign In/Get Started to dashboard URLs
```

## Open Item
- Consider permanent 301 redirects from marketing-site /auth/* routes to dashboard (discussed but not implemented)
