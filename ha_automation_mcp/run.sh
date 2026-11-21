#!/bin/sh
set -eu
export MCP_ACCESS_TOKEN="$(python3 -c 'import json; print(json.load(open("/data/options.json"))["access_token"])')"
if [ -z "$MCP_ACCESS_TOKEN" ]; then
  echo "Configure a strong access_token before starting" >&2
  exit 1
fi
exec python3 /app/server.py
