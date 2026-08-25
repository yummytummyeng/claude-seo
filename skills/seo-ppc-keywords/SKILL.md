---
name: seo-ppc-keywords
description: >
  PPC / paid search keyword research for Google Ads and Microsoft (Bing) Ads
  campaigns. Expands seed keywords, classifies commercial/transactional intent,
  recommends match types (broad/phrase/exact), surfaces negative keywords, and
  clusters keywords into ad groups with CPC and competition-based prioritization.
  Use when user says "PPC keywords", "ads keywords", "Google Ads keywords",
  "keyword research for ads", "keywords to run ads", "ad group structure",
  "negative keywords", or "paid search keywords".
user-invokable: true
argument-hint: "[seed keyword or url]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
  - Write
---

# PPC Keyword Research

Builds a campaign-ready keyword list for running paid search ads (Google Ads /
Microsoft Ads): expansion, intent filtering, match types, negatives, ad group
clustering, and priority scoring. This is distinct from organic keyword
research (`seo-content`, `seo-dataforseo`) — PPC keywords are chosen for
**click cost and conversion likelihood**, not ranking difficulty.

## Process

### 1. Seed Input
Accept a seed keyword, a list of seed keywords, or a URL (site/landing page).
If given a URL, extract product/service terms, page titles, and headings to
derive seeds. Ask the user for the target location/language and monthly
budget if not provided — both affect match type and prioritization strategy.

### 2. Keyword Expansion
Expand each seed into a candidate list covering:
- **Head terms**: broad category (e.g., "running shoes")
- **Mid-tail**: qualified terms (e.g., "waterproof running shoes for men")
- **Long-tail**: highly specific, lower volume/higher intent (e.g., "best waterproof trail running shoes size 10")
- **Branded**: competitor and own-brand terms (own-brand defense, competitor conquesting)
- **Commercial modifiers**: "buy", "price", "cost", "discount", "near me", "best", "top", "vs", "for [use case]", "[city/region]"

If DataForSEO extension tools are available (see Integration below), use them
for real volume/CPC/competition data instead of estimating.

### 3. Intent Filtering (PPC-specific)
Unlike organic content strategy, PPC budget should concentrate on
**commercial and transactional intent**. Classify each candidate:

| Intent | PPC Fit | Action |
|--------|---------|--------|
| Transactional ("buy", "order", "price", "near me") | High | Prioritize, exact/phrase match |
| Commercial investigation ("best", "top", "review", "vs") | Medium-High | Include, phrase/broad match |
| Navigational (brand names) | Depends on strategy | Only if defending brand or conquesting competitors |
| Informational ("what is", "how to", "guide") | Low | Exclude from spend or add as negatives, unless top-of-funnel awareness is the explicit goal |

### 4. Match Type Recommendation

| Match Type | Syntax | When to Use |
|------------|--------|--------------|
| Exact | `[keyword]` | High-intent, proven converters; tightest control over spend |
| Phrase | `"keyword"` | Mid-tail terms where word order/context matters |
| Broad (with Smart Bidding) | `keyword` | Discovery/expansion only, paired with automated bidding and strong negative list; never broad match without a bidding strategy and negative list in place |

Default recommendation: start new campaigns on phrase + exact for control,
layer in broad match only once conversion data exists to support automated
bidding.

### 5. Negative Keyword Discovery
Identify terms to exclude so spend isn't wasted:
- Informational modifiers not filtered in step 3 ("free", "diy", "definition", "meaning", "jobs", "salary", "course")
- Irrelevant use cases (e.g., a B2B SaaS excludes "for personal use")
- Competitor terms if not intentionally conquesting
- Cross-category overlap (e.g., "running shoes" campaign should negative "running shoes emoji", "running shoes drawing")
- Mine existing Search Terms Report data if the user provides it (paste-in) for terms that received clicks but zero conversions

### 6. Ad Group Clustering
Group keywords by shared intent/theme so ad copy and landing page can stay
tightly relevant (this drives Quality Score):
- **Thematic clusters** (recommended default): 5-20 closely related keywords per ad group, one clear theme (e.g., "waterproof running shoes", "trail running shoes")
- **SKAG (Single Keyword Ad Groups)**: one keyword per ad group for maximum message match; use only for high-value/high-volume terms where the extra management overhead is justified
- Each ad group should map to one landing page (or landing page section) — flag when no matching landing page exists

### 7. Prioritization
Score each keyword/ad group candidate on:
- Estimated CPC (lower is better for budget efficiency, but not at the cost of relevance)
- Competition level (Low/Medium/High)
- Search volume (higher = more opportunity, but check budget can sustain it)
- Intent strength (from step 3)

Compute a simple priority tier (not a fixed formula — reason about tradeoffs
per the user's stated goal of volume vs. efficiency vs. budget):
- **Tier 1**: High intent, reasonable CPC, adequate volume → launch first
- **Tier 2**: High intent, high CPC or low volume → include with tight budget caps
- **Tier 3**: Medium intent → test with small budget, monitor closely
- **Excluded**: Low intent / high negative-keyword overlap → do not include

## Output

### Campaign Structure
```
Campaign: [Name]
├── Ad Group: [Theme 1]
│   ├── Keywords (match type, est. volume, est. CPC, intent, tier)
│   └── Negative keywords (ad-group level)
├── Ad Group: [Theme 2]
│   └── ...
└── Campaign-level negative keywords
```

### Keyword Table
| Keyword | Match Type | Intent | Est. Volume | Est. CPC | Competition | Ad Group | Tier |
|---------|-----------|--------|-------------|----------|-------------|----------|------|

### Negative Keyword List
| Negative Keyword | Level (Campaign/Ad Group) | Reason |
|-------------------|---------------------------|--------|

### Recommendations
- Match type rollout plan
- Budget allocation guidance by tier
- Landing page gaps (ad groups without a matching page)
- Quality Score risk flags (ad group too broad, no landing page match)

## DataForSEO Integration (Optional)

If the DataForSEO extension is installed, use live data instead of estimates:
- `dataforseo_labs_google_keyword_ideas` / `dataforseo_labs_google_keyword_suggestions` / `dataforseo_labs_google_related_keywords` — expansion (step 2)
- `kw_data_google_ads_search_volume` — real search volume and CPC (this endpoint returns actual Google Ads CPC/competition data, the most direct PPC signal available)
- `dataforseo_labs_search_intent` — intent classification (step 3)
- `dataforseo_labs_bulk_keyword_difficulty` — use as a rough proxy for auction competitiveness alongside the CPC/competition fields from `kw_data_google_ads_search_volume`
- `kw_data_google_trends_explore` — seasonality, useful for budget pacing recommendations

Without the extension, state clearly that volume/CPC figures are estimates
based on general category knowledge, not live auction data, and recommend the
user verify with Google Keyword Planner or the DataForSEO extension
(`./extensions/dataforseo/install.sh`) before setting real budgets.

## Error Handling

| Scenario | Action |
|----------|--------|
| No seed keyword or URL provided | Ask the user for at least one seed keyword, the target product/service, and target location. Do not guess an industry. |
| URL provided but unreachable | Report the error and ask the user to paste seed keywords directly instead. |
| DataForSEO unavailable and user expects live data | State plainly that figures are estimates, not live auction data, and point to the DataForSEO extension for real numbers. |
| Very broad seed (e.g., single generic word) | Ask a clarifying question about the specific product/service/audience before expanding, to avoid a low-relevance keyword list. |
