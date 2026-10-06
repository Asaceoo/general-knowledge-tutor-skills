# TECHNICAL.md · 技术手册

> 面向二次开发者、技能维护者与想深入理解工作流的用户。
> 使用层面的问题请先看 [README.md](README.md)（用户手册）。

---

## 1. 系统架构

```
general-knowledge-tutor/
├── SKILL.md                       # 技能主体：frontmatter + 五阶段工作流 + 质量门控
├── references/
│   ├── manim-patterns.md          # Manim 分镜规范 + 4 个可复用 Scene 模板 + 渲染/降级
│   ├── visualization-cookbook.md  # matplotlib/plotly/SVG/交互 HTML 速查模板
│   ├── 3d-animation.md            # 3D 五层选型（mplot3d/PyVista/vpython/Three.js/Blender bpy/ThreeDScene/plotly）+ 坑清单
│   └── extended-viz.md            # 扩展工具箱（ECharts/D3/p5.js/pyvis/schemdraw/Motion Canvas/GeoGebra/Desmos）+ 表达方式
├── test-prompts.json              # 触发测试用例（should_trigger / should_not_trigger）
├── README.md                      # 用户手册
└── TECHNICAL.md                   # 本文件
```

设计定位：**纯声明式技能**——不包含任何可执行脚本，全部产出由智能体在运行时按模板生成。好处：跨平台零适配成本；代价：依赖宿主智能体具备「写文件 + 执行命令」能力（缺失时的降级策略见 §4）。

### 1.1 触发机制

技能命中由 `SKILL.md` frontmatter 的 `description` 驱动。description 中显式埋入了触发词族：

- 动作词：搞懂 / 理解 / 讲讲 / 原理 / 本质 / 科普 / 教学 / 入门 / 系统学
- 方法词：第一性原理 / 可视化讲解 / 做个动画 / 面试讲解

测试用例（`test-prompts.json`）覆盖三类：典型命中、模糊命中（如「复利是不是利滚利」）、近似误触发（如「写个批量重命名脚本」应不命中）。改动 description 后应重跑判定。

## 2. 五阶段工作流规范

### Phase 0 意图定位
输入：用户 query。输出：`(主题, 深度∈{速览,精通,输出}, 覆盖∈{单点,带前置,完整体系}, 基础∈{零基础,有背景,专业}, 可视化⊆{动画,交互图,3D,配音,记忆卡})`。
确认方式：用提问能力弹结构化选项（单选/多选），禁止开放式追问；用户已给则跳过该项。
组合规则：深度=速览时忽略可视化与覆盖范围（只出通俗版）；覆盖范围默认对齐深度（速览→单点，精通→带前置，输出→完整体系），显式指定则覆盖。
未确认时的默认值：`(精通, 带前置, 有相关背景, 可视化自动)`，且必须在交付物开头标注假设。
**门控 🔴 CHECKPOINT**：五项确认（或超时走默认）才可进入 Phase 1。

### Phase 1 第一性原理拆解
产出三件套：假设清单（3–6 条，区分承重/情景）、原子事实（每条标来源类型）、推理链（每步「A+B→C」）。推理链是 Phase 3 讲解与 Phase 4 分镜的主干，不允许后补。

### Phase 2 体系化知识地图
产出概念 DAG（核心层/支撑层/延伸层）+ 跨学科坐标。表达强制用 Mermaid（优先）或 SVG（兜底），禁止纯文字描述依赖关系。

### Phase 3 本质理解
一句话本质（主谓宾，禁止循环定义）→ 1–2 个类比 → **每个类比必须紧跟失效边界** → 存在动机 → 适用条件与反例。

### Phase 4 可视化生产（核心工程环节）
选型矩阵（按概念类型）：

