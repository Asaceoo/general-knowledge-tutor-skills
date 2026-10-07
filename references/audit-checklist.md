# 对抗性审查台账（audit-checklist）

> 2026-10-06 首轮三视角对抗性审查（audit-loop 工作流）。审查对象：SKILL.md + references/ 全部 5 个 md + templates/ + 电流实例交付。
> 证据纪律：每个结论有真实工具输出背书；回归命令见文末，修复后基线 **25 PASS / 2 SKIP / 0 FAIL**。

## 问题台账

| # | 视角 | 问题 | 真实证据（原文） | 修法 | 状态 |
|---|---|---|---|---|---|
| 1 | 实现者 | pymunk 模板只 `space.add(joint)` 未 add body → **摆不被模拟且无任何报错**，measure_period 无守卫返回 `0/(0-1)=-0.0`（静默错误结果） | 回归输出 `θ0=60° T=-0.0000s` | 模板改 `space.add(body, joint)`；measure_period 加 `len(zeros)<2 抛错` 守卫；坑表新增 #0 | ✅ |
| 2 | 实现者 | PyVista 体渲染模板多维标量未 ravel：新版 pyvista 严格校验，`(40,40,40)` 被判「40 个标量」；`np.c_[a,b,c]` 得 `(40,40,120)` 同炸 | `ValueError: Number of scalars (40) must match either the number of points (64000)...` | `v` 与 `vec` 均显式 `ravel(order="F")`（vec 修复曾漏，二次回归抓回） | ✅ |
| 3 | 实现者 | vpython 依赖 `pkg_resources`，**setuptools ≥81 已移除该模块**（新环境默认 84.x 直接炸） | `ModuleNotFoundError: No module named 'pkg_resources'`（装完 setuptools 84 仍复现→才定位版本根因） | 坑注：先 `pip install "setuptools<81"` 再装 vpython | ✅ |
| 4 | 实现者 | graphviz 模板声称「pip install graphviz 即可」，实际只装 Python 绑定 | `ExecutableNotFound: failed to execute WindowsPath('dot')` | 模板注释纠正：dot.exe 需单独装 Graphviz 系统包；无则降级 pyvis/Mermaid；回归显式 SKIP | ✅ |
| 5 | 实现者 | cookbook 动画块依赖上一块的 import（单独复制即 `NameError: plt`） | `NameError: name 'plt' is not defined` | 块内补独立 import | ✅ |
| 6 | AI 使用方 | quiz 完整模板写成「见本仓库 release 附件或示例目录」——**两者当时都不存在**，照文档找不到模板 | 文档检索无该文件 | 模板入库 `references/templates/quiz-template.html`，文档指向真实路径 | ✅ |
| 7 | 审查者 | SKILL.md 断言「Manim 渲染需 3.10–3.12」与真机矛盾 | `deeptutor env: Python 3.13.14 + manim 0.21.0`（傅里叶实例已渲染） | 改「3.10–3.13（0.21.0 已实测于 3.13.14）」 | ✅ |
| 8 | AI 使用方 | description 触发词未覆盖双文档/自测/记忆卡场景 | ——（文本审查） | 补「通俗版 / 讲给外行听 / 出几道题测测我 / 记忆卡」 | ✅ |
| 9 | 审查者 | test-prompts.json 停在 v1.0.0（6 用例，无新能力覆盖） | 字段 version=1.0.0, date=2026-10-05 | 升 v1.2.1：+3 should_trigger（物理模拟/双文档+自测/3D 可交互）+2 should_not_trigger | ✅ |
| 10 | 审查者 | TECHNICAL §3 章节乱序（3.3→3.5→3.4→3.6） | 标题行序检查 | 3.4/3.5 对调，README 引用同步 §3.4–3.6 | ✅ |
| 11 | 实现者 | genanki 模板 `CARDS` 未定义即使用（占位不明） | `NameError: name 'CARDS' is not defined` | 模板内嵌占位示例行 + 注释说明 | ✅ |
| 12 | 实现者 | manim-voiceover 可装不可跑：清华镜像无源；gtts 后端缺 extra 时**交互式询问安装→headless 挂死（exit 124）**；装齐后 gtts 依赖 translate.google.com 不可达（`--dry_run` 也过不了） | `Exception: gTTS gave an error...`；`Shall I install them for you? [Y/n]` 后挂死 | 文档升级为「⚠️ 实测受限」+ 完整证据链 + 绕行路径（edge-tts 独立 mp3） | ✅（受限豁免） |
| 13 | 实现者 | bpy 模板依赖 330MB Blender wheel | `ModuleNotFoundError: No module named 'bpy'` | 回归显式 SKIP + 文档保留（环境具备时执行） | ✅（SKIP 豁免） |

