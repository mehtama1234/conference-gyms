# Repo Publication

## Current Local State

This directory is now a local Git repo for the gym analysis and production
readiness layer. It intentionally does not vendor the upstream benchmark repos
or heavyweight data.

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

No remote is configured yet. The likely repo name should be one of:

- `conference-gyms`
- `gyms`
- `conference-gym-readiness`

Once the remote exists, run:

```bash
git remote add origin git@github.com:mehtama1234/conference-gyms.git
git push -u origin main
```

If using HTTPS:

```bash
git remote add origin https://github.com/mehtama1234/conference-gyms.git
git push -u origin main
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
