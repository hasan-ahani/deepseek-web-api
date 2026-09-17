#!/usr/bin/env bash
#
# Push a freshly captured DeepSeek session to the server so the container can
# use it. Only session.json is portable across OSes — the Chrome profile is not
# (cookies are encrypted with an OS-specific key), so we deliberately never copy
# session/profile.
#
# Usage:
#   SSH_HOST=root@1.2.3.4 ./scripts/push-session.sh
#
# Optional:
#   REMOTE_DIR   remote session dir (default /home/hassan/weui/deepseek-session)
#   LOCAL_FILE   local session.json (default ../session/session.json)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_FILE="${LOCAL_FILE:-$SCRIPT_DIR/../session/session.json}"
REMOTE_DIR="${REMOTE_DIR:-/home/hassan/weui/deepseek-session}"
SSH_HOST="${SSH_HOST:-}"

if [ -z "$SSH_HOST" ]; then
    echo "error: SSH_HOST is not set (e.g. SSH_HOST=root@1.2.3.4 $0)" >&2
    exit 1
fi

if [ ! -f "$LOCAL_FILE" ]; then
    echo "error: $LOCAL_FILE not found. Run first:  python -m deepseek.auth" >&2
    exit 1
fi

echo "==> Ensuring $REMOTE_DIR exists on $SSH_HOST"
ssh "$SSH_HOST" "mkdir -p '$REMOTE_DIR'"

echo "==> Copying session.json"
rsync -av "$LOCAL_FILE" "$SSH_HOST:$REMOTE_DIR/session.json"

echo "==> Fixing ownership (container runs as uid 1000)"
ssh "$SSH_HOST" "chown -R 1000:1000 '$REMOTE_DIR' && chmod 700 '$REMOTE_DIR' && chmod 600 '$REMOTE_DIR/session.json'"

echo "Done. Restart the service to pick it up:"
echo "    docker compose -f docker-compose.yml -f docker-compose.prod.yml restart deepseek-web"
