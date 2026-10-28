# 技术手册 · general-knowledge-tutor

> 面向技能维护者、二次开发者，以及想弄清「它凭什么可信」的读者。
> 只想用它学习 → [用户手册](USER_GUIDE.md)；想看用法与实例 → [README](README.md)。

---

## 1. 系统架构

```text
general-knowledge-tutor/
├── SKILL.md                       # 技能主体：frontmatter(description) + 五阶段工作流 + 质量门控
├── README.md                      # 门面：概念图 + 用法 + 20 个实例
├── USER_GUIDE.md                  # 用户手册：安装、怎么问、产物、FAQ
├── TECHNICAL.md                   # 本文件：架构、规范、脚本、坑表、版本史
├── VERSION                        # 版本号单一来源（package.py 读取并递增）
├── test-prompts.json              # 触发测试用例（should_trigger / should_not_trigger）
├── LICENSE
├── references/
│   ├── manim-patterns.md          # Manim 分镜规范 + Scene 模板 + 渲染/降级
│   ├── visualization-cookbook.md  # matplotlib/plotly/SVG/交互 HTML 速查
│   ├── 3d-animation.md            # 3D 五层选型 + Blender E 层 + glb 出口 + 坑表
│   ├── extended-viz.md            # 扩展工具箱（ECharts/D3/p5.js/pyvis/GeoGebra/Desmos）
│   ├── extended-viz-2.md          # 第二批次（Mermaid/pymunk/edge-tts/自测/trimesh→model-viewer）
│   ├── audit-checklist.md         # 对抗性审查台账：改任何内容后必须过这张清单
│   ├── chart-catalog.md           # 图表目录：52 种 + 按问题选图 + 反模式 + 扩展路线
│   └── templates/
│       ├── quiz-template.html             # 自测 HTML（esc 转义 + #selftest 判分）
│       ├── selftest-web-template.html     # SELFTEST 约定（非空/交互/WebGL + a11y）
│       ├── drag-interactive-template.html # 拖对象型交互（单位圆 + 指针/键盘）
│       ├── constraint-drag-template.html  # 约束求解型交互（连杆链，拖末端按边长重排）
│       └── model-viewer-template.html     # glb→单文件可交互 3D（内联库 + base64）
├── scripts/
│   ├── package.py                 # 打包：VERSION 单一来源 + 原子递增 + 三份手册同步 + zip 自检
│   ├── regression.py              # 全量回归：代码块真机执行 + headless 断言 + 文档一致性
│   ├── selftest_web.py            # 交互/3D 产物断言器（Chrome headless，退出码 0/1/2）
│   ├── make_readme_figures.py     # 生成 README 概念图（docs/images/01~04）
│   ├── chart_gallery.py           # 52 种图表定义 + 分类注册表 + 拼版
│   └── chart.py                   # 按需调用 CLI：--list/--search/--json/<名称>/--all
└── docs/images/                   # 概念图、真实产出示例、52 张图表与拼版（入包）
```

**设计定位**：声明式技能 + 少量工程脚本。交付物由智能体运行时按模板生成；`scripts/` 只服务技能自身的**打包、自检、回归与图表渲染**，不参与运行时交付。

### 1.1 触发机制

命中由 `SKILL.md` frontmatter 的 `description` 驱动，埋入三类词族：动作词（搞懂/理解/讲讲/本质/系统学）、方法词（第一性原理/可视化讲解/做个动画/面试讲解）、产物词（通俗版/讲给外行听/出几道题测测我/记忆卡）。`test-prompts.json` 覆盖典型命中、模糊命中与近似误触发。

## 2. 五阶段工作流规范

### Phase 0 意图定位
输出五元组 `(主题, 深度, 覆盖, 基础, 可视化)`。结构化选项确认，禁止开放式追问；用户已给则跳过；一次最多 4 问，主题从 query 推断、深度与覆盖可合并、超限分批、多选必须带「自动」兜底。未确认默认：精通 + 带前置 + 有相关背景 + 自动，并在交付物标注。

