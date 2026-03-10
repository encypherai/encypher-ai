# D2 Diagrams

This directory is the canonical home for repo-wide D2 diagram sources.

## Goals

- Keep architecture and workflow diagrams source-controlled and diffable.
- Place diagrams close to the docs sections they explain.
- Use D2 source as the single source of truth for rendered artifacts.
- Prefer static SVG output for engineering docs and reserve motion for high-value walkthroughs only.

## Directory Structure

```text
docs/diagrams/
├── README.md
├── architecture/
│   ├── system-context.d2
│   ├── microservices-topology.d2
│   └── enterprise-vs-core.d2
└── workflows/
    ├── enterprise-api-sign-verify.d2
    ├── dashboard-extension-auth-handoff.d2
    └── sdk-generation-pipeline.d2
```

Integration-specific diagrams should live next to the owning integration docs when they explain a local workflow:

- `apps/dashboard/docs/diagrams/*.d2`
- `integrations/chrome-extension/docs/*.d2`
- `integrations/wordpress-provenance-plugin/docs/*.d2`

## Style Rules

- One diagram should answer one primary question.
- Prefer smaller focused diagrams over one large poster.
- Label arrows with the action or payload they represent.
- Use consistent visual zones:
  - Client surfaces
  - Integrations/browser/plugin surfaces
  - Backend/services
  - Storage/external systems
- Use solid arrows for synchronous request/response flows.
- Use dashed arrows for async events, polling, webhooks, or background processing.

## Rendering

Use the repo render/check script:

```bash
./scripts/render-d2-diagrams.sh --check
./scripts/render-d2-diagrams.sh
```

`--check` validates discovery and output paths without requiring the `d2` CLI. A normal render requires `d2` to be installed locally.

## Animation Guidance

Animation is optional and should only be used when motion improves understanding.

Recommended patterns:

- Step-by-step storyboard variants for multi-stage workflows
- Light SVG/CSS emphasis in a docs site wrapper
- HTML walkthroughs for product demos

Avoid decorative looping animation in engineering READMEs.

## Maintenance Rules

- Update the relevant D2 source in the same PR as the workflow or architecture change.
- Keep README links pointed at the diagram source and any rendered output when available.
- Do not duplicate SSOT tier logic or API contract details inside diagrams when those already live elsewhere.
