---
name: exa-search
description: Advanced web search, research, and crawling via Exa AI. Use for deep web searches, company research, LinkedIn lookups, code context, URL crawling, and AI-powered deep research reports. Triggers on research tasks, people/company lookups, code documentation needs, or when higher-quality search results are needed than basic web search.
---

# Exa Search

Exa AI provides neural-powered web search with content extraction, category filters, and deep research capabilities.

## MCP Server

```
https://mcp.exa.ai/mcp
```

Add to mcporter config:
```bash
mcporter config add exa --url "https://mcp.exa.ai/mcp"
mcporter auth exa  # OAuth flow opens in browser
```

## Tools

### Quick Search

**web_search_exa** — Simple web search
```bash
mcporter call exa.web_search_exa query="latest AI developments"
```

**deep_search_exa** — Natural language search returning formatted results
```bash
mcporter call exa.deep_search_exa objective="Find recent papers on transformer architectures"
```

### Advanced Search

**web_search_advanced_exa** — Full control over filters, domains, dates, highlights
```bash
mcporter call exa.web_search_advanced_exa \
  query="machine learning" \
  category="research paper" \
  --include-domains arxiv.org,openreview.net \
  --start-published-date 2024-01-01 \
  --enable-summary true
```

Options: `type` (auto|fast|deep|neural), `category` (company|research paper|news|pdf|github|tweet|personal site|people|financial report), `includeDomains`, `excludeDomains`, `startPublishedDate`, `endPublishedDate`, `includeText`, `excludeText`, `enableSummary`, `enableHighlights`, `subpages`

### Specialized

**company_research_exa** — Company intelligence
```bash
mcporter call exa.company_research_exa companyName="Anthropic"
```

**linkedin_search_exa** — Find professionals
```bash
mcporter call exa.linkedin_search_exa query="AI engineers London"
```

**get_code_context_exa** — API/SDK/library documentation
```bash
mcporter call exa.get_code_context_exa query="Next.js app router middleware" tokensNum:10000
```

**crawling_exa** — Extract content from specific URLs
```bash
mcporter call exa.crawling_exa url="https://example.com/article" maxCharacters:5000
```

### Deep Research (Async)

For complex research requiring multi-source synthesis:

```bash
# Start research task
mcporter call exa.deep_researcher_start \
  instructions="Analyze the current state of AI regulation in the EU vs US" \
  model="exa-research-pro"

# Poll for results (repeat until status=completed)
mcporter call exa.deep_researcher_check taskId="<returned-task-id>"
```

Models: `exa-research` (15-45s, default), `exa-research-pro` (45s-2min, comprehensive)

## When to Use

- **web_search_exa**: Quick lookups, general queries
- **web_search_advanced_exa**: Need filters, date ranges, specific domains, or highlights
- **deep_search_exa**: Natural language research questions
- **company_research_exa**: Business/org intelligence
- **linkedin_search_exa**: Finding people/professionals
- **get_code_context_exa**: Programming docs, API references, SDK examples
- **crawling_exa**: Extract specific page content
- **deep_researcher_start/check**: Complex multi-source research reports