## 对抗性输入测试记录（Playwright 真机）

| 场景 | 注入 | 期望 | 实测 |
|---|---|---|---|
| quiz 空选提交 | 不选任何 radio 调 `grade()` | 0/5 未通过、不崩溃 | ✅ `未通过：0/5` result 可见 |
| quiz 全错提交 | 每题选错误项 | 0/5、错误项标红、正确项标绿 | ✅ wrong=5, right=5 |
| quiz 全对提交 | `#selftest` hash | 5/5 通过 | ✅ `SELFTEST score=5/5 pass=true` |
| Mermaid DAG 语法 | CDN mermaid@11 渲染模板块 | svg 生成 | ✅ `RENDER_OK nodes=6` |
| 3D 单文件 HTML | model-viewer + base64 glb | 3D 渲染 | ✅ 截图（环面/剖切导线两例） |

## 回归命令（修复后基线 25 PASS / 2 SKIP / 0 FAIL）

```bash
python scripts/regression.py   # 代码块真机执行 + quiz headless + 双文档约束 + 版本一致性
```

SKIP 豁免名单（环境受限，非模板缺陷）：graphviz#2（需 dot.exe 二进制）、3d-animation#5（需 bpy）。

---

# 第三批对抗性审查台账（2026-10-06，v1.2.2 基线 → v1.3.0）

> 对象：README/TECHNICAL 手册 + scripts/package.py + quiz 模板 + 命名规则。三视角：实现者（边界输入）/ 审查者（文档-实物一致）/ AI 使用方（照文档能走通）。修复后回归仍 **25 PASS / 2 SKIP / 0 FAIL**。

| # | 视角 | 问题 | 真实证据（原文） | 修法 | 状态 |
|---|---|---|---|---|---|
| R4-1 | 审查者 | test-prompts.json version 字段漂移（v1.2.2 发布时漏同步） | `"version": "1.2.1"` vs VERSION=1.2.2 | 纳入 package.py 自动同步（--bump 联动） | ✅ |
| R4-2 | 审查者 | TECHNICAL §3.6 物理位置在 §3.5 前（上批 3.4/3.5 对调遗留） | §3.x 顺序实测 `['3.1','3.2','3.3','3.4','3.6','3.5']` | 3.5/3.6 物理调换，编号不变 | ✅ |
| R4-8 | 审查者 | TECHNICAL §3.6 写「7 条实测坑」且漏 pymunk 静默坑、genanki 固定 ID（上批 7→9 修正只改了 SKILL.md 的姊妹遗漏） | L136 原文「第二批次实测坑（7 条…）：PillowWriter…」 | 补全为 9 条（含 pymunk `space.add(body, joint)` 与 genanki 固定 ID） | ✅ |
| R4-3 | 审查者 | README 无当前版本锚点；三手册版本号无自动递增机制 | 静态扫描 `README当前版本字段=无` | README 加「> 当前版本：」锚点行；package.py v2 `--bump` 联动递增 README/TECHNICAL §7/test-prompts.json 三处 | ✅ |
| R4-4 | AI 使用方 | README 实例 3 承诺「要手绘风」「要白板讲解」都会被采纳，但 SKILL.md 选型矩阵/工具箱无此能力 | grep SKILL.md「白板」0 命中；「手绘」仅出现在降级产物描述 | 点名说法换为真实能力：「要真实物理模拟」「要带配音讲解」 | ✅ |
| R4-5 | 实现者 | package.py 边界输入裸崩溃 | `--bump foo` → 裸 `KeyError: 'foo'`；VERSION='abc' → 裸 `ValueError` | v2 加校验：level 白名单 + VERSION 格式正则，中文报错退出。真机复测三用例全部 `[FAIL] ...优雅提示` | ✅ |
| R4-6 | 实现者 | quiz 模板 `innerHTML` 三处插值（题干/选项/解析）无转义：`<img onerror>` 可注入、`a<b` 破版式 | 双 Case 真机对照：剥 esc 后注入生效（真实 `<img>` 元素入 DOM + `document.title` 被篡改为 'XSS fired'） | 模板内置 `esc()` 包裹全部动态插值；修复后同载荷 3 判据全 PASS（注入不执行/title 不变/判分 5/5 不回归） | ✅ |
| R4-7 | AI 使用方 | 文件命名规则不覆盖主题含非法文件名字符（如 TCP/IP、含 `:` 的主题）——Windows 下直接建文件报错 | SKILL.md 命名块无净化条款 | 补「主题名净化」：非法字符替换为「－」；C++/DNA/GDP 等缩写可与中文混排 | ✅ |