### Phase 1 第一性原理拆解
假设清单（3–6 条，区分承重/情景）+ 原子事实（标来源类型）+ 推理链（每步 A+B→C）。推理链是 Phase 3 与 Phase 4 的主干，不允许后补。

### Phase 2 体系化知识地图
概念 DAG（核心/支撑/延伸）+ 跨学科坐标，强制 Mermaid 或 SVG，禁止纯文字描述依赖。

### Phase 3 本质理解
一句话本质（主谓宾、禁循环定义）→ 1–2 个类比 → **每个类比紧跟失效边界** → 存在动机 → 适用条件与反例。

### Phase 4 可视化生产
选型矩阵（按概念类型）：

| 概念类型 | 首选 | 降级链 |
|---|---|---|
| 过程/流程/演化 | Manim 分镜动画 | matplotlib 帧序列 → ffmpeg MP4（循环用 GIF）→ SVG 分步图 |
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

**2D 备选图强制**：凡选 3D，必须同时产出一张同概念的 2D 备选图（最直白的视角），用于降级、离线阅读与快速浏览。

**成本档**：mplot3d + GIF（秒级、零依赖）< PyVista（GPU，秒~十秒级）< Manim（6~30 秒/件）< Blender（分钟级、需本机应用）；vpython / Three.js / model-viewer 需浏览器，内联后可离线。

### Phase 4.1 3D 与 Blender 调用决策清单

**① 空间维度闸**：判定问句同上；否 → 概念定义 / 数据分布 / 流程时间线 / 体系 DAG 老实做 2D。

**② 反向门控**：公式推导 → Manim；数据分布 → matplotlib / plotly；参数探索 → 交互 HTML。这类不上 3D。

**③ 依赖探测**（四个都探）：`blender.exe` 走 PATH → 常见目录（`Program Files/Blender Foundation/*`）→ 注册表，Windows 上通常不在 PATH；`trimesh` / `pyvista` / `manim` 走 `import` 且必须**跨解释器**扫。**探测结论 = 环境现状而非能力上限**：三者都是 pip 包，允许先装再用（隔离 venv 优先）；只有 Blender 是桌面应用、装不了才真没有。确实都用不了才降 mplot3d + GIF 或交互 HTML。

**④ 质感门槛**：场 / 曲面 / 体数据 → PyVista；只有光路 / 机构 / 晶格 / 流体 / 拓扑 / 分子构型这类需要 Cycles 光追、Mantaflow 流体、刚体约束、glTF 导出的才上 E 层 Blender。Blender 不在本机时按能力拆开降级：光路/材质 → mplot3d 或 Manim ThreeDScene；刚体/流体 → pymunk 或 Manim 手绘帧（PyVista 做不了动力学仿真）；晶格/分子/拓扑 → trimesh 或 PyVista 建网格导 glb/PNG。

**两种出口**，优先前者：① glb + model-viewer（导出带材质 glb → base64 内联单文件 HTML，读者自己转、断网可开；**glb 有两个来源**：Blender `export_scene.gltf` 或纯 Python trimesh）；② mp4/gif 录像（仅运镜叙事）。

**两条硬规则**：上了 E 层不等于只用 Blender；凡上 3D 必配 2D 备选图。

### Phase 5 交付
统一骨架：一句话本质 → 第一性原理拆解 → 体系坐标 → 通俗理解 → 边界与反例 → 可视化 → 学习路径 → 自检问题 → 参考来源。深度=精通/输出另交通俗版（≤ 主卡 40%）。命名强制「主题—用途」，非法字符替换为「－」。

## 3. 工程脚本

### 3.1 package.py（打包与版本同步）

```bash
python scripts/package.py --bump patch --note "一句话变更"
```

**原子递增**：先 `preflight_manuals()` 预检三份手册锚点，任一不可定位即整体失败、磁盘零改动；预检通过才写手册，`VERSION` 最后落盘。同步范围：`README.md` / `USER_GUIDE.md` 的「> 当前版本：」锚点、`TECHNICAL.md` §7 版本史、`test-prompts.json`。

### 3.2 regression.py（全量回归）

```bash
python scripts/regression.py      # 代码块真机执行 + headless 断言 + 文档一致性 + 图表校验
```

