---
name: daily-reports
description: Produce a recurring Chinese research digest for edge-cloud collaborative omni models (video-leaning, speech included), agent memory (conversation / working / long-term), self-evolving agents, and a real-time full-duplex interaction backbone. Use when the user asks to recommend recent papers (arXiv cs.CV/cs.MM/cs.CL/cs.MA/eess.AS, OpenReview, ACL, CVPR, Interspeech), industry news, product/API releases, or GitHub projects for this direction, or to tune the research profile. Reads config/research-profile.md as the source of truth.
---

# DailyReports

## Overview

Use this skill to prepare a concise, daily Chinese digest of frontier papers and industry updates aligned with the user's research profile. The canonical profile is `config/research-profile.md`; read it before collecting or ranking items.

This repository offers two ways to build a digest:

- **Agent-driven (this skill):** you gather, rank, dedup, and write the digest yourself, following the profile. Best for an interactive, interpreted push.
- **Automated (Python package):** `python -m daily_research_report` fetches arXiv/RSS and scores by `config/default_config.json`. Use it for an unattended run or to produce a starting candidate list.

## Required Files

- Research profile: `config/research-profile.md`
- Source and query map: `references/source-map.md`
- History helper: `scripts/paper_history.py`
- Paper history (dedup counts): `~/DailyReports/paper-history.json` (override with `DAILY_REPORT_HISTORY`)
- Daily report output root: `~/DailyReports/` (override with `DAILY_REPORT_OUTPUT_DIR`)
- Optional deep-read handoff: an AutoPaperReader-style paper-reading skill, output to your paper vault (default `~/AutoPaperReader/`)

If the profile changes, use the current file content as the source of truth. Do not rely on older chat history when the profile file has more specific or newer constraints.

## Daily Digest Workflow

1. Read `config/research-profile.md`.
2. Gather current papers and industry updates. Use `references/source-map.md` when query seeds or source expansion are needed. Prefer primary or near-primary sources:
   - Papers: arXiv cs.CL/cs.AI/cs.LG/cs.CV/cs.MM/cs.MA/cs.HC/eess.AS/cs.SD, OpenReview, ACL Anthology, ICLR/NeurIPS/ICML/CVPR/ICCV/ECCV/EMNLP/Interspeech proceedings, Papers with Code, Hugging Face Papers.
   - Industry: official research/product blogs, model/API release notes, GitHub repositories, technical reports from OpenAI, Google DeepMind, Anthropic, Meta, Microsoft, Apple, NVIDIA, Alibaba Qwen, DeepSeek, Hugging Face.
3. Rank items by fit to the profile (these axes are co-equal high priority):
   - High priority: edge-cloud / small-large model collaboration and routing/handoff; omni & multimodal foundation models, especially **video** (video-language, streaming/long video, video generation, world models) with speech as the audio modality; real-time full-duplex / turn-taking / barge-in / always-listening interaction; agent memory (long-conversation/long-context, working memory, long-term/episodic/retrieval memory); self-evolving / self-improving agents (self-play, self-refine, continual learning, skill acquisition).
   - Medium priority: efficient inference, distillation, quantization, speculative decoding, KV-cache/memory compression, on-device RAG, tool-use reliability, multi-agent orchestration, evaluation of interactive/multimodal agents, on-device inference frameworks and low-power hardware.
   - Low priority: generic LLM leaderboard updates, broad benchmarks, pure scaling papers, or product news without implications for edge-cloud omni, memory, self-evolution, or real-time interaction.
4. Enforce the repeat limit before finalizing paper recommendations:
   - Each paper may be recommended at most 2 times total.
   - Identify papers by arXiv ID, DOI, canonical URL, then normalized title.
   - Use `scripts/paper_history.py check --input <candidate-json>` to filter out over-limit papers when working from a candidate file.
   - After sending the digest, record delivered papers with `scripts/paper_history.py record --input <delivered-json>`.
   - Keep recommendation counts in the history file; do not show `推荐次数` in the visible report.
