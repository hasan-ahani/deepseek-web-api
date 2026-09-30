<div align="center">

# DeepSeek Web API

**A free, self-hosted LLM API that turns your own DeepSeek account into a drop-in OpenAI-compatible endpoint.**

No API key, no credits, no paid plan — just your normal [chat.deepseek.com](https://chat.deepseek.com) session, exposed as a REST API.

[![Build](https://github.com/hasan-ahani/deepseek-web-api/actions/workflows/build.yml/badge.svg)](https://github.com/hasan-ahani/deepseek-web-api/actions/workflows/build.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/hassanahani/deepseek-web-api)](https://hub.docker.com/r/hassanahani/deepseek-web-api)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

**English** · [فارسی](README.fa.md)

</div>

---

## Overview

This project bridges the consumer DeepSeek web app to standard APIs. You can use
it in two ways:

- 🐍 **As a Python library** — `client.chat("Hi")` for one-shot or multi-turn chats, with streaming.
- 🔌 **As an OpenAI-compatible server** — a local HTTP server that speaks the OpenAI protocol, so the official `openai` SDK and any OpenAI-compatible client work unchanged with `base_url=http://localhost:8000/v1`.

You sign in **once** in a browser; the session is cached and refreshed
automatically from then on.

> **Unofficial project.** Not affiliated with or endorsed by DeepSeek. It
> automates the consumer DeepSeek web experience for personal use. Use it
> responsibly and within DeepSeek's terms of service.

### Highlights

Everything you need to run it as a real, authenticated service:

| Feature | What it gives you |
| --- | --- |
| **API-key authentication** | Every `/v1` request must present `Authorization: Bearer <WEUI_AI_API_KEY>`; constant-time comparison, `401` otherwise (`server/security.py`). |
| **Docker image** | A headless container that serves the API, published for `linux/amd64` and `linux/arm64`. |
| **CI/CD** | GitHub Actions builds and pushes a multi-arch image to GHCR and Docker Hub on every push/tag (`.github/workflows/build.yml`). |
| **Session status endpoint** | `GET /v1/session/status` to report whether a usable DeepSeek session is live, for monitoring and health checks. |
| **Per-key rate limiting** | The sliding-window limiter buckets by API key (falling back to client IP) so one trusted caller shares a bucket (`server/api.py`). |
| **Session portability** | `scripts/push-session.sh` ships a freshly captured `session.json` to a remote host so a headless container can use it. |

---

## Table of contents

- [Why use this?](#why-use-this)
- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [Usage 1 — In Python (no server)](#usage-1--in-python-no-server)
- [Usage 2 — As an OpenAI-compatible server](#usage-2--as-an-openai-compatible-server)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Running in Docker](#running-in-docker)
- [Session lifecycle & headless deployments](#session-lifecycle--headless-deployments)
- [Human-check & proof-of-work (automatic)](#human-check--proof-of-work-automatic)
- [Models, DeepThink & web search](#models-deepthink--web-search)
- [Endpoints](#endpoints)
- [Concurrency](#concurrency)
- [Rate limiting](#rate-limiting)
- [CI/CD & container images](#cicd--container-images)
- [Project layout](#project-layout)
- [Notes & limitations](#notes--limitations)
- [License](#license)

---

## Why use this?

- **Free** — uses your normal signed-in DeepSeek account, no API billing.
- **Drop-in OpenAI replacement** — point any OpenAI client at `/v1` and it just works.
- **Full DeepSeek toolset** — pick the fast or expert model, and toggle DeepThink reasoning and web search per request.
- **Streaming + conversations** — token-by-token output and multi-turn threads addressed by `conversation_id`.
- **Deployable** — authenticated, rate-limited, Dockerized, and built for both x86_64 and arm64.

---

## Requirements

- **Python 3.9+**
- A **DeepSeek account** (the free one you use for [chat.deepseek.com](https://chat.deepseek.com))
- Works on Windows, macOS, and Linux
- Docker (optional, for the containerized deployment)

---

## Quickstart

```bash
# 1. Clone this repository
git clone https://github.com/hasan-ahani/deepseek-web-api.git
cd deepseek-web-api
```

**2. Create and activate a virtual environment**

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> On Windows you may need to allow script execution once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. In `cmd.exe` activate
> with `venv\Scripts\activate.bat` instead.

**3. Install dependencies and sign in**

```bash
# Install dependencies
pip install -r requirements.txt

# Install the browser Playwright needs (one-time)
playwright install chromium

# Sign in once: a browser opens, log into your DeepSeek account
python -m deepseek.auth
```

The login window opens so you can sign in by hand and solve the human-check once.
After that your session (bearer token + cookies) is saved under `session/`
(git-ignored, never shared) and reused on every run — the cached session is
refreshed automatically, so your first request works right away.

> The server can also open this window for you on demand the first time it needs
> a session (see `SERVER_INTERACTIVE_LOGIN`), so this step is optional for local
> single-user use.

**4. Start the server**

```bash
cp .env.example .env          # then set WEUI_AI_API_KEY to a strong secret
python app.py                 # -> http://127.0.0.1:8000
```

---

## Usage 1 — In Python (no server)

The simplest path if your code is already Python.

```python
from deepseek import DeepSeekClient

client = DeepSeekClient()                # loads your signed-in session

# Get a full reply
reply = client.chat("Say hello in one short sentence.")
print(reply.text)

# Continue the SAME conversation — pass the id back
reply2 = client.chat("And now in French?", conversation_id=reply.conversation_id)
print(reply2.text)

# Stream the answer as it's typed
for chunk in client.stream("Tell me a short joke"):
    print(chunk, end="", flush=True)
```

`chat()` returns the full text plus a `conversation_id`; pass that id back to
keep the thread going, or omit it to start fresh. `stream()` yields the reply
piece by piece.

👉 More: [`examples/01_direct_chat.py`](examples/01_direct_chat.py), [`02_direct_conversation.py`](examples/02_direct_conversation.py), [`03_direct_stream.py`](examples/03_direct_stream.py)

---

## Usage 2 — As an OpenAI-compatible server

Start a local server that speaks the OpenAI API, so existing OpenAI tools and
SDKs work unchanged.

```bash
python app.py
# -> DeepSeek OpenAI-compatible API on http://127.0.0.1:8000
```

Then point any OpenAI client at it. The API key is required once authentication
is enabled (see [Authentication](#authentication)):

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="your-secret")

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)
```

Or call it with plain HTTP / `curl`:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hello!"}]}'
```

> Change the bind address with env vars: `HOST=0.0.0.0 PORT=8080 python app.py`,
> or run `uvicorn server.api:app --host 0.0.0.0 --port 8080`.

👉 More: [`examples/04_server_http.py`](examples/04_server_http.py), [`examples/05_server_stream.py`](examples/05_server_stream.py), [`examples/06_server_openai_sdk.py`](examples/06_server_openai_sdk.py)

---

## Authentication

The deployed server is protected by a static bearer token. Every request under
`/v1` must send it:

```
Authorization: Bearer <WEUI_AI_API_KEY>
```

- Requests with a missing or wrong key get `401 Unauthorized`.
- Comparison is **constant-time** (`secrets.compare_digest`) to avoid leaking the
  key through timing (`server/security.py`).
- `/healthz` is intentionally left open so container health checks keep working.
- If `WEUI_AI_API_KEY` is unset, the server **refuses to start** — unless
  `WEUI_AI_ALLOW_UNAUTH=1` is set, an escape hatch intended for local
  development only.

Generate a strong secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Configuration

All settings are read from the environment (and `.env` via `python-dotenv`). See
[`.env.example`](.env.example) for the annotated template.

| Variable | Default | Purpose |
| --- | --- | --- |
| `WEUI_AI_API_KEY` | *(none)* | Bearer token required on every `/v1` request. Required to start unless `WEUI_AI_ALLOW_UNAUTH=1`. |
| `WEUI_AI_ALLOW_UNAUTH` | `0` | **Local dev only.** Allow `/v1` calls without a key. Never enable in production. |
| `HOST` | `127.0.0.1` | Bind address for `app.py`. |
| `PORT` | `8000` | Bind port for `app.py`. |
| `RATE_LIMIT_PER_MINUTE` | `30` | Accepted requests per minute, keyed by API key (or client IP). |
| `SERVER_INTERACTIVE_LOGIN` | `1` | When no session exists, open a visible browser to sign in. Set to `0` for headless deploys (returns `503` instead). |
| `SESSION_MAX_AGE` | `21600` | Seconds a saved `session.json` is trusted before a refresh is attempted (6 hours). |
| `DEEPSEEK_PROFILE_DIR` | `session/profile` | Reuse an existing signed-in Chrome profile. |
| `DEEPSEEK_BROWSER_ARGS` | *(none)* | Extra Chromium flags (e.g. `--no-sandbox --disable-dev-shm-usage`). |

```bash
RATE_LIMIT_PER_MINUTE=60 python app.py          # raise the rate limit
SERVER_INTERACTIVE_LOGIN=0 python app.py        # headless: no browser popup
```

---

## Running in Docker

A prebuilt multi-arch image is published to Docker Hub and GHCR:

```bash
docker pull hassanahani/deepseek-web-api:latest
# or: docker pull ghcr.io/hasan-ahani/deepseek-web-api:latest
```

The container serves the API **only** — it cannot create a session, because the
one-time human-check needs a real browser window (the container has no display).
Sign in on a desktop first, then hand the resulting `session.json` to the
container:

```bash
# 1. On your machine, with a browser: writes session/session.json
python -m deepseek.auth

# 2. Run the server with that session mounted
docker run --rm -it -p 8000:8000 \
  -v "$PWD/session:/app/session" \
  -e WEUI_AI_API_KEY=your-secret \
  hassanahani/deepseek-web-api:latest
```

Key details:

- `session.json` is the **only** portable artifact. The Chromium profile is not
  portable across operating systems (its cookies are encrypted with an
  OS-specific key), so only `session.json` is meant to be moved.
- Re-create and re-push `session.json` before `SESSION_MAX_AGE` expires — the
  container cannot refresh it headlessly, and once it expires the API returns
  `503 login_required`.
- The image runs as an unprivileged user (uid 1000), so the mounted session
  volume must be writable by that uid.
- Do **not** run `python -m deepseek.auth` inside the image; it fails with a
  "Missing X server or $DISPLAY" error by design.

Build the image yourself:

```bash
docker build -t deepseek-web-api:local .
```

---

## Session lifecycle & headless deployments

A DeepSeek session is a bearer token plus cookies captured from a signed-in
browser. The lifecycle is:

1. **First login (desktop):** `python -m deepseek.auth` opens a real browser so
   you can sign in and clear the human-check once.
2. **Cached reuse:** the captured session is stored in `session/session.json` and
   reused on every request.
3. **Headless refresh:** when possible, the token is re-captured from the saved
   Chrome profile without any window.
4. **Expiry:** if the session fully expires and no interactive login is allowed,
   the API returns `503 login_required`, telling you to re-run the login step.

For a remote/headless host, capture the session locally and copy it over. The
bundled helper does this (it deliberately never copies the browser profile):

```bash
# Copy session/session.json to a remote host and fix container ownership
SSH_HOST=user@host ./scripts/push-session.sh

# Optional overrides
REMOTE_DIR=/srv/deepseek/session LOCAL_FILE=./session/session.json \
  SSH_HOST=user@host ./scripts/push-session.sh
```

You can verify the live session at any time:

```bash
curl http://localhost:8000/v1/session/status
# {"status":"ok","session_age_seconds":42}
```

---

## Human-check & proof-of-work (automatic)

DeepSeek's chat sits behind two gates, both handled for you:

- **AWS WAF human-check:** access needs a signed-in browser session that has
  cleared the "verify you're human" check. `python -m deepseek.auth` opens a real
  browser so you can sign in and solve it once; the resulting token + cookies are
  cached under `session/` and reused on every request.
- **Proof-of-work:** every completion is gated by a PoW challenge. The bridge
  solves it by running DeepSeek's own `sha3_wasm_bg.wasm` module — the same one
  the browser loads — inside a `wasmtime` sandbox, so there's nothing to do on
  your end.

A cached session is reused for ~6 hours (`SESSION_MAX_AGE`) and refreshed
headlessly from your saved Chrome profile when possible; only a full expiry sends
you back to the browser.

---

## Models, DeepThink & web search

The `model` name selects **which model** answers. DeepThink and web search are
**not** models — they're orthogonal toggles you pass per request.

| Model | DeepSeek mode | Notes |
| --- | --- | --- |
| `deepseek-chat` | Instant | Fast default model |
| `deepseek-expert` | Expert | Stronger, slower |

Pass `thinking: true` (DeepThink reasoning) and/or `search: true` (web search) in
the request body — or via the OpenAI SDK's `extra_body`:

```python
resp = client.chat.completions.create(
    model="deepseek-expert",
    messages=[{"role": "user", "content": "What changed in the news today?"}],
    extra_body={"thinking": True, "search": True},
)
```

`conversation_id`, `thinking`, and `search` are non-OpenAI extras. A thread's
model is fixed at creation, so `model` can't be combined with `conversation_id`
on resume. Unknown model names return a `404` (no silent fallback). See
[`server/config.py`](server/config.py).

---

## Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/v1/chat/completions` | ✅ | Chat. Supports `"stream": true`, plus optional `"conversation_id"`, `"thinking"`, `"search"`. |
| `GET` | `/v1/models` | ✅ | Lists the available models. |
| `GET` | `/v1/session/status` | ✅ | Reports whether a usable DeepSeek session is available (`ok` / `login_required` / `error`). |
| `GET` | `/healthz` | ❌ | Liveness probe. Exempt from auth and rate limiting. |

---

## Concurrency

The server bridges a **single** signed-in DeepSeek account behind one shared
client. The PoW solver's `wasmtime` store isn't reentrant, so upstream calls are
**serialized**: parallel HTTP requests queue behind a lock and run one at a time
(see [`server/api.py`](server/api.py)). This is intentional — throughput is
sequential, not parallel. Keep concurrent in-flight requests low, and please
don't hammer your account.

---

## Rate limiting

On top of serialization, the bridge enforces a self-imposed rate limit with a
dependency-free sliding-window limiter
([`server/ratelimit.py`](server/ratelimit.py)): it caps accepted requests per API
key — falling back to the client IP when unauthenticated — and returns a standard
`429` + `Retry-After` when you exceed it. `/healthz` is exempt.

```bash
RATE_LIMIT_PER_MINUTE=60 python app.py   # raise it
```

**On the client side, use exponential backoff.** Transient `429`s clear if you
retry with growing delays (e.g. 1s, 2s, 4s). The official `openai` SDK does this
automatically and honours `Retry-After`; with plain HTTP, add a few retries
yourself.

---

## CI/CD & container images

[`.github/workflows/build.yml`](.github/workflows/build.yml) builds a
multi-platform image and publishes it to both registries:

- **GHCR:** `ghcr.io/hasan-ahani/deepseek-web-api`
- **Docker Hub:** `hassanahani/deepseek-web-api`

| Trigger | Tags |
| --- | --- |
| Push to `main` / `master` | `latest`, `<branch>`, `sha-<short>` |
| Push tag `v*.*.*` | `v1.2.3`, `1.2.3`, `1.2`, `1`, `sha-<short>` |
| Pull request | build only (no push) |
| Manual dispatch | build + push |

Images are built for `linux/amd64` **and** `linux/arm64` (arm64 via QEMU), so the
same manifest list runs on x86_64 servers and Apple Silicon machines. Builds are
provenance-attested and include an SBOM. Publishing requires the repository
secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`; GHCR uses the built-in
`GITHUB_TOKEN`.

---

## Project layout

| Path | What it does |
| --- | --- |
| [`deepseek/`](deepseek/) | Core library: `DeepSeekClient`, browser sign-in ([`auth.py`](deepseek/auth.py)), the HTTP driver ([`client.py`](deepseek/client.py)), and the PoW solver ([`pow.py`](deepseek/pow.py)). |
| [`server/`](server/) | The FastAPI OpenAI-compatible server: [`api.py`](server/api.py), [`config.py`](server/config.py), [`security.py`](server/security.py), [`ratelimit.py`](server/ratelimit.py), [`openai_format.py`](server/openai_format.py), [`schemas.py`](server/schemas.py). |
| [`examples/`](examples/) | Runnable examples for every feature ([`examples/README.md`](examples/README.md)). |
| [`scripts/`](scripts/) | Ops helpers, e.g. [`push-session.sh`](scripts/push-session.sh). |
| [`Dockerfile`](Dockerfile) | Headless container image. |
| [`.github/workflows/build.yml`](.github/workflows/build.yml) | Multi-arch build & push pipeline. |
| [`app.py`](app.py) | Starts the server. |

---

## Notes & limitations

- **Sign in once, then reuse.** The cached session refreshes automatically; you only re-sign-in if it fully expires.
- **Be reasonable.** Please use it in moderation, and don't spam or hammer it with automated bulk requests.
- **No real token counts.** `usage` in responses is a rough ~4-chars/token estimate.
- **Most OpenAI params are accepted but ignored** (`temperature`, `top_p`, `max_tokens`); only `model`, `messages`, `stream`, `conversation_id`, `thinking`, and `search` do anything.
- **Vision is deferred.** It needs image-upload plumbing that isn't built yet.
- **Your session is private.** Everything in `session/` (cookies + token) stays on your machine and is git-ignored.

---

## License

Released under the [MIT License](LICENSE). As this is an unofficial project, you
remain responsible for complying with DeepSeek's terms of service.