## 第三批新坑回灌（不只修代码不回灌）

- TECHNICAL §3.2 坑表 + extended-viz-2.md quiz 坑表新增两条：①`esc()` 转义对策（含实测证据）；②**QUIZ 源码内联数据含字面 `</script>` 会截断 HTML `<script>` 块**（HTML 解析层截断，任何运行时转义不可防，写 `<\/script>` 绕行）——对抗过程中真实踩到（首次 probe 载荷含 `</script>` 导致整页 JS 断裂、SELFTEST NOT FOUND）。

## 第三批回归/对抗命令

```bash
python scripts/regression.py                    # 全量回归（修复后仍 25 PASS / 2 SKIP / 0 FAIL）
python _audit_v121/audit_r4_scan.py             # 审查者视角静态扫描（版本一致性/引用/语法/断言互查）
python _audit_v121/audit_r4_pkg.py              # 实现者视角：package.py 边界 4 用例
python _audit_v121/audit_r4_xss.py              # 实现者视角：quiz XSS 双 Case 真机对照
```

> 注：audit_r4_scan.py 的 B1「README 引用 MISS」为扫描器自身正则吃进反引号的假阳性（文件实际存在），已复核排除；「3D 五层」措辞差异（README「3D 分五层」）同为关键词匹配假阳性，能力链在 TECHNICAL §3.3 完整。

---

## 第四批（v1.4.0 基线，2026-10-06）

