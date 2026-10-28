# 技术手册 · general-knowledge-tutor

> 面向技能维护者、二次开发者、以及想弄清「它凭什么可信」的读者。
> 只想用它学习 → 看 [用户手册](USER_GUIDE.md)；想先了解这是什么 → 看 [README](README.md)。

> 当前版本见 [VERSION](VERSION) 与 §7 版本史。

---

## 1. 系统架构

```text
general-knowledge-tutor/
├── SKILL.md                       # 技能主体：frontmatter(description 触发词) + 五阶段工作流 + 质量门控
├── README.md                      # 门面：概念图 + 能力概览 + 30 秒上手
├── USER_GUIDE.md                  # 用户手册：安装、怎么问、产物怎么读、FAQ
├── TECHNICAL.md                   # 本文件：架构、规范、脚本、坑表、版本史
├── VERSION                        # 版本号单一来源（package.py 读取并递增）
├── test-prompts.json              # 触发测试用例（should_trigger / should_not_trigger）
├── LICENSE
├── references/
│   ├── manim-patterns.md          # Manim 分镜规范 + 可复用 Scene 模板 + 渲染/降级
│   ├── visualization-cookbook.md  # matplotlib/plotly/SVG/交互 HTML 速查模板
│   ├── 3d-animation.md            # 3D 五层选型 + Blender E 层 + glb 出口 + 坑清单
│   ├── extended-viz.md            # 扩展工具箱（ECharts/D3/p5.js/pyvis/schemdraw/GeoGebra/Desmos）
│   ├── extended-viz-2.md          # 第二批次（Mermaid/pymunk/edge-tts/自测 HTML+genanki/trimesh→model-viewer）
│   ├── audit-checklist.md         # 对抗性审查台账：改任何内容后必须过这张清单
│   ├── chart-catalog.md           # 图表目录：42 种图表 + 按问题类型选图 + 反模式 + 扩展路线
│   └── templates/
│       ├── quiz-template.html             # 自测 HTML（esc 转义防注入 + #selftest 判分模式）
│       ├── selftest-web-template.html     # SELFTEST 约定（非空/交互/WebGL 断言 + a11y）
│       ├── drag-interactive-template.html # 拖对象型交互（单位圆拖拽 + 指针/键盘 + 断言）
│       ├── constraint-drag-template.html  # 约束求解型交互（连杆链：拖末端，其余按边长重排）
│       └── model-viewer-template.html     # glb→单文件可交互 3D（内联渲染库 + base64 glb）
├── scripts/
│   ├── package.py                 # 一键打包：VERSION 单一来源 + 原子递增 + 三份手册版本同步 + zip 自检
│   ├── regression.py              # 全量回归：代码块真机执行 + headless 断言 + 文档一致性
│   ├── selftest_web.py            # 交互/3D 产物断言器（Chrome headless，退出码 0/1/2）
│   ├── make_readme_figures.py     # 生成 README 概念图（matplotlib，输出到 docs/images）
│   └── chart_gallery.py           # 真实渲染 42 种图表 + 拼版（chart-catalog.md 的可执行证据）
└── docs/images/                   # README 概念图、真实产出示例、图表画廊（打包时一并入包）
```

**设计定位**：声明式技能 + 少量工程脚本。技能交付物由智能体在运行时按模板生成；`scripts/` 下的脚本只服务**技能自身的打包、自检与回归**，不参与运行时交付。好处是跨平台零适配；代价是依赖宿主具备「写文件 + 执行命令」能力。

### 1.1 触发机制

技能命中由 `SKILL.md` frontmatter 的 `description` 驱动，其中显式埋入触发词族：

- 动作词：搞懂 / 理解 / 讲讲 / 原理 / 本质 / 科普 / 教学 / 入门 / 系统学
- 方法词：第一性原理 / 可视化讲解 / 做个动画 / 面试讲解
- 产物词：通俗版 / 讲给外行听 / 出几道题测测我 / 记忆卡

`test-prompts.json` 覆盖三类：典型命中、模糊命中（如「复利是不是利滚利」）、近似误触发（如「写个批量重命名脚本」应不命中）。改动 description 后必须重跑判定。

## 2. 五阶段工作流规范

