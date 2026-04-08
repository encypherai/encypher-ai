# PRD: C2PA Knowledge Graph Generator

## Status: PLANNING

## Current Goal
Design and build an open-source, programmatically triggerable tool that generates a versioned RDF/OWL knowledge graph from C2PA specification source files, with an optional MCP server interface for AI agent consumption.

## Overview
The C2PA specification publishes 43 CDDL schemas, a 49-definition JSON Schema (crJSON), and prose validation rules, but no machine-readable ontology that captures entity relationships, validation logic, or version diffs. AI agents implementing C2PA today work from prose text, which produces hallucinated validation rules and missed version-specific changes. This tool parses the spec source for any given version, extracts structured entities and relationships, and emits a versioned RDF/OWL ontology plus JSON-LD context document. An MCP server mode lets AI agents query the graph directly.

## Objectives
- Parse C2PA spec source (CDDL schemas, JSON Schema, AsciiDoc prose) into structured intermediate representation
- Generate RDF/OWL ontology (Turtle format) covering all C2PA entity types, relationships, and constraints
- Generate JSON-LD context document for each spec version
- Extract machine-readable validation rules from normative prose sections
- Version output artifacts to match spec release tags (0.5 through 2.4, no 2.3)
- Serve knowledge graph via MCP server for AI agent consumption
- Open-source under Apache 2.0

## Known Issues to Address

### C2PA Schema URL 404s (upstream bug)
The crJSON schema declares `$id: https://c2pa.org/crjson/crJSON.schema.json` but that URL returns 404. The `@vocab` URI `https://c2pa.org/crjson/` also 404s. The decentralized-lookup schema (`https://c2pa.org/schemas/decentralized-lookup.schema.json`) and repository-receipt schema (`https://c2pa.org/schemas/repository-receipt.json`) are similarly unreachable. All schemas exist in the GitHub repo and the downloadable ZIP at `spec.c2pa.org`, but are not served at their declared addresses. This should be raised at the next C2PA working group call as a straightforward fix: serve the schemas at the URLs they already declare.

## Architecture

### Input Sources (per spec version)
| Source | Path in specs-core | Format | Content |
|--------|-------------------|--------|---------|
| CDDL schemas | `docs/modules/specs/partials/schemas/cddl/*.cddl` | RFC 8610 CDDL | 43 files, all CBOR data structures |
| crJSON schema | `docs/modules/crJSON/partials/crJSON.schema.json` | JSON Schema 2020-12 | 49 definitions, manifest through validation |
| Assertion specs | `docs/modules/specs/partials/Standard_Assertions/*.adoc` | AsciiDoc | 29 assertion type definitions |
| Architecture docs | `docs/modules/specs/partials/Architecture/*.adoc` | AsciiDoc | Claims, manifests, entities, versioning |
| Validation rules | `docs/modules/specs/partials/Validation/*.adoc` | AsciiDoc | Normative validation algorithms |
| Trust model | `docs/modules/specs/partials/Trust_Model/*.adoc` | AsciiDoc | Trust anchors, cert profiles, revocation |
| Cert profile schemas | conformance repo `docs/schemas/cert-profiles/*.json` | JSON Schema 2020-12 | X.509 certificate validation |
| URN grammar | `docs/modules/specs/partials/schemas/c2pa_urn.abnf` | ABNF | URN identifier syntax |

### Output Artifacts (per spec version)
| Artifact | Format | Description |
|----------|--------|-------------|
| `ontology.ttl` | Turtle (RDF/OWL) | Full entity/relationship ontology |
| `context.jsonld` | JSON-LD | `@context` document for C2PA terms |
| `validation-rules.json` | JSON | Machine-readable validation rule set |
| `changelog.json` | JSON | Structured diff from previous version |
| `metadata.json` | JSON | Version, date, source commit hash, entity counts |

### Pipeline Architecture
```
specs-core repo (git checkout by tag)
        |
        v
  +------------------+
  | 1. CDDL Parser   |  cddlparser -> typed AST
  +------------------+
        |
        v
  +------------------+
  | 2. JSON Schema   |  jsonschema + jsonschema-path -> definition map
  |    Parser        |
  +------------------+
        |
        v
  +------------------+
  | 3. AsciiDoc      |  Extract normative sections (validation, trust model)
  |    Extractor     |  Identify RFC 2119 keywords (MUST/SHALL/SHOULD)
  +------------------+
        |
        v
  +------------------+
  | 4. IR Builder    |  Merge all sources into intermediate representation
  |                  |  Entity types, properties, relationships, constraints
  +------------------+
        |
        v
  +-----+------+-----+---------+
  |            |           |            |
  v            v           v            v
Turtle     JSON-LD     Rules JSON   Changelog
emitter    context     emitter      diff engine
```

