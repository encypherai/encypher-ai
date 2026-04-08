# TEAM_299 - C2PA Knowledge Graph Generator

## Session Start
- **Date**: 2026-04-06
- **Repo**: https://github.com/encypherai/c2pa-knowledge-graph (standalone public repo)
- **Goal**: Build an open-source tool that programmatically generates versioned C2PA knowledge graphs from spec source, with MCP server interface

## Context
- C2PA specs-core repo cloned locally at /home/developer/specs-core/ (v2.4, 2026-04-01)
- 11 published spec versions (0.7 through 2.4, no 2.3)
- Existing machine-readable artifacts: 43 CDDL schemas, crJSON JSON Schema (49 defs), cert profile schemas, OpenAPI spec
- Gap filled: RDF/OWL ontology, JSON-LD context, machine-readable validation rules, MCP server for AI agents
- Stack: Python (UV), cddlparser, rdflib, jsonschema, mcp[cli], click

## Deliverables
- [x] PRD drafted at PRDs/CURRENT/PRD_C2PA_Knowledge_Graph_Generator.md
- [x] Full project implemented: 34 files, 6,360 lines
- [x] 136 tests passing
- [x] Public repo created and pushed

## Pipeline Output (v2.4)
- 148 entities, 203 relationships, 237 validation rules
- 37 enum types, 114 status codes
- ontology.ttl: 364 KB, context.jsonld: 130 KB, validation-rules.json: 145 KB

## Architecture
```
specs-core -> CDDL parser + JSON Schema parser + AsciiDoc parser
  -> IR builder (merge + relationship inference)
    -> Turtle emitter (ontology.ttl)
    -> JSON-LD emitter (context.jsonld)
    -> Rules emitter (validation-rules.json)
    -> Changelog emitter (version diffs)
  -> MCP server (resources + tools for AI agents)
  -> CLI (generate, generate-all, serve, diff, list-versions)
```

## Known Upstream Issue
C2PA schema URLs return 404:
- `https://c2pa.org/crjson/crJSON.schema.json`
- `https://c2pa.org/crjson/` (@vocab)
- `https://c2pa.org/schemas/decentralized-lookup.schema.json`
- `https://c2pa.org/schemas/repository-receipt.json`

Schemas exist in the GitHub repo and downloadable ZIP, but are not served at declared addresses. Should be raised at next C2PA working group call.

## Handoff Notes
Project is complete and public. Next steps:
1. Generate artifacts for all 11 spec versions and tag the output repo
2. Publish to PyPI as `c2pa-knowledge-graph`
3. Add GitHub Actions CI workflow
4. Raise the 404 schema URL issue at C2PA working group
5. Consider contributing to c2pa-org namespace once established

## Suggested Commit Message
```
feat: C2PA Knowledge Graph generator - initial release

Open-source tool that parses C2PA spec source (CDDL, JSON Schema,
AsciiDoc) and generates versioned RDF/OWL ontology, JSON-LD context,
and validation rules. MCP server for AI agent consumption.

- 148 entities, 203 relationships, 237 rules from v2.4 spec
- Covers all 11 published spec versions (0.7 through 2.4)
- 136 tests passing
- Apache 2.0 license
- Repo: https://github.com/encypherai/c2pa-knowledge-graph
```
