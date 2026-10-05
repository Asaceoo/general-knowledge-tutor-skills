# General Knowledge Tutor · 通识可视化学习导师

> 把「学一个东西」从线性阅读升级成：**先拆到底层 → 再建体系 → 配可视化 → 讲清本质 → 自检闭环**。
> 平台无关的 AI 智能体技能：Claude Code / OpenClaw / WorkBuddy / Cursor / WPS AI / Codex 等均可使用。

**面向读者：想直接用它学习的人 → 看本手册。想了解实现原理、二次开发 → 看 [TECHNICAL.md](TECHNICAL.md)（技术手册）。**

---

## 一、这是什么

`general-knowledge-tutor` 是一个**通识类学习技能**（Agent Skill）：安装后，你对 AI 说「帮我搞懂 X」，它不再给一篇普通讲解，而是走完一套固定五阶段工作流，交付一份**结构化学习包**：

| 阶段 | 产出 | 解决的问题 |
|---|---|---|
| Phase 1 第一性原理拆解 | 隐含假设清单 + 原子事实 + 推理链 | 死记结论，记不住 |
| Phase 2 体系化知识地图 | 概念依赖 DAG + 跨学科坐标 | 学完孤立、不成体系 |
| Phase 3 本质理解 | 一句话本质 + 生活类比（带失效边界） | 看懂了名词，没建立直觉 |
| Phase 4 可视化生产 | Manim 动画 / GIF 图表 / 交互 HTML | 抽象概念看不见摸不着 |
| Phase 5 结构化交付 | 学习卡（含自检题 + 学习路径） | 学完不知自己会不会 |

核心承诺：**所有可视化脚本真实运行渲染，不交付「看起来对」的伪产物；所有事实优先核验，不确定处标注「待核验」。**

## 二、安装

### Claude Code / OpenClaw（Agent Skills 标准格式）

```bash
# 克隆到用户级技能目录
git clone https://github.com/Asaceoo/general-knowledge-tutor-skills.git
cp -r general-knowledge-tutor-skills ~/.claude/skills/general-knowledge-tutor   # Claude Code
# OpenClaw 用户复制到其技能目录（如 ~/.openclaw/skills/）即可
```

安装后自动按 `SKILL.md` 的 description 触发，无需任何配置。

### WorkBuddy

将仓库内容复制到 `~/.workbuddy/skills/general-knowledge-tutor/`（保留 `SKILL.md` 与 `references/` 结构），重启会话即可。也可在对话中说「安装技能」从市场导入。

### Cursor / WPS AI 等无 Skill 机制的智能体

这类工具没有技能目录，用「规则注入」方式等效使用：

1. 复制本仓库 `SKILL.md` 全文。
2. Cursor：存为 `.cursor/rules/knowledge-tutor.mdc`（`description` 放进 frontmatter，`alwaysApply: false`）。
3. WPS AI / 其他：粘贴到「自定义指令 / 系统提示词 / 项目规则」中。
4. 使用时说「按 knowledge-tutor 技能讲讲 X」，即可触发同一套工作流。

### 可选依赖（决定动画质量上限）

| 依赖 | 作用 | 缺失时的行为 |
|---|---|---|
| Python 3.10+ + numpy + matplotlib | 图表 / GIF 动画（主力兜底） | 无 Python 时产出可复制的脚本，请用户运行 |
| manim（`pip install manim`） | 电影级动画 mp4 | 自动降级为 matplotlib GIF + SVG，并在交付中注明 |
| 浏览器 | 查看交互式 HTML 组件 | — |

## 三、快速上手（30 秒）

安装后直接说，不需要记任何指令格式：

- 「用第一性原理讲讲熵到底是什么」
- 「梯度下降我老是没直觉，做个动画帮我理解」
- 「系统学一下复利，给我画出来」
- 「帮我搞懂相对论，最好有 Manim 动画」
- 「我想入门宏观经济学，给我建个体系」

第一次使用会先确认三件事：**主题、目标深度（速览/精通/输出）、你的基础（零基础/有背景/专业）**。直接跳过让它猜也行——它按「体系化精通 + 有相关背景」默认处理并在开头标注。

### 交付物长什么样

一份「通识可视化学习卡」（Markdown 或自包含 HTML），固定骨架：

```
一句话本质 → 第一性原理拆解 → 体系坐标（依赖图）
→ 通俗理解（类比 + 失效边界）→ 边界与反例
→ 可视化（动画/图表/交互组件）→ 学习路径 → 自检问题 → 参考来源
```

所有图片/动画以文件形式落盘（PNG/GIF/MP4/HTML），交互组件双击即可在浏览器使用。

## 四、使用技巧

1. **报你的基础**：「我是文科零基础」会让类比更生活化、术语密度更低。
2. **点名可视化形式**：「做成 3D 动画」「要可以拖动滑块调参数的」会被采纳（但 2D 能讲清时它会拒绝上 3D，这是特性不是 bug）。
3. **要速览版**：「30 秒版」只给本质 + 类比 + 一张图 + 自检。
4. **追问边界**：「这个概念的适用边界和反例」会触发专门的严谨性收口。
5. **面试/教学输出**：「我要讲给别人听」会按可讲解标准补全学习路径与自检题。

## 五、常见问题（FAQ）

**Q1：没装 Manim 会怎样？**
自动走降级链：Manim mp4 → matplotlib 多帧 GIF → SVG 静态图 → 文字分步说明。每级降级都会在交付物中如实标注，不会假装是动画。

**Q2：中文乱码怎么办？**
技能内置防线：matplotlib 需在绘图前设置 `font.family`（如 Microsoft YaHei）与 `axes.unicode_minus: False`，模板中已写好。

**Q3：它会不会编造数据？**
质量约束禁止编造。事实优先核验（有联网工具则搜索交叉验证），无法核验的显式标「待核验」并给出验证路径。

**Q4：交互组件打不开？**
独立 HTML 文件双击用浏览器打开即可；其中 Three.js 3D 组件首次加载需联网（CDN），失败时页面会显示降级提示并指向静态 GIF。

**Q5：和直接问 AI「讲讲 X」的区别？**
直接问得到一篇作文（质量看运气）；本技能强制走五阶段 + 质量门控（🛑 STOP 检查点）+ 反例黑名单，输出确定性更高，且可视化产物可复现（脚本随交付落盘）。

## 六、反馈与贡献

- 问题反馈 / 改进建议：[Issues](https://github.com/Asaceoo/general-knowledge-tutor-skills/issues)
- 质量评分记录与测试用例见 `test-prompts.json`；技术细节见 [TECHNICAL.md](TECHNICAL.md)。

## 许可证

[MIT](LICENSE)
