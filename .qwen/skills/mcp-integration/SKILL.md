---
name: mcp-integration
description: This skill should be used when creating, configuring, or debugging MCP (Model Context Protocol) servers for the AI Employee. Use when integrating external services (email, browser, filesystem) or building custom MCP servers for specialized tasks.
---

# MCP Integration Skill

## Purpose

Create and manage MCP (Model Context Protocol) servers that enable Qwen to interact with external services. MCP servers provide tools that Qwen can call to perform actions like sending emails, browsing websites, or accessing files.

## When to Use This Skill

✅ User says: "Add MCP support for..."
✅ User needs to: Create custom MCP server, configure existing MCP, debug MCP connections
✅ User wants to: Integrate new API, service, or platform via MCP
✅ Existing MCP servers (filesystem, email, browser) need customization

❌ Don't use for: Direct API integration without MCP (use action-builder skill)
❌ Don't use for: Watcher scripts (use watcher-creator skill)

---

## MCP Architecture

```
.qwen/
├── mcp.json                  ← MCP server configuration
├── model_config.yaml         ← Qwen model settings
└── tools.json                ← Tool definitions (optional)

AI_Employee_Vault/
└── Logs/
    └── mcp/                  ← MCP-specific logs
```

### Current MCP Servers

| Server | Type | Purpose | Status |
|--------|------|---------|--------|
| filesystem | builtin | File operations | ✅ Active |
| email | custom | Gmail API via MCP | ✅ Active |
| browser | custom | Web automation | ✅ Active |

---

## MCP Configuration

### .qwen/mcp.json Template

```json
{
  "servers": [
    {
      "name": "filesystem",
      "type": "builtin"
    },
    {
      "name": "email",
      "command": "node",
      "args": ["/abs/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/abs/path/to/credentials.json",
        "NODE_ENV": "production"
      },
      "cwd": "/abs/path/to/email-mcp",
      "timeout": 30000
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true",
        "SESSION_PATH": "/abs/path/to/browser_session"
      },
      "cwd": "/abs/path/to/project",
      "timeout": 60000
    }
  ],
  "model": {
    "provider": "qwen",
    "model_name": "qwen-max",
    "temperature": 0.2,
    "max_tokens": 4096,
    "top_p": 0.95
  },
  "logging": {
    "level": "info",
    "path": "AI_Employee_Vault/Logs/mcp/mcp.log"
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique server identifier |
| `type` | enum | Conditional | `builtin` or `custom` |
| `command` | string | Conditional | Command to run (for custom servers) |
| `args` | array | Conditional | Command arguments |
| `env` | object | No | Environment variables for server |
| `cwd` | string | No | Working directory for server |
| `timeout` | int | No | Timeout in milliseconds (default: 30000) |

---

## Creating a Custom MCP Server

### Step 1: Choose Language & Framework

**TypeScript (Recommended):**
- Official MCP SDK support
- Better type safety
- Good for complex servers

**Python:**
- FastMCP framework
- Easier for Python developers
- Good for data processing

### Step 2: Project Structure

**TypeScript:**
```
email-mcp/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          ← Server entry point
│   ├── tools/
│   │   ├── send_email.ts
│   │   ├── read_email.ts
│   │   └── list_emails.ts
│   ├── client/
│   │   └── gmail_client.ts
│   └── types.ts
└── README.md
```

**Python:**
```
email-mcp/
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── server.py         ← FastMCP server
│   ├── tools/
│   │   ├── send_email.py
│   │   ├── read_email.py
│   │   └── list_emails.py
│   └── client/
│       └── gmail_client.py
└── README.md
```

### Step 3: Implement Server (TypeScript)

**package.json:**
```json
{
  "name": "email-mcp",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "inspector": "npx @modelcontextprotocol/inspector"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "googleapis": "^130.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "tsx": "^4.0.0"
  }
}
```

**src/index.ts:**
```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

import { sendEmailTool } from './tools/send_email.js';
import { readEmailTool } from './tools/read_email.js';
import { listEmailsTool } from './tools/list_emails.js';

const TOOLS = {
  send_email: sendEmailTool,
  read_email: readEmailTool,
  list_emails: listEmailsTool,
};

