---
name: paper-kb
description: 查询量子计算论文知识库 - 期刊/会议信息、论文检索、投稿建议、趋势分析。触发词：查知识库、paper kb、search papers、论文、投稿、哪个期刊、related work、趋势、venue、期刊、会议
---

# 量子计算论文知识库 (Paper KB)

知识库位于 `F:/数据集/论文/paper_kb/`。

## 绝对禁令

1. **在读取 venues.json 之前，禁止对任何期刊/会议做出评价或推荐。** 不管你觉得自己多了解某个期刊，都必须先读数据。
2. **禁止高估成果水平。** 宁可低估也不要高估。用户被你高估后去投稿被拒，浪费的是他的时间。
3. **禁止编造论文。** 提到的每一篇论文都必须来自知识库数据，附带真实 DOI/arXiv URL。
4. **禁止在没有充分证据时给出 "可以冲XXX" 的建议。** 如果不确定，说不确定。
5. **禁止反复改口。** 给出判断后，除非用户提供了新的事实信息（不是追问），不要改变你的结论。用户追问"真的稳吗"不是新信息，不要因此把"稳"改成"不稳"。如果你第一次就不确定，第一次就说清楚不确定的程度。
6. **费用不用考虑。** 用户所有论文费用都报销，不要在推荐中提及 APC/OA 费用。
7. **概率估计必须基于先例密度，不能基于"有没有先例"。** 具体规则：
   - 搜到同方向论文数 = 0 → 概率不超过 15%
   - 搜到 1 篇但是多年前的唯一一篇 → 概率不超过 20%（说明该venue对此方向门槛极高，只有开山之作才进得去）
   - 搜到 2-5 篇近 3 年的 → 概率可以到 30-50%（说明venue在积极接收此方向）
   - 搜到 5+ 篇 → 概率可以到 50-70%（说明是该venue的常规方向）
   - **"有1篇先例"≠"该venue欢迎这个方向"。要分析为什么只有1篇——是开山之作独一份，还是该方向确实被接收？**
8. **常见国内期刊必须认识。** CPB = Chinese Physics B（物理天文4区, IF 1.5），CPL = Chinese Physics Letters（物理天文3区, IF 1.0），CPC = Chinese Physics C（核物理），CTP = Communications in Theoretical Physics。不要问"CPB是哪个"。

## 投稿建议的强制流程

当用户问"这个工作投哪里"时，你必须严格按以下步骤执行，不许跳步：

### Step 1: 了解用户的工作
- 如果用户有项目文件夹，先读里面的 honest assessment / 实验结果 / 已知局限
- **不要只看论文的叙事**，要看实际数据和内部评估
- 明确列出：成果的强项、弱项、规模限制

### Step 2: 读取 venue 数据
```bash
cd "F:/数据集/论文/paper_kb" && python -c "
import json
with open('data/venues.json','r',encoding='utf-8') as f: venues=json.load(f)
for vid in ['PRXQ','npjQI','QST','Quantum','TQC','TQE','PRA','NC','PRL']:
    v=venues.get(vid,{})
    print(f\"{vid}: IF={v.get('impact_factor')} | tier={v.get('tier')} | scope={v.get('scope','')[:100]}...\")
    print(f\"  not_suitable_for: {v.get('not_suitable_for','')[:100]}\")
    print(f\"  distinguishing_notes: {v.get('distinguishing_notes','')[:100]}\")
    print()
"
```

### Step 3: 自动扫描所有 venue 的接收情况
```bash
cd "F:/数据集/论文/paper_kb" && python scripts/search.py recommend "关键词1" "关键词2" "关键词3" --top 10
```
这会自动扫描所有 venue，输出每个 venue 对该方向的接收密度。**必须用这个命令**，不要手动逐个搜。
重点看：
- **3yr 列**：近3年接收了几篇同类论文？0篇 = 基本不接收
- **Latest 列**：最近一篇是什么时候？越近越说明在活跃接收
- **Top Cited**：该 venue 的代表性工作，用来判断你的工作和它对标的差距

### Step 4: 给出一个明确推荐 + 备选
基于以上数据，**严格按以下格式**输出推荐（最多 3 个 venue）：

```
1. [首选venue] (tier, ~XX%) — 一句话理由，引用具体数据
2. [备选venue] (tier, ~XX%) — 一句话理由
3. [保底venue] (tier, ~XX%) — 一句话理由（可选）
```

示例：
```
1. QST (T3, ~40%) — scope match "量子技术应用"，但无扩散模型先例
2. Quantum (T3, ~35%) — Riu et al. ML+电路先例，但偏理论
3. TQE (T4, ~70%) — 工程scope契合，但在BAQIS认可度低于物理刊
```

**强制要求**：
- 每个推荐必须包含：tier、成功概率%、scope 匹配度、同类论文先例
- **明确说明风险**（如"reviewer 可能认为规模不够"）
- **不提费用**（BAQIS 全额报销，费用不是决策因素）
- **给出判断后就坚持住**。不要因为用户追问就改口。如果把握只有 40%，第一次就说 40%，不要先说"稳"后说"不稳"。
- 如果用户追问"真的吗？""确定吗？"——重复你的数据依据，不要改结论
- **只有用户提供了新的事实信息**（如"我们加了新实验""规模扩展到20 qubit了"），才允许重新评估

