# personal-ai-tools

Personal Claude Code skills and MCP servers.

## Skills

Claude Code skills loaded via `~/.claude/skills/`. Invoke with the `Skill` tool.

| Skill | Description |
|-------|-------------|
| [shizuka-na-tabi](./skills/shizuka-na-tabi/) | 静かな旅 Douyin account workflow — video editing, cover generation, copywriting, publishing |
| [sub2api-opencode](./skills/sub2api-opencode/) | Configure Sub2API as a provider in OpenCode (Claude/Gemini endpoint routing) |

## MCPs

Model Context Protocol servers.

| MCP | Description |
|-----|-------------|
| [mcp-chrome](./mcps/mcp-chrome/) | Chrome extension MCP server — exposes browser automation, content analysis, and semantic search to AI assistants |

## Setup

```bash
git clone git@github.com:nianyi778/personal-ai-tools.git ~/personage/personal-ai-tools

# Link skills
ln -s ~/personage/personal-ai-tools/skills/shizuka-na-tabi ~/.claude/skills/shizuka-na-tabi
ln -s ~/personage/personal-ai-tools/skills/sub2api-opencode ~/.claude/skills/sub2api-opencode
```
