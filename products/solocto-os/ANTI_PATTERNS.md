# 🛡️ Anti-Patterns Registry — AI Immune System

> AI MUST check this file BEFORE executing commands, SSH, deploy, or writing critical code.
> Every production mistake gets recorded here. Never repeat the same error twice.

---

## How It Works

1. You (or AI) make a mistake in production
2. Document it here with the pattern code
3. AI reads this file before risky operations
4. The mistake never happens again

## Pattern Codes
- `PY-XXX` — Python code anti-patterns
- `SRV-XXX` — Server/infrastructure anti-patterns
- `PROC-XXX` — Process/workflow anti-patterns
- `SEC-XXX` — Security anti-patterns
- `DEPLOY-XXX` — Deployment anti-patterns

---

## Python Anti-Patterns

### PY-001: datetime.now() vs datetime.utcnow()
- **Wrong:** `datetime.now()` — gives local timezone, breaks in Docker/servers
- **Right:** `datetime.now(timezone.utc)` or `datetime.utcnow()`
- **Context:** Timestamps in databases, logs, cron jobs

### PY-002: f-string in logging
- **Wrong:** `logger.info(f"User {user_id} logged in")` — string always computed
- **Right:** `logger.info("User %s logged in", user_id)` — lazy evaluation
- **Context:** High-frequency logging, performance-critical paths

### PY-003: asyncio.sleep(0) for yield
- **Wrong:** Blocking the event loop with CPU-heavy sync code
- **Right:** `await asyncio.sleep(0)` to yield control, or use `run_in_executor`
- **Context:** Long-running async handlers

### PY-004: Mutable default arguments
- **Wrong:** `def foo(items=[]): items.append(1)`
- **Right:** `def foo(items=None): items = items or []`
- **Context:** Function defaults persist between calls

### PY-005: Bare except
- **Wrong:** `except:` or `except Exception:` catching everything
- **Right:** `except SpecificError:` — catch only what you expect
- **Context:** Silent failures, hidden bugs

---

## Server Anti-Patterns

### SRV-001: SSH to wrong server
- **Wrong:** `ssh root@some-ip` — mixing up server IPs
- **Right:** Keep a server table. Always verify IP before SSH.
- **Context:** Multiple VPS instances with similar configs
- **Your servers:**
  | Name | IP | Port | Role |
  |------|----|------|------|
  | Production | [YOUR_IP] | 2222 | Main |
  | Backup | [YOUR_IP] | 22 | Secondary |

### SRV-002: No log rotation → disk full
- **Wrong:** Never configuring log rotation
- **Right:** `logrotate` config, or app-level log size limits
- **Context:** Long-running services, access logs, x-ui panels

### SRV-003: Forgot chmod/chown after deploy
- **Wrong:** `scp file server:path` → service can't read it
- **Right:** Always `chmod 644` / `chown www-data:www-data` after file transfers
- **Context:** Python services, web servers, systemd units

### SRV-004: Editing .env via sed through SSH
- **Wrong:** `ssh server "sed -i 's/old/new/' .env"` — quoting hell in PowerShell
- **Right:** Create a Python script that edits .env remotely
- **Context:** PowerShell → SSH → sed escaping is a guaranteed footgun

### SRV-005: Restarting service without checking config
- **Wrong:** `systemctl restart myservice` after config change
- **Right:** `cat /path/to/config` → verify → `systemctl restart` → `journalctl -u myservice -f`
- **Context:** One typo in config = service won't start

---

## Process Anti-Patterns

### PROC-001: Deploying without CHANGELOG update
- **Wrong:** Push to production, forget to update CHANGELOG
- **Right:** CHANGELOG is part of the deploy checklist. No update = no deploy.

### PROC-002: Large uncommitted changes
- **Wrong:** 10+ files changed, no commits
- **Right:** Commit every 3-5 files. Meaningful commit messages.

### PROC-003: Skipping pre-deploy review for "small" changes
- **Wrong:** "It's just a CSS change" → breaks production
- **Right:** Code Complexity Levels. Even Level 1 gets a quick scan.

### PROC-004: No monitoring after deploy
- **Wrong:** Deploy → close terminal → sleep
- **Right:** Deploy → watch logs for 5 min → check health endpoint → then relax

---

## Security Anti-Patterns

### SEC-001: Secrets in code/markdown
- **Wrong:** API keys, passwords in .py, .md, or commit history
- **Right:** `.env` only. `.env` in `.gitignore`. Always.

### SEC-002: Default credentials in production
- **Wrong:** admin/admin, test/test, panel default passwords
- **Right:** Change ALL default credentials before going live

---

## Deployment Anti-Patterns

### DEPLOY-001: No rollback plan
- **Wrong:** "If it breaks we'll figure it out"
- **Right:** Always have a backup: `cp app.py app.py.bak` before overwrite

### DEPLOY-002: Deploying on Friday evening
- **Wrong:** Push to prod at 11 PM Friday
- **Right:** Deploy Monday-Thursday. Fridays = code freeze.

---

> **Rule:** When you discover a new anti-pattern, add it IMMEDIATELY with the next available code.
> This file is your team's immune system. It only gets stronger.