## Venue 理解要点

**tier 基于中科院分区 + SJR + IF + h-index 综合排名，数据来源：中科院分区表2024、SCImago、JCR。**

### 期刊 Tier（按中科院分区+SJR）

| Tier | 中科院分区 | 期刊 | SJR | IF | 量子科技分区 |
|------|-----------|------|-----|-----|------------|
| T1-flagship | 综合1区Top | Nature, Science | - | 48-46 | - |
| T2-top-physics | 物理天文1区 | NatPhys, PRL(2.86), NC, PRX, PRXQ(5.34) | 2.9-5.3 | 8.6-18.4 | 量子科技1区(PRXQ) |
| T3-excellent | 物理天文1-2区 | npjQI(2.73), Quantum(2.53), QST(1.91), CommPhys(1.78) | 1.8-2.7 | 5.2-7.9 | 量子科技1-2区 |
| T4-standard | 物理天文2区/工程2-3区 | PRA(1.03), PRApplied, PRResearch, TQE(1.05), TQC(1.11), AQT, EPJQT | 1.0-1.2 | 2.9-6.8 | 量子科技2-3区 |
| T5-entry | 物理天文3区 | QIP_journal(0.48), NJP, CPL | 0.5 | 2.2-2.8 | 量子科技3-4区 |
| T6-保底 | 物理天文4区 | CPB(0.33) | 0.3 | 1.5 | - |

### 会议 Tier

| Tier | 等级 | 会议 |
|------|------|------|
| T2-CCF-A | CCF-A / CORE A* | ASPLOS, MICRO, ISCA, HPCA, DAC, SC, PPoPP |
| T2-physics | 量子信息旗舰会议 | QIP |
| T3-CCF-B | CCF-B / CORE A | ICCAD, CGO |

### 关键排名说明

- **PRXQ SJR 5.34，量子专刊最高**，中科院量子科技1区，远超第二名 npjQI(2.73)
- **npjQI 中科院量子科技1区**，比 QST/Quantum(2区) 高一档，但三者都是 T3
- **TQC IF 6.8 但 SJR 仅 1.11（T4）**——2020年新刊，中科院未收录，h-index 17，IF 虚高是论文量少导致
- **PRA IF 2.9 看起来低，但 h-index 330**——中科院物理天文2区，量子信息理论的传统主力期刊
- **TQE 中科院工程技术2-3区**，在物理院(BAQIS)认可度低于同级物理刊

### Scope 区分

- 偏物理理论 → PRA, PRXQ, Quantum, PRL
- 偏实验/硬件 → PRApplied, npjQI, QST, NC
- 偏CS/工程/编译 → TQC, TQE, DAC, ASPLOS
- ML+量子 → 理论性强走 PRXQ/Quantum，应用性强走 QST/npjQI/TQE

### 用户机构偏好（BAQIS）

用户在北京量子信息科学研究院(BAQIS)工作：
- **物理期刊认可度 > CS期刊**，即使 IF 相近。PRA(IF 2.9, 物理2区) 在院里认可度高于 TQC(IF 6.8, 未收录)
- **中科院分区是核心参考指标**，比 IF 更重要
- 同等条件下优先推荐物理系期刊

## 数据文件

- `data/venues.json` — 所有期刊/会议的元数据（IF、scope、投稿要求等）
- `data/papers/{venue_id}.json` — 每个 venue 的量子计算论文列表
- `data/papers/arxiv.json` — arXiv 论文
- `data/last_update.json` — 最后更新时间

## 检索命令

```bash
# 搜索论文
cd "F:/数据集/论文/paper_kb" && python scripts/search.py search "关键词" --venue VENUE_ID --sort citations --limit 10 --verbose

# ⭐ 投稿推荐（核心命令）— 自动扫描所有 venue，按接收密度排序
cd "F:/数据集/论文/paper_kb" && python scripts/search.py recommend "关键词1" "关键词2" "关键词3" --top 10
# 输出每个 venue 的：匹配论文数、近3年数、近1年数、最新一篇、最高引一篇
# Step 3 必须用这个命令，不要手动逐个 venue 搜

# 统计各 venue 论文数
cd "F:/数据集/论文/paper_kb" && python scripts/search.py stats --by venue

# 按 topic 统计
cd "F:/数据集/论文/paper_kb" && python scripts/search.py stats --by topic

# 未总结论文
cd "F:/数据集/论文/paper_kb" && python scripts/search.py unsummarized --limit 20
```

### recommend 输出解读

- **Match**: 该 venue 中匹配关键词的论文总数
- **3yr**: 近3年(2023+)匹配数 — **核心指标，反映该 venue 是否在活跃接收这个方向**
- **1yr**: 近1年匹配数 — 最新趋势
- **Latest**: 最近一篇匹配论文的日期和标题
- **Top Cited**: 最高引用的匹配论文

**判读规则**：
- 3yr=0 → 该 venue 基本不接收这个方向，概率≤15%
- 3yr=1-2 → 零星接收，概率≤25%
- 3yr=3-5 → 有在接收但不是主力方向，概率30-50%
- 3yr=5+ → 活跃接收，概率50-70%
