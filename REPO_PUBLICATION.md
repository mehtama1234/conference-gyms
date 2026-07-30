# Repo Publication

## Current Published State

This directory is now a local Git repo for the gym analysis and production
readiness layer, pushed to:

```text
https://github.com/mehtama1234/conference-gyms
```

It intentionally does not vendor the upstream benchmark repos or heavyweight
data.

Tracked scope:

- top-level analysis docs
- production readiness status
- lane receipts under `lanes/`
- validators and replay wrappers under `scripts/`
- CI workflow for non-heavy validation

Ignored scope:

- cloned upstream benchmark repos
- `.cache/` downloads and extracted task data
- Docker/server/runtime outputs
- generated Python cache files

## Push Target

The local `origin` remote is configured as:

```text
https://github.com/mehtama1234/conference-gyms.git
```

`main` tracks `origin/main`.

Check publication readiness:

```bash
make publication-check
```

## CI Gate

The tracked GitHub Actions workflow runs only non-heavy checks:

```bash
make validate
```

It does not download TerminalTraj task archives, pull Docker images, start
containers, download CyberGym server data, or run heavy benchmark tasks.

The TerminalTraj replay remains available locally:

```bash
make replay-terminaltraj
```