覆盖：references 五份文档的代码块逐一真机执行（bpy 用 `blender -b --factory-startup -P`）、四类模板 headless 断言、双文档约束、Phase 0 结构、文档交叉一致性（黑名单条数 / 选型矩阵行数 / 目录树 / 五处版本号 / 配图存在性）、图表目录与画廊、图表 CLI 边界与注册表完整性。

### 3.3 selftest_web.py（交互 / 3D 断言器）

页面需暴露 `window.__SELFTEST__()`；`#selftest` 打开时把结果写入 DOM。退出码 0=通过 / 1=断言失败 / 2=环境问题。

### 3.4 图表：注册表 + 按需调用

`chart_gallery.py` 定义 52 个渲染函数与分类注册表；`chart.py` 提供按需调用：

```bash
python scripts/chart.py --list              # 12 个分类 / 52 种
python scripts/chart.py --search 分布        # 关键词检索
python scripts/chart.py --json              # 机器可读清单
python scripts/chart.py 箱线图 --out a.png   # 只渲染一张
python scripts/chart.py --all               # 全量 + 拼版
```

**退出码约定**：`0` 成功（含「无匹配」）/ `1` 名称未知（附相近名称提示）/ `2` 参数缺失或渲染异常。

注册表只维护「名称 → 分类」，文件名用 `inspect.getsource` 从函数内 `save(fig, "xxx")` 解析，**不维护第二份真值**。

### 3.5 make_readme_figures.py

生成 `docs/images/01~04` 概念图（matplotlib + 微软雅黑）。

## 4. 质量门控

- **可视化 STOP**：产物未通过真实运行自检（存在、可播放、中文正常）不得进入 Phase 5。
- **交互 / 3D 强制断言**：必须通过 `selftest_web.py`，退出码 0 才放行。
- **无障碍底线**：`<meta name="viewport">`、`:focus-visible`、动画类带 `prefers-reduced-motion`。
- **反例黑名单**：内置 **8 条**反模式（编造数据 / 伪产物 / 循环定义 / 单点孤立 / 为炫技上 3D / 把类比当定义 / 无依赖硬上高阶工具 / 把速览撑成完整流程）。

## 5. 实测坑表

| 坑 | 现象 | 处置 |
|---|---|---|
| 帧序列合成 MP4 | libx264 要求宽高偶数，奇数尺寸整条失败 | `-vf scale=trunc(iw/2)*2:trunc(ih/2)*2` |
| 中文控制台 | GBK 下打印中文 `UnicodeEncodeError`，常崩在汇总前 | `reconfigure(encoding="utf-8")` + 子进程 `PYTHONIOENCODING` |
| LaTeX 缺失 | `MathTex` 直接失败无产物 | 探测 `latex`/`dvisvgm`，缺失降级纯文本公式 |
| 配音依赖 | manim-voiceover 缺后端会交互式询问并挂死；SoX 缺装 | 改 edge-tts 出 mp3 + srt，再 ffmpeg 合体 |
| 体渲染透明 | 深度伪影导致遮挡错误 | PyVista 开 `enable_depth_peeling` |
| 3D 导出 | 曲线对象不在 glTF 范围，静默丢几何 | 先 `convert(target="MESH")` 再 `export_scene.gltf` |
| 圆柱朝向 | 直接给 rotation_euler 会歪 | `to_track_quat("Z", "Y")` 对齐方向 |
| 3D 质量 | 默认渲染发糊 | PyVista 开 `ssaa`；Blender 先小分辨率出样片 |
| 体渲染 | 多维标量未 `ravel` 触发数量校验失败 | 显式 `ravel(order="F")` |
| plotly 静态导出 | 缺 `kaleido` 直接报错 | 探测 `import kaleido`，缺失改 `write_html` 或 matplotlib |
| edge-tts 合成 | WebSocket 403（`Sec-MS-GEC` 带时间戳） | 先查系统时钟，再升级 edge-tts，最后降级本地 TTS |
| 交互自测 | 白屏 / 死控件看起来像正常页面 | SELFTEST 断言 + 空白画布反面用例 |
| 约束拖拽 | 只加 joint 不加 body 会静默不动 | `space.add(body, joint)` + 周期守卫 |
| 离线 3D | `<model-viewer src="./x.glb">` 双击被 CORS 拦 | glb 内联 data URI 或起 http 服务 |
| 无头 WebGL | 部分 Chrome 拿不到 context | `--enable-unsafe-swiftshader`；拿不到判 skip 而非 fail |
| 中文字体 | 只设 `font.family` 时，networkx / Sankey 标签回落 DejaVu Sans 变方框 | **同时设 `font.sans-serif`** |
| 图表 CLI | 「无匹配」返回 3，与 0/1/2 约定冲突，脚本误判为故障 | 无匹配返回 0 并提示（R12-1） |

