# HA Automation MCP (experimental)

Home Assistant OS app providing MCP tools to manage automations. **Not production-ready.**

## Important

- Do not expose port 8765 directly to the internet.
- An authenticated TLS reverse proxy and a ChatGPT connector with compatible authentication are required.
- Never commit tokens, certificates or private configuration to GitHub.
- Uses Home Assistant's `/api/config/automation/config/{id}` endpoints; these are not part of the stable public REST API and must be tested on your Home Assistant version.
- The tool-level `confirm` flag is not a substitute for server-side authorization or a trusted confirmation workflow.

## Layout

`repository.yaml` describes the app repository; `ha_automation_mcp/` contains the app.

## Status

Source package only. Installation, build, authentication, API compatibility and reverse-proxy integration have **not yet been verified** on the target Home Assistant host.