| # | 视角 | 问题 | 真机证据 | 修法 | 状态 |
|---|---|---|---|---|---|
| R5-1 | 实现者 | **`--bump patch` 静默不递增**：`bump()` 的 patch 分支写成 `f"{a}.{b}.{c}"`（c 未 +1），exit=0 且照常打包 → 打出与旧版同名的 zip 覆盖原产物，用户以为发布了新版本 | 隔离副本真机：`VERSION 1.4.0 --bump patch → VERSION=1.4.0`，exit=0，产物名 `...-v1.4.0.zip` | patch 分支改 `c+1`；并加防御断言「递增后必须 != 旧值，否则 fail（禁止静默复用旧版本号）」 | ✅ |
| R5-2 | 实现者 | `--note` / `--bump` 置于末位缺值 → 裸 `IndexError: list index out of range`（v2 新增参数未做边界校验，是 R4-5 的同类遗漏） | 真机：`['--bump','patch','--note']` 与 `['--bump']` 均抛 IndexError + Traceback | 新增 `opt_val(flag)`：缺值 / 末位 / 后接另一个 flag 一律 `[FAIL] xx 后缺少取值（正确用法：--xx <值>）` | ✅ |
| R5-3 | 实现者 | README 无版本锚点时的「自动插入」分支从未被真机验证（首轮因 R5-1 连带失败被误判） | 真机 T9：删除锚点行后跑 `--bump patch`，插入结果 False | 修 R5-1 后复测：锚点自动插入 True，9/9 用例全 PASS | ✅ |
| R5-4 | 审查者 | TECHNICAL §1 目录树严重滞后：缺 `extended-viz-2.md`、`audit-checklist.md`、`templates/`、`scripts/`、`VERSION`；且正文仍写「**纯声明式技能——不包含任何可执行脚本**」，与已存在的 `scripts/package.py`、`scripts/regression.py` 自相矛盾 | 静态扫描 A3 系列：磁盘 6 个 references + 1 模板 + 2 脚本，目录树仅列 4 个 | 目录树补全（含 `templates/`、`scripts/`、`VERSION`）；定位描述改为「声明式技能 + 两个工程脚本（仅服务打包/回归，不参与运行时交付）」 | ✅ |
| R5-5 | 审查者 | TECHNICAL §5.2 称「内置 6 条反模式」，SKILL.md 实测 **8 条**（与历史上 7→9 计数漂移同源） | 扫描 A1：`TECHNICAL=6 vs SKILL.md 实测=8` | 改为 8 条并列举；回归新增 `doc-黑名单计数` 断言永久防复发 | ✅ |
| R5-6 | 审查者 | TECHNICAL Phase 4 选型矩阵 **10 行** vs SKILL.md **13 行**（缺 Mermaid / pymunk / 配音+自测+3D 单文件三行） | 扫描 A2：`SKILL.md=13 vs TECHNICAL=10` | TECHNICAL 补 3 行；回归新增 `doc-选型矩阵行数` 断言 | ✅ |
| R5-7 | 审查者 | TECHNICAL §5.4 质量评分记录只写到第二轮（88.45），缺第三轮（94.1 + ROI 网关跳过结论） | 扫描 A5：§5.4 仅两轮表格 | 补「第三轮」小节（含 10 维明细与真机证据来源） | ✅ |
| R5-8 | AI 使用方 | **Phase 0 指令撞墙**：要求「一次性弹出五项让用户点选」，但主流结构化提问组件一次最多 4 个问题 → 模型照做会失败并退化成开放式追问（与「禁止开放式追问」自相矛盾） | 扫描 B3：需弹选项维度 ≥4（上限 4），且无任何分批/合并兜底说明 | SKILL.md 新增「提问能力约束」5 条：主题不单列、深度+覆盖范围可合并为 1 问、超限则分批（首批答完即开工）、无提问能力时走默认值；TECHNICAL §2 同步 | ✅ |
| R5-9 | AI 使用方 | 多选维度（可视化形式）未说明须声明为多选，且「可全不选」在提问组件中**无对应机制**（用户无法表达「不选」） | 扫描 B4b：仅缺省策略兜底，无选项级兜底 | 明确「须声明为多选」+ 必须提供「自动（交给技能决定）」显式选项 | ✅ |
| R5-10 | AI 使用方 | SKILL.md「深度=精通/**交付**时交付双文档」——「交付」不是深度档位名（档位为 速览/精通/**输出**），属术语漂移 | 扫描 B6 命中 `深度=精通/交付时交付` | 改为「深度=精通/输出时」 | ✅ |
| R5-11 | AI 使用方 | SKILL.md「配套资源」未列 `audit-checklist.md` 与 `templates/quiz-template.html`——AI 使用方做自测/记忆卡时不知道有现成模板，事后校验也无清单入口 | 扫描 B7：两项 MISS | 补两行引用（含 `#selftest` 断言用法与「改动后必跑回归」提示） | ✅ |
| R5-12 | AI 使用方 | 第二批次产物（mp3 / 自测 HTML / apkg / 3D HTML）**无命名约定**——「电流」实例自行命名，换会话即不一致 | 对照 `D:\skills\electric-current\` 实际命名 vs SKILL.md 命名块无相关条款 | 命名块补「第二批次产物命名」：`[主题]—语音讲解.mp3` / `—自测N题.html` / `—记忆卡.apkg` / `—3D结构.html` | ✅ |
| R5-13 | 实现者 | 回归未覆盖 v1.4.0 新功能（Phase 0 五项）与文档交叉一致性，属「常规验证未覆盖全部功能」 | 原回归仅 27 项，无 SKILL.md 结构断言 | regression.py 新增三组 18 项断言（Phase 0 结构 13 项 / 文档一致性 4 项 / package bump 真机 1 项）→ 43 PASS / 2 SKIP / 0 FAIL | ✅ |

### 第四批新坑回灌

- **静默失败比崩溃更危险**：`--bump patch` 未递增却 exit=0，会打出与旧版同名的压缩包覆盖产物。凡「版本号单一来源 + 自动递增」类脚本，必须加「递增后 != 旧值」断言（已写进 package.py 与回归用例）。
- **隔离沙箱脚本要排除 `.git`**：`shutil.rmtree` 清理含 `.git` 的临时副本会触发本机安全策略（PermissionError WinError 5）。构造隔离副本时 `ignore=ignore_patterns(".git", "dist", "_reg_work", "__pycache__")`，并给每次运行加唯一 ID，删除用 `ignore_errors=True`。
- **文档计数类漂移会反复发生**（7→9 坑、6→8 反模式、10→13 矩阵行）。根治方式不是人工核对，而是把「声称数 vs 实测数」写成回归断言（本批新增 `doc-黑名单计数`、`doc-选型矩阵行数`、`doc-目录树覆盖`、`doc-版本号四处一致`）。

### 第四批回归/对抗命令

```bash
python scripts/regression.py              # 全量回归（修复后 43 PASS / 2 SKIP / 0 FAIL）
python _audit_v121/audit_r5_scan.py        # 审查者 + AI使用方视角静态扫描（A1-A5 / B1-B7）
python _audit_v121/audit_r5_pkg.py         # 实现者视角：package.py 9 个边界用例（隔离副本真机）
```

> 注：audit_r5_scan.py 首版 B3「需弹选项 7 项」为 section 截断正则过宽（把 Phase 1–5 的编号项一并计入）导致的计数偏差，结论方向不变（5 维度 > 4 上限），已按修复后的 SKILL.md 复核。

---

## 第五批（v1.5.1 / v1.5.2 基线，2026-10-07）：可视化链路加固

触发方式：真实使用本机环境跑通「安装 → 依赖探测 → 2D/3D 可视化」全链路，逐环节取证。

| # | 视角 | 问题 | 真机证据 | 处置 | 状态 |
|---|---|---|---|---|---|
| R6-1 | AI 使用方 | **依赖探测只探当前解释器**：PATH 上的 `python` 是干净解释器，manim 装在另一个 venv → 技能误判「本机没装 manim」并降级到 matplotlib GIF | 真机：`C:\Program Files\Python312\python.exe` 无 manim；`envs\deeptutor` 有 manim 0.21.0 且 `-ql` **6.6 秒**出片 | manim-patterns §2.1 跨解释器扫描 + 环境画像；SKILL Phase 4 新增第 0 步；回归 `viz-跨解释器探测` | ✅ |
| R6-2 | 实现者 | `MathTex` 模板从未探测 LaTeX 依赖 | 真机：`shutil.which('latex')=None`（MiKTeX 装了但 bin 不在 PATH）→ 渲染失败、无产物；把 MiKTeX bin 前置后同一场景渲染成功（4780 B PNG） | manim-patterns §2.2 探测 + PATH 修复 + 三级降级；TECHNICAL 坑表同步 | ✅ |
| R6-3 | 实现者 | 2D 降级档只有 PillowWriter GIF（256 色、体积大） | 真机同 40 帧 360×240：**GIF 104.6 KB vs MP4 19.4 KB**；且 libx264 要求宽高偶数（360×225 直接整条失败） | cookbook 新增「帧序列 → ffmpeg MP4」升级档 + `scale=trunc(iw/2)*2` 兜底 + 坑表 | ✅ |
| R6-4 | 实现者 | 配音与动画无法合体（manim-voiceover 受限网络不可用、SoX 缺装），「解说念不完」原始痛点未解 | 真机：edge-tts 出 mp3 + srt → ffmpeg `-c:v copy -c:a aac -shortest` 得 **50 KB mp4，h264 + aac 双流**（ffprobe 验证） | extended-viz-2 §3.1 合体管线（含软字幕 `mov_text` 与 ffprobe 自检） | ✅ |
| R6-5 | 实现者 | PyVista 只用了离屏截图，透明体仍靠「淡化辅助元素」缓解；`open_movie` 缺后端未记录 | 真机：pyvista 0.49.0 具备 `enable_depth_peeling`/`ssaa`/`shadows`/`ssao`/EDL；default 环境**无 imageio/av/kaleido** | 3d-animation 质量档 + 文末可复制模板（回归真机执行）；TECHNICAL 坑表同步 | ✅ |
| R6-6 | AI 使用方 | **交互/3D 产物无机器断言**：白屏、死控件、CDN 失败全都「看起来像正常页面」 | 真机：headless Chrome 下 WebGL 可渲染可断言（`readPixels=51,102,204,255`）；反面用例（空白画布）被判 FAIL、退出码 1 | SELFTEST 约定 + `scripts/selftest_web.py` + `templates/selftest-web-template.html`；回归 `selftest-web模板`/`selftest-web脚本` 两条真机断言 | ✅ |
| R6-7 | AI 使用方 | CDN 依赖导致离线/内网白屏，且此前无体积依据判断内联是否可行 | 实测 three.min.js **589 KB** / model-viewer **913 KB** / echarts **1005 KB** | 离线自足档（内联进 HTML 或落本地 `assets/`）+ 坑表 | ✅ |
| R6-8 | 实现者 | regression.py 在 GBK 控制台打印中文说明时 `UnicodeEncodeError` **中途崩溃**（跑完但不出结果） | 真机：`UnicodeEncodeError: 'gbk' codec can't encode character '\ufffd'` | `sys.stdout.reconfigure(encoding="utf-8")`；对子进程注入 `PYTHONIOENCODING=utf-8` | ✅ |
| R6-9 | AI 使用方 | 无障碍/移动端完全空白：模板无 `prefers-reduced-motion`、`:focus-visible`、窄屏适配 | grep 两个模板均 0 命中 | 两个模板补 a11y 样式；SKILL / TECHNICAL / cookbook / extended-viz 自检清单加底线；回归 `viz-无障碍` | ✅ |
| R6-10 | AI 使用方 | 3D 选型缺成本维度，降级靠「临时补」 | — | 3D 门槛补「2D 备选图强制」+ 成本档（mplot3d < PyVista < Manim < Blender）；回归 `viz-2D备选图` | ✅ |

### 第五批新坑回灌

- **「import 失败」≠「本机没装」**：Windows 没有全局包注册表，`py -0p` 只列注册过的安装、PATH 只列 PATH 上的，**两者都会漏掉 venv**。否定性结论必须写明搜索范围（「在我探测的解释器里没有」），范围不足就不能下结论。
- **见到指向本机的硬编码路径（含本机用户名/盘符），第一动作是 `Test-Path`，不是解释它为何不适用**。本轮 R6-1 的路径就写在同一份 `regression.py` 里，曾被误判为「作者环境专用」而跳过。
- **断言必须配反面用例**：不绘制任何东西的页面如果也能判 PASS，说明断言是永真的——回归里的 `selftest-web模板` 与空白画布对照共同固化这一点。
- **无头 WebGL 可用但不可假定**：多数机器 `--disable-gpu` 即走 SwiftShader 正常，个别 Chrome 版本需 `--enable-unsafe-swiftshader`（断言器已默认带上）；拿不到 context 时应判 `skip` 而非 fail，避免把环境限制误报为产物损坏。
- **中文输出要有编码防线**：脚本在 GBK 控制台打印中文说明会崩，且往往崩在「跑完准备汇总」的最后一步——症状是「有过程没结论」。

### 第五批回归/对抗命令

```bash
python scripts/regression.py                    # 全量回归（v1.5.3 基线 60 PASS / 1 SKIP / 0 FAIL）
python scripts/selftest_web.py                  # 交互产物自测：内置模板自检
python scripts/selftest_web.py <产物.html>       # 断言具体交互/3D 产物（退出码 0/1/2）
# Blender E 层：bpy 代码块由回归用 `blender -b --factory-startup -P` 真机执行，不再 SKIP
```

### 第五批续（v1.5.3）：Blender E 层从「跳过」变为「真机执行」

| # | 视角 | 问题 | 真机证据 | 处置 | 状态 |
|---|---|---|---|---|---|
| R6-11 | 实现者 | 回归对 bpy 代码块一律 SKIP，理由写的是「bpy 依赖 Blender wheel(330MB)，环境未装」——**把「pip 里没有 bpy」当成了「本机没有 Blender」** | 本机实际装有 **Blender 5.2.2 LTS**（`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`，注册表可查）；`bpy` 是 Blender **自带**模块，用 `blender -b -P` 根本不需要那个 wheel | 探测改为「PATH → 常见目录 → 注册表 Uninstall 键」；run_blocks 识别 `import bpy` 时改用 `blender -b --factory-startup -P` 真机执行；删除该 SKIP 条目 | ✅ |
| R6-12 | 实现者 | 引擎可用性判断错误：`RenderSettings.bl_rna.properties['engine'].enum_items` 在 5.2.2 只返回 `['BLENDER_EEVEE']`，据此会得出「没有 Cycles」的错误结论 | 真机：`bpy.app.build_options.cycles = True`，直接 `scn.render.engine = 'CYCLES'` 成功，CPU 8 采样渲染 0.2 s 出图 | 文档写明**不要用 enum_items 判断**，改为「赋值 + try」；并给出 EEVEE 无头失败时切 Cycles CPU 的兜底 | ✅ |
| R6-13 | AI 使用方 | 「Blender 成本高（分钟级）」的说法让 E 层被默认回避，实际未测 | 真机（320×180 简单场景，Blender 5.2.2）：EEVEE 首帧 1.0 s、后续 **0.16 s/帧**；12 帧合计 2.8 s，含启动墙钟 5.1 s；ffmpeg 合成 mp4 6.4 KB | 成本档按实测改写；模板改为「先小分辨率出样片再抬规格」 | ✅ |

**第五批续新坑回灌**：

- 「某个 pip 模块找不到」**不等于**「对应的桌面应用没装」——Blender/PyVista/VTK 这类都自带运行时，先查应用再下结论。
- **不要用枚举去找能力**：动态枚举（如 Blender 的 engine）会漏项，能用「赋值 + try」验证的，就别读枚举列表。
- 应用类依赖（Blender、Chrome、ffmpeg）**常年不在 PATH**：探测必须叠加「常见目录 + 注册表」，否则会重演 R6-1 的误判。


---

## 第六批（v1.5.7 → v1.5.8，2026-10-07）：Blender 调用决策清单固化后的三视角复审

触发方式：把「3D 与 Blender 调用决策清单」固化进 SKILL.md/TECHNICAL.md 后，按实现者/审查者/AI 使用方三视角做对抗性复审，并以真机取证。

| # | 视角 | 问题 | 真机证据 | 处置 | 状态 |
|---|---|---|---|---|---|
| R7-1 | 审查者 | **新清单无任何回归断言**：清单可被静默删除或改坏而全量回归仍全绿（与 R5-13「文档漂移无断言」同类，属复发） | 静态扫描：`regression.py` 中 `调用决策清单` 0 命中，而 SKILL/TECHNICAL 均有 | 新增 `viz-Blender决策清单` 断言：两份文档必须同时含清单，且四道闸关键词齐全 + glb 出口 + 探测三级 | ✅ |
| R7-2 | AI 使用方 | **清单把「可交互 3D」隐含绑定到 Blender**：闸③写「找不到 blender.exe → PyVista/Manim/交互 HTML」，会漏掉 trimesh 这条零 Blender 的 glb 通道 → AI 在无 Blender 机器上直接跳到录像或静态图，丢掉最优出口 | 文档交叉比对：`extended-viz-2.md §5` 明载 trimesh→glb→model-viewer 且「实测通过（截图验证）」，与清单闸③结论矛盾 | 闸③改为同时探 blender.exe 与 trimesh；出口段补「glb 有两个来源，别绑死在 Blender 上」 | ✅ |
| R7-3 | AI 使用方 | **把「探测不到」误当成「装不了」**：清单只写探测，未区分「pip 包可临时装」与「桌面应用装不了」，会导致无 trimesh 环境下误降级 | 本机实测：Python312 / uv-cpython3.12.13 / anaconda base **三个解释器 scan 均无** trimesh、pyvista、manim（只有 matplotlib）——正是「探测不到」的典型环境 | 闸③补「探测结论=环境现状而非能力上限；trimesh/pyvista/manim 允许先装再用（隔离 venv 优先）；只有 Blender 是桌面应用」 | ✅ |
| R7-4 | AI 使用方 | **降级路径把能力塞错库**：闸④「是→E 层 Blender」，无 Blender 时统一指向 PyVista，但 PyVista **做不了刚体/流体动力学仿真**（那是 Blender 刚体约束/Mantaflow 的独占能力） | 场景推演：齿轮传动/流体主题在本机（无 Blender 时）按原清单会得到「用 PyVista」的无效结论 | 闸④补按能力拆分的降级表：光路/材质/运镜→mplot3d 或 Manim ThreeDScene；刚体/流体→pymunk 或 Manim 手绘帧；晶格/分子构型/拓扑→trimesh/PyVista 建网格导 glb/PNG | ✅ |
| R7-5 | 实现者 | 断言若写成恒真则毫无防护力（历史教训：不绘制任何东西的页面也能判 PASS） | 反永真用例真机跑：真实文档→true；抽掉 SKILL 清单→false；抽掉 TECHNICAL 清单→false；删「质感门槛」→false；删 `blender.exe`→false；删 glb 出口→false（7/7 符合预期） | 断言按「两份文档同源 + 闸关键词 + 出口 + 探测」多点合取，任一缺失即 FAIL | ✅ |
| R7-6 | 实现者 | 后台任务输出为空 + exit 1，被误读成「脚本跑挂了」（实际是工具层长命令转后台的表现，回归真实结果 PASS 68 / SKIP 1 / FAIL 0） | 同一命令前台跑输出为空、`job_list` 显示 exit 1；改用 Python wrapper 直跑得完整 74 行输出与 `SYSTEMEXIT 0` | 结论：**空输出 ≠ 脚本失败**，判断回归成败必须以「汇总行/退出码/marker」为准，不能以「有没有输出」为准 | ✅ |

**第六批新坑回灌**：

- **文档里新增规则，必须同时新增断言**——否则规则只是「写在纸上」，回归给不出任何保障（R7-1 是 R5-13 的复发，说明「新增文档时补断言」要成为固定动作，而不是事后补救）。
- **「没有 X」不等于「不能用 X」**：pip 包（trimesh/pyvista/manim）可以先装；只有桌面应用（Blender/Chrome/ffmpeg）才存在「装不了」。清单里的降级分支必须区分这两类。
- **降级要按能力拆**，不能按「层级」一刀切：PyVista 不是 Blender 的通用替代品（它擅长场/曲面，不做动力学仿真），错的映射会让 AI 得到一个「能跑但答非所问」的方案。
- **空输出先怀疑工具层，再怀疑脚本**：长命令被转后台时会表现为「无输出 + 非零退出」，与脚本崩溃同形；用 wrapper 直跑 + 打印 marker 是可靠的分辨手段。

### 第六批回归/对抗命令

```bash
python scripts/regression.py            # 全量回归（v1.5.7 基线 68 PASS / 1 SKIP / 0 FAIL）
```