### Phase 0 意图定位
输入：用户 query。输出五元组 `(主题, 深度, 覆盖, 基础, 可视化)`。
确认方式：结构化选项，**禁止开放式追问**；用户已给则跳过。
组合规则：深度=速览时忽略可视化与覆盖范围；覆盖范围默认对齐深度；显式指定则覆盖。
提问上限：多数运行时一次最多 4 问，因此主题从 query 推断、深度与覆盖可合并、超限分两批、多选必须带「自动」兜底项。
未确认默认值：精通 + 带前置 + 有相关背景 + 可视化自动，且必须在交付物开头标注该假设。
门控：五项确认（或超时走默认）后才进入 Phase 1。

### Phase 1 第一性原理拆解
产出三件套：假设清单（3–6 条，区分承重/情景）、原子事实（每条标来源类型）、推理链（每步「A+B→C」）。推理链是 Phase 3 讲解与 Phase 4 分镜的主干，不允许后补。

### Phase 2 体系化知识地图
概念 DAG（核心层/支撑层/延伸层）+ 跨学科坐标。表达强制用 Mermaid（优先）或 SVG（兜底），禁止纯文字描述依赖关系。

### Phase 3 本质理解
一句话本质（主谓宾，禁止循环定义）→ 1–2 个类比 → **每个类比必须紧跟失效边界** → 存在动机 → 适用条件与反例。

### Phase 4 可视化生产
选型矩阵（按概念类型）：

| 概念类型 | 首选 | 降级链 |
|---|---|---|
| 过程/流程/演化 | Manim 分镜动画 | matplotlib 帧序列 → ffmpeg MP4（循环场景用 GIF）→ SVG 分步图 |
| 几何/证明/空间 | Manim | SVG 静态图 |
| 数据/分布/关系 | matplotlib / plotly | SVG 手绘 |
| 概念/体系/依赖 | Mermaid / SVG | 文本缩进树 |
| 可探索参数 | HTML widget（滑块 + canvas） | 静态多状态图 |
| 空间结构/旋转/场 | 3D（五层选型见 §3.3） | 静态 3D 多视角 PNG |
| 场/曲面/体渲染 | PyVista（深度排序正确） | mplot3d 多视角 PNG |
| 物理/轨道/仿真教学 | vpython | p5.js 动画 / 分步静态图 |
| 函数/几何交互探索 | GeoGebra / Desmos iframe | 滑块 HTML widget |
| 网络/关系/流向 | pyvis / graphviz；桑基等用 ECharts | Mermaid 手写 |
| 结构/流程/状态机/体系 DAG | Mermaid 文本即图 | graphviz 出 PNG |
| 力学/碰撞/真实物理过程 | pymunk 物理引擎真实模拟 | matplotlib 手绘帧动画 |
| 讲解可听化 / 3D 可交互 / 自测闭环 | edge-tts 配音 + model-viewer 单文件 3D + 自测 HTML/genanki | 纯文字通俗版 / mp4 动画 |
| 分布形态（偏态/多峰/离群） | 直方图+KDE / 箱线 / 小提琴 / 山脊 | 条带图（样本 <20） |
| 构成与占比 | 堆叠柱 / 树状图 / 旭日图 | 百分比条形（饼图仅 ≤5 类） |
| 流向与转化 | 桑基图 / 漏斗图 | 两列对比条形 + 转化表 |
| 进度与排期 | 甘特图 / 时间线 | 里程碑表 |
| 多维比较与权衡 | 平行坐标 / 雷达图 / 斜率图 | 小倍数图 |
| 统计推断与不确定性 | 误差棒 / 置信带 / 森林图 | 文字给区间 + 样本量 |
| 空间分布与场（2D） | 等高线 / 相图 / choropleth | 分块示意图 |

**3D 启用门槛**：仅当空间结构本身承载信息（旋转→振荡、螺旋、场、曲面、轨道）时启用；2D 能讲清的不上 3D。

**3D 优先档**：带空间维度的知识点**默认产出 3D**（结构/旋转/轨道/场/曲面/机构/光路/拓扑/晶格/分子构型），交互优先（glb 可拖拽 > 视频），不依赖用户点名。判定问句：把 3D 换成 2D 会不会丢掉「转一下才能看见」的信息——会就上，不会就老实做 2D。

**2D 备选图强制**：凡选 3D，必须同时产出一张同概念的 2D 备选图（最直白的那个视角），用于降级、离线阅读与快速浏览——降级要真·就绪，不能临时补。

