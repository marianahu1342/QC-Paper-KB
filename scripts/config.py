"""
量子计算论文知识库 - 配置文件
定义所有 venue 和搜索关键词
"""

# ============================================================
# Venue 定义
# ============================================================

VENUES = {
    # ---- 顶级期刊 ----
    "Nature": {
        "full_name": "Nature",
        "type": "journal",
        "tier": "top",
        "publisher": "Springer Nature",
        "issn": "0028-0836",
        "semantic_scholar_venue": "Nature",
        "crossref_issn": "0028-0836",
    },
    "Science": {
        "full_name": "Science",
        "type": "journal",
        "tier": "top",
        "publisher": "AAAS",
        "issn": "0036-8075",
        "semantic_scholar_venue": "Science",
        "crossref_issn": "0036-8075",
    },
    "NatPhys": {
        "full_name": "Nature Physics",
        "type": "journal",
        "tier": "top",
        "publisher": "Springer Nature",
        "issn": "1745-2473",
        "semantic_scholar_venue": "Nature Physics",
        "crossref_issn": "1745-2473",
    },
    "PRL": {
        "full_name": "Physical Review Letters",
        "type": "journal",
        "tier": "top",
        "publisher": "APS",
        "issn": "0031-9007",
        "semantic_scholar_venue": "Physical Review Letters",
        "crossref_issn": "0031-9007",
    },
    "NC": {
        "full_name": "Nature Communications",
        "type": "journal",
        "tier": "top",
        "publisher": "Springer Nature",
        "issn": "2041-1723",
        "semantic_scholar_venue": "Nature Communications",
        "crossref_issn": "2041-1723",
    },

    # ---- 优秀期刊 ----
    "PRXQ": {
        "full_name": "PRX Quantum",
        "type": "journal",
        "tier": "excellent",
        "publisher": "APS",
        "issn": "2691-3399",
        "semantic_scholar_venue": "PRX Quantum",
        "crossref_issn": "2691-3399",
    },
    "PRX": {
        "full_name": "Physical Review X",
        "type": "journal",
        "tier": "excellent",
        "publisher": "APS",
        "issn": "2160-3308",
        "semantic_scholar_venue": "Physical Review X",
        "crossref_issn": "2160-3308",
    },
    "npjQI": {
        "full_name": "npj Quantum Information",
        "type": "journal",
        "tier": "excellent",
        "publisher": "Springer Nature",
        "issn": "2056-6387",
        "semantic_scholar_venue": "npj Quantum Information",
        "crossref_issn": "2056-6387",
    },

    # ---- 良好期刊 ----
    "QST": {
        "full_name": "Quantum Science and Technology",
        "type": "journal",
        "tier": "good",
        "publisher": "IOP",
        "issn": "2058-9565",
        "semantic_scholar_venue": "Quantum Science and Technology",
        "crossref_issn": "2058-9565",
    },
    "Quantum": {
        "full_name": "Quantum",
        "type": "journal",
        "tier": "good",
        "publisher": "Verein zur Förderung des Open Access Publizierens in den Quantenwissenschaften",
        "issn": "2521-327X",
        "semantic_scholar_venue": "Quantum",
        "crossref_issn": "2521-327X",
    },
    "AQT": {
        "full_name": "Advanced Quantum Technologies",
        "type": "journal",
        "tier": "good",
        "publisher": "Wiley",
        "issn": "2511-9044",
        "semantic_scholar_venue": "Advanced Quantum Technologies",
        "crossref_issn": "2511-9044",
    },

    # ---- 标准期刊 ----
    "PRA": {
        "full_name": "Physical Review A",
        "type": "journal",
        "tier": "standard",
        "publisher": "APS",
        "issn": "2469-9926",
        "semantic_scholar_venue": "Physical Review A",
        "crossref_issn": "2469-9926",
    },
    "PRApplied": {
        "full_name": "Physical Review Applied",
        "type": "journal",
        "tier": "standard",
        "publisher": "APS",
        "issn": "2331-7019",
        "semantic_scholar_venue": "Physical Review Applied",
        "crossref_issn": "2331-7019",
    },
    "PRResearch": {
        "full_name": "Physical Review Research",
        "type": "journal",
        "tier": "standard",
        "publisher": "APS",
        "issn": "2643-1564",
        "semantic_scholar_venue": "Physical Review Research",
        "crossref_issn": "2643-1564",
    },
    "TQE": {
        "full_name": "IEEE Transactions on Quantum Engineering",
        "type": "journal",
        "tier": "standard",
        "publisher": "IEEE",
        "issn": "2689-1808",
        "semantic_scholar_venue": "IEEE Transactions on Quantum Engineering",
        "crossref_issn": "2689-1808",
    },
    "TQC": {
        "full_name": "ACM Transactions on Quantum Computing",
        "type": "journal",
        "tier": "standard",
        "publisher": "ACM",
        "issn": "2643-6809",
        "semantic_scholar_venue": "ACM Transactions on Quantum Computing",
        "crossref_issn": "2643-6809",
    },
    "QIP_journal": {
        "full_name": "Quantum Information Processing",
        "type": "journal",
        "tier": "standard",
        "publisher": "Springer",
        "issn": "1570-0755",
        "semantic_scholar_venue": "Quantum Information Processing",
        "crossref_issn": "1570-0755",
    },
    "NJP": {
        "full_name": "New Journal of Physics",
        "type": "journal",
        "tier": "standard",
        "publisher": "IOP",
        "issn": "1367-2630",
        "semantic_scholar_venue": "New Journal of Physics",
        "crossref_issn": "1367-2630",
    },

    # ---- 会议：体系结构 ----
    "ASPLOS": {
        "full_name": "ACM International Conference on Architectural Support for Programming Languages and Operating Systems",
        "type": "conference",
        "tier": "top",
        "publisher": "ACM",
        "semantic_scholar_venue": "ASPLOS",
    },
    "MICRO": {
        "full_name": "IEEE/ACM International Symposium on Microarchitecture",
        "type": "conference",
        "tier": "top",
        "publisher": "IEEE/ACM",
        "semantic_scholar_venue": "MICRO",
    },
    "ISCA": {
        "full_name": "International Symposium on Computer Architecture",
        "type": "conference",
        "tier": "top",
        "publisher": "ACM/IEEE",
        "semantic_scholar_venue": "ISCA",
    },
    "HPCA": {
        "full_name": "IEEE International Symposium on High-Performance Computer Architecture",
        "type": "conference",
        "tier": "top",
        "publisher": "IEEE",
        "semantic_scholar_venue": "HPCA",
    },

    # ---- 会议：EDA ----
    "DAC": {
        "full_name": "Design Automation Conference",
        "type": "conference",
        "tier": "top",
        "publisher": "ACM/IEEE",
        "semantic_scholar_venue": "DAC",
    },
    "ICCAD": {
        "full_name": "IEEE/ACM International Conference on Computer-Aided Design",
        "type": "conference",
        "tier": "top",
        "publisher": "IEEE/ACM",
        "semantic_scholar_venue": "ICCAD",
    },

    # ---- 会议：量子专项 ----
    "QCE": {
        "full_name": "IEEE International Conference on Quantum Computing and Engineering",
        "type": "conference",
        "tier": "good",
        "publisher": "IEEE",
        "semantic_scholar_venue": "IEEE International Conference on Quantum Computing and Engineering",
    },
    "QIP_conf": {
        "full_name": "Quantum Information Processing Conference",
        "type": "conference",
        "tier": "excellent",
        "publisher": "Various",
        "semantic_scholar_venue": "QIP",
    },
}

