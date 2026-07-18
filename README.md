# 🧬AdDNA — AI Creative Intelligence

AdDNA collects ads from Foreplay and PiPiSpy, normalizes provider data, removes duplicate placements, extracts creative features, identifies market patterns, surfaces opportunity gaps, and generates actionable creative outputs.

## What the dashboard covers

- Market search by brand, category, country, platform, and provider
- Provider-safe normalization (searched brand is never falsely assigned as advertiser)
- Content-aware deduplication and duplicate-rate reporting
- Hook and CTA extraction from provider fields, copy, or transcript
- Pain points, benefits, proof, audience, tone, emotion, and positioning signals
- Executive summary, winning patterns, opportunity gaps, and evidence counts
- Positioning matrix, Creative DNA, and Market Scorecard
- AI recommendations, creative brief, 30-second script, and shot list
- Evidence table and complete JSON export

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m streamlit run app/main.py
```

The app works in sample mode without API keys. Configure provider keys in `.env` for live data.

## Architecture

```text
Provider APIs
  -> Collector
  -> Provider mappers
  -> Advertisement schema
  -> Creative deduplicator
  -> Feature extractor
  -> Pattern engine
  -> Recommendation engine
  -> Report generator
  -> Streamlit dashboard
```

## Important interpretation note

Search results can mention a searched brand without being official ads from that advertiser. AdDNA preserves the provider-detected brand and adds a data-quality warning rather than overwriting advertiser identity with the search term.


## v4 Insight-First UI

The v4 dashboard replaces engagement graphs with decision-ready metric cards.

Each intelligence metric includes:

- Score and level
- What the evidence means
- Confidence
- A specific improvement action

New sections:

- Executive Intelligence
- Engagement Analysis
- Creative Intelligence
- Strategy Intelligence
- Why Competitors Are Winning
- Next Best Creative

The scoring is directional and is explicitly based on the fields returned by providers.


## v6 LLM Tabs

The dashboard now uses four top-level tabs:

- Overview
- Market Intelligence
- Creative Strategy
- Evidence

Market Intelligence and the primary Creative Brief are generated through the configured
OpenRouter model. If the API key is unavailable or the response is invalid, the UI does
not display fabricated AI market claims.


## v7 UI refinements

- Added consistent spacing across tabs, cards, columns, and sections.
- Added more top padding so the product header no longer touches the browser chrome.
- Rebuilt the sidebar as a compact, consistent filter form with placeholders.
- Added session-state persistence so export format changes do not erase the analysis.
- Replaced multiple export buttons with one top-level export selector and one download button.
- The complete ZIP export includes HTML, JSON, and CSV reports.