## 6. 发布流程

```bash
python scripts/regression.py                                   # 1. 全绿（FAIL 必须 0）
python scripts/chart.py --all                                  # 2. 若改了图表，重渲染
python scripts/package.py --bump patch --note "本次变更"         # 3. 原子递增 + 打包
git add -A && git commit -m "vX.Y.Z: ..." && git push          # 4. 推源码 + tag
gh release create vX.Y.Z dist/<zip> README.md USER_GUIDE.md TECHNICAL.md --notes-file <notes>
```

发布前对照 [references/audit-checklist.md](references/audit-checklist.md) 兜底。

## 7. 版本

- v1.9.0（2026-10-29）：重写 README/用户手册/技术手册：README 新增用法说明与 20 个使用实例、概念图与图表画廊；技术手册补图表 CLI 与退出码约定；修复 chart.py 无匹配返回 3 与文档 0/1/2 冲突（R12-1）；新增 viz-图表CLI边界 断言（未知=1 缺参=2 无匹配=0 + 注册表完整性）
- v1.8.0（2026-10-29）：图表第三批扩容（42 → 52 种）+ 按需调用：新增 scripts/chart.py（--list/--search/--json/点名渲染/--all）与注册表；新增百分比堆叠/发散条/哑铃/CDF/生存曲线/控制图/时间线/流程图/决策树/标签云；补 import re；回归阈值提到 50 并新增按需调用断言
- v1.7.0（2026-10-29）：图表第二批扩容（25 → 42 种）：阶梯/置信带/迷你图/帕累托/子弹/仪表/华夫/玫瑰/云雨/联合分布/六边形/QQ/森林/韦恩/弧线/日历热力/矢量场
- v1.6.0（2026-10-29）：图表目录（25 种）+ chart_gallery.py 真机画廊；矩阵扩到 20 行；修复 networkx/Sankey 中文方框
- v1.5.9（2026-10-26）：重写三份文档；package.py 原子递增（修复版本史断档）
- v1.5.8（2026-10-07）：第六批三视角审查（R7-1~R7-6），Blender 决策清单三处判定缺陷
- v1.5.7（2026-10-07）：新增「3D 与 Blender 调用决策清单」四道闸
- v1.5.6（2026-10-07）：3D 优先档（双向门控）
- v1.5.5（2026-10-07）：交互三分类与 constraint-drag 模板
- v1.5.4（2026-10-07）：Blender E 层真机验证 + glb→model-viewer 出口
- v1.5.3（2026-10-07）：Blender 从 SKIP 改为真机执行
- v1.5.2（2026-10-07）：SELFTEST 强制 + 2D 备选图强制 + 无障碍
- v1.5.1（2026-10-07）：跨解释器依赖画像 + LaTeX 探测 + MP4 降级档
- v1.5.0（2026-10-07）：Phase 0 结构化选项上限约束
- v1.4.0（2026-10-06）：Phase 0 五项确认；第二批次产物命名
- v1.3.0（2026-10-06）：第三批审查（R4-1~R4-5）
- v1.2.2（2026-10-06）：第二批次扩展工具箱
- v1.2.1（2026-10-06）：首轮三视角审查修复（13 项）
- v1.2.0（2026-10-06）：extended-viz-2.md 与五类模板真机实测
- v1.1.0（2026-10-05）：3D 五层选型 + extended-viz.md
- v1.0.0（2026-10-05）：五阶段工作流骨架