| 概念类型 | 首选 | 降级链 |
|---|---|---|
| 过程/流程/演化 | Manim 分镜动画 | matplotlib 多帧 GIF → SVG + 分步文字 |
| 几何/证明/空间 | Manim | SVG 静态图 |
| 数据/分布/关系 | matplotlib / plotly | SVG 手绘 |
| 概念/体系/依赖 | Mermaid / SVG | 文本缩进树 |
| 可探索参数 | HTML widget（滑块+canvas） | 静态多状态图 |
| 空间结构/旋转/场 | 3D（五层选型见 §3.3） | 多视角 3D PNG |
| 场/曲面/体渲染 | PyVista | mplot3d 多视角 PNG |
| 物理/轨道/仿真教学 | vpython | p5.js 动画 / 分步静态图 |
| 函数/几何交互探索 | GeoGebra / Desmos iframe | 滑块 HTML widget |
| 网络/关系/流向 | pyvis / graphviz；桑基等用 ECharts | Mermaid 手写 |

**3D 启用门槛**：仅当空间结构本身承载信息（旋转→振荡、螺旋、场、曲面、轨道）时启用；2D 能讲清的不上 3D。

**分镜规范**：先写 storyboard（镜号/画面/旁白/时长/动作），旁白时长按 ~4 字/秒估算；分镜定稿后才写 Scene 代码。

**门控 🛑 STOP**：可视化产物未通过真实运行自检（文件存在、可播放、中文显示正常）不得进入 Phase 5，必须降级并注明。

### Phase 5 交付
**双文档交付**（v1.1.3 起；**v1.1.4 起文件命名强制中文**，禁止拼音/英文文件名；产物与 md 同目录、相对路径引用）：
1. **主卡** `[主题]—通识可视化学习卡.md`：固定骨架（本质/拆解/体系/通俗/边界/可视化/路径/自检/来源）。深度=速览时裁剪为四节。
2. **通俗版** `[主题]—通俗版.md`：一句话说人话 / 解决什么麻烦 / 生活比方×2（各带「哪里不准」）/ 一张图看懂（复用主卡）/ 3 个自问自答。硬规则：共用事实不二次创作、术语翻译（元词汇禁用）、篇幅 ≤ 主卡 40%。
深度=速览仅交付通俗版；精通/输出档交付双文档；输出档另补讲解附加物（分镜表 / 类比库 / 预设追问 Q&A）。**门控 🔴 CHECKPOINT**：质量约束逐条自检 + 通俗版三硬规则核查。

## 3. 可视化工具链

### 3.1 降级决策树

```
探测 manim ──有──► Manim 分镜渲染（-qm，验证 mp4 >10KB 可播放）
    │无
    ├─ 过程/演化类 ──► matplotlib FuncAnimation + PillowWriter → GIF
    ├─ 几何/结构类 ──► 代码生成 SVG
    └─ 数据类 ──► matplotlib PNG / plotly HTML
任何一级失败：降级 + 在交付物标注「本应动画呈现，已降级为 X」
```

### 3.2 已知工程坑（模板中已内置对策）

| 坑 | 对策 |
|---|---|
| matplotlib 中文乱码（Windows） | 绘图前设 `font.family`（Microsoft YaHei/SimHei）+ `axes.unicode_minus: False` |
| mplot3d 深度排序伪影 | 辅助元素 alpha≤0.6 淡化 + 主线加粗（无法根治，只能缓解） |
| GIF 相机环绕首尾跳变 | 方位角匀速转满 360°（首尾帧相机位置重合 → 无缝循环） |
| GIF 体积失控 | dpi 85–95、60 帧、fps 16–20，目标 ≤2 MB（base64 内嵌后 ×1.33） |
| Three.js CDN 加载失败 | `typeof THREE === 'undefined'` 检测 → 显示降级文案并指向静态 GIF |
| Manim 系统依赖（cairo/pango/ffmpeg） | 安装失败即走降级链，不阻塞交付 |
| 自测 HTML 题目/选项含 `<` `&` 破版式或 `<img onerror>` 注入 | 模板内置 `esc()` 转义所有动态插值（v1.3.0 实测：注入不执行、判分不回归）；生成题目时避免数据含字面 `</script>`（会截断 HTML 解析层，转义不可防，必要时写 `<\/script>`） |

