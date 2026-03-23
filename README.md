# QC-Paper-KB 🔬

**The first AI-native, programmatically searchable, auto-updating knowledge base for quantum computing research.**

> 20,000+ papers · 25 venues · Daily auto-updates · Venue recommendation engine · Trend analysis · LLM-ready

[![Papers](https://img.shields.io/badge/Papers-19%2C846-blue)]()
[![Venues](https://img.shields.io/badge/Venues-25-green)]()
[![Auto Update](https://img.shields.io/badge/Update-Daily-brightgreen)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

## What is this?

QC-Paper-KB is a **structured, searchable knowledge base** of quantum computing research papers, designed to be directly consumed by LLM agents and AI-assisted research workflows.

Unlike existing [awesome-lists](https://github.com/desireevl/awesome-quantum-computing) that are manually curated link collections (hundreds of entries), QC-Paper-KB is:

| Feature | Awesome Lists | QC-Paper-KB |
|---------|--------------|-------------|
| Scale | ~200-500 links | **19,846 papers** |
| Searchable | ❌ Manual browsing | ✅ Full-text keyword search |
| Venue metadata | ❌ None | ✅ IF, SJR, CAS zones, scope, tiers for 25 venues |
| Auto-updating | ❌ Manual PRs | ✅ Daily via Semantic Scholar + arXiv APIs |
| Venue recommendation | ❌ | ✅ `recommend` command: auto-scans all venues by acceptance density |
| Trend analysis | ❌ | ✅ Year-over-year growth, emerging topic detection, cross-domain analysis |
| LLM integration | ❌ | ✅ Structured JSON, Claude Code skill, agent-ready |

## Quick Start

### Search papers
```bash
python scripts/search.py search "quantum error correction surface code" --sort citations --limit 10 --verbose
```

### Get venue recommendation for your paper
```bash
# Input your paper's keywords, get ranked venues by acceptance density
python scripts/search.py recommend "diffusion model" "circuit generation" "quantum circuit" --top 10
```

Output:
```
Venue           Tier                 Match   3yr   1yr   Latest       Top Cited
---------------------------------------------------------------------------------------------------------
NC              T2-top-physics       7       6     5     2026-03-16   Enhancing combinatorial... (40c)
npjQI           T3-excellent         6       6     3     2026-02-13   Parameterized quantum... (14c)
PRL             T2-top-physics       5       5     0     2024-12-16   Generative quantum... (49c)
...
```

### Analyze research trends
```bash
# Quantum computing field trends
python scripts/trends.py --kb quantum --emerging

# Cross-domain analysis (Quantum × ML)
python scripts/trends.py --kb cross
```

## Coverage

### Journals (19 venues)

| Tier | Venues | CAS Zone |
|------|--------|----------|
| T1-flagship | Nature, Science | 综合1区Top |
| T2-top-physics | PRL, PRX, PRXQ, Nature Physics, Nature Communications | 物理天文1区 |
| T3-excellent | npj Quantum Information, Quantum, QST, Communications Physics | 物理天文1-2区 |
| T4-standard | PRA, PR Applied, PR Research, TQE, TQC, AQT, EPJQT | 物理天文2区 |
| T5-entry | QIP, NJP | 物理天文3区 |

### Conferences (6 venues)

| Tier | Venues |
|------|--------|
| CCF-A | ASPLOS, MICRO, ISCA, HPCA, DAC, ICCAD |

### Preprints

| Source | Papers |
|--------|--------|
| arXiv quant-ph | 10,846 |

## Paper Counts by Venue

| Venue | Papers | | Venue | Papers |
|-------|--------|-|-------|--------|
| arXiv | 10,846 | | QST | 367 |
| NC | 739 | | Science | 253 |
| PRL | 729 | | NJP | 251 |
| PRA | 674 | | QIP | 241 |
| Nature | 522 | | DAC | 236 |
| PRXQ | 513 | | TQE | 232 |
| Quantum | 493 | | ASPLOS | 230 |
| PR Applied | 490 | | ICCAD | 226 |
| PR Research | 468 | | MICRO | 196 |
| npj QI | 432 | | HPCA | 185 |
| PRX | 419 | | ISCA | 176 |
| AQT | 401 | | TQC | 141 |
| Nature Physics | 386 | | | |

## LLM / AI Agent Integration

QC-Paper-KB is designed to be **directly consumed by AI agents**:

### Claude Code (Built-in Skill)

Drop the `skills/paper-kb/` folder into your `.claude/skills/` directory. Then in any Claude Code conversation:

> "我这个量子纠错的工作投哪个期刊合适？"
>
> Claude will automatically search the KB, analyze venue acceptance patterns, and give a data-driven recommendation.

### Any LLM Agent (RAG)

All data is structured JSON — load into any vector store or RAG pipeline:

```python
import json

# Load all papers
with open("data/papers/PRXQ.json") as f:
    papers = json.load(f)

# Each paper has: title, authors, date, abstract, citations, doi, arxiv_id, tldr
for p in papers[:3]:
    print(f"{p['title']} ({p['citations']} citations)")
```

### Venue Metadata API

```python
with open("data/venues.json") as f:
    venues = json.load(f)

# Rich metadata: IF, SJR, CAS zone, scope, tier, submission guidelines
prxq = venues["PRXQ"]
print(f"IF={prxq['impact_factor']}, SJR={prxq['sjr']}, Tier={prxq['tier']}")
# IF=11.0, SJR=5.34, Tier=T2-top-physics
```

## Data Schema

### Paper Entry
```json
{
  "title": "Quantum Error Correction with Gauge Symmetries",
  "authors": ["A. Kubica", "M. Vasmer"],
  "date": "2024-12-15",
  "venue": "PRXQ",
  "citations": 42,
  "abstract": "We introduce a framework for quantum error correction...",
  "tldr": "A new framework connecting gauge symmetries to QEC codes...",
  "doi": "10.1103/PRXQuantum.5.040301",
  "arxiv_id": "2312.09272",
  "url": "https://doi.org/10.1103/PRXQuantum.5.040301"
}
```

### Venue Entry
```json
{
  "PRXQ": {
    "tier": "T2-top-physics",
    "impact_factor": 11.0,
    "sjr": 5.34,
    "cas_zone": {"big_category": "物理天文1区", "small_category": "量子科技1区"},
    "scope": "All topics in quantum information science and technology...",
    "not_suitable_for": "Incremental advances without broad impact..."
  }
}
```

## Trend Analysis

### Quantum Computing Research Growth (2023 → 2025)

| Direction | 2023 | 2025 | Growth |
|-----------|------|------|--------|
| Quantum Simulation | 213 | 809 | **+280%** 🔥 |
| Quantum Networking | 47 | 165 | **+251%** 🔥 |
| QEC | 228 | 678 | **+197%** |
| Quantum ML | 380 | 984 | **+159%** |
| Hardware | 375 | 945 | **+152%** |
| Compilation | 39 | 110 | **+182%** |
| Optimization | 161 | 286 | +78% |

### Cross-Domain Hotspots (Quantum × ML)

| Intersection | Papers | Since 2024 | Maturity |
|-------------|--------|------------|----------|
| RL + Quantum | 331 | 221 | Mature |
| Transformer + Quantum | 156 | 132 | Growing fast |
| GNN + Quantum | 75 | 61 | Emerging |
| Diffusion + Quantum | 28 | 22 | **Blue ocean** 🌊 |

## Installation

```bash
git clone https://github.com/taoge946/QC-Paper-KB.git
cd QC-Paper-KB
pip install -r requirements.txt  # No heavy dependencies

# Search papers
python scripts/search.py search "surface code" --sort citations --limit 10

# Get venue recommendations
python scripts/search.py recommend "your keywords here" --top 10

# Run trend analysis
python scripts/trends.py --kb quantum --emerging
```

## Daily Updates

The knowledge base auto-updates daily via Semantic Scholar and arXiv APIs. To run manually:

```bash
python scripts/daily_update.py
```

Set up your own Semantic Scholar API key (free) for faster updates:
```bash
# In scripts/config.py
SEMANTIC_SCHOLAR_API_KEY = "your-key-here"
```

Apply at: https://www.semanticscholar.org/product/api#api-key-form

## Citation

If you use QC-Paper-KB in your research, please cite:

```bibtex
@software{li2026qcpaperkb,
  author = {Jintao Li},
  title = {QC-Paper-KB: AI-Native Knowledge Base for Quantum Computing Research},
  year = {2026},
  url = {https://github.com/taoge946/QC-Paper-KB}
}
```

## License

MIT License

## Acknowledgments

- Data sourced from [Semantic Scholar](https://www.semanticscholar.org/) and [arXiv](https://arxiv.org/)
- Venue metadata from [中科院分区表](https://www.fenqubiao.com/), [SCImago](https://www.scimagojr.com/), [JCR](https://jcr.clarivate.com/)
- Built at [Beijing Academy of Quantum Information Sciences (BAQIS)](http://www.baqis.ac.cn/)
