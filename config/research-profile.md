# 研究方向画像：端云协同 Omni 模型 · Agent 记忆与自进化

> 本文件是每日推送的唯一事实源。研究方向若微调，直接改本文件；`config/default_config.json` 的 topics 与 `skills/daily-reports/references/source-map.md` 的检索关键词随之同步。

## 身份与长期目标

我是一名计算机科学与技术专业的博士生。研究方向围绕**端云协同（edge-cloud collaboration）的 omni 基础模型**展开，模态覆盖语音与视频（**更偏向视频**），并进一步延伸到 **Agent 的记忆机制**（对话记忆 / 工作记忆 / 长期记忆）与 **Agent 的自进化（self-evolving）**。

长期目标：构建一个端云协同的实时交互智能体——端侧常驻一个轻量 omni 交互模型，实时地「听 + 看 + 说」，维持在场与交互控制；云端由高能力推理模型 / Agentic LLM 承担复杂任务；两端在同一套协同协议下共享上下文、用户状态、记忆与中间结果，并且系统能从持续交互中自我改进。

## 目标系统形态

系统由两类模型协同构成：

1. 端侧 omni 交互模型：部署在端侧或低延迟环境，实时处理音频与视频输入，负责监听 / 观看、对话承接、实时反馈、状态说明，以及判断何时打断、追问、确认或把任务转交云端。它是实时交互控制层，不只是大模型的前端包装。
2. 云端推理 / Agentic 模型：负责复杂 query 的规划、推理、工具调用、长上下文与长期记忆处理、最终任务完成。

在两类模型之上，系统还需要两个横向层：

- **记忆层**：跨会话的长对话记忆、任务执行期间的工作记忆、可检索的长期记忆（episodic / semantic），并解决端云之间记忆如何分层存储与同步。
- **自进化层**：Agent 能从交互经验、失败与反馈中持续改进策略、技能与记忆，而不是静态部署。

## 核心研究问题

- 端云协同：端侧小 omni 模型与云端大模型如何分工；上下文、用户状态、任务状态、置信度、中间结果如何在两端传递；路由 / 转交 / 失败恢复的协议与评价指标如何设计。
- Omni 与视频：视频（及音频）的实时理解与生成如何在端云间切分；streaming video、long video、video-language、world model 等如何服务实时交互；端侧算力 / 延迟 / 功耗约束下如何取舍。
- 实时交互：端侧模型如何判断用户意图变化、打断时机、转交时机、澄清时机；full-duplex、turn-taking、barge-in、backchannel 等实时控制如何在 omni（音视频）场景下实现与评估。
- 记忆：如何为交互 Agent 构建对话记忆 / 工作记忆 / 长期记忆；记忆的写入、检索、压缩、遗忘与一致性；长上下文与外部记忆如何配合；端云之间记忆如何共享。
- 自进化：Agent 如何 self-evolving / self-improving——从经验中更新策略与技能、self-play / self-refine / self-correction、continual / lifelong learning、技能获取，以及如何避免灾难性遗忘与能力退化。

## 推送内容优先级

高优先级（以下各轴并列，不分主次）：

- **端云协同 / 大小模型协作**：Small↔Large、edge-cloud collaboration、模型路由、任务转交、agent orchestration、协同推理、端侧 LLM/SLM、低延迟推理。
- **Omni / 多模态基础模型（偏视频）**：omni-modal / any-to-any、unified multimodal、MLLM；**视频理解与生成**（video-language、streaming / long video、video diffusion、world model）为最高权重；图文与跨模态次之。
- **实时全双工交互**：实时语音 / 多模态对话 agent、always-listening、turn-taking、barge-in、interruption detection、流式交互与用户等待体验、状态同步。
- **Agent 记忆**：长对话记忆 / long-context、工作记忆（working memory）、长期记忆（episodic / semantic / retrieval / memory bank）、记忆压缩与一致性、个性化记忆。
- **Agent 自进化**：self-evolving / self-improving agent、self-play、self-refine / self-correction、continual / lifelong learning、经验驱动的技能获取与策略更新。

中优先级：

- 模型压缩、蒸馏、量化、speculative decoding、KV cache 优化、端侧 RAG。
- 交互式 / 多模态 agent 的评估、对话状态建模、多智能体协作、工具调用可靠性。
- 语音专项（ASR / TTS / speech-LM / audio codec）作为 omni 的音频模态支撑。
- 开源端侧推理框架、移动端部署工具链、低功耗芯片与端侧 AI SDK。

低优先级：

- 与端云协同 / omni / 记忆 / 自进化关系不强的通用大模型榜单。
- 只有规模提升、缺少系统机制或方法启发的纯模型发布。
- 无明确技术细节或研究启发的营销类资讯。

## 输出偏好

每日推送应同时覆盖前沿论文和行业资讯。论文推荐要解释它与目标系统（端云协同 omni、实时交互、记忆、自进化）的关系，而不是只摘要论文。论文正文中不要展示推荐次数；推荐次数只用于后台去重。相关性用星级等级描述，例如 `★★★★★`、`★★★★☆`、`★★★☆☆`。论文的「核心想法」应改写为更具体的「原文做法」，优先说明作者实际提出的架构、模块、训练或优化目标、运行机制、实验设置和指标，而不是只给一句概括。行业资讯要说明它对端侧 / 端云 omni 模型、实时 agent、记忆或自进化机制、产品落地的影响。若某篇论文值得深读，应标记为深读候选，可交给 AutoPaperReader 类论文精读技能输出报告到 `~/AutoPaperReader`。