### 3.3 3D 五层选型

| 层 | 方案 | 依赖 | 产物 | 适用 |
|---|---|---|---|---|
| A | matplotlib mplot3d → GIF | numpy+matplotlib | .gif | 零依赖兜底（任何环境可用） |
| B | PyVista | pip | .gif/.png/交互 .html | 质量主力：场/曲面/体渲染，深度排序正确 |
| C | vpython | pip | 自包含 .html | 教学仿真：轨道/波/刚体，浏览器可交互 |
| D | Three.js r128（CDN） | 浏览器 | 内联 script | 卡内可拖拽探索（查看时需联网） |
| E | Blender bpy 无头渲染 | 本机 Blender | PNG 序列→.gif/.mp4 | 电影级质感/运镜（无需 Manim） |
| F | Manim `ThreeDScene` | manim | .mp4 | 已装 Manim 时的 3D |
| G | plotly 3D | plotly | 自包含 .html | 数据曲面/散点探索 |

### 3.4 扩展工具箱（references/extended-viz.md）

按「填补空白」准入，模板含最小可运行示例 + 降级链：

- **ECharts**（CDN）：桑基/和弦/热力日历/关系图，中文最友好 → 降级 matplotlib
- **D3.js**（CDN）：完全自定义交互（力导向图等）→ 降级 ECharts
- **p5.js**（CDN）：粒子流场等过程动画 → 降级 streamplot 静态图
- **pyvis / graphviz**（pip）：Phase 2 DAG 自动布局 → 降级 Mermaid
- **schemdraw**（pip）：电路/原理示意图 → 降级 SVG 手绘
- **GeoGebra / Desmos**（iframe）：函数/几何调参探索零代码 → 降级自写 widget
- **Motion Canvas**（Node）：时间轴级程序化动画 → 降级 Manim

表达方式层（跨工具）：滚动叙事（scrollytelling，适配 Phase 1 推理链）、小倍数图（参数族）、粒子流场、物理仿真驱动、reveal.js 交互幻灯、rough.js 手绘风。

### 3.5 交互组件交付策略

1. 宿主有内联 HTML 能力（如 WorkBuddy widget）→ 原始 HTML 片段交付；
2. 否则 → 独立 `.html` 文件落盘 + 回复中给路径。
两种路径最终产物等价，均为「滑块驱动 canvas/SVG 重绘」的自包含组件。

### 3.6 扩展工具箱第二批次（references/extended-viz-2.md，v1.2.0，全部真机实测）

- **Mermaid**（文本即图）：体系 DAG/流程/状态机 Markdown 原生渲染，零脚本零产物 → 降级 graphviz 出 PNG
- **pymunk**（pip，2D 刚体物理）：真实引擎计算，实测单摆 θ₀=60° 周期 +7.37%（理论 1+θ²/16=+6.85% 吻合）→ 降级 matplotlib 手绘帧
- **edge-tts**（pip，中文语音）：免费 TTS 出讲解 mp3（实测 203KB/40s，沙箱可达）→ 降级纯文字通俗版
- **交互自测 HTML + genanki**（零依赖/pip）：自检问题 → 判分组件（实测 headless 5/5）+ Anki .apkg 记忆卡 → 降级 md 内自检问题
- **trimesh → glb → model-viewer**（pip/CDN）：代码造 3D 模型，glb **base64 内嵌**单 HTML 双击即用（实测截图渲染通过）→ 降级 mp4/GIF（3D 五层）