### MCP Server Interface
The MCP server exposes the knowledge graph as queryable resources and tools:

**Resources:**
- `c2pa://versions` - list all available spec versions
- `c2pa://{version}/ontology` - full ontology for a version
- `c2pa://{version}/entities` - list all entity types
- `c2pa://{version}/entity/{name}` - single entity definition with relationships
- `c2pa://{version}/validation-rules` - all validation rules
- `c2pa://{version}/changelog` - diff from previous version

**Tools:**
- `query_entity(version, name)` - get entity definition, properties, relationships
- `query_relationship(version, from, to)` - get relationship between two entities
- `query_validation_rule(version, context)` - find validation rules for a given context
- `diff_versions(from_version, to_version)` - structured diff between any two versions
- `search(version, query)` - full-text search across entity definitions and rules

### Versioning Strategy
- Git tags in the output repo match C2PA spec tags exactly (bare numbers: `2.4`, `2.2`, `2.1`, etc.)
- Each tag contains the generated artifacts for that spec version
- The `main` branch always contains artifacts for the latest stable spec version
- A `versions/` directory on main contains all versions for easy browsing
- CI regenerates artifacts when the generator code changes (ensures reproducibility)

## Tech Stack
| Component | Package | Version | Role |
|-----------|---------|---------|------|
| CDDL parsing | `cddlparser` | 0.6.0 | Parse CDDL schemas to typed AST |
| JSON Schema | `jsonschema` + `jsonschema-path` | 4.26.0 / 0.4.5 | Traverse crJSON schema definitions |
| RDF/OWL output | `rdflib` | 7.6.0 | Generate Turtle and JSON-LD |
| MCP server | `mcp[cli]` | 1.27.0 | Serve KG to AI agents |
| CLI framework | `click` | - | CLI interface for generation |
| Testing | `pytest` | - | Unit and integration tests |

## Tasks

### 1.0 Project Setup
- [ ] 1.1 Create `tools/c2pa-knowledge-graph/` directory with `pyproject.toml`
- [ ] 1.2 Add to UV workspace members in root `pyproject.toml`
- [ ] 1.3 Add dependencies: `cddlparser`, `rdflib`, `jsonschema`, `jsonschema-path`, `click`, `mcp[cli]`
- [ ] 1.4 Create CLI entry point (`c2pa-kg`) with `generate` and `serve` commands
- [ ] 1.5 Write project README with usage examples

### 2.0 CDDL Schema Parser
- [ ] 2.1 Write CDDL-to-IR parser that walks `cddlparser` AST
- [ ] 2.2 Map CDDL `map` rules to entity classes
- [ ] 2.3 Map CDDL `group` choices to union types
- [ ] 2.4 Extract property names, types, cardinality, and constraints
- [ ] 2.5 Handle cross-file references (e.g., claim.cddl referencing hashed-uri.cddl)
- [ ] 2.6 Tests: parse all 43 CDDL files from spec v2.4, verify entity count and relationships

### 3.0 JSON Schema Parser
- [ ] 3.1 Write JSON Schema-to-IR parser for crJSON definitions
- [ ] 3.2 Walk `$ref` chains to resolve cross-definition references
- [ ] 3.3 Extract property metadata (types, enums, descriptions, required fields)
- [ ] 3.4 Merge JSON Schema entities with CDDL entities (CDDL is normative, JSON Schema supplements)
- [ ] 3.5 Tests: parse crJSON schema, verify all 49 definitions mapped

### 4.0 AsciiDoc Extractor
- [ ] 4.1 Parse AsciiDoc section structure from validation and trust model files
- [ ] 4.2 Extract normative statements (RFC 2119 keywords: MUST, SHALL, SHOULD, etc.)
- [ ] 4.3 Link normative statements to entities they reference
- [ ] 4.4 Build validation rule IR (condition, action, severity, referenced entities)
- [ ] 4.5 Tests: extract rules from Validation section, verify rule count and entity linkage

