# Source Map for DailyReports

## Paper Sources

- arXiv categories: cs.CL, cs.AI, cs.LG, cs.CV, cs.MM, cs.MA, cs.HC, eess.AS, cs.SD.
  - Video-leaning omni is the top axis, so weight `cs.CV` / `cs.MM` highly; `cs.MA` / `cs.CL` / `cs.AI` cover agent memory and self-evolving; `eess.AS` / `cs.SD` cover speech; `cs.HC` covers real-time interaction.
- Conference and review sites: OpenReview, ACL Anthology, NeurIPS, ICML, ICLR, EMNLP, CVPR, ICCV, ECCV, Interspeech, CHI, UIST.
- Discovery aggregators: Papers with Code, Hugging Face Papers, Semantic Scholar.

## Industry Sources

- Model and API providers: OpenAI, Google DeepMind, Anthropic, Meta AI, Microsoft Research, Apple Machine Learning Research, NVIDIA, Hugging Face, Alibaba Qwen, DeepSeek, Zhipu/GLM, Moonshot/Kimi, ByteDance Seed.
- Edge and deployment stacks: llama.cpp, vLLM, MLC LLM, ExecuTorch, Core ML, TensorFlow Lite, ONNX Runtime, WebNN, Qualcomm AI Hub, MediaTek NeuroPilot.
- Agent/product signals: official release notes, technical blogs, public GitHub repos, SDK docs, benchmark posts with reproducible details.

## Query Seeds

Use combinations of these terms, then filter by the current research profile. The five axes below are co-equal high priority; video carries the highest weight within omni.

Edge-cloud & large-small collaboration:
- "small language model large language model collaboration"
- "edge-cloud LLM agent collaboration"
- "on-device multimodal model real-time"
- "model routing handoff small large model"
- "collaborative inference edge cloud"

Omni & video (top weight):
- "omni-modal foundation model any-to-any"
- "unified multimodal understanding and generation"
- "video large language model understanding"
- "streaming video LLM real-time"
- "long video understanding"
- "video generation diffusion world model"
- "audio-visual multimodal interaction"

Real-time full-duplex interaction:
- "full-duplex spoken dialogue model"
- "turn-taking barge-in interruption detection"
- "real-time voice multimodal agent streaming"
- "always-listening interactive agent"

Memory (conversation / working / long-term):
- "long conversation memory LLM agent"
- "long-context memory management"
- "agent working memory"
- "LLM agent long-term memory episodic"
- "retrieval augmented memory bank agent"
- "memory compression consolidation dialogue"

Self-evolving agents:
- "self-evolving LLM agent"
- "self-improving agent from experience"
- "self-play language model"
- "self-refine self-correction reasoning"
- "continual lifelong learning agent"
- "autonomous skill acquisition agent"

Speech (omni audio modality):
- "speech language model full-duplex"
- "streaming ASR TTS real-time"

## Ranking Heuristics

Prioritize items that change system-design decisions:

- Edge-cloud: does it improve division of labor, routing, handoff, or collaborative inference between a small on-device model and a large cloud model?
- Omni / video: does it advance omni (especially **video**) understanding or generation, streaming / long-video, or its edge-cloud split under latency / energy constraints?
- Interaction: does it help a real-time model decide when to speak, watch, interrupt, wait, or hand off (full-duplex, turn-taking, barge-in)?
- Memory: does it propose or evaluate conversation / working / long-term memory (write, retrieve, compress, forget, or share across edge-cloud)?
- Self-evolution: does it let an agent self-improve / self-evolve from experience (self-play, self-refine, continual learning, skill acquisition)?
- Deployment: does it expose implementation constraints for mobile, edge, privacy, energy, or API orchestration?