第二批次实测坑（9 条，详见 extended-viz-2.md 各节坑表）：pymunk 只 add joint 不 add body = 模拟静默不发生（必须 `space.add(body, joint)`，测周期函数加 `len(zeros)<2` 抛错守卫）、genanki Deck/Model ID 一经发布必须固定（随机 ID 会在 Anki 重复建组）、PillowWriter 不支持 with 上下文、Unicode 下标 U+2080 缺字形（改 mathtext）、trimesh 5.x 无 torus_knot、glb 导出+设色需 scipy、model-viewer file:// CORS 拦 glb（必须 base64 内嵌或 http 服务）、headless WebGL 需 --enable-unsafe-swiftshader、Chrome 截图对工作区目录写文件被拒（指向 %TEMP%）。

## 4. 平台适配层

SKILL.md 通过「能力占位符 + 映射表」实现平台无关。四个占位符：

| 占位符 | 含义 | 缺失时降级 |
|---|---|---|
| 提问澄清 | 结构化向用户提问 | 用默认假设继续 + 交付物标注 |
| 执行命令 | 运行渲染脚本 | 产出可复制脚本请用户运行 |
| 联网核验 | WebSearch/WebFetch 交叉验证 | 标注「待核验」+ 验证路径 |
| 交互组件 | 内联 HTML 交付 | 独立 HTML 文件 |

原则：**降级不跳过**——任何能力缺失都用等效手段完成该 Phase 目标，绝不静默省略可视化环节。

## 5. 质量体系

### 5.1 质量约束（五条，SKILL.md 中声明为不可妥协）

专业严谨（事实核验）/ 通俗易懂（类比先行）/ 全面准确（含边界反例）/ 可视化优先（真实运行）/ 体系化（依赖图坐标）。

### 5.2 反例黑名单

SKILL.md 内置 6 条反模式→替代做法对照（编造数据、伪产物、循环定义、孤立讲解、炫技 3D、类比当定义），要求智能体每轮交付前对照。

### 5.3 门控机制

3 处显式门控（Phase 0 CHECKPOINT / Phase 4 STOP / Phase 5 CHECKPOINT），STOP 级别为硬阻断：可视化自检不过，禁止交付。

### 5.4 质量评分记录

本技能经鲁班 Quick 模式两轮优化：

**第一轮（2026-10-05，通用版前）：基线 76.0 → 83.8**

| 轮次 | 维度 | 改动 | Δ |
|---|---|---|---|
| R1 | 检查点 0→8 | 3 处门控落位 | +5.4 |
| R2 | 具体性 8→8.5 | 软化词硬化（工具必选、交付方式明确） | +0.9 |
| R3 | 反例黑名单 5→7.5 | 6 条反模式表 | +1.5 |

**第二轮（2026-10-05，通用版 v1.1.1）：基线 86.1 → 88.45**

| 轮次 | 维度 | 改动 | Δ |
|---|---|---|---|
| R1 | 具体性 8.5→9 | Phase 执行顺序硬化（P4 必须在 P1–3 后）+ 渲染限时 3 分钟条款 | +0.85 |
| R2 | 黑名单 7.5→8.5 | 新增 2 条反模式（硬上高阶工具干等 / 速览被撑成全流程） | +0.6 |
| R3 | 语义 8→8.5 | 设计原则与质量约束去重（回归「为什么」定位）；dim3 簇观察 +0.5 | +0.9 |

## 6. 二次开发指南

1. **改触发词**：编辑 frontmatter `description`，跑 `test-prompts.json` 的用例验证命中/误触发。
2. **加可视化手段**：在 Phase 4 选型矩阵加行 + 对应 references 加模板 + 降级链写明。模板必须含「最小可运行示例 + 自检要点 + 已知坑」三要素。
3. **加新平台适配**：在「平台适配」表加一列，占位符不变。
4. **改学习卡骨架**：Phase 5 的骨架与 Phase 1–4 产出一一对应，改动需同步门控自检项。
5. **验证方式**：拿 `test-prompts.json` 中 should_trigger 用例在目标平台实测端到端产出（重点验证：可视化真实渲染、降级标注、中文显示）。

