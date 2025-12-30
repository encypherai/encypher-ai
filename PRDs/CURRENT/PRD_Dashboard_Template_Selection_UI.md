# Dashboard UI for Template Selection

**Status:** ✅ Complete
**Current Goal:** Implement template selection UI in dashboard for signing workflow.
**Related PRD:** `PRDs/CURRENT/PRD_Enterprise_Rights_Metadata_AI_Licensing.md` (Task 3.3 deferred to Phase 2)

## Overview

Publishers need a user-friendly way to select C2PA assertion templates when signing content. This PRD covers the dashboard UI components that allow users to browse available templates, set organization defaults, and select templates during the signing workflow.

## Objectives

- Provide a template browser UI showing built-in and custom templates
- Allow template selection in the signing playground
- Enable setting organization default template (Business+ tier)
- Surface template details (name, description, category, assertions)

## API Dependencies

The following Enterprise API endpoints are already implemented:

| Endpoint | Method | Tier | Description |
|----------|--------|------|-------------|
| `/api/v1/enterprise/c2pa/templates` | GET | Business+ | List available templates (built-in + custom) |
| `/api/v1/enterprise/c2pa/templates/{id}` | GET | Business+ | Get template details |
| `/api/v1/enterprise/c2pa/templates` | POST | Enterprise | Create custom template |
| `/api/v1/enterprise/c2pa/templates/{id}` | PUT | Enterprise | Update custom template |
| `/api/v1/enterprise/c2pa/templates/{id}` | DELETE | Enterprise | Delete custom template |

## Tasks

### 1.0 API Client Integration

- [x] 1.1 Add template API methods to `apps/dashboard/src/lib/api.ts` — ✅ TEAM_044
  - [x] 1.1.1 `getC2PATemplates()` — list templates
  - [x] 1.1.2 `getC2PATemplate(id)` — get single template
- [x] 1.2 Add TypeScript types for template responses (`C2PATemplate`, `C2PATemplateListResponse`)

### 2.0 Template Browser Component

- [x] 2.1 Create `TemplateSelector` component — ✅ TEAM_044
  - [x] 2.1.1 Dropdown view of available templates grouped by category
  - [x] 2.1.2 Category badges (news, legal, academic, publisher)
  - [x] 2.1.3 Template name, description display
  - [x] 2.1.4 Selection state management via props
- [ ] 2.2 Create `TemplateDetailModal` component (deferred — not critical for MVP)

### 3.0 Playground Integration

- [x] 3.1 Add template selector to `/playground` page — ✅ TEAM_044
  - [x] 3.1.1 Template dropdown in sign form
  - [x] 3.1.2 Pass `template_id` to `/sign` API call via request body
  - [x] 3.1.3 Show selected template in request body preview

### 4.0 Settings Integration (Optional - Business+)

- [ ] 4.1 Add "Default Template" section to organization settings (deferred to future sprint)

### 5.0 Testing & Verification

- [x] 5.1 TypeScript compilation verified — ✅ `npx tsc --noEmit`
- [x] 5.2 Tier gating handled (API returns error for non-Business+ users)

## Success Criteria

- Users can browse and select templates in the playground
- Template selection is passed to the `/sign` API
- UI gracefully handles tier restrictions
- Built-in templates are always visible

## Technical Notes

### Built-in Templates (from `c2pa_builtin_templates.py`)

| Template ID | Name | Category |
|-------------|------|----------|
| `tmpl_builtin_cc_by_4_0_v1` | CC-BY 4.0 | publisher |
| `tmpl_builtin_cc_by_nc_4_0_v1` | CC-BY-NC 4.0 | publisher |
| `tmpl_builtin_all_rights_reserved_v1` | All Rights Reserved | publisher |
| `tmpl_builtin_academic_open_access_v1` | Academic Open Access | academic |
| `tmpl_builtin_news_wire_syndication_v1` | News Wire Syndication | news |

### API Response Schema

```typescript
interface C2PATemplate {
  id: string;
  name: string;
  description: string | null;
  schema_id: string;
  template_data: Record<string, any>;
  category: string | null;
  organization_id: string;
  is_default: boolean;
  is_active: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

interface C2PATemplateListResponse {
  templates: C2PATemplate[];
  total: number;
  page: number;
  page_size: number;
}
```
