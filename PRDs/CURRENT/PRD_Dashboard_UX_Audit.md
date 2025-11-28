# Dashboard UX/UI Audit

**Date:** November 28, 2025  
**Auditor:** AI Assistant  
**Scope:** API Keys page and overall dashboard design

---

## Executive Summary

The dashboard has a clean, functional foundation but needs refinement in visual hierarchy, readability, and component consistency. Key issues include low-contrast text, inconsistent spacing, and missing feedback states.

---

## 🔴 Critical Issues

### 1. Date/Time Readability
**Location:** API Key cards - "CREATED" field  
**Issue:** Raw ISO timestamp `2025-11-28T07:13:00.957065Z` is unreadable  
**Impact:** Users cannot quickly understand when keys were created  
**Fix:** Format as human-readable: "Nov 28, 2025 at 7:13 AM"

### 2. Low Contrast Text
**Location:** Muted foreground text (`#64748b` on `#f1f5f9`)  
**Issue:** Contrast ratio ~3.5:1, below WCAG AA (4.5:1) for body text  
**Impact:** Accessibility violation, hard to read for users with vision issues  
**Fix:** Darken muted-foreground to `#475569` (slate-600)

### 3. API Key Display Truncation
**Location:** Masked key display `ency_ueHzoLF...`  
**Issue:** Truncation with `...` makes it unclear how much of the key is shown  
**Impact:** Users unsure if they're seeing the full prefix  
**Fix:** Show consistent prefix length (e.g., first 16 chars) with clear indicator

---

## 🟡 Major Issues

### 4. Card Visual Hierarchy
**Location:** API Key cards  
**Issue:** All elements have similar visual weight  
**Impact:** Users can't quickly scan for important info  
**Fix:**
- Make key name larger/bolder
- Use subtle background for metadata section
- Add visual separator between key info and metadata

### 5. "New API Key" Banner Prominence
**Location:** Generated key success card  
**Issue:** Light blue border doesn't stand out enough for critical action  
**Impact:** Users might miss the one-time-only key display  
**Fix:**
- Add warning icon
- Use stronger background color
- Add countdown or emphasis animation

### 6. Button Hierarchy
**Location:** "Generate key" button  
**Issue:** Columbia Blue (#b7d5ed) is too light for primary CTA  
**Impact:** Button doesn't draw attention as the primary action  
**Fix:** Use Blue NCS (#2a87c4) for primary buttons, reserve Columbia Blue for secondary

### 7. Empty State Design
**Location:** When no API keys exist  
**Issue:** Plain text "You have not generated any API keys yet."  
**Impact:** Missed opportunity to guide users  
**Fix:** Add illustration, clearer CTA, and brief explanation of what API keys do

---

## 🟢 Minor Issues

### 8. Inconsistent Spacing
**Location:** Throughout dashboard  
**Issue:** Gap between header and content varies, card padding inconsistent  
**Fix:** Standardize to 8px grid system

### 9. Permission Tags
**Location:** "sign, verify, read" text  
**Issue:** Plain comma-separated text lacks visual distinction  
**Fix:** Use pill/badge components for each permission

### 10. Delete Button Placement
**Location:** Top-right of each card  
**Issue:** Destructive action is prominent but lacks confirmation  
**Fix:** Add confirmation dialog, consider moving to overflow menu

### 11. Mobile Navigation
**Location:** Header nav  
**Issue:** `hidden lg:flex` hides nav on mobile with no hamburger menu  
**Fix:** Add mobile menu drawer

### 12. Loading States
**Location:** Key list  
**Issue:** Plain text "Loading API keys…"  
**Fix:** Add skeleton loaders matching card layout

---

## Design System Gaps

### Missing Components
1. **Badge/Tag** - For permissions, status indicators
2. **Alert/Banner** - For important notices (like new key warning)
3. **Dialog/Modal** - For confirmations
4. **Skeleton** - For loading states
5. **Empty State** - Reusable empty state component
6. **Tooltip** - For additional context
7. **Dropdown Menu** - For overflow actions

### Color System Issues
1. **Primary button color** - Columbia Blue too light for CTAs
2. **Text hierarchy** - Need more distinct heading/body/caption colors
3. **Status colors** - Success/warning/error need consistent application

---

## Recommended Changes

### Phase 1: Quick Wins (1-2 hours)

- [ ] **1.1** Format dates with `date-fns` or `Intl.DateTimeFormat`
- [ ] **1.2** Increase muted-foreground contrast
- [ ] **1.3** Add permission badges
- [ ] **1.4** Add delete confirmation

### Phase 2: Component Updates (4-6 hours)

- [ ] **2.1** Create Badge component
- [ ] **2.2** Create Alert/Banner component  
- [ ] **2.3** Create Skeleton component
- [ ] **2.4** Create EmptyState component
- [ ] **2.5** Update Button primary color to Blue NCS

### Phase 3: UX Improvements (4-6 hours)

- [ ] **3.1** Redesign API Key card with better hierarchy
- [ ] **3.2** Enhance "New API Key" banner with urgency
- [ ] **3.3** Add mobile navigation
- [ ] **3.4** Improve empty states across all pages

---

## Visual Mockup Recommendations

### API Key Card (Improved)
```
┌─────────────────────────────────────────────────────────────┐
│  WordPress Production                              ⋮ Menu   │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ency_ueHzoLFYRn76vTU3KRb7081w...                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────┐ ┌────────┐ ┌──────┐                              │
│  │ sign │ │ verify │ │ read │   Permissions                │
│  └──────┘ └────────┘ └──────┘                              │
│                                                             │
│  Created: Nov 28, 2025        Last used: Never             │
└─────────────────────────────────────────────────────────────┘
```

### New Key Banner (Improved)
```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️  New API Key Created                                     │
│                                                             │
│ Copy this key now — you won't be able to see it again!     │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ ency_ueHzoLFYRn76vTU3KRb7081wd8DZC5ayZITJPRyvX_0    │ 📋 │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
│                                    [ Got it, I've copied ] │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| P0 | Date formatting | 30 min | High |
| P0 | Text contrast | 15 min | High |
| P1 | Permission badges | 1 hour | Medium |
| P1 | Delete confirmation | 1 hour | Medium |
| P1 | Primary button color | 30 min | High |
| P2 | New key banner | 2 hours | Medium |
| P2 | Empty states | 2 hours | Medium |
| P3 | Mobile nav | 3 hours | Medium |

---

## Next Steps

1. Start with P0 issues (date formatting, contrast)
2. Create Badge component in design system
3. Update Button primary variant color
4. Implement delete confirmation dialog
5. Redesign API key cards with improved hierarchy