const server = new Server(
  {
    name: 'email-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: Object.values(TOOLS).map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema,
      outputSchema: tool.outputSchema,
    })),
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  const tool = TOOLS[name as keyof typeof TOOLS];
  if (!tool) {
    throw new Error(`Unknown tool: ${name}`);
  }
  
  // Validate input with Zod
  const parsed = tool.inputSchema.parse(args);
  
  // Execute tool
  const result = await tool.handler(parsed);
  
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Email MCP server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
```

**src/tools/send_email.ts:**
```typescript
import { z } from 'zod';
import { GmailClient } from '../client/gmail_client.js';

export const sendEmailTool = {
  name: 'send_email',
  description: 'Send an email via Gmail API',
  inputSchema: z.object({
    to: z.string().email().describe('Recipient email address'),
    subject: z.string().describe('Email subject'),
    body: z.string().describe('Email body text'),
    cc: z.array(z.string().email()).optional().describe('CC recipients'),
    attachment: z.string().optional().describe('Path to attachment'),
  }),
  outputSchema: z.object({
    success: z.boolean(),
    messageId: z.string().optional(),
    error: z.string().optional(),
  }),
  handler: async (args: z.infer<typeof sendEmailTool.inputSchema>) => {
    try {
      const client = new GmailClient(process.env.GMAIL_CREDENTIALS);
      const messageId = await client.sendEmail({
        to: args.to,
        subject: args.subject,
        body: args.body,
        cc: args.cc,
        attachment: args.attachment,
      });
      
      return {
        success: true,
        messageId,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },
};
```

### Step 4: Implement Server (Python/FastMCP)

**pyproject.toml:**
```toml
[project]
name = "email-mcp"
version = "1.0.0"
dependencies = [
    "mcp>=1.0.0",
    "google-api-python-client>=2.0.0",
    "pydantic>=2.0.0",
]

[project.scripts]
email-mcp = "email_mcp.server:main"
```

**src/server.py:**
```python
#!/usr/bin/env python3
"""Email MCP Server - FastMCP implementation."""

import os
import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from .client.gmail_client import GmailClient

# Configure transport security for Docker
transport_security = TransportSecuritySettings(
    allowed_hosts=[
        "127.0.0.1:*",
        "localhost:*",
        "[::1]:*",
        "email-mcp:*",  # Docker container name
    ],
)

mcp = FastMCP("email-mcp", transport_security=transport_security)


class SendEmailInput(BaseModel):
    to: EmailStr
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    attachment: Optional[str] = None


class SendEmailOutput(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


@mcp.tool()
async def send_email(input: SendEmailInput) -> SendEmailOutput:
    """Send an email via Gmail API."""
    try:
        client = GmailClient(os.getenv("GMAIL_CREDENTIALS"))
        message_id = await client.send_email(
            to=input.to,
            subject=input.subject,
            body=input.body,
            cc=input.cc,
            attachment=input.attachment,
        )
        return SendEmailOutput(success=True, message_id=message_id)
    except Exception as e:
        return SendEmailOutput(success=False, error=str(e))


@mcp.tool()
async def read_email(message_id: str) -> dict:
    """Read a specific email by ID."""
    client = GmailClient(os.getenv("GMAIL_CREDENTIALS"))
    return await client.read_email(message_id)


@mcp.tool()
async def list_emails(query: str = "is:unread", max_results: int = 10) -> list:
    """List emails matching a Gmail query."""
    client = GmailClient(os.getenv("GMAIL_CREDENTIALS"))
    return await client.list_emails(query, max_results)


# Health check endpoint for Docker
from starlette.responses import JSONResponse

class HealthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/health":
            response = JSONResponse({"status": "healthy"})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


_mcp_app = mcp.streamable_http_app()
app = HealthMiddleware(_mcp_app)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

---

## Testing MCP Servers

### Using MCP Inspector

```bash
# TypeScript
cd email-mcp
npm run build
npx @modelcontextprotocol/inspector node dist/index.js

# Python
cd email-mcp
npx @modelcontextprotocol/inspector python -m email_mcp.server
```

### Manual Testing

```bash
# Test tool listing
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node dist/index.js

# Test tool call
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"send_email","arguments":{"to":"test@example.com","subject":"Test","body":"Test body"}}}' | node dist/index.js
```

---

## Docker Deployment

### Dockerfile (TypeScript)

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist/ ./dist/

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health').read()"

CMD ["node", "dist/index.js"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  email-mcp:
    build: ./email-mcp
    container_name: email-mcp
    environment:
      - GMAIL_CREDENTIALS=/run/secrets/gmail_credentials
      - NODE_ENV=production
    secrets:
      - gmail_credentials
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health').read()"]
      interval: 30s
      timeout: 10s
      start_period: 20s

secrets:
  gmail_credentials:
    file: ./secrets/credentials.json

networks:
  mcp-network:
    driver: bridge
```

---

## Debugging MCP

### Common Issues

**Issue 1: Server won't start**
```bash
# Check logs
tail -f AI_Employee_Vault/Logs/mcp/mcp.log

# Test manually
cd email-mcp && node dist/index.js

# Check credentials
ls -la /path/to/credentials.json
```

**Issue 2: Tool calls fail**
```bash
# Enable debug logging
export MCP_DEBUG=true
node dist/index.js 2>&1 | tee mcp-debug.log

# Check tool schema
npx @modelcontextprotocol/inspector node dist/index.js
```

**Issue 3: Connection timeout**
```json
// .qwen/mcp.json
{
  "servers": [
    {
      "name": "email",
      "timeout": 60000  // Increase timeout
    }
  ]
}
```

**Issue 4: Docker DNS rebinding (421 Misdirected Request)**
```python
# Add transport security settings
transport_security = TransportSecuritySettings(
    allowed_hosts=["email-mcp:*", "127.0.0.1:*", "localhost:*"]
)
mcp = FastMCP("email-mcp", transport_security=transport_security)
```

---

## Security Best Practices

### Credentials Management

```bash
# NEVER hardcode in code
export GMAIL_CREDENTIALS=/path/to/credentials.json

# Use Docker secrets
docker secret create gmail_credentials ./credentials.json

# Use environment variables from .env (never commit .env)
# .env
GMAIL_CREDENTIALS=/absolute/path/to/credentials.json
```

### .gitignore

```
# MCP servers
*.log
node_modules/
__pycache__/
dist/
.env
credentials.json
*.key
```

### Rate Limiting

```typescript
// In tool handler
import { RateLimiter } from './rate_limiter.js';

const rateLimiter = new RateLimiter({
  maxCalls: 10,
  periodSeconds: 3600,
});

export const sendEmailTool = {
  handler: async (args) => {
    if (!rateLimiter.checkAndIncrement()) {
      throw new Error('Rate limit exceeded');
    }
    // ... rest of handler
  },
};
```

---

## Reference Files

- [MCP Protocol Spec](https://modelcontextprotocol.io/specification)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Python SDK (FastMCP)](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Current MCP Config](../../.qwen/mcp.json)
- [Email MCP](../../email-mcp/)
- [Browser MCP](../../browser-mcp/)

---

## Examples

### Example 1: Add Slack MCP Server

**User request:** "Add Slack integration via MCP"

**Implementation:**
1. Create `slack-mcp/` directory
2. Initialize TypeScript project
3. Implement tools: `send_message`, `list_channels`, `get_thread`
4. Add to `.qwen/mcp.json`
5. Test with MCP Inspector

### Example 2: Add Database MCP Server

**User request:** "Add PostgreSQL query capability via MCP"

**Implementation:**
1. Create `database-mcp/` directory
2. Use Python/FastMCP (better for data processing)
3. Implement tools: `query`, `insert`, `update`, `delete`
4. Add connection pooling
5. Add read-only mode for safety

### Example 3: Add Calendar MCP Server

**User request:** "Add Google Calendar integration"

**Implementation:**
1. Create `calendar-mcp/` directory
2. Use Google Calendar API
3. Implement tools: `list_events`, `create_event`, `update_event`, `delete_event`
4. Add timezone handling
5. Add conflict detection

---

## Anti-Patterns (Avoid These)

❌ **Hardcoding credentials** - Always use env vars or secrets
❌ **No error handling** - Always catch and return structured errors
❌ **Missing input validation** - Always use Zod/Pydantic schemas
❌ **No rate limiting** - Always implement rate limits
❌ **Ignoring transport security** - Configure allowed_hosts for Docker
❌ **No health endpoint** - Add /health for Docker healthchecks
❌ **Logging sensitive data** - Never log credentials or tokens
❌ **Blocking the event loop** - Use async/await for I/O

---

## Success Metrics

✅ MCP server starts without errors
✅ Tools listed correctly in Inspector
✅ Tool calls return structured results
✅ Error messages are actionable
✅ Rate limiting enforced
✅ Credentials never in logs
✅ Docker healthcheck passes
✅ Transport security configured

---

**Created from:** AI Employee Hackathon - MCP Integration Patterns
**Reference:** MCP Protocol Specification, FastMCP Documentation
