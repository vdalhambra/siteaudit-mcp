# SiteAudit MCP

**Instant SEO, Performance, and Security Audits for AI Agents** — analyze any URL with a single tool call via the Model Context Protocol.

## What it does

SiteAudit gives your AI agent the ability to audit any website instantly. No API keys, no configuration, no cost. Just ask:

- "Audit example.com"
- "Check the SEO of my competitor's site"
- "Is my site secure? Check the security headers"
- "Compare my site vs 3 competitors"
- "Show me the robots.txt for this domain"

## Tools (6)

| Tool | Description |
|------|-------------|
| `full_audit` | Comprehensive SEO + performance + security audit with unified score (0-100) |
| `seo_audit` | SEO analysis: title, meta, headings, images, links, structured data, Open Graph |
| `security_audit` | Security headers, HTTPS, HSTS, CSP, SSL certificate check, cookie flags |
| `performance_audit` | Response time, page size, compression, caching, redirects |
| `compare_sites` | Side-by-side comparison of multiple websites |
| `check_robots_txt` | Parse and analyze robots.txt rules and sitemaps |

## Installation

### Claude Code / Claude Desktop

```json
{
  "mcpServers": {
    "siteaudit": {
      "command": "uvx",
      "args": ["--from", "siteaudit-mcp", "siteaudit"]
    }
  }
}
```

### From source

```bash
git clone https://github.com/vdalhambra/siteaudit-mcp.git
cd siteaudit-mcp
uv sync
uv run siteaudit
```

## What it checks

### SEO (20+ checks)
- Title tag (presence, length)
- Meta description (presence, length)
- H1 tag (count, content)
- Heading hierarchy (H1-H6)
- Image alt text coverage
- Internal/external link count
- Canonical URL
- Open Graph tags
- Twitter Card tags
- Mobile viewport
- Structured data (JSON-LD)
- Favicon
- Language attribute
- robots meta directives
- Content length (word count)

### Security (10+ checks)
- HTTPS enforcement
- HSTS header (with subdomains and preload)
- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy
- Server/X-Powered-By disclosure
- Cookie security flags (Secure, HttpOnly, SameSite)
- SSL certificate validity and expiration

### Performance
- Server response time (ms)
- Page size (KB)
- Compression (gzip/brotli)
- Cache-Control headers
- Redirect chain analysis
- HTTP status code

## Example Output

```
URL: https://github.com
Overall Score: 90/100 (Grade: A)

Scores:
  SEO: 85/100
  Performance: 95/100
  Security: 90/100

Issues: 0
Warnings: 3
  [SEO] No JSON-LD structured data
  [Security] Missing Content-Security-Policy header
  [Security] Server header discloses: 'GitHub.com'
```

## No API Keys Required

SiteAudit works entirely by analyzing the HTML and HTTP headers of the target URL. No third-party API keys needed. It uses:
- `requests` for HTTP fetching
- `BeautifulSoup` for HTML parsing
- Python `ssl` for certificate checking

## License

MIT
