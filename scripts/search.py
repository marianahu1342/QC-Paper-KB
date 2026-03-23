#!/usr/bin/env python3
"""
量子计算论文知识库 - 检索接口
支持按 venue、关键词、topic 搜索，支持排序和过滤
"""

import json
import os
import sys
import argparse
import re
import io
from typing import Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import VENUES, PAPERS_DIR, VENUES_FILE, DATA_DIR


def load_all_papers(venue_ids: Optional[list] = None, dedup: bool = True) -> list:
    """加载所有论文数据，支持去重。

    去重策略：同一篇论文可能出现在 venue 文件和 arXiv 文件中，
    优先保留 venue 版本（有正式发表信息），用 DOI > arxiv_id > title 作为 key。
    """
    all_papers = []
    if venue_ids is None:
        if not os.path.exists(PAPERS_DIR):
            return []
        # 先加载非 arXiv 文件（优先保留 venue 版本）
        fnames = sorted(os.listdir(PAPERS_DIR))
        non_arxiv = [f for f in fnames if f.endswith(".json") and not f.startswith("arxiv")]
        arxiv_files = [f for f in fnames if f.endswith(".json") and f.startswith("arxiv")]
        for fname in non_arxiv + arxiv_files:
            fpath = os.path.join(PAPERS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                papers = json.load(f)
            all_papers.extend(papers)
    else:
        for vid in venue_ids:
            fpath = os.path.join(PAPERS_DIR, f"{vid}.json")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    papers = json.load(f)
                all_papers.extend(papers)

    if dedup and len(all_papers) > 0:
        seen = set()
        unique = []
        for p in all_papers:
            # 用 DOI > arxiv_id > title 前50字符 作为去重 key
            key = p.get("doi") or p.get("arxiv_id") or p.get("title", "")[:50].lower()
            if key and key not in seen:
                seen.add(key)
                unique.append(p)
            elif not key:
                unique.append(p)  # 无法判断的保留
        all_papers = unique

    return all_papers


def search_papers(
    query: str = "",
    venue: Optional[str] = None,
    venues: Optional[list] = None,
    sort_by: str = "date",  # "date", "citations"
    limit: int = 20,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    needs_summary: Optional[bool] = None,
    expand: bool = False,
) -> list:
    """搜索论文。expand=True 时对查询词做同义词扩展。"""
    venue_ids = None
    if venue:
        venue_ids = [venue]
    elif venues:
        venue_ids = venues

    papers = load_all_papers(venue_ids)

    # 关键词过滤
    if query:
        if expand:
            # 扩展模式：查询词拆分后每个都扩展，匹配任一扩展词即可
            expanded = expand_keywords(query.lower().split())
            filtered = []
            for p in papers:
                text = f"{p.get('title', '')} {p.get('abstract', '')} {p.get('tldr', '')}".lower()
                if any(kw in text for kw in expanded):
                    filtered.append(p)
        else:
            # 原始模式：所有词都必须出现
            query_lower = query.lower()
            query_terms = query_lower.split()
            filtered = []
            for p in papers:
                text = f"{p.get('title', '')} {p.get('abstract', '')} {p.get('tldr', '')}".lower()
                if all(term in text for term in query_terms):
                    filtered.append(p)
        papers = filtered

    # 年份过滤
    if year_from:
        papers = [p for p in papers if (p.get("date") or "")[:4] >= str(year_from)]
    if year_to:
        papers = [p for p in papers if (p.get("date") or "")[:4] <= str(year_to)]

    # needs_summary 过滤
    if needs_summary is not None:
        papers = [p for p in papers if p.get("needs_summary") == needs_summary]

    # 排序
    if sort_by == "citations":
        papers.sort(key=lambda p: p.get("citations", 0), reverse=True)
    elif sort_by == "date":
        papers.sort(key=lambda p: (p.get("date") or ""), reverse=True)

    return papers[:limit]


def format_paper(p: dict, idx: int, verbose: bool = False) -> str:
    """格式化单篇论文输出"""
    lines = []
    lines.append(f"[{idx}] {p['title']}")
    lines.append(f"    Authors: {', '.join(p['authors'][:5])}" + ("..." if len(p['authors']) > 5 else ""))
    lines.append(f"    Venue: {p['venue']} | Date: {p.get('date', 'N/A')} | Citations: {p.get('citations', 0)}")
    lines.append(f"    URL: {p.get('url', 'N/A')}")

    if verbose:
        if p.get("tldr"):
            lines.append(f"    TLDR: {p['tldr']}")
        if p.get("abstract"):
            abstract = p["abstract"][:300] + "..." if len(p.get("abstract", "")) > 300 else p.get("abstract", "")
            lines.append(f"    Abstract: {abstract}")
        if p.get("summary"):
            s = p["summary"]
            if isinstance(s, dict):
                if s.get("method"):
                    lines.append(f"    Method: {s['method']}")
                if s.get("results"):
                    lines.append(f"    Results: {s['results']}")
                if s.get("baselines"):
                    lines.append(f"    Baselines: {', '.join(s['baselines'])}")
                if s.get("contribution"):
                    lines.append(f"    Contribution: {s['contribution']}")

    return "\n".join(lines)


def stats_by_venue() -> dict:
    """统计各 venue 论文数量"""
    stats = {}
    if not os.path.exists(PAPERS_DIR):
        return stats
    for fname in os.listdir(PAPERS_DIR):
        if fname.endswith(".json"):
            vid = fname[:-5]
            fpath = os.path.join(PAPERS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                papers = json.load(f)
            stats[vid] = {
                "total": len(papers),
                "needs_summary": sum(1 for p in papers if p.get("needs_summary")),
                "recent_6m": sum(1 for p in papers if (p.get("date") or "") >= "2025-09"),
            }
    return stats


def expand_keywords(keywords: list) -> list:
    """将用户关键词扩展为同义词族，提高搜索覆盖率。

    例如 "compilation" 会自动包含 "transpilation", "routing", "mapping" 等。
    返回去重后的扩展关键词列表。
    """
    # 预定义关键词族（topic clusters）
    TOPIC_CLUSTERS = {
        # 编译/优化方向
        "compilation": ["compilation", "transpilation", "transpiler", "circuit optimization",
                       "routing", "mapping", "qubit mapping", "qubit routing", "gate synthesis",
                       "circuit synthesis", "layout synthesis"],
        "ZX": ["ZX calculus", "ZX diagram", "ZX rewriting", "graph rewriting",
               "ZX-calculus", "pyzx", "spider fusion"],
        # 纠错方向
        "error correction": ["error correction", "QEC", "surface code", "stabilizer code",
                            "toric code", "color code", "LDPC", "fault tolerant",
                            "fault-tolerant", "decoder", "decoding"],
        "surface code": ["surface code", "rotated surface code", "planar code",
                        "toric code", "topological code"],
        # ML 方向
        "machine learning": ["machine learning", "neural network", "deep learning",
                           "reinforcement learning", "GNN", "graph neural",
                           "transformer", "diffusion model"],
        "reinforcement learning": ["reinforcement learning", "RL", "policy gradient",
                                  "actor-critic", "PPO", "DQN", "Q-learning"],
        "diffusion": ["diffusion model", "denoising diffusion", "DDPM",
                     "score matching", "flow matching", "generative model"],
        # 硬件方向
        "superconducting": ["superconducting", "transmon", "fluxonium",
                          "superconducting qubit", "cQED"],
        "trapped ion": ["trapped ion", "ion trap", "shuttling", "ion chain"],
        "neutral atom": ["neutral atom", "Rydberg", "optical tweezer", "atom array"],
        # 调度/多程序
        "scheduling": ["scheduling", "multiprogramming", "multi-programming",
                      "multi-tenant", "resource allocation", "job scheduling",
                      "circuit partitioning", "workload"],
        "crosstalk": ["crosstalk", "cross-talk", "frequency collision",
                     "ZZ interaction", "parasitic coupling", "qubit interference"],
        # 模拟
        "simulation": ["quantum simulation", "hamiltonian simulation",
                      "Trotter", "product formula", "variational simulation"],
        # 变分
        "variational": ["variational quantum", "VQE", "QAOA", "VQA",
                       "parameterized quantum circuit", "PQC", "ansatz"],
        # 量子网络
        "networking": ["quantum network", "quantum internet", "entanglement distribution",
                      "quantum repeater", "quantum communication"],
    }

    expanded = set()
    for kw in keywords:
        kw_lower = kw.lower()
        expanded.add(kw_lower)
        # 检查是否匹配某个 cluster
        for cluster_key, cluster_words in TOPIC_CLUSTERS.items():
            if kw_lower in cluster_key or cluster_key in kw_lower:
                expanded.update(w.lower() for w in cluster_words)
            # 也检查是否是 cluster 中的某个词
            for w in cluster_words:
                if kw_lower in w.lower() or w.lower() in kw_lower:
                    expanded.update(ww.lower() for ww in cluster_words)
                    break

    return list(expanded)


def recommend_venues(keywords: list, top_n: int = 10, expand: bool = True) -> list:
    """基于关键词自动扫描所有 venue，按接收密度排序推荐。

    对每个 venue 返回：
    - 匹配论文总数
    - 近3年匹配数
    - 最近一篇的日期和标题
    - 高引代表作

    expand=True 时自动扩展同义词（推荐开启）
    """
    # 关键词扩展
    if expand:
        expanded = expand_keywords(keywords)
        if len(expanded) > len(keywords):
            print(f"  Keywords expanded: {len(keywords)} → {len(expanded)}", flush=True)
    else:
        expanded = [kw.lower() for kw in keywords]

    # 加载 venue 元数据
    venues_data = {}
    if os.path.exists(VENUES_FILE):
        with open(VENUES_FILE, "r", encoding="utf-8") as f:
            venues_data = json.load(f)

    # 排除的文件
    skip_files = {"arxiv.json", "arxiv_supplement.json", "QCE.json", "QIP_conf.json"}

    results = []

    for fname in os.listdir(PAPERS_DIR):
        if not fname.endswith(".json") or fname in skip_files:
            continue
        vid = fname[:-5]
        fpath = os.path.join(PAPERS_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            papers = json.load(f)

        # 搜索匹配论文
        matched = []
        for p in papers:
            text = f"{p.get('title', '')} {p.get('abstract', '')} {p.get('tldr', '')}".lower()
            if any(kw in text for kw in expanded):
                matched.append(p)

        if not matched:
            continue

        # 按日期排序（最近的在前）
        matched.sort(key=lambda p: (p.get("date") or ""), reverse=True)

        # 近3年的（2023+）
        recent_3y = [p for p in matched if (p.get("date") or "") >= "2023-01"]
        # 近1年的（2025+）
        recent_1y = [p for p in matched if (p.get("date") or "") >= "2025-01"]

        # 最高引用
        top_cited = max(matched, key=lambda p: p.get("citations", 0))

        # venue 元数据
        vmeta = venues_data.get(vid, {})
        tier = vmeta.get("tier", "?")

        results.append({
            "venue": vid,
            "tier": tier,
            "total_match": len(matched),
            "recent_3y": len(recent_3y),
            "recent_1y": len(recent_1y),
            "latest": {
                "date": matched[0].get("date", "?"),
                "title": matched[0].get("title", "?")[:80],
                "citations": matched[0].get("citations", 0),
            },
            "top_cited": {
                "date": top_cited.get("date", "?"),
                "title": top_cited.get("title", "?")[:80],
                "citations": top_cited.get("citations", 0),
            },
        })

    # 排序：近3年匹配数 > 总匹配数
    results.sort(key=lambda x: (x["recent_3y"], x["total_match"]), reverse=True)
    return results[:top_n]


def stats_by_topic(query_topics: Optional[list] = None) -> dict:
    """按 topic 统计各 venue 发表情况"""
    if query_topics is None:
        query_topics = [
            "quantum error correction",
            "surface code",
            "quantum circuit compilation",
            "qubit mapping",
            "machine learning quantum",
            "variational quantum",
            "quantum optimization",
        ]

    papers = load_all_papers()
    topic_stats = {}

    for topic in query_topics:
        topic_lower = topic.lower()
        topic_papers = [
            p for p in papers
            if topic_lower in f"{p.get('title', '')} {p.get('abstract', '')}".lower()
        ]
        venue_counts = {}
        for p in topic_papers:
            v = p.get("venue", "unknown")
            venue_counts[v] = venue_counts.get(v, 0) + 1

        topic_stats[topic] = {
            "total": len(topic_papers),
            "by_venue": dict(sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)),
        }

    return topic_stats


def main():
    parser = argparse.ArgumentParser(description="量子计算论文知识库检索")
    sub = parser.add_subparsers(dest="command")

    # search 子命令
    search_p = sub.add_parser("search", help="搜索论文")
    search_p.add_argument("query", nargs="?", default="", help="搜索关键词")
    search_p.add_argument("--venue", "-v", help="限定 venue")
    search_p.add_argument("--sort", "-s", default="date", choices=["date", "citations"])
    search_p.add_argument("--limit", "-n", type=int, default=20)
    search_p.add_argument("--year-from", type=int)
    search_p.add_argument("--year-to", type=int)
    search_p.add_argument("--verbose", action="store_true")
    search_p.add_argument("--expand", action="store_true", help="启用同义词扩展搜索")

    # stats 子命令
    stats_p = sub.add_parser("stats", help="统计信息")
    stats_p.add_argument("--by", choices=["venue", "topic"], default="venue")

    # recommend 子命令
    rec_p = sub.add_parser("recommend", help="基于关键词自动推荐投稿 venue")
    rec_p.add_argument("keywords", nargs="+", help="关键词列表（空格分隔）")
    rec_p.add_argument("--top", "-n", type=int, default=10)
    rec_p.add_argument("--no-expand", action="store_true", help="禁用同义词扩展")

    # unsummarized 子命令
    unsum_p = sub.add_parser("unsummarized", help="列出未总结的论文")
    unsum_p.add_argument("--venue", "-v")
    unsum_p.add_argument("--limit", "-n", type=int, default=50)

    args = parser.parse_args()

    if args.command == "search":
        results = search_papers(
            query=args.query,
            venue=args.venue,
            sort_by=args.sort,
            limit=args.limit,
            year_from=args.year_from,
            year_to=args.year_to,
            expand=getattr(args, 'expand', False),
        )
        print(f"Found {len(results)} papers:\n")
        for i, p in enumerate(results, 1):
            print(format_paper(p, i, verbose=args.verbose))
            print()

    elif args.command == "stats":
        if args.by == "venue":
            stats = stats_by_venue()
            print(f"{'Venue':<20} {'Total':<8} {'Need Summary':<14} {'Recent 6m':<10}")
            print("-" * 52)
            for vid, s in sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True):
                print(f"{vid:<20} {s['total']:<8} {s['needs_summary']:<14} {s['recent_6m']:<10}")
        else:
            topic_stats = stats_by_topic()
            for topic, s in topic_stats.items():
                print(f"\n{topic}: {s['total']} papers")
                for v, cnt in list(s["by_venue"].items())[:5]:
                    print(f"  {v}: {cnt}")

    elif args.command == "recommend":
        recs = recommend_venues(args.keywords, top_n=args.top, expand=not getattr(args, 'no_expand', False))
        print(f"=== Venue Recommendation for: {', '.join(args.keywords)} ===\n")
        print(f"{'Venue':<15} {'Tier':<20} {'Match':<7} {'3yr':<5} {'1yr':<5} {'Latest':<12} {'Top Cited'}")
        print("-" * 105)
        for r in recs:
            top_str = f"{r['top_cited']['title'][:40]}... ({r['top_cited']['citations']}c)"
            print(f"{r['venue']:<15} {r['tier']:<20} {r['total_match']:<7} {r['recent_3y']:<5} {r['recent_1y']:<5} {r['latest']['date']:<12} {top_str}")
        print(f"\n--- Detail: latest paper per venue ---\n")
        for r in recs:
            print(f"[{r['venue']}] ({r['tier']})")
            print(f"  Latest: {r['latest']['date']} | {r['latest']['title']}")
            print(f"  Top cited: {r['top_cited']['citations']}c | {r['top_cited']['title']}")
            print()

    elif args.command == "unsummarized":
        results = search_papers(
            venue=args.venue,
            needs_summary=True,
            limit=args.limit,
            sort_by="date",
        )
        print(f"Unsummarized papers: {len(results)}\n")
        for i, p in enumerate(results, 1):
            print(f"[{i}] [{p['venue']}] {p['title']}")
            print(f"    {p.get('date', 'N/A')} | {p.get('url', '')}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
