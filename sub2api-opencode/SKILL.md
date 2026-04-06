---
name: sub2api-opencode
description: Configure Sub2API as a provider in OpenCode. Use when setting up sub2api proxy, configuring antigravity endpoints, or connecting Claude/Gemini models through sub2api gateway in opencode.json. Handles provider setup, model registration, endpoint routing, and troubleshooting 404 errors.
---

# Sub2API OpenCode Configuration Guide

Configure [Sub2API](https://github.com/Wei-Shaw/sub2api) as an AI provider in [OpenCode](https://opencode.ai).

Sub2API is an open-source AI API Gateway (6K+ stars) that converts Antigravity, Claude, OpenAI, and Gemini subscriptions into unified API endpoints. It supports multi-account management, smart scheduling, sticky sessions, token-level billing, and concurrency control.

**Official domains:** `sub2api.org` and `pincc.ai`. Other sites using the Sub2API name may be third-party deployments.

---

## Critical Knowledge

### Sub2API Endpoint Architecture

Sub2API exposes **different endpoints for different model families and protocols**:

| Endpoint Path | Protocol | Model Family | SDK to Use |
|---|---|---|---|
| `/antigravity/v1/messages` | Anthropic Messages API | Claude (via Antigravity) | `@ai-sdk/anthropic` |
| `/antigravity/v1beta/` | Google Generative AI API | Gemini (via Antigravity) | `@ai-sdk/google-generative-ai` |
| `/v1/messages` | Anthropic Messages API | Claude (direct/hybrid) | `@ai-sdk/anthropic` |
| `/v1beta/` | Google Generative AI API | Gemini (direct/hybrid) | `@ai-sdk/google-generative-ai` |
| `/v1/chat/completions` | OpenAI Chat Completions | OpenAI models | `@ai-sdk/openai-compatible` |

### The #1 Mistake: Wrong SDK

**NEVER use `@ai-sdk/openai-compatible` for Claude or Gemini models on Sub2API.** It sends requests to `/chat/completions` which **does not exist** on the `/antigravity/` path, causing `404 page not found`.

**Correct SDK mapping:**

| Model Family | npm Package | Endpoint Called |
|---|---|---|
| Claude | `@ai-sdk/anthropic` | `/v1/messages` |
| Gemini | `@ai-sdk/google-generative-ai` | `/v1beta/` |
| OpenAI | `@ai-sdk/openai-compatible` | `/v1/chat/completions` |

### Hybrid Scheduling Mode

When hybrid scheduling is enabled in Sub2API admin, the general endpoints `/v1/messages` and `/v1beta/` will also route to Antigravity accounts.

> **Warning**: Anthropic Claude and Antigravity Claude **cannot be mixed within the same conversation context**. Use groups to isolate them.

---

## Configuration Templates

### Claude Models via Antigravity (Most Common)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "sub2api-claude/claude-sonnet-4-6",
  "provider": {
    "sub2api-claude": {
      "npm": "@ai-sdk/anthropic",
      "name": "Sub2API Claude",
      "options": {
        "baseURL": "https://<YOUR_SUB2API_DOMAIN>/antigravity/v1",
        "apiKey": "<YOUR_SUB2API_API_KEY>"
      },
      "models": {
        "claude-sonnet-4-6": {
          "name": "Claude Sonnet 4.6",
          "limit": { "context": 200000, "output": 64000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-opus-4-6": {
          "name": "Claude Opus 4.6",
          "limit": { "context": 200000, "output": 128000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-opus-4-6-thinking": {
          "name": "Claude Opus 4.6 (Thinking)",
          "limit": { "context": 200000, "output": 128000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-sonnet-4-5": {
          "name": "Claude Sonnet 4.5",
          "limit": { "context": 200000, "output": 64000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-sonnet-4-5-thinking": {
          "name": "Claude Sonnet 4.5 (Thinking)",
          "limit": { "context": 200000, "output": 64000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-opus-4-5-thinking": {
          "name": "Claude Opus 4.5 (Thinking)",
          "limit": { "context": 200000, "output": 128000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        }
      }
    }
  }
}
```

### Gemini Models via Antigravity

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "sub2api-gemini/gemini-3-flash",
  "provider": {
    "sub2api-gemini": {
      "npm": "@ai-sdk/google-generative-ai",
      "name": "Sub2API Gemini",
      "options": {
        "baseURL": "https://<YOUR_SUB2API_DOMAIN>/antigravity/v1beta",
        "apiKey": "<YOUR_SUB2API_API_KEY>"
      },
      "models": {
        "gemini-3-flash": {
          "name": "Gemini 3 Flash",
          "limit": { "context": 1048576, "output": 65536 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "gemini-3-pro-low": {
          "name": "Gemini 3 Pro (Low Thinking)",
          "limit": { "context": 1048576, "output": 65535 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "gemini-3-pro-high": {
          "name": "Gemini 3 Pro (High Thinking)",
          "limit": { "context": 1048576, "output": 65535 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "gemini-3.1-pro-low": {
          "name": "Gemini 3.1 Pro (Low)",
          "limit": { "context": 1048576, "output": 65535 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "gemini-3.1-pro-high": {
          "name": "Gemini 3.1 Pro (High)",
          "limit": { "context": 1048576, "output": 65535 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "gemini-2.5-flash": {
          "name": "Gemini 2.5 Flash",
          "limit": { "context": 1048576, "output": 65536 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        }
      }
    }
  }
}
```

### Both Claude + Gemini (Full Setup)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "sub2api-claude/claude-sonnet-4-6",
  "provider": {
    "sub2api-claude": {
      "npm": "@ai-sdk/anthropic",
      "name": "Sub2API Claude",
      "options": {
        "baseURL": "https://<YOUR_SUB2API_DOMAIN>/antigravity/v1",
        "apiKey": "<YOUR_SUB2API_API_KEY>"
      },
      "models": {
        "claude-sonnet-4-6": {
          "name": "Claude Sonnet 4.6",
          "limit": { "context": 200000, "output": 64000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-opus-4-6": {
          "name": "Claude Opus 4.6",
          "limit": { "context": 200000, "output": 128000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "claude-opus-4-6-thinking": {
          "name": "Claude Opus 4.6 (Thinking)",
          "limit": { "context": 200000, "output": 128000 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        }
      }
    },
    "sub2api-gemini": {
      "npm": "@ai-sdk/google-generative-ai",
      "name": "Sub2API Gemini",
      "options": {
        "baseURL": "https://<YOUR_SUB2API_DOMAIN>/antigravity/v1beta",
        "apiKey": "<YOUR_SUB2API_API_KEY>"
      },
      "models": {
        "gemini-3-flash": {
          "name": "Gemini 3 Flash",
          "limit": { "context": 1048576, "output": 65536 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        },
        "gemini-3-pro-high": {
          "name": "Gemini 3 Pro (High Thinking)",
          "limit": { "context": 1048576, "output": 65535 },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        }
      }
    }
  }
}
```

### Using Environment Variables for API Key (Recommended for Security)

Instead of hardcoding the API key, use OpenCode's `{env:VAR_NAME}` syntax:

```json
"options": {
  "baseURL": "https://your-sub2api-domain/antigravity/v1",
  "apiKey": "{env:SUB2API_KEY}"
}
```

Then set the environment variable:

```bash
export SUB2API_KEY="sk-your-api-key"
```

---

## Step-by-Step Setup Process

### Step 1: Gather Information

Ask the user for:
1. **Sub2API domain** (e.g., `sub2api.example.com`)
2. **API Key** (starts with `sk-`, get from Sub2API admin panel under "API Keys")
3. **Which models** they want to use (Claude, Gemini, or both)
4. **Endpoint type** - Antigravity (`/antigravity/`) or direct (`/`)

### Step 2: Verify Connectivity

Test the API endpoint before configuring:

```bash
# Test Claude endpoint (Antigravity)
curl -s "https://<DOMAIN>/antigravity/v1/messages" -X POST \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}'

# Test available models
curl -s "https://<DOMAIN>/antigravity/v1/models" \
  -H "Authorization: Bearer <API_KEY>"

# Test Gemini endpoint (Antigravity)
curl -s "https://<DOMAIN>/antigravity/v1beta/models" \
  -H "Authorization: Bearer <API_KEY>"
```

A successful Claude response returns JSON with `"type": "message"`.
If you get `404 page not found`, the endpoint path is wrong.
If you get `503`, all upstream accounts are rate-limited or unavailable.

### Step 3: Write Configuration

Use the appropriate template from above. Write to:
- `~/.config/opencode/opencode.json` for global config
- `./opencode.json` for project-specific config

### Step 4: Restart and Verify

After saving, restart OpenCode and use `/models` command to check if Sub2API models appear.

---

## Troubleshooting

### Error: "Not Found: 404 page not found"

This is the most common error. Check these in order:

| # | Check | Fix |
|---|---|---|
| 1 | Using `@ai-sdk/openai-compatible` for Claude? | Change `npm` to `@ai-sdk/anthropic` |
| 2 | Using `@ai-sdk/openai-compatible` for Gemini? | Change `npm` to `@ai-sdk/google-generative-ai` |
| 3 | baseURL ends with `/v1` for Gemini? | Change to `/v1beta` |
| 4 | baseURL missing `/antigravity`? | Add `/antigravity/v1` or `/antigravity/v1beta` |
| 5 | Using wrong model ID? | Check with `curl <baseURL>/models` |

### Error: "Service temporarily unavailable" (503)

Sub2API has no available upstream accounts, or all are in cooldown.

**Fix:** Wait for cooldown, or add more upstream accounts in Sub2API admin.

### Error: "Configuration is invalid"

The `provider` field must be an object `{}`, never a string.

```json
// WRONG - causes "expected record, received string"
"provider": "google"

// CORRECT
"provider": {
  "sub2api-claude": { ... }
}
```

Also check for unrecognized top-level keys. All provider definitions must be **inside** the `provider` object.

### Image/PDF not working

Missing `modalities` in model config. OpenCode defaults to text-only if not specified.

```json
"modalities": {
  "input": ["text", "image", "pdf"],
  "output": ["text"]
}
```

### Claude Code Plan Mode stuck

Known Sub2API issue: In Claude Code, Plan Mode cannot exit automatically.

**Workaround:** Press `Shift + Tab` to manually exit Plan Mode.

### Model format: `<provider>/<model>`

OpenCode's `model` field uses the format `<provider-key>/<model-id>`:

```json
{
  "model": "sub2api-claude/claude-sonnet-4-6",
  "provider": {
    "sub2api-claude": { ... }
  }
}
```

The part before `/` **must match** a key inside `provider`.

---

## Nginx Reverse Proxy

If you use Nginx in front of Sub2API, add this to the `http` block:

```nginx
underscores_in_headers on;
```

Nginx drops headers with underscores by default (e.g. `session_id`), breaking sticky session routing.

---

## Reference: Sub2API Endpoint Map

| Path | Purpose | Protocol |
|---|---|---|
| `/antigravity/v1/messages` | Claude chat (Antigravity accounts) | Anthropic |
| `/antigravity/v1/models` | List available models | REST |
| `/antigravity/v1beta/` | Gemini chat (Antigravity accounts) | Google AI |
| `/v1/messages` | Claude chat (direct + hybrid) | Anthropic |
| `/v1beta/` | Gemini chat (direct + hybrid) | Google AI |
| `/v1/chat/completions` | OpenAI chat (if configured) | OpenAI |

## Reference: Claude Code Environment Variables

For Claude Code CLI (not OpenCode), use:

```bash
export ANTHROPIC_BASE_URL="https://<YOUR_DOMAIN>/antigravity"
export ANTHROPIC_AUTH_TOKEN="sk-xxx"
```

## Reference: Available Models (Typical Antigravity Setup)

### Claude Models
- `claude-sonnet-4-6` - Latest, fast and capable
- `claude-opus-4-6` - Latest, most capable
- `claude-opus-4-6-thinking` - With extended thinking
- `claude-sonnet-4-5` - Previous generation
- `claude-sonnet-4-5-thinking` - Previous gen with thinking
- `claude-opus-4-5-thinking` - Previous gen, most capable with thinking

### Gemini Models
- `gemini-3-flash` - Latest fast model
- `gemini-3-pro-low` / `gemini-3-pro-high` - Pro with thinking levels
- `gemini-3.1-pro-low` / `gemini-3.1-pro-high` - Latest Pro
- `gemini-3.1-flash-image` - Latest image generation
- `gemini-2.5-flash` / `gemini-2.5-flash-thinking` - Previous generation
- `gemini-2.5-flash-image` - Image generation

> Note: Actual available models depend on your Sub2API instance. Query the models endpoint to check.

## Reference Links

- Sub2API GitHub: https://github.com/Wei-Shaw/sub2api
- Sub2API Demo: https://demo.sub2api.org/
- OpenCode Docs: https://opencode.ai/docs
- OpenCode Provider Config: https://opencode.ai/docs/providers/
