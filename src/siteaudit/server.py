"""
SiteAudit MCP Server — Instant SEO, Performance, and Security Audits for AI Agents.

Analyze any URL with a single tool call: SEO checks, security headers,
performance metrics, SSL verification, and competitive comparison.
"""

from fastmcp import FastMCP

from siteaudit.tools.audit import register_audit_tools

mcp = FastMCP(
    name="SiteAudit",
    instructions=(
        "SiteAudit provides instant website audits for any URL. "
        "Use these tools to check SEO (meta tags, headings, links, structured data), "
        "security (HTTPS, headers, SSL certificate, cookies), "
        "and performance (response time, page size, compression, caching). "
        "You can audit a single URL or compare multiple sites side by side. "
        "Just provide a URL like 'example.com' — no API keys needed."
    ),
    version="1.0.0",
    mask_error_details=True,
)

register_audit_tools(mcp)


def main():
    """Entry point for the SiteAudit MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