# ============================================================
# 量子计算搜索关键词
# ============================================================

QUANTUM_KEYWORDS = [
    # QEC
    "quantum error correction",
    "surface code",
    "topological code",
    "LDPC quantum",
    "quantum decoder",
    "fault-tolerant quantum",
    "stabilizer code",

    # 编译/调度
    "quantum circuit compilation",
    "quantum circuit optimization",
    "qubit mapping",
    "qubit routing",
    "quantum circuit scheduling",
    "quantum transpilation",
    "quantum gate synthesis",

    # AI for Quantum
    "machine learning quantum",
    "neural network quantum",
    "reinforcement learning quantum",
    "diffusion model quantum",
    "GNN quantum",
    "deep learning quantum error",

    # 变分/优化
    "variational quantum",
    "QAOA",
    "VQE",
    "quantum approximate optimization",
    "quantum optimization",
    "quantum annealing",

    # 通用
    "quantum computing",
    "quantum algorithm",
    "quantum simulation",
    "quantum hardware",
    "superconducting qubit",
    "quantum processor",
    "quantum supremacy",
    "quantum advantage",
]

# 用于不同 API 的精简关键词组（避免 API 调用次数过多）
KEYWORD_GROUPS = {
    "qec": [
        "quantum error correction",
        "surface code",
        "fault-tolerant quantum computing",
    ],
    "compiler": [
        "quantum circuit compilation",
        "qubit mapping routing",
        "quantum gate synthesis",
    ],
    "ai_quantum": [
        "machine learning quantum computing",
        "neural network quantum error correction",
        "deep learning quantum",
    ],
    "variational": [
        "variational quantum eigensolver",
        "quantum approximate optimization",
    ],
    "general": [
        "quantum computing",
        "quantum processor",
        "quantum algorithm",
    ],
}

# ============================================================
# API 配置
# ============================================================

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_FIELDS = "title,authors,year,abstract,citationCount,externalIds,publicationDate,venue,tldr"
SEMANTIC_SCHOLAR_API_KEY = ""  # Get your free key at https://www.semanticscholar.org/product/api
SEMANTIC_SCHOLAR_RATE_LIMIT = 1.05  # 秒，有API key后限制为1 req/s

CROSSREF_API = "https://api.crossref.org/works"
CROSSREF_MAILTO = "lijt@baqis.ac.cn"  # 进入 polite pool，速度更快

ARXIV_API = "http://export.arxiv.org/api/query"

# ============================================================
# 路径配置
# ============================================================

import os

KB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(KB_ROOT, "data")
PAPERS_DIR = os.path.join(DATA_DIR, "papers")
VENUES_FILE = os.path.join(DATA_DIR, "venues.json")
LAST_UPDATE_FILE = os.path.join(DATA_DIR, "last_update.json")
