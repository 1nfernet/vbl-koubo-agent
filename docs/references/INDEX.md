# 核心开源参考规范与权威索引 (Core References)

本文档整理了本项目在“Agent Skill 规范设计、口播/视频工程、质量门禁与跨平台分发”方面参考的业界权威开源项目与标准。
用于在后续迭代自身 Skill、打包分发以及制作新 Skill 时作为规范依据。

---

## 一、 Agent Skill 标准与官方规范 (Standards & Official Specs)

| 项目 / 链接 | 核心设计价值 | 本项目借鉴与落地要点 |
| :--- | :--- | :--- |
| **[Agent Skills Specification](https://agentskills.io/specification)** | 跨平台统一的 Agent Skill 开放行业标准 | - 强制要求顶层标准 YAML Frontmatter (`name`, `description`)<br>- 标准目录结构与纯 Markdown 指令设计，兼容 Claude Code、Cursor、Codex 等主流宿主 |
| **[Anthropic Skills / skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)** | Anthropic 官方生产级 Skill 仓库与技能创造者 | - 技能开发 SOP：明确意图 -> 编写契约 -> 黄金样例测试 -> 闭环优化<br>- 单一职责原则：一个 Skill 专注解决一类领域问题 |
| **[Matt Pocock / writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents)** | 专门给 Agent 编写指导文档的工程方法学 | - **Positive Over Negation**：多用正向明确指示（如“单句控制在16字”），少用否定式套话<br>- **Leading Words**：使用高信息密度的专业词汇（如“气口”、“打结”、“文化锚点”）<br>- **Hunt No-ops**：删除模型默认就会做的废话，只保留不可妥协的硬约束 |
| **[obra / superpowers](https://github.com/obra/superpowers)** | 工业级可组合 Agent Skill 体系框架 | - **Systematic over ad-hoc**：以体系化规则取代临时发挥<br>- **Evidence over claims**：确凿证据先行，必须运行验证命令拿到物理输出 |

---

## 二、 前端与审美规范工程 (Design Systems & Anti-AI Smell)

| 项目 / 链接 | 核心设计价值 | 本项目借鉴与落地要点 |
| :--- | :--- | :--- |
| **[pbakaus / impeccable](https://github.com/pbakaus/impeccable)** | 让 AI 摆脱千篇一律模板感与“AI味”的严密设计语言 | - **模式路由 (Mode Routing)**：区分 `Persuade`（短视频转化）与 `Read/Operate`（中长视频深拆），禁止拿短视频逻辑粗暴裁剪深度内容<br>- **消除 AI 模板味**：剔除大模型生成的平均主义、无细节、无个性表达 |

---

## 三、 口播、视频与认知转写开源项目 (Video & Script Craft)

| 项目 / 链接 | 核心设计价值 | 本项目借鉴与落地要点 |
| :--- | :--- | :--- |
| **[gushuaialan1 / broadcast-craft](https://github.com/gushuaialan1/broadcast-craft)** | 数字生命卡兹克长文人格化写作迁移至短视频口播的系统 | - **HKR 黄金钩子模型**：从 H(悬念好奇)、K(硬核数据)、R(痛点共鸣) 三个维度竞争开头<br>- **四层自检体系**：L1 硬性禁词拦截、L2 结构审核、L3 活人感终审 |
| **[nanyin-gif / koubo-copywriter-lite](https://github.com/nanyin-gif/koubo-copywriter-lite)** | 抖音/快手真人口播五件套与去 AI 味清单 | - 物理语速折算表（4.0~4.2 字/秒）与单句呼吸气口<br>- 严格的静态禁词与书面连词清扫清单 |
| **[KIRVO-REPORTING / video-to-notes](https://github.com/KIRVO-REPORTING/video-to-notes)** | 面向 Agent 的视频资料整理与本地化转写 CLI | - **字幕优先（Caption-first）**：不盲目下载大视频跑重型 Whisper，优先轻量提取字幕与纯文本，零负担可移植 |

---

## 四、 技能单包打包与分发参考 (Packaging & Distribution)

| 项目 / 链接 | 核心设计价值 | 本项目借鉴与落地要点 |
| :--- | :--- | :--- |
| **[Skills Marketplace (skillsmp.com)](https://skillsmp.com/zh/skills)** | 全球 Agent Skill 索引与分发市场 | - 规范单一 Skill 打包格式，支持作为独立子目录发布，用户一键 `clone` 或复制即可在任意支持 Agent 的工具中运行 |
| **[bketelsen / agentic-template](https://github.com/bketelsen/agentic-template)** | Agent 自维护项目的最小工程范式 | - `AGENTS.md` 作为统一权威法则，通过单法则约束所有接入 Agent<br>- 结构不写空话，直接切断 Agent 的有害自由度 |