## 7. 版本

- v1.4.0（2026-10-06）：Phase 0 升级结构化选项确认：新增主题覆盖范围（单点/带前置/完整体系）与可视化形式多选（动画/交互图/3D/配音/记忆卡）两个维度，改为禁止开放式追问、缺省策略兜底、组合规则防维度冲突；README 指令速查表补说法、test-prompts 补 typical-7
- v1.3.0（2026-10-06）：第三批对抗性审查（R4-1~R4-8）：quiz 模板 esc 转义防注入（双 Case 真机对照）；package.py 边界校验 + 手册版本号自动递增（README/TECHNICAL/test-prompts 三处联动）；TECHNICAL §3.5/3.6 顺序修正 + 坑表补全 9 条；README 过度承诺措辞修正；SKILL.md 主题名净化规则
- v1.2.2（2026-10-06）：鲁班第三轮评审（基线 94.1，ROI 网关触发跳过优化循环）——修正 SKILL.md L195 坑表计数（7 条→9 条：pymunk 4 + genanki 1 + glb 4，dim6 恢复满分）；WorkBuddy 部署副本 references 同步（补齐 extended-viz-2.md / audit-checklist.md / templates，消除 5 处引用不可达与旧版无 ravel 修复问题）。回归 25 PASS / 2 SKIP / 0 FAIL（独立子 agent 复跑复核）。
- v1.2.1（2026-10-06）：三视角对抗性审查修复（台账见 references/audit-checklist.md，13 项）——pymunk 模板静默不模拟 bug（space.add 补 body + 测周期守卫）、PyVista 多维标量 ravel、vpython/setuptools≥81 坑、graphviz dot.exe 坑、quiz 模板入库 references/templates/、Manim 版本断言实测校正（0.21.0@3.13.14）、触发词/测试用例扩充（12 条）、章节序修正；回归脚本 scripts/regression.py（25 PASS/2 SKIP/0 FAIL）；新增 VERSION 单一来源 + scripts/package.py 自动递增打包。
- v1.2.0（2026-10-06）：扩展工具箱第二批次——新增 references/extended-viz-2.md（Mermaid / pymunk / edge-tts / 交互自测 HTML + genanki / trimesh→model-viewer 3D 单文件交付），**五类模板全部真机实测**（pymunk 单摆出 GIF+周期数据、edge-tts 出 mp3、genanki 出 apkg、自测 HTML headless 判分 5/5、model-viewer 截图渲染验证），7 条实测坑回填；Phase 4 选型矩阵扩至 13 行。
- v1.1.4（2026-10-06）：双文档文件命名强制中文——主卡 `[主题]—通识可视化学习卡.md`、通俗版 `[主题]—通俗版.md`（禁止拼音/英文文件名）；可视化产物与 md 同目录、相对路径引用。经「电流」实测交付验证（`电流—通识可视化学习卡.md` / `电流—通俗版.md`）。
- v1.1.3（2026-10-06）：Phase 5 升级双文档交付——主卡 + 通俗版（固定骨架 + 三条防漂移硬规则：共用事实/术语翻译/篇幅≤40%）；速览档仅交付通俗版。
- v1.1.2（2026-10-05）：鲁班第二轮优化（86.1→88.45）：执行顺序硬化、渲染限时 3 分钟条款、反例黑名单扩至 8 条、设计原则去重。
- v1.1.0（2026-10-05）：扩展可视化工具箱——3D 五层选型（+PyVista/vpython/Blender bpy）、新增 references/extended-viz.md（ECharts/D3/p5.js/pyvis/schemdraw/Motion Canvas/GeoGebra/Desmos + 表达方式层）、Phase 4 选型矩阵扩至 10 行。
- v1.0.0（2026-10-05）：首个开源版本。通用化改造（平台适配层），含用户手册/技术手册/触发测试用例。
