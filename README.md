# Chronicle Documentation

Chronicle is a software evolution intelligence platform that reconstructs how software projects change over time from development activity and evidence.

## Documentation map

### Product

- `product.md` — product goals, scope, V1 requirements, and non-goals

### Architecture

- `architecture.md` — system architecture, module boundaries, data flow, and technical principles

### Domain

- `domain-model.md` — entities, relationships, invariants, and domain vocabulary

### API

- `API.md` — Phase 1 REST API contract

### Architecture decisions

- `decisions/0001-modular-monolith.md`
- `decisions/0002-postgresql.md`
- `decisions/0003-raw-and-normalized-events.md`

## Phase coverage

These documents cover the initial product specification and the foundation needed to begin implementation.

The first coding milestone is:

```text
Django + DRF + PostgreSQL
        |
        v
Authentication
        |
        v
Workspace
        |
        v
Project
        |
        v
GitHub source registration
```

Then the next milestone will add the first complete ingestion vertical slice:

```text
GitHub webhook
    -> raw event
    -> normalized event
    -> project timeline
```