**成本档**：mplot3d + GIF（秒级、零依赖）< PyVista（GPU，秒~十秒级）< Manim（6~30 秒/件）< Blender（分钟级、需本机应用）；vpython / Three.js / model-viewer 需浏览器，内联后可离线。同等讲解效果下选成本最低的一档。

### Phase 4.1 3D 与 Blender 调用决策清单

过闸顺序从左到右，任一不通过就走它的「否则」分支。**不要因为本机装了 Blender 就到处用**——E 层是最高成本档，不是默认档。

**① 空间维度闸**：判定问句同上；否 → 概念定义 / 数据分布 / 流程时间线 / 体系 DAG 老实做 2D。

**② 反向门控**：公式推导 → Manim（讲到哪画到哪）；数据分布 → matplotlib / plotly；参数探索 → 交互 HTML。这类不上 3D。

**③ 依赖探测**（四个都要探，别只探一个）：`blender.exe` 走 PATH → 常见目录（`Program Files/Blender Foundation/*`）→ 注册表，Windows 上它通常不在 PATH；`trimesh` / `pyvista` / `manim` 走 `import` 且必须**跨解释器**扫，单解释器会误判「没装」。**探测结论 = 环境现状而非能力上限**：三者都是 pip 包，允许先装再用（隔离 venv 优先）；只有 Blender 是桌面应用、装不了才真没有。确实都用不了才降 mplot3d + GIF 或交互 HTML，并在交付物注明降级原因。

**④ 质感门槛**：场 / 曲面 / 体数据 → PyVista（更快、更科学、深度排序正确）；只有光路 / 机构 / 晶格 / 流体 / 拓扑 / 分子构型这类需要 Cycles 光追、Mantaflow 流体、刚体约束、glTF 导出的才上 E 层 Blender。**Blender 不在本机时按能力拆开降级，别硬塞给做不了的库**：光路/材质/运镜 → mplot3d 或 Manim ThreeDScene；刚体/流体/烟雾 → pymunk 或 Manim 手绘帧（PyVista 做不了动力学仿真）；晶格/分子构型/拓扑 → trimesh 或 PyVista 建网格导 glb/PNG。

**过闸后的两种出口**，优先上面那条：

1. **glb + model-viewer**（默认首选）：导出带材质 glb → 与渲染库一起 base64 内联成单文件 HTML，读者自己转着看，断网可开。**glb 有两个来源，别绑死在 Blender 上**：有 Blender 用 `export_scene.gltf`（PBR 材质完整）；没有也能出——trimesh 纯 Python 造 glb（几何较简陋、无材质）。所以「没装 Blender」不等于「做不了可交互 3D」。
2. **mp4 / gif 录像**：只在确实需要运镜叙事时用——观众只能被动看。

**两条硬规则**：上了 E 层不等于只用 Blender（场与曲面归 PyVista，公式推导归 Manim）；凡上 3D 必配 2D 备选图。

### Phase 5 交付
统一骨架：一句话本质 → 第一性原理拆解 → 体系坐标 → 通俗理解 → 边界与反例 → 可视化 → 学习路径 → 自检问题 → 参考来源。深度=精通/输出时另交通俗版（≤ 主卡 40%）。文件命名强制「主题—用途」，主题中的 `/:*?"<>|` 替换为「－」。

## 3. 工程脚本

### 3.1 package.py（打包与版本同步）

```bash
python scripts/package.py                  # 按当前 VERSION 打包
python scripts/package.py --bump patch     # 递增 patch 位并同步三份手册
python scripts/package.py --bump minor --note "变更一句话"
```

**原子递增（v1.5.9 起）**：先 `preflight_manuals()` 预检三份手册的锚点，任何一项不可定位就整体失败、**磁盘零改动**；预检通过才写手册，`VERSION` 最后落盘。

> 历史缺陷：旧实现先写 VERSION 再同步手册。同步失败会留下「VERSION 已递增、手册没更新」的半成品，重跑还会叠加版本号。真机复现证据：技术手册版本史出现 `1.5.11 → 1.5.9` 断档（缺 1.5.10）。

同步范围：`README.md` / `USER_GUIDE.md` 的「> 当前版本：」锚点行、`TECHNICAL.md` §7 版本史、`test-prompts.json` 的 version 字段。

