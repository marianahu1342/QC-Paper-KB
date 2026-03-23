#!/usr/bin/env python3
"""趋势分析工具 - 支持量子 KB 和 ML KB"""

import json
import os
import sys
import io
import glob
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def load_papers(base_dir):
    papers = []
    papers_dir = os.path.join(base_dir, "data", "papers")
    for f in glob.glob(os.path.join(papers_dir, "*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            for p in json.load(fh):
                if p.get("date"):
                    papers.append(p)
    return papers


def analyze_trends(papers, topic_keywords, start_year="2020"):
    """分析各 topic 的年度趋势"""
    year_topic = defaultdict(lambda: defaultdict(int))

    for p in papers:
        year = (p.get("date") or "")[:4]
        if not year or year < start_year:
            continue
        text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                year_topic[year][topic] += 1

    return dict(year_topic)


def find_hot_new_topics(papers, min_year="2024", min_count=5):
    """找最近突然出现的新热点（2024+才有但增长快的）"""
    from collections import Counter

    # 提取所有论文的关键短语（简单的 bigram 分析）
    recent_bigrams = Counter()
    old_bigrams = Counter()

    for p in papers:
        year = (p.get("date") or "")[:4]
        if not year:
            continue
        title_words = p.get("title", "").lower().split()
        bigrams = [f"{title_words[i]} {title_words[i+1]}" for i in range(len(title_words)-1)]

        if year >= min_year:
            recent_bigrams.update(bigrams)
        elif year >= "2022":
            old_bigrams.update(bigrams)

    # 找"最近多但以前少"的
    emerging = []
    for bigram, count in recent_bigrams.most_common(500):
        if count < min_count:
            continue
        old_count = old_bigrams.get(bigram, 0)
        if old_count == 0:
            ratio = float('inf')
        else:
            ratio = count / old_count
        if ratio > 3:  # 增长 3 倍以上
            emerging.append((bigram, count, old_count, ratio))

    emerging.sort(key=lambda x: x[1], reverse=True)
    return emerging[:30]


def cross_kb_analysis(quantum_dir, ml_dir):
    """跨 KB 分析：找量子+ML 的交叉热点"""
    q_papers = load_papers(quantum_dir)
    m_papers = load_papers(ml_dir)

    cross_topics = {
        "diffusion+quantum": {
            "q_kw": ["diffusion model", "denoising diffusion", "score matching"],
            "m_kw": ["quantum", "qubit"],
        },
        "RL+quantum": {
            "q_kw": ["reinforcement learning", "policy gradient", "actor-critic"],
            "m_kw": ["quantum", "qubit"],
        },
        "GNN+quantum": {
            "q_kw": ["graph neural", "message passing neural", "GNN"],
            "m_kw": ["quantum", "qubit"],
        },
        "transformer+quantum": {
            "q_kw": ["transformer", "attention mechanism"],
            "m_kw": ["quantum", "qubit"],
        },
    }

    print("=== Cross-domain Analysis: Quantum x ML ===\n")

    for topic, kws in cross_topics.items():
        # Count in quantum KB
        q_count = 0
        q_recent = 0
        for p in q_papers:
            text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
            if any(kw in text for kw in kws["q_kw"]):
                q_count += 1
                if (p.get("date") or "") >= "2024-01":
                    q_recent += 1

        # Count in ML KB
        m_count = 0
        m_recent = 0
        for p in m_papers:
            text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
            if any(kw in text for kw in kws["m_kw"]):
                m_count += 1
                if (p.get("date") or "") >= "2024-01":
                    m_recent += 1

        print(f"  {topic:25s} | Quantum KB: {q_count:>4} ({q_recent} since 2024) | ML KB: {m_count:>4} ({m_recent} since 2024)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Research Trend Analysis")
    parser.add_argument("--kb", choices=["quantum", "ml", "cross"], default="quantum")
    parser.add_argument("--start-year", default="2020")
    parser.add_argument("--emerging", action="store_true", help="Find emerging topics")
    args = parser.parse_args()

    QUANTUM_DIR = "F:/数据集/论文/paper_kb"
    ML_DIR = "F:/数据集/论文/rl_kb"

    if args.kb == "cross":
        cross_kb_analysis(QUANTUM_DIR, ML_DIR)
    else:
        base_dir = QUANTUM_DIR if args.kb == "quantum" else ML_DIR
        papers = load_papers(base_dir)
        print(f"Loaded {len(papers)} papers from {args.kb} KB\n")

        if args.kb == "quantum":
            topic_kw = {
                "QEC": ["quantum error correction", "surface code", "LDPC", "fault tolerant"],
                "QML": ["quantum machine learning", "variational quantum", "quantum neural"],
                "Compilation": ["quantum circuit compilation", "qubit mapping", "qubit routing", "transpil"],
                "Hardware": ["superconducting qubit", "trapped ion", "neutral atom", "quantum processor"],
                "Simulation": ["quantum simulation", "hamiltonian simulation"],
                "Networking": ["quantum network", "quantum internet", "entanglement distribution"],
                "Optimization": ["QAOA", "quantum annealing", "quantum approximate optimization"],
                "Cryptography": ["quantum key distribution", "post-quantum cryptography"],
            }
        else:
            topic_kw = {
                "Offline RL": ["offline reinforcement", "batch reinforcement"],
                "MARL": ["multi-agent reinforcement", "multi-agent rl"],
                "RL+LLM": ["RLHF", "reinforcement learning from human", "language model reinforcement"],
                "GNN": ["graph neural network", "graph attention", "graph transformer"],
                "Diffusion": ["diffusion model", "denoising diffusion", "score matching", "flow matching"],
                "Discrete Diff": ["discrete diffusion"],
                "Neural CO": ["neural combinatorial optimization", "learning to optimize"],
                "Model-based RL": ["model-based reinforcement", "world model", "dreamer"],
                "Safe RL": ["safe reinforcement", "constrained reinforcement"],
            }

        trends = analyze_trends(papers, topic_kw, args.start_year)

        all_topics = sorted(topic_kw.keys())
        years = sorted(trends.keys())

        # Print table
        header = f"{'Year':<6}" + "".join(f"{t[:12]:>13}" for t in all_topics)
        print(header)
        print("-" * len(header))
        for year in years:
            row = f"{year:<6}"
            for t in all_topics:
                row += f"{trends[year].get(t, 0):>13}"
            print(row)

        # Growth rates
        if "2023" in trends and "2025" in trends:
            print(f"\n=== Growth 2023 -> 2025 ===")
            growth_list = []
            for t in all_topics:
                v23 = trends["2023"].get(t, 0)
                v25 = trends["2025"].get(t, 0)
                g = ((v25 - v23) / v23 * 100) if v23 > 0 else float('inf')
                growth_list.append((t, v23, v25, g))
            growth_list.sort(key=lambda x: x[3], reverse=True)
            for t, v23, v25, g in growth_list:
                arrow = "+" if g > 0 else ""
                print(f"  {t:25s} {v23:>5} -> {v25:>5} ({arrow}{g:.0f}%)")

        if args.emerging:
            print(f"\n=== Emerging Topics (new since 2024) ===")
            emerging = find_hot_new_topics(papers)
            for bigram, recent, old, ratio in emerging[:20]:
                print(f"  {bigram:35s} recent={recent:>4}  old={old:>4}  ratio={ratio:.1f}x")