5. If the user says they are interested in a paper, hand it off to an AutoPaperReader-style paper-reading skill and write the report under your paper vault (default `~/AutoPaperReader/`) unless the user gives a different path in that same request.
6. When the user asks to generate a daily report, save Markdown to `~/DailyReports/YYYY-MM-DD-daily-report.md`. Save the delivered paper list as `~/DailyReports/YYYY-MM-DD-papers.json` when using the history helper.

## Candidate JSON Format

Use a list of objects. The helper accepts these fields:

```json
[
  {
    "title": "Paper title",
    "url": "https://arxiv.org/abs/0000.00000",
    "arxiv_id": "0000.00000",
    "doi": "",
    "source": "arXiv",
    "date": "2026-06-16"
  }
]
```

## Output Format

Write the digest in Chinese:

1. `今日判断`: 2-4 bullets on what matters today.
2. `论文推荐`: 3-5 papers when available. Do not show recommendation counts in the report body. For each paper use the paper-entry format below.
3. `行业资讯`: 3-5 items. Explain why each matters for edge-cloud omni models, real-time agents, memory, self-evolution, APIs, deployment, or interaction design.
4. `研究启发`: 2-4 actionable design implications for edge-cloud omni collaboration, agent memory, self-evolution, or real-time interaction.
5. `可深读候选`: list the best 1-2 papers and say the user can ask for a deep AutoPaperReader-style reading.

Avoid padding. If few high-quality items exist, recommend fewer items and say why.

## Paper Entry Format

For every recommended paper, use this structure:

```markdown
### N. [Paper Title](paper-url)

- 来源/日期：source，YYYY-MM-DD
- 相关性等级：★★★★★
- 相关性说明：one sentence explaining why this paper fits the user's current research goal.
- 原文做法：
  - 方法框架：describe the architecture, modules, or pipeline proposed by the paper.
  - 训练/优化：describe training data, objectives, alignment method, reward design, fine-tuning, or optimization when available.
  - 推理/运行机制：describe the runtime control flow, routing, streaming, memory, tool/action interface, or deployment mechanism when available.
  - 实验与指标：describe the tasks, baselines, metrics, and main reported findings; distinguish author claims from your own interpretation.
- 对目标系统的启发：explain how the paper can inform edge-cloud omni collaboration, the memory design, the self-evolution loop, the interaction/handoff policy, or evaluation.
```

Relevance levels:

- `★★★★★`: Directly addresses a core mechanism, such as edge-cloud omni collaboration, video understanding/generation for interaction, agent long-term/working memory, self-evolving agents, or full-duplex interaction/handoff.
- `★★★★☆`: Strongly relevant supporting mechanism, such as on-device multimodal inference, streaming perception, memory compression/retrieval, continual learning, or evaluation for real-time/multimodal agents.
- `★★★☆☆`: Adjacent but useful, such as efficient inference, general agent orchestration, multimodal streaming, or deployment infrastructure.

Method-writing rules:

- Prefer "what the authors actually do" over high-level summaries.
- Include concrete mechanisms, named modules, losses/rewards, datasets, control signals, evaluation metrics, or deployment constraints when available from the abstract, paper page, or PDF.
- If the source does not expose enough detail, say `原文公开信息有限` and avoid inventing method details.
- Keep `原文做法` more detailed than `对目标系统的启发`.

## AutoPaperReader Handoff

When the user expresses interest in a recommended paper:

- Use an AutoPaperReader-style paper-reading skill (see github.com/ParadoxZW/AutoPaperReader).
- Default output root: `~/AutoPaperReader/`.
- Use the paper title, arXiv URL, DOI, or PDF URL from the digest.
- Do not paste the full report into chat; summarize the generated paths and any limitations.

## Maintenance

- Update `config/research-profile.md` when the research direction changes; keep `config/default_config.json` topics and `references/source-map.md` seeds in sync for the automated path.
- Keep the paper history file intact unless the user explicitly asks to reset it.
- If a paper is excluded only because it reached 2 recommendations, mention it only when useful as an omission note; do not recommend it again.