### 3.2 regression.py（全量回归）

```bash
python scripts/regression.py      # 全量：代码块真机执行 + headless 断言 + 文档一致性
```

覆盖范围：references 五份文档的代码块逐一真机执行（bpy 代码块用 `blender -b --factory-startup -P` 真机跑）、quiz / 拖拽 / 约束拖拽 / selftest 四类模板的 headless 断言、双文档约束（命名 / 篇幅 / 禁用词）、Phase 0 结构断言、文档交叉一致性（黑名单条数 / 选型矩阵行数 / 目录树 / 五处版本号）、package.py 边界用例。

### 3.3 selftest_web.py（交互 / 3D 断言器）

```bash
python scripts/selftest_web.py                 # 自检内置模板
python scripts/selftest_web.py 产物.html        # 断言具体产物
python scripts/selftest_web.py 产物.html --json # 机器可读
```

约定：页面暴露 `window.__SELFTEST__() → {pass, checks}`；`#selftest` 打开时把结果写入 DOM。退出码 0=通过 / 1=断言失败 / 2=环境问题。

### 3.4 make_readme_figures.py（文档配图）

```bash
python scripts/make_readme_figures.py   # 生成 docs/images/01~04 概念图
```

依赖 matplotlib 与中文字体（微软雅黑 / SimHei）。图 05、06 是真实产出示例，直接取自学习包产物。

## 4. 质量门控

- **可视化 STOP**：产物未通过真实运行自检（存在、可播放、中文正常）不得进入 Phase 5，必须降级并注明。
- **交互 / 3D 强制断言**：必须暴露 `__SELFTEST__` 并通过 `selftest_web.py`，退出码 0 才放行。
- **无障碍底线**：`<meta name="viewport">`、`:focus-visible`、动画类带 `prefers-reduced-motion`。
- **反例黑名单**：内置 **8 条**反模式（编造数据、伪产物、循环定义、单点孤立、为炫技上 3D、把类比当定义、无依赖硬上高阶工具、把速览撑成完整流程），每轮对照。

## 5. 实测坑表

| 坑 | 现象 | 处置 |
|---|---|---|
| 帧序列合成 MP4 | libx264 要求宽高偶数，奇数尺寸整条失败 | `-vf scale=trunc(iw/2)*2:trunc(ih/2)*2` |
| 中文控制台 | GBK 下打印中文说明 `UnicodeEncodeError`，常崩在汇总前 | 脚本 `reconfigure(encoding="utf-8")` + 子进程 `PYTHONIOENCODING` |
| LaTeX 缺失 | `MathTex` 直接失败，无产物 | 探测 `latex` / `dvisvgm`，缺失降级纯文本公式 |
| 配音依赖 | manim-voiceover 缺后端会交互式询问并挂死；SoX 缺装 | 改用 edge-tts 出 mp3 + srt，再 ffmpeg 合体 |
| 体渲染透明 | 深度伪影导致前后遮挡错误 | PyVista 开 `enable_depth_peeling`（而非只淡化辅助元素） |
| 3D 导出 | 曲线对象不在 glTF 导出范围，静默丢几何 | 先 `convert(target="MESH")` 再 `export_scene.gltf` |
| 圆柱朝向 | 直接给 rotation_euler 会歪 | `to_track_quat("Z", "Y")` 对齐方向向量 |
| 3D 质量 | 默认渲染发糊 | PyVista 开 `ssaa`，Blender 先小分辨率出样片再抬规格 |
| 体渲染 | 多维标量未 `ravel` 触发数量校验失败 | 显式 `ravel(order="F")` |
| plotly 静态导出 | `write_image` 缺 `kaleido` 直接报错；新版本还需 `kaleido<1` 才稳 | 先探测 `import kaleido`，缺失则改 `write_html` 或 matplotlib 出图 |
| edge-tts 合成 | WebSocket 403（`Sec-MS-GEC` 是带时间戳的 DRM token） | 先查系统时钟是否同步、再升级 edge-tts，最后降级为本地 TTS（CapsWriter / PotPlayer） |
| 交互自测 | 白屏 / 死控件看起来像正常页面 | SELFTEST 断言 + 空白画布反面用例 |
| 约束拖拽 | 只加 joint 不加 body 会静默不动 | `space.add(body, joint)` + 周期守卫 |
| 离线 3D | `<model-viewer src="./x.glb">` 双击被 CORS 拦 | glb 内联 data URI（单文件）或起 http 服务 |
| 无头 WebGL | 部分 Chrome 版本拿不到 context | 加 `--enable-unsafe-swiftshader`；拿不到判 skip 而非 fail |
| 包管理器 | winget 下载 GitHub release 报 `InternetOpenUrl() failed` | 直连下载 zip 解压，或走本机代理 |
| GitHub API | `gh` 直连超时 | 设置 `HTTPS_PROXY`；SSH 推送走 22 端口不受影响 |

