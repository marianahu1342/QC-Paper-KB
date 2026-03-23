#!/usr/bin/env python3
"""
量子计算论文知识库 - 每日更新脚本
从 Semantic Scholar、CrossRef、arXiv 拉取论文数据
"""

import json
import os
import sys
import io
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from typing import Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 添加 scripts 目录到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    VENUES, KEYWORD_GROUPS, SEMANTIC_SCHOLAR_API, SEMANTIC_SCHOLAR_FIELDS,
    SEMANTIC_SCHOLAR_RATE_LIMIT, SEMANTIC_SCHOLAR_API_KEY, CROSSREF_API, CROSSREF_MAILTO,
    PAPERS_DIR, LAST_UPDATE_FILE, DATA_DIR
)


def api_get(url: str, headers: Optional[dict] = None, max_retries: int = 3) -> Optional[dict]:
    """带重试的 API GET 请求"""
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", f"PaperKB/1.0 (mailto:{CROSSREF_MAILTO})")
    # 如果是 S2 请求且有 API key，加上认证头
    if "semanticscholar.org" in url and SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait = min(2 ** attempt * 5, 60)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code == 404:
                return None
            else:
                print(f"  HTTP {e.code} for {url}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return None


def load_existing_papers(venue_id: str) -> dict:
    """加载已有论文数据，返回 {paper_id: paper_dict}"""
    filepath = os.path.join(PAPERS_DIR, f"{venue_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            papers = json.load(f)
        return {p["id"]: p for p in papers}
    return {}


def save_papers(venue_id: str, papers_dict: dict):
    """保存论文数据"""
    papers_list = sorted(papers_dict.values(), key=lambda p: p.get("date") or "", reverse=True)
    filepath = os.path.join(PAPERS_DIR, f"{venue_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(papers_list, f, ensure_ascii=False, indent=2)
    return len(papers_list)


# ============================================================
# Semantic Scholar 数据源
# ============================================================

def search_semantic_scholar(query: str, venue_filter: str = "", year_from: int = 2020,
                            limit: int = 100, offset: int = 0) -> list:
    """通过 Semantic Scholar 搜索论文"""
    params = {
        "query": query,
        "fields": SEMANTIC_SCHOLAR_FIELDS,
        "limit": min(limit, 100),
        "offset": offset,
    }
    if venue_filter:
        params["venue"] = venue_filter
    if year_from:
        params["year"] = f"{year_from}-"

    url = f"{SEMANTIC_SCHOLAR_API}/paper/search?{urllib.parse.urlencode(params)}"
    time.sleep(SEMANTIC_SCHOLAR_RATE_LIMIT)

    data = api_get(url)
    if not data or "data" not in data:
        return []
    return data["data"]


def s2_paper_to_record(paper: dict, venue_id: str) -> Optional[dict]:
    """将 Semantic Scholar 论文转换为我们的格式"""
    if not paper.get("title"):
        return None

    ext_ids = paper.get("externalIds") or {}
    doi = ext_ids.get("DOI", "")
    arxiv_id = ext_ids.get("ArXiv", "")

    # 生成唯一 ID
    paper_id = doi if doi else (f"arxiv:{arxiv_id}" if arxiv_id else f"s2:{paper.get('paperId', '')}")
    if not paper_id:
        return None

    authors = []
    for a in (paper.get("authors") or []):
        if a.get("name"):
            authors.append(a["name"])

    tldr_text = ""
    if paper.get("tldr") and paper["tldr"].get("text"):
        tldr_text = paper["tldr"]["text"]

    return {
        "id": paper_id,
        "arxiv_id": arxiv_id,
        "title": paper["title"],
        "authors": authors,
        "date": paper.get("publicationDate", ""),
        "venue": venue_id,
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""),
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        "citations": paper.get("citationCount", 0),
        "abstract": paper.get("abstract", ""),
        "tldr": tldr_text,
        "summary": None,
        "topics": [],
        "needs_summary": True,
        "first_fetched": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }


def fetch_papers_for_venue_s2(venue_id: str, venue_info: dict, existing: dict) -> dict:
    """从 Semantic Scholar 获取某个 venue 的量子计算论文"""
    s2_venue = venue_info.get("semantic_scholar_venue", "")
    new_papers = {}
    total_fetched = 0

    for group_name, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            print(f"  [{venue_id}] Searching S2: '{kw}' in '{s2_venue}'...")
            papers = search_semantic_scholar(
                query=kw,
                venue_filter=s2_venue,
                year_from=2020,
                limit=100,
            )

            for p in papers:
                record = s2_paper_to_record(p, venue_id)
                if not record:
                    continue

                pid = record["id"]
                if pid in existing:
                    # 更新引用数
                    existing[pid]["citations"] = record["citations"]
                    existing[pid]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                elif pid not in new_papers:
                    new_papers[pid] = record
                    total_fetched += 1

            if total_fetched > 0 and total_fetched % 50 == 0:
                print(f"    ... {total_fetched} new papers so far")

    return new_papers


# ============================================================
# CrossRef 数据源（补充 DOI 和引用数据）
# ============================================================

def search_crossref(query: str, issn: str = "", rows: int = 50) -> list:
    """通过 CrossRef 搜索论文"""
    params = {
        "query": query,
        "rows": rows,
        "sort": "published",
        "order": "desc",
        "mailto": CROSSREF_MAILTO,
    }
    if issn:
        # 使用 filter 限定期刊
        params["filter"] = f"issn:{issn}"

    url = f"{CROSSREF_API}?{urllib.parse.urlencode(params)}"
    time.sleep(0.5)  # CrossRef polite pool

    data = api_get(url)
    if not data or "message" not in data or "items" not in data["message"]:
        return []
    return data["message"]["items"]


def crossref_paper_to_record(item: dict, venue_id: str) -> Optional[dict]:
    """将 CrossRef 记录转换为我们的格式"""
    doi = item.get("DOI", "")
    if not doi:
        return None

    title_list = item.get("title", [])
    title = title_list[0] if title_list else ""
    if not title:
        return None

    authors = []
    for a in (item.get("author") or []):
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            authors.append(name)

    # 解析日期
    date = ""
    pub_date = item.get("published") or item.get("created")
    if pub_date and "date-parts" in pub_date:
        parts = pub_date["date-parts"][0]
        if len(parts) >= 3:
            date = f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}"
        elif len(parts) >= 2:
            date = f"{parts[0]:04d}-{parts[1]:02d}-01"
        elif len(parts) >= 1:
            date = f"{parts[0]:04d}-01-01"

    abstract = item.get("abstract", "")
    # CrossRef abstract 有时带 HTML
    if abstract:
        import re
        abstract = re.sub(r"<[^>]+>", "", abstract)

    return {
        "id": doi,
        "arxiv_id": "",
        "title": title,
        "authors": authors,
        "date": date,
        "venue": venue_id,
        "doi": doi,
        "url": f"https://doi.org/{doi}",
        "arxiv_url": "",
        "citations": item.get("is-referenced-by-count", 0),
        "abstract": abstract,
        "tldr": "",
        "summary": None,
        "topics": [],
        "needs_summary": True,
        "first_fetched": datetime.now().strftime("%Y-%m-%d"),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }


def fetch_papers_for_venue_crossref(venue_id: str, venue_info: dict, existing: dict) -> dict:
    """从 CrossRef 获取某个 venue 的量子计算论文"""
    issn = venue_info.get("crossref_issn", "")
    if not issn:
        return {}

    new_papers = {}
    for group_name, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            print(f"  [{venue_id}] Searching CrossRef: '{kw}'...")
            items = search_crossref(query=kw, issn=issn, rows=50)

            for item in items:
                record = crossref_paper_to_record(item, venue_id)
                if not record:
                    continue

                pid = record["id"]
                if pid in existing:
                    # 更新引用数（取较大值）
                    if record["citations"] > existing[pid].get("citations", 0):
                        existing[pid]["citations"] = record["citations"]
                    existing[pid]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                elif pid not in new_papers:
                    new_papers[pid] = record

    return new_papers


# ============================================================
# arXiv 数据源（补充）
# ============================================================

def search_arxiv(query: str, max_results: int = 50) -> list:
    """通过 arXiv API 搜索论文"""
    import xml.etree.ElementTree as ET

    # Build proper arXiv query: quote multi-word phrases
    if " " in query:
        kw_query = f'all:"{query}"'
    else:
        kw_query = f"all:{query}"
    params = {
        "search_query": f"cat:quant-ph AND {kw_query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
    time.sleep(3)  # arXiv 要求 3 秒间隔

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode()
    except Exception as e:
        print(f"  arXiv error: {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    results = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        id_el = entry.find("atom:id", ns)

        if not all([title_el, id_el]):
            continue

        # 提取 arXiv ID
        arxiv_url = id_el.text.strip()
        arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else ""

        # 提取作者
        authors = []
        for author in entry.findall("atom:author", ns):
            name_el = author.find("atom:name", ns)
            if name_el is not None:
                authors.append(name_el.text.strip())

        # 提取日期
        date = ""
        if published_el is not None:
            date = published_el.text.strip()[:10]

        # 提取 DOI（如果有）
        doi = ""
        doi_el = entry.find("arxiv:doi", ns)
        if doi_el is not None:
            doi = doi_el.text.strip()

        results.append({
            "arxiv_id": arxiv_id,
            "title": " ".join(title_el.text.strip().split()),
            "authors": authors,
            "date": date,
            "doi": doi,
            "abstract": " ".join(summary_el.text.strip().split()) if summary_el is not None else "",
            "url": arxiv_url,
        })

    return results


def fetch_arxiv_supplement(existing_all_ids: set) -> dict:
    """从 arXiv 获取补充论文（未在任何 venue 中出现的重要预印本）"""
    new_papers = {}

    for group_name, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            print(f"  [arXiv] Searching: '{kw}'...")
            results = search_arxiv(query=kw, max_results=30)

            for r in results:
                arxiv_id = r["arxiv_id"]
                doi = r["doi"]

                # 跳过已在某个 venue 中的论文
                pid = doi if doi else f"arxiv:{arxiv_id}"
                if pid in existing_all_ids or doi in existing_all_ids:
                    continue

                new_papers[pid] = {
                    "id": pid,
                    "arxiv_id": arxiv_id,
                    "title": r["title"],
                    "authors": r["authors"],
                    "date": r["date"],
                    "venue": "arxiv",
                    "doi": doi,
                    "url": f"https://doi.org/{doi}" if doi else r["url"],
                    "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                    "citations": 0,
                    "abstract": r["abstract"],
                    "tldr": "",
                    "summary": None,
                    "topics": [],
                    "needs_summary": True,
                    "first_fetched": datetime.now().strftime("%Y-%m-%d"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                }

    return new_papers


# ============================================================
# arXiv 独立全量采集（不限于补充）
# ============================================================

def fetch_arxiv_recent(days: int = 30, max_per_keyword: int = 200) -> dict:
    """从 arXiv API 拉取最近 N 天的量子计算新论文"""
    new_papers = {}

    for group_name, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            print(f"  [arXiv-recent] Searching: '{kw}' (last {days} days)...")
            results = search_arxiv(query=kw, max_results=max_per_keyword)

            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            for r in results:
                if r["date"] < cutoff:
                    continue

                arxiv_id = r["arxiv_id"]
                doi = r["doi"]
                pid = f"arxiv:{arxiv_id}" if arxiv_id else (doi if doi else "")
                if not pid:
                    continue

                if pid not in new_papers:
                    new_papers[pid] = {
                        "id": pid,
                        "arxiv_id": arxiv_id,
                        "title": r["title"],
                        "authors": r["authors"],
                        "date": r["date"],
                        "venue": "arxiv",
                        "doi": doi,
                        "url": f"https://doi.org/{doi}" if doi else r["url"],
                        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                        "citations": 0,
                        "abstract": r["abstract"],
                        "tldr": "",
                        "summary": None,
                        "topics": [],
                        "needs_summary": True,
                        "first_fetched": datetime.now().strftime("%Y-%m-%d"),
                        "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    }

    return new_papers


def fetch_arxiv_highcited_via_s2(existing: dict) -> dict:
    """通过 Semantic Scholar 拉取 arXiv 上的量子计算论文（不限是否已发表）"""
    new_papers = {}

    # 覆盖面更广的关键词
    broad_queries = [
        "quantum error correction",
        "quantum computing",
        "quantum circuit",
        "quantum algorithm",
        "variational quantum",
        "quantum machine learning",
        "surface code",
        "quantum compilation",
        "fault tolerant quantum",
        "quantum decoder",
        "quantum optimization",
        "quantum simulation",
        "quantum processor",
        "qubit mapping",
        "quantum noise",
        "quantum gate",
        "LDPC quantum code",
        "quantum annealing",
        "quantum chemistry",
        "quantum walk",
    ]

    for query in broad_queries:
        # 每个关键词拉多页（offset 0 和 100）
        for offset in [0, 100]:
            print(f"  [arXiv-S2] Searching: '{query}' (offset={offset})...")

            params = {
                "query": query,
                "fields": SEMANTIC_SCHOLAR_FIELDS,
                "limit": 100,
                "offset": offset,
                "year": "2023-",
            }
            url = f"{SEMANTIC_SCHOLAR_API}/paper/search?{urllib.parse.urlencode(params)}"
            time.sleep(SEMANTIC_SCHOLAR_RATE_LIMIT)

            data = api_get(url)
            if not data or "data" not in data:
                continue

            for p in data["data"]:
                ext_ids = p.get("externalIds") or {}
                arxiv_id = ext_ids.get("ArXiv", "")
                if not arxiv_id:
                    continue

                doi = ext_ids.get("DOI", "")
                pid = f"arxiv:{arxiv_id}"

                if pid in existing or pid in new_papers:
                    # 更新引用数
                    if pid in existing:
                        existing[pid]["citations"] = p.get("citationCount", 0)
                        existing[pid]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                    continue

                authors = [a["name"] for a in (p.get("authors") or []) if a.get("name")]
                tldr_text = ""
                if p.get("tldr") and p["tldr"].get("text"):
                    tldr_text = p["tldr"]["text"]

                new_papers[pid] = {
                    "id": pid,
                    "arxiv_id": arxiv_id,
                    "title": p.get("title", ""),
                    "authors": authors,
                    "date": p.get("publicationDate") or "",
                    "venue": "arxiv",
                    "doi": doi,
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
                    "citations": p.get("citationCount", 0),
                    "abstract": p.get("abstract") or "",
                    "tldr": tldr_text,
                    "summary": None,
                    "topics": [],
                    "needs_summary": True,
                    "first_fetched": datetime.now().strftime("%Y-%m-%d"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                }

    return new_papers


def fetch_arxiv_by_keyword(keyword: str, max_results: int = 1000) -> list:
    """从 arXiv 按关键词搜索量子计算论文，支持大批量"""
    import xml.etree.ElementTree as ET

    all_results = []
    batch_size = 200  # arXiv 推荐每次不超过 200

    for offset in range(0, max_results, batch_size):
        fetch_size = min(batch_size, max_results - offset)
        # arXiv API: quote multi-word phrases for exact matching
        if " " in keyword:
            kw_query = f'all:"{keyword}"'
        else:
            kw_query = f"all:{keyword}"
        query = f"cat:quant-ph AND {kw_query}"
        params = {
            "search_query": query,
            "start": offset,
            "max_results": fetch_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
        print(f"    [DEBUG] URL: {url[:120]}...", flush=True)
        time.sleep(3)

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read().decode()
            print(f"    [DEBUG] Response length: {len(content)}", flush=True)
        except Exception as e:
            print(f"    arXiv error: {e}")
            break

        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            print(f"    [DEBUG] XML parse error", flush=True)
            break

        entries = root.findall("atom:entry", ns)
        print(f"    [DEBUG] Entries found: {len(entries)}", flush=True)
        if not entries:
            break

        for entry in entries:
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            published_el = entry.find("atom:published", ns)
            id_el = entry.find("atom:id", ns)

            if title_el is None or id_el is None:
                continue

            arxiv_url = id_el.text.strip()
            arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else ""
            if not arxiv_id:
                continue

            authors = []
            for author in entry.findall("atom:author", ns):
                name_el = author.find("atom:name", ns)
                if name_el is not None:
                    authors.append(name_el.text.strip())

            date = ""
            if published_el is not None:
                date = published_el.text.strip()[:10]

            doi = ""
            doi_el = entry.find("arxiv:doi", ns)
            if doi_el is not None:
                doi = doi_el.text.strip()

            all_results.append({
                "arxiv_id": arxiv_id,
                "title": " ".join(title_el.text.strip().split()),
                "authors": authors,
                "date": date,
                "doi": doi,
                "abstract": " ".join(summary_el.text.strip().split()) if summary_el is not None else "",
                "url": arxiv_url,
            })

        if len(entries) < fetch_size:
            break

    return all_results


def run_arxiv_full_update():
    """arXiv 独立全量更新：批量拉 quant-ph + S2 补引用数"""
    os.makedirs(PAPERS_DIR, exist_ok=True)

    print(f"\n=== arXiv Full Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    existing = load_existing_papers("arxiv")
    existing_count = len(existing)
    print(f"  Existing arXiv papers: {existing_count}")

    # 收集所有已在 venue 文件中的论文 ID（用于排除已发表的）
    all_venue_ids = set()
    for fname in os.listdir(PAPERS_DIR):
        if fname.endswith(".json") and fname != "arxiv.json" and fname != "arxiv_supplement.json":
            fpath = os.path.join(PAPERS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    venue_papers = json.load(f)
                for p in venue_papers:
                    if p.get("arxiv_id"):
                        all_venue_ids.add(f"arxiv:{p['arxiv_id']}")
                    if p.get("doi"):
                        all_venue_ids.add(p["doi"])
            except Exception:
                pass
    print(f"  Papers already in venue files: {len(all_venue_ids)}")

    # Phase 1: 按关键词从 arXiv 搜索量子计算论文
    arxiv_search_keywords = [
        "quantum computing",
        "quantum error correction",
        "quantum circuit",
        "qubit",
        "surface code",
        "quantum algorithm",
        "variational quantum",
        "quantum machine learning",
        "fault tolerant quantum",
        "quantum compilation",
        "quantum decoder",
        "LDPC quantum",
        "quantum optimization",
        "quantum simulation",
        "quantum annealing",
        "quantum processor",
        "quantum chemistry",
        "quantum walk",
        "quantum gate synthesis",
        "superconducting qubit",
    ]

    print(f"\n  Phase 1: Keyword search on arXiv ({len(arxiv_search_keywords)} keywords, 1000 each)...")
    bulk_results = []
    seen_ids = set()
    for kw in arxiv_search_keywords:
        print(f"  [arXiv] Searching: '{kw}'...")
        results = fetch_arxiv_by_keyword(kw, max_results=1000)
        for r in results:
            if r["arxiv_id"] not in seen_ids:
                seen_ids.add(r["arxiv_id"])
                bulk_results.append(r)
        print(f"    +{len(results)} results, {len(bulk_results)} unique total")

    print(f"  Total unique QC papers from arXiv: {len(bulk_results)}")

    new_papers = {}
    skipped_published = 0
    for r in bulk_results:
        arxiv_id = r["arxiv_id"]
        doi = r["doi"]
        pid = f"arxiv:{arxiv_id}"

        # 跳过已在 venue 文件中的（已发表的）
        if pid in all_venue_ids or (doi and doi in all_venue_ids):
            skipped_published += 1
            continue

        if pid in existing or pid in new_papers:
            continue

        new_papers[pid] = {
            "id": pid,
            "arxiv_id": arxiv_id,
            "title": r["title"],
            "authors": r["authors"],
            "date": r["date"],
            "venue": "arxiv",
            "doi": doi,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
            "citations": 0,
            "abstract": r["abstract"],
            "tldr": "",
            "summary": None,
            "topics": [],
            "needs_summary": True,
            "first_fetched": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }

    print(f"  Skipped (already in venue files): {skipped_published}")
    print(f"  Candidate new preprints: {len(new_papers)}")

    # Phase 1.5: 通过 S2 批量检查新论文是否已发表（有 venue/journal）
    print(f"\n  Phase 1.5: Checking S2 for venue info on {len(new_papers)} candidates...")
    candidates = list(new_papers.items())
    s2_skipped = 0
    s2_checked = 0
    batch_size_s2 = 50  # S2 batch API 每次最多 500，但我们分小批
    for batch_start in range(0, len(candidates), batch_size_s2):
        batch_items = candidates[batch_start:batch_start + batch_size_s2]
        arxiv_ids_batch = []
        pid_map = {}  # arxiv_id -> pid
        for pid, paper in batch_items:
            aid = paper.get("arxiv_id", "")
            if aid:
                arxiv_ids_batch.append(f"ArXiv:{aid}")
                pid_map[f"ArXiv:{aid}"] = pid

        if not arxiv_ids_batch:
            continue

        # S2 batch paper lookup
        s2_batch_url = f"{SEMANTIC_SCHOLAR_API}/paper/batch"
        post_data = json.dumps({"ids": arxiv_ids_batch}).encode("utf-8")
        params_s2 = {"fields": "venue,journal,citationCount"}
        full_url = f"{s2_batch_url}?{urllib.parse.urlencode(params_s2)}"
        time.sleep(SEMANTIC_SCHOLAR_RATE_LIMIT)

        try:
            req = urllib.request.Request(full_url, data=post_data, method="POST")
            req.add_header("Content-Type", "application/json")
            if SEMANTIC_SCHOLAR_API_KEY:
                req.add_header("x-api-key", SEMANTIC_SCHOLAR_API_KEY)
            with urllib.request.urlopen(req, timeout=30) as resp:
                s2_results = json.loads(resp.read().decode())
        except Exception as e:
            print(f"    S2 batch error: {e}")
            continue

        for i, s2_paper in enumerate(s2_results):
            if s2_paper is None:
                continue
            s2_checked += 1
            s2_id = arxiv_ids_batch[i]
            pid = pid_map.get(s2_id, "")
            if not pid:
                continue

            venue = (s2_paper.get("venue") or "").strip()
            journal_name = ""
            if s2_paper.get("journal"):
                journal_name = (s2_paper["journal"].get("name") or "").strip()

            # If the paper has a venue or journal, it's published - skip it
            if venue or journal_name:
                del new_papers[pid]
                s2_skipped += 1
            else:
                # Update citation count from S2
                cit = s2_paper.get("citationCount", 0)
                if cit and pid in new_papers:
                    new_papers[pid]["citations"] = cit

        if (batch_start // batch_size_s2) % 10 == 0 and batch_start > 0:
            print(f"    Checked {s2_checked}, skipped {s2_skipped} published...")

    print(f"  S2 venue check: {s2_checked} checked, {s2_skipped} skipped (published)")
    print(f"  Final new preprints: {len(new_papers)}")

    # Phase 2: 用 S2 补充已有论文的引用数
    print(f"\n  Phase 2: Updating citations via S2...")
    updated_citations = 0
    batch = list(existing.keys())[:200]  # 每天更新前200篇的引用
    for pid in batch:
        arxiv_id = existing[pid].get("arxiv_id", "")
        if not arxiv_id:
            continue
        s2_url = f"{SEMANTIC_SCHOLAR_API}/paper/ArXiv:{arxiv_id}?fields=citationCount"
        time.sleep(SEMANTIC_SCHOLAR_RATE_LIMIT)
        data = api_get(s2_url)
        if data and "citationCount" in data:
            old_cit = existing[pid].get("citations", 0)
            new_cit = data["citationCount"]
            if new_cit != old_cit:
                existing[pid]["citations"] = new_cit
                existing[pid]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                updated_citations += 1
    print(f"  Citations updated: {updated_citations}")

    # 合并
    merged = dict(existing)
    merged.update(new_papers)

    new_count = len(merged) - existing_count
    total = save_papers("arxiv", merged)
    print(f"  Total arXiv papers: {total} (+{new_count} new)")

    return {"total": total, "new": new_count}


# ============================================================
# 主流程
# ============================================================

def merge_papers(existing: dict, new_s2: dict, new_cr: dict) -> dict:
    """合并来自不同数据源的论文，去重"""
    merged = dict(existing)

    # 先合入 CrossRef（DOI 为 key）
    for pid, paper in new_cr.items():
        if pid not in merged:
            merged[pid] = paper

    # 再合入 Semantic Scholar（可能有更好的 abstract 和 tldr）
    for pid, paper in new_s2.items():
        if pid in merged:
            # 补充缺失字段
            if not merged[pid].get("abstract") and paper.get("abstract"):
                merged[pid]["abstract"] = paper["abstract"]
            if not merged[pid].get("tldr") and paper.get("tldr"):
                merged[pid]["tldr"] = paper["tldr"]
            if not merged[pid].get("arxiv_id") and paper.get("arxiv_id"):
                merged[pid]["arxiv_id"] = paper["arxiv_id"]
                merged[pid]["arxiv_url"] = paper["arxiv_url"]
        else:
            merged[pid] = paper

    return merged


def run_daily_update(venue_ids: Optional[list] = None):
    """运行每日更新"""
    os.makedirs(PAPERS_DIR, exist_ok=True)

    if venue_ids is None:
        venue_ids = list(VENUES.keys())

    stats = {"venues_processed": 0, "new_papers": 0, "updated_papers": 0}
    all_paper_ids = set()

    print(f"=== Daily Update Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Processing {len(venue_ids)} venues...\n")

    for venue_id in venue_ids:
        venue_info = VENUES.get(venue_id)
        if not venue_info:
            print(f"[SKIP] Unknown venue: {venue_id}")
            continue

        print(f"\n--- {venue_id} ({venue_info['full_name']}) ---")

        # 加载已有数据
        existing = load_existing_papers(venue_id)
        existing_count = len(existing)
        print(f"  Existing papers: {existing_count}")

        # 从 Semantic Scholar 获取
        new_s2 = fetch_papers_for_venue_s2(venue_id, venue_info, existing)
        print(f"  New from S2: {len(new_s2)}")

        # 从 CrossRef 获取（仅期刊）
        new_cr = {}
        if venue_info.get("crossref_issn"):
            new_cr = fetch_papers_for_venue_crossref(venue_id, venue_info, existing)
            print(f"  New from CrossRef: {len(new_cr)}")

        # 合并
        merged = merge_papers(existing, new_s2, new_cr)
        new_count = len(merged) - existing_count

        # 保存
        total = save_papers(venue_id, merged)
        print(f"  Total papers: {total} (+{new_count} new)")

        stats["venues_processed"] += 1
        stats["new_papers"] += new_count
        all_paper_ids.update(merged.keys())

    # arXiv 全量更新（独立数据源）
    print(f"\n--- arXiv Full Update ---")
    arxiv_stats = run_arxiv_full_update()
    stats["new_papers"] += arxiv_stats["new"]

    # 保存更新时间
    update_info = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
    }
    with open(LAST_UPDATE_FILE, "w", encoding="utf-8") as f:
        json.dump(update_info, f, ensure_ascii=False, indent=2)

    print(f"\n=== Update Complete ===")
    print(f"Venues: {stats['venues_processed']}, New papers: {stats['new_papers']}")
    return stats


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--arxiv-only":
        # 只跑 arXiv
        run_arxiv_full_update()
    elif len(sys.argv) > 1:
        # 指定 venue
        venues = sys.argv[1:]
        run_daily_update(venues)
    else:
        # 全量更新（含 arXiv）
        run_daily_update()