### 5.0 Intermediate Representation
- [ ] 5.1 Define IR schema (entity types, properties, relationships, constraints, rules)
- [ ] 5.2 Build IR merger that combines CDDL, JSON Schema, and AsciiDoc sources
- [ ] 5.3 Resolve entity name conflicts and cross-source references
- [ ] 5.4 Add relationship inference (e.g., manifest -> claim -> assertion -> ingredient)
- [ ] 5.5 Tests: build complete IR for v2.4, verify entity graph connectivity

### 6.0 RDF/OWL Ontology Generator
- [ ] 6.1 Define C2PA OWL namespace and class hierarchy
- [ ] 6.2 Map IR entities to `owl:Class` definitions
- [ ] 6.3 Map IR properties to `owl:ObjectProperty` and `owl:DatatypeProperty`
- [ ] 6.4 Map IR relationships to RDF triples
- [ ] 6.5 Map IR constraints to OWL restrictions (`owl:Restriction`, cardinality)
- [ ] 6.6 Serialize to Turtle format via `rdflib`
- [ ] 6.7 Tests: validate generated Turtle syntax, verify class and property counts

### 7.0 JSON-LD Context Generator
- [ ] 7.1 Generate `@context` document from ontology namespace
- [ ] 7.2 Map all C2PA terms to their ontology IRIs
- [ ] 7.3 Include type coercion for known datatypes
- [ ] 7.4 Tests: validate JSON-LD context resolves all terms in crJSON examples

### 8.0 Validation Rules Emitter
- [ ] 8.1 Serialize IR validation rules to structured JSON format
- [ ] 8.2 Include rule ID, description, condition, severity, referenced entities
- [ ] 8.3 Group rules by validation phase (structural, cryptographic, trust)
- [ ] 8.4 Tests: verify all extracted rules serialize and round-trip

### 9.0 Version Management and Diff Engine
- [ ] 9.1 Implement spec version checkout (git checkout by tag from specs-core)
- [ ] 9.2 Build version registry (all known spec tags, dates, commit hashes)
- [ ] 9.3 Implement structured diff engine (added/removed/modified entities, properties, rules)
- [ ] 9.4 Generate changelog.json between consecutive versions
- [ ] 9.5 Tests: generate KG for v2.2 and v2.4, verify diff captures known changes

### 10.0 MCP Server
- [ ] 10.1 Implement MCP server with resource endpoints (versions, ontology, entities, rules)
- [ ] 10.2 Implement query tools (query_entity, query_relationship, search)
- [ ] 10.3 Implement diff_versions tool
- [ ] 10.4 Add server configuration (port, spec-source path, default version)
- [ ] 10.5 Add MCP entry to `.mcp.json` for local development
- [ ] 10.6 Tests: integration tests for all MCP resources and tools

### 11.0 CLI and CI
- [ ] 11.1 Implement `c2pa-kg generate` command (version, output-dir, format options)
- [ ] 11.2 Implement `c2pa-kg serve` command (start MCP server)
- [ ] 11.3 Implement `c2pa-kg diff` command (compare two versions)
- [ ] 11.4 Implement `c2pa-kg list-versions` command
- [ ] 11.5 Add GitHub Actions workflow: regenerate on push, validate output
- [ ] 11.6 Tests: CLI smoke tests for all commands

### 12.0 Open Source Packaging
- [ ] 12.1 Add Apache 2.0 LICENSE
- [ ] 12.2 Write comprehensive README (motivation, quickstart, MCP setup, API reference)
- [ ] 12.3 Add CONTRIBUTING.md
- [ ] 12.4 Publish to PyPI as `c2pa-knowledge-graph`
- [ ] 12.5 Create separate GitHub repo (c2pa-org or encypher namespace TBD)
- [ ] 12.6 Generate and tag artifacts for all published spec versions (0.7 through 2.4)

## Success Criteria
- Generator produces valid Turtle ontology for all published spec versions (0.7+)
- JSON-LD context document resolves all C2PA terms used in crJSON examples
- Validation rules JSON covers all normative MUST/SHALL statements from the Validation section
- Version diff accurately captures entity additions, removals, and modifications between consecutive versions
- MCP server responds to all defined resources and tools
- Full generation pipeline runs in under 60 seconds per spec version
- All tests pass (`uv run pytest`)
- Published to PyPI, installable via `uv add c2pa-knowledge-graph`

## Completion Notes
(to be filled on completion)