## 6. 发布流程

```bash
python scripts/regression.py                                   # 1. 全绿（FAIL 必须为 0）
python scripts/make_readme_figures.py                          # 2. 若改了图，重新生成
python scripts/package.py --bump patch --note "本次变更一句话"   # 3. 原子递增 + 打包
git add -A && git commit -m "vX.Y.Z: ..." && git push          # 4. 推源码
gh release create vX.Y.Z dist/<zip> README.md USER_GUIDE.md TECHNICAL.md --notes-file <notes>
```

发布前对照 [references/audit-checklist.md](references/audit-checklist.md) 兜底校验。

## 7. 版本

- v1.7.0（2026-10-29）：图表第二批扩容（25 → 42 种）：新增阶梯/置信带/迷你图/帕累托/子弹/仪表/华夫/玫瑰/云雨/联合分布/六边形分箱/QQ/森林/韦恩/弧线/日历热力/矢量场；修复子弹图文字重叠与仪表缺底轨；回归阈值提到 40
- v1.6.0（2026-10-29）：图表类型扩容：新增 references/chart-catalog.md（25 种图表 + 按问题选图 + 反模式）与 scripts/chart_gallery.py 真机画廊；选型矩阵扩至 20 行；修复 networkx/Sankey 中文标签方框（font.sans-serif）
- v1.5.9（2026-10-26）：重写三份文档（README 门面 + USER_GUIDE 用户手册 + TECHNICAL 技术手册），新增 docs/images 概念图与生成脚本；package.py 改为原子递增并支持三份手册同步（修复「VERSION 已递增但手册未更新」的半成品缺陷）；新增三处回归断言（文档存在性 / 配图存在性 / 五处版本号一致）
- v1.5.8（2026-10-07）：第六批三视角对抗性审查（R7-1~R7-6）——修复 Blender 决策清单三处判定缺陷（glb 通道未含 trimesh、把探测不到当装不了、降级把能力塞给做不了的库），新增 viz-Blender决策清单 回归断言并做反永真验证
- v1.5.7（2026-10-07）：SKILL.md / TECHNICAL.md 新增「3D 与 Blender 调用决策清单」四道闸 + 两种出口优先级 + 两条硬规则
- v1.5.6（2026-10-07）：3D 优先档（双向门控），带空间维度的知识点默认产出 3D
- v1.5.5（2026-10-07）：交互三分类（拖参数 / 拖对象 / 拖视角）与 constraint-drag 模板
- v1.5.4（2026-10-07）：Blender E 层真机验证 + glb→model-viewer 单文件出口
- v1.5.3（2026-10-07）：Blender 从 SKIP 改为真机执行；Cycles 判定改为赋值 + try
- v1.5.2（2026-10-07）：交互产物 SELFTEST 强制 + 2D 备选图强制 + 无障碍底线
- v1.5.1（2026-10-07）：跨解释器依赖画像 + LaTeX 探测 + MP4 降级档
- v1.5.0（2026-10-07）：Phase 0 结构化选项上限约束与分批策略
- v1.4.0（2026-10-06）：Phase 0 五项结构化确认；第二批次产物中文命名
- v1.3.0（2026-10-06）：第三批对抗性审查（R4-1~R4-5），package.py 边界校验
- v1.2.2（2026-10-06）：第二批次扩展工具箱（Mermaid / pymunk / edge-tts / 自测 / genanki）
- v1.2.1（2026-10-06）：首轮三视角审查修复（13 项）
- v1.2.0（2026-10-06）：extended-viz-2.md 与五类模板真机实测
- v1.1.0（2026-10-05）：3D 五层选型 + extended-viz.md
- v1.0.0（2026-10-05）：五阶段工作流骨架
