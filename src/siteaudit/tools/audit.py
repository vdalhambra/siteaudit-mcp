"""Audit tools — the main tools exposed via MCP."""

from typing import Annotated
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from siteaudit.utils.fetcher import fetch_page, fetch_url, get_domain
from siteaudit.analyzers.seo import analyze_seo
from siteaudit.analyzers.security import analyze_security
from siteaudit.analyzers.performance import analyze_performance


def register_audit_tools(mcp: FastMCP) -> None:
    """Register audit tools on the MCP server."""

    @mcp.tool(
        tags={"audit", "comprehensive"},
        annotations={"readOnlyHint": True},
    )
    def full_audit(
        url: Annotated[str, Field(description="URL to audit (e.g., 'example.com' or 'https://example.com')")],
    ) -> dict:
        """Run a comprehensive audit on a URL — SEO, performance, and security in one call.

        Returns a unified score (0-100) plus detailed results for each category.
        This is the most complete analysis available.
        """
        resp, soup = fetch_page(url)
        actual_url = resp.url

        seo = analyze_seo(actual_url, resp, soup)
        perf = analyze_performance(actual_url, resp)
        sec = analyze_security(actual_url, resp)

        # Overall score (weighted average)
        overall = round(seo["score"] * 0.4 + perf["score"] * 0.3 + sec["score"] * 0.3)

        # Collect top issues across all categories
        all_issues = (
            [f"[SEO] {i}" for i in seo["issues"]]
            + [f"[Performance] {i}" for i in perf["issues"]]
            + [f"[Security] {i}" for i in sec["issues"]]
        )
        all_warnings = (
            [f"[SEO] {w}" for w in seo["warnings"][:5]]
            + [f"[Performance] {w}" for w in perf["warnings"][:3]]
            + [f"[Security] {w}" for w in sec["warnings"][:5]]
        )

        grade = _score_to_grade(overall)

        return {
            "url": actual_url,
            "overall_score": overall,
            "grade": grade,
            "scores": {
                "seo": seo["score"],
                "performance": perf["score"],
                "security": sec["score"],
            },
            "top_issues": all_issues,
            "top_warnings": all_warnings[:10],
            "seo": seo,
            "performance": perf,
            "security": sec,
        }

    @mcp.tool(
        tags={"audit", "seo"},
        annotations={"readOnlyHint": True},
    )
    def seo_audit(
        url: Annotated[str, Field(description="URL to analyze for SEO")],
    ) -> dict:
        """Run an SEO-focused audit on a URL.

        Checks title tags, meta descriptions, headings, images alt text,
        internal/external links, canonical URLs, Open Graph, structured data,
        mobile viewport, and content length. Returns score + actionable recommendations.
        """
        resp, soup = fetch_page(url)
        result = analyze_seo(resp.url, resp, soup)
        result["url"] = resp.url
        return result

    @mcp.tool(
        tags={"audit", "security"},
        annotations={"readOnlyHint": True},
    )
    def security_audit(
        url: Annotated[str, Field(description="URL to check for security")],
    ) -> dict:
        """Run a security audit on a URL.

        Checks HTTPS, HSTS, CSP, X-Frame-Options, cookie flags,
        SSL certificate validity and expiration, server disclosure,
        and other security headers. Returns score + fixes needed.
        """
        resp, soup = fetch_page(url)
        result = analyze_security(resp.url, resp)
        result["url"] = resp.url
        return result

    @mcp.tool(
        tags={"audit", "performance"},
        annotations={"readOnlyHint": True},
    )
    def performance_audit(
        url: Annotated[str, Field(description="URL to check for performance")],
    ) -> dict:
        """Check page performance — response time, page size, compression, caching.

        Returns server response time, page size, compression status,
        redirect chain analysis, and caching header review.
        """
        resp, soup = fetch_page(url)
        result = analyze_performance(resp.url, resp)
        result["url"] = resp.url
        return result

    @mcp.tool(
        tags={"audit", "comparison"},
        annotations={"readOnlyHint": True},
    )
    def compare_sites(
        urls: Annotated[str, Field(description="Comma-separated URLs to compare (e.g., 'example.com,competitor.com')")],
    ) -> dict:
        """Compare SEO and performance scores of multiple websites side by side.

        Useful for competitive analysis — see how your site stacks up
        against competitors across SEO, performance, and security.
        """
        url_list = [u.strip() for u in urls.split(",") if u.strip()]
        if len(url_list) < 2:
            raise ToolError("Provide at least 2 URLs to compare, separated by commas.")
        if len(url_list) > 5:
            url_list = url_list[:5]

        results = []
        for u in url_list:
            try:
                resp, soup = fetch_page(u)
                seo = analyze_seo(resp.url, resp, soup)
                perf = analyze_performance(resp.url, resp)
                sec = analyze_security(resp.url, resp)
                overall = round(seo["score"] * 0.4 + perf["score"] * 0.3 + sec["score"] * 0.3)

                results.append({
                    "url": resp.url,
                    "overall_score": overall,
                    "grade": _score_to_grade(overall),
                    "seo_score": seo["score"],
                    "performance_score": perf["score"],
                    "security_score": sec["score"],
                    "issues_count": seo["issues_count"] + perf["issues_count"] + sec["issues_count"],
                    "page_size_kb": perf["metrics"]["page_size_kb"],
                    "response_time_ms": perf["metrics"]["response_time_ms"],
                })
            except Exception as e:
                results.append({"url": u, "error": str(e)})

        # Rank by overall score
        valid = [r for r in results if "overall_score" in r]
        ranked = sorted(valid, key=lambda x: x["overall_score"], reverse=True)
        for i, r in enumerate(ranked):
            r["rank"] = i + 1

        best = ranked[0]["url"] if ranked else None
        return {
            "sites_compared": len(url_list),
            "best_overall": best,
            "comparison": results,
        }

    @mcp.tool(
        tags={"audit", "check"},
        annotations={"readOnlyHint": True},
    )
    def check_robots_txt(
        url: Annotated[str, Field(description="Website URL or domain to check robots.txt")],
    ) -> dict:
        """Check and analyze a site's robots.txt file.

        Shows which paths are allowed/disallowed, sitemaps referenced,
        and crawl-delay settings.
        """
        domain = get_domain(url)
        robots_url = f"https://{domain}/robots.txt"
        resp = fetch_url(robots_url)

        if resp is None or resp.status_code != 200:
            return {
                "url": robots_url,
                "exists": False,
                "note": "No robots.txt found — search engines will crawl everything",
            }

        content = resp.text
        lines = content.strip().split("\n")
        rules = []
        sitemaps = []
        current_agent = "*"

        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.lower().startswith("user-agent:"):
                current_agent = line.split(":", 1)[1].strip()
            elif line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path:
                    rules.append({"agent": current_agent, "type": "disallow", "path": path})
            elif line.lower().startswith("allow:"):
                path = line.split(":", 1)[1].strip()
                if path:
                    rules.append({"agent": current_agent, "type": "allow", "path": path})
            elif line.lower().startswith("sitemap:"):
                sitemaps.append(line.split(":", 1)[1].strip())

        return {
            "url": robots_url,
            "exists": True,
            "rules_count": len(rules),
            "rules": rules[:30],
            "sitemaps": sitemaps,
            "raw_length": len(content),
        }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
